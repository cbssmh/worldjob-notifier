import json
from apscheduler.schedulers.blocking import BlockingScheduler

from config import CHECK_INTERVAL_MINUTES
from workflow import process_site

def load_sites():
    with open("sites.json", "r", encoding="utf-8") as f:
        return json.load(f)


def check_sites():
    print("\n[CHECK] 사이트 점검 시작")

    sites = load_sites()

    for site in sites:
        try:
            result = process_site(site)
            if result["status"] == "initialized":
                print(f"[INIT] {result['site']} 초기값 저장: {result['latest_number']}")
            elif result["status"] == "notified":
                print(f"[NEW] {result['site']} 새 글 알림 전송: {result['latest_number']}")
            else:
                print(f"[OK] {result['site']} 변경 없음")

        except Exception as e:
            print(f"[ERROR] {site['name']}: {e}")


def start_scheduler():
    scheduler = BlockingScheduler()

    scheduler.add_job(
        check_sites,
        "interval",
        minutes=CHECK_INTERVAL_MINUTES,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300
    )

    print(f"스케줄러 시작: {CHECK_INTERVAL_MINUTES}분마다 점검")
    check_sites()
    scheduler.start()
