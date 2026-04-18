import React from "react";
import { Link } from "react-router-dom";

function Topbar() {
  return (
    <div className="topbar">
      <span>🟢 System Active</span>
      <span>⚡ Live Monitoring</span>
      <Link to="/stored" style={{ color: "white" }}>Stored Alerts</Link>

    </div>
  );
}

export default Topbar;