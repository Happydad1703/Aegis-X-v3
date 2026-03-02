# Signal Interface ICD — Engine I/O Dict Schemas + Snapshot Key Catalog

Engines are pure dict in → dict out. All snapshot writes via snapshot_repo only.

---

## 1. Regime engine

- **Input:** `{ events_count, trend_score, volatility_state, universe }`
- **Output:** `{ regime_label, crisis_probability, trend_score, confidence_score, volatility_state, generated_inputs_hash, computed_at_utc }`
- **Snapshot key:** `regime_current`

---

## 2. Allocation engine

- **Input:** regime_current (dict)
- **Output:** `{ base_weights, regime_label, formula, … }`
- **Snapshot key:** `allocation_matrix`

---

## 3. Fleet budget engine

- **Input:** allocation_matrix, optional pilot_config
- **Output:** `{ weights, regime_label }`
- **Snapshot key:** `fleet_budget_snapshot`

---

## 4. Core engine (targets)

- **Input:** `{ regime, crisis_prob, price, ma60, ma120, ma120_slope, relative_strength_rank, current_position }`
- **Output:** `{ action, target_weight, stop_loss, reason }` (structural trend follow, 60>120 hold, breach rule)
- **Snapshot keys:** `core_force_state`, `targets_core`

---

## 5. Swing engine (targets)

- **Input:** `{ regime, price, ma20, ma60, volume_ratio, breakout_10d, holding_days }`
- **Output:** `{ signal, position_size, stop_loss, max_holding_days }` (weekly trend, conservative entry/exit)
- **Snapshot keys:** `swing_force_state`, `targets_swing`

---

## 6. Strike engine (targets)

- **Input:** `{ regime, price, vol_spike, z_score, holding_days }`
- **Output:** `{ entry, exit, tp, sl }` (short-term breakout/mean-revert, risk cap)
- **Snapshot keys:** `strike_force_state`, `targets_strike`

---

## Snapshot key catalog (minimum set)

Required for one engine cycle and UI:

- engine_heartbeat  
- comm_health  
- llm_status  
- operation_mode  
- regime_current  
- allocation_matrix  
- fleet_budget_snapshot  
- risk_guard  
- targets_core  
- targets_swing  
- targets_strike  

Extended: core_force_state, swing_force_state, strike_force_state, active_session, session_state, timezone, usd_exposure_status.

SSOT: `backend/app/core/snapshot_keys.py` (ALLOWED_SNAPSHOT_KEYS).
