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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # [핵심 수정] 월드잡의 실제 클래스명 'board-list-type'을 타격합니다.
        # 모든 행(tr)을 가져와서 분석합니다.
        rows = soup.select(".board-list-type table tbody tr") or \
               soup.select("table tbody tr")

        valid_title = ""
        for row in rows:
            # 제목이 들어있는 칸(보통 클래스가 'subject'이거나 'left'임)
            title_el = row.select_one(".subject") or row.select_one(".left") or row.select_one("a")
            
            if title_el:
                # 텍스트 내부에 '공지' 같은 말머리가 있을 수 있으니 정리
                title = title_el.text.strip()
                # 빈 줄이 아니고 실제 글 제목 같은 것만 채택
                if len(title) > 2:
                    valid_title = title
                    break

        if not valid_title:
            print("데이터 파싱 실패: 적절한 제목을 찾을 수 없습니다.")
            return

        print(f"성공! 최신글 확인: {valid_title}")

        # 비교 및 저장
        db_path = "last_title.txt"
        last_title = ""
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                last_title = f.read().strip()
                
        if valid_title != last_title:
            msg = f"🆕 월드잡 새 공지사항\n\n제목: {valid_title}\n링크: {URL}"
            send_message(msg)
            with open(db_path, "w", encoding="utf-8") as f:
                f.write(valid_title)
            print("텔레그램 알림 전송 완료")
        else:
            print("변동 사항 없음 (이전 글과 동일)")

    except Exception as e:
        print(f"시스템 오류: {e}")

if __name__ == "__main__":
    check_worldjob()
