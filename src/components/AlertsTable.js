import React from "react";
import AlertRow from "./AlertRow";

function AlertsTable({ alerts }) {
  return (
    <table>
      <thead>
  <tr>
    <th>Time</th>
    <th>Source IP</th>
    <th>Destination IP</th> 
    <th>Protocol</th>
    <th>Size</th>
    <th>Rate</th>
    <th>AI Score</th>
    <th>LSTM</th>
    <th>Rating</th>
    <th>Attack</th>
  </tr>
</thead>

      <tbody>
        {alerts.map((alert, index) => (
          <AlertRow key={index} alert={alert} />
        ))}
      </tbody>
    </table>
  );
}

export default AlertsTable;