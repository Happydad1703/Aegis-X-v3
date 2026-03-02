# Verification Playbook — How the System Self-Verifies

SE-compliant validation: scripts + pytest + run checklist.

---

## 1. Scripts

| Script | Purpose | Success |
|--------|---------|---------|
| **scripts/migrate_db.ps1** | Apply DDL to container (PowerShell pipe → docker exec psql) | Exit 0, "Migration complete." |
| **scripts/migrate_db_via_url.py** | Apply same DDL using DATABASE_URL (use when Python and container target different DBs) | Exit 0, "[OK] 001_... 002_... ..." |
| **scripts/debug_db_target.py** | Verify DB target (current_database, user, server, engine_snapshot existence) | Exit 0; prints target info |
| **scripts/run_engine_cycle.py** | One cycle end-to-end; writes snapshots via snapshot_repo | Exit 0 |
| **scripts/verify_snapshot_keys.py** | Assert required snapshot keys exist in engine_snapshot | Exit 0, "[OK] Required snapshot keys present" |
| **scripts/validate_phase0_1.ps1** | Full harness: docker → migrate → debug → cycle → verify → pytest | All steps pass |

---

## 2. Pytest suite

| Test module | Purpose |
|-------------|---------|
| **backend/tests/test_engine_loop.py** | One cycle writes required snapshot keys; keys exist with valid generated_at |
| **backend/tests/test_gates.py** | EmergencyStop / Retract / Freeze precedence; mode gate blocks BACKTEST |
| **backend/tests/test_execution_contract.py** | Engines never call KIS (no kis_executor / requests to KIS in engine modules) |
| **backend/tests/test_combat_force_spec_lock.py** | Core/Swing/Strike I/O and formula lock |
| **backend/tests/test_combat_system_lock.py** | Gate precedence, order state transition, allowed initial status |
| **backend/tests/test_combat_integration.py** | Migration table exists; one cycle + gate PASS + paper order → order_log |

---

## 3. Run checklist (order of execution)

1. **Infrastructure:** `docker ps` → container aegisx-db; `.\scripts\migrate_db.ps1` → success.
2. **DB target:** `python scripts\debug_db_target.py` → success. If fail: `python scripts\migrate_db_via_url.py` then retry.
3. **One cycle:** `python scripts\run_engine_cycle.py` → success.
4. **Snapshot keys:** `python scripts\verify_snapshot_keys.py` → success.
5. **Unit tests:**  
   `pytest backend/tests/test_engine_loop.py backend/tests/test_gates.py backend/tests/test_execution_contract.py backend/tests/test_combat_force_spec_lock.py backend/tests/test_combat_system_lock.py -v`  
   → pass or skip (DB).
6. **Integration:** `pytest backend/tests/test_combat_integration.py -v` → pass or skip.
7. **One-shot:** `.\scripts\validate_phase0_1.ps1` → all steps pass.

**Exact commands (Run Checklist):**
```powershell
cd D:\AEGIS-X_v3
docker ps
.\scripts\migrate_db.ps1
python scripts\debug_db_target.py
python scripts\run_engine_cycle.py
python scripts\verify_snapshot_keys.py
pytest backend/tests/test_engine_loop.py backend/tests/test_gates.py backend/tests/test_execution_contract.py backend/tests/test_combat_force_spec_lock.py backend/tests/test_combat_system_lock.py backend/tests/test_combat_integration.py -v
.\scripts\validate_phase0_1.ps1
```

---

## 4. What is verified

- **P1:** API/UI read only from DB (no direct calculation in API).  
- **P2:** Engines pure (test_execution_contract + test_combat_* scan imports).  
- **P3:** Snapshot writes only via snapshot_repo (single write path tests).  
- **P4:** Gate precedence (test_gates, test_combat_system_lock).  
- **P5:** No KIS in engines (test_execution_contract).
