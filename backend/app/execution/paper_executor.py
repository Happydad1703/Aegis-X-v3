# execution/paper_executor.py — SE-51: Paper mode order → order_log via order_repo only. FULL COMBAT LOCK.
# Gate check is done upstream; this module only writes. No KIS; no strategy logic.

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.core.order_repo import insert_order_sync
from backend.app.core.order_state import ORDER_STATUS_PAPER_FILLED

try:
    from backend.app.core.notifications import push_event
except Exception:
    def push_event(_: str, __: str) -> bool:
        return False


def execute_paper_sync(
    db: Session,
    *,
    symbol: str,
    side: str,
    quantity: float,
    mode: str = "PAPER",
) -> None:
    """Record paper order in order_log. Gate check done upstream. Single write path: order_repo only."""
    insert_order_sync(
        db,
        symbol=symbol,
        side=side,
        quantity=quantity,
        mode=mode,
        execution_status=ORDER_STATUS_PAPER_FILLED,
        execution_payload={"simulated": True},
    )
    push_event("trade_filled", f"{mode} {side} {symbol} qty={quantity}")


def execute_paper_from_intent_sync(db: Session, intent: dict, mode: str = "PAPER") -> None:
    """
    Execute paper order from OrderIntent-like dict.
    Keys: symbol, side, quantity (optional: strategy, rationale). Gate must be PASS upstream.
    """
    symbol = str(intent.get("symbol", ""))
    side = str(intent.get("side", "BUY")).upper()
    quantity = float(intent.get("quantity", 0))
    if not symbol or quantity <= 0:
        return
    execute_paper_sync(db, symbol=symbol, side=side, quantity=quantity, mode=mode)
