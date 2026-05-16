from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from typing import Annotated

from app.types import NovelPublic, NovelCreate, NovelUpdate, Novel
from app.db import SessionDep

router = APIRouter()


@router.get("/novels/{novel_id}", response_model=NovelPublic)
def get_novel_by_id(novel_id: int, session: SessionDep):
    """Get a novel by its ID."""
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    return novel

@router.get("/novels", response_model=list[NovelPublic])
def get_novels(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
    ):
    """Get all novels."""
    novels = session.exec(select(Novel).offset(offset).limit(limit)).all()
    return novels

@router.post("/novels", response_model=NovelPublic)
def create_novel(novel: NovelCreate, session: SessionDep):
    """Create a new novel."""
    db_novel = Novel.model_validate(novel)
    session.add(db_novel)
    session.commit()
    session.refresh(db_novel)
    return db_novel

@router.patch("/novels/{novel_id}", response_model=NovelPublic)
def update_novel(novel_id: int, novel: NovelUpdate, session: SessionDep):
    novel_db = session.get(Novel, novel_id)
    if not novel_db:
        raise HTTPException(status_code=404, detail="Novel not found")
    novel_data = novel.model_dump(exclude_unset=True)
    novel_db.sqlmodel_update(novel_data)
    session.add(novel_db)
    session.commit()
    session.refresh(novel_db)
    return novel_db

@router.delete("/novels/{novel_id}")
def delete_novel(novel_id: int, session: SessionDep):
    """Delete a novel."""
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    session.delete(novel)
    session.commit()
    return { "ok": True }