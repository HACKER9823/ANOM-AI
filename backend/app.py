from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

import numpy as np
from sklearn.ensemble import IsolationForest

from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP

from datetime import datetime, timedelta
import threading
import os

# ==============================
# DEEP LEARNING
# ==============================
from tensorflow.keras.models import load_model

# ==============================
# APP SETUP
# ==============================
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ==============================
# ML MODEL (Isolation Forest)
# ==============================
X_train = np.random.normal(loc=500, scale=50, size=(1000, 2))
ml_model = IsolationForest(contamination=0.05)
ml_model.fit(X_train)

# ==============================
# LOAD TRAINED LSTM MODEL
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

total_packets = 0
MAX_ALERTS = 300

# ==============================
# NORMALIZATION (MUST MATCH TRAINING)
# ==============================
def normalize_features(packet_size, proto_val, packet_rate):
    packet_size = packet_size / 2000.0
    packet_rate = packet_rate / 50.0
    return [packet_size, proto_val, packet_rate]

# ==============================
# ATTACK CLASSIFICATION
# ==============================
def classify_attack(packet_size, rate, protocol):
    if rate > 30:
        return "Flood Attempt"
    elif rate > 15:
        return "Port Scan"
    elif packet_size > 1600:
        return "Large Packet Attack"
    elif protocol == "Other":
        return "Unknown Protocol"
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

        # Protocol detection
        if packet.haslayer(TCP):
            protocol = "TCP"
            proto_val = 1
        elif packet.haslayer(UDP):
            protocol = "UDP"
            proto_val = 0
        else:
            protocol = "Other"
            proto_val = 0

        # ==========================
        # RATE CALCULATION
        # ==========================
        ip_stats[src_ip] = ip_stats.get(src_ip, 0) + 1

        now = datetime.now()
        packet_times.setdefault(src_ip, []).append(now)

        packet_times[src_ip] = [
            t for t in packet_times[src_ip]
            if now - t < timedelta(seconds=5)
        ]

        packet_rate = len(packet_times[src_ip])

        # ==========================
        # ML (Isolation Forest)
        # ==========================
        features = np.array([[packet_size, proto_val]])
        ml_pred = ml_model.predict(features)[0]  # -1 = anomaly

        # ==========================
        # LSTM SEQUENCE BUILD
        # ==========================
        ip_sequences.setdefault(src_ip, [])

        norm_features = normalize_features(packet_size, proto_val, packet_rate)
        ip_sequences[src_ip].append(norm_features)

        ip_sequences[src_ip] = ip_sequences[src_ip][-10:]

        lstm_score = 0

        if lstm_model and len(ip_sequences[src_ip]) == 10:
            sequence = np.array(ip_sequences[src_ip])
            sequence = sequence.reshape((1, 10, 3))

            lstm_score = float(lstm_model.predict(sequence, verbose=0)[0][0])

        # ==========================
        # RULE-BASED DETECTION
        # ==========================
        rule_trigger = (
            packet_rate > 20 or
            packet_size > 1500 or
            protocol == "Other"
        )

        # ==========================
        # FINAL DECISION
        # ==========================
        if ml_pred == -1 or lstm_score > 0.6 or rule_trigger:

            score = 0

            if ml_pred == -1:
                score += 3
            if lstm_score > 0.6:
                score += 5
            if packet_rate > 20:
                score += 2

            # Severity rating
            if score >= 9:
                rating = "Critical"
            elif score >= 7:
                rating = "High"
            elif score >= 5:
                rating = "Medium"
            else:
                rating = "Low"

            attack_type = classify_attack(packet_size, packet_rate, protocol)

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
# SNIFFING THREAD
# ==============================
def start_sniffing():
    sniff(prn=process_packet, store=False)

# ==============================
# ROUTES
# ==============================
@app.route("/")
def home():
    return "🚀 ANOM-AI SOC Backend Running with LSTM"

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
# RUN SERVER
# ==============================
if __name__ == "__main__":
    thread = threading.Thread(target=start_sniffing)
    thread.daemon = True
    thread.start()

    socketio.run(app, host="0.0.0.0", port=5000, debug=True)