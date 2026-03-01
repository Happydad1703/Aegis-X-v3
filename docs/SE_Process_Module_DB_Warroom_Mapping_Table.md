# Aegis-X v3 — 전체 프로세스 / 모듈 / DB / Warroom CIC 매핑 테이블

**기준**: SE Documentation  
**목적**: 정보획득 → 분석 → 기록 → 전장별 Regime → 군별 자원분배·전략 → Force별 후보군 선정 → Target Lock-on → 교전수칙 수립 → 교전 → 전투결과보고 → 종합분석 → 시스템 튜닝까지의 **프로세스·알고리즘**과 **필요 모듈·DB·Warroom 화면/기능**의 연결고리를 1:1로 정립.

---

## 0. 전체 프로세스 개요 (SE 아키텍처 기준)

```
정보획득 → 분석 → 기록 → 전장별 Regime → 군별 자원·전략 → 후보군 선정 → Target Lock-on
    → 교전수칙(ROE) 수립 → 교전(Execution) → 전투결과보고 → 종합분석(AAR) → 시스템 튜닝
```

| # | 프로세스 단계 | SE 문서 | 데이터 흐름 요약 |
|---|----------------|---------|------------------|
| 1 | 정보획득 | 03_ICD, 04_DDD | External API → Ingest → Ledger/DB |
| 2 | 분석 | 05_Regime, 39_Regime_Math | Raw → Regime/Allocation/Risk 계산 |
| 3 | 기록 | 64_Phase0_1, 23_CIC_DB_Contract | engine_snapshot, ext_event_raw, macro_context |
| 4 | 전장별 Regime | 29_Battlefield, 05_Regime | Battlefield별 regime_state, crisis_prob |
| 5 | 군별 자원·전략 | 31_Force_Org, 36_Allocation_Matrix, 34_FBGC | allocation_matrix, fleet_budget |
| 6 | Force별 후보군 선정 | 07_Fleet_Execution | Universe → Score → Select |
| 7 | Target Lock-on | 07_Fleet_Execution, 50_Pre_Trade_Gate | selected_targets, ROE 적용 |
| 8 | 교전수칙 수립 | 07_Fleet_Execution (ROE), 50_Pre_Trade_Gate | ROE JSON, Gate 통과 |
| 9 | 교전 | 51_Order_Execution, 07_Fleet_Execution | Pre-Trade Gate → Paper/KIS → order_log |
| 10 | 전투결과보고 | 53_AAR, 40_AAR_Learning | battle_report, strategy_log |
| 11 | 종합분석 | 40_AAR_Learning, 53_AAR | TPS/RAS/SES/CES, 파라미터 평가 |
| 12 | 시스템 튜닝 | 09_Meta_Control, 40_AAR_Learning | Strategy State, Bounded Parameter Adjustment |

---

## 1. 상세 매핑 테이블

### 1.1 정보획득 (뉴스/공시/자료)

| 항목 | 내용 |
|------|------|
| **프로세스** | 외부 소스(뉴스·공시·매크로·브로커)에서 데이터 수집, 정규화, DB 적재 |
| **SE 문서** | 03_External_Interface_Control_Document_ICD, 04_Data_Architecture_DDD |
| **모듈** | `workers/ingest_worker.py` (스케줄 기반 수집), `core/env_keys.py` (API Key) |
| **DB 테이블** | `ext_event_raw` (원시 이벤트), `macro_context` (매크로 지표, FRED/ECOS 등) |
| **Snapshot 키** | (직접 없음 — 하류 분석 입력) |
| **Warroom/CIC** | — (수집 상태는 Health/Incident로 간접 표시) |
| **연결고리** | ICD의 Source Inventory·Failure Handling; DDD의 NEWS_EVENT/DART_EVENT/macro_context SSOT |

---

### 1.2 분석 (Regime / Allocation / Risk)

| 항목 | 내용 |
|------|------|
| **프로세스** | 수집 데이터 기반 Regime 점수·전장 가중치·Fleet 예산·리스크 상태 계산 |
| **SE 문서** | 05_Regime_Engine_Spec, 39_Regime_Engine_Mathematical_Spec, 36_Global_Battlefield_Allocation_Matrix, 34_Force_Budget_Growth_Curve_Spec, 35_Strike_Risk_Engine, 50_Pre_Trade_Gate (Risk Gate) |
| **모듈** | `engines/regime_engine.py`, `engines/allocation_engine.py`, `engines/fleet_budget_engine.py` (또는 `capital_scaling.py`), `engines/` 내 Strike/Swing/Core 엔진, `gates/risk_gate.py` |
| **DB 테이블** | (쓰기) 없음 — 엔진은 순수 함수; 결과는 Worker가 `engine_snapshot`에 기록 |
| **Snapshot 키** | `regime_current`, `allocation_matrix`(또는 전장별), `fleet_budget_snapshot`, `risk_guard` |
| **Warroom/CIC** | **Header**: Regime Block, Health Block / **Global Overview**: Regime Card, Allocation Heatmap, Fleet Budget Pie / **Regime Intelligence**, **Allocation Matrix**, **Risk Control** |
| **연결고리** | DB-Only Read: UI는 위 snapshot_key만 조회. Single Write Path: `core/snapshot_repo.py` 경유만 허용 |

---

### 1.3 기록 (Snapshot·로그 적재)

| 항목 | 내용 |
|------|------|
| **프로세스** | 엔진/워커 산출물을 DB에 일관되게 기록; 감사·추적 가능 보장 |
| **SE 문서** | 64_Phase0_1_DB_and_MinWorker_Package_Spec, 23_CIC_DB_Schema_Contract, 18_CIC_Warroom_Spec |
| **모듈** | `core/snapshot_repo.py` (engine_snapshot), `core/incident_repo.py`, `core/command_repo.py`, `workers/engine_worker.py` |
| **DB 테이블** | `engine_snapshot`, `incident_log`, `command_log`, `system_mode`, `system_config` |
| **Snapshot 키** | `engine_heartbeat`, `comm_health`, `regime_current`, `operation_mode`, `llm_status`, `risk_guard` (Phase 0-1 정본 6종) + 확장 시 allocation, fleet_budget, portfolio_state 등 |
| **Warroom/CIC** | 모든 카드/패널 — 표시 데이터는 반드시 `source_name`, `generated_at`, `refresh_rate_sec`, `freshness_status` 메타 포함 (24_CIC_Data_Transparency, 55_Warroom_UI_Spec) |
| **연결고리** | Single Write Path: DB 쓰기는 repo 모듈만. CIC는 engine_snapshot + 로그 테이블만 Read |

---

### 1.4 전장별 Regime 설정

| 항목 | 내용 |
|------|------|
| **프로세스** | Battlefield(예: KOSPI, KOSDAQ, USD/KRW) 단위로 독립 Regime·CrisisProb·Allocation 계산 및 스냅샷 기록 |
| **SE 문서** | 29_Battlefield_Definition_Spec, 05_Regime_Engine_Spec, 36_Global_Battlefield_Allocation_Matrix |
| **모듈** | `engines/regime_engine.py` (전장별 호출 또는 전장 dimension 포함), `workers/engine_worker.py` (전장 루프) |
| **DB 테이블** | `engine_snapshot` (전장별 snapshot_key: 예 `battlefield_KOSPI_status`, `battlefield_KOSDAQ_status`) |
| **Snapshot 키** | `regime_current` (글로벌/집계), `battlefield_{id}_status` (전장별: regime, allocation, risk, crisis_prob, freshness) |
| **Warroom/CIC** | **Header**: 전장별 Regime Badge / **Left Menu**: Battlefield → KOSPI, KOSDAQ, US Proxy, Hedge / **Battlefield Page**: 해당 전장 Regime, SAA Radar, Fleet Targets, Risk Panel, Execution Log (55, 29) |
| **연결고리** | 29의 Battlefield 속성 계약(regime_state, crisis_probability, allocation_weight 등); Retract/E-Stop은 전역·전장 단위 모두 지원 (29 §11) |

---

### 1.5 군별 자원분배 및 전략수립

| 항목 | 내용 |
|------|------|
| **프로세스** | 총자본 → 전장 가중치 → Fleet(Strike/Swing/Core/Reserve) 예산 배분; 전략·ROE 프로필 결정 |
| **SE 문서** | 31_Force_Organization_and_Structure_Spec, 36_Global_Battlefield_Allocation_Matrix, 34_Force_Budget_Growth_Curve_Spec, 09_Meta_Control_Spec |
| **모듈** | `engines/allocation_engine.py`, `engines/fleet_budget_engine.py`, `engines/capital_scaling.py`, (전략 객체) Meta-Control 연동 |
| **DB 테이블** | `engine_snapshot`, (확장 시) `allocation_history`, `system_config` (전략 프로필) |
| **Snapshot 키** | `allocation_matrix`, `fleet_budget_snapshot`, `operation_mode` |
| **Warroom/CIC** | **Allocation Matrix** 패널, **Fleet** 하위 Strike/Swing/Core/Reserve 페이지, **Portfolio Command**, **System Control Panel** (자본·모드 설정) |
| **연결고리** | 36의 4단계( Capital Scale → Battlefield Weights → Fleet Budget → Strike Risk 조정); 31의 JCS→STRATCOM→Battlefield→Fleet 하달 구조 |

---

### 1.6 Force별 후보군 선정

| 항목 | 내용 |
|------|------|
| **프로세스** | Universe Filtering → Candidate Scoring → Top N + Sector/Position 제한으로 Target 후보 선정 |
| **SE 문서** | 07_Fleet_Execution_Spec (§4 Universe, §5 Candidate Scoring, §6 Target Selection) |
| **모듈** | `engines/` 내 Fleet별 엔진(예: `strike_engine.py`, `swing_engine.py`, `core_engine.py`) — Universe·Score·Select 로직; (선택) 전용 `universe_engine.py` |
| **DB 테이블** | `engine_result` 또는 `engine_snapshot` (선정 결과: selected_targets, proposed_weight 등) |
| **Snapshot 키** | (예) `strike_targets`, `swing_targets`, `core_targets` 또는 Fleet 통합 `fleet_target_set` |
| **Warroom/CIC** | **Fleet** 페이지별 “Active Targets”, “후보군/선정 종목” 영역; **Orders & Execution** 전 단계 표시 |
| **연결고리** | 07의 Feature Vector·Score 공식·Selection Rule(Sector ≤35%, Single ≤12%); Decision Object UNIVERSE_DECISION, SCORE_DECISION, TARGET_DECISION (07 §14) |

---

### 1.7 Target Lock-on

| 항목 | 내용 |
|------|------|
| **프로세스** | 선정된 Target에 대해 진입/청산 조건·포지션 사이징 확정; Pre-Trade Gate 입력 준비 |
| **SE 문서** | 07_Fleet_Execution_Spec (§6 Target Selection, §7 ROE), 50_Pre_Trade_Gate_Spec |
| **모듈** | `gates/pre_trade_gate.py`, `gates/mode_gate.py`, `gates/freshness_gate.py`, `gates/risk_gate.py`; ROE는 `system_config` 또는 전용 스키마 |
| **DB 테이블** | `engine_snapshot` (최신 regime/portfolio 스냅샷), `system_config` (ROE 프로필), `order_log` (이후 기록) |
| **Snapshot 키** | `regime_current`, `operation_mode`, (portfolio/risk) `risk_guard` 등 Gate 검사에 필요한 키 |
| **Warroom/CIC** | **Orders & Execution**: “Lock-on” 상태, Gate 통과 여부 / **Risk Control**: Gate 실패 사유 |
| **연결고리** | 50의 3단 Gate(Mode → Freshness → Risk); 07의 ROE JSON Schema(entry, position_sizing, exit) |

---

### 1.8 교전수칙(ROE) 수립

| 항목 | 내용 |
|------|------|
| **프로세스** | Fleet별 ROE(진입 신호·포지션 사이징·손절/목표/시간 스탑) 정의 및 버전 관리; 실행 시 참조 |
| **SE 문서** | 07_Fleet_Execution_Spec (§7 Rules of Engagement), 09_Meta_Control_Spec (Strategy Object) |
| **모듈** | `core/config_service.py` (ROE 프로필 저장/조회), `gates/` (ROE 적용 검증), `execution/` (실행 시 ROE 참조) |
| **DB 테이블** | `system_config` (config_key 예: roe_strike_v1, roe_core_v1), (확장) `engagement_rules` |
| **Snapshot 키** | (선택) `roe_active` — 현재 적용 ROE 요약 |
| **Warroom/CIC** | **Fleet** 페이지 “교전수칙”, **System Control Panel** — ROE 버전/편집 (권한 있을 때) |
| **연결고리** | 07 §7.1 ROE JSON Schema; 07 §7.2 Fleet별 Stop/Holding/Risk 차이 |

---

### 1.9 교전 (Execution)

| 항목 | 내용 |
|------|------|
| **프로세스** | Pre-Trade Gate 통과 주문 → Mode(Backtest/Paper/Pilot/Live)에 따라 Paper 또는 KIS 실행 → 결과 DB 기록 |
| **SE 문서** | 51_Order_Execution_Engine_Spec, 07_Fleet_Execution_Spec (§8 Pre-Trade, §9 Execution), 49_Mode_Execution_Layer_Spec |
| **모듈** | `execution/paper_executor.py`, `execution/kis_executor.py`; `gates/pre_trade_gate.py`; (오케스트레이션) Order Engine 또는 `workers/` 내 실행 루프 |
| **DB 테이블** | `order_log` (symbol, side, quantity, price, mode, execution_status, execution_payload, created_at) |
| **Snapshot 키** | `portfolio_state` (실행 후 포트폴리오 갱신), `operation_mode` |
| **Warroom/CIC** | **Orders & Execution**: 주문 목록, 체결 상태, 모드 표시 / **Footer Ticker**: 최근 체결 요약 |
| **연결고리** | 51의 흐름: Strategy → Order Proposal → Pre-Trade Gate → Order Execution Engine → Paper/KIS → order_log; 49의 BACKTEST/PAPER/PILOT/FULL_LIVE 분기 |

---

### 1.10 전투결과보고 (Battle Report)

| 항목 | 내용 |
|------|------|
| **프로세스** | 포지션 종료 감지 → Battle Report 생성 → battle_report 테이블 및 스냅샷 기록 |
| **SE 문서** | 53_AAR_Automation_Implementation_Spec, 40_AAR_Automated_Learning_Loop_Spec, 07_Fleet_Execution_Spec (§11 AAR) |
| **모듈** | (예) `workers/trade_lifecycle_engine.py` 또는 AAR 전용 워커 — 종료 감지, `create_battle_report`; `core/` 내 report 저장 (repo 패턴) |
| **DB 테이블** | `battle_report` (symbol, fleet, strategy_module, entry_price, exit_price, quantity, pnl_pct, holding_period, regime_at_entry, crisis_prob_at_entry, created_at), `engine_snapshot` (snapshot_key=battle_report 요약) |
| **Snapshot 키** | `battle_report` (최근 N건 요약 또는 집계) |
| **Warroom/CIC** | **AAR & Battle Reports**: 전투 결과 목록, Fleet별 성과, R:R, Regime 적합성 / **Fleet** 페이지 “최근 10개 교전 결과” |
| **연결고리** | 53의 AAR Schema; 40의 battle_report snapshot_data 구조; 07 §11.2 strategy_log + Ledger AAR_EVENT |

---

### 1.11 종합분석 (AAR·성과 분석)

| 항목 | 내용 |
|------|------|
| **프로세스** | Battle Report 수집 → TPS/RAS/SES/CES 등 4계층 점수 계산 → 전략·Regime 정합도·자본 효율 평가 |
| **SE 문서** | 40_AAR_Automated_Learning_Loop_Spec, 53_AAR_Automation_Implementation_Spec |
| **모듈** | AAR 분석 엔진(4계층 점수), (선택) `engines/` 내 순수 함수로 점수 계산; 결과는 repo 경유 DB 기록 |
| **DB 테이블** | `battle_report`, `strategy_log` (또는 engine_result/engine_snapshot에 AAR 집계) |
| **Snapshot 키** | (예) `aar_summary`, `strategy_effectiveness`, `regime_alignment` |
| **Warroom/CIC** | **AAR & Battle Reports**: 종합 점수, Regime Alignment, Strategy Effectiveness / **Global Overview**: AAR Summary 행 |
| **연결고리** | 40의 Layer 1~4 (TPS, RAS, SES, CES); 53의 Bounded Parameter Adjustment 입력 |

---

### 1.12 시스템 튜닝

| 항목 | 내용 |
|------|------|
| **프로세스** | 성과 평가 → 전략 State Machine(SHADOW→CANDIDATE→LIVE→QUARANTINE→RETIRED) 업데이트; 파라미터 Bounded 조정; Fleet Budget·Regime 모델 보정 |
| **SE 문서** | 09_Meta_Control_Spec, 40_AAR_Automated_Learning_Loop_Spec, 06_Allocation_Risk_Learning_Spec |
| **모듈** | Meta-Control 서비스(전략 평가·승격 규칙), AAR Learning 루프(파라미터 조정), `core/config_service.py` (설정 반영) |
| **DB 테이블** | `system_config`, (확장) `strategy_lineage`, `allocation_history`, `engine_snapshot` (튜닝 후 스냅샷) |
| **Snapshot 키** | `operation_mode`, `regime_current`, `allocation_matrix`, `fleet_budget_snapshot` (튜닝 반영 후) |
| **Warroom/CIC** | **System Control Panel**: 전략 버전, Meta Score, 승격/격리 상태 / **Backtest Lab**: 파라미터 시나리오 |
| **연결고리** | 09의 Meta Score·Strategy State Machine·Promotion Rule; 40의 Bounded Parameter Adjustment → Next Engagement 루프 |

---

## 2. DB 테이블 ↔ 프로세스 요약

| DB 테이블 | 주로 사용하는 프로세스 단계 |
|-----------|-----------------------------|
| `ext_event_raw` | 1. 정보획득 |
| `macro_context` | 1. 정보획득, 2. 분석(Regime 입력) |
| `engine_snapshot` | 2. 분석, 3. 기록, 4. 전장별 Regime, 5. 자원·전략, 6. 후보군, 7. Lock-on, 9. 교전, 10. 전투결과, 11. 종합분석, 12. 튜닝 |
| `engine_result` | (선택) 2. 분석 중간 결과, 6. 후보군 산출 |
| `incident_log` | 3. 기록, 9. 교전(실패 시) |
| `command_log` | 3. 기록, 7–9. 제어 명령 |
| `system_mode` | 7. Lock-on, 8. ROE, 9. 교전(Mode Gate) |
| `system_config` | 5. 자원·전략, 8. ROE, 12. 튜닝 |
| `order_log` | 9. 교전 |
| `battle_report` | 10. 전투결과보고, 11. 종합분석, 12. 튜닝 |

---

## 3. Warroom CIC / Dashboard 화면 ↔ Snapshot·기능 연결고리

| 화면/영역 | 주로 참조하는 Snapshot 키 | API/기능 |
|-----------|---------------------------|----------|
| **Header** | `operation_mode`, `regime_current`, `comm_health`, `llm_status`, `engine_heartbeat`, `risk_guard` | GET /api/snapshot/{key}, GET /api/health |
| **Left Menu** | (네비게이션; 클릭 시 해당 페이지 데이터) | — |
| **Global Overview** | `regime_current`, `allocation_matrix`, `fleet_budget_snapshot`, `portfolio_state`, `battle_report` 요약, incident | GET /api/snapshot/latest?key=... |
| **Battlefield (전장)** | `battlefield_{id}_status`, `regime_current` | GET /api/snapshot/{key} |
| **Fleet (Strike/Swing/Core/Reserve)** | `fleet_budget_snapshot`, Fleet별 targets, `battle_report` | GET /api/snapshot/..., (확장) Fleet API |
| **Regime Intelligence** | `regime_current`, 전장별 regime | GET /api/snapshot/regime_current |
| **Allocation Matrix** | `allocation_matrix`, `fleet_budget_snapshot` | GET /api/snapshot/allocation_matrix |
| **Orders & Execution** | `order_log` (API), `operation_mode` | GET /api/orders(확장), GET /api/snapshot/operation_mode |
| **Risk Control** | `risk_guard`, `regime_current`, Gate 실패 incident | GET /api/snapshot/risk_guard, incident feed |
| **AAR & Battle Reports** | `battle_report`, AAR 집계 스냅샷 | GET /api/snapshot/battle_report, (확장) AAR API |
| **System Control Panel** | `system_config`, `operation_mode`, Meta-Control 상태 | POST /api/control/..., GET /api/mode |
| **Footer Ticker** | 최근 order/incident/snapshot 갱신 | 실시간/폴링 (27_CIC_RealTime_Update_Contract) |

---

## 4. 모듈 디렉토리 ↔ 담당 프로세스

| 디렉토리/모듈 | 담당 프로세스 (요약) |
|---------------|----------------------|
| `workers/ingest_worker.py` | 1. 정보획득 |
| `workers/engine_worker.py` | 2. 분석, 3. 기록, 4. 전장별 Regime, 5. 자원·전략 (스냅샷 생산) |
| `engines/regime_engine.py` | 2. 분석, 4. 전장별 Regime |
| `engines/allocation_engine.py` | 2. 분석, 5. 자원분배 |
| `engines/fleet_budget_engine.py`, `capital_scaling.py` | 2. 분석, 5. 군별 자원 |
| `engines/strike_engine.py`, `swing_engine.py`, `core_engine.py` | 2. 분석, 6. 후보군 선정 |
| `gates/pre_trade_gate.py`, `mode_gate.py`, `freshness_gate.py`, `risk_gate.py` | 7. Target Lock-on, 8. ROE 검증, 9. 교전 전 Gate |
| `execution/paper_executor.py`, `kis_executor.py` | 9. 교전 |
| `core/snapshot_repo.py` | 3. 기록 (Single Write Path) |
| `core/incident_repo.py`, `command_repo.py` | 3. 기록, 9. 교전(실패 시) |
| `core/config_service.py`, `mode_service.py` | 5. 전략, 8. ROE, 12. 튜닝 |
| `api/cic.py`, `api/control.py`, `api/health.py` | Warroom Read/Control — 모든 단계의 “보기/명령” 연결고리 |

---

## 5. 연결고리 검증 체크리스트

- [ ] **정보획득 → 분석**: `ext_event_raw` / `macro_context` 조회는 **workers 또는 gates**에서만 수행하고, **engines/** 는 dict in/out만 사용.
- [ ] **분석 → 기록**: 모든 스냅샷 INSERT는 **core/snapshot_repo.py** 경유만.
- [ ] **기록 → Warroom**: Warroom/API는 **GET /api/snapshot/{key}**, **GET /api/health** 등으로만 조회; 계산 로직 없음.
- [ ] **전장별 Regime**: Battlefield 속성 계약(29) 준수; Retract/E-Stop 전장 단위 지원.
- [ ] **교전**: Pre-Trade Gate 3단(Mode → Freshness → Risk) 통과 후에만 **order_log** 기록.
- [ ] **전투결과 → AAR → 튜닝**: `battle_report` → AAR 4계층 점수 → Bounded 조정 → `system_config`/스냅샷 갱신.
- [ ] **표시 메타**: 모든 CIC 패널에 `source_name`, `generated_at`, `refresh_rate_sec`, `freshness_status` 포함 (24, 55).

---

*문서 버전: v1.0 | 기준: SE Documentation (00~65, 07, 09, 18, 23, 29, 31, 34, 36, 39, 40, 44, 45, 50, 51, 53, 55, 64, 65)*
