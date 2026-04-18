from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

import numpy as np
import pandas as pd
import joblib
import torch
import warnings

from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP

from datetime import datetime, timedelta
import threading
import os
import uuid

from models.lstm_model import LSTMModel
from services.detection_logic import calculate_severity, detect_attack_type

from pymongo import MongoClient

# ==============================
# ⚠️ REMOVE WARNING SPAM
# ==============================
warnings.filterwarnings("ignore", category=UserWarning)

# ==============================
# APP SETUP
# ==============================
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ==============================
# DATABASE
# ==============================
client = MongoClient("mongodb://localhost:27017/")
db = client["anomai"]
alerts_collection = db["alerts"]

# ==============================
# LOAD MODELS
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "trained_model_files")

ml_model = joblib.load(os.path.join(MODEL_DIR, "isolation_model.pkl"))
scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))

lstm_model = LSTMModel(input_size=6)
lstm_model.load_state_dict(
    torch.load(os.path.join(MODEL_DIR, "lstm.pth"), map_location=torch.device("cpu"))
)
lstm_model.eval()

lstm_scaler = joblib.load(os.path.join(MODEL_DIR, "lstm_scaler.pkl"))
LSTM_THRESHOLD = joblib.load(os.path.join(MODEL_DIR, "lstm_threshold.pkl"))

print("✅ Models Loaded | LSTM Threshold:", LSTM_THRESHOLD)

# ==============================
# GLOBALS
# ==============================
alerts = []
ip_stats = {}
packet_times = {}
ip_sequences = {}
ip_ports = {}
alert_cache = {}
cooldown_map = {}
alert_counter = {}
total_packets = 0
MAX_ALERTS = 300

# ==============================
# HELPERS
# ==============================
def is_duplicate(key, window=10):
    now = datetime.now()
    if key in alert_cache and (now - alert_cache[key]).seconds < window:
        return True
    alert_cache[key] = now
    return False


def is_in_cooldown(ip, cooldown=15):
    now = datetime.now()
    if ip in cooldown_map and (now - cooldown_map[ip]).seconds < cooldown:
        return True
    cooldown_map[ip] = now
    return False

# ==============================
# FEATURES
# ==============================
def build_features(src_ip, packet_size, port, packet_rate, unique_ports):
    return [
        packet_size,
        packet_rate,
        1,
        port,
        port,
        unique_ports,
        min(unique_ports / 10, 1),
        (packet_size - 500) / 200,
        packet_rate / 2,
        1 if packet_size > 1400 else 0,
        packet_rate * 12,
        ip_stats.get(src_ip, 1),
        0.1
    ]

def build_lstm_features(packet_size, packet_rate, unique_ports):
    return [
        packet_size,
        packet_rate,
        unique_ports,
        unique_ports / 10,
        packet_rate * 10,
        1 if packet_size > 1400 else 0
    ]

# ==============================
# PACKET PROCESSING
# ==============================
def process_packet(packet):
    global total_packets

    if not packet.haslayer(IP):
        return

    total_packets += 1

    src_ip = packet[IP].src
    dst_ip = packet[IP].dst
    packet_size = len(packet)

    if packet.haslayer(TCP):
        protocol = "TCP"
        port = packet[TCP].dport
    elif packet.haslayer(UDP):
        protocol = "UDP"
        port = packet[UDP].dport
    else:
        protocol = "Other"
        port = 0

    # Track ports
    ip_ports.setdefault(src_ip, set()).add(port)
    unique_ports = len(ip_ports[src_ip])

    now = datetime.now()

    # Packet rate
    packet_times.setdefault(src_ip, []).append(now)
    packet_times[src_ip] = [
        t for t in packet_times[src_ip]
        if now - t < timedelta(seconds=5)
    ]
    packet_rate = len(packet_times[src_ip])

    ip_stats[src_ip] = ip_stats.get(src_ip, 0) + 1

    # ======================
    # ML MODEL
    # ======================
    features = build_features(src_ip, packet_size, port, packet_rate, unique_ports)
    features_scaled = scaler.transform([features])  # keep stable
    ml_score = float(ml_model.decision_function(features_scaled)[0])

    # ======================
    # LSTM MODEL (FIXED)
    # ======================
    ip_sequences.setdefault(src_ip, [])

    lstm_input = build_lstm_features(packet_size, packet_rate, unique_ports)

    if lstm_scaler:
        lstm_scaled = lstm_scaler.transform(np.array(lstm_input).reshape(1, -1))[0]
    else:
        lstm_scaled = lstm_input

    ip_sequences[src_ip].append(lstm_scaled)
    ip_sequences[src_ip] = ip_sequences[src_ip][-10:]

    lstm_score = 0
    lstm_anomaly = False

    if len(ip_sequences[src_ip]) == 10:
        seq = np.array(ip_sequences[src_ip])
        tensor = torch.tensor([seq], dtype=torch.float32)

        with torch.no_grad():
            output = lstm_model(tensor)
            lstm_score = float(torch.mean((tensor - output) ** 2).item())

            # ✅ CORRECT anomaly detection
            if lstm_score > LSTM_THRESHOLD:
                lstm_anomaly = True

    # ======================
    # SMART DECISION ENGINE
    # ======================
    rating = calculate_severity(packet_rate, ml_score, lstm_score)
    attack_type = detect_attack_type(
    packet_rate,
    protocol,
    packet_size,
    unique_ports
)

    if rating in ["Low", "Medium", "High", "Critical"]:

        alert = {
            "timestamp": now,
            "source_ip": src_ip,
            "destination_ip": dst_ip,
            "packet_size": packet_size,
            "protocol": protocol,
            "packet_rate": packet_rate,
            "ml_score": round(ml_score, 3),
            "lstm_score": round(lstm_score, 4),
            "lstm_anomaly": lstm_anomaly,
            "rating": rating,
            "attack_type": attack_type,
            "id": str(uuid.uuid4())
        }

        key = f"{src_ip}-{dst_ip}-{attack_type}-{rating}"

        if is_duplicate(key) or is_in_cooldown(src_ip):
            return

        alert_counter[key] = alert_counter.get(key, 0) + 1
        alert["repeat_count"] = alert_counter[key]

        # always send to frontend (ALL alerts including Low)
        alerts.append(alert)
        socketio.emit("new_alert", alert)

        # store only important alerts in DB
        if alerts_collection is not None and rating in ["Medium", "High", "Critical"]:
            try:
                alerts_collection.insert_one(alert)
            except Exception as e:
                print("DB error:", e)

                if len(alerts) > MAX_ALERTS:
                    alerts.pop(0)

# ==============================
# ROUTES
# ==============================
@app.route("/")
def home():
    return "ANOM-AI Running"

@app.route("/alerts")
def get_alerts():
    data = list(alerts_collection.find().sort("timestamp", -1).limit(300))
    for d in data:
        d["_id"] = str(d["_id"])
    return jsonify(data)

@app.route("/stats")
def stats():
    return jsonify({
        "total_packets": total_packets,
        "unique_ips": len(ip_stats)
    })




# ==============================
# CHATBOT ENDPOINT
# ==============================
import requests
from flask import request, jsonify

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    alert = data.get("alert", {})

    # 🧠 Build prompt for local AI
    prompt = f"""
You are a cybersecurity AI assistant for a SOC dashboard.

Explain the alert in a simple, clear, and practical way.

Rules:
- Be concise (5–7 lines max)
- Use bullet points
- Highlight severity clearly
- Explain what it means (not generic statements)
- Suggest actionable steps
- Do NOT use corporate phrases like "our team is investigating"

User question: {message}

Alert data:
{alert}
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "tinyllama",   # ✅ free local model
                "prompt": prompt,
                "stream": False
            }
        )

        result = response.json()
        return jsonify({"response": result.get("response", "No response")})

    except Exception as e:
        print("Ollama Error:", e)
        return jsonify({"response": "⚠️ Local AI not running. Start Ollama."})

# ==============================
# START
# ==============================
def start_sniffing():
    sniff(prn=process_packet, store=False)

if __name__ == "__main__":
    threading.Thread(target=start_sniffing, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)