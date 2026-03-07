WorldJob Notice Notifier
월드잡플러스 공지사항 목록을 주기적으로 확인하여 새 일반 공지가 등록되면 Discord로 알림을 보내는 Python 프로젝트입니다.

주요 기능
웹사이트 공지사항 목록 크롤링

최신 일반 공지 자동 추출

이전 공지와 비교하여 새 글 감지

Discord Webhook 알림 전송

SQLite 기반 상태 저장

APScheduler 기반 주기 실행

기술 스택
Python

requests

BeautifulSoup4

SQLite

APScheduler

Discord Webhook

프로젝트 구조
Plaintext
new-post-notifier/
├── app.py
├── crawler.py
├── db.py
├── scheduler.py
├── notifier.py
├── config.py
├── requirements.txt
├── sites.json
└── README.md
실행 방법
1. 가상환경 생성
Bash
python -m venv .venv
2. 가상환경 활성화
Windows:

DOS
.venv\Scripts\activate
3. 패키지 설치
Bash
pip install -r requirements.txt
4. 환경변수 설정
기본 설정:

Bash
export DISCORD_WEBHOOK_URL="your_webhook_url"
Windows PowerShell:

PowerShell
$env:DISCORD_WEBHOOK_URL="your_webhook_url"
5. 실행
Bash
python app.py
동작 방식
월드잡 공지사항 목록 페이지 요청

일반 공지 중 가장 최신 글 추출

DB에 저장된 이전 공지와 비교

새 공지 발견 시 Discord 알림 전송

향후 개선
여러 사이트 지원

FastAPI 기반 웹 UI

Docker 배포

GitHub Actions 자동 실행
