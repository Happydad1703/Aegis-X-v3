# Aegis-X v3 Internal Simulation Report

**Generated**: 2026-03-01T17:12:48Z (UTC)

기준: docs/64_Phase0_1, 65_Final_Directory_Architecture_Lock, 43_DB_Schema, 14_TVP

---

## 1. Structure (65)

**PASS**

- ✅ backend/app/core/db.py
- ✅ backend/app/core/snapshot_repo.py
- ✅ backend/app/core/incident_repo.py
- ✅ backend/app/core/command_repo.py
- ✅ backend/app/core/mode_service.py
- ✅ backend/app/core/config_service.py
- ✅ backend/app/core/resource_monitor.py
- ✅ backend/app/engines/regime_engine.py
- ✅ backend/app/engines/allocation_engine.py
- ✅ backend/app/engines/fleet_budget_engine.py
- ✅ backend/app/engines/capital_scaling.py
- ✅ backend/app/engines/health_engine.py
- ✅ backend/app/engines/strike_engine.py
- ✅ backend/app/engines/swing_engine.py
- ✅ backend/app/engines/core_engine.py
- ✅ backend/app/gates/pre_trade_gate.py
- ✅ backend/app/gates/cap_gate.py
- ✅ backend/app/gates/risk_gate.py
- ✅ backend/app/gates/freshness_gate.py
- ✅ backend/app/gates/mode_gate.py
- ✅ backend/app/gates/crisis_gate.py
- ✅ backend/app/execution/paper_executor.py
- ✅ backend/app/execution/kis_executor.py
- ✅ backend/app/workers/engine_worker.py
- ✅ backend/app/workers/ingest_worker.py
- ✅ backend/app/api/control.py
- ✅ backend/app/api/cic.py
- ✅ backend/app/api/health.py
- ✅ backend/app/api/pilot.py
- ✅ backend/app/models/schemas.py
- ✅ backend/app/utils/time_utils.py

## 2. DDL (64/43)

**PASS**

- ✅ Table: ext_event_raw
- ✅ Table: engine_snapshot
- ✅ Table: system_mode
- ✅ Table: system_config
- ✅ Table: incident_log
- ✅ Table: command_log
- ✅ TIMESTAMPTZ/NOW() used
- ✅ JSONB used for JSON columns

## 3. Snapshot 6 Keys (64)

**PASS**

- ✅ Snapshot key produced: engine_heartbeat
- ✅ Snapshot key produced: comm_health
- ✅ Snapshot key produced: regime_current
- ✅ Snapshot key produced: operation_mode
- ✅ Snapshot key produced: llm_status
- ✅ Snapshot key produced: risk_guard
- ✅ insert_snapshot (snapshot_repo) used

## 4. Module Boundary (65)

**PASS**

- ✅ engines/__init__.py: no direct DB
- ✅ engines/regime_engine.py: no direct DB
- ✅ engines/allocation_engine.py: no direct DB
- ✅ engines/fleet_budget_engine.py: no direct DB
- ✅ engines/capital_scaling.py: no direct DB
- ✅ engines/health_engine.py: no direct DB
- ✅ engines/strike_engine.py: no direct DB
- ✅ engines/swing_engine.py: no direct DB
- ✅ engines/core_engine.py: no direct DB
- ✅ core/snapshot_repo.py exists (single write path)

---

## Summary

- Pass: 56
- Fail/Gap: 0

**Result: GO** — 시스템 개발 구도 기준 충족. Phase 0-1 개발 착수 가능.