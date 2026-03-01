# backend/app/core/db.py
from __future__ import annotations

import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", "").strip()

# -------------------------
# Sync DB (scripts/engine)
# -------------------------
if not DATABASE_URL and ASYNC_DATABASE_URL:
    # If only async url exists, derive sync url
    # postgresql+asyncpg://...  -> postgresql+psycopg2://...
    DATABASE_URL = ASYNC_DATABASE_URL.replace("+asyncpg", "+psycopg2")

if not DATABASE_URL:
    DATABASE_URL = ""

if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=3,
        pool_pre_ping=True,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None


def get_db_sync():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Async DB (API: Phase 0-2) — requires asyncpg
# -------------------------
async_engine = None
AsyncSessionLocal = None
if not ASYNC_DATABASE_URL and DATABASE_URL:
    ASYNC_DATABASE_URL = DATABASE_URL.replace("+psycopg2", "+asyncpg")

if ASYNC_DATABASE_URL:
    try:
        async_engine = create_async_engine(
            ASYNC_DATABASE_URL,
            pool_pre_ping=True,
        )
        AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)
    except ImportError:
        async_engine = None
        AsyncSessionLocal = None  # asyncpg not installed


async def get_db():
    if not AsyncSessionLocal:
        raise RuntimeError(
            "Async DB unavailable. Install: pip install asyncpg (and set DATABASE_URL or ASYNC_DATABASE_URL)"
        )
    async with AsyncSessionLocal() as session:
        yield session
