import React, { useMemo } from "react";
import { LineChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-gray-900 text-white p-3 rounded-xl shadow-xl border border-cyan-500">
        <p className="text-cyan-400">{payload[0].payload.time}</p>
        <p className="text-lg font-bold">Alerts: <span className="text-white">{payload[0].value}</span></p>
      </div>
    );
  }
  return null;
};

function LiveChart({ data = [] }) {
  const processedData = useMemo(() => {
    return data.map((item, i) => ({
      time: item.time || `T+${i}`,
      count: item.count || 0,
      severityScore: item.severityScore || Math.random() * 10,
    }));
  }, [data]);

  return (
    <div className="bg-gray-950 border border-gray-800 rounded-3xl p-6 shadow-2xl">
      <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
        📈 Live Alerts Trend <span className="text-emerald-400 text-sm">(real-time)</span>
      </h3>
      <ResponsiveContainer width="100%" height={380}>
        <LineChart data={processedData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.4}/>
              <stop offset="95%" stopColor="#22d3ee" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="time" stroke="#64748b" tick={{ fill: "#64748b" }} />
          <YAxis stroke="#64748b" tick={{ fill: "#64748b" }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Area type="monotone" dataKey="count" stroke="#22d3ee" fillOpacity={1} fill="url(#colorCount)" />
          <Line type="monotone" dataKey="count" stroke="#22d3ee" strokeWidth={4} dot={{ r: 5, fill: "#67e8f9" }} activeDot={{ r: 8 }} />
          <Line type="monotone" dataKey="severityScore" stroke="#f43f5e" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default LiveChart;