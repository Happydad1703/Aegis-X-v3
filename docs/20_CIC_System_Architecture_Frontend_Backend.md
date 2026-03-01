# 20_CIC_System_Architecture_Frontend_Backend.md
목적
Foreground–Backend–DB 상호작용 구조 정의
포함 내용
1. Logical Architecture
Browser UI
   ↓
API Layer (FastAPI)
   ↓
PostgreSQL (Docker)
   ↓
Engine Workers
2. DB-Only UI Contract
UI는 engine_snapshot만 조회
Drilldown은 engine_result / ext_event_raw 조회
외부 API 직접 호출 금지
3. Snapshot Strategy
snapshot_key 정의
upsert 규칙
latency 최소화 구조