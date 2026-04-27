import React, { useEffect, useState } from "react";
import axios from "axios";
import LiveChart from "../components/LiveChart";
import SeverityChart from "../components/SeverityChart";
import AttackTypeChart from "../components/AttackTypeChart";

function Analytics() {
  const [alerts, setAlerts] = useState([]);           // ← Master data
  const [liveData, setLiveData] = useState([]);
  const [severityData, setSeverityData] = useState([]);
  const [attackData, setAttackData] = useState([]);

  // Fetch ALL real alerts from backend (MongoDB)
  const fetchAlerts = async () => {
    try {
      const res = await axios.get("http://localhost:5000/alerts"); // ← Your existing endpoint
      const allAlerts = res.data || [];
      setAlerts(allAlerts);

      // 1. Build Severity Pie Data
      const severityCount = { Critical: 0, High: 0, Medium: 0, Low: 0 };
      allAlerts.forEach(a => {
        const rating = a.rating || a.severity || "Medium";
        severityCount[rating] = (severityCount[rating] || 0) + 1;
      });
      setSeverityData([
        { name: "Critical", value: severityCount.Critical },
        { name: "High", value: severityCount.High },
        { name: "Medium", value: severityCount.Medium },
        { name: "Low", value: severityCount.Low },
      ]);

      // 2. Build Attack Type Bar Data
      const attackCount = {};
      allAlerts.forEach(a => {
        const type = a.attack_type || "Unknown";
        attackCount[type] = (attackCount[type] || 0) + 1;
      });
      setAttackData(Object.entries(attackCount).map(([name, count]) => ({ name, count })));

      // 3. Live trend (last 20 alerts)
      const trend = allAlerts.slice(0, 20).map((a, i) => ({
        time: new Date(a.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        count: allAlerts.length - i,
        severityScore: a.ai_score || Math.random() * 10,
      }));
      setLiveData(trend.reverse());

    } catch (err) {
      console.warn("⚠️ Could not fetch alerts – using fallback data");
      // Fallback (only for demo)
      setAlerts([]);
      setSeverityData([
        { name: "Critical", value: 12 },
        { name: "High", value: 28 },
        { name: "Medium", value: 45 },
        { name: "Low", value: 15 },
      ]);
      setAttackData([
        { name: "DDoS", count: 18 },
        { name: "Port Scan", count: 25 },
        { name: "Brute Force", count: 9 },
      ]);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 7000); // refresh every 7s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8 bg-gray-950 min-h-screen">
      <h1 className="text-4xl font-bold text-white mb-8">📊 Analytics Dashboard</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <LiveChart data={liveData} />
        <SeverityChart data={severityData} />
        <AttackTypeChart data={attackData} />
      </div>

      {/* Real Alert Table – now synced with pie chart */}
      <div className="mt-12 bg-gray-900 border border-gray-800 rounded-3xl p-6">
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          📋 Recent Alerts ({alerts.length})
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-gray-300">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3">Time</th>
                <th className="text-left py-3">Source IP</th>
                <th className="text-left py-3">Attack Type</th>
                <th className="text-left py-3">Severity</th>
                <th className="text-left py-3">AI Score</th>
              </tr>
            </thead>
            <tbody>
              {alerts.slice(0, 15).map((alert, i) => (
                <tr key={i} className="border-b border-gray-800 hover:bg-gray-800">
                  <td className="py-3">{new Date(alert.timestamp).toLocaleTimeString()}</td>
                  <td className="py-3 font-mono">{alert.source_ip || alert.src_ip}</td>
                  <td className="py-3">{alert.attack_type}</td>
                  <td className="py-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold
                          ${alert.rating === "Critical" ? "bg-red-500" : 
                            alert.rating === "High" ? "bg-orange-500" : 
                            alert.rating === "Medium" ? "bg-yellow-500" : "bg-green-500"}`}>
                      {alert.rating || alert.severity}
                    </span>
                  </td>
                  <td className="py-3 font-mono">{alert.ai_score?.toFixed(2) || "—"}</td>
                </tr>
              ))}
              {alerts.length === 0 && (
                <tr>
                  <td colSpan="5" className="py-8 text-center text-gray-500">
                    No alerts yet. Run traffic simulation or connect real packets.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Analytics;