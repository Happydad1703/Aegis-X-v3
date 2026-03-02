# Aegis-X v3 시스템 운영지침서

**문서 ID:** AEGIS-X-SOM-v1.1  
**프로젝트 루트:** `D:\AEGIS-X_v3`  
**대상:** 운용자·관리자  
**참조:** Master_Process_Map.md, Verification_Playbook.md, Execution_ROE.md

---

## 1. 개요 및 전제조건

### 1.1 시스템 개요
- Aegis-X v3는 **Snapshot 기반** 자동 자산운용 시스템입니다.
- **Warroom(CIC)** 웹 대시보드에서 상태를 조회하고, **Freeze / Retract / Emergency Stop** 등 제어를 수행합니다.
- 모든 UI 데이터는 **DB(engine_snapshot)** 에서만 읽으며, 엔진이 계산한 결과는 Snapshot으로 DB에 기록된 뒤 화면에 표시됩니다.

### 1.2 운용 전제조건
| 항목 | 요구사항 |
|------|----------|
| OS | Windows 11 |
| Python | 3.10+ (프로젝트 루트 또는 venv에서 실행) |
| Docker | PostgreSQL 16용 컨테이너 실행 가능 |
| 브라우저 | Chrome, Edge 등 (Warroom/런처 접속용) |

### 1.3 프로젝트 루트
- **고정 경로:** `D:\AEGIS-X_v3`
- 모든 스크립트·문서 내 경로는 이 루트 기준입니다.

---

## 2. 초기 설정 (최초 1회)

### 2.1 데이터베이스(PostgreSQL)
1. Docker 기동 후 마이그레이션 적용.
   ```powershell
   cd D:\AEGIS-X_v3
   docker compose up -d
   .\scripts\migrate_db.ps1
   ```
2. 테이블 확인:
   ```powershell
   docker exec -it aegisx-db psql -U postgres -d aegisx -c "\dt"
   ```
3. Python에서 접속하는 DB가 맞는지 확인:
   ```powershell
   python .\scripts\debug_db_target.py
   ```
   - `current_database()` 가 `aegisx`, `to_regclass('public.engine_snapshot')` 이 존재하면 정상.
4. **Python과 컨테이너가 다른 DB를 가리킬 때:** `debug_db_target.py`에서 테이블이 없다고 나오면, **DATABASE_URL이 가리키는 DB**에 직접 스키마를 적용:
   ```powershell
   python .\scripts\migrate_db_via_url.py
   ```
   동일한 `db/migrations/` SQL을 DATABASE_URL 기준으로 적용하므로, 앱과 동일한 DB가 마이그레이션됩니다.

### 2.2 환경변수(.env / Windows)
- **DB 연결:** 루트에 `.env` 생성 또는 Windows 환경변수에 설정.
  - `DATABASE_URL=postgresql+psycopg2://postgres:<비밀번호>@localhost:5433/aegisx`
  - (선택) `PG_CONTAINER=aegisx-db`
- **API 키·Push:** 외부 연동·Telegram 알림용 키는 **Windows 11 환경변수**에만 설정.  
  상세: [ENV_Windows11_API_Keys.md](./ENV_Windows11_API_Keys.md)

### 2.3 바탕화면·툴바 실행 아이콘
- 바탕화면에 **실행 아이콘** 생성 (프로젝트 루트에서 실행):
  ```powershell
  cd D:\AEGIS-X_v3
  .\scripts\Create_Desktop_Shortcut.bat
  ```
- 생성되는 항목:
  - **Aegis-X v3 Warroom.bat** — 더블클릭 시 Backend 기동 후 브라우저에서 Warroom/Launcher 열림.
  - **Aegis-X v3 실행.lnk** — 동일 동작의 바로가기 아이콘(.lnk).
- 아이콘 우클릭 → **작업 표시줄에 고정** 하면 툴바에서 한 번에 실행 가능.
- 프로젝트 경로가 `D:\AEGIS-X_v3` 가 아니어도, 스크립트가 위치한 폴더 기준으로 자동 인식됩니다.

---

## 3. 일일·시작 절차

### 3.1 권장 순서
1. **DB(PostgreSQL) 기동**
   ```powershell
   cd D:\AEGIS-X_v3
   docker compose up -d
   ```
2. **백엔드 + 브라우저 실행**
   - **방법 A:** 바탕화면(또는 툴바)에서 **Aegis-X v3 Warroom.bat** 더블클릭  
     → Backend가 없으면 자동 기동 후 약 8초 뒤 브라우저가 `http://localhost:8000/launcher/` 로 열림.
   - **방법 B:** 터미널에서 직접 실행
     ```powershell
     cd D:\AEGIS-X_v3
     .\scripts\Start_AegisX_With_Browser.bat
     ```
   - **방법 C:** Backend만 수동 기동 후 브라우저는 직접 접속
     ```powershell
     .\scripts\run_api.ps1
     ```
     브라우저에서 `http://localhost:8000/launcher/` 접속.

### 3.2 엔진·Ingest 사이클 (선택)
- 엔진 1회 사이클(스냅샷 생성):
  ```powershell
  .\scripts\run_engine_worker.ps1
  ```
- Ingest 1회 사이클(외부 이벤트 수집):
  ```powershell
  python .\scripts\run_ingest_cycle.py
  ```
- 실제 운용에서는 스케줄러/워커로 주기 실행하는 구성을 권장.

### 3.3 정상 동작 확인
- 브라우저: `http://localhost:8000/launcher/` → Warroom·Dashboard 영역 표시.
- Health: `http://localhost:8000/api/health` → DB 기반 상태 응답.
- 스냅샷 적재 확인:
  ```powershell
  docker exec -it aegisx-db psql -U postgres -d aegisx -c "SELECT snapshot_key, generated_at FROM engine_snapshot ORDER BY generated_at DESC LIMIT 10;"
  ```

---

## 4. 런처·Warroom 사용

### 4.1 런처 화면 (`/launcher/`)
- **단일 디스플레이**
  - 상단: **Warroom** (스냅샷 카드·상태)
  - 하단: **Dashboard & Control Panel** (동일 Warroom 페이지)
  - 맨 아래: **WSL Terminal** 링크 → `run_wsl_terminal.bat` 다운로드/실행 또는 `scripts\run_wsl_terminal.bat` 실행.
- **복수 디스플레이**
  - 런처에서 **「복수 디스플레이 (창 분리)」** 선택.
  - **Warroom 열기**, **Dashboard & Control 열기** 로 각각 새 창을 띄운 뒤 원하는 모니터로 드래그.

### 4.2 Warroom 화면 구성
- **헤더:** Operation Mode, Regime, Health 요약, **Freeze / Retract / Emergency Stop** 버튼.
- **좌측 메뉴:** 스냅샷·메뉴 링크 (모바일에서는 ☰ 로 열기).
- **본문:** 스냅샷 카드(engine_heartbeat, comm_health, regime_current, operation_mode, llm_status, risk_guard 등).  
  각 카드에는 **source_name, generated_at, refresh_rate_sec, freshness_status** 가 표시됩니다.
- **푸터:** 티커·알림 영역.

### 4.3 제어 동작 (우선순위 준수)
- **우선순위:** Emergency Stop > Retract > Operation Mode > 전략/실행. (SE-50 Gate 체인)
- **단일 명령 진입로:** 모든 제어는 `POST /api/control/command` 로만 수행. 허용 명령: `EMERGENCY_STOP`, `RETRACT`, `SET_MODE`, `RUN_ENGINE_CYCLE`.
- **Emergency Stop:** 최우선 정지. `command_type: "EMERGENCY_STOP"`, payload `{ "reason": "..." }`.
- **Retract:** 리스크 축소. `command_type: "RETRACT"`.
- **SET_MODE:** `command_type: "SET_MODE"`, payload `{ "mode": "PAPER" }` (BACKTEST | PAPER | PILOT | FULL_LIVE).
- **RUN_ENGINE_CYCLE:** 엔진 1회 사이클 수동 실행.
- Gate 상태 조회: `GET /api/control/state` → `emergency_stop`, `retract` (DB 기반).
- (레거시) `POST /api/control/mode`, `POST /api/control/emergency_stop`, `POST /api/control/retract` 도 지원.

---

## 5. 스크립트 참조

| 스크립트 | 용도 |
|----------|------|
| `scripts/migrate_db.ps1` | DB 마이그레이션 적용 (001~004, PowerShell 파이프 사용) |
| `scripts/debug_db_target.py` | 접속 DB·테이블·engine_snapshot 존재 확인 |
| `scripts/run_engine_cycle.py` | 엔진 1회 사이클 (스냅샷 기록) |
| `scripts/run_engine_worker.ps1` | 엔진 1회 사이클 래퍼 (프로젝트 루트에서 실행) |
| `scripts/verify_snapshot_keys.py` | 필수 스냅샷 키 존재 여부 검증 |
| `scripts/validate_phase0_1.ps1` | Phase 0-1 통합 검증 (docker→migrate→debug→cycle→verify→pytest) |
| `scripts/run_ingest_cycle.py` | Ingest 1회 사이클 (ext_event_raw 수집) |
| `scripts/run_engine_comm_check.py` | 엔진·스냅샷·외부 통신 점검 |
| `run_api.ps1` / Backend | FastAPI 서버 (0.0.0.0:8000), /api/snapshot/*, /api/control/*, /warroom |
| `Create_Desktop_Shortcut.bat` | 바탕화면 Warroom 바로가기 |
| `Start_AegisX_With_Browser.bat` | Backend 기동 후 브라우저 런처 |
| `check_comm.py` | 외부 API 통신 확인 |

---

## 6. 원격 접속·모바일·Push

### 6.1 모바일(S24 Ultra 등) 접속
- **같은 Wi‑Fi:** PC IP 확인 후 `http://<PC-IP>:8000/warroom/` 또는 `http://<PC-IP>:8000/launcher/` 접속.
- **다른 네트워크:** ngrok 등으로 8000 포트 터널 후 발급 URL로 접속.
- Backend는 `--host 0.0.0.0` 으로 기동되어 있어야 LAN 내 접속 가능 (run_api.ps1 / Start_AegisX_With_Browser.bat 사용 시 해당됨).

### 6.2 Push 알림 (Telegram)
- **환경변수:** `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` 설정.
- **자동 발송 이벤트:** Freeze, Retract, Emergency Stop, 매매 체결(trade_filled).  
  시장 개시/종료·target 선정·AAR 등은 모듈 연동 후 확장 가능.
- 상세: [Launcher_and_Remote_Access.md](./Launcher_and_Remote_Access.md).

---

## 7. 장애 대응

| 현상 | 확인·조치 |
|------|------------|
| **ERR_CONNECTION_REFUSED** (localhost:8000) | Backend 미기동. `Start_AegisX_With_Browser.bat` 또는 `run_api.ps1` 실행. |
| **테이블/engine_snapshot 없음** | `migrate_db.ps1` 재실행. `debug_db_target.py` 로 접속 DB·테이블 확인. |
| **Python/uvicorn 없음** | 프로젝트 루트에서 `pip install -r requirements.txt`. venv 사용 시 활성화 후 실행. |
| **바탕화면 바로가기 실패** | `Create_Desktop_Shortcut.bat` 재실행. 생성된 bat은 `D:\AEGIS-X_v3\scripts\Start_AegisX_With_Browser.bat` 를 호출함. |
| **Push 미수신** | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` 환경변수 및 봇·채팅 설정 확인. |

---

## 8. 검증·품질 관문 (실행안정성 검증)

### 8.1 실행안정성 검증 절차 (권장 순서)
다음 순서로 수행 시 **시스템 실행안정성**을 확인할 수 있다. 상세: [Verification_Playbook.md](./Verification_Playbook.md).

1. **인프라** — Docker 기동, 컨테이너 `aegisx-db` 확인  
   `docker ps`
2. **마이그레이션** — DDL 적용  
   `.\scripts\migrate_db.ps1`
3. **DB 타깃** — 접속 DB·engine_snapshot 테이블 확인  
   `python scripts\debug_db_target.py`
4. **엔진 1사이클** — 스냅샷 기록  
   `python scripts\run_engine_cycle.py`
5. **스냅샷 키** — 필수 키 존재 확인  
   `python scripts\verify_snapshot_keys.py`
6. **단위·통합 테스트** — 엔진 순수성, 게이트 우선순위, 주문 상태 전이 등  
   `pytest backend/tests/test_engine_loop.py backend/tests/test_gates.py backend/tests/test_execution_contract.py backend/tests/test_combat_force_spec_lock.py backend/tests/test_combat_system_lock.py backend/tests/test_combat_integration.py -v`
7. **원샷 하니스** — 위 1~6을 한 번에 실행  
   `.\scripts\validate_phase0_1.ps1`

**통과 조건:** 1~5 성공, 6에서 DB 의존 테스트는 스킵 가능(DB 미기동 시). 7은 DB+마이그레이션 선행 필요.  
**검증 결과 보고:** [Execution_Stability_Verification_Report.md](./Execution_Stability_Verification_Report.md) 참조.

### 8.2 DB 없이 실행 가능한 검증
- **엔진 순수성·게이트·주문 상태:**  
  `pytest backend/tests/test_execution_contract.py backend/tests/test_gates.py backend/tests/test_combat_force_spec_lock.py backend/tests/test_combat_system_lock.py -v`  
  (일부 test_gates는 system_config 테이블 필요 시 스킵)
- **계약 테스트 전체:** DB·asyncpg 준비 후 [Phase0_1_Run_Checklist.md](./Phase0_1_Run_Checklist.md) 또는 [Verification_Playbook.md](./Verification_Playbook.md) 실행.

---

## 9. 참조 문서

| 문서 | 내용 |
|------|------|
| [Verification_Playbook.md](./Verification_Playbook.md) | 셀프 검증 스크립트·pytest·Run Checklist |
| [Execution_Stability_Verification_Report.md](./Execution_Stability_Verification_Report.md) | 실행안정성 검증 결과 보고 |
| [Execution_ROE.md](./Execution_ROE.md) | 실행 규칙(Gate 우선순위, Mode, 주문 상태 전이) |
| [Master_Process_Map.md](./Master_Process_Map.md) | 프로세스 맵 단일 소스 |
| [ARCHITECTURE_AUDIT_REPORT.md](./ARCHITECTURE_AUDIT_REPORT.md) | 아키텍처 감사 결과 |
| [Phase0_1_Run_Checklist.md](./Phase0_1_Run_Checklist.md) | Phase 0-1 실행 체크리스트 |
| [ENV_Windows11_API_Keys.md](./ENV_Windows11_API_Keys.md) | 환경변수·API 키 |
| [SE_Master_Index.md](./SE_Master_Index.md) | SE 문서 인덱스 |

---

*문서 버전: 1.1 | 프로젝트 루트: D:\AEGIS-X_v3*
