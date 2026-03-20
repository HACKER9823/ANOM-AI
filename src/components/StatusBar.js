import React from "react";

function StatusBar({ status, count }) {
  return (
    <>
      <div className="status">{status}</div>
      <div className="alert-count">🚨 Total Alerts: {count}</div>
    </>
  );
}

export default StatusBar;