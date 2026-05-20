from sqlmodel import Session, select

from app.types import GlossaryEntry, GlossaryUpdate


def load_glossary(session: Session, novel_id: int) -> dict[str, str]:
    rows = session.exec(
        select(GlossaryEntry).where(GlossaryEntry.novel_id == novel_id)
    ).all()
    return {r.source_term: r.translation for r in rows}


def format_for_prompt(glossary: dict[str, str]) -> str | None:
    if not glossary:
        return None
    lines = sorted(
        (f"- {src} => {tgt}" for src, tgt in glossary.items()),
        key=str.lower,
    )
    return "\n".join(lines)


def merge_updates(
    session: Session,
    novel_id: int,
    existing: dict[str, str],
    updates: list[GlossaryUpdate],
) -> int:
    """First-write-wins: only insert terms not already present. Returns count added."""
    added = 0
    for u in updates:
        src = u.source_term.strip()
        tgt = u.preferred_translation.strip()
        if not src or not tgt or src in existing:
            continue
        session.add(GlossaryEntry(novel_id=novel_id, source_term=src, translation=tgt))
        existing[src] = tgt
        added += 1
    if added:
        session.commit()
    return added
