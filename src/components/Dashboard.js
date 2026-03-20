import React, { useState, useEffect } from "react";
import AlertsTable from "./AlertsTable";
import StatusBar from "./StatusBar";

function Dashboard() {
  const [alerts, setAlerts] = useState([]);
  const [status, setStatus] = useState("Connecting...");
  const [currentPage, setCurrentPage] = useState(1);
  const [filter, setFilter] = useState("ALL");

  const alertsPerPage = 10;

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch("http://127.0.0.1:5000/alerts");
        const data = await res.json();
        setAlerts(data.reverse());
        setStatus("Live Monitoring Active ✅");
      } catch {
        setStatus("Backend not reachable ❌");
      }
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 3000);
    return () => clearInterval(interval);
  }, []);

  // 📊 METRICS
  const critical = alerts.filter(a => a.rating === "Critical").length;
  const high = alerts.filter(a => a.rating === "High").length;
  const low = alerts.filter(a => a.rating === "Low").length;
  const medium = alerts.filter(a => a.rating === "Medium").length;

  // FILTER
  const filteredAlerts =
    filter === "ALL" ? alerts : alerts.filter(a => a.rating === filter);

  // PAGINATION
  const indexOfLast = currentPage * alertsPerPage;
  const indexOfFirst = indexOfLast - alertsPerPage;
  const currentAlerts = filteredAlerts.slice(indexOfFirst, indexOfLast);

  const totalPages = Math.ceil(filteredAlerts.length / alertsPerPage);

  return (
    <div className="dashboard">

      <h1>🛡 ANOM-AI Security Dashboard</h1>

      <StatusBar status={status} count={alerts.length} />

      {/* 🔥 METRIC CARDS */}
      <div className="metrics">

  <div className="card total">
    🚨 Total Alerts
    <span>{alerts.length}</span>
  </div>

  <div className="card critical">
    🔥 Critical
    <span>{critical}</span>
  </div>

  <div className="card high">
    ⚠ High
    <span>{high}</span>
  </div>

  <div className="card medium">
    ⚡ Medium
    <span>{medium}</span>
  </div>

  <div className="card low">
    ✅ Low
    <span>{low}</span>
  </div>

</div>

      {/* FILTER */}
      <div className="filters">
        {["ALL", "Low", "Medium", "High", "Critical"].map(f => (
          <button
            key={f}
            onClick={() => {
              setFilter(f);
              setCurrentPage(1);
            }}
            className={filter === f ? "active" : ""}
          >
            {f}
          </button>
        ))}
      </div>

      <AlertsTable alerts={currentAlerts} />

      {/* PAGINATION */}
      <div className="pagination">
        <button
          onClick={() => setCurrentPage(p => Math.max(p - 1, 1))}
          disabled={currentPage === 1}
        >
          ←
        </button>

        {Array.from({ length: totalPages }, (_, i) => i + 1)
          .slice(Math.max(currentPage - 3, 0), currentPage + 2)
          .map(page => (
            <button
              key={page}
              onClick={() => setCurrentPage(page)}
              className={currentPage === page ? "active" : ""}
            >
              {page}
            </button>
          ))}

        <button
          onClick={() => setCurrentPage(p => Math.min(p + 1, totalPages))}
          disabled={currentPage === totalPages}
        >
          →
        </button>
      </div>

    </div>
  );
}

export default Dashboard;