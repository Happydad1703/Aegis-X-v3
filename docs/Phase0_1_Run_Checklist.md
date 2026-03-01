# Phase 0-1 실행 체크리스트 (PowerShell)

**전제**: 컨테이너 `aegisx-db`, DB `aegisx`, 포트 5433.  
`.env`: `DATABASE_URL=postgresql+psycopg2://postgres:2041@localhost:5433/aegisx` (선택: `PG_CONTAINER=aegisx-db`)

---

```powershell
cd D:\AEGIS-X_v3

# 1) DB 기동
docker compose up -d

# 2) 마이그레이션
.\scripts\migrate_db.ps1

# 3) 테이블 확인
docker exec -it aegisx-db psql -U postgres -d aegisx -c "\dt"

# 4) Python이 붙는 DB가 맞는지 20초 진단
python .\scripts\debug_db_target.py

# 5) (선택) API 기동
.\scripts\run_api.ps1

# 6) 엔진 1회 사이클 실행
.\scripts\run_engine_worker.ps1

# 7) 적재 확인
docker exec -it aegisx-db psql -U postgres -d aegisx -c "SELECT snapshot_key, generated_at FROM engine_snapshot ORDER BY generated_at DESC LIMIT 10;"

# 8) 계약 테스트 (3원칙 검증)
pytest backend/tests/test_contract_api_db_only_read.py backend/tests/test_contract_ui_never_calls_compute.py backend/tests/test_contract_single_write_path.py backend/tests/test_contract_engines_purity.py backend/tests/test_engine_loop.py -v
```

**참조**: `docs/Cursor_SOO_Phase0_1.md` (SOO 1페이지), `docs/Cursor_Guardrails_SE_Enforcement.md`
