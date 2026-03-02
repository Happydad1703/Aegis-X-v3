from __future__ import annotations

import json
from sqlalchemy import text


def create_incident(db, severity: str, category: str, message: str,
                    related_snapshot_key: str | None = None) -> None:
    """Insert incident (core/incident_repo only)."""
    q = text("""
        INSERT INTO incident_log (severity, category, message, related_snapshot_key)
        VALUES (:s, :c, :m, :k)
    """)
    db.execute(q, {"s": severity, "c": category, "m": message, "k": related_snapshot_key})
    db.commit()


def insert_incident(db, severity: str, category: str, message: str,
                    related_snapshot_key: str | None = None, meta: dict | None = None) -> None:
    """Phase 1 API: insert incident; optional meta appended to message or logged."""
    msg = message
    if meta:
        msg = message + " | meta=" + json.dumps(meta, ensure_ascii=False)
    create_incident(db, severity, category, msg, related_snapshot_key)
