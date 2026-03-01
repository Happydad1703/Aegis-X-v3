from __future__ import annotations

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
