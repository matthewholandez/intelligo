from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openrouter import ChatOpenRouter

TRANSLATIONS_DIR = Path(__file__).resolve().parent.parent / "translations"
MODEL = "google/gemini-2.5-flash"

SYSTEM_PROMPT = (
    "You are a professional literary translator. Translate the user's chapter "
    "into fluent, natural English. Preserve paragraph breaks and any markdown "
    "formatting. Do not add commentary, headers, or notes — output only the "
    "translated chapter text."
)


def translate_text(source: str) -> str:
    llm = ChatOpenRouter(model=MODEL)
    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=source),
        ]
    )
    content = response.content
    return content if isinstance(content, str) else str(content)


def write_translation_file(novel_id: int, chapter_number: int, translated: str) -> Path:
    novel_dir = TRANSLATIONS_DIR / str(novel_id)
    novel_dir.mkdir(parents=True, exist_ok=True)
    path = novel_dir / f"chapter-{chapter_number:04d}.md"
    path.write_text(translated, encoding="utf-8")
    return path
