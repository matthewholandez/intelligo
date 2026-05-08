import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from trafilatura import extract

from db import connect
from schemas import Series, SeriesPostRequest, SeriesPostResponse, TranslateResponse
from translator import translate_chapter

load_dotenv()

MAX_CHARS_IN_SERIES_NAME = 150


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = connect()
    yield
    app.state.db.close()


app = FastAPI(lifespan=lifespan)


def create_series(name: str) -> str:
    series_id = str(uuid.uuid4())
    app.state.db.execute(
        "INSERT INTO series VALUES (?, ?, ?)",
        (series_id, name, datetime.now().isoformat()),
    )
    app.state.db.commit()
    return series_id


def get_series(series_id: str) -> Series | None:
    row = app.state.db.execute(
        "SELECT id, name, created_at FROM series WHERE id = ?",
        (series_id,),
    ).fetchone()
    if row is None:
        return None
    return Series(id=row[0], name=row[1], created_at=row[2])


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
    series_id = create_series(req.name)
    return SeriesPostResponse(id=series_id, name=req.name)


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

    if chapter_body:
        translate_chapter(chapter_body, series_id, chapter_number, app.state.db)
        return TranslateResponse(ok=True)
    
    elif chapter_file:
        text = get_text_from_file(chapter_file)
        extracted_text = extract(text)
        if extracted_text:
            translate_chapter(extracted_text, series_id, chapter_number, app.state.db)
            return TranslateResponse(ok=True)
        raise RuntimeError("Extraction failed")

    raise HTTPException(status_code=501, detail="chapterFile uploads are not implemented yet")
