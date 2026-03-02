# execution/kis_executor.py — ONLY place that talks to KIS. FULL COMBAT LOCK.
# Retry/backoff; behind Mode gate (PILOT or FULL_LIVE only). Paper/BACKTEST never call KIS.

from __future__ import annotations

import time
from sqlalchemy.orm import Session

from backend.app.core.order_repo import insert_order_sync, update_order_status_sync
from backend.app.core.order_state import (
    ORDER_STATUS_PENDING,
    ORDER_STATUS_FILLED,
    ORDER_STATUS_REJECTED,
    ORDER_STATUS_ERROR,
)
from backend.app.core.incident_repo import create_incident

# Retry config (no over-engineering)
KIS_RETRY_COUNT = 3
KIS_BACKOFF_BASE_SEC = 1.0


def _current_mode(db: Session) -> str:
    """Current operation mode from system_mode table."""
    from sqlalchemy import text
    row = db.execute(
        text("SELECT mode FROM system_mode ORDER BY changed_at DESC NULLS LAST LIMIT 1")
    ).mappings().first()
    return (row.get("mode") or "PAPER").upper() if row else "PAPER"


def _stub_kis_send(symbol: str, side: str, quantity: float) -> tuple[bool, str]:
    """
    Stub: real KIS API call would go here. Returns (success, status).
    KR scope only; no US market.
    """
    # Phase 0-1: no real KIS SDK call; simulate success for testing.
    if not symbol or quantity <= 0:
        return False, ORDER_STATUS_REJECTED
    return True, ORDER_STATUS_FILLED


def execute_kis_sync(
    db: Session,
    *,
    symbol: str,
    side: str,
    quantity: float,
    mode: str,
) -> int | None:
    """
    Send order to KIS (stub) with retry/backoff. Only when mode is PILOT or FULL_LIVE.
    Returns order_log id if PENDING inserted; None if blocked or failed.
    Writes only via order_repo; logs failures to incident_repo.
    """
    if mode.upper() not in ("PILOT", "FULL_LIVE", "LIVE"):
        create_incident(db, "WARNING", "KIS_EXEC", f"kis_executor skipped: mode={mode} (not PILOT/LIVE)", "operation_mode")
        return None

    # Insert PENDING first (state transition: then ACK/FILLED/REJECTED)
    insert_order_sync(
        db,
        symbol=symbol,
        side=side,
        quantity=quantity,
        mode=mode,
        execution_status=ORDER_STATUS_PENDING,
        execution_payload={"sent_to_kis": False},
    )
    # Get last inserted id (order_log id)
    from sqlalchemy import text
    row = db.execute(text("SELECT id FROM order_log ORDER BY id DESC LIMIT 1")).mappings().first()
    order_id = int(row["id"]) if row else None
    if not order_id:
        return None

    last_error = None
    for attempt in range(KIS_RETRY_COUNT):
        try:
            ok, status = _stub_kis_send(symbol, side, quantity)
            if ok:
                update_order_status_sync(db, order_id, status, execution_payload={"simulated": True, "attempt": attempt + 1})
                return order_id
            update_order_status_sync(db, order_id, ORDER_STATUS_REJECTED, execution_payload={"reason": "stub_reject", "attempt": attempt + 1})
            return order_id
        except Exception as e:
            last_error = e
            if attempt < KIS_RETRY_COUNT - 1:
                time.sleep(KIS_BACKOFF_BASE_SEC * (2 ** attempt))
            else:
                update_order_status_sync(db, order_id, ORDER_STATUS_ERROR, execution_payload={"error": str(e)})
                create_incident(db, "ERROR", "KIS_EXEC", f"KIS send failed after {KIS_RETRY_COUNT} retries: {e}", "order_log")
                return order_id
    return order_id


def execute_kis_from_intent_sync(db: Session, intent: dict) -> int | None:
    """Execute KIS order from OrderIntent-like dict. Mode from DB; gate must be PASS upstream."""
    mode = _current_mode(db)
    if mode.upper() not in ("PILOT", "FULL_LIVE", "LIVE"):
        return None
    symbol = str(intent.get("symbol", ""))
    side = str(intent.get("side", "BUY")).upper()
    quantity = float(intent.get("quantity", 0))
    if not symbol or quantity <= 0:
        return None
    return execute_kis_sync(db, symbol=symbol, side=side, quantity=quantity, mode=mode)
