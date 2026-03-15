from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import numpy as np
from sklearn.ensemble import IsolationForest
from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP
from datetime import datetime, timedelta
import threading

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ==============================
# AI MODEL
# ==============================
X_train = np.random.normal(loc=500, scale=50, size=(1000, 2))
model = IsolationForest(contamination=0.05)
model.fit(X_train)

# ==============================
# GLOBAL STATE
# ==============================
alerts = []
ip_stats = {}
packet_times = {}
total_packets = 0
MAX_ALERTS = 300

# ==============================
# ATTACK CLASSIFICATION
# ==============================
def classify_attack(packet_size, ip_count, protocol):
    if ip_count > 30:
        return "Flood Attempt"
    if ip_count > 15:
        return "Port Scan"
    if packet_size > 1600:
        return "Suspicious Large Packet"
    if protocol == "Other":
        return "Unknown Protocol Abuse"
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
            proto_val = 1
        elif packet.haslayer(UDP):
            protocol = "UDP"
            proto_val = 0
        else:
            protocol = "Other"
            proto_val = 0

        # IP statistics
        ip_stats[src_ip] = ip_stats.get(src_ip, 0) + 1

        # Time-window tracking
        now = datetime.now()
        packet_times.setdefault(src_ip, []).append(now)
        packet_times[src_ip] = [
            t for t in packet_times[src_ip]
            if now - t < timedelta(seconds=5)
        ]

        burst_count = len(packet_times[src_ip])

        # ML prediction
        features = np.array([[packet_size, proto_val]])
        prediction = model.predict(features)

        if prediction[0] == -1 or burst_count > 20:
            # Attack classification without severity
            attack_type = classify_attack(
                packet_size,
                burst_count,
                protocol
            )

            alert = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "source_ip": src_ip,
                "destination_ip": dst_ip,
                "packet_size": packet_size,
                "protocol": protocol,
                "attack_type": attack_type,
                "packet_rate": burst_count,
                "status": "Anomaly Detected 🚨"
            }

            alerts.append(alert)
            socketio.emit("new_alert", alert)

            if len(alerts) > MAX_ALERTS:
                alerts.pop(0)

    except Exception as e:
        print("Packet error:", e)

# ==============================
# SNIFF THREAD
# ==============================
def start_sniffing():
    sniff(prn=process_packet, store=False)

# ==============================
# API ROUTES
# ==============================
@app.route("/")
def home():
    return "ANOM-AI Advanced Live Monitoring 🚀"

@app.route("/alerts")
def get_alerts():
    return jsonify(alerts)

@app.route("/stats")
def get_stats():
    return jsonify({
        "total_packets": total_packets,
        "unique_ips": len(ip_stats),
        "top_ips": sorted(ip_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    })

@app.route("/anomalies")
def get_anomalies():
    # Return anomalies without severity
    anomalies = [{"timestamp": alert["timestamp"], 
                  "source_ip": alert["source_ip"], 
                  "attack_type": alert["attack_type"]} 
                 for alert in alerts]
    return jsonify(anomalies)

# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    sniff_thread = threading.Thread(target=start_sniffing)
    sniff_thread.daemon = True
    sniff_thread.start()

    socketio.run(app, host="0.0.0.0", port=5000, debug=True)