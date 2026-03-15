import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link
} from "react-router-dom";
import "./App.css";


// ✅ AlertsPage MUST BE HERE (above App)
function AlertsPage({ filter }) {
  const [alerts, setAlerts] = useState([]);
  const [status, setStatus] = useState("Connecting...");
  const [currentPage, setCurrentPage] = useState(1);

  const alertsPerPage = 10;

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/alerts");
        const data = await response.json();

        const normalizedData = data.map((a) => ({
          ...a,
          severity: a.severity || "Unknown",
        }));

        if (filter) {
          setAlerts(
            normalizedData.filter((a) => a.severity === filter)
          );
        } else {
          setAlerts(normalizedData);
        }

        setStatus("Live Monitoring Active ✅");
      } catch (error) {
        console.error(error);
        setStatus("Backend not reachable ❌");
      }
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 3000);
    return () => clearInterval(interval);
  }, [filter]);

  // Pagination Logic
  const indexOfLast = currentPage * alertsPerPage;
  const indexOfFirst = indexOfLast - alertsPerPage;
  const currentAlerts = alerts.slice(indexOfFirst, indexOfLast);

  const totalPages = Math.ceil(alerts.length / alertsPerPage);

  return (
    <div className="dashboard">
      <h2>{filter ? `${filter} Alerts` : "All Alerts"}</h2>
      <div className="status">{status}</div>

      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Source IP</th>
            <th>Destination IP</th>
            <th>Protocol</th>
            <th>Packet Size</th>
            <th>Severity</th>
          </tr>
        </thead>

        <tbody>
          {currentAlerts.map((alert, index) => (
            <tr key={index} className={alert.severity.toLowerCase()}>
              <td>{alert.timestamp}</td>
              <td>{alert.source_ip}</td>
              <td>{alert.destination_ip}</td>
              <td>{alert.protocol}</td>
              <td>{alert.packet_size}</td>
              <td>{alert.severity}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination Controls */}
      <div className="pagination">
        <button
          onClick={() => setCurrentPage(currentPage - 1)}
          disabled={currentPage === 1}
        >
          ⬅ Previous
        </button>

        <span>
          Page {currentPage} / {totalPages || 1}
        </span>

        <button
          onClick={() => setCurrentPage(currentPage + 1)}
          disabled={currentPage === totalPages || totalPages === 0}
        >
          Next ➡
        </button>
      </div>
    </div>
  );
}


// ✅ App BELOW AlertsPage
function App() {
  return (
    <Router>
      <div className="App">
        <h1>🛡 ANOM-AI Security Monitor</h1>

        <nav className="nav">
          <Link to="/">All</Link>
          <Link to="/high">High</Link>
          <Link to="/medium">Medium</Link>
          <Link to="/low">Low</Link>
        </nav>

        <Routes>
          <Route path="/" element={<AlertsPage />} />
          <Route path="/high" element={<AlertsPage filter="High" />} />
          <Route path="/medium" element={<AlertsPage filter="Medium" />} />
          <Route path="/low" element={<AlertsPage filter="Low" />} />
        </Routes>

      </div>
    </Router>
  );
}

export default App;