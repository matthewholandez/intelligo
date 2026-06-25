from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlmodel import col, select

from app.db import SessionDep
from app.extraction import extract_text_from_html
from app.glossary import (
    format_for_prompt,
    load_glossary,
    merge_updates,
    scan_existing,
)
from app.translation import extract_terms, translate_text, write_translation_file
from app.types import Chapter, ChapterPublic, ChapterUpdate, Novel

router = APIRouter()

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
    """Upload a chapter via .html file or raw source_text."""
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
        if suffix != ".html":
            raise HTTPException(
                status_code=400,
                detail="Unsupported file extension; expected .html",
            )
        raw_bytes = await file.read(MAX_BYTES + 1)
        if len(raw_bytes) > MAX_BYTES:
            raise HTTPException(status_code=413, detail="File too large (max 5 MB)")
        try:
            html = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be valid UTF-8")
        try:
            text = extract_text_from_html(html)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        assert source_text is not None
        text = source_text

    existing_glossary = load_glossary(session, novel_id)

    # Agent 1 — extract new key terms from this chapter (skipping known ones)
    # and store them in the glossary with first-write-wins semantics.
    new_terms = extract_terms(text, existing_terms=list(existing_glossary))
    merge_updates(session, novel_id, existing_glossary, new_terms)

    # Deterministically gather the glossary context for this chapter: existing
    # terms that are mentioned, plus the freshly extracted ones (now merged in).
    glossary_context = scan_existing(text, existing_glossary)

    # Agent 2 — translate using the glossary as canonical context.
    translated_text = translate_text(
        text, glossary_lines=format_for_prompt(glossary_context)
    )

    chapter = Chapter(
        number=number,
        source_text=text,
        translated_text=translated_text,
        novel_id=novel_id,
    )
    session.add(chapter)
    session.commit()
    session.refresh(chapter)

    write_translation_file(novel_id, chapter.number, translated_text)
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
