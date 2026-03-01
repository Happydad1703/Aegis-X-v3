# Test & Evaluation Master Plan (TEMP)

**Document ID:** AEGIS-X-TEMP-v1.0  
**Owner:** Verification & Validation  
**Purpose:** Verification 준비 마무리 — 테스트 수준·실행 순서·합격 기준·TVP 연계를 단일 계획으로 정리.

**참조:** SE-14 (TVP), SOO §7 Execution Checks, Phase0_1_Run_Checklist, Cursor_Guardrails_SE_Enforcement

---

## 1. 목적 및 범위

본 계획은 다음을 정의한다.

- **검증 수준(Level)** — Contract / Unit / Integration / System / Acceptance
- **Phase 0-1 필수 검증** — 3원칙 계약 테스트, 엔진 1사이클 스냅샷 무결성, 진단 스크립트
- **실행 순서 및 환경** — DB·스크립트·pytest 명령
- **TVP(14_Test_Verification_Validation_Plan_TVP) 연계** — RTM·Unit/Integration/System 테스트 ID 매핑
- **진입/완료 기준** — 단계별 통과 조건
- **지속 검증 및 Production Gate** — PR/커밋 체크, 정기 실행 주기

---

## 2. V-Model 및 테스트 수준

| 수준 | 설명 | Phase 0-1 구현 | TVP 섹션 |
|------|------|----------------|----------|
| **Contract** | 아키텍처/3원칙 위반 방지 (DB-Only Read, Engine Purity, Single Write Path) | ✅ 구현됨 | Guardrails |
| **Unit** | 엔진·게이트 단위 순수 함수/로직 | 부분 (engine_loop) | §4 |
| **Integration** | DB·API·외부 연동, 파이프라인 | 스크립트 (check_comm, debug_db) | §5 |
| **System** | 전체 재생·위기 시나리오 | 향후 | §6 |
| **Acceptance** | 인수 조건 충족 | Phase 0-1 체크리스트 | §10 |

---

## 3. Phase 0-1 필수 검증 (현재 준비 완료)

### 3.1 Contract Tests (3원칙 강제)

| 테스트 파일 | 검증 내용 | 위반 시 |
|-------------|-----------|---------|
| `test_contract_api_db_only_read.py` | API가 ext_event_raw/order_log 직접 조회 금지 (DB-Only Read) | 빌드 실패 |
| `test_contract_ui_never_calls_compute.py` | API/UI가 engines import 금지 | 빌드 실패 |
| `test_contract_single_write_path.py` | DB write는 지정 repo 모듈만 (Single Write Path) | 빌드 실패 |
| `test_contract_engines_purity.py` | engines/에서 SQLAlchemy import 금지 (Engine Purity) | 빌드 실패 |

### 3.2 Data Integrity (엔진 1사이클 + 스냅샷)

| 테스트 파일 | 검증 내용 | SOO/TVP |
|-------------|-----------|---------|
| `test_engine_loop.py` | 1사이클 후 engine_snapshot에 필수 6키 존재, generated_at 최근, refresh_rate_sec 존재 | SOO §7, SE-64 |

**필수 Snapshot Key (6종):**  
engine_heartbeat, llm_status, comm_health, regime_current, risk_guard, operation_mode  
— SSOT: `backend/app/core/snapshot_keys.py`

### 3.3 진단 스크립트 (실행 검증)

| 스크립트 | 용도 | 성공 기준 |
|----------|------|-----------|
| `scripts/debug_db_target.py` | Python이 접속하는 DB·engine_snapshot 존재 확인 | current_database=aegisx, to_regclass('public.engine_snapshot') 존재 |
| `scripts/migrate_db.ps1` | DDL 적용 (PowerShell 파이프 방식) | exit 0, `\dt`에 테이블 목록 |
| `scripts/run_engine_worker.ps1` → `run_engine_cycle.py` | 동기 1사이클 실행 | exit 0, engine_snapshot 신규 행 증가 |
| `scripts/check_comm.py` | 외부 API(FRED/LLM/KIS 등) 통신 점검 | OK 또는 SKIP/rate limit, FAIL 시 원인 조사 |

### 3.4 실행 순서 (Phase 0-1 Run)

**문서:** `docs/Phase0_1_Run_Checklist.md`

1. `docker compose up -d`
2. `.\scripts\migrate_db.ps1`
3. `docker exec ... \dt` 로 테이블 확인
4. `python .\scripts\debug_db_target.py`
5. (선택) `.\scripts\run_api.ps1`
6. `.\scripts\run_engine_worker.ps1`
7. `SELECT snapshot_key, generated_at FROM engine_snapshot ...` 로 적재 확인
8. `pytest backend/tests/test_contract_*.py backend/tests/test_engine_loop.py -v` — **전체 통과 필수**

---

## 4. 테스트–요구사항 추적 (RTM 요약)

| Req/원칙 | 테스트 ID / 산출물 |
|----------|---------------------|
| DB-Only Read | test_contract_api_db_only_read, test_contract_ui_never_calls_compute |
| Strict Engine Purity | test_contract_engines_purity, test_contract_ui_never_calls_compute |
| Single Write Path | test_contract_single_write_path |
| SE-64 필수 6키 적재 | test_engine_loop (test_one_cycle_produces_six_snapshot_keys) |
| Health DB-backed | API /api/health 가 DB 조회 기반 (수동 또는 향후 자동화) |
| SOO §7 Execution Checks | debug_db_target, engine 1cycle, contract tests |

---

## 5. 환경 및 전제 조건

- **OS:** Windows 11, PowerShell
- **DB:** PostgreSQL (Docker container `aegisx-db`, port 5433, DB `aegisx`)
- **.env:** `DATABASE_URL=postgresql+psycopg2://...` (필수), `PG_CONTAINER=aegisx-db` (권장)
- **Python:** 프로젝트 루트에서 `pytest` 실행, `backend` 경로 및 의존성 설치됨
- **API Key:** 외부 연동 검증 시 Windows 11 사용자 환경 변수 (check_comm.py 참조)

---

## 6. 단계별 진입/완료 기준

### Phase 0-1 (현재)

| 단계 | 진입 조건 | 완료(Pass) 조건 |
|------|-----------|-----------------|
| 인프라 | docker compose up -d 성공 | aegisx-db healthy |
| DB 스키마 | migrate_db.ps1 실행 | \dt 에 engine_snapshot 등 핵심 테이블 존재 |
| DB 접속 검증 | DATABASE_URL 설정 | debug_db_target.py 0 exit, engine_snapshot regclass 존재 |
| 엔진 1사이클 | run_engine_worker.ps1 실행 | engine_snapshot에 최근 6키 행 존재 |
| Contract | pytest 수집 가능 | test_contract_* + test_engine_loop 전부 PASS |
| PR/커밋 체크 | SOO §PR 단위 | engines 무 DB/네트워크, API/UI 무 계산, snapshot_repo 외 무 write |

### 향후 (TVP §6–§9 연동)

- **Integration:** check_comm.py 전체 OK/SKIP, verify_data_integrity 등 (TVP §5)
- **System:** Full Replay, Crisis Replay, Regime Misclassification (TVP §6)
- **Scaling:** Twin Lab 1×/5×/10× (TVP §7)
- **Self-Healing:** Shock / Structural Drift / Systemic Breakdown (TVP §8)
- **Governance:** Hash chain, Decision logging, LLM Fallback 시뮬레이션 (TVP §9)

---

## 7. 지속 검증 계획 (Continuous Validation)

| 주기 | 항목 | 명령/산출물 |
|------|------|-------------|
| **PR/커밋 시** | Contract + Engine Loop | `pytest backend/tests/test_contract_*.py backend/tests/test_engine_loop.py -v` |
| **로컬 배포 전** | 전체 Run Checklist | Phase0_1_Run_Checklist 1~8 단계 |
| **정기 (향후)** | 외부 연동 | check_comm.py (TVP §5.1) |
| **정기 (향후)** | 데이터 무결성 | verify_data_integrity 등 (TVP §5.2, §11) |

---

## 8. Production Gate 체크리스트 (TVP §12 정합)

Phase 0-1에서 확보한 항목과 향후 확장을 함께 정의.

| Item | Phase 0-1 | 비고 |
|------|-----------|------|
| check_comm OK (또는 SKIP) | ✅ 스크립트 있음 | 외부 키 설정 시 검증 |
| DB target / migration OK | ✅ debug_db_target, migrate_db.ps1 | |
| Engine 1cycle → 6 keys | ✅ test_engine_loop | |
| Contract tests PASS | ✅ test_contract_* 4종 | 3원칙 강제 |
| Health endpoint DB-backed | 수동 확인 권장 | 향후 자동 테스트 추가 |
| Twin PASS | 향후 | TVP §6.1 |
| Risk Engine PASS | 향후 | TVP §4.3 |
| Self-Healing PASS | 향후 | TVP §8 |
| Governance Chain Verified | 향후 | TVP §9 |

---

## 9. 요약 — Verification 준비 완료 상태

- **Contract Tests:** 4개 파일로 3원칙 위반 시 빌드 실패 보장.
- **Data Integrity:** 1사이클 후 6종 스냅샷 키·메타 검증 (test_engine_loop).
- **진단 스크립트:** debug_db_target, migrate_db.ps1, run_engine_worker.ps1, check_comm.py.
- **실행 순서:** Phase0_1_Run_Checklist에 고정, SOO §7과 일치.
- **TVP 연계:** RTM 요약·테스트 수준·진입/완료 기준·Production Gate를 본 TEMP로 정리하여 TVP §1–§12와 정합.

**다음 액션:** PR/커밋 시 contract + engine_loop pytest 필수 실행. 신규 기능 시 RTM 및 필요 시 Unit/Integration 테스트 추가.

---

## 10. 이행 가이드 (How to Execute This Plan)

이 계획을 이행하려면 **Phase 0-1 필수 검증**을 아래 순서대로 실행하면 된다.

### 10.1 전제 조건 (한 번만 확인)

| 확인 항목 | 방법 |
|-----------|------|
| 프로젝트 루트 | `cd D:\AEGIS-X_v3` (또는 실제 프로젝트 경로) |
| .env 존재 | 루트에 `.env` 파일, 내부에 `DATABASE_URL=postgresql+psycopg2://postgres:...@localhost:5433/aegisx` |
| Docker 실행 중 | `docker ps` 에 `aegisx-db` 컨테이너 표시 |
| Python 환경 | `python -c "import sqlalchemy; print('OK')"` → OK |

### 10.2 한 번에 실행 (PowerShell, 프로젝트 루트에서)

```powershell
# 1) DB 기동
docker compose up -d

# 2) 마이그레이션
.\scripts\migrate_db.ps1

# 3) 테이블 확인 (engine_snapshot 등 보여야 함)
docker exec -it aegisx-db psql -U postgres -d aegisx -c "\dt"

# 4) Python이 보는 DB가 aegisx인지 확인 (exit 0, engine_snapshot regclass 출력)
python .\scripts\debug_db_target.py

# 5) 엔진 1회 사이클 실행
.\scripts\run_engine_worker.ps1

# 6) 스냅샷 적재 확인 (6종 키 최근 시각으로 나와야 함)
docker exec -it aegisx-db psql -U postgres -d aegisx -c "SELECT snapshot_key, generated_at FROM engine_snapshot ORDER BY generated_at DESC LIMIT 10;"

# 7) 계약 테스트 + 엔진 루프 테스트 (전부 PASS 여야 TEMP 이행 완료)
pytest backend/tests/test_contract_api_db_only_read.py backend/tests/test_contract_ui_never_calls_compute.py backend/tests/test_contract_single_write_path.py backend/tests/test_contract_engines_purity.py backend/tests/test_engine_loop.py -v
```

### 10.3 단계별 성공 기준

| 단계 | 성공 시 | 실패 시 점검 |
|------|---------|--------------|
| 1 docker compose | `aegisx-db` Up | Docker Desktop 실행, 포트 5433 비어 있는지 |
| 2 migrate_db.ps1 | "Migration complete." | 컨테이너명 `aegisx-db`, .env의 DB_USER/DB_NAME |
| 3 \dt | engine_snapshot, ext_event_raw 등 목록 | 2번 재실행 또는 001_init_core.sql 확인 |
| 4 debug_db_target | [OK] current_database = aegisx, engine_snapshot regclass 있음 | .env DATABASE_URL, 포트 5433 |
| 5 run_engine_worker | [OK] engine cycle done | sqlalchemy 등 패키지 설치, 동일 Python 인터프리터 |
| 6 SELECT | 6종 snapshot_key, generated_at 최근 | 5번 재실행 |
| 7 pytest | 5 passed | 실패한 테스트 이름 확인 → SOO/Guardrails 위반 여부 점검 |

### 10.4 일상 이행 (PR/커밋 시)

- **코드 변경 후:** 위 **7번만** 실행해도 TEMP의 Contract + Data Integrity 검증에 해당한다.  
  `pytest backend/tests/test_contract_*.py backend/tests/test_engine_loop.py -v`
- **DB/인프라 변경 후:** 1~7 전체 실행 (Phase0_1_Run_Checklist).
- **외부 API 연동 확인:** `python scripts/check_comm.py` (선택).

### 10.5 이행 완료 판정

- **Phase 0-1 이행 완료:** 10.2의 1~7 단계가 모두 성공 기준을 만족하고, pytest 5개 전부 PASS.
- **지속 이행:** PR/커밋 시 10.4의 pytest 실행을 필수로 두면 TEMP의 “지속 검증”을 이행하는 것이다.

---

*Ref: 14_Test_Verification_Validation_Plan_TVP.md, Cursor_SOO_Phase0_1.md §7, Phase0_1_Run_Checklist.md, Cursor_Guardrails_SE_Enforcement.md*
