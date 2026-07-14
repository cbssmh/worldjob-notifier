import pytest

import crawler


SITE = {
    "name": "Example",
    "url": "https://example.test/notices/list",
    "link_pattern": "/notices/view",
}


class FakeResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        return None


def test_fetch_latest_post_parses_configured_notice_link(monkeypatch):
    html = """
    <a href="/other/view">999 Wrong 2026-03-01</a>
    <a href="/notices/view?id=1147">1147 New notice 2026-03-01</a>
    """
    calls = []
    monkeypatch.setattr(
        crawler.requests,
        "get",
        lambda *args, **kwargs: (calls.append((args, kwargs)) or FakeResponse(html)),
    )

    latest = crawler.fetch_latest_post(SITE)

    assert latest == {
        "number": 1147,
        "title": "New notice",
        "date": "2026-03-01",
        "link": "https://example.test/notices/view?id=1147",
    }
    assert calls[0][0] == (SITE["url"],)
    assert calls[0][1]["timeout"] == 15


def test_fetch_latest_post_ignores_links_outside_configured_pattern(monkeypatch):
    monkeypatch.setattr(
        crawler.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(
            '<a href="/other/view">1147 New notice 2026-03-01</a>'
        ),
    )

    with pytest.raises(ValueError, match="일반 공지를 찾지 못했습니다"):
        crawler.fetch_latest_post(SITE)


def test_fetch_latest_post_requires_link_pattern():
    with pytest.raises(ValueError, match="link_pattern"):
        crawler.fetch_latest_post({"name": "Example", "url": "https://example.test"})
