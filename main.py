import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
URL = "https://www.worldjob.or.kr/info/bbs/notice/list.do?menuId=1000006475"

def send_message(text):
    if TOKEN and CHAT_ID:
        api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        # [수정] 전송 결과를 확인하기 위해 response를 받습니다.
        res = requests.post(api_url, data={'chat_id': CHAT_ID, 'text': text})
        if res.status_code == 200:
            print("텔레그램 알림 전송 성공!")
        else:
            print(f"텔레그램 전송 실패! 에러코드: {res.status_code}, 사유: {res.text}")

def check_worldjob():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # [정밀 파싱] 로고를 피하기 위해 리스트가 들어있는 특정 영역(ID 혹은 Class)을 먼저 지정합니다.
        # 월드잡 리스트는 보통 'gridContent' 또는 'content' 영역 안에 있습니다.
        content_area = soup.select_one("#gridContent") or soup.select_one(".board-list-type") or soup.select_one("#content")
        
        if not content_area:
            # 영역을 못 찾으면 전체에서 찾되, 로고 단어는 건너뜁니다.
            content_area = soup

        links = content_area.find_all('a')
        
        valid_title = ""
        # 제외할 키워드 보강 (로고 및 메뉴 방어)
        exclude_keywords = ['World Job', 'WorldJob', '로그인', '회원가입', '바로가기', '메인으로', '사이트맵', '이용약관']
        
        for a in links:
            title = a.text.strip()
            # 제목 길이가 적당하고 제외 키워드가 없는 것
            if len(title) > 5 and not any(key in title for key in exclude_keywords):
                # 자바스크립트 호출문이나 의미 없는 문자는 제외
                if "javascript" not in a.get('href', '') and "ShowList" not in title:
                    valid_title = title
                    break

        if not valid_title:
            print("적절한 공지사항 제목을 찾지 못했습니다.")
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
        else:
            print(f"변동 없음: {valid_title}")

    except Exception as e:
        print(f"시스템 오류: {e}")

if __name__ == "__main__":
    check_worldjob()
