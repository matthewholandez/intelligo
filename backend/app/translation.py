from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openrouter import ChatOpenRouter

from app.types import ChapterResponse

TRANSLATIONS_DIR = Path(__file__).resolve().parent.parent / "translations"
MODEL = "google/gemini-2.5-flash"

SYSTEM_PROMPT_BASE = (
    "You are a professional literary translator. Translate the user's chapter "
    "into fluent, natural English. Preserve paragraph breaks and markdown "
    "formatting. translated_text must contain only the translated chapter — "
    "no commentary, headers, or notes.\n\n"
    "Additionally, extract any new proper nouns, character names, factions, "
    "titles, skills, realms, or key items that should be translated "
    "consistently across future chapters, and return them as glossary_updates. "
    "Only include stable, recurring terms — no common nouns or uncertain "
    "mappings. Do NOT propose updates for terms already in the glossary."
)


def _build_system_prompt(glossary_lines: str | None) -> str:
    if not glossary_lines:
        return SYSTEM_PROMPT_BASE
    return (
        f"{SYSTEM_PROMPT_BASE}\n\n"
        f"<glossary_reference>\n{glossary_lines}\n</glossary_reference>\n"
        "Use these canonical translations verbatim whenever the source term appears."
    )


def translate_text(source: str, glossary_lines: str | None = None) -> ChapterResponse:
    llm = ChatOpenRouter(model=MODEL).with_structured_output(ChapterResponse)
    result = llm.invoke(
        [
            SystemMessage(content=_build_system_prompt(glossary_lines)),
            HumanMessage(content=source),
        ]
    )
    assert isinstance(result, ChapterResponse)
    return result


def write_translation_file(novel_id: int, chapter_number: int, translated: str) -> Path:
    novel_dir = TRANSLATIONS_DIR / str(novel_id)
    novel_dir.mkdir(parents=True, exist_ok=True)
    path = novel_dir / f"chapter-{chapter_number:04d}.md"
    path.write_text(translated, encoding="utf-8")
    return path
