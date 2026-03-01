# core/event_repo.py — Single write path for ext_event_raw (SE-64, 04_DDD)
# Ingest worker MUST use this module only; no direct INSERT into ext_event_raw elsewhere.

from __future__ import annotations

import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


def insert_raw_event_sync(
    db: Session,
    *,
    source_name: str,
    event_type: str,
    payload: dict,
) -> None:
    """Insert one row into ext_event_raw. Ingest worker uses this only."""
    db.execute(
        text("""
            INSERT INTO ext_event_raw (source_name, event_type, payload)
            VALUES (:source_name, :event_type, CAST(:payload AS JSONB))
        """),
        {
            "source_name": source_name,
            "event_type": event_type,
            "payload": json.dumps(payload, ensure_ascii=False),
        },
    )
    db.commit()


async def insert_raw_event_async(
    db: AsyncSession,
    *,
    source_name: str,
    event_type: str,
    payload: dict,
) -> None:
    """Async insert one row into ext_event_raw."""
    await db.execute(
        text("""
            INSERT INTO ext_event_raw (source_name, event_type, payload)
            VALUES (:source_name, :event_type, CAST(:payload AS JSONB))
        """),
        {
            "source_name": source_name,
            "event_type": event_type,
            "payload": json.dumps(payload, ensure_ascii=False),
        },
    )
    await db.commit()
