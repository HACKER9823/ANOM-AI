import React from "react";
import { Link, useLocation } from "react-router-dom";

function Sidebar() {
  const location = useLocation();

  return (
    <div className="sidebar">
      <h2>ANOM-AI</h2>

      <ul>
        <li className={location.pathname === "/" ? "active" : ""}>
          <Link to="/dashboard">📊 Dashboard</Link>
        </li>

        <li className={location.pathname === "/alerts" ? "active" : ""}>
          <Link to="/alerts">🚨 Alerts</Link>
        </li>

        <li className={location.pathname === "/analytics" ? "active" : ""}>
          <Link to="/analytics">🧠 AI Insights</Link>
        </li>

        <li className={location.pathname === "/network" ? "active" : ""}>
          <Link to="/network">🌐 Network</Link>
        </li>
      </ul>
    </div>
  );
}

export default Sidebar;