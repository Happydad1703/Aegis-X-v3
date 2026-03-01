# backend/tests/conftest.py — pytest fixtures (SE-14 TVP, Continuous Validation)
# asyncio_mode = auto in pytest.ini
# DB 테스트: Postgres 기동 + migrate + asyncpg 설치 필요

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

import pytest


def _async_session_available() -> bool:
    from backend.app.core.db import AsyncSessionLocal
    return AsyncSessionLocal is not None


@pytest.fixture
async def db_session() -> AsyncSession:
    from backend.app.core.db import AsyncSessionLocal
    if AsyncSessionLocal is None:
        pytest.skip("AsyncSessionLocal not available (install asyncpg and set DATABASE_URL)")
    async with AsyncSessionLocal() as session:
        yield session
