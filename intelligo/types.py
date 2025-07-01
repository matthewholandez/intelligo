from pydantic import BaseModel

class RawChapter(BaseModel):
    """
    Represents a chapter of a novel in its raw form.
    """
    novel_title: str
    content: str
    number: int

class TranslatedChapter(RawChapter):
    """
    Represents a chapter of a novel after translation.
    """
    chapter_title: str | None = None

class GeminiChapterOutput(BaseModel):
    """
    Represents the output format for the translated chapter.
    """
    chapter_title: str | None = None
    content: str