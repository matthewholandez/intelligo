"""
Home for Intelligo's main API logic.
"""

from fastapi import FastAPI

from .db import lifespan
from .routers import chapters, glossary, novels

app = FastAPI(lifespan=lifespan)
app.include_router(novels.router)
app.include_router(chapters.router)
app.include_router(glossary.router)