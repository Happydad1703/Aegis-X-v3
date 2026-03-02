# engines/swing_engine.py — Spec Lock v1.0: Swing Engine Contract. PURE dict in → dict out.
# NO DB, NO API, NO env, NO datetime, NO randomness.
# 수식 Lock: BUY iff regime in {Bull,Sideways} & ma20>ma60 & breakout_10d & volume_ratio ≥ 1.2;
#            SELL iff ma20<ma60 OR holding_days>15 OR -8% 손절.

from __future__ import annotations

# --- Spec Lock v1.0 constants ---
SWING_VOLUME_RATIO_MIN = 1.2
SWING_MAX_HOLDING_DAYS = 15
SWING_STOP_LOSS_PCT = -0.08
BUY_REGIMES = frozenset({"Bull", "Sideways"})


def compute_swing(swing_input: dict) -> dict:
    """
    Pure: Swing Engine Contract (Spec Lock v1.0).
    Input: regime, price, ma20, ma60, volume_ratio, breakout_10d, holding_days
    Output: signal (BUY|SELL|HOLD), position_size, stop_loss, max_holding_days
    """
    regime = (swing_input.get("regime") or "").strip()
    ma20 = float(swing_input.get("ma20", 0))
    ma60 = float(swing_input.get("ma60", 0))
    volume_ratio = float(swing_input.get("volume_ratio", 0))
    breakout_10d = bool(swing_input.get("breakout_10d", False))
    holding_days = int(swing_input.get("holding_days", 0))

    # SELL: ma20 < ma60 OR holding_days > 15 (손절 -8%는 실행 레이어에서 가격 기반 적용)
    if ma20 < ma60:
        return {
            "signal": "SELL",
            "position_size": 0.0,
            "stop_loss": SWING_STOP_LOSS_PCT,
            "max_holding_days": SWING_MAX_HOLDING_DAYS,
        }
    if holding_days > SWING_MAX_HOLDING_DAYS:
        return {
            "signal": "SELL",
            "position_size": 0.0,
            "stop_loss": SWING_STOP_LOSS_PCT,
            "max_holding_days": SWING_MAX_HOLDING_DAYS,
        }

    # BUY: regime in {Bull, Sideways}, ma20 > ma60, breakout_10d == True, volume_ratio ≥ 1.2
    if (
        regime in BUY_REGIMES
        and ma20 > ma60
        and breakout_10d is True
        and volume_ratio >= SWING_VOLUME_RATIO_MIN
    ):
        return {
            "signal": "BUY",
            "position_size": 0.15,
            "stop_loss": SWING_STOP_LOSS_PCT,
            "max_holding_days": SWING_MAX_HOLDING_DAYS,
        }

    return {
        "signal": "HOLD",
        "position_size": 0.0,
        "stop_loss": SWING_STOP_LOSS_PCT,
        "max_holding_days": SWING_MAX_HOLDING_DAYS,
    }
