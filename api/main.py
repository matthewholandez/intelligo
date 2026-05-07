from fastapi import FastAPI, File, Form, HTTPException
from typing import Annotated, Dict
from pydantic import BaseModel
from contextlib import asynccontextmanager
from openrouter import OpenRouter
from dotenv import load_dotenv
import uuid
import sqlite3
import datetime
import os

load_dotenv()

MAX_CHARS_IN_SERIES_NAME = 150
DB_FILE = "intelligo.db"
KEY = os.getenv("OPENROUTER_API_KEY")

database: Dict[str, sqlite3.Connection] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the database before startup
    con = sqlite3.connect(DB_FILE, check_same_thread=False)
    con.execute("""
        CREATE TABLE IF NOT EXISTS series (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    con.commit()
    database["con"] = con
    
    yield

    # Unload after exit
    database["con"].close()

app = FastAPI(lifespan=lifespan)

def create_series_id(series_name: str) -> str:
    series_id = str(uuid.uuid4())
    current_datetime = datetime.datetime.now()

    cur = database["con"].cursor()
    cur.execute("INSERT INTO series VALUES (?, ?, ?)", (series_id, series_name, current_datetime))
    database["con"].commit()
    
    return series_id

class Series(BaseModel):
    id: str
    name: str
    created_at: str

def get_series_info(id: str) -> Series | None:
    cur = database["con"].cursor()
    
    res = cur.execute("SELECT id, name, created_at FROM series WHERE id=(?)", (id,))
    info = res.fetchone()
    database["con"].commit()

    if info:
        return Series(
            id=info[0],
            name=info[1],
            created_at=info[2]
        )
    else:
        return None
    
@app.get("/api/series")
def read_series(
    id: str
) -> Series:
    series_info: Series | None = get_series_info(id)

    if series_info is None:
        raise HTTPException(status_code=400, detail=f"Series with id {id} does not exist")

    return series_info

class SeriesPostRequest(BaseModel):
    name: str

class SeriesPostResponse(BaseModel):
    id: str
    name: str

@app.post("/api/series")
def create_series(
    req: SeriesPostRequest
) -> SeriesPostResponse:
    if len(req.name) > MAX_CHARS_IN_SERIES_NAME:
        raise HTTPException(status_code=400, detail=f"Series name is too long (limit: {MAX_CHARS_IN_SERIES_NAME} characters)")

    id = create_series_id(req.name)

    return SeriesPostResponse(
        id=id,
        name=req.name
    )

def translate_chapter(content: str):
    prompt = "You are an expert web novel translator. Translate the user's text into English."

    with OpenRouter(KEY) as client:
        response = client.chat.send(
            model="google/gemini-3-flash-preview",
            messages=[
                { "role": "system", "content": prompt },
                { "role": "user", "content": content }
            ],
            stream=False,
            temperature=0.7
        )
        return response.choices[0].message.content

@app.post("/api/translations")
def create_translation(
    chapter_number: Annotated[int, Form(alias="chapterNumber")],
    series_id: Annotated[str, Form(alias="seriesId")],
    overwrite_chapter_if_exists: Annotated[bool, Form(alias="overwriteChapterIfExists")] = False,
    chapter_file: Annotated[bytes | None, File(alias="chapterFile")] = None,
    chapter_body: Annotated[str | None, Form(alias="chapterBody")] = None,
):
    
    if chapter_file and chapter_body:
        raise HTTPException(status_code=422, detail="chapterFile and chapterBody cannot both be populated")  
    
    if not chapter_file and not chapter_body:
        raise HTTPException(status_code=400, detail="Provide either chapterFile or chapterBody")
    
    if not series_id or not chapter_number:
        raise HTTPException(status_code=400, detail="chapterNumber and seriesId are required fields")

    # Check if series_id is real
    info = get_series_info(series_id)
    if info is None:
        raise HTTPException(status_code=400, detail="Invalid seriesId was provided")
    
    if chapter_body:
        t = translate_chapter(chapter_body)
        return t

    return chapter_body