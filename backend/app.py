from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

import numpy as np
import joblib
from sklearn.ensemble import IsolationForest

from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP

from datetime import datetime, timedelta
import threading
import os

# ==============================
# OPTIONAL: CLEAN TENSORFLOW LOGS
# ==============================
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from tensorflow.keras.models import load_model

# ==============================
# APP SETUP
# ==============================
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ==============================
# LOAD ML MODEL
# ==============================
try:
    ml_model = joblib.load("ml_model.pkl")
    print("✅ Loaded trained ML model")
except:
    print("⚠️ Using fallback ML model")
    X_train = np.random.normal(loc=500, scale=50, size=(1000, 2))
    ml_model = IsolationForest(contamination=0.05)
    ml_model.fit(X_train)

# ==============================
# LOAD LSTM MODEL
# ==============================
LSTM_MODEL_PATH = "lstm_model.h5"
lstm_model = None

if os.path.exists(LSTM_MODEL_PATH):
    lstm_model = load_model(LSTM_MODEL_PATH)
    print("✅ LSTM model loaded")
else:
    print("⚠️ No LSTM model found (running fallback)")

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
# NORMALIZATION
# ==============================
def normalize_features(packet_size, proto_val, packet_rate):
    return [
        packet_size / 2000.0,
        proto_val,
        packet_rate / 50.0
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
        return "Brute Force / Rapid Requests"
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

        # --------------------------
        # Protocol + Port Detection
        # --------------------------
        if packet.haslayer(TCP):
            protocol = "TCP"
            proto_val = 1
            port = packet[TCP].dport

        elif packet.haslayer(UDP):
            protocol = "UDP"
            proto_val = 0
            port = packet[UDP].dport

        else:
            protocol = "Other"
            proto_val = 0
            port = 0

        # --------------------------
        # Port Tracking
        # --------------------------
        ip_ports.setdefault(src_ip, set()).add(port)

        if len(ip_ports[src_ip]) > 20:
            ip_ports[src_ip] = set(list(ip_ports[src_ip])[-20:])

        unique_ports = len(ip_ports[src_ip])

        # --------------------------
        # Packet Rate Calculation
        # --------------------------
        ip_stats[src_ip] = ip_stats.get(src_ip, 0) + 1

        now = datetime.now()
        packet_times.setdefault(src_ip, []).append(now)

        packet_times[src_ip] = [
            t for t in packet_times[src_ip]
            if now - t < timedelta(seconds=5)
        ]

        packet_rate = len(packet_times[src_ip])

        # --------------------------
        # LOG REAL TRAFFIC (for training)
        # --------------------------
        with open("traffic_log.csv", "a") as f:
            f.write(f"{packet_size},{proto_val},{packet_rate}\n")

        # --------------------------
        # ML PREDICTION
        # --------------------------
        features = np.array([[packet_size, proto_val]])
        ml_pred = ml_model.predict(features)[0]

        # --------------------------
        # LSTM SEQUENCE
        # --------------------------
        ip_sequences.setdefault(src_ip, [])

        norm_features = normalize_features(packet_size, proto_val, packet_rate)
        ip_sequences[src_ip].append(norm_features)

        ip_sequences[src_ip] = ip_sequences[src_ip][-10:]

        lstm_score = 0

        if lstm_model and len(ip_sequences[src_ip]) == 10:
            sequence = np.array(ip_sequences[src_ip]).reshape((1, 10, 3))
            lstm_score = float(lstm_model.predict(sequence, verbose=0)[0][0])

        # --------------------------
        # RULE DETECTION
        # --------------------------
        rule_trigger = (
            packet_rate > 20 or
            packet_size > 1500 or
            protocol == "Other"
        )

        # --------------------------
        # FINAL DECISION
        # --------------------------
        if ml_pred == -1 or lstm_score > 0.6 or rule_trigger:

            score = 0
            if ml_pred == -1:
                score += 3
            if lstm_score > 0.6:
                score += 5
            if packet_rate > 20:
                score += 2

            # Severity
            if score >= 9:
                rating = "Critical"
            elif score >= 7:
                rating = "High"
            elif score >= 5:
                rating = "Medium"
            else:
                rating = "Low"

            attack_type = classify_attack(packet_size, packet_rate, protocol, unique_ports)

            alert = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "source_ip": src_ip,
                "destination_ip": dst_ip,
                "packet_size": packet_size,
                "protocol": protocol,
                "packet_rate": packet_rate,
                "ml_flag": int(ml_pred == -1),
                "lstm_score": round(lstm_score, 2),
                "ai_score": score,
                "rating": rating,
                "attack_type": attack_type
            }

            alerts.append(alert)
            socketio.emit("new_alert", alert)

            if len(alerts) > MAX_ALERTS:
                alerts.pop(0)

    except Exception as e:
        print("Error:", e)

# ==============================
# SNIFF THREAD
# ==============================
def start_sniffing():
    sniff(prn=process_packet, store=False)

# ==============================
# ROUTES
# ==============================
@app.route("/")
def home():
    return "🚀 ANOM-AI SOC Backend Running"

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
# RUN SERVER (FIXED THREADING)
# ==============================
if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        thread = threading.Thread(target=start_sniffing)
        thread.daemon = True
        thread.start()

    socketio.run(app, host="0.0.0.0", port=5000, debug=True)