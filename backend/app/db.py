from fastapi import FastAPI, Depends
from sqlmodel import Session, SQLModel, create_engine
from typing import Annotated
from contextlib import asynccontextmanager

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