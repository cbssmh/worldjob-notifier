import sqlite3
from config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS site_state (
        site_name TEXT PRIMARY KEY,
        last_number INTEGER,
        last_title TEXT,
        last_link TEXT
    )
    """)

    conn.commit()
    conn.close()


def get_last_post(site_name: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT last_number, last_title, last_link FROM site_state WHERE site_name = ?",
        (site_name,)
    )
    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "number": row[0],
            "title": row[1],
            "link": row[2]
        }
    return None


def save_last_post(site_name: str, number: int, title: str, link: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO site_state (site_name, last_number, last_title, last_link)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(site_name) DO UPDATE SET
        last_number = excluded.last_number,
        last_title = excluded.last_title,
        last_link = excluded.last_link
    """, (site_name, number, title, link))

    conn.commit()
    conn.close()