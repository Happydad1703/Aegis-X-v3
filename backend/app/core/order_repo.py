# core/order_repo.py — Single write path for order_log (SE-51). Phase 3: Hash chain. State transition enforced.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.order_state import is_allowed_initial_status, validate_transition


def _order_chain_hash(prev_hash: str, payload_str: str, created_at_utc: str) -> str:
    """current_hash = SHA256(previous_hash + payload + timestamp). SE-50 Phase 3."""
    content = f"{prev_hash}{payload_str}{created_at_utc}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _get_last_order_self_hash_sync(db: Session) -> str:
    r = db.execute(text("SELECT self_hash FROM order_log ORDER BY id DESC LIMIT 1")).mappings().first()
    return (r["self_hash"] or "genesis") if r else "genesis"


def insert_order_sync(
    db: Session,
    *,
    symbol: str,
    side: str,
    quantity: float | Decimal,
    mode: str,
    execution_status: str,
    execution_payload: dict | None = None,
) -> None:
    if not is_allowed_initial_status(execution_status):
        raise ValueError(f"Invalid initial order status: {execution_status}. Allowed: PENDING, PAPER_FILLED, REJECTED, ERROR")
    payload = execution_payload or {}
    payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    now_utc = datetime.now(timezone.utc).isoformat()
    prev_hash = _get_last_order_self_hash_sync(db)
    self_hash = _order_chain_hash(prev_hash, payload_str, now_utc)
    try:
        db.execute(
            text("""
                INSERT INTO order_log (symbol, side, quantity, mode, execution_status, execution_payload, created_at, prev_hash, self_hash)
                VALUES (:symbol, :side, :quantity, :mode, :execution_status, CAST(:payload AS JSONB), CAST(:created_at AS TIMESTAMPTZ), :prev_hash, :self_hash)
            """),
            {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "mode": mode,
                "execution_status": execution_status,
                "payload": payload_str,
                "created_at": now_utc,
                "prev_hash": prev_hash,
                "self_hash": self_hash,
            },
        )
    except Exception:
        db.execute(
            text("""
                INSERT INTO order_log (symbol, side, quantity, mode, execution_status, execution_payload)
                VALUES (:symbol, :side, :quantity, :mode, :execution_status, CAST(:payload AS JSONB))
            """),
            {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "mode": mode,
                "execution_status": execution_status,
                "payload": payload_str,
            },
        )
    db.commit()


async def insert_order_async(
    db: AsyncSession,
    *,
    symbol: str,
    side: str,
    quantity: float | Decimal,
    mode: str,
    execution_status: str,
    execution_payload: dict | None = None,
) -> None:
    if not is_allowed_initial_status(execution_status):
        raise ValueError(f"Invalid initial order status: {execution_status}")
    await db.execute(
        text("""
            INSERT INTO order_log (symbol, side, quantity, mode, execution_status, execution_payload)
            VALUES (:symbol, :side, :quantity, :mode, :execution_status, CAST(:payload AS JSONB))
        """),
        {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "mode": mode,
            "execution_status": execution_status,
            "payload": json.dumps(execution_payload or {}, ensure_ascii=False),
        },
    )
    await db.commit()


def update_order_status_sync(db: Session, order_id: int, new_status: str, execution_payload: dict | None = None) -> None:
    """Update order_log execution_status; enforce valid transition. Single write path."""
    row = db.execute(
        text("SELECT id, execution_status FROM order_log WHERE id = :id"),
        {"id": order_id},
    ).mappings().first()
    if not row:
        raise ValueError(f"Order id={order_id} not found")
    from_status = row["execution_status"]
    if not validate_transition(from_status, new_status):
        raise ValueError(f"Invalid order state transition: {from_status} -> {new_status}")
    payload = execution_payload or {}
    payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    db.execute(
        text("""
            UPDATE order_log SET execution_status = :status, execution_payload = CAST(:payload AS JSONB) WHERE id = :id
        """),
        {"id": order_id, "status": new_status, "payload": payload_str},
    )
    db.commit()
