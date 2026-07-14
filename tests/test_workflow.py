import pytest

import workflow


SITE = {"name": "WorldJob Notice"}
LATEST = {
    "number": 1147,
    "title": "New notice",
    "date": "2026-03-01",
    "link": "https://example.test/notices/1147",
}


def configure_workflow(monkeypatch, saved, notifier=None):
    saved_calls = []
    monkeypatch.setattr(workflow, "fetch_latest_post", lambda site: LATEST)
    monkeypatch.setattr(workflow, "get_last_post", lambda site_name: saved)
    monkeypatch.setattr(
        workflow,
        "save_last_post",
        lambda site_name, number, title, link: saved_calls.append(
            (site_name, number, title, link)
        ),
    )
    monkeypatch.setattr(workflow, "send_discord_message", notifier or (lambda message: None))
    return saved_calls


def test_process_site_initializes_baseline_without_notification(monkeypatch):
    notifications = []
    saved_calls = configure_workflow(
        monkeypatch, None, lambda message: notifications.append(message)
    )

    result = workflow.process_site(SITE)

    assert result == {
        "status": "initialized",
        "site": "WorldJob Notice",
        "latest_number": 1147,
        "notification_sent": False,
    }
    assert saved_calls == [("WorldJob Notice", 1147, "New notice", LATEST["link"])]
    assert notifications == []


def test_process_site_skips_unchanged_notice(monkeypatch):
    notifications = []
    saved_calls = configure_workflow(
        monkeypatch,
        {"number": 1147, "title": "Old title", "link": "https://example.test/old"},
        lambda message: notifications.append(message),
    )

    result = workflow.process_site(SITE)

    assert result["status"] == "unchanged"
    assert result["notification_sent"] is False
    assert saved_calls == []
    assert notifications == []


def test_process_site_notifies_then_saves_checkpoint(monkeypatch):
    call_order = []
    saved_calls = []

    monkeypatch.setattr(workflow, "fetch_latest_post", lambda site: LATEST)
    monkeypatch.setattr(
        workflow,
        "get_last_post",
        lambda site_name: {"number": 1146, "title": "Old", "link": "https://example.test/old"},
    )
    monkeypatch.setattr(
        workflow,
        "save_last_post",
        lambda *args: (call_order.append("save"), saved_calls.append(args)),
    )

    def send(message):
        assert saved_calls == []
        call_order.append("notify")

    monkeypatch.setattr(workflow, "send_discord_message", send)

    result = workflow.process_site(SITE)

    assert result["status"] == "notified"
    assert result["notification_sent"] is True
    assert call_order == ["notify", "save"]
    assert saved_calls == [("WorldJob Notice", 1147, "New notice", LATEST["link"])]


def test_process_site_does_not_save_when_notification_fails(monkeypatch):
    saved_calls = configure_workflow(
        monkeypatch,
        {"number": 1146, "title": "Old", "link": "https://example.test/old"},
        lambda message: (_ for _ in ()).throw(RuntimeError("Discord unavailable")),
    )

    with pytest.raises(RuntimeError, match="Discord unavailable"):
        workflow.process_site(SITE)

    assert saved_calls == []
