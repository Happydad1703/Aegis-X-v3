# 시스템 실행안정성 검증 보고서

**문서 ID:** AEGIS-X-ESV-2025  
**기준:** Verification_Playbook.md, System_Operations_Manual.md §8  
**목적:** 시스템 실행안정성 점검 결과 기록 및 재현 절차 정리

---

## 1. 검증 체크리스트

| # | 항목 | 명령/방법 | 통과 기준 |
|---|------|-----------|-----------|
| 1 | 인프라 | `docker ps` | 컨테이너 aegisx-db 표시 (또는 PG 접속 가능) |
| 2 | 마이그레이션 | `.\scripts\migrate_db.ps1` | Exit 0, "Migration complete." |
| 3 | DB 타깃 | `python scripts\debug_db_target.py` | Exit 0, engine_snapshot 존재 |
| 4 | 엔진 1사이클 | `python scripts\run_engine_cycle.py` | Exit 0, "[OK] engine cycle done" |
| 5 | 스냅샷 키 | `python scripts\verify_snapshot_keys.py` | Exit 0, "[OK] Required snapshot keys present" |
| 6 | 엔진 순수성 | pytest test_execution_contract | KIS/SQL/HTTP 미사용 |
| 7 | 게이트·주문 | pytest test_gates, test_combat_system_lock | EmergencyStop 우선, 주문 상태 전이 준수 |
| 8 | Core/Swing/Strike | pytest test_combat_force_spec_lock | Spec Lock v1.0 I/O·수식 준수 |
| 9 | 통합 | pytest test_engine_loop, test_combat_integration | 1사이클 후 필수 키 존재, Gate PASS 시 paper order |
| 10 | 원샷 하니스 | `.\scripts\validate_phase0_1.ps1` | 1~6 단계 모두 성공 |

---

## 2. 검증 실행 결과 (요약)

**실행 일시:** 2025-03-02  
**환경:** Windows, Python 3.14, pytest 9.0.2

### 2.1 DB 불필요 단위 테스트 (로컬 실행)

| 테스트 모듈 | 결과 | 비고 |
|-------------|------|------|
| test_execution_contract | **PASS** (3/3) | 엔진에 KIS/sqlalchemy/requests·httpx 없음 |
| test_combat_force_spec_lock | **PASS** (11/11) | Core/Swing/Strike 입출력·수식 Lock 준수 |
| test_combat_system_lock | **PASS** (8/8) | 게이트 우선순위, 모드 차단, 주문 상태 전이 |
| test_gates | **PASS** (3/3), 스킵 (2) | E-Stop/Retract 선행 확인; DB 필요 2건 스킵 |

**합계:** 25 passed, 2 skipped.

### 2.2 DB·인프라 의존 검증

- **1~5, 9, 10:** DB 기동 + 마이그레이션 + `.env`의 `DATABASE_URL` 설정 후 동일 환경에서 실행 시 통과 가능.
- **test_engine_loop:** async 세션 + engine_snapshot 테이블 필요. 미준비 시 스킵 또는 ProgrammingError 시 스킵 처리됨.
- **test_combat_integration:** sync DB + system_mode, order_log 테이블 필요.

---

## 3. 결론 및 권장 사항

- **정적·로직 검증:** 엔진 순수성, 게이트 우선순위, 주문 상태 전이, Core/Swing/Strike Spec Lock은 **통과**.
- **런타임 검증:** DB 및 스크립트 검증(1~5, 9, 10)은 운용 환경에서 **정기 실행** 권장 (일일/배포 전).
- **운영지침:** 실행안정성 검증 절차는 [System_Operations_Manual.md](./System_Operations_Manual.md) §8 및 [Verification_Playbook.md](./Verification_Playbook.md) 참조.

---

## 4. 재현 명령 (복사용)

```powershell
cd D:\AEGIS-X_v3

# DB 불필요 테스트만
pytest backend/tests/test_execution_contract.py backend/tests/test_combat_force_spec_lock.py backend/tests/test_combat_system_lock.py backend/tests/test_gates.py -v --tb=short

# 전체 (DB 필요)
docker ps
.\scripts\migrate_db.ps1
python scripts\debug_db_target.py
python scripts\run_engine_cycle.py
python scripts\verify_snapshot_keys.py
pytest backend/tests/test_engine_loop.py backend/tests/test_gates.py backend/tests/test_execution_contract.py backend/tests/test_combat_force_spec_lock.py backend/tests/test_combat_system_lock.py backend/tests/test_combat_integration.py -v
.\scripts\validate_phase0_1.ps1
```

---

*문서 버전: 1.0 | 프로젝트 루트: D:\AEGIS-X_v3*
