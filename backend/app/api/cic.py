# api/cic.py — SE-45, SE-65: snapshot_key 기반 Read-only API (DB-Only Read)
# 원칙 1: engine_snapshot 테이블만 조회, 직접 계산 금지

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_db
from backend.app.core.snapshot_keys import ALLOWED_SNAPSHOT_KEYS
from backend.app.core.snapshot_repo import get_latest_snapshot

router = APIRouter(prefix="/api", tags=["cic"])


@router.get("/snapshot/{snapshot_key}")
async def get_snapshot_by_key(
    snapshot_key: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """GET /api/snapshot/{snapshot_key} — 단일 스냅샷 조회 (Read-only, engine_snapshot만)."""
    if snapshot_key not in ALLOWED_SNAPSHOT_KEYS:
        raise HTTPException(status_code=404, detail=f"Unknown snapshot_key: {snapshot_key}")
    row = await get_latest_snapshot(db, snapshot_key)
    if not row:
        raise HTTPException(status_code=404, detail=f"No data for snapshot_key: {snapshot_key}")
    return {
        "snapshot_key": row["snapshot_key"],
        "data": row["snapshot_data"],
        "source_name": row["source_name"],
        "generated_at": row["generated_at"],
        "refresh_rate_sec": row["refresh_rate_sec"],
        "freshness_status": row["freshness_status"],
    }


@router.get("/snapshot/latest")
async def get_snapshot_latest(
    key: str = Query(..., description="snapshot_key (e.g. regime_current)"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """GET /api/snapshot/latest?key=regime_current — 최신 스냅샷 조회 (Read-only)."""
    if key not in ALLOWED_SNAPSHOT_KEYS:
        raise HTTPException(status_code=404, detail=f"Unknown snapshot_key: {key}")
    row = await get_latest_snapshot(db, key)
    if not row:
        raise HTTPException(status_code=404, detail=f"No data for snapshot_key: {key}")
    return {
        "snapshot_key": row["snapshot_key"],
        "data": row["snapshot_data"],
        "source_name": row["source_name"],
        "generated_at": row["generated_at"],
        "refresh_rate_sec": row["refresh_rate_sec"],
        "freshness_status": row["freshness_status"],
    }
