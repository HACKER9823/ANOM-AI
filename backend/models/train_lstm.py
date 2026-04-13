import pandas as pd
import numpy as np
import torch
import joblib
import os

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
try:
    df = pd.read_csv(DATA_PATH)
    print("✅ Dataset loaded")
except Exception as e:
    print("❌ Error loading dataset:", e)
    exit()

# ==============================
# SELECT FEATURES (MATCH APP.PY)
# ==============================
features = [
    "packet_size",
    "connection_rate",
    "unique_dst_ports",
    "port_entropy",
    "connection_count_per_min",
    "large_packet_flag"
]

missing = [f for f in features if f not in df.columns]
if missing:
    print("❌ Missing columns:", missing)
    exit()

data = df[features].fillna(0).values

# ==============================
# CREATE SEQUENCES
# ==============================
def create_sequences(data, seq_length=10):
    sequences = []

    for i in range(len(data) - seq_length):
        sequences.append(data[i:i+seq_length])

    return np.array(sequences)

X = create_sequences(data)

print("✅ Sequence shape:", X.shape)

# ==============================
# NORMALIZE
# ==============================
scaler = MinMaxScaler()

X_reshaped = X.reshape(-1, X.shape[-1])
X_scaled = scaler.fit_transform(X_reshaped)
X_scaled = X_scaled.reshape(X.shape)

# ==============================
# MODEL
# ==============================
model = LSTMModel(input_size=6)

criterion = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

inputs = torch.tensor(X_scaled, dtype=torch.float32)

# ==============================
# TRAINING LOOP
# ==============================
for epoch in range(20):
    outputs = model(inputs)

    loss = criterion(outputs, inputs)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(f"Epoch {epoch}, Loss: {loss.item()}")

# ==============================
# CALCULATE THRESHOLD 🔥
# ==============================
model.eval()
scores = []

with torch.no_grad():
    for seq in X_scaled:
        tensor = torch.tensor([seq], dtype=torch.float32)
        output = model(tensor)

        error = torch.mean((tensor - output) ** 2).item()
        scores.append(error)

scores = np.array(scores)

# 95th percentile → anomaly threshold
threshold = np.percentile(scores, 95)

print(f"✅ LSTM Threshold: {threshold}")

# ==============================
# SAVE EVERYTHING
# ==============================
torch.save(model.state_dict(), os.path.join(MODEL_DIR, "lstm.pth"))
joblib.dump(scaler, os.path.join(MODEL_DIR, "lstm_scaler.pkl"))
joblib.dump(threshold, os.path.join(MODEL_DIR, "lstm_threshold.pkl"))

print("✅ LSTM trained on dataset2 & saved successfully")