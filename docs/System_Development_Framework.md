# Aegis-X v3 시스템 개발 구도

**목적**: docx_md·TVP(14) 기준으로 **시스템 개발이 가능한지 구도를 설정**하고, 단계별 의존성·산출물·검증을 정의한다.

**참조**: `docx_md` (00~65), `14_Test_Verification_Validation_Plan_TVP.md`, `64_Phase0_1_DB_and_MinWorker_Package_Spec.md`, `65_Final_Directory_Architecture_Lock_Spec.md`

---

## 1. 개발 가능성 구도 (개요)

| 구도 요소 | 상태 | 근거 |
|-----------|------|------|
| 아키텍처 동결 | ✅ 확정 | 65_Final_Directory_Architecture_Lock — backend/app 구조 변경 금지 |
| DB-First·모듈 경계 | ✅ 확정 | 65: engines 무DB, snapshot_repo 단일 경로, Gate→Execution |
| Phase 0-1 명세 | ✅ 확정 | 64: Docker PG, DDL, Engine Worker, Snapshot 6종 |
| 검증 체계 | ✅ 확정 | 14_TVP: V-Model, Unit/Integration/System Test, RTM |
| 구현 동기화 | ✅ 완료 | 내부 시뮬레이션 실행 결과: 구조·DDL·Snapshot 6종·경계 모두 PASS → **GO** |

**결론**: SE 문서를 기준으로 **시스템 개발 구도는 설정 완료**이며, 내부 시뮬레이션으로 **개발 착수 가능(GO)** 이 확인되었다. 최신 결과: [Internal_Simulation_Report.md](./Internal_Simulation_Report.md).

---

## 2. 단계별 개발 구도 (Phase)

### Phase 0-1 (현재 스코프)
- **목표**: DB 기동, DDL 적용, Engine Worker 1회 사이클, **Snapshot 6종** 산출.
- **SE 근거**: 64_Phase0_1_DB_and_MinWorker_Package_Spec.
- **산출물**: `db/migrations/001_init_core.sql`, `backend/app/core/*`, `engines/*`, `workers/engine_worker.py`, `snapshot_repo` 경유 6종 키.
- **완료 조건 (64 Acceptance)**:
  1. DB 재시작 후 데이터 유지
  2. Worker 실행 후 5분 이내 engine_snapshot에 6종 키 생성
  3. health_status가 stale 시 YELLOW/RED 전환
  4. incident_log에 CRITICAL 폭증 없음

### Phase 2 (Go 조건)
- **목표**: Pre-Trade Gate + Pilot Cap + Daily entry gate 연결, Mode enforcement, Order Engine(Paper) 연결.
- **SE 근거**: 49_Mode_Execution_Layer, 50_Pre_Trade_Gate, 51_Order_Execution, 60~61 Pilot Ramp.
- **의존성**: Phase 0-1 완료 후.

### Phase 3 이후
- **목표**: Twin, AAR 자동화, Production Hardening, Warroom/CIC 등.
- **SE 근거**: 08_Digital_Twin, 40/53 AAR, 56_Production_Hardening, 55_Warroom_CIC.

---

## 3. 의존성 순서 (구현 순서)

```
1) 인프라
   docker-compose.yml, .env, db/migrations/001_init_core.sql
   ← 64, 43_DB_Schema

2) core/
   db.py, snapshot_repo.py, incident_repo.py, command_repo.py, mode_service.py, config_service.py
   ← 65

3) engines/
   regime_engine, allocation_engine, fleet_budget_engine, capital_scaling, health_engine, strike_engine, swing_engine, core_engine
   ← 65 (DB I/O 없음, dict in/out)

4) gates/
   pre_trade_gate, cap_gate, risk_gate, freshness_gate, mode_gate, crisis_gate
   ← 65, 50

5) execution/
   paper_executor, kis_executor
   ← 65, 51

6) workers/
   engine_worker (snapshot_repo만 호출), ingest_worker
   ← 64, 47/48

7) api/
   control, cic, health, pilot
   ← 65, DB Snapshot만 조회
```

---

## 4. SE 문서 ↔ 구현 매핑 (개발 시 참조)

| SE 문서 | 구현 대상 | 비고 |
|---------|-----------|------|
| 00_System_Charter | 목표·범위·자동화 수준 | 제약 조건 |
| 01_SRS, 02_SAD | 요구사항·아키텍처 | RTM(14_TVP) 추적 |
| 04_Data_Architecture_DDD | 데이터 흐름, SSOT | engine_snapshot = Warroom SSOT |
| 64_Phase0_1 | DDL, Worker, Snapshot 6종 | Phase 0-1 수용 기준 |
| 65_Final_Directory | backend/app 구조, 모듈 경계 | 절대 변경 금지 |
| 43_DB_Schema_v1_Core | 테이블·컬럼 상세 | 001_init_core.sql 정합 |
| 14_TVP | Unit/Integration/System Test | 테스트 케이스·스크립트 |
| 49, 50, 51 | Mode, Pre-Trade, Order Execution | Phase 2 |

---

## 5. 내부 시뮬레이션 (검증 절차)

개발 착수 전·후 **내부 시뮬레이션**으로 다음을 점검한다.

1. **구조 시뮬레이션**: 65 명세 디렉터리/파일 존재 여부.
2. **DDL 시뮬레이션**: 001_init_core.sql이 64·43 필수 테이블 포함 여부.
3. **스냅샷 시뮬레이션**: engine_worker가 Snapshot 6종(engine_heartbeat, health_status, regime_current, allocation_matrix, fleet_budget_snapshot, portfolio_state) 산출 가능 경로 보유 여부.
4. **경계 시뮬레이션**: engines에 DB/sql 사용 없음, snapshot_repo 단일 경로, gates/execution 분리.

실행: `python scripts/internal_simulation.py`  
결과: 콘솔 요약 + `docs/Internal_Simulation_Report.md` (매 실행 시 갱신).  
최신 실행에서 **Result: GO** 이면 Phase 0-1 개발 착수 가능 상태.

---

## 6. Go/No-Go 판단

| 조건 | 담당 문서 | 판단 |
|------|-----------|------|
| 65 구조 준수 | 65 | 시뮬레이션 1 통과 시 Go |
| DDL 64·43 정합 | 64, 43 | 시뮬레이션 2 통과 시 Go (갭 있으면 DDL 보강 후 Go) |
| Snapshot 6종 경로 확보 | 64 | 시뮬레이션 3 통과 시 Go (미구현 시 engine_worker 확장 후 Go) |
| 모듈 경계 준수 | 65 | 시뮬레이션 4 통과 시 Go |

**전체 Go 시**: Phase 0-1 개발 정식 착수 가능.  
**일부 No-Go**: 해당 항목 보완 후 시뮬레이션 재실행.
