from fastapi import FastAPI, Depends
from sqlalchemy import event
from sqlmodel import Session, SQLModel, col, create_engine, select
from typing import Annotated
from contextlib import asynccontextmanager

# ================================
# CONSTANTS
# ================================
SQLITE_FILE_NAME = "novels.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"
SQLITE_CONNECT_ARGS = {"check_same_thread": False}

engine = create_engine(SQLITE_URL, connect_args=SQLITE_CONNECT_ARGS)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """WAL keeps reads non-blocking while the background pipeline writes."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


# ================================
# SQLMODEL
# ================================
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def reconcile_interrupted_translations():
    """A restart can orphan a chapter mid-pipeline; mark such chapters failed
    so the UI can offer a re-translate rather than spinning forever."""
    # Imported here to avoid a circular import at module load.
    from app.types import Chapter, ChapterStatus

    in_progress = (
        ChapterStatus.pending,
        ChapterStatus.analyzing,
        ChapterStatus.translating,
    )
    with Session(engine) as session:
        stuck = session.exec(
            select(Chapter).where(col(Chapter.status).in_(in_progress))
        ).all()
        for chapter in stuck:
            chapter.status = ChapterStatus.failed
            chapter.error = "Interrupted by server restart"
            session.add(chapter)
        if stuck:
            session.commit()


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
    reconcile_interrupted_translations()
    yield
    # On close
