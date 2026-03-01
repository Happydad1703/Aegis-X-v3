# backend/app/core/snapshot_repo.py
from __future__ import annotations

import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


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
            "snapshot_data": json.dumps(snapshot_data, ensure_ascii=False),
            "freshness_status": freshness_status,
            "source_name": source_name,
            "refresh_rate_sec": refresh_rate_sec,
        },
    )
    db.commit()


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
