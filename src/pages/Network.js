import React from "react";

function Network({ alerts }) {

  // 🔥 Count IP activity
  const ipCount = {};

  alerts.forEach(a => {
    ipCount[a.source_ip] = (ipCount[a.source_ip] || 0) + 1;
  });

  // 🔥 Convert to array + sort
  const topIPs = Object.entries(ipCount)
    .map(([ip, count]) => ({ ip, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  return (
    <div className="dashboard">
      <h1>🌐 Network Overview</h1>

      <h3>Top Active Source IPs</h3>

      <table>
        <thead>
          <tr>
            <th>IP Address</th>
            <th>Packets</th>
          </tr>
        </thead>

        <tbody>
          {topIPs.map((item, index) => (
            <tr key={index}>
              <td>{item.ip}</td>
              <td>{item.count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Network;