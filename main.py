import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

URL = "https://www.worldjob.or.kr/info/bbs/notice/list.do?menuId=1000006475"
DB_PATH = "last_seen.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
}

def send_message(text: str) -> None:
    if not (TOKEN and CHAT_ID):
        print("⚠️ TELEGRAM_TOKEN / TELEGRAM_CHAT_ID가 설정되지 않았습니다.")
        return

    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    res = requests.post(api_url, data={"chat_id": CHAT_ID, "text": text})
    if res.status_code == 200:
        print("✅ 텔레그램 알림 전송 성공!")
    else:
        print(f"❌ 텔레그램 전송 실패: {res.status_code} / {res.text}")

def load_last_seen() -> str:
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def save_last_seen(value: str) -> None:
    with open(DB_PATH, "w", encoding="utf-8") as f:
        f.write(value)

def check_worldjob() -> None:
    try:
        r = requests.get(URL, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # 1) 고정글 제외한 "첫번째 글"에서 링크(a) 찾기
        item = soup.select_one(".bbs-list-item:not(.item-fixed)")
        if item is None:
            item = soup.select_one(".bbs-list-item")

        if item is None:
            print("❌ 게시글 리스트(.bbs-list-item)를 찾지 못했습니다.")
            return

        a = item.select_one("a[href]")
        if a is None:
            print("❌ 최신글에서 a[href]를 찾지 못했습니다.")
            return

        title_el = item.select_one(".bbs-list--tit") or a
        title = title_el.get_text(strip=True) if title_el else "제목 없음"

        href = a.get("href", "").strip()
        full_link = urljoin("https://www.worldjob.or.kr", href)

        # ★ 저장 키를 제목 대신 링크로 (더 안전)
        current_key = full_link

        print(f"🎯 최신글: {title}")
        print(f"🔗 링크: {full_link}")

        last_key = load_last_seen()
        if current_key != last_key:
            msg = f"🆕 월드잡 새 공지사항\n\n제목: {title}\n링크: {full_link}"
            send_message(msg)
            save_last_seen(current_key)
        else:
            print("😴 변동 사항 없음")

    except Exception as e:
        print(f"❗ 오류 발생: {e}")

if __name__ == "__main__":
    check_worldjob()
