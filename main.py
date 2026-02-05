import requests
from bs4 import BeautifulSoup
import os

# 1. 설정
URL = "https://www.worldjob.or.kr/info/bbs/notice/list.do?menuId=1000006475"
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
DB_FILE = "last_post.txt"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message}
    requests.get(url, params=params)

def check_notice():
    # 2. 웹페이지 가져오기
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    res = requests.get(URL, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    # 3. 최신 공지글 추출 (월드잡 구조에 맞게 선택자 설정)
    # 일반글 중 가장 위에 있는 것을 가져옵니다 (공지 고정글 제외 로직은 추가 가능)
    first_post = soup.select_one("#gridContent table tbody tr:not(.notice)") 
    if not first_post:
        first_post = soup.select_one("#gridContent table tbody tr") # 예외 처리
        
    title = first_post.select_one(".title").text.strip()
    link_attr = first_post.select_one("a")['onclick'] # 월드잡은 자바스크립트 호출 형태일 수 있음
    
    # 4. 이전 글과 비교
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()
    else:
        last_title = ""

    if title != last_title:
        # 5. 새 글이 있으면 알림 전송 및 저장
        print(f"새 글 발견: {title}")
        send_telegram(f"🔔 월드잡 새 공지사항!\n\n제목: {title}\n링크: {URL}")
        with open(DB_FILE, "w", encoding="utf-8") as f:
            f.write(title)
    else:
        print("새로운 공지사항이 없습니다.")

if __name__ == "__main__":
    check_notice()
