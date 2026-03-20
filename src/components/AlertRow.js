import React from "react";

function AlertRow({ alert }) {
  const rating = alert?.rating?.toLowerCase() || "low";

  return (
    <tr
      className={`
        ${rating}
        glow-${rating}
        ${rating === "critical" ? "blink" : ""}
      `}
    >
      <td>{alert.timestamp}</td>

      <td>{alert.source_ip}</td>

      <td>{alert.destination_ip}</td>

      <td>{alert.protocol}</td>

      <td>{alert.packet_size}</td>

      <td>{alert.packet_rate || "-"}</td>

      {/* 🔥 AI SCORE BAR */}
      <td>
        <div className="progress">
          <div
            className="progress-fill"
            style={{
              width: `${Math.min(alert.ai_score * 10, 100)}%`
            }}
          />
        </div>
      </td>

      {/* 🧠 LSTM SCORE */}
      <td className="lstm">
        {alert.lstm_score
          ? `${(alert.lstm_score * 100).toFixed(0)}%`
          : "-"}
      </td>

      {/* 🎯 SEVERITY BADGE */}
      <td>
        <span className={`badge ${rating}`}>
          {alert.rating}
        </span>
      </td>

      {/* ⚠️ ATTACK TYPE */}
      <td>{alert.attack_type || "Unknown"}</td>
    </tr>
  );
}

export default AlertRow;