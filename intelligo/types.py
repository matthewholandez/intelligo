from pydantic import BaseModel


class ScrapedChapterMetadata(BaseModel):
    """
    Represents chapter metadata.
    """
    novel_title: str
    chapter_number: int | None


class ScrapedChapter(BaseModel):
    """
    Represents a raw novel chapter.
    """
    metadata: ScrapedChapterMetadata
    raw_text: str


class TranslatedChapter(BaseModel):
    """
    Represents a translated novel chapter.
    """
    novel_title: str
    chapter_title: str | None
    chapter_number: int | None
    translated_text: str


class GeminiChapterResponse(BaseModel):
    """
    Represents the output format Gemini should return.
    """
    chapter_title: str | None
    translated_text: str


class IntelligoConfigGemini(BaseModel):
    """
    Gemini configuration.
    """
    model: str
    temperature: float
    thinking_budget: int


class IntelligoConfigConstants(BaseModel):
    """
    Constants configuration.
    """
    max_attempts: int
    acceptable_line_count_ratio: float


class IntelligoConfig(BaseModel):
    """
    Configuration model.
    """
    gemini: IntelligoConfigGemini
    constants: IntelligoConfigConstants