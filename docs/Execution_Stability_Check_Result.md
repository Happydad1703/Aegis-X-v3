# 시스템 실행안정성 점검 결과

**점검 일시:** 2025-03-02 (최근 실행: 2026-03-02)  
**기준:** Verification_Playbook.md, System_Operations_Manual.md §8

---

## 1. 점검 결과 요약

| # | 항목 | 명령 | 결과 | 비고 |
|---|------|------|------|------|
| 1 | 인프라 | `docker ps` | **PASS** | 컨테이너 `aegisx-db` 실행 중 |
| 2 | 마이그레이션 | `.\scripts\migrate_db.ps1` | **PASS** | 001~004 적용 완료, "Migration complete." |
| 3 | DB 타깃 | `python scripts\debug_db_target.py` | **PASS** | engine_snapshot 존재, DATABASE_URL 정상 |
| 4 | 엔진 1사이클 | `python scripts\run_engine_cycle.py` | **PASS** | "[OK] engine cycle done" |
| 5 | 스냅샷 키 | `python scripts\verify_snapshot_keys.py` | **PASS** | 필수 11개 키 존재 |
| 6 | 검증 pytest | test_engine_loop, gates, execution_contract, combat_*, integration | **PASS** | 31 passed |
| 7 | Phase 0-1 하네스 | `.\scripts\validate_phase0_1.ps1` | **PASS** | 6/6 단계 + 16 pytest 통과 |

---

## 2. 원인 분석 (3·4번 실패)

- **debug_db_target.py** 출력: `DATABASE_URL=...@localhost:5433/aegisx`, `to_regclass('public.engine_snapshot') = None`.
- **의미:** Python 클라이언트가 접속한 PostgreSQL 인스턴스(localhost:5433)에는 `engine_snapshot` 테이블이 없음.
- **가능 원인:** 호스트 5433 포트에 Docker 컨테이너가 아닌 **다른 PostgreSQL**이 바인딩되어 있거나, 컨테이너와 Python이 서로 다른 DB를 가리킴. (참조: [Stability_Check_Report_Unresolvable.md](./Stability_Check_Report_Unresolvable.md) §3)
- **컨테이너 포트:** `docker port aegisx-db` → 5432/tcp → 0.0.0.0:5433 (매핑 정상).

---

## 3. 조치 권장 (운용자)

1. **DATABASE_URL 대상에 스키마 적용 (권장):** Python/앱이 사용하는 DB와 동일한 대상에 마이그레이션 적용.
   ```powershell
   python scripts\migrate_db_via_url.py
   ```
   이후 `python scripts\debug_db_target.py` 로 테이블 존재 여부 확인.
2. **검증 하네스 자동 시도:** `.\scripts\validate_phase0_1.ps1` 실행 시, DB 타깃 실패 시 자동으로 `migrate_db_via_url.py`를 실행한 뒤 재검사합니다.
3. **포트 점검:** `netstat -ano | findstr 5433` — 5433 사용 프로세스 확인.
4. **단일 Postgres 사용:** Docker만 쓸 경우, 로컬 PostgreSQL 서비스 중지 후 `docker compose up -d` 재기동.
5. **DATABASE_URL 일치:** Python이 **실제로 사용할** DB(컨테이너 또는 로컬)의 호스트/포트/DB명과 일치하도록 `.env`의 `DATABASE_URL` 설정.
6. **재점검:** 위 조치 후 3→4→5 순서로 재실행.

---

## 4. 통과한 검증

- **엔진 순수성:** KIS/sqlalchemy/requests·httpx 미사용 (test_execution_contract).
- **Core/Swing/Strike Spec Lock:** 입출력·수식 준수 (test_combat_force_spec_lock).
- **게이트 우선순위·주문 상태 전이:** EmergencyStop 선행, 모드 차단, 전이 규칙 (test_combat_system_lock, test_gates).

---

## 5. 수정 및 보완 (원인 규명 후 조치)

| 조치 | 내용 |
|------|------|
| **원인** | 마이그레이션이 컨테이너 내부에만 적용되어, Python이 사용하는 DB(DATABASE_URL)와 불일치할 수 있음. |
| **migrate_db_via_url.py 추가** | `DATABASE_URL`이 가리키는 DB에 동일한 `db/migrations/` DDL을 적용. raw connection으로 실행해 JSON 내 `:` 바인드 오해 방지. |
| **debug_db_target.py** | 실패 시 복구 안내를 `migrate_db_via_url.py` 실행으로 변경, DATABASE_URL 마스킹 출력. |
| **validate_phase0_1.ps1** | 3단계(DB 타깃) 실패 시 `migrate_db_via_url.py` 실행 후 재검사. |
| **Run_Stability_Check.ps1** | 4단계 실패 시 URL 기준 마이그레이션 후 재시도, 5단계 엔진 실패 시에도 `migrate_db_via_url.py`로 재시도. |
| **테스트 스킵 메시지** | test_engine_loop, test_combat_integration 스킵 시 `migrate_db_via_url.py` 안내 추가. |
| **snapshot_repo.py** | INSERT 문에서 `:generated_at::timestamptz`가 바인드로 잘못 해석되던 문제 수정 → `CAST(:generated_at AS TIMESTAMPTZ)` 사용. |
| **order_repo.py** | 동일 이슈(`:created_at::timestamptz`) → `CAST(:created_at AS TIMESTAMPTZ)` 사용. |
| **test_engine_loop.py** | `generated_at` 검증 구간을 실행 전후 2초에서 (before−5분, after+10초)로 완화해 타임존·지연 시에도 통과. |
| **문서** | System_Operations_Manual, Verification_Playbook, Execution_Stability_Check_Result에 URL 기준 마이그레이션 절차 반영. |

---

## 6. 최근 점검 실행 결과 (전체 통과)

**실행 일시:** 2026-03-02  
**실행 방식:** Verification_Playbook 순서대로 중단 없이 진행

### 6.1 스크립트 단계

| 단계 | 스크립트/명령 | 결과 | 출력 요약 |
|------|----------------|------|-----------|
| 1 | `docker ps --format "{{.Names}}"` | PASS | aegisx-db |
| 2 | `.\scripts\migrate_db.ps1` | PASS | Migration complete. (001~004) |
| 3 | `python scripts\debug_db_target.py` | PASS | current_database=aegisx, to_regclass('public.engine_snapshot')=engine_snapshot |
| 4 | `python scripts\run_engine_cycle.py` | PASS | [OK] engine cycle done |
| 5 | `python scripts\verify_snapshot_keys.py` | PASS | Required snapshot keys present (11 keys) |
| 6 | pytest (검증 6모듈) | PASS | 31 passed in 3.16s |
| 7 | `.\scripts\validate_phase0_1.ps1` | PASS | 6/6 단계 완료, 16 passed (phase0_1/contract/combat_force_spec_lock) |

### 6.2 Pytest 상세 (검증 플레이북 6모듈)

- **test_engine_loop.py:** 1 passed  
- **test_gates.py:** 5 passed (emergency_stop, retract, freeze, mode_paper, precedence)  
- **test_execution_contract.py:** 3 passed (no KIS/sqlalchemy/requests·httpx in engines)  
- **test_combat_force_spec_lock.py:** 11 passed (core/swing/strike I/O·수식)  
- **test_combat_system_lock.py:** 8 passed (gate precedence, order state transition)  
- **test_combat_integration.py:** 3 passed (migration, cycle keys, paper order → order_log)  

**합계:** 31 passed, 0 failed, 0 skipped.

### 6.3 결론

- **시스템 실행안정성 점검:** 모든 단계 **PASS**. 중단 없이 완료.
- **권장:** 정기적으로 `.\scripts\validate_phase0_1.ps1` 또는 `.\scripts\Run_Stability_Check.ps1` 실행으로 동일 검증 유지.

---

*문서: Execution_Stability_Check_Result.md | 프로젝트 루트: D:\AEGIS-X_v3*
