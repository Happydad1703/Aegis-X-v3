41_Execution_and_Deployment_Architecture_Spec.md (v1.0)
________________________________________
1️⃣ 아키텍처 목표
Aegis-X는:
•	24시간 무중단 운용
•	Docker 기반 PostgreSQL
•	DB-centric 설계
•	API 엔진 백그라운드 가동
•	Warroom Web은 DB Snapshot만 소비
•	Windows 11 환경변수 기반 API Key 관리
•	단일 KIS 계좌 운용
________________________________________
2️⃣ 전체 시스템 구조
[External Sources]
   ↓
[Ingest Layer]
   ↓
[PostgreSQL (Docker)]
   ↓
[Core Engine Layer]
   ├─ Regime Engine
   ├─ Allocation Engine
   ├─ Strike/Swing/Core Engines
   ├─ Risk Engine
   ├─ AAR Engine
   ↓
[Snapshot Generator]
   ↓
[API Layer]
   ↓
[Warroom Web UI]
   ↓
[Mobile + Messenger]
________________________________________
3️⃣ Docker 구성
3.1 PostgreSQL (필수)
version: "3.9"
services:
  aegis_postgres:
    image: postgres:15
    container_name: aegis_pg
    restart: always
    environment:
      POSTGRES_DB: aegis
      POSTGRES_USER: aegis_user
      POSTGRES_PASSWORD: strong_password
    ports:
      - "5432:5432"
    volumes:
      - aegis_pg_data:/var/lib/postgresql/data

volumes:
  aegis_pg_data:
운영 원칙:
•	자동 재시작
•	데이터 영구 보존
•	daily backup script 추가
________________________________________
4️⃣ 실행 계층 분리
4.1 Ingest Worker
•	scan_scheduler
•	macro_collect
•	news ingest
•	KIS sync
주기:
•	refresh_schedule.yaml 기반
________________________________________
4.2 Core Engine Worker
•	Regime 계산
•	Allocation 계산
•	Strike/Swing/Core 업데이트
•	Risk 체크
•	AAR 업데이트
________________________________________
4.3 Snapshot Generator
모든 엔진 결과를:
snapshot_table
에 1~3분 간격으로 저장.
Warroom은 여기만 조회.
________________________________________
5️⃣ API Layer
FastAPI 기반 권장.
엔드포인트 예시:
GET /api/snapshot/regime
GET /api/snapshot/allocation
GET /api/snapshot/fleet/{fleet}
POST /api/control/freeze
POST /api/control/retract
POST /api/control/stop
모든 POST는:
•	인증
•	Audit 기록
•	상태 변경
•	Snapshot 갱신
________________________________________
6️⃣ Warroom Web 구성
6.1 Frontend
•	React + TypeScript
•	Sticky Header / Left Tree / Footer
•	Drawer Drilldown
•	WebSocket or SSE Snapshot push
________________________________________
6.2 UI 데이터 흐름
DB Snapshot → API → Web → Render
엔진 직접 호출 금지.
________________________________________
7️⃣ Mobile & Messenger 연결
7.1 Telegram Bot Service
별도 서비스:
telegram_bot_worker
동작:
•	명령 수신
•	DB 기록
•	Engine 상태 변경
•	응답 송신
________________________________________
8️⃣ Scheduler 구조
2개 레벨:
8.1 Fast Loop (1~3분)
•	KIS sync
•	Snapshot update
•	Strike Risk check
8.2 Slow Loop (10~60분)
•	Regime recalculation
•	Macro update
•	AAR aggregation
________________________________________
9️⃣ Fail-Safe 구조
9.1 Health Monitor
•	DB 연결
•	KIS 연결
•	API latency
•	Snapshot freshness
RED 발생 시:
•	Strike disable
•	Alert 발송
________________________________________
🔟 Mode Execution Layer
Mode	동작
Backtest	DB read-only, KIS disabled
Paper	KIS mock
Pilot	KIS 실거래, cap 제한
Full Live	전면 활성
Mode는 DB에 저장되고 Snapshot에 반영.
________________________________________
11️⃣ Logging & Audit
필수 테이블:
•	command_log
•	incident_log
•	messenger_log
•	engine_error_log
•	snapshot_log
모든 이벤트는 기록.
________________________________________
12️⃣ Latency 최소화 전략
•	Snapshot만 UI에 제공
•	Heavy 계산은 백그라운드
•	WebSocket push
•	Index 최적화
•	DB connection pooling
________________________________________
13️⃣ 24시간 Global Force 전략
한국을 Main Base로 두고:
•	한국장: 적극
•	미국 ETF: Proxy 활용
•	비거래 시간: Macro + Regime 계산
________________________________________