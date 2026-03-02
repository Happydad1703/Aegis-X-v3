# FULL COMBAT SYSTEM LOCK — Validation Checklist

Run in order. KR scope only; no US market.

---

## 1. Infrastructure

| Step | Command | Expected |
|------|---------|----------|
| 1.1 | `docker ps` | Container `aegisx-db` listed (or `docker compose up -d`) |
| 1.2 | `.\scripts\migrate_db.ps1` | Exit 0, "Migration complete." |
| 1.3 | `python scripts\debug_db_target.py` | Exit 0, engine_snapshot table exists |

---

## 2. Engine + Snapshot

| Step | Command | Expected |
|------|---------|----------|
| 2.1 | `python scripts\run_engine_cycle.py` | Exit 0 |
| 2.2 | `python scripts\verify_snapshot_keys.py` | Exit 0, "[OK] Required snapshot keys present" |

---

## 3. Unit tests (no DB required for most)

| Step | Command | Expected |
|------|---------|----------|
| 3.1 | `pytest backend/tests/test_combat_force_spec_lock.py -v` | 11 passed (engine purity, core enter, swing buy, strike entry) |
| 3.2 | `pytest backend/tests/test_combat_system_lock.py -v` | 8 passed (gate precedence, live mode block, order state transition) |

---

## 4. Integration test (DB required)

| Step | Command | Expected |
|------|---------|----------|
| 4.1 | `pytest backend/tests/test_combat_integration.py -v` | Pass or skip if no DB (migration table, one cycle keys, gate PASS + paper order) |

---

## 5. One-shot harness

| Step | Command | Expected |
|------|---------|----------|
| 5.1 | `.\scripts\validate_phase0_1.ps1` | All steps 1–6 pass (docker, migrate, debug, engine cycle, verify keys, pytest) |

---

## 6. Execution ROE (manual)

- **PAPER**: Set system_mode to PAPER; run execution_runner with intent → order_log row with PAPER_FILLED.
- **BACKTEST**: Set system_mode to BACKTEST; run execution_runner → gate blocks, no order_log insert from flow.
- **KIS**: Only when mode is PILOT/FULL_LIVE; kis_executor is the only place that talks to KIS (stub in Phase 0-1).

---

## Success criteria

- All unit tests pass.
- Integration tests pass when DB is available (or skip cleanly).
- No engine imports sqlalchemy or kis_executor.
- All DB writes go through snapshot_repo or *_repo.
- Gate precedence enforced; order state transitions validated.
