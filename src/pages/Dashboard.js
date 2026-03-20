import React from "react";
import StatusBar from "../components/StatusBar";

function Dashboard({ alerts, status }) {
  const critical = alerts.filter(a => a?.rating === "Critical").length;
  const high = alerts.filter(a => a?.rating === "High").length;
  const medium = alerts.filter(a => a?.rating === "Medium").length;
  const low = alerts.filter(a => a?.rating === "Low").length;

  return (
    <div className="dashboard">
      <h1>🛡 ANOM-AI Dashboard</h1>

      <StatusBar status={status} count={alerts.length} />

      <div className="metrics">
        <div className="card total">🚨 Total <span>{alerts.length}</span></div>
        <div className="card critical">🔥 Critical <span>{critical}</span></div>
        <div className="card high">⚠ High <span>{high}</span></div>
        <div className="card medium">⚡ Medium <span>{medium}</span></div>
        <div className="card low">✅ Low <span>{low}</span></div>
      </div>
    </div>
  );
}

export default Dashboard;