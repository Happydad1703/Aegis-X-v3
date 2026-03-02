# AEGIS-X V3 — Master Architecture Pack (Phase 0-1)

Single Windows 11 PC, KIS as ONLY execution gateway. SE principles locked; minimal, testable, 7/24-ready.

---

## 1. Master Process Map

```
Ingest  →  Engines  →  Gates  →  Execution  →  Logs  →  UI
   |           |          |           |          |        |
   v           v          v           v          v        v
event_repo   snapshot_   gate_chain   paper_/    order_   API
ext_event_   repo        (linear     kis_       log,     (read
raw          engine_     priority)   executor   incident_ only
             snapshot                  |        log       engine_
                                       v                   snapshot
                                    KIS API
                                    (execution
                                     layer ONLY)
```

| Stage | Module(s) | Input | Output | DB Write Path |
|-------|-----------|--------|--------|----------------|
| Ingest | ingest_worker | External APIs, heartbeat | event_type, payload | event_repo → ext_event_raw only |
| Regime | regime_engine (pure) | events_count, trend_score, volatility | regime_current | snapshot_repo → engine_snapshot |
| Allocation | allocation_engine (pure) | regime_current | allocation_matrix | snapshot_repo |
| Fleet Budget | fleet_budget_engine (pure) | allocation_matrix | fleet_budget_snapshot | snapshot_repo |
| Core/Swing/Strike | core_engine, swing_engine, strike_engine (pure) | regime, battlefield, etc. | core_force_state, swing_force_state, strike_force_state | snapshot_repo |
| Gates | gate_chain, mode_gate, risk_gate, freshness_gate, pre_trade_gate | snapshots, system_config | allow/block | (no write) |
| Execution | paper_executor, kis_executor | Order intent (after gate PASS) | order_log rows | order_repo → order_log only |
| API / UI | cic API, Warroom | — | Read-only from engine_snapshot | No write (P1 DB-Only Read) |

**KIS boundary**: Engines produce target intents / orders as pure dict. **Only the execution layer** (paper_executor, kis_executor) may talk to KIS. Never send live orders unless Mode==LIVE and all gates pass.

---

## 2. Module Master

| Directory | Role | Write Path (if any) |
|-----------|------|---------------------|
| **core/** | db.py (sync + async), snapshot_repo, event_repo, incident_repo, command_repo, config_service, mode_service, snapshot_keys, env_keys, timezone_service, universe_selector | snapshot_repo → engine_snapshot; event_repo → ext_event_raw; incident_repo → incident_log; command_repo → command_log |
| **engines/** | regime_engine, allocation_engine, fleet_budget_engine, core_engine, swing_engine, strike_engine | None (P2 pure dict→dict) |
| **gates/** | gate_chain, mode_gate, risk_gate, freshness_gate, pre_trade_gate | incident_repo when gate fails (optional) |
| **execution/** | paper_executor, kis_executor | order_repo → order_log only |
| **workers/** | ingest_worker, engine_worker | Via core repos only |
| **api/** | cic (snapshot read-only), control (commands) | command_repo, config/mode updates |
| **database/** | models.py (SQLAlchemy 2.0) | None (reflection of DDL) |
| **scripts/** | migrate_db.ps1, debug_db_target.py, run_engine_cycle.py, verify_snapshot_keys.py, validate_phase0_1.ps1 | None |

---

## 3. Schema Summary (tables + key columns)

| Table | Key Columns | Single Write Path |
|-------|-------------|-------------------|
| ext_event_raw | id, event_type, source_name, payload, received_at | event_repo |
| engine_snapshot | id, snapshot_key, snapshot_data, freshness_status, source_name, refresh_rate_sec, generated_at, prev_hash, self_hash | snapshot_repo |
| system_mode | id, mode, changed_by, changed_at | mode_service / command path |
| system_config | id, config_key, config_value, updated_by, updated_at | config_service |
| incident_log | id, severity, category, message, related_snapshot_key, created_at | incident_repo |
| command_log | id, command_type, issued_by, command_payload, status, created_at | command_repo |
| order_log | id, symbol, side, quantity, mode, execution_status, execution_payload, created_at, prev_hash, self_hash | order_repo |

DDL source: `db/migrations/001_init_core.sql`, `002_order_log.sql`, `003_hash_chain_columns.sql`. ORM: `backend/app/database/models.py` (aligned, no DDL change from ORM).

---

## 4. Signal Interfaces

### Engine input/output (pure dict)

- **regime_engine**: in `{ events_count, trend_score, volatility_state, universe }` → out `{ regime_label, crisis_probability, trend_score, confidence_score, ... }`
- **allocation_engine**: in `regime_current` → out `{ base_weights, regime_label, ... }`
- **fleet_budget_engine**: in `allocation_matrix`, pilot_config → out `{ weights, regime_label }`
- **core_engine** (Spec Lock v1.0): in `{ regime, crisis_prob, price, ma60, ma120, ma120_slope, relative_strength_rank, current_position }` → out `{ action, target_weight, stop_loss, reason }`
- **swing_engine**: in `{ regime, price, ma20, ma60, volume_ratio, breakout_10d, holding_days }` → out `{ signal, position_size, stop_loss, max_holding_days }`
- **strike_engine**: in `{ regime, price, vol_spike, z_score, holding_days }` → out `{ entry, exit, tp, sl }`

### Snapshot key catalog (allowlist)

**Phase 0-1 required (6):** engine_heartbeat, comm_health, llm_status, operation_mode, regime_current, risk_guard  

**Extended:** allocation_matrix, fleet_budget_snapshot, core_force_state, swing_force_state, strike_force_state, active_session, session_state, timezone, usd_exposure_status  

SSOT: `backend/app/core/snapshot_keys.py` (ALLOWED_SNAPSHOT_KEYS, get_required_snapshot_keys_for_cycle).

---

## 5. Verification Checklist (FULL COMBAT LOCK — exact commands + expected results)

| Step | Command | Expected |
|------|---------|----------|
| 1 | `docker ps` | Container `aegisx-db` listed (or start with `docker compose up -d`) |
| 2 | `.\scripts\migrate_db.ps1` | Exit 0; "Migration complete." |
| 3 | `python scripts\debug_db_target.py` | Exit 0; prints current_database()=aegisx, to_regclass('public.engine_snapshot') non-null |
| 4 | `python scripts\run_engine_cycle.py` | Exit 0; "OK" or cycle completion |
| 5 | `python scripts\verify_snapshot_keys.py` | Exit 0; "[OK] Required snapshot keys present" |
| 6 | `python -m pytest backend/tests/test_phase1_acceptance.py backend/tests/test_contract_engines_purity.py backend/tests/test_combat_force_spec_lock.py -v` | All tests pass or skip (DB unavailable) |

**One-shot harness:** `.\scripts\validate_phase0_1.ps1` runs steps 1–6 in order; fails fast with clear error.

**Combat system lock tests:**

| Test | Command | Expected |
|------|---------|----------|
| Engine purity + Core/Swing/Strike | `pytest backend/tests/test_combat_force_spec_lock.py -v` | All pass |
| Gate precedence + order state | `pytest backend/tests/test_combat_system_lock.py -v` | All pass |
| Integration (cycle + paper order) | `pytest backend/tests/test_combat_integration.py -v` | Pass or skip if no DB |

**Runtime baseline:** Container `aegisx-db`, DB `aegisx`, user `postgres`, host port `5433`.  
`.env`: `DATABASE_URL=postgresql+psycopg2://postgres:PW@localhost:5433/aegisx`. Optional `PG_CONTAINER` overrides container name.

---

## 6. SE Hard Lock (non-negotiable)

- **P1 DB-Only Read**: UI and upper layers read ONLY from DB (engine_snapshot, logs). No direct calculations outside engines.
- **P2 Strict Engine Purity**: engines/* are pure dict in → dict out. No DB, SQL, HTTP, side effects.
- **P3 Single Write Path**: All engine outputs written ONLY via core/snapshot_repo; logs via core/*_repo. No other DB writes.

**Safety order:** EmergencyStop > Retract > Mode > Strategy. On uncertainty or stale data: degrade conservatively (Freeze/Disable trading).

**Scope freeze:** KR (KOSPI/KOSDAQ via KIS) only. US/S&P not implemented beyond stubs; design extensible for later.
