# Signal Interface Master — Schema, DB, 모듈 신호 계약

**목적**: 고도 복잡 시스템에서 **Schema·DB·모듈 간 신호 인터페이스**를 단일 정본으로 관리하여, 인터페이스 불일치로 인한 시스템 폴트를 방지한다.

**기계 판독 정본**: `db/signal_interface_master.json` (버전·테이블·스냅샷 키·모듈 입출력·API·단일 쓰기 경로).

---

## 1. DB 테이블 및 쓰기/읽기 주체

| 테이블 | 용도 | 쓰기 주체 (단일) | 읽기 주체 |
|--------|------|------------------|-----------|
| ext_event_raw | 외부 이벤트 원시 | event_repo (ingest_worker 경유) | engine_worker, regime 입력 |
| engine_snapshot | 엔진 결과 SSOT | **snapshot_repo 만** | CIC API, Warroom, gates, health |
| system_mode | BACKTEST/PAPER/PILOT/FULL_LIVE | command_repo, control API | mode_gate, execution |
| system_config | 설정 키-값 (pilot_config, LKS 등) | config_service, llm_gateway | config_service, llm_gateway, engine_worker |
| incident_log | 사고 로그 | incident_repo, llm_gateway on_blackout | ops, 보고 |
| command_log | 명령 로그 | command_repo, control API | ops, 감사 |
| order_log | 주문 이력 | **order_repo 만** (paper/kis_executor 경유) | ops, 보고 |

- **원칙**: 위 "쓰기 주체" 외 모듈이 해당 테이블에 직접 INSERT/UPDATE 하지 않음. 위반 시 인터페이스 폴트 가능성.

---

## 2. snapshot_key 화이트리스트 및 산출 모듈

| snapshot_key | 산출 모듈 | 용도 |
|--------------|-----------|------|
| engine_heartbeat | engine_worker | 생존 신호 |
| comm_health | engine_worker | 외부 통신 상태 |
| regime_current | regime_engine | 국면 판정 |
| operation_mode | engine_worker | 운영 모드 |
| llm_status | engine_worker | LLM 상태 |
| risk_guard | engine_worker | 리스크 가드 |
| allocation_matrix | allocation_engine | 할당 가중치 |
| fleet_budget_snapshot | fleet_budget_engine | 함대 예산 |
| core_force_state | core_engine | 구조적 추세·트레이드 시그널 |

- API는 위 키만 허용 (`snapshot_keys.is_allowed_snapshot_key`). 신규 키 추가 시 `snapshot_keys.py`와 `db/signal_interface_master.json` 동시 반영.

---

## 3. 모듈 신호 인터페이스 (입력/출력)

| 모듈 | 입력 | 출력 | 쓰기 대상 |
|------|------|------|-----------|
| ingest_worker | 외부 API, heartbeat | event_type, payload | ext_event_raw (event_repo) |
| regime_engine | events_count, trend_score, volatility_state | regime_label, crisis_probability, ... | engine_snapshot.regime_current |
| allocation_engine | regime (dict) | base_weights, regime_label, formula | engine_snapshot.allocation_matrix |
| fleet_budget_engine | allocation, pilot_config | weights, regime_label | engine_snapshot.fleet_budget_snapshot |
| core_engine | regime, battlefield, allocation, fleet_budget, risk_guard, macro, growth | structural_trend_status, trade_signal, ... | engine_snapshot.core_force_state |
| pre_trade_gate | core_force_state, regime_current (snapshot_data) | allow_trade, reasons | 없음 (무상태) |
| engine_worker | ext_event_raw, DB | 전체 스냅샷 키 기록 | engine_snapshot (snapshot_repo), audit_chain |
| cic API | engine_snapshot (read) | GET /api/snapshot/* | 없음 |
| llm_gateway | role, task_type, payload, db | result 또는 LKS | incident_log (blackout), system_config (LKS) |

- **엔진**: 모두 pure dict → dict. DB/HTTP/LLM 직접 호출 금지. 쓰기는 worker가 snapshot_repo로만 수행.

---

## 4. API 엔드포인트와 읽기/쓰기

| 엔드포인트 | 읽기 | 쓰기 | 비고 |
|------------|------|------|------|
| GET /api/snapshot/{key} | engine_snapshot | — | key는 화이트리스트 |
| GET /api/snapshot/latest?key= | engine_snapshot | — | 동일 |
| GET /api/health | engine_snapshot (heartbeat, comm_health) | — | DB 전용 |
| POST /api/control/mode | — | command_log, audit_chain | |
| POST /api/control/freeze | — | command_log, audit_chain | |
| POST /api/control/retract | — | command_log, audit_chain | |
| POST /api/control/emergency_stop | — | command_log, audit_chain | |

---

## 5. 단일 쓰기 경로 (Single Write Path)

- **engine_snapshot**: snapshot_repo 만.
- **ext_event_raw**: event_repo 만.
- **command_log**: command_repo 만.
- **order_log**: order_repo 만.
- **incident_log**: incident_repo (및 llm_gateway on_blackout).

코드/배포 변경 시 위 계약이 깨지지 않도록 검증. (계약 테스트: test_contract_single_write_path 등.)

---

## 6. JSON 정본 사용

- **경로**: `db/signal_interface_master.json`
- **용도**: 자동 검증 스크립트, 신규 모듈 추가 시 계약 확인, 문서 생성.
- **갱신**: 스키마·스냅샷 키·모듈 입출력 변경 시 반드시 이 파일과 본 문서를 함께 수정.

---

*문서 버전: v1.0 | Signal Interface Master — 시스템 폴트 방지*
