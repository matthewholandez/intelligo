"""Load environment from the repo-root .env.local before anything reads it.

Runs on first import of the ``app`` package — i.e. before ``ChatOpenRouter`` is
constructed and reads ``OPENROUTER_API_KEY``. Real environment variables already
set in the shell take precedence (``load_dotenv`` does not override them).
"""

from pathlib import Path

from dotenv import load_dotenv

# backend/app/__init__.py -> parents[2] is the repo root.
_ENV_LOCAL = Path(__file__).resolve().parents[2] / ".env.local"
load_dotenv(_ENV_LOCAL)
