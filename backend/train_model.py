import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Load dataset
df = pd.read_csv("dataset2.csv")

# -------------------------------
# 🔥 Select ONLY valid features
# -------------------------------
features = [
    "packet_size",
    "connection_rate",
    "flow_duration",
    "src_port",
    "dst_port",
    "unique_dst_ports",
    "port_entropy",
    "packet_size_zscore",
    "rate_vs_duration_ratio",
    "large_packet_flag",
    "connection_count_per_min",
    "src_ip_frequency",
    "icmp_ratio"
]

X = df[features]

# -------------------------------
# ⚡ Scale features (VERY IMPORTANT)
# -------------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Save scaler
joblib.dump(scaler, "scaler.pkl")

# -------------------------------
# 🧠 Train Isolation Forest
# -------------------------------
model = IsolationForest(
    n_estimators=150,
    contamination=0.15,   # because your dataset has ~20% anomalies
    random_state=42
)

model.fit(X_scaled)

# Save model
joblib.dump(model, "isolation_model.pkl")

print("✅ Model trained successfully on dataset2")