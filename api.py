from fastapi import FastAPI
import json

from crawler import fetch_latest_post
from db import get_last_post, save_last_post
from notifier import send_discord_message

app = FastAPI(title="WorldJob Notifier API")


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

    latest = fetch_latest_post(site)
    saved = get_last_post(site["name"])

    if saved and saved["number"] == latest["number"]:
        return {
            "message": "No new notice",
            "site": site["name"],
            "latest_number": latest["number"],
            "latest_title": latest["title"]
        }

    save_last_post(
        site["name"],
        latest["number"],
        latest["title"],
        latest["link"]
    )

    send_discord_message(
        f"📢 **{site['name']} 새 공지 발견!**\n"
        f"- 번호: {latest['number']}\n"
        f"- 제목: {latest['title']}\n"
        f"- 날짜: {latest['date']}\n"
        f"- 링크: {latest['link']}"
    )

    return {
        "message": "New notice detected",
        "site": site["name"],
        "number": latest["number"],
        "title": latest["title"],
        "date": latest["date"],
        "url": latest["link"]
    }