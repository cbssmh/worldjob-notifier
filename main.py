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
        
        # 1. 일단 페이지 내의 모든 <a> 태그(링크)를 가져옵니다.
        links = soup.find_all('a')
        
        valid_title = ""
        
        # 2. 링크 중에서 진짜 '공지사항 제목'처럼 생긴 것을 찾습니다.
        # 조건: 텍스트가 10자 이상이고, 특정 키워드(로그인, 메뉴 등)가 없는 것
        exclude_keywords = ['로그인', '회원가입', '바로가기', '사이트맵', '이용약관', 'Contact']
        
        for a in links:
            title = a.text.strip()
            # 월드잡 공지사항 제목은 보통 어느 정도 길이가 있습니다.
            if len(title) > 10 and not any(key in title for key in exclude_keywords):
                valid_title = title
                break # 가장 먼저 찾은 긴 링크를 최신글로 간주

        if not valid_title:
            print("--- 디버깅: 발견된 모든 링크 텍스트 (상위 20개) ---")
            for i, a in enumerate(links[:20]):
                print(f"{i}: {a.text.strip()}")
            print("------------------------------------------")
            print("적절한 제목을 찾지 못했습니다.")
            return

        print(f"성공! 최신글 확인: {valid_title}")

        # 비교 및 저장 로직
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
            print(f"변동 없음: {valid_title}")

    except Exception as e:
        print(f"시스템 오류: {e}")

if __name__ == "__main__":
    check_worldjob()
