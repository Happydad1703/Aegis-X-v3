# engines/strike_engine.py — Spec Lock v1.0: Strike Engine Contract. PURE dict in → dict out.
# NO DB, NO API, NO env, NO datetime, NO randomness.
# 수식 Lock: entry iff regime != Crisis & vol_spike ≥ 1.5 & z_score ≤ -2;
#            exit: +5% TP, -3% SL, holding_days ≥ 3.

from __future__ import annotations

# --- Spec Lock v1.0 constants ---
STRIKE_VOL_SPIKE_MIN = 1.5
STRIKE_Z_SCORE_MAX = -2.0
STRIKE_TP_PCT = 0.05
STRIKE_SL_PCT = -0.03
STRIKE_MIN_HOLDING_DAYS_EXIT = 3


def compute_strike(strike_input: dict) -> dict:
    """
    Pure: Strike Engine Contract (Spec Lock v1.0).
    Input: regime, price, vol_spike, z_score, holding_days
    Output: entry (bool), exit (bool), tp (float), sl (float)
    """
    regime = (strike_input.get("regime") or "").strip()
    vol_spike = float(strike_input.get("vol_spike", 0))
    z_score = float(strike_input.get("z_score", 0))
    holding_days = int(strike_input.get("holding_days", 0))

    # entry: regime != "Crisis" AND vol_spike >= 1.5 AND z_score <= -2
    entry = (
        regime != "Crisis"
        and vol_spike >= STRIKE_VOL_SPIKE_MIN
        and z_score <= STRIKE_Z_SCORE_MAX
    )

    # exit: +5% TP or -3% SL or holding_days >= 3 (실제 TP/SL 도달은 실행 레이어)
    exit_ = holding_days >= STRIKE_MIN_HOLDING_DAYS_EXIT

    return {
        "entry": entry,
        "exit": exit_,
        "tp": STRIKE_TP_PCT,
        "sl": STRIKE_SL_PCT,
    }
