# 실행 안정성 점검 — 개선항목 백로그 및 우선순위

**기준:** 실행 안정성 점검 9항목 + SE-64/Phase0-1/계약 테스트  
**목표:** 시스템 완성(SE Documentation 기반)을 위한 순차 개선

---

## 1. 점검 결과 요약 (최근 실행 기준)

| # | 항목 | 결과 | 비고 |
|---|------|------|------|
| 1 | Docker DB (aegisx-db) | **PASS** | 컨테이너 실행 중 |
| 2 | 마이그레이션 (migrate_db.ps1) | **PASS** | 001, 002 적용 |
| 3 | 테이블 목록 (docker exec \dt) | **PASS** | engine_snapshot 등 존재 |
| 4 | Python DB 대상 진단 | **FAIL** | to_regclass(engine_snapshot)=None (연결 DB 불일치) |
| 5 | 엔진 1사이클 | **FAIL** | 4번과 동일 원인 |
| 6 | 스냅샷 적재 6건 이상 | **FAIL** | 5번 실패로 미적재 |
| 7 | 계약 테스트 5개 | **FAIL** | 동일 DB 이슈 |
| 8 | 내부 시뮬레이션 | **PASS** | 구조·스냅샷 키 GO |
| 9 | 외부 통신 (check_comm) | **FAIL** | OK/SKIP 시 PASS 가능하나 환경·import 이슈 가능 |

**결과:** 4/9 항목 통과. 핵심 블로커: **호스트 localhost:5433이 Docker DB가 아닌 다른 PostgreSQL을 가리킴.**

---

## 2. 개선항목 목록 및 책임개발자 Scoring

| ID | 개선항목 | Criticality (1~5) | Severity (1~5) | Priority | 근거 (SE/문서) |
|----|----------|-------------------|----------------|----------|----------------|
| **I1** | DB 연결 일치(포트 충돌 해결) — 환경 가이드·포트 대안 제공 | **5** | **5** | **P1** | Phase0-1, SE-64: 엔진·스냅샷·계약테스트 전제. 미해결 시 4·5·6·7 항목 영구 실패. |
| **I2** | 외부 통신(check_comm) — 환경미설정 시 SKIP만 있으면 안정성 점검 PASS 처리 | 2 | 2 | **P2** | Stability_Check: "환경변수 미설정 시 SKIP 가능". 의도대로면 9번은 SKIP만으로 통과. |
| **I3** | debug_db_target / 안정성 점검 실패 시 복구 가이드 자동 출력 | 3 | 3 | **P2** | 운영성: 포트 충돌 시 즉시 조치 방법(5434 대안, netstat 등) 안내. |
| **I4** | docker-compose·.env에 포트 변수화(5434 대안) 문서·예시 반영 | 4 | 4 | **P1** | 동일 DB 연결을 위한 선택지 명시. SE-64, Phase0_1_Run_Checklist. |
| **I5** | Phase0-1 스냅샷 6종 생산 검증 (엔진 워커 산출물) | 5 | 4 | **P1** (I1 해결 후) | 64_Phase0_1: engine_heartbeat, health_status, regime_current, allocation_matrix, fleet_budget_snapshot, portfolio_state. |
| **I6** | 계약 테스트 5개 전수 통과 (DB 일치 후 재검증) | 5 | 4 | **P1** (I1 해결 후) | Cursor_Guardrails, Phase0_1: 3원칙 검증. |
| **I7** | asyncpg 등 의존성 명시(requirements.txt) 및 점검 스크립트 안내 | 2 | 2 | **P3** | 이미 requirements에 asyncpg 있음. 필요 시 테스트 전 pip 안내 출력. |
| **I8** | check_comm 실행 시 프로젝트 루트 .env 로드 | 2 | 2 | **P2** | env_keys는 os.environ만 사용; 스크립트 실행 시 .env 로드하면 키 누락 방지. |

**Scoring 기준**
- **Criticality:** 5=시스템 실행/계약의 전제, 1=편의
- **Severity:** 5=전체 점검 실패·데이터 불일치, 1=메시지 개선

---

## 3. 우선순위별 실행 계획

### P1 (즉시 — 시스템 완성의 전제)
1. **I1+I4:** DB 연결 일치를 위한 **포트 대안(5434)** 문서·.env.example·docker-compose 대안 반영, 및 실패 시 복구 가이드 출력 강화.
2. **I5, I6:** I1 해결 후 동일 환경에서 엔진 1사이클·스냅샷 6건·계약 테스트 5개 재점검.

### P2 (단기)
3. **I2:** Run_Stability_Check.ps1 9번 — check_comm 출력에 "OK or SKIP"만 있고 "FAIL" 없으면 PASS 처리.
4. **I3:** debug_db_target.py 및 Run_Stability_Check.ps1 — 실패 시 §3.2 조치(포트 확인, 5434 사용법) 안내 문구 출력.
5. **I8:** check_comm.py에서 프로젝트 루트 .env 로드.

### P3 (유지보수)
6. **I7:** 필요 시 pytest 전 pip install -r requirements.txt 안내.

---

## 4. SE Documentation 매핑

| 문서 | 관련 개선항목 |
|------|----------------|
| SE-64 (DB schema, Snapshot contract) | I1, I4, I5, I6 |
| 64_Phase0_1_DB_and_MinWorker_Package_Spec | I5, 스냅샷 6종 |
| Phase0_1_Run_Checklist | I1, I3, I4 |
| Stability_Check_Report_Unresolvable | I1, I3, I4 |
| Cursor_Guardrails_SE_Enforcement | I6 |

---

## 5. 완료 기준

- **Phase 0-1 완성:** 안정성 점검 9/9 통과, 스냅샷 6종 생산, 계약 테스트 5개 통과.
- **유지:** 포트 충돌 시에도 문서·스크립트만으로 5434 대안 적용 가능.

---

*문서 버전: v1.0 | 책임개발자 Scoring 적용*
