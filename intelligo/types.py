from pydantic import BaseModel, Field


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


class GlossaryUpdate(BaseModel):
    """
    Represents a candidate terminology mapping.
    """
    source_term: str
    preferred_translation: str


class ChapterResponse(BaseModel):
    """
    Represents the output format the LLM should return.
    """
    chapter_title: str | None
    translated_text: str
    glossary_updates: list[GlossaryUpdate] = Field(default_factory=list)


class IntelligoConfigOpenRouter(BaseModel):
    """
    OpenRouter configuration.
    """
    model: str
    temperature: float


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
    openrouter: IntelligoConfigOpenRouter
    constants: IntelligoConfigConstants
