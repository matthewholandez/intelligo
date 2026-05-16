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