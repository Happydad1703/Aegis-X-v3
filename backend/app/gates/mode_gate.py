# gates/mode_gate.py — SE-50: Mode Gate. BACKTEST → 주문 금지.

from __future__ import annotations


def run_mode_gate(db) -> tuple[bool, str]:
    """
    DB에서 현재 system_mode 조회. BACKTEST면 실행 차단.
    Returns: (allow, message).
    """
    try:
        from sqlalchemy import text
        row = db.execute(
            text("SELECT mode FROM system_mode ORDER BY changed_at DESC LIMIT 1")
        ).mappings().first()
        mode = (row.get("mode") or "PAPER").upper() if row else "PAPER"
    except Exception:
        mode = "PAPER"
    if mode == "BACKTEST":
        return False, "BACKTEST mode — orders disabled"
    return True, f"mode={mode}"
