# api/control.py — SE-32, 49, 55: Mode / Freeze / Retract / Emergency Stop. command_log 기록 + Push 알림.

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.core.db import get_db_sync
from backend.app.core.command_repo import log_command
from backend.app.core.notifications import push_event

router = APIRouter(prefix="/api/control", tags=["control"])


class ModeBody(BaseModel):
    mode: str  # BACKTEST | PAPER | PILOT | FULL_LIVE


class ActionBody(BaseModel):
    reason: str | None = None


@router.post("/mode")
def set_mode(body: ModeBody, db=Depends(get_db_sync)):
    """Set operation mode. Logged to command_log."""
    mode = body.mode.upper()
    if mode not in ("BACKTEST", "PAPER", "PILOT", "FULL_LIVE"):
        mode = "PAPER"
    log_command(db, "SET_MODE", "warroom", {"mode": mode}, "ACCEPTED")
    return {"status": "ok", "mode": mode}


@router.post("/freeze")
def freeze(body: ActionBody = None, db=Depends(get_db_sync)):
    """Freeze: 신규 진입 차단. command_log 기록 + Telegram/Kakao Push."""
    reason = (body.reason if body else None) or ""
    log_command(db, "FREEZE", "warroom", {"reason": reason}, "ACCEPTED")
    push_event("freeze", reason or "신규 진입 차단")
    return {"status": "ok", "action": "freeze"}


@router.post("/retract")
def retract(body: ActionBody = None, db=Depends(get_db_sync)):
    """Retract: 리스크 축소/청산 권고. command_log 기록 + Push."""
    reason = (body.reason if body else None) or ""
    log_command(db, "RETRACT", "warroom", {"reason": reason}, "ACCEPTED")
    push_event("retract", reason or "리스크 축소 권고")
    return {"status": "ok", "action": "retract"}


@router.post("/emergency_stop")
def emergency_stop(body: ActionBody = None, db=Depends(get_db_sync)):
    """Emergency Stop: 최우선 정지. command_log 기록 + Push."""
    reason = (body.reason if body else None) or ""
    log_command(db, "EMERGENCY_STOP", "warroom", {"reason": reason}, "ACCEPTED")
    push_event("emergency_stop", reason or "비상 정지")
    return {"status": "ok", "action": "emergency_stop"}
