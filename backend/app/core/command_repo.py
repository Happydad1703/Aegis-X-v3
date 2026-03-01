from __future__ import annotations

import json
from sqlalchemy import text

def log_command(db, command_type: str, issued_by: str, payload: dict, status: str) -> None:
    q = text("""
        INSERT INTO command_log (command_type, issued_by, command_payload, status)
        VALUES (:t, :u, :p::jsonb, :s)
    """)
    db.execute(q, {
        "t": command_type,
        "u": issued_by,
        "p": json.dumps(payload, ensure_ascii=False),
        "s": status
    })
    db.commit()
