import { useLocation } from "react-router-dom";

function AlertDetails() {
  const location = useLocation();
  const alert = location.state;

  if (!alert) {
    return <div className="no-data">No alert data found</div>;
  }

  return (
    <div className="details-card">
      <h2 className="alert-title">🚨 Alert Details</h2>
      <p className="alert-info"><b>Time:</b> <span className="alert-value">{alert.timestamp}</span></p>
      <p className="alert-info"><b>Source IP:</b> <span className="alert-value">{alert.source_ip}</span></p>
      <p className="alert-info"><b>Destination IP:</b> <span className="alert-value">{alert.destination_ip}</span></p>
      <p className="alert-info"><b>Protocol:</b> <span className="alert-value">{alert.protocol}</span></p>
      <p className="alert-info"><b>Packet Size:</b> <span className="alert-value">{alert.packet_size}</span></p>
      <p className="alert-info"><b>AI Score:</b> <span className="alert-value">{alert.ai_score}</span></p>
      <p className="alert-info"><b>LSTM Score:</b> <span className="alert-value">{alert.lstm_score}</span></p>
      <p className="alert-info"><b>Rating:</b> <span className="alert-value">{alert.rating}</span></p>
      <p className="alert-info"><b>Attack Type:</b> <span className="alert-value">{alert.attack_type}</span></p>
      <button className="back-btn" onClick={() => window.history.back()}>⬅ Back</button>
    </div>
  );
}

export default AlertDetails;