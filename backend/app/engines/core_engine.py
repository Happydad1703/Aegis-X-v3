# engines/core_engine.py — CoreForce_Structural_Trend_Mapping: pure dict in → core_force_state out. SE-50 Wide Stop.

from __future__ import annotations

from datetime import datetime, timezone


def compute_core_force(core_input: dict) -> dict:
    """
    Pure: core_input (regime, battlefield_state, allocation_matrix, fleet_budget, risk_guard, macro_context)
    → core_output (structural_trend_status, trade_signal, core_weight_delta, promotion_list, meta).
    """
    battlefield = core_input.get("battlefield_state") or {}
    regime = core_input.get("regime_current") or {}
    ma60 = battlefield.get("ma60") or 0.0
    ma120 = battlefield.get("ma120") or 0.0
    ma120_slope = battlefield.get("ma120_slope") or 0.0
    trend_ok = ma60 > ma120 and ma120_slope > 0
    structural_trend_status = "ACTIVE" if trend_ok else "BROKEN"
    trade_signal = "HOLD" if trend_ok else "REVIEW"
    growth = core_input.get("portfolio_growth_rate") or 0.0
    core_weight_delta = 0.01 if growth > 0.05 else 0.0
    return {
        "structural_trend_status": structural_trend_status,
        "trade_signal": trade_signal,
        "core_weight_delta": core_weight_delta,
        "promotion_list": [],
        "meta": {"source_name": "core_engine", "refresh_rate_sec": 3600, "ts_utc": datetime.now(timezone.utc).isoformat()},
    }
