from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlmodel import col, select

from app.db import SessionDep
from app.types import Chapter, ChapterPublic, ChapterUpdate, Novel

router = APIRouter()

SUPPORTED_EXTENSIONS = {".md", ".html"}
MAX_BYTES = 5 * 1024 * 1024


def _get_chapter_or_404(session, novel_id: int, chap_id: int) -> Chapter:
    chapter = session.get(Chapter, chap_id)
    if not chapter or chapter.novel_id != novel_id:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.post("/novels/{novel_id}/chapters", response_model=ChapterPublic)
async def create_chapter(
    novel_id: int,
    session: SessionDep,
    number: Annotated[int, Form()],
    file: UploadFile | None = File(default=None),
    source_text: Annotated[str | None, Form()] = None,
):
    """Upload a chapter via file (.md/.html) or raw source_text."""
    if not session.get(Novel, novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")

    if file is not None and source_text is not None:
        raise HTTPException(
            status_code=400,
            detail="Provide either file or source_text, not both",
        )
    if file is None and source_text is None:
        raise HTTPException(
            status_code=400, detail="Provide either file or source_text"
        )

    if file is not None:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file extension; expected one of {sorted(SUPPORTED_EXTENSIONS)}",
            )
        raw_bytes = await file.read(MAX_BYTES + 1)
        if len(raw_bytes) > MAX_BYTES:
            raise HTTPException(status_code=413, detail="File too large (max 5 MB)")
        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be valid UTF-8")
    else:
        assert source_text is not None
        text = source_text

    chapter = Chapter(number=number, source_text=text, novel_id=novel_id)
    session.add(chapter)
    session.commit()
    session.refresh(chapter)
    return chapter


@router.get("/novels/{novel_id}/chapters", response_model=list[ChapterPublic])
def list_chapters(novel_id: int, session: SessionDep):
    """List all chapters for a novel, ordered by chapter number."""
    if not session.get(Novel, novel_id):
        raise HTTPException(status_code=404, detail="Novel not found")
    return session.exec(
        select(Chapter)
        .where(Chapter.novel_id == novel_id)
        .order_by(col(Chapter.number))
    ).all()


@router.get("/novels/{novel_id}/chapters/{chap_id}", response_model=ChapterPublic)
def get_chapter(novel_id: int, chap_id: int, session: SessionDep):
    """Get a single chapter."""
    return _get_chapter_or_404(session, novel_id, chap_id)


@router.patch("/novels/{novel_id}/chapters/{chap_id}", response_model=ChapterPublic)
def update_chapter(
    novel_id: int,
    chap_id: int,
    chapter: ChapterUpdate,
    session: SessionDep,
):
    """Update a chapter."""
    chapter_db = _get_chapter_or_404(session, novel_id, chap_id)
    chapter_db.sqlmodel_update(chapter.model_dump(exclude_unset=True))
    session.add(chapter_db)
    session.commit()
    session.refresh(chapter_db)
    return chapter_db


@router.delete("/novels/{novel_id}/chapters/{chap_id}")
def delete_chapter(novel_id: int, chap_id: int, session: SessionDep):
    """Delete a chapter."""
    chapter = _get_chapter_or_404(session, novel_id, chap_id)
    session.delete(chapter)
    session.commit()
    return {"ok": True}
