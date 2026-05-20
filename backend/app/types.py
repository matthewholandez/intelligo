from sqlmodel import SQLModel, Field
from datetime import datetime


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