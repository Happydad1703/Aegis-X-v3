# Module Master — Responsibilities and Boundaries

Single source for module ownership. No DB write outside designated repo; no KIS call outside execution layer.

---

## core/

- **db.py** — Sync + async engine/session; URLs from .env; derive one from the other if only one set.
- **snapshot_repo.py** — Only writer for engine_snapshot (P3).
- **event_repo.py** — Only writer for ext_event_raw.
- **incident_repo.py** — Only writer for incident_log.
- **command_repo.py** — Only writer for command_log.
- **order_repo.py** — Only writer for order_log.
- **config_service.py** — Read/write system_config.
- **mode_service.py** — Read/write system_mode.
- **snapshot_keys.py** — SSOT allowlist for snapshot_key.
- **order_state.py** — Order status and valid transitions.
- **env_keys.py**, **timezone_service.py**, **universe_selector.py** — Env, session, universe (KR scope).

---

## engines/

- **regime_engine** — Pure: events_count, trend, volatility → regime_label, crisis_probability.
- **allocation_engine** — Pure: regime_current → base_weights.
- **fleet_budget_engine** — Pure: allocation_matrix → weights.
- **core_engine** — Pure: structural trend, 60/120 MA → action, target_weight, stop_loss.
- **swing_engine** — Pure: weekly trend, conservative entry/exit → signal, position_size, stop_loss.
- **strike_engine** — Pure: short-term breakout/mean-revert, risk cap → entry, exit, tp, sl.

Rule: No DB, SQL, network, datetime inside engines (P2).

---

## gates/

- **gate_chain** — Linear precedence: EmergencyStop → Retract → LLMBlackout → Session → Mode → Risk → Freshness → Pre-Trade → Strategy.
- **mode_gate** — BACKTEST → block orders.
- **risk_gate** — DD, vol spike, USD/FX → block or block_strike.
- **freshness_gate**, **pre_trade_gate** — Age and structural_trend.

Freeze = stop new entries. Retract = reduce exposure. EmergencyStop = flatten and halt.

---

## execution/

- **paper_executor** — Simulated fills → order_repo only.
- **kis_executor** — Only component that talks to KIS; retry/backoff; PILOT/LIVE only.
- **execution_runner** — Run gate_chain then dispatch to paper or KIS by mode.

---

## workers/

- **ingest_worker** — External sources → event_repo (ext_event_raw).
- **engine_worker** — Orchestrate engines; write all snapshot keys via snapshot_repo only.

---

## api/

- **cic** — Read-only snapshot API (allowlist).
- **control** — Commands → command_log, config/mode.

---

## database/

- **models.py** — SQLAlchemy 2.0 typed ORM; Fleet ↔ Order when DDL has fleet; aligned to migrations.

---

## scripts/

- **migrate_db.ps1** — Apply migrations (PowerShell-safe pipe).
- **debug_db_target.py** — Print DB target and engine_snapshot existence.
- **run_engine_cycle.py** — One cycle, write snapshots.
- **verify_snapshot_keys.py**, **validate_phase0_1.ps1** — Verify keys and full harness.
