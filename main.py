import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
URL = "https://www.worldjob.or.kr/info/bbs/notice/list.do?menuId=1000006475"

def send_message(text):
    if TOKEN and CHAT_ID:
        api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(api_url, data={'chat_id': CHAT_ID, 'text': text})

def check_worldjob():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # [수정 포인트] 더 넓은 범위의 선택자를 사용하고, 여러 후보를 시도합니다.
        # 보통 공공기관 게시판은 'board_list' 클래스나 'tbody'의 'tr'을 사용합니다.
        row = soup.select_one(".board_list tbody tr") or \
              soup.select_one("table tbody tr") or \
              soup.select_one(".table_col tbody tr")

        # [방어 코드] 만약 행을 찾지 못했다면 에러를 내지 않고 종료합니다.
        if not row:
            print("게시글 목록을 찾을 수 없습니다. 사이트 구조를 확인해야 합니다.")
            return

        # 제목 태그 찾기 (클래스명이 .title 이거나 첫 번째 a 태그인 경우가 많음)
        title_element = row.select_one(".title") or row.select_one("td.left a") or row.select_one("a")
        
        if not title_element:
            print("제목 태그를 찾을 수 없습니다.")
            return

        title = title_element.text.strip()
        print(f"현재 최신글 제목: {title}")

        # 비교 및 저장 로직
        db_path = "last_title.txt"
        last_title = ""
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                last_title = f.read().strip()
                
        if title != last_title:
            msg = f"🆕 월드잡 새 공지사항\n\n제목: {title}\n바로가기: {URL}"
            send_message(msg)
            with open(db_path, "w", encoding="utf-8") as f:
                f.write(title)
            print("새 글 알림 전송 완료!")
        else:
            print("변동 사항 없음")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    check_worldjob()
