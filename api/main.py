import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Query, Response, UploadFile

from trafilatura import extract

from db import connect, slugify
from schemas import (
    Bookmark,
    Chapter,
    ChapterRef,
    ChapterRefList,
    GlossaryEntry,
    Novel,
    NovelList,
    NovelPostResponse,
    PressItemList,
    RecentChapter,
    RecentChapterList,
    Series,
    SeriesPostRequest,
    SeriesPostResponse,
    TermRow,
    TermRowList,
    TranslateResponse,
)
from translator import translate_chapter

load_dotenv()

MAX_CHARS_IN_SERIES_NAME = 150


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = connect()
    yield
    app.state.db.close()


app = FastAPI(lifespan=lifespan)


# ---------- helpers ----------

def _unique_slug(base: str) -> str:
    db = app.state.db
    slug = base
    i = 2
    while db.execute("SELECT 1 FROM series WHERE slug = ?", (slug,)).fetchone():
        slug = f"{base}-{i}"
        i += 1
    return slug


def create_series(name: str) -> tuple[str, str]:
    series_id = str(uuid.uuid4())
    slug = _unique_slug(slugify(name))
    app.state.db.execute(
        "INSERT INTO series (id, name, slug, created_at) VALUES (?, ?, ?, ?)",
        (series_id, name, slug, datetime.now().isoformat()),
    )
    app.state.db.commit()
    return series_id, slug


def get_series(series_id: str) -> Series | None:
    row = app.state.db.execute(
        "SELECT id, name, created_at FROM series WHERE id = ?",
        (series_id,),
    ).fetchone()
    if row is None:
        return None
    return Series(id=row[0], name=row[1], created_at=row[2])


def get_series_by_slug(slug: str) -> tuple[str, str] | None:
    row = app.state.db.execute(
        "SELECT id, name FROM series WHERE slug = ?",
        (slug,),
    ).fetchone()
    if row is None:
        return None
    return row[0], row[1]


def _current_novel_slug() -> str | None:
    row = app.state.db.execute(
        """
        SELECT s.slug FROM chapters c
        JOIN series s ON s.id = c.series_id
        ORDER BY c.created_at DESC LIMIT 1
        """
    ).fetchone()
    return row[0] if row else None


# ---------- legacy series routes (kept for back-compat) ----------

@app.get("/api/series")
def read_series(id: str) -> Series:
    series = get_series(id)
    if series is None:
        raise HTTPException(status_code=404, detail=f"Series with id {id} does not exist")
    return series


@app.post("/api/series")
def post_series(req: SeriesPostRequest) -> SeriesPostResponse:
    if len(req.name) > MAX_CHARS_IN_SERIES_NAME:
        raise HTTPException(
            status_code=400,
            detail=f"Series name is too long (limit: {MAX_CHARS_IN_SERIES_NAME} characters)",
        )
    series_id, _ = create_series(req.name)
    return SeriesPostResponse(id=series_id, name=req.name)


# ---------- novels ----------

@app.get("/api/novels")
def list_novels() -> NovelList:
    current = _current_novel_slug()
    rows = app.state.db.execute(
        "SELECT slug, name FROM series ORDER BY created_at ASC"
    ).fetchall()
    items = [
        Novel(slug=row[0], name=row[1], is_current=(row[0] == current))
        for row in rows
        if row[0]
    ]
    return NovelList(items=items)


@app.post("/api/novels")
def create_novel(req: SeriesPostRequest) -> NovelPostResponse:
    if len(req.name) > MAX_CHARS_IN_SERIES_NAME:
        raise HTTPException(
            status_code=400,
            detail=f"Novel name is too long (limit: {MAX_CHARS_IN_SERIES_NAME} characters)",
        )
    series_id, slug = create_series(req.name)
    return NovelPostResponse(id=series_id, slug=slug, name=req.name)


@app.get("/api/novels/{slug}")
def get_novel(slug: str) -> Novel:
    found = get_series_by_slug(slug)
    if found is None:
        raise HTTPException(status_code=404, detail=f"Novel '{slug}' does not exist")
    _, name = found
    return Novel(slug=slug, name=name, is_current=(_current_novel_slug() == slug))


# ---------- chapters ----------

def _chapter_ref(row) -> ChapterRef:
    return ChapterRef(number=row[0], name=row[1])


@app.get("/api/novels/{slug}/chapters")
def list_chapters(slug: str) -> ChapterRefList:
    found = get_series_by_slug(slug)
    if found is None:
        raise HTTPException(status_code=404, detail=f"Novel '{slug}' does not exist")
    sid, _ = found
    rows = app.state.db.execute(
        "SELECT number, name FROM chapters WHERE series_id = ? ORDER BY number ASC",
        (sid,),
    ).fetchall()
    return ChapterRefList(items=[_chapter_ref(r) for r in rows])


@app.get("/api/novels/{slug}/chapters/{number}")
def get_chapter(slug: str, number: int) -> Chapter:
    found = get_series_by_slug(slug)
    if found is None:
        raise HTTPException(status_code=404, detail=f"Novel '{slug}' does not exist")
    sid, _ = found
    row = app.state.db.execute(
        "SELECT number, name, body FROM chapters WHERE series_id = ? AND number = ?",
        (sid, number),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Chapter {number} does not exist")

    prev_row = app.state.db.execute(
        "SELECT number, name FROM chapters WHERE series_id = ? AND number < ? ORDER BY number DESC LIMIT 1",
        (sid, number),
    ).fetchone()
    next_row = app.state.db.execute(
        "SELECT number, name FROM chapters WHERE series_id = ? AND number > ? ORDER BY number ASC LIMIT 1",
        (sid, number),
    ).fetchone()

    body = row[2]
    glossary_rows = app.state.db.execute(
        "SELECT term, translation, tag FROM glossary WHERE series_id = ?",
        (sid,),
    ).fetchall()
    referenced = [
        GlossaryEntry(term=g[0], translation=g[1], tag=g[2])
        for g in glossary_rows
        if g[0] in body or g[1] in body
    ]

    return Chapter(
        number=row[0],
        name=row[1],
        body=body,
        prev=_chapter_ref(prev_row) if prev_row else None,
        next=_chapter_ref(next_row) if next_row else None,
        glossary=referenced,
    )


@app.get("/api/chapters/recent")
def recent_chapters(limit: int = Query(3, ge=1, le=20)) -> RecentChapterList:
    rows = app.state.db.execute(
        """
        SELECT s.name, s.slug, c.name, c.number, c.body
        FROM chapters c JOIN series s ON s.id = c.series_id
        ORDER BY c.created_at DESC LIMIT ?
        """,
        (limit,),
    ).fetchall()
    items = []
    for novel_name, slug, ch_name, number, body in rows:
        if not slug:
            continue
        preview = (body or "").strip().split("\n", 1)[0][:240]
        items.append(
            RecentChapter(
                novel=novel_name,
                novel_slug=slug,
                title=ch_name,
                preview=preview,
                chapter=number,
            )
        )
    return RecentChapterList(items=items)


# ---------- bookmark ----------

@app.get("/api/bookmark")
def get_bookmark(response: Response):
    row = app.state.db.execute(
        """
        SELECT s.slug, s.name, c.number, c.name, c.body, c.created_at
        FROM chapters c JOIN series s ON s.id = c.series_id
        ORDER BY c.created_at DESC LIMIT 1
        """
    ).fetchone()
    if row is None:
        response.status_code = 204
        return None
    slug, novel_name, number, ch_name, body, _ = row
    if not slug:
        response.status_code = 204
        return None
    title = (
        f"Chapter {number} · {ch_name}" if ch_name else f"Chapter {number}"
    )
    preview = (body or "").strip().split("\n", 1)[0][:240]
    last_24h = app.state.db.execute(
        "SELECT COUNT(*) FROM chapters WHERE created_at >= datetime('now', '-1 day')"
    ).fetchone()[0]
    return Bookmark(
        novel_slug=slug,
        novel_name=novel_name,
        chapter=number,
        title=title,
        preview=preview,
        chapters_last_24h=last_24h,
    )


# ---------- press ----------

@app.get("/api/press")
def get_press() -> PressItemList:
    return PressItemList(items=[])


# ---------- glossary ----------

@app.get("/api/novels/{slug}/glossary")
def list_glossary(
    slug: str,
    q: str | None = None,
    tag: str | None = None,
) -> TermRowList:
    found = get_series_by_slug(slug)
    if found is None:
        raise HTTPException(status_code=404, detail=f"Novel '{slug}' does not exist")
    sid, _ = found
    sql = "SELECT term, translation, tag, first_seen_chapter FROM glossary WHERE series_id = ?"
    params: list = [sid]
    if tag:
        sql += " AND tag = ?"
        params.append(tag)
    if q:
        sql += " AND (term LIKE ? OR translation LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])
    sql += " ORDER BY first_seen_chapter ASC, term ASC"
    rows = app.state.db.execute(sql, params).fetchall()
    items = [
        TermRow(source=r[0], preferred=r[1], tag=r[2], chapter=r[3])
        for r in rows
    ]
    return TermRowList(items=items)


# ---------- translations ----------

def get_text_from_file(html: UploadFile):
    contents = html.file.read()
    return contents


@app.post("/api/translations")
def create_translation(
    chapter_number: Annotated[int, Form(alias="chapterNumber")],
    series_id: Annotated[str, Form(alias="seriesId")],
    overwrite_chapter_if_exists: Annotated[bool, Form(alias="overwriteChapterIfExists")] = False,
    chapter_file: Annotated[UploadFile | None, File(alias="chapterFile")] = None,
    chapter_body: Annotated[str | None, Form(alias="chapterBody")] = None,
) -> TranslateResponse:
    if chapter_file and chapter_body:
        raise HTTPException(status_code=422, detail="chapterFile and chapterBody cannot both be populated")
    if chapter_file is None and chapter_body is None:
        raise HTTPException(status_code=400, detail="Provide either chapterFile or chapterBody")

    if get_series(series_id) is None:
        raise HTTPException(status_code=400, detail="Invalid seriesId was provided")

    try:
        if chapter_body:
            translate_chapter(
                chapter_body, series_id, chapter_number, app.state.db,
                overwrite=overwrite_chapter_if_exists,
            )
            return TranslateResponse(ok=True)

        if chapter_file:
            text = get_text_from_file(chapter_file)
            extracted_text = extract(text)
            if not extracted_text:
                raise HTTPException(status_code=422, detail="Could not extract chapter text from upload")
            translate_chapter(
                extracted_text, series_id, chapter_number, app.state.db,
                overwrite=overwrite_chapter_if_exists,
            )
            return TranslateResponse(ok=True)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    raise HTTPException(status_code=500, detail="Unreachable")
