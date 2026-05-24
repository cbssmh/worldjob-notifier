import json
from apscheduler.schedulers.blocking import BlockingScheduler

from crawler import fetch_latest_post
from db import get_last_post, save_last_post
from notifier import send_discord_message
from config import CHECK_INTERVAL_MINUTES

FORCE_TEST_NOTIFICATION = False

def load_sites():
    with open("sites.json", "r", encoding="utf-8") as f:
        return json.load(f)


def make_message(site_name: str, latest: dict) -> str:
    prefix = "[TEST] " if FORCE_TEST_NOTIFICATION else ""
    return (
        f"📢 {prefix}**{site_name} 새 공지 발견!**\n"
        f"- 번호: {latest['number']}\n"
        f"- 제목: {latest['title']}\n"
        f"- 날짜: {latest['date']}\n"
        f"- 링크: {latest['link']}"
    )


def check_sites():
    print("\n[CHECK] 사이트 점검 시작")

    sites = load_sites()

    for site in sites:
        site_name = site["name"]

        try:
            latest = fetch_latest_post(site)
            saved = get_last_post(site_name)

            if saved is None:
                save_last_post(
                    site_name,
                    latest["number"],
                    latest["title"],
                    latest["link"]
                )
                print(
                    f"[INIT] {site_name} 초기값 저장: "
                    f"{latest['number']} - {latest['title']}"
                )
                continue

            is_new_post = latest["number"] != saved["number"]

            if is_new_post or FORCE_TEST_NOTIFICATION:
                print(f"[NEW] {site_name} 새 글 발견!")
                print(f"      번호: {latest['number']}")
                print(f"      제목: {latest['title']}")
                print(f"      링크: {latest['link']}")

                message = make_message(site_name, latest)
                send_discord_message(message)

                # 실제 새 글일 때만 DB 업데이트
                if is_new_post:
                    save_last_post(
                        site_name,
                        latest["number"],
                        latest["title"],
                        latest["link"]
                    )
            else:
                print(f"[OK] {site_name} 변경 없음")

        except Exception as e:
            print(f"[ERROR] {site_name}: {e}")


def start_scheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(check_sites, "interval", minutes=CHECK_INTERVAL_MINUTES)

    print(f"스케줄러 시작: {CHECK_INTERVAL_MINUTES}분마다 점검")
    check_sites()
    scheduler.start()