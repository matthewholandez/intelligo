from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from typing import Annotated

from app.types import Chapter, ChapterPublic, ChapterUpdate
from app.db import SessionDep

router = APIRouter()


@router.get("/novels/{novel_id}/chapters")
def get_chapters():
    ...