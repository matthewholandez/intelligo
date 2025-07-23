from pydantic import BaseModel


class ScrapedChapter(BaseModel):
    """
    Represents a raw novel chapter.
    """
    novel_title: str
    chapter_number: int
    raw_text: str


class TranslatedChapter(BaseModel):
    """
    Represents a translated novel chapter.
    """
    novel_title: str
    chapter_title: str | None
    chapter_number: int
    translated_text: str


class GeminiChapterResponse(BaseModel):
    """
    Represents the output format Gemini should return.
    """
    chapter_title: str | None
    translated_text: str


class GeminiConfig(BaseModel):
    """
    Gemini configuration.
    """
    model: str
    temperature: float
    thinking_budget: int


class IntelligoConfig(BaseModel):
    """
    Configuration model.
    """
    gemini: GeminiConfig