# execution/paper_executor.py — SE-51: Paper mode order → order_log via order_repo only. No strategy logic.

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.core.order_repo import insert_order_sync
from backend.app.core.notifications import push_event


def execute_paper_sync(
    db: Session,
    *,
    symbol: str,
    side: str,
    quantity: float,
    mode: str = "PAPER",
) -> None:
    """Record paper order in order_log. Gate check is done upstream (pre_trade_gate). Push on fill."""
    insert_order_sync(
        db,
        symbol=symbol,
        side=side,
        quantity=quantity,
        mode=mode,
        execution_status="PAPER_FILLED",
        execution_payload={"simulated": True},
    )
    push_event("trade_filled", f"{mode} {side} {symbol} qty={quantity}")
