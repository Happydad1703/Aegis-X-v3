# 입력 DB · 프로세싱(모듈/LLM) · 출력 DB · Dashboard 매칭 테이블 (Aegis-X v3)

**목적**: **입력 DB**(테이블/스냅샷) → **프로세싱**(모듈·LLM) → **출력 DB**(테이블·snapshot_key) · **Dashboard**(Warroom CIC 화면)을 1:1로 매칭한다.

**원칙**: DB-First. 모든 표시 데이터는 DB 조회만. Single Write Path로 출력 DB 기록.

---

## 1. 입력 DB → 프로세싱(모듈/LLM) → 출력 DB · Dashboard (종합)

| 입력 DB (테이블 / snapshot_key) | 프로세싱 모듈 | LLM (역할 / Provider) | 출력 DB (테이블 / snapshot_key) | Dashboard (Warroom CIC) |
|--------------------------------|---------------|------------------------|----------------------------------|--------------------------|
| ext_event_raw, macro_context | regime_engine | JCS — OpenAI(국면)·Claude/Gemini(보조) | engine_snapshot · regime_current | Header Regime Block, Regime Intelligence, Global Overview Regime Card |
| ext_event_raw (뉴스) | 뉴스 요약/감성 모듈 | JCS 정보작전 — OpenAI/Gemini | engine_snapshot (news_sentiment 등), Regime 입력 보조 | Regime Intelligence, (확장) 뉴스 요약 패널 |
| regime_current, battlefield 정의 | allocation_engine | 없음 | engine_snapshot · allocation_matrix | Allocation Matrix, Global Overview Heatmap |
| regime_current, allocation_matrix, growth | fleet_budget_engine, capital_scaling | 없음 | engine_snapshot · fleet_budget_snapshot | Fleet Budget Pie, Fleet 페이지, Global Overview |
| regime_current, allocation, portfolio 스냅샷 | risk_gate, risk_engine | 없음 (또는 SRC) | engine_snapshot · risk_guard, incident_log(실패 시) | Risk Control, Header, Global Overview |
| regime_current, allocation | STRATCOM Bias 모듈 | STRATCOM — Claude/Gemini (산업/테마) | engine_snapshot, system_config (strategy_bias 등) | Allocation Matrix, Fleet 페이지 (확장) |
| allocation_matrix, fleet_budget_snapshot, universe | strike_engine, swing_engine, core_engine | Strike — DeepSeek / Swing·Core — 룰 또는 LLM | engine_snapshot · strike_targets, swing_targets, core_targets | Fleet 페이지 (Active Targets), Orders & Execution |
| regime_current, allocation, portfolio, system_mode | pre_trade_gate (mode, freshness, risk) | 없음 | (통과 시) order_log 입력 허용 / incident_log(실패 시) | Orders & Execution, Risk Control |
| order_log, system_mode | paper_executor, kis_executor | 없음 | order_log, engine_snapshot · portfolio_state | Orders & Execution, Footer Ticker |
| order_log (포지션 종료 감지) | trade_lifecycle_engine, AAR 엔진 | J-4 사후강평 — Gemini(선택) | battle_report, engine_snapshot · battle_report | AAR & Battle Reports, Fleet 페이지 (최근 교전) |
| battle_report, 전략 성과 | Meta-Control, AAR Learning | 없음 (또는 전략 요약 LLM) | system_config, engine_snapshot (튜닝 반영) | System Control Panel, Backtest Lab |
| system_mode, command_log | mode_service | 없음 | engine_snapshot · operation_mode (반영) | Header (Operation Mode), System Control Panel |
| (주기 점검) | engine_worker, comm check | 없음 | engine_snapshot · engine_heartbeat, comm_health, llm_status | Header (Health Block), Global Overview |
| (없음 — 최초 수집) | ingest_worker | 없음 | ext_event_raw, macro_context | — (수집 상태는 Incident/Health로 간접) |

---

## 2. DB 테이블별 입·출력 관점

| DB 테이블 | 주로 입력으로 쓰는 프로세싱 | 주로 출력으로 쓰는 프로세싱 |
|-----------|----------------------------|----------------------------|
| **ext_event_raw** | regime_engine, 뉴스 요약/감성 | ingest_worker (외부 수집) |
| **macro_context** | regime_engine | ingest_worker / collectors (확장 시) |
| **engine_snapshot** | allocation_engine, fleet_budget_engine, risk_gate, strike/swing/core_engine, pre_trade_gate, Dashboard 전반 | engine_worker, snapshot_repo (모든 스냅샷 키) |
| **order_log** | trade_lifecycle, AAR, portfolio 집계 | execution (paper_executor, kis_executor) |
| **battle_report** | AAR Learning, Meta-Control, Dashboard AAR | trade_lifecycle_engine, AAR 엔진 |
| **system_mode** | mode_gate, mode_service, engine_worker | api/control, mode_service |
| **system_config** | ROE 적용, 전략 Bias, Meta-Control, Dashboard 설정 | config_service, STRATCOM Bias, AAR Learning |
| **incident_log** | Dashboard Incident Feed | incident_repo, gates, workers |
| **command_log** | 감사·Dashboard 제어 이력 | command_repo, api/control |

---

## 3. Snapshot Key별 입력 · 프로세싱 · 출력 · Dashboard

| snapshot_key (출력) | 입력 DB/스냅샷 | 프로세싱 모듈 | LLM | Dashboard |
|---------------------|----------------|---------------|-----|-----------|
| engine_heartbeat | — | engine_worker | 없음 | Header (Engine Loop Status) |
| comm_health | 외부 API 상태 | engine_worker, comm check | 없음 | Header (DB/KIS/LLM Status) |
| regime_current | ext_event_raw, macro_context | regime_engine | JCS (OpenAI/Claude/Gemini) | Header, Regime Intelligence, Global Overview |
| operation_mode | system_mode, command | mode_service | 없음 | Header (Operation Mode) |
| llm_status | LLM Health Check | llm_gateway (Phase 4) | — | Header (LLM Status) |
| risk_guard | regime_current, portfolio, allocation | risk_gate, risk_engine | 없음 | Header, Risk Control |
| allocation_matrix | regime_current, battlefield | allocation_engine | 없음 | Allocation Matrix, Global Overview |
| fleet_budget_snapshot | regime, allocation, growth | fleet_budget_engine, capital_scaling | 없음 | Fleet Budget Pie, Fleet 페이지 |
| portfolio_state | order_log, KIS 잔고 | execution, portfolio 집계 | 없음 | Global Overview, Fleet 페이지 |
| battle_report | order_log (종료 감지) | AAR 엔진 | J-4 Gemini(선택) | AAR & Battle Reports |
| (확장) strike_targets, swing_targets, core_targets | allocation, universe, 후보 | strike/swing/core_engine | DeepSeek/룰 | Fleet 페이지 (Active Targets) |

---

## 4. Dashboard(Warroom) 화면별 입력 DB · API

| Dashboard 화면/영역 | 주 입력 DB (테이블 / snapshot_key) | API/조회 방식 |
|--------------------|-------------------------------------|---------------|
| **Header** | engine_snapshot (operation_mode, regime_current, comm_health, llm_status, engine_heartbeat, risk_guard) | GET /api/snapshot/{key}, GET /api/health |
| **Global Overview** | engine_snapshot (regime_current, allocation_matrix, fleet_budget_snapshot, portfolio_state, battle_report 요약), incident_log | GET /api/snapshot/latest?key=..., incident feed |
| **Battlefield (전장)** | engine_snapshot (battlefield_{id}_status, regime_current) | GET /api/snapshot/{key} |
| **Fleet (Strike/Swing/Core/Reserve)** | engine_snapshot (fleet_budget_snapshot, strike_targets 등), battle_report | GET /api/snapshot/..., (확장) Fleet API |
| **Regime Intelligence** | engine_snapshot (regime_current, 전장별 regime) | GET /api/snapshot/regime_current |
| **Allocation Matrix** | engine_snapshot (allocation_matrix, fleet_budget_snapshot) | GET /api/snapshot/allocation_matrix |
| **Orders & Execution** | order_log, engine_snapshot (operation_mode) | GET /api/orders(확장), GET /api/snapshot/operation_mode |
| **Risk Control** | engine_snapshot (risk_guard, regime_current), incident_log | GET /api/snapshot/risk_guard, incident feed |
| **AAR & Battle Reports** | battle_report, engine_snapshot (battle_report) | GET /api/snapshot/battle_report, (확장) AAR API |
| **System Control Panel** | system_config, system_mode, engine_snapshot (operation_mode) | POST /api/control/..., GET /api/mode |
| **Footer Ticker** | order_log, incident_log, 최근 스냅샷 갱신 | 실시간/폴링 (27_CIC_RealTime_Update_Contract) |

---

## 5. 파이프라인 요약 (입력 DB → 프로세싱 → 출력 DB → Dashboard)

```
[입력 DB]                    [프로세싱]                    [출력 DB]                 [Dashboard]
─────────────────────────────────────────────────────────────────────────────────────────────
ext_event_raw     →   ingest_worker (수집)           →   ext_event_raw            (간접: Incident/Health)
macro_context          (또는 collectors)

ext_event_raw     →   regime_engine + JCS(LLM)       →   engine_snapshot           Header, Regime Intelligence,
macro_context                                              (regime_current)         Global Overview

regime_current    →   allocation_engine              →   engine_snapshot           Allocation Matrix,
battlefield                                               (allocation_matrix)       Global Overview

regime_current    →   fleet_budget_engine             →   engine_snapshot           Fleet Budget Pie,
allocation, growth                                       (fleet_budget_snapshot)   Fleet 페이지

regime, alloc,    →   risk_gate, risk_engine        →   engine_snapshot           Risk Control, Header
portfolio                                               (risk_guard)

allocation,       →   strike/swing/core_engine      →   engine_snapshot           Fleet (Active Targets)
universe              + DeepSeek(선택)                   (strike_targets 등)

스냅샷 + system_mode → pre_trade_gate               →   (통과 시) order_log      Orders & Execution
                                                          incident_log(실패)

order_log         →   paper/kis_executor            →   order_log                 Orders, Footer
(주문 요청)                                              engine_snapshot(portfolio_state)

order_log         →   trade_lifecycle, AAR + Gemini  →   battle_report             AAR & Battle Reports
(종료 감지)                                              engine_snapshot(battle_report)

battle_report     →   Meta-Control, AAR Learning     →   system_config             System Control Panel
전략 성과                                               engine_snapshot(튜닝 반영)   Backtest Lab
```

---

## 6. 참조 문서

- **외부기관·모듈·LLM·DB 매칭**: `docs/외부기관_모듈_LLM_프로세스결과_DB_매칭테이블.md`
- **프로세스·모듈·Warroom 매핑**: `docs/SE_Process_Module_DB_Warroom_Mapping_Table.md`
- **Warroom UI 명세**: `docs/55_Warroom_CIC_Commercial_UI_Spec.md`, `docs/46_Warroom_Home_Component_Tree.md`
