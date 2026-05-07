import sqlite3

DB_FILE = "intelligo.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS series (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS glossary (
    series_id TEXT NOT NULL REFERENCES series(id),
    term TEXT NOT NULL,
    translation TEXT NOT NULL,
    first_seen_chapter INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (series_id, term)
);
"""


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_FILE, check_same_thread=False)
    con.executescript(SCHEMA)
    con.commit()
    return con
