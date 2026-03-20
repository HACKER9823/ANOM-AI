import React from "react";
import SeverityChart from "../components/SeverityChart";
import LiveChart from "../components/LiveChart";

function Analytics({ alerts }) {
  const critical = alerts.filter(a => a?.rating === "Critical").length;
  const high = alerts.filter(a => a?.rating === "High").length;
  const medium = alerts.filter(a => a?.rating === "Medium").length;
  const low = alerts.filter(a => a?.rating === "Low").length;

  const chartData = [
    { name: "Critical", value: critical },
    { name: "High", value: high },
    { name: "Medium", value: medium },
    { name: "Low", value: low }
  ];

  const liveData = alerts.slice(0, 10).map((a, i) => ({
    time: a.timestamp?.split(" ")[1] || i,
    count: i + 1
  }));

  return (
    <div className="dashboard">
      <h1>📈 Analytics</h1>

      <div className="charts">
        <SeverityChart data={chartData} />
        <LiveChart data={liveData} />
      </div>
    </div>
  );
}

export default Analytics;