import React, { useEffect, useState } from "react";
import axios from "axios";
import AlertRow from "../components/AlertRow";

const StoredAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      const res = await axios.get("http://localhost:5000/alerts");
      setAlerts(res.data.reverse()); // latest first
    } catch (err) {
      console.error("Error fetching alerts:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>📂 Stored Alerts</h2>

      {loading ? (
        <p>Loading...</p>
      ) : alerts.length === 0 ? (
        <p>No alerts found</p>
      ) : (
        alerts.map((alert, index) => (
  <AlertRow key={index} alert={alert} />
))
      )}
    </div>
  );
};

export default StoredAlerts;