# gates/gate_chain.py — SE-50: 선형 우선순위 체인. 병렬 아님.
# 순서: EmergencyStop → Retract → Mode → Risk → Freshness → Pre-Trade → Strategy
# Execution은 모든 게이트 통과 후에만 허용.

from __future__ import annotations

from typing import Any

# Gate name constants (order = priority)
GATE_EMERGENCY_STOP = "EmergencyStop"
GATE_RETRACT = "Retract"
GATE_MODE = "Mode"
GATE_RISK = "Risk"
GATE_FRESHNESS = "Freshness"
GATE_PRE_TRADE = "PreTrade"
GATE_STRATEGY = "Strategy"

GATE_ORDER = (
    GATE_EMERGENCY_STOP,
    GATE_RETRACT,
    GATE_MODE,
    GATE_RISK,
    GATE_FRESHNESS,
    GATE_PRE_TRADE,
    GATE_STRATEGY,
)


def run_gate_chain(db: Any, context: dict[str, Any] | None = None) -> tuple[bool, str, list[tuple[str, bool, str]]]:
    """
    SE-50: 선형 게이트 체인. 첫 실패 시 즉시 (allow=False, failed_gate_name) 반환.
    Returns: (allow_execution, failed_gate_or_empty, reasons).
    """
    context = context or {}
    reasons: list[tuple[str, bool, str]] = []

    # 1. EmergencyStop (DB: system_config gate_emergency_stop_active)
    cfg = _get_config(db, "gate_emergency_stop_active")
    if _is_active(cfg):
        reasons.append((GATE_EMERGENCY_STOP, False, "Emergency stop active"))
        return False, GATE_EMERGENCY_STOP, reasons

    reasons.append((GATE_EMERGENCY_STOP, True, "OK"))

    # 2. Retract (DB: system_config gate_retract_active)
    cfg = _get_config(db, "gate_retract_active")
    if _is_active(cfg):
        reasons.append((GATE_RETRACT, False, "Retract active"))
        return False, GATE_RETRACT, reasons

    reasons.append((GATE_RETRACT, True, "OK"))

    # 2b. LLM Blackout (Execution Freeze: block_new_orders, allow_only_risk_reduction)
    cfg_blackout = _get_config(db, "llm_blackout_active")
    if _is_active(cfg_blackout):
        reasons.append(("LLMBlackout", False, "LLM blackout; execution freeze"))
        return False, "LLMBlackout", reasons
    reasons.append(("LLMBlackout", True, "OK"))

    # 2c. Session (Follow-the-Sun: OFF session → block_new_orders, allow_only_risk_reduction)
    session_row = _get_snapshot(db, "active_session")
    session_data = (session_row or {}).get("snapshot_data") if isinstance(session_row, dict) else None
    active_session = (session_data or {}).get("session") if isinstance(session_data, dict) else None
    if active_session == "OFF":
        reasons.append(("Session", False, "OFF session; block new orders"))
        return False, "Session", reasons
    reasons.append(("Session", True, f"session={active_session or 'unknown'}"))

    # 3. Mode Gate
    from backend.app.gates.mode_gate import run_mode_gate
    ok, msg = run_mode_gate(db)
    if not ok:
        reasons.append((GATE_MODE, False, msg))
        return False, GATE_MODE, reasons
    reasons.append((GATE_MODE, True, msg))

    # 4. Risk Gate (risk_guard snapshot: DD ≤ -8% or VolSpike ≥ 1.8)
    from backend.app.gates.risk_gate import run_risk_gate
    ok, msg = run_risk_gate(db)
    if not ok:
        reasons.append((GATE_RISK, False, msg))
        return False, GATE_RISK, reasons
    reasons.append((GATE_RISK, True, msg))

    # 5. Freshness Gate
    from backend.app.gates.freshness_gate import run_freshness_gate
    ok, msg = run_freshness_gate(db)
    if not ok:
        reasons.append((GATE_FRESHNESS, False, msg))
        return False, GATE_FRESHNESS, reasons
    reasons.append((GATE_FRESHNESS, True, msg))

    # 6. Pre-Trade Gate (structural_trend)
    from backend.app.gates.pre_trade_gate import run_pre_trade_gate
    core_row = context.get("core_force_snapshot") or _get_snapshot(db, "core_force_state")
    regime_row = context.get("regime_snapshot") or _get_snapshot(db, "regime_current")
    core_data = core_row.get("snapshot_data") if isinstance(core_row, dict) else None
    regime_data = regime_row.get("snapshot_data") if isinstance(regime_row, dict) else None
    allow, pre_reasons = run_pre_trade_gate(regime_snapshot_data=regime_data, core_force_snapshot_data=core_data)
    if not allow:
        for name, passed, m in pre_reasons:
            if not passed:
                reasons.append((GATE_PRE_TRADE, False, m))
                return False, GATE_PRE_TRADE, reasons
    reasons.append((GATE_PRE_TRADE, True, "structural_trend OK"))

    # 7. Strategy Signal = allow execution
    reasons.append((GATE_STRATEGY, True, "all gates passed"))
    return True, "", reasons


def _get_config(db: Any, key: str) -> dict | None:
    try:
        from backend.app.core.config_service import get_config
        out = get_config(db, key)
        return out if isinstance(out, dict) else None
    except Exception:
        return None


def _is_active(cfg: dict | None) -> bool:
    if not cfg or not isinstance(cfg, dict):
        return False
    return bool(cfg.get("active") is True)


def _get_snapshot(db: Any, snapshot_key: str) -> dict | None:
    try:
        from backend.app.core.snapshot_repo import get_latest_snapshot_sync
        return get_latest_snapshot_sync(db, snapshot_key)
    except Exception:
        return None
