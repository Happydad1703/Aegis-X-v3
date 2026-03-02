# engines/core_engine.py — Spec Lock v1.0: Core Engine Contract. PURE dict in → dict out.
# NO DB, NO API, NO env, NO datetime, NO randomness.
# 수식 Lock: ENTER iff regime in {Goldilocks,Bull} & ma60>ma120 & ma120_slope>0 & RS_rank ≤ 20%;
#            EXIT iff ma60<ma120 OR regime==Crisis; stop_loss = -0.20.

from __future__ import annotations

# --- Spec Lock v1.0 constants (변경 시 SE 승인 필요) ---
CORE_STOP_LOSS = -0.20  # wide structural
RS_ENTER_CAP = 0.20     # relative_strength_rank ≤ 20% for ENTER
ENTER_REGIMES = frozenset({"Goldilocks", "Bull"})


def compute_core_force(core_input: dict) -> dict:
    """
    Pure: Core Engine Contract (Spec Lock v1.0).
    Input: regime, crisis_prob, price, ma60, ma120, ma120_slope, relative_strength_rank, current_position
    Output: action ("HOLD"|"ENTER"|"EXIT"), target_weight, stop_loss, reason
    """
    regime = (core_input.get("regime") or "").strip()
    crisis_prob = float(core_input.get("crisis_prob", 0))
    ma60 = float(core_input.get("ma60", 0))
    ma120 = float(core_input.get("ma120", 0))
    ma120_slope = float(core_input.get("ma120_slope", 0))
    rs_rank = float(core_input.get("relative_strength_rank", 1.0))
    current_position = float(core_input.get("current_position", 0))

    # EXIT 우선: ma60 < ma120 OR regime == "Crisis"
    if ma60 < ma120:
        return {
            "action": "EXIT",
            "target_weight": 0.0,
            "stop_loss": CORE_STOP_LOSS,
            "reason": "ma60 < ma120",
        }
    if regime == "Crisis":
        return {
            "action": "EXIT",
            "target_weight": 0.0,
            "stop_loss": CORE_STOP_LOSS,
            "reason": "regime Crisis",
        }

    # ENTER: regime in {Goldilocks, Bull}, ma60 > ma120, ma120_slope > 0, RS_rank ≤ 20%
    if (
        regime in ENTER_REGIMES
        and ma60 > ma120
        and ma120_slope > 0
        and rs_rank <= RS_ENTER_CAP
    ):
        return {
            "action": "ENTER",
            "target_weight": 0.25,
            "stop_loss": CORE_STOP_LOSS,
            "reason": "trend_ok_rs_ok",
        }

    # HOLD
    return {
        "action": "HOLD",
        "target_weight": current_position,
        "stop_loss": CORE_STOP_LOSS,
        "reason": "conditions_not_met",
    }
