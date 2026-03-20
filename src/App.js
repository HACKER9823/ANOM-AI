import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useState, useEffect } from "react";

import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";

import Dashboard from "./pages/Dashboard";
import Alerts from "./pages/Alerts";
import Analytics from "./pages/Analytics";
import Network from "./pages/Network"; // ✅ ADD THIS

function App() {
  const [alerts, setAlerts] = useState([]);
  const [status, setStatus] = useState("Connecting...");

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch("http://127.0.0.1:5000/alerts");
        const data = await res.json();

        setAlerts([...data].reverse());
        setStatus("Live Monitoring Active ✅");
      } catch {
        setStatus("Backend not reachable ❌");
      }
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Router>
      <div className="layout">
        <Sidebar />

        <div className="main">
          <Topbar status={status} />

          <Routes>
            <Route path="/dashboard" element={<Dashboard alerts={alerts} status={status} />} />
            <Route path="/alerts" element={<Alerts alerts={alerts} />} />
            <Route path="/analytics" element={<Analytics alerts={alerts} />} />
            <Route path="/network" element={<Network alerts={alerts} />} /> {/* ✅ */}
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;