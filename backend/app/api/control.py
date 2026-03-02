# api/control.py — SE-32, 49, 55: Mode / Freeze / Retract / Emergency Stop. command_log 기록 + Push 알림.
# Warroom/Cockpit: POST /api/control/command single endpoint; GET /api/control/state for gate state.

from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.core.db import get_db_sync
from backend.app.core.command_repo import log_command
from backend.app.core.config_service import set_config, get_config
from backend.app.core.mode_service import set_mode as set_system_mode
from backend.app.core.notifications import push_event
from backend.app.core.audit_chain import append_audit_event

router = APIRouter(prefix="/api/control", tags=["control"])

# SE-50 Gate state keys (DB-only). EmergencyStop/Retract 시 게이트 체인에서 차단.
GATE_EMERGENCY_STOP_ACTIVE = "gate_emergency_stop_active"
GATE_RETRACT_ACTIVE = "gate_retract_active"

ALLOWED_COMMANDS = frozenset({"EMERGENCY_STOP", "RETRACT", "SET_MODE", "RUN_ENGINE_CYCLE"})


class CommandBody(BaseModel):
    """Single command endpoint — Warroom SE spec."""
    command_type: str  # EMERGENCY_STOP | RETRACT | SET_MODE | RUN_ENGINE_CYCLE
    payload: dict | None = None  # e.g. {"mode": "PAPER"} for SET_MODE


class ModeBody(BaseModel):
    mode: str  # BACKTEST | PAPER | PILOT | FULL_LIVE


class ActionBody(BaseModel):
    reason: str | None = None


@router.get("/state")
def get_control_state(db=Depends(get_db_sync)):
    """GET /api/control/state — EmergencyStop and Retract state from system_config (DB-only read)."""
    e = get_config(db, GATE_EMERGENCY_STOP_ACTIVE)
    r = get_config(db, GATE_RETRACT_ACTIVE)
    return {
        "emergency_stop": bool(e and e.get("active")) if isinstance(e, dict) else False,
        "retract": bool(r and r.get("active")) if isinstance(r, dict) else False,
    }


@router.post("/command")
def post_command(body: CommandBody, db=Depends(get_db_sync)):
    """POST /api/control/command — Only way to issue commands (EMERGENCY_STOP, RETRACT, SET_MODE, RUN_ENGINE_CYCLE)."""
    cmd = (body.command_type or "").strip().upper()
    if cmd not in ALLOWED_COMMANDS:
        return {"status": "rejected", "detail": f"Unknown command_type: {body.command_type}"}
    payload = body.payload or {}
    if cmd == "EMERGENCY_STOP":
        log_command(db, "EMERGENCY_STOP", "warroom", {"reason": payload.get("reason", "")}, "ACCEPTED")
        set_config(db, GATE_EMERGENCY_STOP_ACTIVE, {"active": True, "reason": payload.get("reason", "")}, "control")
        append_audit_event("emergency_stop", {"reason": payload.get("reason"), "source": "warroom", "ts_utc": datetime.now(timezone.utc).isoformat()}, payload_preview="Emergency Stop")
        push_event("emergency_stop", payload.get("reason") or "비상 정지")
        return {"status": "ok", "command_type": "EMERGENCY_STOP"}
    if cmd == "RETRACT":
        log_command(db, "RETRACT", "warroom", {"reason": payload.get("reason", "")}, "ACCEPTED")
        set_config(db, GATE_RETRACT_ACTIVE, {"active": True, "reason": payload.get("reason", "")}, "control")
        append_audit_event("retract", {"reason": payload.get("reason"), "source": "warroom", "ts_utc": datetime.now(timezone.utc).isoformat()}, payload_preview=payload.get("reason") or "Retract")
        push_event("retract", payload.get("reason") or "리스크 축소 권고")
        return {"status": "ok", "command_type": "RETRACT"}
    if cmd == "SET_MODE":
        mode = (payload.get("mode") or "PAPER").upper()
        if mode not in ("BACKTEST", "PAPER", "PILOT", "FULL_LIVE"):
            mode = "PAPER"
        log_command(db, "SET_MODE", "warroom", {"mode": mode}, "ACCEPTED")
        set_system_mode(db, mode, "warroom")
        append_audit_event("mode", {"mode": mode, "source": "warroom", "ts_utc": datetime.now(timezone.utc).isoformat()}, payload_preview=f"SET_MODE {mode}")
        return {"status": "ok", "command_type": "SET_MODE", "mode": mode}
    if cmd == "RUN_ENGINE_CYCLE":
        log_command(db, "RUN_ENGINE_CYCLE", "warroom", payload, "ACCEPTED")
        try:
            from backend.app.workers.engine_worker import run_single_cycle_sync
            run_single_cycle_sync(db)
        except Exception as e:
            log_command(db, "RUN_ENGINE_CYCLE", "warroom", {"error": str(e)}, "FAILED")
            return {"status": "error", "command_type": "RUN_ENGINE_CYCLE", "detail": str(e)}
        return {"status": "ok", "command_type": "RUN_ENGINE_CYCLE"}
    return {"status": "rejected", "detail": "Unknown command"}


@router.post("/mode")
def set_mode(body: ModeBody, db=Depends(get_db_sync)):
    """Set operation mode. Logged to command_log + Hash Chain."""
    mode = body.mode.upper()
    if mode not in ("BACKTEST", "PAPER", "PILOT", "FULL_LIVE"):
        mode = "PAPER"
    log_command(db, "SET_MODE", "warroom", {"mode": mode}, "ACCEPTED")
    append_audit_event("mode", {"mode": mode, "source": "warroom", "ts_utc": datetime.now(timezone.utc).isoformat()}, payload_preview=f"SET_MODE {mode}")
    return {"status": "ok", "mode": mode}


@router.post("/freeze")
def freeze(body: ActionBody = None, db=Depends(get_db_sync)):
    """Freeze: 신규 진입 차단. command_log + Hash Chain + Telegram/Kakao Push."""
    reason = (body.reason if body else None) or ""
    log_command(db, "FREEZE", "warroom", {"reason": reason}, "ACCEPTED")
    append_audit_event("freeze", {"reason": reason, "source": "warroom", "ts_utc": datetime.now(timezone.utc).isoformat()}, payload_preview=reason or "신규 진입 차단")
    push_event("freeze", reason or "신규 진입 차단")
    return {"status": "ok", "action": "freeze"}


@router.post("/retract")
def retract(body: ActionBody = None, db=Depends(get_db_sync)):
    """Retract: 리스크 축소/청산 권고. Gate 체인 2순위 차단. command_log + config + Hash Chain + Push."""
    reason = (body.reason if body else None) or ""
    log_command(db, "RETRACT", "warroom", {"reason": reason}, "ACCEPTED")
    set_config(db, GATE_RETRACT_ACTIVE, {"active": True, "reason": reason}, "control")
    append_audit_event("retract", {"reason": reason, "source": "warroom", "ts_utc": datetime.now(timezone.utc).isoformat()}, payload_preview=reason or "리스크 축소 권고")
    push_event("retract", reason or "리스크 축소 권고")
    return {"status": "ok", "action": "retract"}


@router.post("/emergency_stop")
def emergency_stop(body: ActionBody = None, db=Depends(get_db_sync)):
    """Emergency Stop: 최우선 정지. Gate 체인 1순위 차단. command_log + config + Hash Chain + Push."""
    reason = (body.reason if body else None) or ""
    log_command(db, "EMERGENCY_STOP", "warroom", {"reason": reason}, "ACCEPTED")
    set_config(db, GATE_EMERGENCY_STOP_ACTIVE, {"active": True, "reason": reason}, "control")
    append_audit_event("emergency_stop", {"reason": reason, "source": "warroom", "ts_utc": datetime.now(timezone.utc).isoformat()}, payload_preview=reason or "비상 정지")
    push_event("emergency_stop", reason or "비상 정지")
    return {"status": "ok", "action": "emergency_stop"}


@router.post("/resume")
def resume(body: ActionBody = None, db=Depends(get_db_sync)):
    """Resume: EmergencyStop/Retract 해제. Gate 체인에서 재평가 가능."""
    reason = (body.reason if body else None) or ""
    set_config(db, GATE_EMERGENCY_STOP_ACTIVE, {"active": False}, "control")
    set_config(db, GATE_RETRACT_ACTIVE, {"active": False}, "control")
    log_command(db, "RESUME", "warroom", {"reason": reason}, "ACCEPTED")
    append_audit_event("resume", {"reason": reason, "source": "warroom"}, payload_preview=reason or "resume")
    return {"status": "ok", "action": "resume"}
