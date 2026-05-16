"""
Home for Intelligo's main API logic.
"""

from fastapi import FastAPI, Depends, HTTPException, Query, Body
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel

from contextlib import asynccontextmanager

from typing import Annotated, Sequence
from datetime import date, datetime


# ================================
# DATA MODELS
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

class NovelRequest(BaseModel):
    name: str

# ================================
# CONSTANTS
# ================================
SQLITE_FILE_NAME = "novels.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"
SQLITE_CONNECT_ARGS = {"check_same_thread": False}

engine = create_engine(SQLITE_URL, connect_args=SQLITE_CONNECT_ARGS)


# ================================
# SQLMODEL
# ================================
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# ================================
# FASTAPI
# ================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    create_db_and_tables()
    yield
    # On close

app = FastAPI(lifespan=lifespan)

@app.get("/novels/{novel_id}", response_model=NovelPublic)
def get_novel_by_id(novel_id: int, session: SessionDep):
    """Get a novel by its ID."""
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    return novel

@app.get("/novels", response_model=list[NovelPublic])
def get_novels(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
    ):
    """Get all novels."""
    novels = session.exec(select(Novel).offset(offset).limit(limit)).all()
    return novels

@app.post("/novels", response_model=NovelPublic)
def create_novel(novel: NovelCreate, session: SessionDep):
    """Create a new novel."""
    db_novel = Novel.model_validate(novel)
    session.add(db_novel)
    session.commit()
    session.refresh(db_novel)
    return db_novel

@app.patch("/novels/{novel_id}", response_model=NovelPublic)
def update_novel(novel_id: int, novel: NovelUpdate, session: SessionDep):
    novel_db = session.get(Novel, novel_id)
    if not novel_db:
        raise HTTPException(status_code=404, detail="Novel not found")
    novel_data = novel.model_dump(exclude_unset=True)
    novel_db.sqlmodel_update(novel_data)
    session.add(novel_db)
    session.commit()
    session.refresh(novel_db)
    return novel_db

@app.delete("/novels/{novel_id}")
def delete_novel(novel_id: int, session: SessionDep):
    """Delete a novel."""
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    session.delete(novel)
    session.commit()
    return { "ok": True }