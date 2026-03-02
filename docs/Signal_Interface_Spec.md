# Signal Interface Spec (FULL COMBAT LOCK)

Engine and execution layer contracts. Engines are pure dict → dict (P2).

---

## 1. Regime Engine

- **Input**: `{ events_count, trend_score, volatility_state, universe }`
- **Output**: `{ regime_label, crisis_probability, trend_score, confidence_score, volatility_state, ... }`
- **Snapshot key**: `regime_current`

---

## 2. Allocation Engine

- **Input**: `regime_current` (dict)
- **Output**: `{ base_weights, regime_label, formula, ... }`
- **Snapshot key**: `allocation_matrix`

---

## 3. Fleet Budget Engine

- **Input**: `allocation_matrix`, optional `pilot_config`
- **Output**: `{ weights, regime_label }`
- **Snapshot key**: `fleet_budget_snapshot`

---

## 4. Core Engine (Spec Lock v1.0 / v1.1)

- **Input**: `{ regime, crisis_prob, price, ma60, ma120, ma120_slope, relative_strength_rank, current_position }`
- **Output**: `{ action: "HOLD"|"ENTER"|"EXIT", target_weight, stop_loss, reason }`
- **Snapshot key**: `core_force_state`

---

## 5. Swing Engine

- **Input**: `{ regime, price, ma20, ma60, volume_ratio, breakout_10d, holding_days }`
- **Output**: `{ signal: "BUY"|"SELL"|"HOLD", position_size, stop_loss, max_holding_days }`
- **Snapshot key**: `swing_force_state`

---

## 6. Strike Engine

- **Input**: `{ regime, price, vol_spike, z_score, holding_days }`
- **Output**: `{ entry, exit, tp, sl }`
- **Snapshot key**: `strike_force_state`

---

## 7. Order Intent (to execution layer)

Execution layer accepts intent dict; gate must be PASS upstream.

- **Fields**: `symbol` (str), `side` ("BUY"|"SELL"), `quantity` (float). Optional: `strategy`, `rationale`, `limit_price`, `time_in_force`.
- **Source**: Built from engine outputs (Core/Swing/Strike) by worker or strategy layer; never from UI directly.

---

## 8. ExecutableOrder (after gate)

- **symbol**, **side**, **quantity**, **mode** (PAPER/PILOT/FULL_LIVE), **risk_tag** (optional).
- Only execution layer (paper_executor / kis_executor) writes to order_log via order_repo.
