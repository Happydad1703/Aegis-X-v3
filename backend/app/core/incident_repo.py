from __future__ import annotations

from sqlalchemy import text

def create_incident(db, severity: str, category: str, message: str,
                    related_snapshot_key: str | None = None) -> None:
    q = text("""
        INSERT INTO incident_log (severity, category, message, related_snapshot_key)
        VALUES (:s, :c, :m, :k)
    """)
    db.execute(q, {"s": severity, "c": category, "m": message, "k": related_snapshot_key})
    db.commit()
