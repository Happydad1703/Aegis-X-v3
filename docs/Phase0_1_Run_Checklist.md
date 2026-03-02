# Phase 0 & Phase 1 — Run Checklist

**Confirmed runtime baseline:** Container `aegisx-db`, DB `aegisx`, user `postgres`, host port `5433`.  
**.env:** `DATABASE_URL=postgresql+psycopg2://postgres:2041@localhost:5433/aegisx` (override `PG_CONTAINER` if needed).

---

## Phase 0 — Make it Run

### 1. Docker/Postgres + migrations

- **Container name**: `aegisx-db` (default; override via `.env` `PG_CONTAINER`).
- **DB**: `aegisx`, user: `postgres`, host port: `5433`.
- **.env**: `DATABASE_URL=postgresql+psycopg2://postgres:{PW}@localhost:5433/aegisx`
- **Migration**: `scripts/migrate_db.ps1` uses **pipe only** — PowerShell does NOT support `< file.sql`. Uses `Get-Content $sqlPath -Raw | docker exec -i $container psql ...`.

**Acceptance:**

```powershell
# From project root (D:\AEGIS-X_v3)
.\scripts\migrate_db.ps1
# Expected: Exit 0, "Migration complete."

docker exec aegisx-db psql -U postgres -d aegisx -c "\dt"
# Expected: engine_snapshot, ext_event_raw, incident_log, command_log, system_mode, system_config, order_log, etc.
```

### 2. DB target diagnostic (<20 seconds)

```powershell
python scripts/debug_db_target.py
```

**Expected:** Exit 0. Prints `current_database()`, `current_user`, `inet_server_addr()`, `inet_server_port()`, `to_regclass('public.engine_snapshot')`. Non-zero if `engine_snapshot` missing (e.g. wrong DB); script prints recovery steps.

### 3. One-shot validation harness (Phase 0-1)

```powershell
.\scripts\validate_phase0_1.ps1
```

Runs in order: docker ps → migrate_db.ps1 → debug_db_target.py → run_engine_cycle.py → verify_snapshot_keys.py → pytest. Fails fast with clear error messages.

---

## Phase 1 — Minimum Vertical Slice

### 1. One engine cycle

```powershell
.\scripts\run_engine_worker.ps1
```

**Acceptance:** Completes; DB has snapshot rows for at least: `engine_heartbeat`, `comm_health`, `llm_status`, `operation_mode`, `regime_current`, `risk_guard`.

### 2. Read-only API

- `GET /api/snapshot/{snapshot_key}` — latest row for allowed keys only.
- `GET /api/snapshot/latest?key=regime_current` — latest single.

**Acceptance:** API returns JSON from DB (source_name, generated_at, refresh_rate_sec, freshness_status). Missing key → 404 with clear message.

### 3. Warroom UI

- Single page: fixed header (Mode / Regime / Health / E-Stop / Retract), left menu (Overview, Regime, Allocation, Risk, Orders, AAR, System), center panels (snapshot JSON + metadata), footer ticker.
- UI calls API only; API reads DB only.

**Acceptance:** One page renders all 6 snapshots and metadata.

### 4. Tests

```powershell
python -m pytest backend/tests/test_phase1_acceptance.py -v
```

- `test_engine_cycle_inserts_minimum_snapshots` — one cycle → 6 keys in engine_snapshot.
- `test_pre_trade_gate_blocks_on_emergency_stop` — E-Stop → gate blocks.
- `test_api_snapshot_readonly_no_compute` — API response shape (DB-only).

---

## Definition of Done (Phase 1)

- [ ] migrate_db.ps1 runs cleanly
- [ ] run_engine_worker.ps1 produces snapshots
- [ ] API reads snapshots (DB-only)
- [ ] Warroom renders snapshots with metadata
- [ ] Phase 1 acceptance tests pass (or skip when DB unavailable)
