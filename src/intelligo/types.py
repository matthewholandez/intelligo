from pydantic import BaseModel


class ScrapedChapter(BaseModel):
    """
    Represents a chapter of a novel after scraping.
    """
    novel_title: str
    chapter_number: int
    raw_text: str


class GeminiChapterResponse(BaseModel):
    """
    Represents the output format Gemini should return.
    """
    chapter_title: str | None
    translated_text: str

class TranslatedChapter(BaseModel):
    """
    Represents a translated chapter of a novel.
    """
    novel_title: str
    chapter_title: str | None
    chapter_number: int
    translated_text: str


class GeminiConfig(BaseModel):
    model: str
    temperature: float
    thinking_budget: int


class IntelligoConfig(BaseModel):
    """
    Configuration model.
    """
    gemini: GeminiConfig