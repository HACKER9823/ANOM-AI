import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

const COLORS = ["#ef4444", "#f97316", "#facc15", "#22c55e"]; 
// Critical, High, Medium, Low

function SeverityChart({ data }) {
  return (
    <div style={{ textAlign: "center" }}>
      <h3>Severity Distribution</h3>

      <PieChart width={350} height={300}>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          outerRadius={100}
        >
          {data.map((entry, index) => (
            <Cell key={index} fill={COLORS[index]} />
          ))}
        </Pie>

        <Tooltip />
        <Legend />
      </PieChart>
    </div>
  );
}

export default SeverityChart;