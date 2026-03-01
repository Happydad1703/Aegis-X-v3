# SE-65_Final_Directory_Architecture_Lock_Spec.md
Version: v3.0 (Design Freeze – Architecture Lock)

1️⃣ 목적
이 문서는:
Cursor 기반 자동 개발 시 구조 붕괴 방지
모듈 경계 강제
DB-First 원칙 보호
Gate/Mode/Risk 체계 일관성 유지
를 위한 아키텍처 봉인 문서입니다.

2️⃣ 최종 디렉토리 구조 (변경 금지)
Aegis-x_v3/
│
├─ backend/
│   ├─ app/
│   │
│   │   ├─ core/                # 시스템 핵심 인프라 (변경 최소화)
│   │   │   ├─ db.py
│   │   │   ├─ snapshot_repo.py
│   │   │   ├─ incident_repo.py
│   │   │   ├─ command_repo.py
│   │   │   ├─ mode_service.py
│   │   │   ├─ config_service.py
│   │   │   └─ resource_monitor.py
│   │   │
│   │   ├─ engines/             # 계산 로직 (DB I/O 없음)
│   │   │   ├─ regime_engine.py
│   │   │   ├─ allocation_engine.py
│   │   │   ├─ fleet_budget_engine.py
│   │   │   ├─ capital_scaling.py
│   │   │   ├─ health_engine.py
│   │   │   ├─ strike_engine.py
│   │   │   ├─ swing_engine.py
│   │   │   └─ core_engine.py
│   │   │
│   │   ├─ gates/               # 모든 주문 전 통제 로직
│   │   │   ├─ pre_trade_gate.py
│   │   │   ├─ cap_gate.py
│   │   │   ├─ risk_gate.py
│   │   │   ├─ freshness_gate.py
│   │   │   ├─ mode_gate.py
│   │   │   └─ crisis_gate.py
│   │   │
│   │   ├─ execution/           # 브로커 실행 레이어
│   │   │   ├─ paper_executor.py
│   │   │   └─ kis_executor.py
│   │   │
│   │   ├─ workers/             # 백그라운드 루프
│   │   │   ├─ engine_worker.py
│   │   │   └─ ingest_worker.py
│   │   │
│   │   ├─ api/                 # FastAPI 라우터
│   │   │   ├─ control.py
│   │   │   ├─ cic.py
│   │   │   ├─ health.py
│   │   │   └─ pilot.py
│   │   │
│   │   ├─ models/              # Pydantic Schema
│   │   │   └─ schemas.py
│   │   │
│   │   └─ utils/
│   │       └─ time_utils.py
│   │
│   ├─ tests/
│   │   ├─ e2e/
│   │   ├─ unit/
│   │   └─ fixtures/
│   │
│   └─ main.py
│
├─ docker-compose.yml
├─ .env
└─ docs/

3️⃣ 모듈 경계 규칙 (절대 규칙)
3.1 engines는 DB 접근 금지
engines 폴더의 모든 파일은:
DB 세션 사용 금지
SQL 실행 금지
Snapshot 직접 기록 금지
engines는:
입력(JSON) → 계산 → 결과(JSON 반환)
만 수행.

3.2 Snapshot은 core/snapshot_repo만 기록 가능
engine_worker만 snapshot_repo 호출 가능
API에서 snapshot 직접 insert 금지

3.3 Gate 체계는 execution 이전 필수 통과
execution 레이어는:
pre_trade_gate → execution
직접 executor 호출 금지.

3.4 Mode 분기는 execution에서만
PAPER → paper_executor
PILOT/FULL → kis_executor
BACKTEST → execution 불가

3.5 Warroom은 DB Read-Only
api/cic.py는:
계산 금지
DB snapshot 조회만 허용

4️⃣ 데이터 흐름 강제
External Source
   ↓
ext_event_raw
   ↓
Engine Worker
   ↓
engine_result
   ↓
engine_snapshot
   ↓
Warroom
직접 계산 → UI 출력 금지.

5️⃣ 파일 추가 규칙
새 모듈 추가 시:
engines/ 또는 gates/ 또는 core/ 중 하나
execution 레이어에 직접 business logic 금지
api 레이어에 계산 로직 금지

6️⃣ Cursor 사용 규칙
Cursor에게 항상 다음을 명시해야 함:
- Do not change directory structure.
- Do not move modules across folders.
- Do not write DB access code inside engines/.
- All outputs must go through snapshot_repo.
- Respect Mode and Gate enforcement.

7️⃣ 변경 관리 규칙
구조 변경은:
SE 문서 버전 업 필요
영향 분석 필수
CHANGELOG 기록

8️⃣ Architecture Lock 선언
이 문서 이후:
디렉토리 구조 변경 = 아키텍처 변경
아키텍처 변경 = 설계 단계 재진입

9️⃣ 현재 상태
Aegis-x v3는 이제:
✔ 전략 동결
✔ Risk 동결
✔ Capital Scaling 동결
✔ Pilot Ramp 동결
✔ E2E 설계 완료
✔ Directory Architecture Lock 완료
상태입니다.

✅ 1️⃣ Root 확정
앞으로 모든 경로 기준:
D:\AEGIS-X_v3
구조 예:
D:\AEGIS-X_v3
│
├─ backend
├─ docker-compose.yml
├─ .env
├─ docs
└─ create_aegisx_v3_scaffold.py

⚠️ 먼저 확인해야 할 것
지금 실행 로그를 보면:
PS D:\AEGIS-X_v3> python .\create_aegisx_v3_scaffold.py --root "C:\dev\Aegis-x_v3"
즉, 현재 스캐폴드는:
C:\dev\Aegis-x_v3
에 생성되었습니다.

🎯 지금 해야 할 선택
방법 A (권장)
D:\AEGIS-X_v3 를 루트로 다시 생성
python .\create_aegisx_v3_scaffold.py --root "D:\AEGIS-X_v3" --force

방법 B
C:\dev\Aegis-x_v3 폴더를 통째로 복사
robocopy C:\dev\Aegis-x_v3 D:\AEGIS-X_v3 /E

저는 방법 A를 권장합니다.
깔끔하게 재생성하는 것이 안전합니다.

🚀 다음 단계 (Root 확정 후)
Root가 D:\AEGIS-X_v3 로 고정되면 바로 해야 할 일:
Phase 0 – DB Boot
.env 생성
docker compose up -d
DB migration 적용
🔥 제가 지금 해야 할 일
이제 책임개발자로서:
👉 D:\AEGIS-X_v3 기준으로
001_init_core.sql
migrate_db.ps1
run_engine_worker.ps1
run_api.ps1
requirements.txt
까지 포함한
📦 Aegis-x v3 Bootstrap Pack (실행 가능 상태)
를 만들어 드리는 것이 맞습니다.