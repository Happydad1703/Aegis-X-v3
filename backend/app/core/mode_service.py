from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import text

VALID_MODES = ["BACKTEST", "PAPER", "PILOT", "FULL_LIVE"]


def get_current_mode(db) -> str:
    q = text("""
        SELECT mode
        FROM system_mode
        ORDER BY changed_at DESC
        LIMIT 1
    """)
    row = db.execute(q).fetchone()
    return row[0] if row else "PAPER"


def set_mode(db, mode: str, changed_by: str = "warroom") -> None:
    """Append a new system_mode row (history preserved)."""
    mode = (mode or "PAPER").upper()
    if mode not in VALID_MODES:
        mode = "PAPER"
    db.execute(
        text("""
            INSERT INTO system_mode (mode, changed_by, changed_at)
            VALUES (:mode, :changed_by, (NOW() AT TIME ZONE 'UTC'))
        """),
        {"mode": mode, "changed_by": changed_by},
    )
    db.commit()
