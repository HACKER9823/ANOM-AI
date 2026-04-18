def generate_explanation(alert):
    reasons = []

    packet_rate = alert.get("packet_rate", 0)
    protocol = alert.get("protocol")
    ml_score = alert.get("isolation_forest_score", 0)
    lstm_score = alert.get("lstm_score", 0)
    severity = alert.get("severity", "")

    # ======================
    # Traffic behavior
    # ======================
    if packet_rate > 500:
        reasons.append("Very high traffic detected (possible flooding attack)")
    elif packet_rate > 100:
        reasons.append("Moderately high traffic observed")
    elif packet_rate > 50:
        reasons.append("Slight increase in traffic")

    # ======================
    # Protocol
    # ======================
    if protocol == "TCP":
        reasons.append("TCP traffic pattern analyzed")
    elif protocol == "UDP":
        reasons.append("UDP traffic pattern analyzed")
    else:
        reasons.append("Unusual protocol observed")

    # ======================
    # ML detection
    # ======================
    if ml_score < -0.2:
        reasons.append("Isolation Forest strongly indicates anomaly")
    elif ml_score < -0.1:
        reasons.append("Isolation Forest detected slight deviation")

    # ======================
    # LSTM detection (FIXED)
    # ======================
    if lstm_score > 0.11:   # ✅ use real threshold
        reasons.append("LSTM detected abnormal traffic sequence")

    # ======================
    # Severity reasoning
    # ======================
    if severity == "High":
        reasons.append("Multiple anomaly indicators triggered → High severity")
    elif severity == "Medium":
        reasons.append("Moderate anomaly detected")
    elif severity == "Low":
        reasons.append("Minor deviation from normal behavior")

    return " | ".join(reasons) if reasons else "Traffic appears normal"

print("🔥 NEW DETECTION LOGIC RUNNING")