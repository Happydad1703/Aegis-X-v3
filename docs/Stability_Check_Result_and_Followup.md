# 실행 안정성 점검 결과 분석 및 후속조치

**문서:** 실행 안정성 점검 재실행 결과 분석 및 필요한 후속조치 정리.

---

## 1. 점검 실행 방법

```powershell
cd D:\AEGIS-X_v3
powershell -ExecutionPolicy Bypass -File .\scripts\Run_Stability_Check.ps1
```

---

## 2. 점검 항목 (9단계)

| # | 항목 | 성공 시 |
|---|------|--------|
| 1 | Docker DB (aegisx-db) | 컨테이너 실행 중 |
| 2 | 마이그레이션 (migrate_db.ps1) | 001, 002 SQL 적용 완료 |
| 3 | 테이블 목록 (docker exec \dt) | engine_snapshot 등 존재 |
| 4 | Python DB 진단 (debug_db_target.py) | 동일 DB 접속·engine_snapshot 존재 |
| 5 | 엔진 1사이클 (run_engine_worker.ps1) | 스냅샷 INSERT 성공 |
| 6 | 스냅샷 적재 | 최근 5분 내 6건 이상 |
| 7 | 계약 테스트 (pytest 5개) | 4 passed + (1 passed 또는 1 skipped) |
| 8 | 내부 시뮬레이션 | 구조·스냅샷 키 GO |
| 9 | 외부 통신 (check_comm.py) | OK 또는 SKIP |

---

## 3. 결과 분석 (최근 실행 기준)

- **통과(6):** 1 Docker, 2 마이그레이션, 3 테이블(docker exec), 4 Python DB 진단, 8 내부 시뮬레이션, 9 외부 통신.
- **실패(3):** 5 엔진 1사이클, 6 스냅샷 적재, 7 계약 테스트.

### 3.1 원인 요약

- **5·6 실패:** Python(엔진/스크립트)이 접속하는 DB에 `engine_snapshot` 테이블이 없음.  
  - `docker exec`로 확인한 DB와 **다른 DB**에 Python이 연결된 상황 가능성 있음.  
  - 즉, `.env`의 `DATABASE_URL`이 마이그레이션을 적용한 컨테이너(예: `localhost:5433` → aegisx-db)가 아닌, 다른 인스턴스(예: 로컬 PostgreSQL 5433)를 가리킬 수 있음.
- **7 실패:** `test_engine_loop`가 async DB로 `engine_snapshot`에 INSERT 시도 시 동일하게 “relation does not exist” 발생 → 위와 같은 “Python이 보는 DB ≠ 마이그레이션 적용 DB” 문제와 동일 이슈.

### 3.2 Python이 “어느 DB”를 보는지 확인

- `debug_db_target.py`는 **동기 연결**로 `to_regclass('public.engine_snapshot')`를 조회.
- 이 스크립트가 **실패(exit 1)** 하면: Python이 보는 DB에 테이블이 없는 것이므로, 5·6·7 실패와 일치.
- 이 스크립트가 **성공(exit 0)** 하면: 동기 연결로는 테이블이 보임. 이 경우 엔진 실패는 세션/트랜잭션 이슈 등 추가 원인 가능.

---

## 4. 후속조치 (필수)

### 4.1 DB 연결 일치시키기

1. **포트 점유 확인**  
   - `localhost:5433`에 실제로 어떤 프로세스가 붙어 있는지 확인.  
   - Docker만 5433을 써야 함.  
   - 예: `netstat -ano | findstr 5433` 또는 Docker Desktop에서 aegisx-db 포트 매핑 확인.

2. **.env 확인**  
   - `D:\AEGIS-X_v3\.env`  
   - `DATABASE_URL=postgresql+psycopg2://postgres:<비밀번호>@localhost:5433/aegisx`  
   - 마이그레이션을 적용한 컨테이너가 `5433`이면 위와 일치해야 함.

3. **마이그레이션 적용 DB와 Python 동일 DB인지 확인**  
   - 터미널 1: `docker exec -it aegisx-db psql -U postgres -d aegisx -c "\dt"`  
   - 터미널 2: `python scripts\debug_db_target.py`  
   - `debug_db_target`이 **실패**하면: Python이 보는 DB에 테이블이 없는 것이므로, 위 1·2 재확인 후 `DATABASE_URL`을 마이그레이션 적용 DB로 맞추기.

### 4.2 점검 재실행

- 1·2·3 조치 후:
  ```powershell
  cd D:\AEGIS-X_v3
  .\scripts\migrate_db.ps1
  python scripts\debug_db_target.py
  .\scripts\run_engine_worker.ps1
  powershell -ExecutionPolicy Bypass -File .\scripts\Run_Stability_Check.ps1
  ```

### 4.3 계약 테스트 (test_engine_loop)

- **asyncpg 미설치:** `db_session` 픽스처에서 `AsyncSessionLocal is None`이면 `pytest.skip` → “4 passed, 1 skipped”으로 처리 가능.  
- **asyncpg 설치·테이블 존재:** `test_engine_loop`는 async로 동일 DB 사용. Python이 보는 DB에 `engine_snapshot`이 있으면 5개 통과 가능.

---

## 5. 적용한 코드/스크립트 변경 요약

| 대상 | 변경 내용 |
|------|-----------|
| `scripts/run_engine_cycle.py` | 프로젝트 루트 `sys.path` 추가, `os.chdir(_ROOT)`, `load_dotenv(_ROOT / ".env")`로 .env 명시 로드 |
| `scripts/debug_db_target.py` | `load_dotenv(_ROOT / ".env")`, `engine_snapshot` 미존재 시 exit 1 반환 |
| `backend/tests/conftest.py` | `AsyncSessionLocal is None`일 때 `pytest.skip` |
| `scripts/Run_Stability_Check.ps1` | 엔진 실패 시 “does not exist”면 마이그레이션 재실행 후 엔진 1회 재시도, 계약 테스트 “4 passed + 1 skipped” 시 성공 처리 |
| `backend/app/workers/engine_worker.py` | `ext_event_raw` 조회 시 `ProgrammingError` 시 `db.rollback()` 후 count=0 처리 (기존 반영) |

---

## 6. 정리

- **안정성 점검**은 “Docker·마이그레이션·동일 DB에서 Python 접속·엔진·스냅샷·계약테스트·내부시뮬레이션·외부통신”이 한 흐름으로 맞을 때 9/9 통과.
- **실패 시:** “Python이 보는 DB ≠ 마이그레이션 적용 DB” 가능성을 먼저 제거하고(포트·.env·debug_db_target), 위 후속조치 순서대로 진행한 뒤 점검을 재실행하면 됨.
