"""
Home for Intelligo's main API logic.
"""

from fastapi import FastAPI

from .db import lifespan
from .routers import novels

app = FastAPI(lifespan=lifespan)
app.include_router(novels.router)