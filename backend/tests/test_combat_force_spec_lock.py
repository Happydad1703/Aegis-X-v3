# backend/tests/test_combat_force_spec_lock.py — Spec Lock v1.0 검증: Core/Swing/Strike I/O 계약 및 수식 Lock

from __future__ import annotations

import pytest


def test_engine_purity_core_no_sqlalchemy() -> None:
    """엔진 순수성: core_engine 모듈에 sqlalchemy 미포함."""
    import backend.app.engines.core_engine as core
    assert "sqlalchemy" not in str(core.__dict__).lower()


def test_engine_purity_swing_strike_no_sqlalchemy() -> None:
    """엔진 순수성: swing/strike 모듈에 sqlalchemy 미포함."""
    import backend.app.engines.swing_engine as swing
    import backend.app.engines.strike_engine as strike
    assert "sqlalchemy" not in str(swing.__dict__).lower()
    assert "sqlalchemy" not in str(strike.__dict__).lower()


def test_core_enter_logic() -> None:
    """Core ENTER: regime=Bull, ma60>ma120, ma120_slope>0, RS_rank ≤ 20% → action==ENTER."""
    from backend.app.engines.core_engine import compute_core_force
    input_data = {
        "regime": "Bull",
        "crisis_prob": 0.1,
        "price": 100.0,
        "ma60": 110.0,
        "ma120": 100.0,
        "ma120_slope": 1.0,
        "relative_strength_rank": 0.10,
        "current_position": 0.0,
    }
    result = compute_core_force(input_data)
    assert result["action"] == "ENTER"
    assert result["stop_loss"] == -0.20


def test_core_exit_on_crisis() -> None:
    """Core EXIT: regime==Crisis → action==EXIT."""
    from backend.app.engines.core_engine import compute_core_force
    result = compute_core_force({
        "regime": "Crisis",
        "ma60": 110,
        "ma120": 100,
    })
    assert result["action"] == "EXIT"


def test_core_exit_on_ma_cross() -> None:
    """Core EXIT: ma60 < ma120 → action==EXIT."""
    from backend.app.engines.core_engine import compute_core_force
    result = compute_core_force({
        "regime": "Goldilocks",
        "ma60": 90,
        "ma120": 100,
    })
    assert result["action"] == "EXIT"


def test_swing_buy_logic() -> None:
    """Swing BUY: regime in {Bull,Sideways}, ma20>ma60, breakout_10d, volume_ratio ≥ 1.2 → signal==BUY."""
    from backend.app.engines.swing_engine import compute_swing
    input_data = {
        "regime": "Bull",
        "price": 50.0,
        "ma20": 52.0,
        "ma60": 48.0,
        "volume_ratio": 1.5,
        "breakout_10d": True,
        "holding_days": 0,
    }
    result = compute_swing(input_data)
    assert result["signal"] == "BUY"
    assert result["stop_loss"] == -0.08


def test_swing_sell_on_ma() -> None:
    """Swing SELL: ma20 < ma60 → signal==SELL."""
    from backend.app.engines.swing_engine import compute_swing
    result = compute_swing({
        "regime": "Bull",
        "ma20": 45,
        "ma60": 50,
        "holding_days": 5,
    })
    assert result["signal"] == "SELL"


def test_swing_sell_on_holding_days() -> None:
    """Swing SELL: holding_days > 15 → signal==SELL."""
    from backend.app.engines.swing_engine import compute_swing
    result = compute_swing({
        "regime": "Bull",
        "ma20": 52,
        "ma60": 48,
        "volume_ratio": 1.5,
        "breakout_10d": True,
        "holding_days": 20,
    })
    assert result["signal"] == "SELL"


def test_strike_entry_logic() -> None:
    """Strike entry: regime != Crisis, vol_spike ≥ 1.5, z_score ≤ -2 → entry==True."""
    from backend.app.engines.strike_engine import compute_strike
    input_data = {
        "regime": "Sideways",
        "price": 100.0,
        "vol_spike": 2.0,
        "z_score": -2.5,
        "holding_days": 0,
    }
    result = compute_strike(input_data)
    assert result["entry"] is True
    assert result["tp"] == 0.05
    assert result["sl"] == -0.03


def test_strike_no_entry_on_crisis() -> None:
    """Strike: regime==Crisis → entry==False."""
    from backend.app.engines.strike_engine import compute_strike
    result = compute_strike({
        "regime": "Crisis",
        "vol_spike": 2.0,
        "z_score": -2.5,
    })
    assert result["entry"] is False


def test_strike_exit_holding_days() -> None:
    """Strike exit: holding_days ≥ 3 → exit==True."""
    from backend.app.engines.strike_engine import compute_strike
    result = compute_strike({
        "regime": "Bull",
        "vol_spike": 0,
        "z_score": 0,
        "holding_days": 5,
    })
    assert result["exit"] is True
