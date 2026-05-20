from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import col, select

from app.db import SessionDep
from app.types import (
    GlossaryEntry,
    GlossaryEntryCreate,
    GlossaryEntryPublic,
    GlossaryEntryUpdate,
    Novel,
)

router = APIRouter()


def _get_entry_or_404(session, novel_id: int, entry_id: int) -> GlossaryEntry:
    entry = session.get(GlossaryEntry, entry_id)
    if not entry or entry.novel_id != novel_id:
        raise HTTPException(status_code=404, detail="Glossary entry not found")
    return entry


@router.get("/novels/{novel_id}/glossary", response_model=list[GlossaryEntryPublic])
def list_glossary(novel_id: int, session: SessionDep):
    """List all glossary entries for a novel, ordered by source_term."""
    if not session.get(Novel, novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")
    return session.exec(
        select(GlossaryEntry)
        .where(GlossaryEntry.novel_id == novel_id)
        .order_by(col(GlossaryEntry.source_term))
    ).all()


@router.post("/novels/{novel_id}/glossary", response_model=GlossaryEntryPublic)
def create_glossary_entry(
    novel_id: int, entry: GlossaryEntryCreate, session: SessionDep
):
    """Manually add a glossary entry."""
    if not session.get(Novel, novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")
    db_entry = GlossaryEntry(
        novel_id=novel_id,
        source_term=entry.source_term,
        translation=entry.translation,
    )
    session.add(db_entry)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Glossary entry for this source_term already exists",
        )
    session.refresh(db_entry)
    return db_entry


@router.get(
    "/novels/{novel_id}/glossary/{entry_id}", response_model=GlossaryEntryPublic
)
def get_glossary_entry(novel_id: int, entry_id: int, session: SessionDep):
    """Get a single glossary entry."""
    return _get_entry_or_404(session, novel_id, entry_id)


@router.patch(
    "/novels/{novel_id}/glossary/{entry_id}", response_model=GlossaryEntryPublic
)
def update_glossary_entry(
    novel_id: int,
    entry_id: int,
    entry: GlossaryEntryUpdate,
    session: SessionDep,
):
    """Update a glossary entry."""
    entry_db = _get_entry_or_404(session, novel_id, entry_id)
    entry_db.sqlmodel_update(entry.model_dump(exclude_unset=True))
    session.add(entry_db)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Glossary entry for this source_term already exists",
        )
    session.refresh(entry_db)
    return entry_db


@router.delete("/novels/{novel_id}/glossary/{entry_id}")
def delete_glossary_entry(novel_id: int, entry_id: int, session: SessionDep):
    """Delete a glossary entry."""
    entry = _get_entry_or_404(session, novel_id, entry_id)
    session.delete(entry)
    session.commit()
    return {"ok": True}
