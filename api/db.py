import re
import sqlite3

DB_FILE = "intelligo.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS series (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS chapters (
    series_id TEXT NOT NULL REFERENCES series(id),
    number INTEGER NOT NULL,
    name TEXT,
    body TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (series_id, number)
);

CREATE TABLE IF NOT EXISTS glossary (
    series_id TEXT NOT NULL REFERENCES series(id),
    term TEXT NOT NULL,
    translation TEXT NOT NULL,
    tag TEXT,
    first_seen_chapter INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (series_id, term)
);
"""


def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return s or "untitled"


def _columns(con: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in con.execute(f"PRAGMA table_info({table})").fetchall()}


def _migrate(con: sqlite3.Connection) -> None:
    series_cols = _columns(con, "series")
    if "slug" not in series_cols:
        con.execute("ALTER TABLE series ADD COLUMN slug TEXT")
        rows = con.execute("SELECT id, name FROM series").fetchall()
        used: set[str] = set()
        for sid, name in rows:
            base = slugify(name)
            slug = base
            i = 2
            while slug in used:
                slug = f"{base}-{i}"
                i += 1
            used.add(slug)
            con.execute("UPDATE series SET slug = ? WHERE id = ?", (slug, sid))
        con.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_series_slug ON series(slug)")

    glossary_cols = _columns(con, "glossary")
    if "tag" not in glossary_cols:
        con.execute("ALTER TABLE glossary ADD COLUMN tag TEXT")


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_FILE, check_same_thread=False)
    con.executescript(SCHEMA)
    _migrate(con)
    con.commit()
    return con
