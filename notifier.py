import requests
from config import DISCORD_WEBHOOK_URL


def send_discord_message(content: str):
    if not DISCORD_WEBHOOK_URL or "여기에_" in DISCORD_WEBHOOK_URL:
        print("[WARN] 디스코드 웹훅 URL이 설정되지 않았습니다.")
        return

    payload = {
        "content": content
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()