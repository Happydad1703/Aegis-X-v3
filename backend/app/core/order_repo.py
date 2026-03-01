# core/order_repo.py — Single write path for order_log (SE-51). Execution layer uses this only.

from __future__ import annotations

import json
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


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
            "payload": json.dumps(execution_payload or {}, ensure_ascii=False),
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
