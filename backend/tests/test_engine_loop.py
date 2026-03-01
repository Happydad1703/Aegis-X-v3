# backend/tests/test_engine_loop.py — SE-64 데이터 무결성: 1사이클 후 DB에 6종 스냅샷 키 존재 확인
# 지속적 재검증(Continuous Validation): pytest backend/tests/test_engine_loop.py
# 사전 조건: .env에 DATABASE_URL 또는 ASYNC_DATABASE_URL, Postgres 기동 및 migrate 적용

from __future__ import annotations

import pytest
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.snapshot_keys import get_required_snapshot_keys_for_cycle


@pytest.mark.asyncio
async def test_one_cycle_produces_six_snapshot_keys(db_session: AsyncSession) -> None:
    """한 사이클 실행 후 engine_snapshot에 6종 키가 정확히 기록되는지 검증 (SE-64, SSOT: snapshot_keys)."""
    from backend.app.workers.engine_worker import run_single_cycle

    required_keys = get_required_snapshot_keys_for_cycle()
    before = datetime.now(timezone.utc)
    await run_single_cycle(db_session)
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
        # generated_at이 방금 실행 구간 내에 있는지 (최대 5초 여유)
        gen_at = row["generated_at"]
        if gen_at.tzinfo is None:
            from datetime import timezone as tz
            gen_at = gen_at.replace(tzinfo=tz.utc)
        assert before.timestamp() - 2 <= gen_at.timestamp() <= after.timestamp() + 2, (
            f"snapshot_key {key} generated_at not in cycle window"
        )
