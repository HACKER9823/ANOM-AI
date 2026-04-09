import pandas as pd
import numpy as np

df = pd.read_csv("dataset2.csv")

# SELECT FEATURES (match your system)
features = [
    "packet_size",
    "connection_rate",
    "unique_dst_ports",
    "port_entropy",
    "connection_count_per_min",
    "large_packet_flag"
]

data = df[features].values

# CREATE SEQUENCES
def create_sequences(data, seq_length=10):
    sequences = []

    for i in range(len(data) - seq_length):
        sequences.append(data[i:i+seq_length])

    return np.array(sequences)

X = create_sequences(data)

print("Shape:", X.shape)