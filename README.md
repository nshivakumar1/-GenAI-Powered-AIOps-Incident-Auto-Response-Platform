# 🧠 GenAI-Powered AIOps Incident Auto-Response Platform

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Status](https://img.shields.io/badge/status-active-success.svg) ![AI](https://img.shields.io/badge/AI-Gemini%20Pro-orange)

An enterprise-grade **Self-Healing Cloud Monitoring System** that detects incidents, analyzes them using **Google Gemini AI**, and automates remediation via **Jira** and **Slack**.

Designed to simulate a real-world **Site Reliability Engineering (SRE)** workflow, reducing Mean Time To Resolution (MTTR) by automating Root Cause Analysis (RCA).

---

## 🏗️ Architecture

```mermaid
graph TD
    subgraph "AWS Cloud / Infrastructure"
        VS[Victim Service (ECS/EC2)] -->|Logs & Metrics| CW[CloudWatch]
        CW -->|Alarm State Change| EB[EventBridge]
        EB -->|Trigger| L_AI[AIOps Lambda (The Brain)]
    end

    subgraph "External Integrations"
        L_AI -->|Analyze Logs| GEM[Gemini AI API]
        L_AI -->|Create Ticket| JIRA[Jira Cloud]
        L_AI -->|Send Alert| SLACK[Slack]
        L_AI -->|Index Data| ELK[ELK Stack (Elasticsearch)]
    end

    subgraph "Auto-Remediation"
        SLACK -->|Interactive Button| L_REM[Remediation Lambda]
        L_REM -->|Restart/Scale| VS
    end

    subgraph "Frontend & Chaos"
        FE[React Ops Dashboard] -->|Poll Health| VS
        FE -->|Trigger Chaos| VS
    end
```

## ✨ Key Features

- **🤖 AI-Driven RCA**: Uses Google Gemini to analyze logs and identify root causes (e.g., Memory Leaks, DB Connection Failures).
- **🚨 Smart Alerting**: Classifies severity (P1/P2/P3) and routes alerts to **Slack** with interactive "Auto-Fix" buttons.
- **🎫 Auto-Ticketing**: Automatically creates structured **Jira** tickets with generated context and tags.
- **🛠️ Self-Healing**: Triggers serverless remediation (e.g., restarting containers) without human intervention.
- **📉 Observability**: Real-time dashboards using **ELK Stack** and a custom **React Operations Center**.
- **🧪 Chaos Engineering**: Built-in "Chaos Monkey" to simulate CPU spikes, memory leaks, and crashes.

## 🚀 Tech Stack

- **Cloud**: AWS (Lambda, ECS, EventBridge, CloudWatch)
- **IaC**: Terraform
- **AI**: Google Gemini Pro
- **Backend**: Python (FastAPI, Boto3)
- **Frontend**: React, Tailwind CSS, Vite
- **Observability**: Elasticsearch, Logstash, Kibana (ELK)

---

## 🛠️ Getting Started

### Prerequisites
- AWS Account & CLI configured
- Docker & Docker Compose
- Node.js (for Frontend)
- Python 3.9+

### 1. Infrastructure Deployment (Terraform)
```bash
cd infra
# Update variables.tf with your API Keys
terraform init
terraform apply
```

### 2. Monitoring Stack (ELK)
```bash
cd infra/elk
docker-compose up -d
# Kibana: http://localhost:5601
```

### 3. Run Victim Service (The "App")
```bash
cd src/victim-service
docker build -t aiops-victim .
docker run -p 8000:8000 aiops-victim
```

### 4. Launch Operations Dashboard
```bash
cd src/frontend
npm install
npm run dev
# Dashboard: http://localhost:5173
```

---

## 🧪 Simulation (Chaos Monkey)

You can trigger incidents via the Frontend or CLI:

```bash
# Trigger a CPU Spike (P1 Incident)
python src/chaos-scripts/chaos_engine.py --action cpu

# Trigger a Memory Leak
python src/chaos-scripts/chaos_engine.py --action memory
```

**What happens next?**
1. System CPU > 80% ➔ **CloudWatch Alarm** Fires.
2. **Gemini AI** analyzes logs ➔ Identifies "CPU Stress Test".
3. **Slack Alert** received with "Auto-Fix" button.
4. **Jira Ticket** created (P1).
5. User clicks "Auto-Fix" ➔ Service Restarts ➔ Incident Resolved.

---

## 📷 Screenshots

*(Placeholder for Screenshots of Dashboard, Slack Alert, and Jira Ticket)*

---

## 📄 License
MIT
