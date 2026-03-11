# WorldJob Notice Notifier

A **Python-based automation system** that monitors the WorldJob+ notice board and sends alerts via **Discord Webhook** when a new general announcement is posted.

Unlike a simple crawler, this project is designed as a **24/7 server-side notification service deployed on a cloud VM**.

---

# Architecture

```
WorldJob Site
      ↓
Crawler
      ↓
Scheduler
      ↓
SQLite (state)
      ↓
Notifier
      ↓
Discord
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
- Deployed on Oracle Cloud Always Free VM
- Runs continuously using `systemd`

---

# Tech Stack

## Backend

- Python

## Libraries

- requests
- BeautifulSoup4
- APScheduler
- python-dotenv

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
├── requirements.txt
├── sites.json
├── .env.example
└── README.md
```

---

# Setup (Local Development)

## 1. Create virtual environment

```
python -m venv .venv
```

## 2. Activate virtual environment

### Windows

```
.venv\Scripts\activate
```

### Mac / Linux

```
source .venv/bin/activate
```

## 3. Install dependencies

```
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

| Variable | Description |
|--------|-------------|
| DISCORD_WEBHOOK_URL | Discord webhook URL for notifications |
| CHECK_INTERVAL_MINUTES | Interval for checking new notices (minutes) |

---

# Run

```
python app.py
```

When running successfully:

```
Scheduler started: checking every 10 minutes
[CHECK] Starting site check
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

## Service Management

```
sudo systemctl status worldjob-notifier
sudo systemctl restart worldjob-notifier
sudo systemctl stop worldjob-notifier
```

## View Logs

```
journalctl -u worldjob-notifier -f
```

---

# Future Improvements

- Support monitoring multiple websites
- Status API using FastAPI
- Web dashboard
- Docker deployment
- GitHub Actions CI/CD pipeline

---

# Author

GitHub  
https://github.com/cbssmh
