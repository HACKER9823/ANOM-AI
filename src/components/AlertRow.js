import React from "react";

function AlertRow({ alert }) {
  return (
    <tr className={alert.rating.toLowerCase()}>
      <td>{alert.timestamp}</td>
      <td>{alert.source_ip}</td>
      <td>{alert.protocol}</td>
      <td>{alert.packet_size}</td>
      <td>{alert.packet_rate}</td>

      <td className="score">{alert.ai_score}</td>

      <td className="lstm">
        {(alert.lstm_score * 100).toFixed(0)}%
      </td>

      <td>
        <span className={`badge ${alert.rating.toLowerCase()}`}>
          {alert.rating}
        </span>
      </td>

      <td>{alert.attack_type}</td>
    </tr>
  );
}

export default AlertRow;