# AEGIS-X v3 — Cursor Standard Operating Order (SOP, 1 page)

**Mission:**  
Implement Aegis-X exactly per SE philosophy: DB-First, Snapshot-Driven UI, Always-On, Safe Degradation.

---

## Non-negotiable Rules (Hard Guards)

1. **DB-Only Read**: UI/API/Controllers MUST read only from `engine_snapshot` (and supporting log tables). No direct calculations in UI/API.
2. **Single Write Path**: ANY DB write MUST go through `core/snapshot_repo.py` (or designated repo modules). No raw SQL writes elsewhere.
3. **Strict Module Boundary**: `engines/` MUST be pure functions (dict→dict). No DB session, SQL, HTTP, or LLM calls inside `engines/`.
4. **Safety Priority**: EmergencyStop > Retract > Mode(Backtest/Paper/Pilot/Live) > Strategy/Execution. This priority MUST be explicit in code.
5. All displayed data MUST carry: **real-name source**, **timestamp (UTC and local)**, **refresh_rate** metadata.

---

## Execution Model

- Engine computes and writes snapshots.
- API exposes read-only endpoints: `GET /api/snapshot/{key}`, `GET /api/snapshot/latest?key=...`
- UI renders from snapshots only.

---

## Deliverables Order (DO IN THIS ORDER)

| Phase | Task |
|-------|------|
| **Phase 0** | Infra: ensure Docker Postgres container `aegisx-db` on port 5433. Apply migration via PowerShell pipeline (no `< file.sql`). |
| **Phase 1** | Engine: run one engine cycle and persist required snapshot keys (6 keys minimum). Verify in DB. |
| **Phase 2** | API: implement CIC read-only endpoints returning snapshots only. No compute. |
| **Phase 3** | UI: render Warroom widgets from snapshots, fixed header/left/footer layout, mobile responsive. |
| **Phase 4** | LLM Gateway: multi-provider, health-check, N+1 fallback, blackout mode (Last-Known Strategy). |

---

## Quality Gates (MUST PASS)

- **pytest**: engine loop writes required keys; `generated_at` monotonic; `refresh_rate` present.
- **lint/guard**: `engines/` has no forbidden imports (sqlalchemy, requests/httpx, openai, anthropic, google).
- **guard**: no DB writes outside repo modules.

---

## When Unsure

**Stop and ask for the SE doc reference section** to avoid drift. Do not invent new behavior.

---

*Ref: Chain of Command — DB-Only Read, Single Write Path, Strict Module Boundary. Full lock: docs/Cursor_Developer_Mode_Hard_Lock.md*
