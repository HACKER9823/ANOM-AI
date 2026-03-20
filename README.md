<!-- ANOM-AI README -->

<h1 align="center">🚨 ANOM-AI</h1>
<h3 align="center">AI-Powered Cybersecurity SOC Dashboard 🔐</h3>

<p align="center">
  Real-time anomaly detection • AI insights • SOC visualization
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Built%20With-React%20%2B%20Flask-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/AI-Powered-purple?style=for-the-badge" />
</p>

---

## 🧠 About ANOM-AI

ANOM-AI is a **Security Operations Center (SOC) dashboard** that uses **machine learning** to detect anomalies in network traffic and provide real-time threat insights.

> ⚡ Built for modern cybersecurity workflows with real-time monitoring and intelligent alerting.

---

## 🚀 Features

- 🔍 Real-time packet sniffing (Scapy)
- 🚨 AI-based anomaly detection
- 📊 SOC dashboard with metrics & alerts
- 📈 Alerts table with filtering & pagination
- ⚠️ Severity classification system
- 🧠 Intelligent threat insights (in progress)
- 🛡️ Planned: Automated response system

---

## 🛠️ Tech Stack

### 💻 Frontend
<p>
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB"/>
  <img src="https://img.shields.io/badge/TailwindCSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white"/>
</p>

### ⚙️ Backend
<p>
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask"/>
  <img src="https://img.shields.io/badge/Scapy-4B8BBE?style=for-the-badge"/>
</p>

### 🧠 AI / ML
<p>
  <img src="https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white"/>
  <img src="https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge"/>
</p>

---

## ⚙️ Installation

### 🔧 Clone Repo
```bash
git clone https://github.com/HACKER9823/ANOM-AI.git
cd ANOM-AI


### 🖥️ Backend Setup

```bash
cd backend
python -m venv venv

# Activate virtual environment
source venv/Scripts/activate   # Windows (Git Bash)
# OR
venv\Scripts\activate          # Windows (CMD / PowerShell)

pip install -r requirements.txt
python app.py
