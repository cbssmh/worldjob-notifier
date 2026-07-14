from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
import json

from db import get_last_post, init_db
from workflow import process_site


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="WorldJob Notifier API", lifespan=lifespan)


def load_sites():
    with open("sites.json", "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/status")
def status():
    return {
        "status": "running",
        "service": "worldjob-notice-notifier"
    }


@app.get("/sites")
def sites():
    return {
        "sites": [site["name"] for site in load_sites()]
    }


@app.get("/last-notice")
def last_notice():
    sites = load_sites()
    site = sites[0]
    last = get_last_post(site["name"])

    if not last:
        return {"message": "No notice stored yet"}

    return {
        "site": site["name"],
        "number": last["number"],
        "title": last["title"],
        "url": last["link"]
    }

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/run-check")
def run_check():
    sites = load_sites()
    site = sites[0]

    try:
        return process_site(site)
    except Exception:
        raise HTTPException(status_code=502, detail="Notice check failed")
