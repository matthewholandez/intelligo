"""Background translation pipeline.

Runs the two LLM agents (term extraction + translation) outside the request
cycle. Scheduled via FastAPI ``BackgroundTasks`` as a sync function, so Starlette
runs it in the threadpool and the blocking ``llm.invoke`` calls never touch the
event loop. Backs both chapter upload and re-translation.
"""

import logging

from sqlmodel import Session

from app.db import engine
from app.glossary import (
    format_for_prompt,
    load_glossary,
    merge_updates,
    scan_existing,
)
from app.translation import extract_terms, translate_text, write_translation_file
from app.types import Chapter, ChapterStatus

logger = logging.getLogger(__name__)


def run_translation_pipeline(chapter_id: int, novel_id: int) -> None:
    """Extract terms, then translate, persisting status at each stage.

    Opens its own session — the request session that scheduled this is already
    closed by the time the task runs.
    """
    with Session(engine) as session:
        chapter = session.get(Chapter, chapter_id)
        if chapter is None:
            logger.warning("Chapter %s vanished before translation", chapter_id)
            return

        try:
            chapter.status = ChapterStatus.analyzing
            chapter.error = None
            session.add(chapter)
            session.commit()

            existing_glossary = load_glossary(session, novel_id)

            # Agent 1 — extract new key terms, store with first-write-wins.
            new_terms = extract_terms(
                chapter.source_text, existing_terms=list(existing_glossary)
            )
            added = merge_updates(session, novel_id, existing_glossary, new_terms)

            chapter = session.get(Chapter, chapter_id)
            if chapter is None:
                return
            chapter.new_terms_count = added
            chapter.status = ChapterStatus.translating
            session.add(chapter)
            session.commit()

            # Deterministically gather glossary context (incl. freshly added terms).
            glossary_context = scan_existing(chapter.source_text, existing_glossary)

            # Agent 2 — translate using the glossary as canonical context.
            translated_text = translate_text(
                chapter.source_text,
                glossary_lines=format_for_prompt(glossary_context),
            )

            chapter.translated_text = translated_text
            chapter.status = ChapterStatus.completed
            session.add(chapter)
            session.commit()

            write_translation_file(novel_id, chapter.number, translated_text)
        except Exception as exc:  # noqa: BLE001 — surface any failure to the user
            logger.exception("Translation pipeline failed for chapter %s", chapter_id)
            session.rollback()
            chapter = session.get(Chapter, chapter_id)
            if chapter is not None:
                chapter.status = ChapterStatus.failed
                chapter.error = str(exc)
                session.add(chapter)
                session.commit()
