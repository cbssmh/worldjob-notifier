from crawler import fetch_latest_post
from db import get_last_post, save_last_post
from notifier import send_discord_message


def make_message(site_name: str, latest: dict) -> str:
    return (
        f"📢 **{site_name} 새 공지 발견!**\n"
        f"- 번호: {latest['number']}\n"
        f"- 제목: {latest['title']}\n"
        f"- 날짜: {latest['date']}\n"
        f"- 링크: {latest['link']}"
    )


def process_site(site: dict) -> dict:
    """Process one site and persist a checkpoint only after a successful send."""
    site_name = site["name"]
    latest = fetch_latest_post(site)
    saved = get_last_post(site_name)

    if saved is None:
        save_last_post(
            site_name,
            latest["number"],
            latest["title"],
            latest["link"],
        )
        return {
            "status": "initialized",
            "site": site_name,
            "latest_number": latest["number"],
            "notification_sent": False,
        }

    if saved["number"] == latest["number"]:
        return {
            "status": "unchanged",
            "site": site_name,
            "latest_number": latest["number"],
            "notification_sent": False,
        }

    send_discord_message(make_message(site_name, latest))
    save_last_post(
        site_name,
        latest["number"],
        latest["title"],
        latest["link"],
    )
    return {
        "status": "notified",
        "site": site_name,
        "latest_number": latest["number"],
        "notification_sent": True,
    }
