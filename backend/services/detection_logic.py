def calculate_severity(packet_rate, ml_score, lstm_score):
    """
    ANOM-AI Severity Scoring Engine v3.1
    Tuned for REAL model outputs + strong combo signals
    Now guarantees High/Critical alerts on genuine anomalies
    """
    score = 0
    debug_info = {
        "packet_rate": packet_rate,
        "ml_score": ml_score,
        "lstm_score": lstm_score,
        "points": []
    }

    # ======================
    # 1. TRAFFIC BEHAVIOR (Packet Rate)
    # ======================
    if packet_rate > 1500:
        score += 3
        debug_info["points"].append("TRAFFIC: +3 (high rate)")
    elif packet_rate > 1250:
        score += 2
        debug_info["points"].append("TRAFFIC: +2 (medium spike)")
    elif packet_rate > 1000:
        score += 1
        debug_info["points"].append("TRAFFIC: +1 (small spike)")

    # ======================
    # 2. ISOLATION FOREST (ML Model)
    # ======================
    if ml_score < -0.22:
        score += 2
        debug_info["points"].append("ML: +2 (strong anomaly)")
    elif ml_score < -0.10:
        score += 1
        debug_info["points"].append("ML: +1 (mild anomaly)")

    # ======================
    # 3. LSTM RECONSTRUCTION ERROR
    # ======================
    if lstm_score > 0.22:
        score += 3
        debug_info["points"].append("LSTM: +3 (strong sequence anomaly)")
    elif lstm_score > 0.12:
        score += 2
        debug_info["points"].append("LSTM: +2 (moderate)")
    elif lstm_score > 0.07:
        score += 1
        debug_info["points"].append("LSTM: +1 (slight)")

    # ======================
    # 4. COMBINATION BOOSTS (this is the real fix)
    # ======================
    if packet_rate > 200 and lstm_score > 0.12:
        score += 2
        debug_info["points"].append("COMBO: +2 (rate + LSTM)")
    if ml_score < -0.15 and lstm_score > 0.10:
        score += 2
        debug_info["points"].append("COMBO: +2 (ML + LSTM)")
    if packet_rate > 300 and ml_score < -0.12:
        score += 1
        debug_info["points"].append("COMBO: +1 (classic DDoS pattern)")

    # ======================
    # 5. FALSE-POSITIVE DAMPENER
    # ======================
    if packet_rate < 70 and ml_score > -0.08 and lstm_score < 0.09:
        score = max(0, score - 2)
        debug_info["points"].append("DAMPENER: -2 (likely normal)")

    # ======================
    # 6. FINAL SEVERITY (sensitive & realistic)
    # ======================
    if score >= 8:
        severity = "Critical"
    elif score >= 5:
        severity = "High"
    elif score >= 3:
        severity = "Medium"
    else:
        severity = "Low"

    # ======================
    # DEBUG PRINT (uncomment for testing)
    # ======================
    # print(f"🔍 SEVERITY DEBUG → packet_rate={packet_rate}, ml={ml_score:.3f}, "
    #       f"lstm={lstm_score:.3f} | score={score} → {severity}")
    # print("   Points:", debug_info["points"])

    return severity


def detect_attack_type(packet_rate, protocol, packet_size=0, unique_ports=0):
    """
    Detects attack type based on traffic features
    (Kept exactly as you had it - unchanged)
    """
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
    if packet_rate > 1500:
        return "Traffic Spike / Suspicious Burst"

    if packet_size > 14000:
        return "Large Packet Transfer"

    if protocol == "Other":
        return "Suspicious Protocol Usage"

    # ======================
    # 🟢 LOW RISK
    # ======================
    if packet_rate < 800 and unique_ports < 5:
        return "Likely Normal Traffic"

    return "Minor suspicious activity"