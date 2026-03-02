# backend/tests/test_engine_loop.py — SE-64: 1사이클 후 DB에 필수 스냅샷 키 존재 확인
# Verification_Playbook: pytest backend/tests/test_engine_loop.py
# 사전 조건: .env에 DATABASE_URL 또는 ASYNC_DATABASE_URL, Postgres 기동 및 migrate 적용

from __future__ import annotations

import pytest
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.snapshot_keys import get_required_snapshot_keys_for_cycle


@pytest.mark.asyncio
async def test_one_cycle_produces_required_snapshot_keys(db_session: AsyncSession) -> None:
    """한 사이클 실행 후 engine_snapshot에 필수 키(REQUIRED_SNAPSHOT_KEYS_MINIMUM)가 기록되는지 검증."""
    from backend.app.workers.engine_worker import run_single_cycle
    from sqlalchemy.exc import ProgrammingError

    required_keys = get_required_snapshot_keys_for_cycle()
    before = datetime.now(timezone.utc)
    try:
        await run_single_cycle(db_session)
    except ProgrammingError as e:
        if "does not exist" in str(e) or "UndefinedTable" in str(e):
            pytest.skip("engine_snapshot table not found (run migrate_db.ps1 or migrate_db_via_url.py)")
        raise
    after = datetime.now(timezone.utc)

    for key in required_keys:
        result = await db_session.execute(
            text("""
                SELECT snapshot_key, generated_at, refresh_rate_sec
                FROM engine_snapshot
                WHERE snapshot_key = :key
                ORDER BY generated_at DESC
                LIMIT 1
            """),
            {"key": key},
        )
        row = result.mappings().first()
        assert row is not None, f"Missing snapshot_key in DB after cycle: {key}"
        assert row["snapshot_key"] == key
        assert row["refresh_rate_sec"] is not None, f"Missing refresh_rate_sec for {key} (metadata required)"
        # generated_at이 사이클 실행 전후 구간 또는 최근 5분 이내 (타임존/지연 허용)
        gen_at = row["generated_at"]
        if gen_at.tzinfo is None:
            from datetime import timezone as tz
            gen_at = gen_at.replace(tzinfo=tz.utc)
        assert before.timestamp() - 300 <= gen_at.timestamp() <= after.timestamp() + 10, (
            f"snapshot_key {key} generated_at not in cycle window (before-5m..after+10s)"
        )
