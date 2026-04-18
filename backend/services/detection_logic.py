def calculate_severity(packet_rate, ml_score, lstm_score):

    score = 0

    # ======================
    # 📊 Traffic behavior
    # ======================
    if packet_rate > 800:
        score += 3
    elif packet_rate > 400:
        score += 2
    elif packet_rate > 150:
        score += 1

    # ======================
    # 🤖 ML anomaly
    # ======================
    if ml_score < -0.35:
        score += 2
    elif ml_score < -0.15:
        score += 1

    # ======================
    # 🧠 LSTM anomaly (balanced)
    # ======================
    if lstm_score > 0.35:
        score += 3
    elif lstm_score > 0.2:
        score += 2
    elif lstm_score > 0.12:
        score += 1

    # ======================
    # 🔥 COMBINATION BOOST (important)
    # ======================
    if packet_rate > 300 and lstm_score > 0.2:
        score += 1  # strong anomaly pattern

    if ml_score < -0.25 and lstm_score > 0.2:
        score += 1  # both models agree

    # ======================
    # 🧊 NORMALIZATION (reduce false positives)
    # ======================
    if packet_rate < 80 and ml_score > -0.1 and lstm_score < 0.15:
        score -= 1  # likely normal traffic

    # ======================
    # 🎯 FINAL SCALE
    # ======================
    if score >= 7:
        return "Critical"
    elif score >= 5:
        return "High"
    elif score >= 3:
        return "Medium"
    else:
        return "Low"


def detect_attack_type(packet_rate, protocol, packet_size=0, unique_ports=0):

    # ======================
    # 🔴 HIGH CONFIDENCE ATTACKS
    # ======================
    if packet_rate > 800:
        return "DDoS / Flood Attack"

    if packet_rate > 300 and protocol == "TCP":
        return "SYN Flood Attempt"

    # ======================
    # 🟠 SCANNING / PROBING
    # ======================
    if unique_ports > 20:
        return "Aggressive Port Scanning"

    if unique_ports > 10:
        return "Port Scanning Activity"

    # ======================
    # 🟡 TRAFFIC ANOMALIES
    # ======================
    if packet_rate > 150:
        return "Traffic Spike / Suspicious Burst"

    if packet_size > 1400:
        return "Large Packet Transfer"

    if protocol == "Other":
        return "Suspicious Protocol Usage"

    # ======================
    # 🟢 LOW RISK
    # ======================
    if packet_rate < 80 and unique_ports < 5:
        return "Likely Normal Traffic"

    return "Minor suspicious activity"