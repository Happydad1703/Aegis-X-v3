# api/cic.py — SE-45, SE-65: snapshot_key 기반 Read-only API (DB-Only Read)
# 원칙 1: engine_snapshot / order_log / incident_log 조회만, 직접 계산 금지

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_db
from backend.app.core.snapshot_keys import ALLOWED_SNAPSHOT_KEYS
from backend.app.core.snapshot_repo import get_latest_snapshot

router = APIRouter(prefix="/api", tags=["cic"])


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


@router.get("/orders")
async def get_orders(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """GET /api/orders — Read-only order_log (UI reads ONLY from DB)."""
    try:
        result = await db.execute(
            text("""
                SELECT id, symbol, side, quantity, mode, execution_status, execution_payload, created_at
                FROM order_log
                ORDER BY id DESC
                LIMIT :limit
            """),
            {"limit": limit},
        )
        rows = result.mappings().all()
    except Exception:
        return {"items": [], "meta": {"source": "order_log"}}
    items = []
    for r in rows:
        items.append({
            "id": r["id"],
            "symbol": r["symbol"],
            "side": r["side"],
            "quantity": float(r["quantity"]) if r["quantity"] is not None else 0,
            "mode": r["mode"],
            "execution_status": r["execution_status"],
            "execution_payload": r["execution_payload"],
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
        })
    return {"items": items, "meta": {"source": "order_log"}}


@router.get("/incidents")
async def get_incidents(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """GET /api/incidents — Read-only incident_log (UI reads ONLY from DB)."""
    try:
        result = await db.execute(
            text("""
                SELECT id, severity, category, message, related_snapshot_key, created_at
                FROM incident_log
                ORDER BY id DESC
                LIMIT :limit
            """),
            {"limit": limit},
        )
        rows = result.mappings().all()
    except Exception:
        return {"items": [], "meta": {"source": "incident_log"}}
    items = []
    for r in rows:
        items.append({
            "id": r["id"],
            "severity": r["severity"],
            "category": r["category"],
            "message": r["message"],
            "related_snapshot_key": r["related_snapshot_key"],
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
        })
    return {"items": items, "meta": {"source": "incident_log"}}


@router.get("/news/sources")
async def get_news_sources(
    limit: int = Query(40, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """GET /api/news/sources — ext_event_raw 기반 뉴스/공시/자료 통합 조회 (Read-only)."""
    try:
        result = await db.execute(
            text("""
                SELECT id, source_name, event_type, payload, received_at
                FROM ext_event_raw
                WHERE event_type IN ('news', 'disclosure', 'macro', 'quote')
                ORDER BY id DESC
                LIMIT :limit
            """),
            {"limit": limit},
        )
        rows = result.mappings().all()
    except Exception:
        return {"items": [], "meta": {"source": "ext_event_raw"}}

    def _extract_title(payload: dict | None) -> str:
        if not isinstance(payload, dict):
            return ""
        items = payload.get("items")
        if isinstance(items, list) and items:
            first = items[0]
            if isinstance(first, dict):
                if first.get("title"):
                    return str(first.get("title"))
                if first.get("corp_name"):
                    return str(first.get("corp_name"))
        if payload.get("series"):
            return f"series={payload.get('series')}"
        if payload.get("symbol"):
            return f"symbol={payload.get('symbol')}"
        return ""

    def _extract_link(payload: dict | None) -> str | None:
        if not isinstance(payload, dict):
            return None
        items = payload.get("items")
        if isinstance(items, list) and items:
            first = items[0]
            if isinstance(first, dict):
                link = first.get("link")
                return str(link) if link else None
        return None

    items = []
    for r in rows:
        payload = r["payload"] if isinstance(r["payload"], dict) else {}
        items.append({
            "id": r["id"],
            "source_name": r["source_name"] or "unknown",
            "event_type": r["event_type"] or "unknown",
            "title": _extract_title(payload),
            "link": _extract_link(payload),
            "received_at": r["received_at"].isoformat() if r["received_at"] else None,
            "payload": payload,
        })

    return {"items": items, "meta": {"source": "ext_event_raw"}}
