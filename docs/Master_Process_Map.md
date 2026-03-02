# Master Process Map — Aegis-X V3 (Single Source)

PC-operable capital robot. KOSPI/KOSDAQ first; US(S&P) expansion = interfaces/ICD only. Single broker: KIS. 7/24 following-the-sun via automation + monitoring.

---

## End-to-end flow

```
Ingest
  → ext_event_raw / macro_context
  → regime_engine (+ LLM if enabled)
  → engine_snapshot(regime_current)
  → allocation_engine
  → engine_snapshot(allocation_matrix)
  → fleet_budget_engine
  → engine_snapshot(fleet_budget_snapshot)
  → risk_gate / pre_trade_gate
  → engine_snapshot(risk_guard, comm_health, llm_status)
  → target engines (core / swing / strike)
  → engine_snapshot(targets_core, targets_swing, targets_strike)
  → execution (paper_executor OR kis_executor)
  → order_log
  → portfolio_state (snapshot)
  → AAR
  → battle_report
  → system_config tuning
```

---

## Stage summary

| Stage | Input | Output | DB write path |
|-------|--------|--------|----------------|
| Ingest | External APIs, heartbeat | event_type, payload | event_repo → ext_event_raw |
| Regime | events_count, trend, volatility, macro | regime_current | snapshot_repo → engine_snapshot |
| Allocation | regime_current | allocation_matrix | snapshot_repo |
| Fleet budget | allocation_matrix, pilot_config | fleet_budget_snapshot | snapshot_repo |
| Gates | snapshots, system_config | risk_guard, comm_health, llm_status | snapshot_repo (status) |
| Target engines | regime, battlefield, allocation | targets_core, targets_swing, targets_strike | snapshot_repo |
| Execution | Order intent (after gate PASS) | order_log rows | order_repo → order_log |
| AAR / tuning | order_log, battle_report | system_config updates | config_service |

---

## SE principles (non-negotiable)

- **P1** DB-Only Read: UI and upper layers read ONLY from engine_snapshot and audit tables.
- **P2** Engine Purity: engines/* are pure dict in → dict out; no DB, SQL, network, time inside engines.
- **P3** Single Write Path: engine results written ONLY via core/snapshot_repo.py.
- **P4** Safety precedence: EmergencyStop > Retract > Mode > Strategy.
- **P5** Execution separation: engines decide; executors execute; engines never call KIS.
