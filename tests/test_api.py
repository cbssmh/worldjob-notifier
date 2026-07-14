from fastapi.testclient import TestClient

import api
import db


def test_api_startup_initializes_db_and_health_is_available(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "api.db"))

    with TestClient(api.app) as client:
        assert client.get("/health").json() == {"ok": True}
        response = client.get("/last-notice")

    assert response.status_code == 200
    assert response.json() == {"message": "No notice stored yet"}


def test_run_check_returns_workflow_result(monkeypatch, tmp_path):
    expected = {
        "status": "initialized",
        "site": "WorldJob Notice",
        "latest_number": 1147,
        "notification_sent": False,
    }
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "api.db"))
    monkeypatch.setattr(api, "process_site", lambda site: expected)

    with TestClient(api.app) as client:
        response = client.post("/run-check")

    assert response.status_code == 200
    assert response.json() == expected


def test_run_check_returns_5xx_when_workflow_fails(monkeypatch, tmp_path):
    def fail(site):
        raise RuntimeError("upstream unavailable")

    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "api.db"))
    monkeypatch.setattr(api, "process_site", fail)

    with TestClient(api.app) as client:
        response = client.post("/run-check")

    assert response.status_code == 502
    assert response.json() == {"detail": "Notice check failed"}
