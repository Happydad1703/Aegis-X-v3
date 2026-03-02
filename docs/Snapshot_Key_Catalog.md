# Snapshot Key Catalog (Phase 0-1 / FULL COMBAT LOCK)

SSOT: `backend/app/core/snapshot_keys.py`. API returns only keys in this allowlist (P1 DB-Only Read).

---

## Required (Phase 0-1 minimum)

| snapshot_key | Written by | Description |
|--------------|------------|-------------|
| engine_heartbeat | engine_worker | Alive tick |
| comm_health | engine_worker | External API connectivity status |
| llm_status | engine_worker | LLM gateway status |
| operation_mode | engine_worker | BACKTEST / PAPER / PILOT / FULL_LIVE |
| regime_current | regime_engine via engine_worker | Regime label, crisis_probability, trend_score |
| risk_guard | engine_worker | DD, vol_spike, policy |

---

## Extended (engine outputs)

| snapshot_key | Written by | Description |
|--------------|------------|-------------|
| allocation_matrix | allocation_engine | Base weights (CORE/SWING/STRIKE/RESERVE) |
| fleet_budget_snapshot | fleet_budget_engine | Weights, regime_label |
| core_force_state | core_engine | action, target_weight, stop_loss, reason (Spec Lock v1.0) |
| swing_force_state | swing_engine | signal, position_size, stop_loss, max_holding_days |
| strike_force_state | strike_engine | entry, exit, tp, sl |

---

## Follow-the-Sun

| snapshot_key | Description |
|--------------|-------------|
| active_session | KR / US / OFF |
| session_state | session, session_multiplier |
| timezone | session, utc |
| usd_exposure_status | usd_exposure_ratio, fx_volatility |

---

## Write path

All snapshot writes go **only** through `core/snapshot_repo.py` (insert_snapshot_sync / insert_snapshot). No other module may INSERT into engine_snapshot (P3 Single Write Path).
