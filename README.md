# WorldJob Notification Automation Service

A single-process Python notification automation service that polls configured WorldJob notice sources, stores a SQLite checkpoint, and sends new notices to a Discord webhook.

## What it does

- Scheduler: checks every configured site on an interval.
- API: provides small inspection and manual-trigger endpoints; manual checking currently targets the first configured site.
- State: stores the last processed notice per site in SQLite.
- Delivery: sends Discord messages only for newly detected notices.

## Data flow

```text
Scheduler or API
  → Fetch
  → Parse latest notice
  → Read checkpoint
  → First-run baseline or compare
  → Notify
  → Save checkpoint after success
```

Both entry points use the same `workflow.process_site()` function.

## State and delivery rules

- **First run:** if a checkpoint does not exist, the current latest notice is saved as a baseline and no Discord message is sent.
- **Unchanged notice:** no message is sent and the checkpoint is not changed.
- **New notice:** Discord is called first; the checkpoint is updated only after successful delivery.
- **Delivery failure:** the checkpoint remains unchanged, so a later run can attempt delivery again.

Checkpoint updates use SQLite upsert operations. This provides checkpoint-based duplicate suppression; it does not provide exactly-once Discord delivery.

## Run

Create and activate a virtual environment, then install all runtime and test dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create `.env` from `.env.example` and set a real webhook URL:

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-id/your-webhook-token
CHECK_INTERVAL_MINUTES=10
```

Configure sites in `sites.json`. Each source requires `name`, `url`, and `link_pattern`; the crawler uses `link_pattern` to select notice-detail links.

Start the scheduled worker:

```bash
python app.py
```

The worker initializes SQLite, performs an immediate check, then checks all configured sites at the configured interval.

Start the API:

```bash
uvicorn api:app --reload
```

The API initializes SQLite on startup. `/run-check` manually processes the first configured site using the same workflow as the Scheduler.

## API

| Endpoint | Behavior |
| --- | --- |
| `GET /health` | Process liveness endpoint; it does not check dependencies or recent job success. |
| `GET /status` | Returns static API service metadata, not Scheduler health. |
| `GET /sites` | Lists configured site names. |
| `GET /last-notice` | Returns the stored checkpoint for the first configured site. |
| `POST /run-check` | Manually processes the first configured site. Workflow failures return HTTP 502. |

`POST /run-check` returns a compact workflow result such as:

```json
{
  "status": "notified",
  "site": "WorldJob Notice",
  "latest_number": 1147,
  "notification_sent": true
}
```

## Test

Run the same command used by CI:

```bash
python -m pytest -q
```

The test suite uses mocks and temporary SQLite databases; it does not call WorldJob or Discord. It covers workflow state transitions, checkpoint persistence, parser behavior, Scheduler site-failure isolation, and API startup/error behavior.

## Manual smoke test

```bash
python smoke_test.py
```

This is a manual network check against the first configured site. It is intentionally separate from pytest and requires external network access.

## Known limitations

- The API manually processes only the first configured site; the Scheduler processes all configured sites.
- The design is intended for one process. Running the Scheduler and API as separate processes has no shared duplicate-execution coordination.
- The checkpoint stores only the latest item, so notices published between polling intervals can be skipped.
- Retry and backoff are not implemented.
- Discord delivery is not exactly-once: a successful send followed by a checkpoint write failure can cause a later duplicate notification.
- The repository contains no Docker, systemd, Oracle Cloud, or other deployment-operation implementation evidence.

## Project structure

```text
app.py          Scheduled-worker entry point
api.py          FastAPI inspection and manual-trigger endpoints
workflow.py     Shared site-processing state transition
crawler.py      HTTP fetch and HTML parsing
db.py           SQLite checkpoint store
notifier.py     Discord webhook adapter
scheduler.py    APScheduler orchestration
tests/          Network-free automated tests
smoke_test.py   Manual network smoke check
```
