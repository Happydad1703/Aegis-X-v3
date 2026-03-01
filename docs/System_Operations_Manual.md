# Aegis-X v3 시스템 운용 매뉴얼

**문서 ID:** AEGIS-X-SOM-v1.0  
**프로젝트 루트:** `D:\AEGIS-X_v3`  
**대상:** 운용자·관리자

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

### 2.2 환경변수(.env / Windows)
- **DB 연결:** 루트에 `.env` 생성 또는 Windows 환경변수에 설정.
  - `DATABASE_URL=postgresql+psycopg2://postgres:<비밀번호>@localhost:5433/aegisx`
  - (선택) `PG_CONTAINER=aegisx-db`
- **API 키·Push:** 외부 연동·Telegram 알림용 키는 **Windows 11 환경변수**에만 설정.  
  상세: [ENV_Windows11_API_Keys.md](./ENV_Windows11_API_Keys.md)

### 2.3 바탕화면·툴바 바로가기
- 바탕화면에 **Aegis-X v3 Warroom** 바로가기 생성:
  ```powershell
  cd D:\AEGIS-X_v3
  .\scripts\Create_Desktop_Shortcut.bat
  ```
- 생성된 **Aegis-X v3 Warroom.bat** 을 우클릭 → **작업 표시줄에 고정** 하면 툴바에서 실행 가능.

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
- **우선순위:** Emergency Stop > Retract > Operation Mode > 전략/실행.
- **Freeze:** 신규 진입 차단. Warroom에서 클릭 시 `command_log` 기록 및 Telegram 등 Push 발송(설정 시).
- **Retract:** 리스크 축소·청산 권고. 동일하게 로그·Push.
- **Emergency Stop:** 최우선 정지. 동일하게 로그·Push.
- Mode 변경은 `POST /api/control/mode` (Backtest / Paper / Pilot / Live 등)로 수행.

---

## 5. 스크립트 참조

| 스크립트 | 용도 |
|----------|------|
| `Create_Desktop_Shortcut.bat` | 바탕화면에 Aegis-X v3 Warroom.bat 생성 |
| `Start_AegisX_With_Browser.bat` | Backend 기동(미기동 시) 후 브라우저로 런처 열기 |
| `Start_AegisX_Launcher.bat` | 브라우저만 런처로 열기 (Backend는 별도 기동) |
| `run_api.ps1` | FastAPI 서버 기동 (0.0.0.0:8000) |
| `migrate_db.ps1` | DB 마이그레이션 적용 (001, 002 순) |
| `run_engine_worker.ps1` | 엔진 1회 사이클 실행 |
| `run_engine_cycle.py` | 엔진 1회 사이클 (Python 직접 호출) |
| `run_ingest_cycle.py` | Ingest 1회 사이클 |
| `run_wsl_terminal.bat` | WSL/Windows Terminal 실행 |
| `debug_db_target.py` | Python이 접속하는 DB·테이블 확인 |
| `check_comm.py` | 외부 API(FRED, OpenAI, Gemini, KIS 등) 통신 확인 |
| `internal_simulation.py` | 아키텍처·스냅샷 키 등 내부 시뮬레이션 점검 |

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

## 8. 검증·품질 관문

### 8.1 시스템 전체 실행 안정성 점검
- **한 번에 실행:**
  ```powershell
  cd D:\AEGIS-X_v3
  powershell -ExecutionPolicy Bypass -File .\scripts\Run_Stability_Check.ps1
  ```
- **점검 항목:** Docker DB 기동, 마이그레이션, 테이블 존재, Python DB 진단, 엔진 1사이클, 스냅샷 적재(최근 5분 6건 이상), 계약 테스트(5개), 내부 시뮬레이션, 외부 통신(check_comm).
- **전체 통과 조건:** 9/9. 계약 테스트 중 `test_engine_loop` 통과에는 **asyncpg** 설치 필요 (`pip install asyncpg`). 엔진/스냅샷 실패 시 `.env`의 `DATABASE_URL`과 마이그레이션 대상 DB가 동일한지 확인.
- **결과 분석·후속조치:** [Stability_Check_Result_and_Followup.md](./Stability_Check_Result_and_Followup.md) 참조.
- **자체 해결 불가 사항 보고:** [Stability_Check_Report_Unresolvable.md](./Stability_Check_Report_Unresolvable.md) — 포트 충돌 등 환경 이슈 정리.

### 8.2 계약 테스트만 수동 실행
- **계약 테스트 (3원칙·엔진 무결성):**
  ```powershell
  cd D:\AEGIS-X_v3
  pytest backend/tests/test_contract_api_db_only_read.py backend/tests/test_contract_ui_never_calls_compute.py backend/tests/test_contract_single_write_path.py backend/tests/test_contract_engines_purity.py backend/tests/test_engine_loop.py -v
  ```
- **실행 순서 요약:** [Phase0_1_Run_Checklist.md](./Phase0_1_Run_Checklist.md) 참조.

---

## 9. 참조 문서

| 문서 | 내용 |
|------|------|
| [ENV_Windows11_API_Keys.md](./ENV_Windows11_API_Keys.md) | 환경변수·API 키 목록 및 통신 확인 |
| [Launcher_and_Remote_Access.md](./Launcher_and_Remote_Access.md) | 런처·원격·모바일·Push 상세 |
| [Phase0_1_Run_Checklist.md](./Phase0_1_Run_Checklist.md) | Phase 0-1 실행 체크리스트 |
| [Cursor_SOO_Phase0_1.md](./Cursor_SOO_Phase0_1.md) | 표준 운영 규칙(SOO)·아키텍처 락 |
| [SE_Master_Index.md](./SE_Master_Index.md) | SE 문서 인덱스 |

---

*문서 버전: 1.0 | 프로젝트 루트: D:\AEGIS-X_v3*
