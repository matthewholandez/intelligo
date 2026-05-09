import os

from openai import OpenAI
from dotenv import load_dotenv
from sqlite3 import Connection
from datetime import datetime

from schemas import TranslatedChapter, GlossaryEntryList

TRANSLATE_SYSTEM_PROMPT = """You are an expert web novel translator. Your only goal is to translate the novel chapter that the user provides, into English.

You will output in JSON form where:
- `body` is the chapter's content.
- `name` is the name of the chapter -- not the name of the novel -- WITHOUT a chapter number.
Both `name` and `body` are STRICTLY English fields. If the text given to you does NOT contain a clear chapter name, you may set `name` as null. Only `body` is required.

You will separate the content in `body` by newline characters as appropriate to distinguish between paragraphs.

You will maintain cultural nuances in your response as much as possible, converting idioms and phrases from the source language to English -- but don't force it."""

REASONING_SYSTEM_PROMPT = """You are the expert assistant on a web novel translation team.
Your only goal is to extract key terms from this web novel that will be placed in a 'glossary' for other translators.
This ensures translators use the term correctly for the entire series.

The criteria for a key term is:
1) Proper nouns, such as character names, place names, faction names, artifact/weapon names.
2) Cultural concepts, such as cultivation stages, martial arts techniques, honorifics used as titles, and terms with no obvious English equivalent.
3) Ambiguous terms, like anything that should be transliterated rather than translated, or words that you are uncertain about in general.

BUT, ignore:
1) Any common words that have standard and widespread English translations
2) Grammatical particles
3) Generic nouns, like sword or master

Output in JSON form, an array called `items` of the following objects:
- `term` is the term in question, IN THE SOURCE LANGUAGE
- `translation` is the ENGLISH translation of `term`, as they should be shown in the TRANSLATED VERSION
- `tag` classifies the term as one of: "character", "place", "technique", "honorific". Pick the closest fit; if none fit, use "technique" as a catch-all for cultural concepts.
"""

TRANSLATION_MODEL = "google/gemini-3-flash-preview"
REASONING_MODEL = "google/gemini-3.1-flash-lite"

TEMPERATURE = 0.7

load_dotenv()

client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)


def save_chapter(
    series_id: str,
    chapter_number: int,
    name: str | None,
    body: str,
    db: Connection,
    overwrite: bool = False,
) -> None:
    existing = db.execute(
        "SELECT 1 FROM chapters WHERE series_id = ? AND number = ?",
        (series_id, chapter_number),
    ).fetchone()
    if existing and not overwrite:
        raise ValueError(f"Chapter {chapter_number} already exists")
    if existing:
        db.execute(
            "UPDATE chapters SET name = ?, body = ?, created_at = ? WHERE series_id = ? AND number = ?",
            (name, body, datetime.now().isoformat(), series_id, chapter_number),
        )
    else:
        db.execute(
            "INSERT INTO chapters (series_id, number, name, body, created_at) VALUES (?, ?, ?, ?, ?)",
            (series_id, chapter_number, name, body, datetime.now().isoformat()),
        )
    db.commit()


def extract_key_terms(content: str, series_id: str, chapter_number: int, db: Connection) -> None:
    print("Parsing key terms now.")
    response = client.responses.parse(
        model=REASONING_MODEL,
        instructions=REASONING_SYSTEM_PROMPT,
        input=content,
        text_format=GlossaryEntryList,
    )
    if response.output_parsed:
        commit_time = datetime.now().isoformat()
        for item in response.output_parsed.items:
            db.execute(
                "INSERT OR IGNORE INTO glossary (series_id, term, translation, tag, first_seen_chapter, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (series_id, item.term, item.translation, item.tag, chapter_number, commit_time),
            )
            db.commit()
            print(f"Committed {item.term}: {item.translation} [{item.tag}]")


def translate_chapter(
    content: str,
    series_id: str,
    chapter_number: int,
    db: Connection,
    overwrite: bool = False,
) -> TranslatedChapter:
    extract_key_terms(content, series_id, chapter_number, db)
    response = client.responses.parse(
        model=TRANSLATION_MODEL,
        instructions=TRANSLATE_SYSTEM_PROMPT,
        input=content,
        reasoning={"effort": "medium"},
        text_format=TranslatedChapter,
    )
    if not response.output_parsed:
        raise RuntimeError("OpenRouter did not return a translation")
    save_chapter(
        series_id=series_id,
        chapter_number=chapter_number,
        name=response.output_parsed.name,
        body=response.output_parsed.body,
        db=db,
        overwrite=overwrite,
    )
    return response.output_parsed
