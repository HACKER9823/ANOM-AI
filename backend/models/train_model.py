import pandas as pd
import joblib
import os

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ==============================
# PATH SETUP
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "datasets", "dataset2.csv")
MODEL_DIR = os.path.join(BASE_DIR, "trained_model_files")

os.makedirs(MODEL_DIR, exist_ok=True)

# ==============================
# LOAD DATA
# ==============================
df = pd.read_csv(DATA_PATH)

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

X = df[features].fillna(0)

# ==============================
# SCALE (IMPORTANT FIX)
# ==============================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 🔥 FIX: keep feature names
X_scaled = pd.DataFrame(X_scaled, columns=features)

# Save scaler
joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))

# ==============================
# TRAIN MODEL
# ==============================
model = IsolationForest(
    n_estimators=150,
    contamination=0.15,
    random_state=42,
    n_jobs=-1
)

model.fit(X_scaled)

# Save model
joblib.dump(model, os.path.join(MODEL_DIR, "isolation_model.pkl"))

print("✅ Model trained without warnings")