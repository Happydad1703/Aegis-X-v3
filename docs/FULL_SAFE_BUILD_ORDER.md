# AEGIS-X V3 — Full Safe Build Order

## Success Condition

1. All Freeze tests pass.
2. Hash chain verified.
3. Blackout simulation passes.
4. 24h simulation passes.
5. Risk constraints enforced.
6. No architecture violation detected.

Only then system is approved for 24/7 operation.

**Note**: Tests that require DB tables (system_config, engine_snapshot, incident_log, order_log) skip when those tables are missing. After running migrations (`scripts/migrate_db.ps1`), all tests run; skipped tests will pass when DB is fully set up.

---

## PHASE 0 — Precondition Check (Verified)

| Check | Status |
|-------|--------|
| engines/ contain NO SQL | ✓ (no text/execute/SELECT/INSERT in engines/) |
| snapshot_repo is the ONLY write path to engine_snapshot | ✓ (only snapshot_repo inserts; workers call insert_snapshot_sync) |
| Gate order exists and is centralized | ✓ (gate_chain.run_gate_chain, GATE_ORDER) |
| Mode enforcement exists | ✓ (mode_gate: BACKTEST → orders disabled) |

---

## PHASE 1 — Institutional Freeze Hard Lock

### 1. Strict linear Gate priority

Order: **EmergencyStop → Retract → Mode → Risk → Freshness → PreTrade → Strategy**

(Additional checks in chain: LLMBlackout, Session — after Retract, before Mode.)

- **Tests**: `test_gate_chain.py` — EmergencyStop blocks all; Retract blocks; Risk violation blocks; Strategy not evaluated before gates.

### 2. Snapshot SSOT Verification

After 1 engine cycle, required keys: regime_current, allocation_matrix, fleet_budget_snapshot, risk_guard, llm_status, operation_mode, engine_heartbeat.

- **Module**: `core/snapshot_integrity.py` — `check_snapshot_integrity(db)`.
- **Tests**: `test_snapshot_integrity.py`.

### 3. Immutable Hash Chain

- Formula: `current_hash = SHA256(previous_hash + snapshot_json + generated_at)`.
- Genesis: first row uses prev_hash = "genesis".
- Stored: prev_hash, self_hash on engine_snapshot and order_log.
- **Verification**: `scripts/verify_hash_chain.py`, `core/hash_chain_verify.py`.
- **Tests**: `test_hash_chain.py` (formula, verify, tampering detection).

### 4. Self-Healing → Gate Link

- Level 1 → Strike Disable (config: self_healing_strike_disabled).
- Level 2 → Budget × 0.7 (config: self_healing_budget_multiplier).
- Level 3 → EmergencyStop=True (config: gate_emergency_stop_active).
- **Module**: `core/self_healing.py` — `apply_self_healing(db, level)`.
- **Tests**: `test_self_healing.py` — Level 3 sets EmergencyStop; Level 1/2 set config.

### 5. LLM Blackout Simulation

- Fallback: Primary → Secondary → Tertiary → LKS → Execution Freeze.
- Execution Freeze: block_new_orders=True, allow_only_risk_reduction=True.
- **Module**: `core/llm_gateway.py` — on_blackout(db); incident_log.
- **Tests**: `test_llm_blackout.py`.

### 6. MetaScore Lock

- MetaScore = a*Sharpe + b*Expectancy - c*MaxDrawdown.
- a, b, c in system_config (metascore_params).
- **Module**: `core/metascore.py`.
- **Tests**: `test_metascore.py` — deterministic recomputation.

---

## PHASE 2–7 — Timezone, Universe, USD Risk, Session, Snapshot, Capital

- **PHASE 2**: `core/timezone_service.py` — get_current_session(now_utc) → KR | US | OFF; windows in system_config.
- **PHASE 3**: `core/universe_selector.py` — KR/US/OFF → korea/us/empty universe; engines pure dict→dict.
- **PHASE 4**: risk_gate extended with usd_exposure_ratio, fx_volatility; usd_limit, fx_vol_cap from config.
- **PHASE 5**: Session behavior in gate only: KR normal, US × session_multiplier, OFF block.
- **PHASE 6**: Snapshot keys: active_session, session_state, timezone, usd_exposure_status.
- **PHASE 7**: session_allocation.apply_session_multiplier_to_fleet_budget; fleet_budget_engine unchanged.

---

## PHASE 8 — Full 24h Simulation Test

- **Tests**: `test_24h_simulation.py` — KR → US → OFF; session switch updates universe; OFF blocks; snapshot metadata; no SQL in engines; single write path.

---

## Absolute Rules

- No new broker. No multi-account logic. No async refactor.
- No engine algorithm rewrite. No structural DB redesign.
- Windows PowerShell compatible. Preserve Freeze guarantees.
