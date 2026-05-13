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

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&color=00FF00&center=true&vCenter=true&width=500&lines=Initializing+ANOM-AI...;Monitoring+Network+Traffic...;Detecting+Anomalies...;Securing+Systems+in+Real-Time..." />
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

## 🧠 [ SYSTEM OVERVIEW ]

```bash
> ANOM-AI is a real-time SOC dashboard powered by machine learning
> Detects anomalies in network traffic
> Provides actionable cybersecurity insights
```

---

## 🚀 [ CORE CAPABILITIES ]

```bash
> Real-time packet sniffing (Scapy)
> AI-based anomaly detection
> SOC dashboard with live metrics
> Alerts table with filtering & pagination
> Severity classification system
> Intelligent threat insights (in progress)
> Automated response system (coming soon)
```

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
```

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
```

### 🌐 Frontend Setup

```bash
npm install
npm start
```

---

## 🧪 [ USAGE GUIDE ]

```bash
> Step 1: Start Backend Server
cd backend
source venv/Scripts/activate      # Git Bash / WSL
# OR
venv\Scripts\activate             # CMD / PowerShell

python app.py

> Step 2: Start Frontend Dashboard
npm start

> Step 3: Open in Browser
http://localhost:3000

> Backend runs on: http://localhost:5000
> Frontend runs on: http://localhost:3000
> Ensure both services are running simultaneously
```

## 💡 Extras

## 🤖 AI Security Assistant

<p align="center">
  <img src="https://img.shields.io/badge/AI-Security%20Assistant-purple?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Ollama-Enabled-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/LLM-Powered-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Real--time%20Insights-orange?style=for-the-badge" />
</p>

<p align="center">
  <strong>Intelligent Threat Explanation • SOC Co-Pilot • Local LLM Powered</strong>
</p>

### 🧠 AI Overview

The **AI Security Assistant** is an embedded LLM-powered co-pilot that explains anomalies detected by Isolation Forest and LSTM models in natural language. It helps security analysts quickly understand threats and take action.

> ⚡ Turns complex ML scores into clear, actionable security insights.

---

### 🚀 AI Capabilities

```bash
> Contextual alert explanations
> Attack pattern identification
> ML & LSTM score interpretation
> Severity reasoning
> Mitigation suggestions
> Natural language Q&A
> Educational threat insights



💬 How to Use

1. Go to Alerts → Click any alert
2. Open Alert Details
3. Scroll to AI Security Assistant
4. Ask questions in plain English

🧪 Suggested Questions

"Explain this alert in simple terms"
"Why was this marked Critical?"
"Is this traffic dangerous?"
"What does the LSTM score mean?"
"Suggest mitigation steps"
"What attack type is this?"

⚙️ Setup

# Start Ollama (Recommended)
ollama run llama3.2

# Backend Endpoint
http://localhost:5000/chat   # All processing runs locally

# Ollama must be running. Larger models need more RAM (16GB+ recommended)
# Below this lower models are recommended

```