# WorldJob Notice Notifier

A Python-based automation system that monitors the **WorldJob+ notice board** and sends alerts via **Discord Webhook** when a new general announcement is posted.

Unlike a simple crawler, this project is designed as a **24/7 server-side notification service** deployed on a cloud VM.

---

# Architecture

```
WorldJob Site
      ↓
Crawler
      ↓
Scheduler (APScheduler)
      ↓
SQLite (state tracking)
      ↓
Notifier (Discord Webhook)
      ↓
Discord Channel
```

---

# Features

- Crawl WorldJob+ notice board
- Extract latest general announcements
- Detect new posts by comparing with stored records
- Send alerts via Discord Webhook
- Persist state using SQLite
- Periodic checks using APScheduler
- Environment variable configuration via `.env`
- Monitoring API using FastAPI
- Deployed on Oracle Cloud Always Free VM
- Runs continuously using systemd

---

# Tech Stack

## Backend
- Python

## Libraries
- requests
- BeautifulSoup4
- APScheduler
- python-dotenv
- FastAPI
- Uvicorn

## Storage
- SQLite

## Deployment
- Oracle Cloud Always Free VM
- systemd service

---

# Project Structure

```
worldjob-notice-notifier/
├── app.py
├── crawler.py
├── db.py
├── scheduler.py
├── notifier.py
├── config.py
├── api.py
├── requirements.txt
├── sites.json
├── .env.example
└── README.md
```

---

# Setup (Local Development)

## 1. Clone repository

```bash
git clone https://github.com/cbssmh/worldjob-notice-notifier.git
cd worldjob-notice-notifier
```

## 2. Create virtual environment

```bash
python -m venv .venv
```

## 3. Activate virtual environment

### Windows

```bash
.venv\Scripts\activate
```

### Mac / Linux

```bash
source .venv/bin/activate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root.

Example:

```
DISCORD_WEBHOOK_URL=your_discord_webhook_url
CHECK_INTERVAL_MINUTES=10
```

You can also copy the example configuration:

```bash
cp .env.example .env
```

| Variable | Description |
|--------|-------------|
| DISCORD_WEBHOOK_URL | Discord webhook URL for notifications |
| CHECK_INTERVAL_MINUTES | Interval for checking new notices (minutes) |

---

# Run

```bash
python app.py
```

When running successfully:

```
Scheduler started: checking every 10 minutes
[CHECK] Starting site check
```

---

# API

This project provides a **FastAPI monitoring API**.

## Available endpoints

| Endpoint | Method | Description |
|--------|--------|-------------|
| /health | GET | Health check |
| /status | GET | Service status |
| /sites | GET | List monitored sites |
| /last-notice | GET | Last stored notice |
| /run-check | POST | Manually trigger a notice check |

Swagger documentation:

```
http://localhost:8000/docs
```

Run API locally:

```bash
uvicorn api:app --reload
```

---

# How It Works

System workflow:

1. Request the WorldJob notice list page  
2. Extract the latest general notice  
3. Compare with the previously stored notice in SQLite  
4. Send a Discord Webhook notification if a new notice is detected  
5. Save the latest state in the database  

---

# Deployment (Oracle Cloud)

This project is deployed on an **Oracle Cloud Always Free VM** and runs continuously.

## Environment

- Oracle Linux 9
- Python 3
- systemd service

---

# Service Management

Check service status:

```bash
sudo systemctl status worldjob-notifier
```

Restart service:

```bash
sudo systemctl restart worldjob-notifier
```

Stop service:

```bash
sudo systemctl stop worldjob-notifier
```

---

# View Logs

```bash
journalctl -u worldjob-notifier -f
```

---

# Future Improvements

- Support monitoring multiple websites
- Web dashboard for notice monitoring
- Docker container deployment
- GitHub Actions CI/CD pipeline
- Alert filtering and keyword notifications

---

# Author

GitHub  
https://github.com/cbssmh

---

# ⭐ Project Goal

This project demonstrates how to build and operate a **real-world automation service**, including:

- Web scraping
- Scheduled jobs
- State persistence
- Notification systems
- Environment-based configuration
- Cloud deployment
- Production service management

---

# 📌 Status

Production-ready notification service running on a cloud VM.
