import sqlite3

DB_FILE = "intelligo.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS series (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
)
"""


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_FILE, check_same_thread=False)
    con.execute(SCHEMA)
    con.commit()
    return con
