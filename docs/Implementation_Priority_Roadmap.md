# 추진계획 — 우선순위 기반 구현 로드맵

**문서:** 책임개발자 관점 시스템 완성 추진계획  
**기준:** 중요도(Importance) × 긴급도(Urgency) 반영, SE/SOO/TEMP 정합  
**참조:** Cursor_SOO_Phase0_1.md, Test_Evaluation_Master_Plan.md, 64_Phase0_1_DB_and_MinWorker, SE_Process_Module_DB_Warroom_Mapping_Table

---

## 1. 우선순위 기준

### 1.1 중요도 (Importance)

| 수준 | 정의 | 예시 |
|------|------|------|
| **P0 (필수)** | 없으면 시스템 정합성/안전이 깨짐 | 3원칙 준수, DB-First, Single Write Path |
| **P1 (핵심)** | 없으면 데이터 흐름·의사결정 불가 | Snapshot 생산·저장·조회, Regime 판단, Gate 차단 |
| **P2 (중요)** | 없으면 운영·모니터링 불가 | Warroom 표시, Health/Comm 상태, LLM Fallback |
| **P3 (보강)** | 있으면 품질·운영 효율 향상 | AAR, Scaling 검증, Self-Healing, Governance 감사 |

### 1.2 긴급도 (Urgency)

| 수준 | 정의 | 예시 |
|------|------|------|
| **U0 (즉시)** | 이미 지연됐거나 다음 단계 진입 차단 | Contract 테스트 통과, DB/Worker 기동 |
| **U1 (단기)** | 현재 Phase 완료에 필요 | API read-only 완성, 6키 스냅샷 연동 |
| **U2 (중기)** | 파이프라인·UI 가시화에 필요 | Ingest → Regime, Warroom 1차, Gate 연동 |
| **U3 (장기)** | Production·안정화에 필요 | LLM Gateway, Execution 실주문, AAR, TVP System 테스트 |

### 1.3 우선순위 매트릭스 (추진 순서 반영)

- **1순위:** P0 또는 (P1 + U0/U1) — 먼저 착수  
- **2순위:** P1 + U2, P2 + U1 — 단계 완료용  
- **3순위:** P2 + U2/U3, P3 — 품질·확장

---

## 2. 현재 상태 (Phase 0-1 완료 항목)

| 항목 | 상태 | 비고 |
|------|------|------|
| Docker PostgreSQL (aegisx-db, 5433) | ✅ | docker-compose.yml |
| DDL 마이그레이션 (001_init_core.sql) | ✅ | migrate_db.ps1 파이프 방식 |
| core/db.py (동기·비동기) | ✅ | SessionLocal, AsyncSessionLocal |
| core/snapshot_repo (insert_snapshot_sync/async) | ✅ | Single Write Path |
| core/snapshot_keys (6종 SSOT) | ✅ | ALLOWED_SNAPSHOT_KEYS |
| engine_worker 1사이클 (6키 placeholder) | ✅ | run_single_cycle_sync |
| Contract 테스트 4종 + test_engine_loop | ✅ | TEMP §10 이행 |
| API /api/health, CIC snapshot read | ✅ | cic.py, snapshot_key 화이트리스트 |
| env_keys, check_comm.py | ✅ | 외부 API 키·통신 점검 |
| SOO, Guardrails, TEMP, 이행 가이드 | ✅ | 문서 고정 |

---

## 3. 단계별 추진계획

### Phase 0-2 (API·Health 안정화) — **1순위**

목표: API가 DB 기반으로만 응답, Health/스냅샷 조회 검증 완료.

| ID | 작업 | 중요도 | 긴급도 | 산출물 | 완료 조건 |
|----|------|--------|--------|--------|-----------|
| 0-2-1 | /api/health가 engine_heartbeat·comm_health 스냅샷 기반으로 응답 | P1 | U1 | backend/main.py 또는 api/health.py | GET /api/health → DB 조회, 메타 포함 |
| 0-2-2 | GET /api/snapshot/{key}, /api/snapshot/latest?key= 검증 및 Warroom 필수 메타 반환 | P1 | U1 | api/cic.py | source_name, generated_at, refresh_rate_sec, freshness_status |
| 0-2-3 | API 계약 테스트·TEMP 이행 유지 (기존 pytest 통과) | P0 | U0 | - | PR 시 pytest 필수 통과 |

**Phase 0-2 완료 판정:** 위 3항 충족, TEMP §10 7번 pytest 통과 유지.

---

### Phase 1 (파이프라인·Warroom 1차) — **2순위**

목표: Ingest → Regime → 스냅샷 흐름 가동, Warroom에서 6종 스냅샷 가시화.

| ID | 작업 | 중요도 | 긴급도 | 산출물 | 완료 조건 |
|----|------|--------|--------|--------|-----------|
| 1-1 | ingest_worker: 외부 소스 → ext_event_raw 적재 (최소 1개 소스) | P1 | U2 | workers/ingest_worker | FRED 또는 뉴스 RSS 등 1종, ext_event_raw 행 증가 |
| 1-2 | regime_engine: dict in → dict out, regime_current 스냅샷 규격 (SE-39) | P1 | U2 | engines/regime_engine | regime_label, crisis_probability, trend_score 등 snapshot_data 계약 |
| 1-3 | engine_worker가 regime_engine 호출 후 snapshot_repo에 regime_current 기록 | P1 | U2 | workers/engine_worker | 기존 placeholder 대신 실제 regime 산출 연동(또는 단계적 전환) |
| 1-4 | Warroom Home: 6종 스냅샷 카드, 필수 props (source_name, generated_at, refresh_rate, freshness) | P2 | U2 | frontend/ 또는 Warroom 컴포넌트 | SOO §5, TEMP PR 체크 |
| 1-5 | Pre-Trade Gate 골격: structural_trend_status 등 스냅샷 읽어 block_trade 판단 (SE-50) | P1 | U2 | gates/pre_trade_gate | 엔진은 상태만, Gate는 허용/차단 |

**Phase 1 완료 판정:** Ingest 1소스 동작, regime_current 실데이터(또는 시뮬레이션) 스냅샷, Warroom 6종 표시, Pre-Trade Gate 연동.

---

### Phase 2 (전략·리스크·실행 골격) — **2~3순위**

목표: Allocation/Risk/Execution 경로 확보, Core Force·Wide Stop 연동.

| ID | 작업 | 중요도 | 긴급도 | 산출물 | 완료 조건 |
|----|------|--------|--------|--------|-----------|
| 2-1 | allocation_engine·fleet_budget_engine: 입력 dict → 스냅샷 규격 산출 | P1 | U2 | engines/ | allocation_matrix, fleet_budget_snapshot |
| 2-2 | risk_guard 스냅샷: risk_engine 또는 risk_gate 연동 | P1 | U2 | engines/ or gates/ | risk_guard snapshot_data 계약 |
| 2-3 | core_engine: Core Force 교리 (구조추세·Wide Stop) → core_force_state 스냅샷 (CoreForce_Structural_Trend_Mapping) | P1 | U2 | engines/core_engine | snapshot_keys에 core_force_state 추가 |
| 2-4 | Pre-Trade Gate: structural_trend_status == BROKEN 시 block_trade (SE-50) | P1 | U2 | gates/pre_trade_gate | 단위/통합 테스트 |
| 2-5 | execution 골격: paper_executor 주문 → order_log 기록 (Mode Gate 연동) | P1 | U2 | execution/, order_repo | Backtest/Paper 모드에서만 실행 |

**Phase 2 완료 판정:** Allocation/Risk/Core 스냅샷 생산, Wide Stop Gate 동작, Paper 실행 → order_log.

---

### Phase 3 (LLM·안정화·Production 준비) — **3순위**

목표: LLM Mesh, LKS, 지속 검증, TVP 상위 테스트.

| ID | 작업 | 중요도 | 긴급도 | 산출물 | 완료 조건 |
|----|------|--------|--------|--------|-----------|
| 3-1 | llm_gateway: Multi-provider, role 라우팅, Health 기록 (SE-58, LLM_Staffing_Fallback_Plan) | P2 | U3 | intelligence/ or core/ | Primary/Secondary, llm_status 스냅샷 |
| 3-2 | Blackout Ladder: LKS 로드, Execution Freeze, incident_log 기록 | P2 | U3 | llm_gateway, gates | TVP §9.3 LLM Fallback 시뮬레이션 |
| 3-3 | verify_data_integrity, check_comm 정기화 (TEMP §7 지속 검증) | P2 | U3 | scripts/ | TVP §5.1, §5.2 |
| 3-4 | Crisis Replay / Self-Healing 검증 (TVP §6.2, §8) | P3 | U3 | tests/, Twin | 설계 범위 내 DD, Risk Mode·Self-Healing 동작 |
| 3-5 | Governance·Hash chain·Decision logging (TVP §9) | P3 | U3 | core/, audit | tamper test, decision object 생성 |

**Phase 3 완료 판정:** LLM N+1·LKS 동작, 지속 검증 스크립트 정기 실행, TVP System/Governance 항목 진행.

---

## 4. 우선순위 요약 (착수 순서)

| 순서 | Phase / 작업군 | 핵심 항목 |
|------|----------------|-----------|
| 1 | **Phase 0-2** | Health·Snapshot API DB 기반, 계약 테스트 유지 |
| 2 | **Phase 1** | Ingest → Regime → 스냅샷, Warroom 6종, Pre-Trade Gate 골격 |
| 3 | **Phase 2** | Allocation/Risk/Core 스냅샷, Wide Stop, Paper execution → order_log |
| 4 | **Phase 3** | LLM Gateway·LKS, 지속 검증, TVP System·Governance |

---

## 5. 의존성 및 제약

- **모든 Phase:** SOO 3원칙(DB-Only Read, Engine Purity, Single Write Path) 및 Safety Priority 준수. 위반 시 리팩터링 후 진행.
- **Phase 1 이전:** Phase 0-2 완료로 API·Health가 DB 스냅샷만 사용하도록 확정.
- **Phase 2:** Phase 1의 regime_current·Pre-Trade Gate 골격에 의존.
- **Phase 3:** Phase 2의 execution·order_log·스냅샷 흐름에 의존.

---

## 6. 책임개발자 체크포인트

| 시점 | 확인 사항 |
|------|------------|
| **PR/커밋** | pytest (contract + engine_loop) 통과, SOO PR 체크(engines 무 DB/API 무 계산/snapshot_repo 외 무 write) |
| **Phase 0-2 완료** | /api/health·/api/snapshot DB 기반, Warroom 필수 메타 계약 만족 |
| **Phase 1 완료** | TEMP §10 1~7 단계 + Ingest 1소스 + regime_current 실데이터 + Warroom 6종 + Pre-Trade 골격 |
| **Phase 2 완료** | Core Force·Wide Stop 문서 정합, order_log 기록, Allocation/Risk 스냅샷 |
| **Phase 3 진행** | LLM_Staffing 최소 4요구사항, TVP §5~§9 연동 계획 수립 |

---

*Ref: Cursor_SOO_Phase0_1.md, Test_Evaluation_Master_Plan.md, SE_Complete_Alignment_Structure_Math_Gate_LLM.md, 64_Phase0_1_DB_and_MinWorker_Package_Spec.md*
