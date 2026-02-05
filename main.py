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
        
        # 1. 고정 게시물(item-fixed)을 제외한 첫 번째 일반 게시물을 찾습니다.
        # :not(.item-fixed)를 사용하여 진짜 최신순 리스트의 첫 번째를 타격합니다.
        latest_item = soup.select_one(".bbs-list-item:not(.item-fixed)")

        if not latest_item:
            # 만약 위 선택자로 못 찾으면 고정글 포함 전체에서 첫 번째를 가져옵니다.
            latest_item = soup.select_one(".bbs-list-item")

        if latest_item:
            # 2. 제목 추출
            title_el = latest_item.select_one(".bbs-list--tit")
            title = title_el.text.strip() if title_el else "제목 없음"
            
            # 3. 링크 추출 (상대 경로인 경우 도메인 붙여줌)
            relative_link = latest_item.get('href', '')
            full_link = f"https://www.worldjob.or.kr{relative_link}" if relative_link.startswith('/') else URL

            print(f"🎯 최종 확인된 최신글: {title}")
            
            # --- 이후 저장 및 비교 로직 (이전과 동일) ---
            db_path = "last_title.txt"
            last_title = ""
            if os.path.exists(db_path):
                with open(db_path, "r", encoding="utf-8") as f:
                    last_title = f.read().strip()
            
            if title != last_title:
                msg = f"🆕 월드잡 새 공지사항\n\n제목: {title}\n링크: {full_link}"
                send_message(msg)
                with open(db_path, "w", encoding="utf-8") as f:
                    f.write(title)
            else:
                print("😴 변동 사항 없음")
        else:
            print("❌ 게시글 리스트를 찾지 못했습니다.")

    except Exception as e:
        print(f"❗ 오류 발생: {e}")

if __name__ == "__main__":
    check_worldjob()
