from __future__ import annotations

import json
from sqlalchemy import text

def get_config(db, key: str) -> dict | None:
    q = text("""
        SELECT config_value
        FROM system_config
        WHERE config_key = :k
        ORDER BY updated_at DESC
        LIMIT 1
    """)
    row = db.execute(q, {"k": key}).fetchone()
    return row[0] if row else None

def set_config(db, key: str, value: dict, updated_by: str) -> None:
    q = text("""
        INSERT INTO system_config (config_key, config_value, updated_by)
        VALUES (:k, CAST(:v AS jsonb), :u)
    """)
    db.execute(q, {"k": key, "v": json.dumps(value, ensure_ascii=False), "u": updated_by})
    db.commit()
