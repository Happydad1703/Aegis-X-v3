64_Phase0_1_DB_and_MinWorker_Package_Spec.md (v1.0)
0) 범위
•	Docker PostgreSQL
•	DB DDL 통합본(필수 테이블 + 인덱스)
•	Engine Worker 최소 실행본
•	Snapshot 6종 생산:
o	engine_heartbeat
o	health_status
o	regime_current
o	allocation_matrix
o	fleet_budget_snapshot
o	portfolio_state (MVP)
________________________________________
1) Docker PostgreSQL (Windows 11)
1.1 docker-compose.yml
version: "3.9"
services:
  aegis_postgres:
    image: postgres:15
    container_name: aegis_pg
    restart: always
    environment:
      POSTGRES_DB: aegis
      POSTGRES_USER: aegis_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - aegis_pg_data:/var/lib/postgresql/data
volumes:
  aegis_pg_data:
1.2 .env 예시(로컬)
•	POSTGRES_PASSWORD=...
•	DATABASE_URL=postgresql+psycopg2://aegis_user:...@localhost:5432/aegis
________________________________________
2) DB 스키마 통합 DDL (v1)
파일명 권장: db/migrations/001_init_core.sql
2.1 공통 규칙
•	모든 시간: TIMESTAMPTZ + UTC
•	모든 JSON: JSONB
•	최신 조회가 많은 테이블: (key, generated_at DESC) 인덱스
________________________________________
2.2 DDL (필수)
-- 0) extension (선택)
-- CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1) 원천 이벤트
CREATE TABLE IF NOT EXISTS ext_event_raw (
  id BIGSERIAL PRIMARY KEY,
  source_name VARCHAR(100) NOT NULL,
  event_type VARCHAR(50) NOT NULL,
  payload JSONB NOT NULL,
  received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  event_timestamp TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_ext_event_source_time
ON ext_event_raw(source_name, received_at DESC);

-- 2) 매크로 컨텍스트
CREATE TABLE IF NOT EXISTS macro_context (
  id BIGSERIAL PRIMARY KEY,
  source_name VARCHAR(100),
  indicator_name VARCHAR(100),
  value NUMERIC,
  observed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_macro_indicator_time
ON macro_context(indicator_name, observed_at DESC);

-- 3) 엔진 결과 (중간 산출/프록시)
CREATE TABLE IF NOT EXISTS engine_result (
  id BIGSERIAL PRIMARY KEY,
  engine_name VARCHAR(100),
  result_key VARCHAR(100),
  result_value JSONB,
  computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_engine_name_time
ON engine_result(engine_name, computed_at DESC);

-- 4) 스냅샷 (Warroom SSOT)
CREATE TABLE IF NOT EXISTS engine_snapshot (
  id BIGSERIAL PRIMARY KEY,
  snapshot_key VARCHAR(100) NOT NULL,
  snapshot_data JSONB NOT NULL,
  freshness_status VARCHAR(20) DEFAULT 'GREEN',
  source_name VARCHAR(100),
  refresh_rate_sec INT,
  generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_snapshot_key_time
ON engine_snapshot(snapshot_key, generated_at DESC);

-- 5) incident 로그
CREATE TABLE IF NOT EXISTS incident_log (
  id BIGSERIAL PRIMARY KEY,
  severity VARCHAR(20),
  category VARCHAR(100),
  message TEXT,
  related_snapshot_key VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_incident_time
ON incident_log(created_at DESC);

-- 6) command 로그
CREATE TABLE IF NOT EXISTS command_log (
  id BIGSERIAL PRIMARY KEY,
  command_type VARCHAR(100),
  issued_by VARCHAR(100),
  command_payload JSONB,
  status VARCHAR(50),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_command_time
ON command_log(created_at DESC);

-- 7) system_mode
CREATE TABLE IF NOT EXISTS system_mode (
  id BIGSERIAL PRIMARY KEY,
  mode VARCHAR(20) NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8) system_config (Pilot Ramp 포함)
CREATE TABLE IF NOT EXISTS system_config (
  id BIGSERIAL PRIMARY KEY,
  config_key VARCHAR(100) NOT NULL,
  config_value JSONB NOT NULL,
  updated_by VARCHAR(100),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_system_config_key
ON system_config(config_key);

-- 9) order_log (MVP)
CREATE TABLE IF NOT EXISTS order_log (
  id BIGSERIAL PRIMARY KEY,
  symbol VARCHAR(20),
  side VARCHAR(10),
  quantity NUMERIC,
  price NUMERIC,
  mode VARCHAR(20),
  execution_status VARCHAR(20),
  execution_payload JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_order_time
ON order_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_order_symbol_time
ON order_log(symbol, created_at DESC);

-- 10) battle_report (후속 Phase에 사용)
CREATE TABLE IF NOT EXISTS battle_report (
  id BIGSERIAL PRIMARY KEY,
  symbol VARCHAR(20),
  fleet VARCHAR(20),
  strategy_module VARCHAR(50),
  entry_price NUMERIC,
  exit_price NUMERIC,
  quantity NUMERIC,
  pnl_pct NUMERIC,
  holding_period INT,
  regime_at_entry VARCHAR(20),
  crisis_prob_at_entry NUMERIC,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
________________________________________
2.3 Seed (초기값)
-- 기본 Mode: PAPER
INSERT INTO system_mode (mode, changed_by)
SELECT 'PAPER', 'SYSTEM_INIT'
WHERE NOT EXISTS (SELECT 1 FROM system_mode);

-- Pilot Config 기본값(P1)
INSERT INTO system_config (config_key, config_value, updated_by)
SELECT
  'pilot_config',
  '{
     "pilot_step":"P1",
     "pilot_cap_pct":0.01,
     "strike_enabled":false,
     "daily_entry_limit":1
   }',
  'SYSTEM_INIT'
WHERE NOT EXISTS (
  SELECT 1 FROM system_config WHERE config_key='pilot_config'
);
________________________________________
3) Engine Worker 최소 실행 패키지
3.1 파일 구조(최소)
backend/
 ├─ app/
 │   ├─ db.py
 │   ├─ workers/
 │   │   ├─ engine_worker.py
 │   │   ├─ snapshot_repo.py
 │   │   ├─ incident_repo.py
 │   │   ├─ health_engine.py
 │   │   ├─ heartbeat_engine.py
 │   │   ├─ regime_engine.py
 │   │   ├─ allocation_engine.py
 │   │   ├─ fleet_budget_engine.py
 │   │   └─ portfolio_state_engine.py
 │   └─ services/
 │       ├─ mode_service.py
 │       └─ config_service.py
 └─ scripts/
     ├─ migrate_db.ps1
     └─ run_engine_worker.ps1
________________________________________
3.2 engine_worker.py 핵심: run_single_cycle(db) 분리
•	E2E 테스트에서도 사용 가능하도록 1-cycle 실행 함수를 분리합니다.
의무 산출물
•	engine_heartbeat (GREEN)
•	health_status (GREEN/YELLOW/RED)
•	regime_current
•	allocation_matrix
•	fleet_budget_snapshot
•	portfolio_state
________________________________________
4) 실행 절차 (Windows 11 PowerShell)
4.1 DB 기동
docker compose up -d
4.2 마이그레이션
migrate_db.ps1는 아래를 수행:
•	psql로 001_init_core.sql 실행
(환경에 따라 psql 경로가 다르므로, 구현 시엔 “psql 설치 경로”를 프로젝트에 문서화하거나, Docker exec 방식으로 실행합니다.)
4.3 Worker 실행
.\scripts\run_engine_worker.ps1
4.4 검증 (DB)
SELECT snapshot_key, freshness_status, generated_at
FROM engine_snapshot
ORDER BY generated_at DESC
LIMIT 20;
________________________________________
5) Acceptance Criteria (Phase 0~1)
아래 4개가 모두 만족하면 Phase 0~1 완료:
1.	DB 재시작 후 데이터 유지
2.	Worker 실행 후 5분 이내 engine_snapshot에 6종 키가 생성
3.	health_status가 stale 조건에서 YELLOW/RED로 변함
4.	incident_log에 CRITICAL 폭증 없음(정상 루프)
________________________________________
6) 다음 단계(Phase 2)로 넘어가기 위한 “Go 조건”
•	Pre-Trade Gate + Pilot Cap + Daily entry gate 연결
•	Mode enforcement
•	Order Engine(Paper) 연결
________________________________________
6️⃣ 권장 디렉토리 구조 (Cursor Friendly)
Aegis-x_v3/
│
├─ backend/
│   ├─ app/
│   │   ├─ core/
│   │   │   ├─ db.py
│   │   │   ├─ snapshot_repo.py
│   │   │   ├─ incident_repo.py
│   │   │   ├─ mode_service.py
│   │   │   └─ config_service.py
│   │   │
│   │   ├─ engines/
│   │   │   ├─ regime_engine.py
│   │   │   ├─ allocation_engine.py
│   │   │   ├─ fleet_budget_engine.py
│   │   │   ├─ capital_scaling.py
│   │   │   └─ health_engine.py
│   │   │
│   │   ├─ gates/
│   │   │   ├─ pre_trade_gate.py
│   │   │   ├─ cap_gate.py
│   │   │   ├─ risk_gate.py
│   │   │   └─ freshness_gate.py
│   │   │
│   │   ├─ execution/
│   │   │   ├─ paper_executor.py
│   │   │   └─ kis_executor.py
│   │   │
│   │   ├─ workers/
│   │   │   └─ engine_worker.py
│   │   │
│   │   ├─ api/
│   │   │   ├─ control.py
│   │   │   ├─ cic.py
│   │   │   └─ health.py
│   │   │
│   │   └─ models/
│   │       └─ schemas.py
│   │
│   └─ tests/
│
├─ docker-compose.yml
└─ docs/
이 구조를 Cursor에게 고정시켜야 합니다.
________________________________________
7️⃣ 결론
👉 Cursor는 “구조를 스스로 설계하는 도구”가 아닙니다.
👉 우리는 구조를 먼저 고정하고,
👉 Cursor는 그 구조 안에서 모듈을 생성하게 해야 합니다.
________________________________________
🔥 다음 전략적 행동
지금 가장 중요한 것은:
Aegis-x v3의 “Final Directory Architecture Lock”을 확정하는 것
그걸 먼저 고정해야
Cursor가 안전하게 개발을 시작할 수 있습니다.
________________________________________
 
