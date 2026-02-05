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
    # 브라우저인 척 하기 위한 헤더 (더 정교하게 수정)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # [수정된 선택자] 월드잡의 실제 구조(table-type-01 또는 board-list 등)를 반영
        # 1순위: 공지사항 리스트의 일반적인 테이블 행
        # 2순위: 텍스트 기반으로 제목을 포함한 링크 찾기
        row = soup.select_one("div.board-list table tbody tr") or \
              soup.select_one(".table-type-01 tbody tr") or \
              soup.select_one("#gridContent tbody tr")

        if not row:
            print("--- 디버깅 정보: HTML 일부 출력 ---")
            print(response.text[:1000]) # 페이지 앞부분 1000자만 출력해서 구조 확인
            print("--------------------------------")
            print("게시글 목록을 찾을 수 없습니다. 선택자를 다시 확인해야 합니다.")
            return

        # 제목 추출 (월드잡은 보통 a 태그 안에 제목이 있음)
        title_el = row.select_one("td.left a") or row.select_one(".title") or row.select_one("a")
        
        if not title_el:
            print("행은 찾았으나 제목 태그를 찾지 못했습니다.")
            return

        title = title_el.text.strip()
        print(f"성공! 최신글 제목: {title}")

        # 비교 로직
        db_path = "last_title.txt"
        last_title = ""
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                last_title = f.read().strip()
                
        if title != last_title:
            msg = f"🆕 월드잡 새 공지사항\n\n제목: {title}\n링크: {URL}"
            send_message(msg)
            with open(db_path, "w", encoding="utf-8") as f:
                f.write(title)
            print("텔레그램 알림 전송 완료")
        else:
            print("새 글 없음 (이전 제목과 동일)")

    except Exception as e:
        print(f"시스템 오류 발생: {e}")

if __name__ == "__main__":
    check_worldjob()
