# Frontend Warroom / CIC Spec

Aegis-X V3 — 6th-gen Cockpit + Warroom. DB-Only Read; no business logic in UI.

---

## 1. Hard locks

- **DB-Only Read**: UI only renders API snapshot/read-only results. No computation of regime, risk, allocation, targets, scores.
- **Single Write Path**: State changes only via Control API (command, mode, E-Stop, Retract). No direct DB write.
- **Safety Priority**: EmergencyStop > Retract > Mode > Strategy. Always visible in CIC Header; control buttons disabled when freshness RED or disconnected.

---

## 2. Tech stack

- Next.js 14 (React) + TypeScript + Tailwind
- Data: TanStack Query (polling 5–10 s)
- State: UI only (filter, tab, sort). SSOT = snapshot from API.
- PWA: manifest.json, theme-color. Optional SW later.

---

## 3. Screen structure

### 3.1 CIC Header Bar (fixed top)

- Mode (Backtest/Paper/Pilot/Live)
- Regime summary (current, confidence, crisis signal)
- Health (comm/db/engine)
- LLM Status (OK / fallback / blackout / LKS)
- Freshness (per key or global)
- E-Stop / Retract (always visible; disabled when RED or disconnected)
- Last Updated (UTC) + connection status (OK / DEGRADED / DISCONNECTED)
- Control: Run Cycle, Retract, E-Stop (or "NOT IMPLEMENTED" if API missing)

### 3.2 Left nav (Warroom panels)

- Warroom Home (Sensor Fusion)
- Regime Intelligence
- Allocation Matrix / Fleet Budget
- Fleet Console (Core/Swing/Strike/Reserve)
- Orders & Execution
- Risk Guard / Incidents
- AAR / Battle Reports
- System Control

### 3.3 Warroom Home — Sensor Fusion

- 6 core snapshot keys (documented):
  - regime_current
  - allocation_matrix
  - fleet_budget_snapshot
  - risk_guard
  - operation_mode
  - engine_heartbeat
- Each card: snapshot_key, generated_at, source_name, refresh_rate_sec, freshness_status.
- Multi-target priority: if snapshot has priority/score/queue fields, display sorted by those (no UI calculation).
- When any snapshot freshness RED: read-only overlay; control blocked; "사령부 승인 필요" message.

### 3.4 Panel pages

- Regime, Allocation, Fleet, Orders, Risk, AAR, System.
- Each: read-only snapshot(s) + Raw JSON viewer (expand/copy for debugging).
- Audit-first: source_name, timestamp, freshness on every card.

---

## 4. Snapshot key list (allowlist)

Aligned with backend `snapshot_keys.py` and Signal_Interface_ICD:

- engine_heartbeat, comm_health, llm_status, operation_mode, regime_current, risk_guard
- allocation_matrix, fleet_budget_snapshot
- core_force_state, swing_force_state, strike_force_state
- targets_core, targets_swing, targets_strike
- active_session, session_state, timezone, usd_exposure_status

No undocumented key. Extension = add key to backend allowlist and use in UI.

---

## 5. API contract (frontend only uses these)

| Method | Path | Purpose |
|--------|------|---------|
| GET | /api/snapshot/{snapshot_key} | Single snapshot |
| GET | /api/snapshot/latest?key=... | Latest by key |
| GET | /api/health | Health payload |
| GET | /api/control/state | E-Stop, Retract state |
| POST | /api/control/command | EMERGENCY_STOP, RETRACT, SET_MODE, RUN_ENGINE_CYCLE |
| GET | /api/orders?limit= | order_log read-only |
| GET | /api/incidents?limit= | incident_log read-only |

If Control API is not implemented: UI shows "Control: NOT IMPLEMENTED" and disables command buttons.

---

## 6. Failure UX

- **Freshness Gate**: RED/STALE → panel read-only overlay; control commands blocked; "사령부 승인 필요" where applicable.
- **Degradation**: DISCONNECTED / DEGRADED badge in header; optional "Execution Freeze 권고" when LLM blackout (from snapshot).
- **Audit-first**: Every major view shows data source (source_name), time (generated_at), freshness (freshness_status).

---

## 7. Component tree (summary)

- `app/layout.tsx` — Providers, CICHeader, LeftNav, main
- `components/CICHeader.tsx` — Mode, Regime, Health, LLM, Freshness, E-Stop, Retract, control buttons
- `components/LeftNav.tsx` — Links to /, /regime, /allocation, /fleet, /orders, /risk, /aar, /system
- `components/SnapshotCard.tsx` — Card with metadata + raw JSON toggle + locked overlay
- `components/Providers.tsx` — QueryClientProvider
- `app/page.tsx` — Warroom Home (6 core snapshots)
- `app/regime/page.tsx` … `app/system/page.tsx` — Panel pages
- `lib/apiClient.ts`, `lib/snapshots.ts`, `lib/health.ts`, `lib/control.ts`, `lib/orders.ts`, `lib/incidents.ts`

---

## 8. Freeze / expansion

- **Freeze**: Current scope = KOSPI/KOSDAQ (or current ops market). Frontend shows whatever snapshot keys backend provides.
- **Expansion**: Same structure; add snapshot keys/fields for S&P (US). No frontend business logic; display only.
