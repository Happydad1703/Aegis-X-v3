# System Realignment Checklist

**목적**: **docx_md** 참조 문서 기준으로 전체 시스템(DB·엔진·게이트·실행·Dashboard)이 SE 설계대로 정렬되었는지 점검한다.

**참조 소스**: `D:\AEGIS-X_v3\docx_md` — docs의 SE 문서는 해당 폴더를 참조하여 Realign됨.

**실행 시점**: docx_md → docs 동기화 후, 또는 DB/코드 변경 후.

---

## 1. DB 스키마 실라인

| 항목 | SE 근거 | 검증 방법 |
|------|---------|-----------|
| Core 테이블 존재 | **64_Phase0_1_DB_and_MinWorker**, 43_DB_Schema_v1_Core_Spec | `db/migrations/001_init_core.sql`이 docx_md/64·43 DDL과 일치: ext_event_raw, macro_context, engine_result, engine_snapshot, incident_log, command_log, system_mode, system_config, order_log 등 |
| 모든 시간 컬럼 TIMESTAMPTZ(UTC) | docx_md 64 | DDL에서 TIMESTAMPTZ, DEFAULT NOW() 등 사용 확인 |
| JSON 컬럼 JSONB | docx_md 64 | payload, snapshot_data, command_payload, config_value 등 JSONB 사용 확인 |
| 인덱스 | docx_md 64 | (key, generated_at DESC), (source_name, received_at DESC) 등 명세된 인덱스 존재 |

---

## 2. 엔진(engines/) 실라인

| 항목 | SE 근거 | 검증 방법 |
|------|---------|-----------|
| DB 직접 접근 금지 | docx_md 65, DB-First | engines/ 내부에 raw SQL·직접 DB 연결 없음 |
| 입출력 dict only | docx_md 64, 47/48 | 각 엔진: inputs dict → outputs dict, 결과는 snapshot_repo 경유로만 기록 |
| 스냅샷 키 일관성 | docx_md 64 (Snapshot 6종) | engine_heartbeat, health_status, regime_current, allocation_matrix, fleet_budget_snapshot, portfolio_state 등 명세와 일치 |

---

## 3. 게이트(gates/) 실라인

| 항목 | SE 근거 | 검증 방법 |
|------|---------|-----------|
| 통제 로직만 포함 | docx_md 65, 50_Pre_Trade_Gate | gates/는 계산 없이 허용/거부·모드·파일럿·리스크 검사만 |
| Mode/Pilot/Emergency Stop 준수 | docx_md 49_Mode_Execution, 65 | mode_gate, crisis_gate 등에서 모드·비상정지 반영 |

---

## 4. 실행(execution/) 실라인

| 항목 | SE 근거 | 검증 방법 |
|------|---------|-----------|
| 실행 로직만 포함 | docx_md 65, 51_Order_Execution | 주문 실행·브로커 연동만, 엔진/게이트 로직 없음 |
| DB 쓰기 경로 | docx_md 65, DB-First | 주문 결과 등은 core 레이어(command_repo, snapshot_repo, order_log) 경유만 |

---

## 5. Core 레이어 실라인

| 항목 | SE 근거 | 검증 방법 |
|------|---------|-----------|
| 스냅샷 기록 단일 경로 | docx_md 64, 65 | 엔진 결과물은 `core/snapshot_repo.py`를 통해서만 DB 기록 |
| 디렉터리 구조 준수 | docx_md 65_Final_Directory_Architecture_Lock | core/, engines/, gates/, execution/, workers/, api/ 구조 변경 금지 |

---

## 6. API·Dashboard 실라인

| 항목 | SE 근거 | 검증 방법 |
|------|---------|-----------|
| UI 데이터는 DB Snapshot만 | docx_md 17_4 Rules, DB-First | API/Dashboard는 engine_snapshot 등 스냅샷 조회만, engines 직접 호출 없음 |

---

## 7. 체크리스트 실행 순서

1. **docx_md 동기화**: docx_md 수정 시 `docx_md` → `docs/` 복사로 docs 실라인  
2. **DB**: `db/migrations/001_init_core.sql`이 docx_md 64·43 DDL과 일치하는지 확인  
3. **Core**: db.py, snapshot_repo.py, config_service, mode_service 등 65 명세 경계 준수  
4. **Engines**: 입출력 계약 및 snapshot_repo 경유, 64 Snapshot 6종 키 일치  
5. **Gates**: 50_Pre_Trade_Gate, 49_Mode_Execution 반영  
6. **Execution**: 51_Order_Execution, order_log 경유  
7. **API/Health**: 스냅샷 기반 응답만 제공  

이 체크리스트는 **docx_md 참조 Realign** 후 및 코드/DB 변경 후 한 번 이상 수행하고, 항목별 결과를 기록하는 것을 권장한다.
