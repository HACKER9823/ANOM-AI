import torch
import numpy as np
import joblib
from models.lstm_model import LSTMModel

# ==============================
# LOAD MODEL
# ==============================
model = LSTMModel(input_size=6)
model.load_state_dict(torch.load("models/lstm.pth"))
model.eval()

scaler = joblib.load("models/lstm_scaler.pkl")
threshold = joblib.load("models/lstm_threshold.pkl")

print("✅ Threshold:", threshold)

# ==============================
# GENERATE TEST DATA
# ==============================
def generate_test_data():
    data = []

    for _ in range(5):
        seq = []
        for _ in range(10):
            packet_size = np.random.normal(500, 50)
            packet_rate = np.random.normal(20, 5)
            unique_ports = np.random.randint(1, 5)

            port_entropy = unique_ports / 10
            conn_per_min = packet_rate * 10
            large_flag = 1 if packet_size > 1400 else 0

            seq.append([
                packet_size,
                packet_rate,
                unique_ports,
                port_entropy,
                conn_per_min,
                large_flag
            ])

        data.append(seq)

    return np.array(data, dtype=np.float32)

data = generate_test_data()

# ==============================
# NORMALIZE
# ==============================
reshaped = data.reshape(-1, data.shape[-1])
scaled = scaler.transform(reshaped)
scaled = scaled.reshape(data.shape)

# ==============================
# TEST
# ==============================
with torch.no_grad():
    for i, seq in enumerate(scaled):
        tensor = torch.tensor([seq], dtype=torch.float32)
        output = model(tensor)

        error = torch.mean((tensor - output) ** 2).item()

        if error > threshold:
            status = "🚨 Anomaly"
        else:
            status = "✅ Normal"

        print(f"Sample {i}: Error={error:.5f} → {status}")