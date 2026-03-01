# 프로세스 정합 세부설계 및 점검계획

**목적:** 시스템 프로세스맵 · 프로세스별 알고리즘 · DB · Dashboard & Control · Push to Telegram이 **SE Documentation과 완전히 Align·Sync·통합**되었는지 확인하기 위한 **세부설계**와 **점검계획** 수립.

**참조:** SE_Process_Module_DB_Warroom_Mapping_Table, 입력DB_프로세싱_출력DB_대시보드_매칭테이블, 03_ICD~65_Directory_Lock, 27_CIC_RealTime_Update_Contract, 32_Warroom_IA, 55_Warroom_CIC_Commercial_UI_Spec

---

## Part A. 세부설계 (Alignment 명세)

### A.1 프로세스맵 ↔ 알고리즘 ↔ DB ↔ Dashboard & Control ↔ Push to Telegram (단일 추적 매트릭스)

각 프로세스 단계별로 **알고리즘(모듈)·DB(테이블/스냅샷)·Dashboard 영역·Telegram 용도**를 1:1로 고정한다.

| # | 프로세스 | 알고리즘(모듈) | DB (테이블 / snapshot_key) | Dashboard & Control | Push to Telegram |
|---|----------|----------------|----------------------------|----------------------|-------------------|
| 1 | 정보획득 | ingest_worker | ext_event_raw, macro_context | — (Health/Incident 간접) | Incident 시 L2/L3 알림 (32) |
| 2 | 분석(Regime/Allocation/Risk) | regime_engine, allocation_engine, fleet_budget_engine, risk_gate | engine_snapshot(regime_current, allocation_matrix, fleet_budget_snapshot, risk_guard) | Header Regime/Health, Global Overview, Allocation, Risk Control | Regime RED/CrisisProb 급등 시 L3 (32, 42) |
| 3 | 기록 | engine_worker, snapshot_repo | engine_snapshot(6종+), incident_log, command_log | 모든 카드 (메타: source_name, generated_at, refresh_rate, freshness) | — |
| 4 | 전장별 Regime | regime_engine(전장 dimension) | engine_snapshot(regime_current, battlefield_*_status) | Header, Left Battlefield, Battlefield 페이지 | 전장 Crisis 시 L3 |
| 5 | 군별 자원·전략 | allocation_engine, fleet_budget_engine | engine_snapshot(allocation_matrix, fleet_budget_snapshot), system_config | Allocation Matrix, Fleet 페이지, System Control | — |
| 6 | Force별 후보군 선정 | strike/swing/core_engine | engine_snapshot(strike_targets, swing_targets, core_targets) | Fleet 페이지 Active Targets | — |
| 7 | Target Lock-on | pre_trade_gate, mode_gate, freshness_gate, risk_gate | engine_snapshot(regime_current, risk_guard, operation_mode), system_config | Orders & Execution, Risk Control | Gate 실패 시 L2 |
| 8 | 교전수칙(ROE) | config_service, gates | system_config(roe_*) | Fleet 교전수칙, System Control Panel | — |
| 9 | 교전(Execution) | paper_executor, kis_executor, pre_trade_gate | order_log, engine_snapshot(portfolio_state, operation_mode) | Orders & Execution, Footer Ticker | 체결/실패 요약 (선택 L1/L2) |
| 10 | 전투결과보고 | AAR/trade_lifecycle 워커 | battle_report, engine_snapshot(battle_report) | AAR & Battle Reports, Fleet 최근 교전 | — |
| 11 | 종합분석(AAR) | AAR 분석 엔진 | battle_report, strategy_log, engine_snapshot(aar_summary 등) | AAR & Battle Reports, Global Overview | — |
| 12 | 시스템 튜닝 | Meta-Control, config_service | system_config, engine_snapshot(반영) | System Control Panel, Backtest Lab | — |

**Control 공통:** Emergency Stop / Retract / Freeze / Mode 변경 — **Dashboard(Header)** + **Telegram 명령** 동시 지원, command_log 기록 (32, 42, 49, 59).

---

### A.2 Module Master (프로세스 → 모듈 · 파일 · SE 문서)

| 프로세스(#) | 모듈(역할) | 파일 경로 | SE 문서 |
|-------------|------------|-----------|---------|
| 1 | Ingest | workers/ingest_worker.py | 03_ICD, 04_DDD |
| 2 | Regime | engines/regime_engine.py | 05_Regime, 39_Regime_Math |
| 2 | Allocation | engines/allocation_engine.py | 36_Allocation_Matrix |
| 2 | Fleet Budget | engines/fleet_budget_engine.py | 34_FBGC |
| 2 | Risk | gates/risk_gate.py, (engines) | 50_Pre_Trade_Gate, 35_Strike_Risk |
| 3 | Snapshot 기록 | core/snapshot_repo.py, workers/engine_worker.py | 64_Phase0_1, 23_CIC_DB_Contract |
| 4 | Regime(전장) | engines/regime_engine.py | 29_Battlefield, 05_Regime |
| 5 | Allocation/Budget | engines/allocation_engine.py, fleet_budget_engine.py | 31_Force_Org, 36, 34 |
| 6 | Fleet 후보 | engines/strike_engine, swing_engine, core_engine | 07_Fleet_Execution |
| 7 | Gate | gates/pre_trade_gate, mode_gate, freshness_gate, risk_gate | 50_Pre_Trade_Gate, 07_ROE |
| 8 | ROE/Config | core/config_service.py | 07_Fleet_Execution §7, 09_Meta_Control |
| 9 | Execution | execution/paper_executor, kis_executor | 51_Order_Execution, 49_Mode_Execution |
| 10, 11 | AAR | (AAR 워커/엔진), core/ (report repo) | 53_AAR, 40_AAR_Learning |
| 12 | Meta-Control | core/config_service, (Meta-Control 서비스) | 09_Meta_Control, 40_AAR |
| — | API(CIC) | api/cic.py, api/health.py, api/control.py | 18_CIC_Warroom, 45_API_Contract |
| — | Telegram | (telegram_bot_worker / Bot Service) | 32_Warroom_IA, 41_Execution_Deployment, 42_Roadmap_90D, 49_Mode, 59_Pilot_Checklist |

---

### A.3 Schema Master (DB 테이블 · Snapshot 키 · 계약 · SE 문서)

#### 테이블

| 테이블 | 용도 | 필수 컬럼/계약 | SE 문서 |
|--------|------|----------------|---------|
| ext_event_raw | 원시 이벤트 | source_name, event_type, payload(JSONB), received_at(TIMESTAMPTZ) | 04_DDD, 03_ICD |
| macro_context | 매크로 지표 | source_name, indicator_name, value, observed_at | 04_DDD |
| engine_snapshot | 엔진 결과 | snapshot_key, snapshot_data(JSONB), freshness_status, source_name, refresh_rate_sec, generated_at(TIMESTAMPTZ) | 64, 23, 44_Snapshot_Key_Catalog |
| order_log | 주문/체결 | symbol, side, quantity, mode, execution_status, (created_at) | 51_Order_Execution |
| battle_report | 전투결과 | symbol, fleet, entry/exit, pnl_pct, regime_at_entry, created_at | 53_AAR, 40_AAR |
| incident_log | 사고/알림 | (계약: source, severity, payload, created_at) | 23, 18 |
| command_log | 제어 명령 | (계약: command_type, payload, created_at) | 23, 32 |
| system_mode | 운영 모드 | (계약: mode, capital_cap 등) | 49_Mode_Execution |
| system_config | ROE/전략 설정 | config_key, config_value(JSONB) | 07, 09, 16_Config |

#### Snapshot Key 계약 (Phase 0-1 정본 + 확장)

| snapshot_key | snapshot_data 필수 필드(예) | Dashboard 사용처 | SE 문서 |
|--------------|-----------------------------|------------------|---------|
| engine_heartbeat | status, ts_utc | Header Health | 64, 44 |
| comm_health | status, ts_utc | Header Health | 64 |
| regime_current | regime_label, crisis_probability, trend_score, volatility_state, confidence_score, generated_inputs_hash | Header Regime, Regime Intelligence, Global Overview | 39_Regime_Math |
| operation_mode | mode, ts_utc | Header Mode | 49 |
| llm_status | status, (provider별) | Header LLM | 58, LLM_Staffing |
| risk_guard | status, ts_utc, (상세) | Header, Risk Control | 50 |
| allocation_matrix | (전장·Fleet 가중치) | Allocation Matrix, Global Overview | 36 |
| fleet_budget_snapshot | (Fleet별 예산) | Fleet Budget Pie, Fleet 페이지 | 34 |
| core_force_state | structural_trend_status, trade_signal, core_weight_delta, promotion_list, meta | Core Status, Structural Trend | CoreForce_Structural_Trend_Mapping |
| (확장) strike_targets, swing_targets, core_targets | selected_targets, proposed_weight 등 | Fleet Active Targets | 07 |

---

### A.4 Signal Interface (API · Push · Telegram)

#### API 계약 (Read-Only CIC)

| 메서드 | 경로 | 용도 | 응답 계약 | SE 문서 |
|--------|------|------|-----------|---------|
| GET | /api/health | Health Block | DB 기반(engine_heartbeat, comm_health), source_name, generated_at, freshness | 45_API_Contract |
| GET | /api/snapshot/{key} | 단일 스냅샷 | snapshot_data + source_name, generated_at, refresh_rate_sec, freshness_status | 45, 55 |
| GET | /api/snapshot/latest?key= | 최신 1건 | 동일 | 45 |
| POST | /api/control/* | Mode/Freeze/Retract/E-Stop | command_log 기록, operation_mode 반영 | 32, 49 |

**원칙:** push는 **snapshot_key 변경 이벤트만** 전송, 실제 데이터는 클라이언트가 DB 재조회 (27_CIC_RealTime_Update_Contract).

#### Push (SSE/WebSocket)

| 항목 | 계약 | SE 문서 |
|------|------|---------|
| 전송 내용 | snapshot_key 변경 이벤트만 (페이로드 없음 또는 key 목록) | 27 |
| 데이터 획득 | 클라이언트가 GET /api/snapshot/{key} 또는 /latest?key= 로 재조회 | 27 |
| 목표 | Snapshot 조회 < 200ms, UI 반응 < 500ms | 27 |

#### Telegram (알림 + 제한된 명령)

| 구분 | 내용 | SE 문서 |
|------|------|---------|
| 알림 등급 | L1 Info, L2 Warning(DEGRADED/YELLOW), L3 Critical(RED/Freeze 추천), L4 Systemic(Stop 권고) | 32 §7.2 |
| 트리거 예 | Data Freshness RED 2개+, CrisisProb Δ>0.15/10min, KIS Sync Fail 3회, DD 근접, E-Stop 실행 | 32 §7.3, 42 |
| 명령 | /status, /freeze, /retract (Confirm Code + DB 기록 강제) | 32 §10, 42, 49, 59 |
| Push to Telegram | Incident 생성 시 알림 발송; 전투결과/주문 요약(선택 L1) | 32, 41, 42 |

---

### A.5 UI/UX (Warroom · 필수 Props · Layout)

#### Layout (고정)

| 영역 | 고정 여부 | 내용 | SE 문서 |
|------|-----------|------|---------|
| Header | 고정(스티키) | Operation Mode, Regime Block, Health Block, Emergency Controls | 55 §2 |
| Left Menu | 고정 | Global Overview, Battlefield, Fleet, Regime Intelligence, Allocation Matrix, Portfolio Command, Orders & Execution, Risk Control, AAR & Battle Reports, Backtest Lab, System Control Panel | 55 §3, 46_Warroom_Home_Component_Tree |
| Main Canvas | 스크롤 | 선택된 메뉴별 콘텐츠 | 55 |
| Footer | 고정 | Ticker (위로 스크롤), 최근 알림/체결 | 55 |

#### 카드/패널 필수 Props (DB-First · 실명제)

모든 Warroom 카드/패널은 다음을 **UI 컴포넌트 레직에서 필수 props**로 강제 (SOO §5, 55 §1, 24_CIC_Data_Transparency).

| Prop | 설명 |
|------|------|
| source_name | 실명(데이터 출처) |
| generated_at | UTC + (선택) Local |
| refresh_rate_sec | 갱신 주기 |
| freshness_status | GREEN / YELLOW / RED |

**데이터 소스:** 모든 표시 데이터는 **DB(engine_snapshot 등) 조회만**, API는 계산 없이 스냅샷 반환 (SOO HL-1).

---

## Part B. 점검계획 (Alignment · Sync · 통합 검증)

### B.1 정합성 점검 (Alignment Check)

목적: **프로세스맵 ↔ 알고리즘 ↔ DB ↔ Dashboard ↔ Telegram** 이 1:1로 연결되어 있는지 확인.

| 점검 ID | 점검 항목 | 방법 | 합격 기준 |
|---------|-----------|------|-----------|
| AL-1 | 12단계 프로세스맵에 대해 알고리즘(모듈)·DB·Dashboard·Telegram 항목이 모두 정의되어 있는지 | A.1 매트릭스 대조 | 모든 #1~#12에 5열(알고리즘, DB, Dashboard, Telegram) 기재 |
| AL-2 | 각 모듈이 SE 문서와 매핑되어 있는지 | A.2 Module Master vs SE 목록 | 누락 모듈 없음, SE 문서 번호 일치 |
| AL-3 | 각 DB 테이블·snapshot_key가 SE/계약과 일치하는지 | A.3 Schema Master vs 43/44/64/23 | DDL·snapshot_keys.py·문서 3자 일치 |
| AL-4 | API·Push·Telegram 계약이 SE(27, 32, 45)와 일치하는지 | A.4 vs 27/32/45 | push=이벤트만, Telegram=/status,/freeze,/retract, API read-only |

### B.2 동기화 점검 (Synchronization Check)

목적: **코드·스키마·문서**가 서로 동기화되어 있는지.

| 점검 ID | 점검 항목 | 방법 | 합격 기준 |
|---------|-----------|------|-----------|
| SY-1 | engine_snapshot 필수 컬럼이 DDL·snapshot_repo·API 응답에 동일하게 존재하는지 | db/migrations/001, snapshot_repo, api/cic | snapshot_key, snapshot_data, freshness_status, source_name, refresh_rate_sec, generated_at |
| SY-2 | snapshot_keys.ALLOWED_SNAPSHOT_KEYS와 문서·API 화이트리스트가 일치하는지 | snapshot_keys.py, cic.py, TEMP/SE_Process 매핑 | 6종(Phase 0-1) + 확장 시 문서 반영 |
| SY-3 | Warroom 필수 props가 UI 스펙·SOO·55에 동일하게 정의되어 있는지 | 55, SOO §5, A.5 | source_name, generated_at, refresh_rate_sec, freshness_status |
| SY-4 | Telegram 명령·알림 등급이 32/42/49/59와 일치하는지 | 구현체 vs 32 §7, §10 | /status, /freeze, /retract, L1~L4 정의 |

### B.3 통합 점검 (Integration Check)

목적: **E2E 추적** 및 **계약 테스트**로 설계-구현 일치 확인.

| 점검 ID | 점검 항목 | 방법 | 합격 기준 |
|---------|-----------|------|-----------|
| IN-1 | 데이터 흐름: Ingest → ext_event_raw → (Regime 등) → engine_snapshot → API → UI | E2E 시나리오 또는 단계별 검증 | SOO §2 Data Flow 순서 준수 |
| IN-2 | 3원칙 계약 테스트 통과 | pytest test_contract_* + test_engine_loop | 전부 PASS (TEMP §10) |
| IN-3 | Single Write Path: engine_snapshot 기록이 snapshot_repo 경유만인지 | test_contract_single_write_path, 코드 스캔 | repo 외 INSERT/UPDATE 없음 |
| IN-4 | Dashboard 데이터가 API → DB 조회만으로 얻어지는지 | test_contract_api_db_only_read, UI 코드 검사 | ext_event_raw/order_log 직접 조회 없음 |

### B.4 SE 문서별 점검표 (Document-by-Document Verification)

| SE 문서 | 점검 항목 | 점검 방법 |
|---------|-----------|-----------|
| 03_ICD | 외부 소스·실패 처리 | Module Master A.2 프로세스 1, ingest_worker |
| 04_DDD | ext_event_raw, macro_context 스키마 | Schema Master A.3 vs 001_init_core.sql |
| 05_Regime, 39_Regime_Math | regime_engine 입출력, regime_current 계약 | A.3 regime_current 필드, SE-39 Snapshot Contract |
| 07_Fleet_Execution | Universe·Score·Target·ROE·Execution·AAR | A.2 Fleet/Execution/ROE 행, 50_Pre_Trade_Gate |
| 18_CIC_Warroom, 23_CIC_DB | 스냅샷·로그 테이블·CIC read-only | A.3, SY-1, IN-2 |
| 27_CIC_RealTime_Update | Push=이벤트만, 재조회 | A.4 Push, IN-1 |
| 29_Battlefield | 전장별 regime·allocation | A.1 #4, A.2, A.3 battlefield_* |
| 32_Warroom_IA | Telegram 알림 등급·명령·Confirm | A.4 Telegram, B.2 SY-4 |
| 44_Snapshot_Key_Catalog | snapshot_key 목록·메타 | snapshot_keys.py, A.3 |
| 45_API_Contract | /api/health, /api/snapshot | api/cic.py, api/health.py, A.4 |
| 50_Pre_Trade_Gate | Gate 순서, Wide Stop | A.2 gates, CoreForce_Structural_Trend_Mapping, SE_Complete_Alignment |
| 51_Order_Execution | order_log, execution 경로 | A.3 order_log, execution/ |
| 55_Warroom_CIC_Commercial_UI | Header/Left/Footer, 실명제·메타 | A.5 Layout·필수 Props |
| 64_Phase0_1 | 6종 키, Worker, Single Write Path | A.3, SY-2, IN-2, IN-3 |
| 65_Directory_Lock | 계층별 허용/금지 | Module Master 경로, SE_Complete_Alignment §5 |

### B.5 점검 주기 및 산출물

| 주기 | 점검 항목 | 산출물 |
|------|-----------|--------|
| **PR/커밋** | IN-2, IN-3, IN-4 (계약 테스트) | pytest 결과 |
| **Phase 완료 시** | AL-1~AL-4, SY-1~SY-4 | 정합성·동기화 체크리스트 기입 |
| **배포 전** | B.4 SE 문서별 점검표 전 항목 | Alignment Sign-Off 테이블 (문서·버전·담당·일자) |
| **분기** | 전체 프로세스맵·Module Master·Schema Master·Signal·UI/UX 재검토 | TEMP·본 문서(Process_Alignment_Detailed_Design_and_Check_Plan) 갱신 |

---

## Part C. 요약

- **세부설계(A):** 프로세스맵 → 알고리즘 → DB → Dashboard & Control → Push to Telegram **단일 추적 매트릭스**, **Module Master**, **Schema Master**, **Signal Interface(API·Push·Telegram)**, **UI/UX(Layout·필수 Props)** 를 SE 문서와 함께 정의.
- **점검계획(B):** **정합성(Alignment)** · **동기화(Sync)** · **통합(Integration)** 점검 항목과 **SE 문서별 점검표**, **점검 주기·산출물**을 명시하여, 시스템이 SE Documentation과 완전히 Align·Sync·통합되었는지 확인할 수 있도록 함.

**다음 액션:** 신규 프로세스/모듈/스냅샷/API/UI 추가 시 A.1~A.5 및 snapshot_keys·DDL에 반영 후, B.1~B.4 항목으로 점검 수행.

---

*Ref: SE_Process_Module_DB_Warroom_Mapping_Table.md, 입력DB_프로세싱_출력DB_대시보드_매칭테이블.md, Cursor_SOO_Phase0_1.md, Test_Evaluation_Master_Plan.md, 27_CIC_RealTime_Update_Contract.md, 32_Warroom_IA_and_Navigation_Spec.md, 55_Warroom_CIC_Commercial_UI_Spec.md, SE_Complete_Alignment_Structure_Math_Gate_LLM.md*
