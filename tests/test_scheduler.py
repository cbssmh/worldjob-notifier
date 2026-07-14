import scheduler


def test_check_sites_continues_after_one_site_fails(monkeypatch):
    sites = [{"name": "First"}, {"name": "Second"}]
    processed = []

    monkeypatch.setattr(scheduler, "load_sites", lambda: sites)

    def process(site):
        processed.append(site["name"])
        if site["name"] == "First":
            raise RuntimeError("source unavailable")
        return {
            "status": "unchanged",
            "site": site["name"],
            "latest_number": 1,
            "notification_sent": False,
        }

    monkeypatch.setattr(scheduler, "process_site", process)

    scheduler.check_sites()

    assert processed == ["First", "Second"]
