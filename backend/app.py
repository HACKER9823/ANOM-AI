from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

import numpy as np
import pandas as pd
import joblib
import torch

from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP

from datetime import datetime, timedelta
import threading
import os

from models.lstm_model import LSTMModel

# ==============================
# APP SETUP
# ==============================
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ==============================
# BASE PATH
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "trained_model_files")

# ==============================
# LOAD ISOLATION FOREST
# ==============================
try:
    ml_model = joblib.load(os.path.join(MODEL_DIR, "isolation_model.pkl"))
    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    print("✅ Isolation Forest loaded")
except Exception as e:
    print("❌ Error loading ML model:", e)
    exit()

# ==============================
# LOAD LSTM
# ==============================
try:
    lstm_model = LSTMModel(input_size=6)
    lstm_model.load_state_dict(
        torch.load(os.path.join(MODEL_DIR, "lstm.pth"), map_location=torch.device("cpu"))
    )
    lstm_model.eval()

    lstm_scaler = joblib.load(os.path.join(MODEL_DIR, "lstm_scaler.pkl"))
    LSTM_THRESHOLD = joblib.load(os.path.join(MODEL_DIR, "lstm_threshold.pkl"))

    print("✅ LSTM loaded | Threshold:", LSTM_THRESHOLD)

except Exception as e:
    print("⚠️ LSTM not loaded:", e)
    lstm_model = None
    lstm_scaler = None
    LSTM_THRESHOLD = 0.05

# ==============================
# GLOBAL STORAGE
# ==============================
alerts = []
ip_stats = {}
packet_times = {}
ip_sequences = {}
ip_ports = {}

total_packets = 0
MAX_ALERTS = 300

# ==============================
# FEATURE ENGINEERING (ML)
# ==============================
def build_features(src_ip, packet_size, port, packet_rate, unique_ports):

    flow_duration = 1
    packet_size_zscore = (packet_size - 500) / 200
    rate_vs_duration_ratio = packet_rate / (flow_duration + 1)
    large_packet_flag = 1 if packet_size > 1400 else 0
    connection_count_per_min = packet_rate * 12
    src_ip_frequency = ip_stats.get(src_ip, 1)
    icmp_ratio = 0.1
    port_entropy = min(unique_ports / 10, 1)

    return [
        packet_size,
        packet_rate,
        flow_duration,
        port,
        port,
        unique_ports,
        port_entropy,
        packet_size_zscore,
        rate_vs_duration_ratio,
        large_packet_flag,
        connection_count_per_min,
        src_ip_frequency,
        icmp_ratio
    ]

# ==============================
# LSTM FEATURES
# ==============================
def build_lstm_features(packet_size, packet_rate, unique_ports):
    port_entropy = unique_ports / 10
    conn_per_min = packet_rate * 10
    large_flag = 1 if packet_size > 1400 else 0

    return [
        packet_size,
        packet_rate,
        unique_ports,
        port_entropy,
        conn_per_min,
        large_flag
    ]

# ==============================
# ATTACK CLASSIFICATION
# ==============================
def classify_attack(packet_size, rate, protocol, unique_ports=0):
    if rate > 50:
        return "DDoS / Flood Attack"
    elif rate > 25 and unique_ports > 10:
        return "Port Scan"
    elif packet_size > 1400:
        return "Large Packet Attack"
    elif protocol == "Other":
        return "Suspicious Protocol"
    elif rate > 15:
        return "Brute Force"
    else:
        return "Generic Anomaly"

# ==============================
# PACKET PROCESSING
# ==============================
def process_packet(packet):
    global total_packets

    try:
        if not packet.haslayer(IP):
            return

        total_packets += 1

        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        packet_size = len(packet)

        # Protocol
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
        if len(ip_ports[src_ip]) > 20:
            ip_ports[src_ip] = set(list(ip_ports[src_ip])[-20:])
        unique_ports = len(ip_ports[src_ip])

        # Packet rate
        ip_stats[src_ip] = ip_stats.get(src_ip, 0) + 1
        now = datetime.now()

        packet_times.setdefault(src_ip, []).append(now)
        packet_times[src_ip] = [
            t for t in packet_times[src_ip]
            if now - t < timedelta(seconds=5)
        ]

        packet_rate = len(packet_times[src_ip])

        # ======================
        # ML MODEL
        # ======================
        feature_names = [
            "packet_size",
            "connection_rate",
            "flow_duration",
            "src_port",
            "dst_port",
            "unique_dst_ports",
            "port_entropy",
            "packet_size_zscore",
            "rate_vs_duration_ratio",
            "large_packet_flag",
            "connection_count_per_min",
            "src_ip_frequency",
            "icmp_ratio"
        ]

        features = build_features(
            src_ip, packet_size, port, packet_rate, unique_ports
        )

        features_df = pd.DataFrame([features], columns=feature_names)
        features_scaled = scaler.transform(features_df)

        ml_score = float(ml_model.decision_function(features_scaled)[0])

        # ======================
        # LSTM MODEL
        # ======================
        ip_sequences.setdefault(src_ip, [])

        lstm_features = build_lstm_features(
            packet_size, packet_rate, unique_ports
        )

        if lstm_scaler:
            lstm_scaled = lstm_scaler.transform(
                np.array(lstm_features).reshape(1, -1)
            )[0]
        else:
            lstm_scaled = lstm_features

        ip_sequences[src_ip].append(lstm_scaled)
        ip_sequences[src_ip] = ip_sequences[src_ip][-10:]

        lstm_score = 0

        if lstm_model and len(ip_sequences[src_ip]) == 10:
            seq = np.array(ip_sequences[src_ip])
            tensor = torch.tensor([seq], dtype=torch.float32)

            with torch.no_grad():
                output = lstm_model(tensor)
                lstm_score = float(torch.mean((tensor - output) ** 2).item())

        # ======================
        # DECISION ENGINE
        # ======================
        score = 0

        if ml_score < -0.35:
            score += 3

        if lstm_score > (LSTM_THRESHOLD * 1.5):
            score += 3

        if packet_rate > 35:
            score += 2

        if protocol == "Other":
            score += 1

        # ======================
        # ALERT
        # ======================
        if score >= 5:

            if score >= 6:
                rating = "Critical"
            elif score >= 5:
                rating = "High"
            else:
                rating = "Medium"

            alert = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "source_ip": src_ip,
                "destination_ip": dst_ip,
                "packet_size": packet_size,
                "protocol": protocol,
                "packet_rate": packet_rate,
                "ml_score": round(ml_score, 3),
                "lstm_score": round(lstm_score, 4),
                "ai_score": score,
                "rating": rating,
                "attack_type": classify_attack(
                    packet_size, packet_rate, protocol, unique_ports
                )
            }

            alerts.append(alert)
            socketio.emit("new_alert", alert)

            if len(alerts) > MAX_ALERTS:
                alerts.pop(0)

    except Exception as e:
        print("Error:", e)

# ==============================
# SNIFF
# ==============================
def start_sniffing():
    sniff(prn=process_packet, store=False)

# ==============================
# ROUTES
# ==============================
@app.route("/")
def home():
    return "🚀 ANOM-AI Running"

@app.route("/alerts")
def get_alerts():
    return jsonify(alerts)

@app.route("/stats")
def stats():
    return jsonify({
        "total_packets": total_packets,
        "unique_ips": len(ip_stats)
    })

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        thread = threading.Thread(target=start_sniffing)
        thread.daemon = True
        thread.start()

    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
