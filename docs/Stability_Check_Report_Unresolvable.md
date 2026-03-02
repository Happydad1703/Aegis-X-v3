# 실행 안정성 점검 — 재실행 결과 및 자체 해결 불가 사항 보고

**일시:** 점검 재실행 기준  
**결과:** 5/9 항목 통과

---

## 1. 재실행 결과 요약

| # | 항목 | 결과 | 비고 |
|---|------|------|------|
| 1 | Docker DB (aegisx-db) | **PASS** | 컨테이너 실행 중 |
| 2 | 마이그레이션 (migrate_db.ps1) | **PASS** | 001, 002 적용 완료 |
| 3 | 테이블 목록 (docker exec \dt) | **PASS** | 컨테이너 내부에서 engine_snapshot 등 존재 |
| 4 | Python DB 대상 진단 | **FAIL** | 아래 §2 참조 |
| 5 | 엔진 1사이클 | **FAIL** | 4번과 동일 원인 |
| 6 | 스냅샷 적재 6건 이상 | **FAIL** | 5번 실패로 미적재 |
| 7 | 계약 테스트 5개 | **FAIL** | 동일 DB 이슈 |
| 8 | 내부 시뮬레이션 | **PASS** | 구조·스냅샷 키 GO |
| 9 | 외부 통신 (check_comm) | **PASS** | OK/SKIP |

---

## 2. 진단 출력으로 확인된 사실

**Step 4 (debug_db_target.py) 출력:**
- `DATABASE_URL = postgresql+psycopg2://postgres:2041@localhost:5433/aegisx`
- `current_database/current_user/server_addr/server_port = ('aegisx', 'postgres', '::1', 5433)`
- **`to_regclass(public.engine_snapshot) = None`**

의미:
- Python은 **localhost:5433**, DB명 **aegisx**, 사용자 **postgres**로 접속함.
- 해당 DB에는 **`engine_snapshot` 테이블이 없음** (to_regclass = None).
- 한편 **docker exec**로 컨테이너 안에서 `\dt`를 실행하면 **engine_snapshot 등 테이블이 존재**함.

따라서:
- **컨테이너 내부 DB** = 마이그레이션 적용됨 → 테이블 있음.
- **호스트에서 localhost:5433으로 접속했을 때의 DB** = 테이블 없음 → **컨테이너가 아닌 다른 PostgreSQL 인스턴스**임.

---

## 3. 자체 해결이 어려운 문제 (환경 조치 필요)

### 3.1 문제: **호스트 포트 5433 충돌**

- **현상:** 호스트의 **localhost:5433**에 Docker 컨테이너가 아닌 **다른 PostgreSQL**이 붙어 있음.
- **결과:** 마이그레이션은 컨테이너 DB에 적용되지만, Python/엔진/테스트는 호스트 5433(다른 인스턴스)에 연결되어 `engine_snapshot`이 없음.
- **코드/스크립트만으로는 해결 불가:** 어떤 프로세스가 5433을 쓸지, Docker와 로컬 중 어느 쪽을 쓸지는 환경 설정 문제이므로, 시스템이 스스로 “올바른 쪽”을 고를 수 없음.

### 3.2 필요한 조치 (운용자/관리자)

다음 중 하나를 선택해 **환경을 정리**해야 함.

| 조치 | 설명 |
|------|------|
| **A. 로컬 PostgreSQL 중지 또는 포트 변경** | 호스트에 설치된 PostgreSQL이 5433을 쓰고 있다면, 해당 서비스를 중지하거나 다른 포트(예: 5432)로 옮긴 뒤, Docker만 5433을 쓰도록 함. |
| **B. Docker가 5433을 쓰도록 확인** | `docker compose up -d` 후 `docker port aegisx-db`로 5433이 컨테이너에 매핑되는지 확인. 이미 다른 프로세스가 5433을 점유 중이면 Docker는 5433에 바인드되지 않을 수 있음. |
| **C. 포트를 나누어 사용** | 로컬 PostgreSQL을 5433에 유지할 경우, **`docker-compose.5434.yml`** 사용: `docker compose -f docker-compose.yml -f docker-compose.5434.yml up -d` 후 `.env`의 `DATABASE_URL`·`ASYNC_DATABASE_URL`을 `localhost:5434`로 수정. 그러면 Python은 컨테이너(5434)만 바라보게 됨. (`.env.example`에 주석으로 안내됨.) |

**확인 방법 (PowerShell):**
```powershell
# 5433 포트 사용 프로세스 확인
netstat -ano | findstr 5433

# Docker 컨테이너 포트 매핑 확인
docker port aegisx-db
```

---

## 4. 시스템이 수행한/수행 가능한 조치

| 구분 | 내용 |
|------|------|
| **이미 적용된 것** | run_engine_cycle/debug_db_target의 프로젝트 루트 .env 명시 로드, 엔진 실패 시 마이그레이션 재실행 후 1회 재시도, debug_db_target에서 테이블 없으면 FAIL 반환, conftest에서 AsyncSessionLocal 없을 때 스킵. |
| **한계** | **어느 PostgreSQL 인스턴스가 5433에 붙을지**는 호스트 환경에 의해 결정되므로, 스크립트만으로 “Docker 쪽에만 연결”하도록 강제할 수 없음. |

---

## 5. 결론 및 다음 단계

- **자체 해결 불가:** **호스트 localhost:5433이 Docker 컨테이너가 아닌 다른 PostgreSQL을 가리키는 포트 충돌**.
- **필수 후속:** §3.2의 A/B/C 중 하나를 적용한 뒤, 아래 순서로 재점검.

```powershell
cd D:\AEGIS-X_v3
.\scripts\migrate_db.ps1
python scripts\debug_db_target.py    # [OK] to_regclass(...) = public.engine_snapshot 이어야 함
.\scripts\run_engine_worker.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\Run_Stability_Check.ps1
```

- **기대:** 5433이 Docker 컨테이너만 가리키도록 정리되면 4·5·6·7번이 통과하고, **9/9**까지 갈 수 있음.
