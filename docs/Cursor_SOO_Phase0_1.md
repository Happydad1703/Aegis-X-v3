# AEGIS-X v3 | CURSOR STANDARD OPERATING ORDER | SE-LOCKED

**Cursor에 붙여넣어 작업 지시로 사용.**  
You are implementing Aegis-X v3 exactly as the SE Documentation philosophy and architecture require.  
You MUST follow the hard locks below. If anything conflicts, STOP and refactor to comply. No exceptions.

---

## 0) ABSOLUTE HARD LOCKS (3 PRINCIPLES + SAFETY ORDER)

**(HL-1) DB-ONLY READ**

- UI and all higher layers MUST read ONLY from DB snapshots (engine_snapshot and other DB tables).
- UI/API MUST NOT compute strategy/indicators directly. No hidden calculations in frontend or API.

**(HL-2) STRICT ENGINE PURITY**

- `/backend/app/engines/*` are PURE functions ONLY: dict_in → dict_out.
- Engines MUST NOT import DB sessions, SQLAlchemy, network clients, filesystem IO, or time-scheduling.
- Any external data required MUST come via input dict produced from DB reads.

**(HL-3) SINGLE WRITE PATH**

- Engine outputs MUST be written to DB ONLY through core/snapshot_repo (single write gateway).
- No other module can write snapshots or "bypass" DB write rules.

**SAFETY PRIORITY ORDER (always enforced):**

EmergencyStop > Retract > Mode(Backtest/Paper/Pilot/Live) > Strategy execution  

- If uncertainty, degradation, or comm failure: choose safety action first.

---

## 1) IDENTITY & OPERATING PRINCIPLES (SE #1)

- Decision System is **Snapshot-based**: all decisions flow via DB snapshots.
- Every panel and metric shown in Warroom MUST display:  
  **real-name(source_name)** + **timestamp(datetime, UTC or explicit TZ)** + **refresh_rate metadata** + **freshness status**
- All external 기관/LLM processing results MUST be recorded to DB.
- All process inputs MUST be fetched from DB; all outputs MUST be written back to DB.

---

## 2) DATA FLOW (INPUT DB → PROCESS → OUTPUT DB → DASHBOARD) (SE #2)

Implement pipeline as:

**A) Ingest**

- External APIs (FRED/ECOS/DART/NEWS/KIS/others) → workers/ingest_worker
- Persist raw events to ext_event_raw (+ optional macro_context table if used)

**B) Regime & Strategy**

- Read ext_event_raw/macro_context → engines/regime_engine + JCS LLM
- Write engine_snapshot(regime_current) (+ comm_health, llm_status, incident_log as needed)

**C) Allocation/Budget**

- Read regime_current + battlefield snapshot → engines/allocation_engine, engines/fleet_budget_engine
- Write allocation_matrix, fleet_budget_snapshot

**D) Risk**

- Read regime + allocation + portfolio_state → gates/pre_trade_gate + gates/risk_gate + risk_engine
- Write risk_guard + incident_log

**E) Targets/Engagement/Execution**

- Read allocation + universe → engines/strike/swing/core_engine (+ LLM support as configured)
- Write targets + order_log + portfolio_state
- execution/ handles paper_executor or kis_executor based on operation mode gates

**F) AAR & Tuning**

- Read order_log (closed) → AAR engine (+ LLM) → write battle_report
- Tuning/meta-control reads battle_report → write system_config updates (DB-first)

---

## 3) MODULE STRUCTURE (SE-65) (SE #3)

Follow this exact boundary:

| 계층 | 역할 |
|------|------|
| **core/** | db, snapshot_repo, incident_repo, command_repo, mode_service, config_service, env_keys |
| **engines/** | regime, allocation, fleet_budget, strike, swing, core_engine — **PURE dict→dict ONLY** |
| **gates/** | pre_trade_gate, mode_gate, freshness_gate, risk_gate — policy enforcement; minimal compute |
| **execution/** | paper_executor, kis_executor — side effects allowed; must log |
| **workers/** | ingest_worker (collect), engine_worker (produce snapshots) |
| **api/** | cic (snapshot read-only), control, health |

---

## 4) DB & SNAPSHOT RULES (SE #4)

DB is the system-of-record. Implement/maintain tables:

- **Input:** ext_event_raw (+ macro_context if used)
- **Core Output:** engine_snapshot keys including:  
  regime_current, allocation_matrix, fleet_budget_snapshot, risk_guard,  
  operation_mode, llm_status, engine_heartbeat, comm_health
- **Audit/Control:** order_log, battle_report, incident_log, command_log, system_mode, system_config

**Snapshot contract**

- Every snapshot row must include: snapshot_key, snapshot_data(JSONB), freshness_status, source_name, refresh_rate_sec, generated_at(TIMESTAMPTZ).
- Dashboard/API reads snapshots only. Any "latest state" is derived by DB query ordering by generated_at.

---

## 5) WARROOM CIC / DASHBOARD REQUIREMENTS (SE #5)

UI is a commercial-grade web dashboard (responsive + mobile + fullscreen).

**Layout**

- Header / LeftMenu / Footer fixed (sticky). Center is workspace (monitoring/results).
- Footer ticker: critical news/disclosure/alerts flow bottom-to-top.

**Header MUST show**

- Mode buttons (Backtest / Paper / Pilot / FullLive)
- Regime (Goldilocks / steady / tapering / crisis)
- Health (comm + engine + DB)
- LLM status
- Emergency Stop + Retract buttons
- All fields must show (source_name, timestamp, refresh_rate, freshness).

All Warroom data MUST come from DB. No direct calls from UI to external sources.

---

## 6) LLM STAFFING + N+1 FALLBACK (IMPLEMENTATION RULE)

Implement an LLM Gateway with provider list + health check + degradation:

- Each role has Primary + Secondary. If Primary fails/slow, auto-fallback.
- If all LLMs fail (blackout): enter **LKS (Last-Known Strategy)** + **Execution Freeze** (safety).
- Strike force failure ⇒ emergency exit rules (capital preservation bias).

---

## 7) EXECUTION CHECKS (MANDATORY)

- Provide scripts to verify DB target and snapshot existence (fast diagnostics).
- Provide tests:
  - After one engine cycle, DB must contain required snapshot keys (≥6 core keys).
  - Health endpoints must return DB-backed status, not computed guesses.
- **Run order (Windows/PowerShell):** See `docs/Phase0_1_Run_Checklist.md` for exact steps (docker → migrate_db.ps1 → debug_db_target.py → run_engine_worker.ps1 → pytest contract tests).

---

## 8) CODING RULES

- Never introduce new write paths to DB other than snapshot_repo / incident_repo / command_repo / order_repo.
- Never compute regime/indicators in API/UI.
- If you need additional data, add ingest persistence + snapshot production.
- Always log side effects: orders, commands, incidents.
- Prefer explicit names, deterministic outputs, idempotent workers.

---

## 선언 (Declaration)

**"위 SOO를 절대 규칙으로 두고, 위반되는 기존 코드가 있으면 리팩터링으로만 해결"**

---

## PR/커밋 단위 체크

- **engines/** 에 DB/네트워크 import가 생기면 → **즉시 롤백**
- **API/UI** 에서 계산 로직이 생기면 → **즉시 롤백**
- **snapshot_repo 외** DB write가 생기면 → **즉시 롤백**
- **Warroom** 화면의 모든 카드/패널에는 **(source_name, generated_at, refresh_rate_sec, freshness_status)** 를 UI 컴포넌트 레벨에서 **"필수 props"** 로 강제한다.

---

[END OF ORDER]

*Ref: Cursor_Guardrails_SE_Enforcement.md, Cursor_Developer_Mode_Hard_Lock.md, SE_Complete_Alignment_Structure_Math_Gate_LLM.md, LLM_Staffing_Fallback_Plan.md*
