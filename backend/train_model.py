import numpy as np
from sklearn.ensemble import IsolationForest

# Load data
data = np.loadtxt("traffic_log.csv", delimiter=",")

# Train model
model = IsolationForest(contamination=0.05)
model.fit(data)

# Save model
import joblib
joblib.dump(model, "ml_model.pkl")

print("✅ Model trained on real traffic")