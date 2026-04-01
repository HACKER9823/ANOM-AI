import torch
import numpy as np
from lstm_model import LSTMModel

# generate dummy normal traffic
def generate_data():
    data = []
    for _ in range(1000):
        seq = []
        for _ in range(10):
            packet_size = np.random.normal(500, 50)
            rate = np.random.normal(20, 5)
            protocol = np.random.choice([0, 1])  # TCP=0 UDP=1
            seq.append([packet_size, rate, protocol])
        data.append(seq)
    return np.array(data, dtype=np.float32)

data = generate_data()

model = LSTMModel()
criterion = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# training
for epoch in range(10):
    inputs = torch.tensor(data)
    targets = inputs[:, -1, :]

    outputs = model(inputs)
    loss = criterion(outputs, targets)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(f"Epoch {epoch}, Loss: {loss.item()}")

# save model
torch.save(model.state_dict(), "lstm.pth")