import pandas as pd
import numpy as np
import joblib
import torch
import os

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler

from lstm_model import LSTMModel

# ==============================
# PATHS
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "datasets", "dataset2.csv")
MODEL_DIR = os.path.join(BASE_DIR, "trained_model_files")

os.makedirs(MODEL_DIR, exist_ok=True)

# ==============================
# LOAD DATASET
# ==============================
df = pd.read_csv(DATA_PATH)
print("✅ Dataset loaded for threshold tuning")

# ==============================
# ML FEATURES
# ==============================
ml_features = [
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

X = df[ml_features].fillna(0)

# ==============================
# SCALE
# ==============================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ==============================
# TRAIN ISOLATION FOREST
# ==============================
ml_model = IsolationForest(
    n_estimators=150,
    contamination=0.1,
    random_state=42
)

ml_model.fit(X_scaled)

# ==============================
# AUTO ML THRESHOLD
# ==============================
scores = ml_model.decision_function(X_scaled)

# lower = more anomalous
ML_THRESHOLD = np.percentile(scores, 5)   # bottom 5% = anomalies

joblib.dump(ML_THRESHOLD, os.path.join(MODEL_DIR, "ml_threshold.pkl"))

print("✅ ML Threshold:", ML_THRESHOLD)

# ==============================
# LSTM FEATURES
# ==============================
lstm_features = [
    "packet_size",
    "connection_rate",
    "unique_dst_ports",
    "port_entropy",
    "connection_count_per_min",
    "large_packet_flag"
]

data = df[lstm_features].fillna(0).values

# ==============================
# CREATE SEQUENCES
# ==============================
def create_sequences(data, seq_length=10):
    sequences = []
    for i in range(len(data) - seq_length):
        sequences.append(data[i:i+seq_length])
    return np.array(sequences)

X_seq = create_sequences(data)

# ==============================
# SCALE LSTM
# ==============================
lstm_scaler = MinMaxScaler()

X_reshaped = X_seq.reshape(-1, X_seq.shape[-1])
X_scaled = lstm_scaler.fit_transform(X_reshaped)
X_scaled = X_scaled.reshape(X_seq.shape)

# ==============================
# LOAD TRAINED LSTM
# ==============================
lstm_model = LSTMModel(input_size=6)
lstm_model.load_state_dict(torch.load(os.path.join(MODEL_DIR, "lstm.pth")))
lstm_model.eval()

# ==============================
# COMPUTE RECONSTRUCTION ERROR
# ==============================
errors = []

with torch.no_grad():
    for seq in X_scaled[:2000]:   # limit for speed
        tensor = torch.tensor([seq], dtype=torch.float32)
        output = lstm_model(tensor)

        loss = torch.mean((tensor - output) ** 2).item()
        errors.append(loss)

# ==============================
# AUTO LSTM THRESHOLD
# ==============================
LSTM_THRESHOLD = np.percentile(errors, 95)  # top 5% anomalies

joblib.dump(LSTM_THRESHOLD, os.path.join(MODEL_DIR, "lstm_threshold.pkl"))

print("✅ LSTM Threshold:", LSTM_THRESHOLD)

print("\n🎯 Auto-threshold tuning COMPLETE")