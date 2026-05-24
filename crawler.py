import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0.0.0 Safari/537.36"
    )
}


def fetch_latest_post(site: dict):
    url = site["url"]
    link_pattern = site.get("link_pattern")
    
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # 상세 페이지로 가는 링크만 후보로 수집
    links = soup.find_all("a", href=True)

    for a in links:
        href = a.get("href", "").strip()
        text = a.get_text(" ", strip=True)

        if not href or not text:
            continue

        # 공지 상세 링크만 통과
        if "/info/bbs/notice/view.do" not in href:
            continue

        # 링크 텍스트가 "1146 제목 2026-02-25" 같은 일반 공지 형식인지 검사
        m = re.match(r"^(\d+)\s+(.+?)\s+(\d{4}-\d{2}-\d{2})$", text)
        if not m:
            continue

        number, title, date = m.groups()

        return {
            "number": int(number),
            "title": title.strip(),
            "date": date,
            "link": urljoin(url, href)
        }

    raise ValueError("일반 공지를 찾지 못했습니다.")