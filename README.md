# WorldJob Notification Automation Service

WorldJob Notification Automation Service is a Python backend system that monitors the WorldJob notice board, detects newly published announcements, persists processing state, and delivers event notifications through Discord Webhooks.

The repository is structured as an automation-oriented backend workflow rather than a one-off scraping script. It separates the concerns of source integration, event extraction, state comparison, scheduled execution, notification delivery, and operational inspection.

## Project Overview

The service periodically checks configured notice sources, extracts the latest valid notice event, compares that event against the last processed state in SQLite, and sends a Discord notification only when a new notice is detected.

It includes two backend entry points:

- `app.py`: starts the persistent scheduled worker.
- `api.py`: exposes a FastAPI interface for health checks, service status, configured source inspection, last-notice inspection, and manual workflow execution.

This design allows the repository to demonstrate both autonomous background automation and an HTTP-accessible operational control plane.

## Operational Problem Being Explored

Many operational workflows depend on external systems that do not provide direct event streams, webhooks, or structured APIs. In this case, the WorldJob notice board is treated as an upstream source that must be polled, normalized, deduplicated, and converted into a downstream notification event.

The engineering problem is not only retrieving page content. The service needs to answer operational questions such as:

- How should a scheduled backend process detect meaningful changes from an external source?
- How can the latest processed event be persisted to prevent duplicate notifications?
- How should the crawler, scheduler, database, and notification channel be isolated from each other?
- How can an operator inspect service state or trigger a manual check without logging into the worker process?
- What reliability behavior is already present, and where should retry or cooldown logic be added as the system matures?

## Key Features

- Scheduled background execution with APScheduler.
- Configurable polling interval through environment variables.
- External source configuration through `sites.json`.
- HTML source integration using `requests` and BeautifulSoup.
- Notice event extraction using URL and text pattern validation.
- State persistence in SQLite using an idempotent upsert.
- Duplicate notification prevention by comparing the latest source event against stored state.
- Discord Webhook delivery for downstream notifications.
- FastAPI monitoring and manual execution endpoints.
- Per-site exception containment inside the scheduled workflow.
- HTTP timeout handling for upstream requests and webhook delivery.
- Initial state bootstrap that records the current latest notice without sending a historical notification.

## System Architecture

```text
Configured Sources
    sites.json
        |
        v
Scheduler / Manual Trigger
    APScheduler or FastAPI /run-check
        |
        v
Crawler
    requests + BeautifulSoup
        |
        v
Event Extraction
    notice link validation
    notice number/title/date parsing
        |
        v
State Store
    SQLite site_state table
        |
        v
Change Detection
    latest notice number vs stored notice number
        |
        v
Notification Adapter
    Discord Webhook
```

The service is intentionally modular:

- `crawler.py` owns upstream page access and parsing.
- `scheduler.py` owns recurring orchestration and event-processing control flow.
- `db.py` owns state persistence.
- `notifier.py` owns outbound notification delivery.
- `api.py` exposes operational HTTP endpoints.
- `config.py` centralizes environment-driven runtime configuration.

## Notification / Automation Workflow

The scheduled workflow is implemented in `scheduler.check_sites()`:

1. Load monitored source definitions from `sites.json`.
2. Fetch the latest notice candidate from each source.
3. Parse the notice number, title, date, and canonical link.
4. Read the last processed notice for the site from SQLite.
5. If no state exists, store the current latest notice as the baseline.
6. If the latest notice number differs from the stored number, build a notification message.
7. Send the message to Discord through the webhook adapter.
8. Persist the newly processed notice after notification delivery.
9. Log per-site outcomes and continue processing other configured sources.

The workflow avoids duplicate notifications by treating the notice number as the event identity. The SQLite row for each site acts as a checkpoint for the last processed event.

## Backend Architecture Explanation

### Source Integration

`crawler.py` uses a browser-like `User-Agent`, request timeouts, and HTTP status validation. The parser collects anchor tags, filters for the configured WorldJob notice detail path, and extracts notice metadata from text matching the expected notice format:

```text
<notice_number> <title> <YYYY-MM-DD>
```

The crawler returns a normalized event object:

```json
{
  "number": 1146,
  "title": "Notice title",
  "date": "2026-02-25",
  "link": "https://www.worldjob.or.kr/info/bbs/notice/view.do..."
}
```

### State Management

`db.py` creates and manages a `site_state` table:

```sql
CREATE TABLE IF NOT EXISTS site_state (
    site_name TEXT PRIMARY KEY,
    last_number INTEGER,
    last_title TEXT,
    last_link TEXT
)
```

Writes use SQLite `ON CONFLICT(site_name) DO UPDATE`, which gives the service idempotent checkpoint updates for each monitored source.

### Orchestration

`scheduler.py` uses `BlockingScheduler` and an interval trigger controlled by `CHECK_INTERVAL_MINUTES`. The service also runs `check_sites()` once during startup, which gives immediate feedback that configuration, source access, parsing, storage, and notification dependencies are working.

### Notification Delivery

`notifier.py` sends messages to Discord through a webhook URL loaded from `.env`. Delivery uses a request timeout and `raise_for_status()` so webhook failures surface as operational errors instead of being silently ignored.

### Operational API

`api.py` provides a small control plane for operators and reviewers. It can be run independently with Uvicorn to inspect state or manually trigger the workflow.

## Tech Stack

- Python
- FastAPI
- Uvicorn
- APScheduler
- requests
- BeautifulSoup4
- python-dotenv
- SQLite
- Discord Webhooks

## API Examples

Run the API:

```bash
uvicorn api:app --reload
```

Swagger UI:

```text
http://localhost:8000/docs
```

### Health Check

```http
GET /health
```

Response:

```json
{
  "ok": true
}
```

### Service Status

```http
GET /status
```

Response:

```json
{
  "status": "running",
  "service": "worldjob-notice-notifier"
}
```

### Configured Sites

```http
GET /sites
```

Response:

```json
{
  "sites": ["WorldJob Notice"]
}
```

### Last Stored Notice

```http
GET /last-notice
```

Response:

```json
{
  "site": "WorldJob Notice",
  "number": 1146,
  "title": "Notice title",
  "url": "https://www.worldjob.or.kr/info/bbs/notice/view.do..."
}
```

### Manual Workflow Execution

```http
POST /run-check
```

Possible response when no new notice exists:

```json
{
  "message": "No new notice",
  "site": "WorldJob Notice",
  "latest_number": 1146,
  "latest_title": "Notice title"
}
```

Possible response when a new notice is detected:

```json
{
  "message": "New notice detected",
  "site": "WorldJob Notice",
  "number": 1147,
  "title": "New notice title",
  "date": "2026-03-01",
  "url": "https://www.worldjob.or.kr/info/bbs/notice/view.do..."
}
```

## Project Structure

```text
worldjob-notifier-main/
├── app.py              # Scheduled worker entry point
├── api.py              # FastAPI operational endpoints
├── config.py           # Environment and runtime configuration
├── crawler.py          # WorldJob source integration and event extraction
├── db.py               # SQLite state store
├── notifier.py         # Discord Webhook delivery adapter
├── scheduler.py        # Workflow orchestration and scheduled execution
├── sites.json          # Monitored source definitions
├── smoke_test.py       # Manual crawler smoke check
├── requirements.txt    # Python dependencies
└── README.md
```

## Engineering Decisions

### Polling-Based Workflow

The upstream source does not expose a webhook or event queue, so the service uses scheduled polling. APScheduler provides a lightweight and explicit scheduling layer suitable for a single-process backend worker.

### SQLite for Checkpoint State

SQLite is sufficient for a compact notification workflow where the primary persistence requirement is storing the last processed event per source. It keeps deployment simple while still providing durable state across process restarts.

### Baseline Initialization

On first run, the service stores the latest visible notice without sending an alert. This avoids sending old notices as if they were newly detected events and gives the worker a clean checkpoint for future comparisons.

### Modular Adapters

The crawler, database, scheduler, API, and notification sender are separated into small modules. This makes it easier to replace individual integrations later, such as moving from Discord to another notification channel or from HTML parsing to an official API.

### Explicit Failure Surfacing

Upstream and webhook calls use timeouts and HTTP status validation. The scheduler catches exceptions per site, logs the error, and continues the workflow loop, preventing one failing source from terminating the entire scheduled process.

## Challenges and Trade-Offs

- The parser depends on the current WorldJob HTML structure and notice text format. A markup change upstream may require parser updates.
- The current implementation compares the latest notice number only. This is efficient for a notice board but does not yet process multiple missed notices if several are published between polling intervals.
- Retry and cooldown policies are not yet implemented as first-class components. Current resilience comes from request timeouts, raised HTTP errors, scheduler-level exception handling, and the next scheduled interval.
- SQLite is appropriate for a single-process deployment, but a multi-worker deployment would require stronger coordination around state updates.
- The API currently inspects and manually checks the first configured site. The scheduled worker is already structured for multiple sites, but the API surface would need to be expanded for full multi-source control.

## Future Improvements

- Add bounded retry with backoff for transient upstream and webhook failures.
- Add notification cooldown or suppression windows for repeated delivery errors.
- Process all missed notices between the stored checkpoint and the latest source event.
- Expand FastAPI endpoints to support per-site manual checks and state inspection.
- Add structured logging with event IDs, site names, and delivery outcomes.
- Add unit tests for parser behavior, state transitions, and notification formatting.
- Add Docker packaging and a production deployment manifest.
- Add CI checks for formatting, tests, and dependency validation.
- Support additional notification adapters such as Slack, email, or queue-based delivery.
- Add metrics for check latency, parse failures, notification failures, and last successful run time.

## Setup Instructions

### 1. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-id/your-webhook-token
CHECK_INTERVAL_MINUTES=10
```

Environment variables:

| Variable | Required | Description |
| --- | --- | --- |
| `DISCORD_WEBHOOK_URL` | Yes | Discord Webhook URL used by the notification adapter. |
| `CHECK_INTERVAL_MINUTES` | No | Scheduler interval in minutes. Defaults to `10`. |

### 4. Review Source Configuration

The monitored source is configured in `sites.json`:

```json
[
  {
    "name": "WorldJob Notice",
    "url": "https://www.worldjob.or.kr/info/bbs/notice/list.do?menuId=1000006475",
    "link_pattern": "/info/bbs/notice/view.do"
  }
]
```

### 5. Run the Scheduled Worker

```bash
python app.py
```

The worker initializes SQLite, performs an immediate check, and then continues running on the configured interval.

### 6. Run the Operational API

```bash
uvicorn api:app --reload
```

Open the API documentation at:

```text
http://localhost:8000/docs
```

### 7. Run a Crawler Smoke Check

```bash
python smoke_test.py
```

This executes the crawler against the first configured source and prints the normalized latest notice event.
