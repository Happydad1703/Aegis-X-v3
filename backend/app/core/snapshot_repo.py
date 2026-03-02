# backend/app/core/snapshot_repo.py — SE-50 Phase 3: Hash chain on engine_snapshot (worker level only).
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


def _snapshot_chain_hash(prev_hash: str, snapshot_data_json: str, timestamp_utc: str) -> str:
    """current_hash = SHA256(previous_hash + snapshot_data_json + timestamp). SE-50 Phase 3."""
    content = f"{prev_hash}{snapshot_data_json}{timestamp_utc}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _get_last_self_hash_sync(db: Session) -> str:
    r = db.execute(text("SELECT self_hash FROM engine_snapshot ORDER BY id DESC LIMIT 1")).mappings().first()
    return (r["self_hash"] or "genesis") if r else "genesis"


async def insert_snapshot(db: AsyncSession, *, snapshot_key: str, snapshot_data: dict,
                         freshness_status: str, source_name: str, refresh_rate_sec: int) -> None:
    await db.execute(
        text(
            """
            INSERT INTO engine_snapshot
              (snapshot_key, snapshot_data, freshness_status, source_name, refresh_rate_sec)
            VALUES
              (:snapshot_key, CAST(:snapshot_data AS JSONB), :freshness_status, :source_name, :refresh_rate_sec)
            """
        ),
        {
            "snapshot_key": snapshot_key,
            "snapshot_data": json.dumps(snapshot_data, ensure_ascii=False),
            "freshness_status": freshness_status,
            "source_name": source_name,
            "refresh_rate_sec": refresh_rate_sec,
        },
    )
    await db.commit()


def insert_snapshot_sync(db: Session, *, snapshot_key: str, snapshot_data: dict,
                         freshness_status: str, source_name: str, refresh_rate_sec: int) -> None:
    payload_str = json.dumps(snapshot_data, sort_keys=True, ensure_ascii=False, default=str)
    prev_hash = _get_last_self_hash_sync(db)
    now_utc = datetime.now(timezone.utc).isoformat()
    self_hash = _snapshot_chain_hash(prev_hash, payload_str, now_utc)
    try:
        db.execute(
            text(
                """
                INSERT INTO engine_snapshot
                  (snapshot_key, snapshot_data, freshness_status, source_name, refresh_rate_sec, generated_at, prev_hash, self_hash)
                VALUES
                  (:snapshot_key, CAST(:snapshot_data AS JSONB), :freshness_status, :source_name, :refresh_rate_sec,
                   CAST(:generated_at AS TIMESTAMPTZ), :prev_hash, :self_hash)
                """
            ),
            {
                "snapshot_key": snapshot_key,
                "snapshot_data": payload_str,
                "freshness_status": freshness_status,
                "source_name": source_name,
                "refresh_rate_sec": refresh_rate_sec,
                "generated_at": now_utc,
                "prev_hash": prev_hash,
                "self_hash": self_hash,
            },
        )
    except Exception:
        db.execute(
            text(
                """
                INSERT INTO engine_snapshot
                  (snapshot_key, snapshot_data, freshness_status, source_name, refresh_rate_sec)
                VALUES
                  (:snapshot_key, CAST(:snapshot_data AS JSONB), :freshness_status, :source_name, :refresh_rate_sec)
                """
            ),
            {
                "snapshot_key": snapshot_key,
                "snapshot_data": payload_str,
                "freshness_status": freshness_status,
                "source_name": source_name,
                "refresh_rate_sec": refresh_rate_sec,
            },
        )
    db.commit()


def get_latest_snapshot_sync(db: Session, snapshot_key: str) -> dict | None:
    """Sync: snapshot_key 최신 1건 조회 (Gate/Execution에서 사용)."""
    result = db.execute(
        text("""
            SELECT snapshot_key, snapshot_data, freshness_status, source_name, refresh_rate_sec, generated_at
            FROM engine_snapshot
            WHERE snapshot_key = :snapshot_key
            ORDER BY generated_at DESC
            LIMIT 1
        """),
        {"snapshot_key": snapshot_key},
    )
    row = result.mappings().first()
    if not row:
        return None
    return {
        "snapshot_key": row["snapshot_key"],
        "snapshot_data": row["snapshot_data"],
        "freshness_status": row["freshness_status"],
        "source_name": row["source_name"],
        "refresh_rate_sec": row["refresh_rate_sec"],
        "generated_at": row["generated_at"].isoformat() if row["generated_at"] else None,
    }


async def get_latest_snapshot(db: AsyncSession, snapshot_key: str):
    """API용: snapshot_key 최신 1건 조회 (DB-Only Read)."""
    result = await db.execute(
        text("""
            SELECT snapshot_key, snapshot_data, freshness_status, source_name, refresh_rate_sec, generated_at
            FROM engine_snapshot
            WHERE snapshot_key = :snapshot_key
            ORDER BY generated_at DESC
            LIMIT 1
        """),
        {"snapshot_key": snapshot_key},
    )
    row = result.mappings().first()
    if not row:
        return None
    return {
        "snapshot_key": row["snapshot_key"],
        "snapshot_data": row["snapshot_data"],
        "freshness_status": row["freshness_status"],
        "source_name": row["source_name"],
        "refresh_rate_sec": row["refresh_rate_sec"],
        "generated_at": row["generated_at"].isoformat() if row["generated_at"] else None,
    }
