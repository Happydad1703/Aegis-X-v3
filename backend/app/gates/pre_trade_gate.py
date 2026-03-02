# gates/pre_trade_gate.py — SE-50 Pre-Trade Gate: ROE 판단 only. 엔진=상태 판단, Gate=행동 허용/차단.
# Phase 1-5 / 2-4: structural_trend_status == BROKEN → block_trade. No strategy computation in gate.

from __future__ import annotations


def get_structural_trend_status(snapshot_data: dict) -> str:
    """Extract structural_trend_status from core_force_state or regime snapshot. Returns ACTIVE | BROKEN | unknown."""
    if not snapshot_data:
        return "unknown"
    # Spec Lock v1.0: core_force_state has "action" (ENTER|HOLD|EXIT)
    action = snapshot_data.get("action")
    if action == "EXIT":
        return "BROKEN"
    if action in ("ENTER", "HOLD"):
        return "ACTIVE"
    # Legacy: structural_trend_status
    s = snapshot_data.get("structural_trend_status")
    if s in ("ACTIVE", "BROKEN"):
        return s
    # regime_current fallback: high crisis_probability => treat as BROKEN for safety
    crisis = snapshot_data.get("crisis_probability")
    if isinstance(crisis, (int, float)) and crisis >= 0.7:
        return "BROKEN"
    return "ACTIVE"


def run_pre_trade_gate(
    regime_snapshot_data: dict | None = None,
    core_force_snapshot_data: dict | None = None,
) -> tuple[bool, list[tuple[str, bool, str]]]:
    """
    SE-50: Gate decides allow/block. Returns (allow_trade, list of (check_name, passed, message)).
    structural_trend_status == BROKEN → block_trade.
    """
    reasons: list[tuple[str, bool, str]] = []
    # Prefer core_force_state if present
    data = core_force_snapshot_data or regime_snapshot_data or {}
    status = get_structural_trend_status(data)
    if status == "BROKEN":
        reasons.append(("structural_trend", False, "structural_trend_status BROKEN"))
        return False, reasons
    reasons.append(("structural_trend", True, f"status={status}"))
    return True, reasons
