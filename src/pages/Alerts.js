import React, { useState, useEffect } from "react";
import AlertsTable from "../components/AlertsTable";

function Alerts({ alerts }) {
  const [currentPage, setCurrentPage] = useState(1);
  const [filter, setFilter] = useState("ALL");

  const alertsPerPage = 10;

  /* ================= FILTER ================= */
  const filteredAlerts =
    filter === "ALL"
      ? alerts
      : alerts.filter(a => a?.rating === filter);

  /* ================= PAGINATION ================= */
  const indexOfLast = currentPage * alertsPerPage;
  const indexOfFirst = indexOfLast - alertsPerPage;
  const currentAlerts = filteredAlerts.slice(indexOfFirst, indexOfLast);

  const totalPages = Math.ceil(filteredAlerts.length / alertsPerPage);

  /* 🔥 RESET PAGE WHEN FILTER CHANGES */
  useEffect(() => {
    setCurrentPage(1);
  }, [filter]);

  return (
    <div className="dashboard">
      <h1>🚨 Alerts</h1>

      {/* ================= FILTER BUTTONS ================= */}
      <div className="filters">
        {["ALL", "Low", "Medium", "High", "Critical"].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={filter === f ? "active" : ""}
          >
            {f}
          </button>
        ))}
      </div>

      {/* ================= TABLE ================= */}
      <div className="table-container">
        <AlertsTable alerts={currentAlerts} />
      </div>

      {/* ================= PAGINATION ================= */}
      <div className="pagination">
        <button
          onClick={() => setCurrentPage(p => Math.max(p - 1, 1))}
          disabled={currentPage === 1}
        >
          ←
        </button>

        {Array.from({ length: totalPages }, (_, i) => i + 1)
          .slice(Math.max(currentPage - 2, 0), currentPage + 1)
          .map(p => (
            <button
              key={p}
              onClick={() => setCurrentPage(p)}
              className={currentPage === p ? "active" : ""}
            >
              {p}
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

export default Alerts;