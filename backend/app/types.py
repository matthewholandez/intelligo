from datetime import datetime

from pydantic import BaseModel
from pydantic import Field as PydField
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


# ================================
# NOVELS
# ================================
class NovelBase(SQLModel):
    name: str = Field(index=True)

class Novel(NovelBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_on: datetime = Field(default_factory=datetime.now)
    updated_on: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": lambda: datetime.now()}
        )

class NovelPublic(NovelBase):
    id: int
    updated_on: datetime

class NovelCreate(NovelBase):
    ...

class NovelUpdate(NovelBase):
    ...


# ================================
# CHAPTERS
# ================================
class ChapterBase(SQLModel):
    number: int = Field(index=True)
    source_text: str

class Chapter(ChapterBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    novel_id: int = Field(foreign_key="novel.id", index=True)
    translated_text: str | None = None
    created_on: datetime = Field(default_factory=datetime.now)
    updated_on: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": lambda: datetime.now()},
    )

class ChapterPublic(ChapterBase):
    id: int
    novel_id: int
    translated_text: str | None
    updated_on: datetime

class ChapterCreate(ChapterBase):
    ...

class ChapterUpdate(SQLModel):
    number: int | None = None
    source_text: str | None = None
    translated_text: str | None = None


# ================================
# GLOSSARY
# ================================
class GlossaryEntryBase(SQLModel):
    source_term: str = Field(index=True)
    translation: str

class GlossaryEntry(GlossaryEntryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    novel_id: int = Field(foreign_key="novel.id", index=True)
    created_on: datetime = Field(default_factory=datetime.now)
    __table_args__ = (UniqueConstraint("novel_id", "source_term"),)

class GlossaryEntryPublic(GlossaryEntryBase):
    id: int
    novel_id: int
    created_on: datetime

class GlossaryEntryCreate(GlossaryEntryBase):
    ...

class GlossaryEntryUpdate(SQLModel):
    source_term: str | None = None
    translation: str | None = None


# ================================
# LLM STRUCTURED OUTPUT
# ================================
class GlossaryUpdate(BaseModel):
    source_term: str
    preferred_translation: str

class GlossaryExtraction(BaseModel):
    """Structured output of the term-extraction agent."""
    terms: list[GlossaryUpdate] = PydField(default_factory=list)

class TranslatedChapter(BaseModel):
    """Structured output of the translation agent."""
    translated_text: str