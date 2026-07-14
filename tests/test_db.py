import db


def test_db_insert_read_upsert_and_site_isolation(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "notifier.db"))
    db.init_db()

    db.save_last_post("First", 1, "First title", "https://example.test/1")
    assert db.get_last_post("First") == {
        "number": 1,
        "title": "First title",
        "link": "https://example.test/1",
    }

    db.save_last_post("First", 2, "Updated title", "https://example.test/2")
    db.save_last_post("Second", 3, "Second title", "https://example.test/3")

    assert db.get_last_post("First")["number"] == 2
    assert db.get_last_post("Second")["number"] == 3
