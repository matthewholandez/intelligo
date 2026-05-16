from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from typing import Annotated

from app.types import NovelPublic, NovelCreate, NovelUpdate, Novel
from app.db import SessionDep

router = APIRouter()


@router.get("/novels/{novel_id}/chapters")
def get_chapters():
    ...