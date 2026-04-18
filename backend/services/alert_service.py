from db import alerts_collection
from datetime import datetime
from services.explanation_service import generate_explanation

def create_alert(packet, score, model, severity):

    alert = {
        "timestamp": datetime.utcnow(),

        # ✅ your actual fields
        "source_ip": packet.get("src_ip"),
        "destination_ip": packet.get("dst_ip"),
        "protocol": packet.get("protocol"),
        "packet_size": packet.get("packet_size"),
        "packet_rate": packet.get("packet_rate"),

        # ✅ your ML fields
        "ml_score": float(score) if model == "IsolationForest" else None,
        "lstm_score": float(score) if model == "LSTM" else None,

        "ai_score": packet.get("ai_score", 0),

        "rating": severity,
        "attack_type": packet.get("attack_type", "Unknown"),
        "status": "NEW"
    }

    # 🧠 FIXED explanation mapping
    alert["explanation"] = generate_explanation({
        "packet_rate": alert.get("packet_rate", 0),
        "protocol": alert.get("protocol"),
        "lstm_score": alert.get("lstm_score", 0),
        "isolation_forest_score": alert.get("ml_score", 0),
        "severity": alert.get("rating")
    })

    alerts_collection.insert_one(alert)
    return alert