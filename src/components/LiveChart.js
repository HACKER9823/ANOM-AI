import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";

function LiveChart({ data }) {
  return (
    <div style={{ textAlign: "center" }}>
      <h3>Live Alerts Trend</h3>

      <LineChart width={500} height={300} data={data}>
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />

        {/* 🔥 Add stroke color */}
        <Line
          type="monotone"
          dataKey="count"
          stroke="#38bdf8"
          strokeWidth={2}
        />
      </LineChart>
    </div>
  );
}

export default LiveChart;