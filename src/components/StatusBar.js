import React from "react";

function StatusBar({ status, count }) {
  return (
    <div className="status-bar">
      <div className="status-left">
        <span className="pulse"></span>
        <span className="status-text">{status}</span>
      </div>

      <div className="alert-count">
        🚨 Total Alerts: {count}
      </div>
    </div>
  );
}

export default StatusBar;