from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openrouter import ChatOpenRouter

from app.types import GlossaryExtraction, GlossaryUpdate, TranslatedChapter

TRANSLATIONS_DIR = Path(__file__).resolve().parent.parent / "translations"
MODEL = "google/gemini-2.5-flash"

EXTRACTION_SYSTEM_PROMPT = (
    "You are a glossary builder for a literary translation pipeline. Read the "
    "chapter and extract proper nouns, character names, factions, titles, "
    "skills, realms, or key items that should be translated consistently "
    "across future chapters. For each, return the source term and a preferred "
    "English translation. Only include stable, recurring terms — no common "
    "nouns or uncertain mappings."
)

TRANSLATION_SYSTEM_PROMPT = (
    "You are a professional literary translator. Translate the user's chapter "
    "into fluent, natural English. Preserve paragraph breaks and markdown "
    "formatting. translated_text must contain only the translated chapter — "
    "no commentary, headers, or notes."
)


def _build_extraction_prompt(existing_terms: list[str]) -> str:
    if not existing_terms:
        return EXTRACTION_SYSTEM_PROMPT
    block = "\n".join(f"- {term}" for term in sorted(existing_terms, key=str.lower))
    return (
        f"{EXTRACTION_SYSTEM_PROMPT}\n\n"
        f"<existing_glossary>\n{block}\n</existing_glossary>\n"
        "Do NOT include any term that already appears in the existing glossary."
    )


def _build_translation_prompt(glossary_lines: str | None) -> str:
    if not glossary_lines:
        return TRANSLATION_SYSTEM_PROMPT
    return (
        f"{TRANSLATION_SYSTEM_PROMPT}\n\n"
        f"<glossary_reference>\n{glossary_lines}\n</glossary_reference>\n"
        "Use these canonical translations verbatim whenever the source term appears."
    )


def extract_terms(source: str, existing_terms: list[str]) -> list[GlossaryUpdate]:
    """Agent 1: extract new glossary terms from a chapter, skipping known ones."""
    llm = ChatOpenRouter(model=MODEL).with_structured_output(GlossaryExtraction)
    result = llm.invoke(
        [
            SystemMessage(content=_build_extraction_prompt(existing_terms)),
            HumanMessage(content=source),
        ]
    )
    assert isinstance(result, GlossaryExtraction)
    return result.terms


def translate_text(source: str, glossary_lines: str | None = None) -> str:
    """Agent 2: translate a chapter, using the glossary as canonical context."""
    llm = ChatOpenRouter(model=MODEL).with_structured_output(TranslatedChapter)
    result = llm.invoke(
        [
            SystemMessage(content=_build_translation_prompt(glossary_lines)),
            HumanMessage(content=source),
        ]
    )
    assert isinstance(result, TranslatedChapter)
    return result.translated_text


def write_translation_file(novel_id: int, chapter_number: int, translated: str) -> Path:
    novel_dir = TRANSLATIONS_DIR / str(novel_id)
    novel_dir.mkdir(parents=True, exist_ok=True)
    path = novel_dir / f"chapter-{chapter_number:04d}.md"
    path.write_text(translated, encoding="utf-8")
    return path
