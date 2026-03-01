-- =============================================================================
-- AEGIS-X v3 Core Schema — Phase 0-1
-- SE 문서: SE-64(모듈 스펙·DB 스키마 의존성), SE-65(디렉터리 구조 락)
-- 구현 항목: 통합 DDL — ext_event_raw, engine_snapshot, system_mode, system_config,
--           incident_log, command_log (모든 시간 UTC TIMESTAMPTZ, JSON은 JSONB)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 외부 이벤트 수집 원시 테이블 (ingest pipeline 입력)
-- SE-64: DB schema dependencies, Snapshot production contract
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ext_event_raw (
  id BIGSERIAL PRIMARY KEY,
  event_type VARCHAR(100) NOT NULL,
  source_name VARCHAR(255),
  payload JSONB NOT NULL,
  received_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE INDEX IF NOT EXISTS idx_ext_event_received
  ON ext_event_raw(received_at DESC);
CREATE INDEX IF NOT EXISTS idx_ext_event_type
  ON ext_event_raw(event_type);

-- -----------------------------------------------------------------------------
-- 엔진 스냅샷 (engines/ 결과물은 core/snapshot_repo.py를 통해서만 기록)
-- SE-64: Snapshot production contract
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS engine_snapshot (
  id BIGSERIAL PRIMARY KEY,
  snapshot_key VARCHAR(100) NOT NULL,
  snapshot_data JSONB NOT NULL,
  freshness_status VARCHAR(20),
  source_name VARCHAR(100),
  refresh_rate_sec INT,
  generated_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE INDEX IF NOT EXISTS idx_snapshot_key_time
  ON engine_snapshot(snapshot_key, generated_at DESC);

-- -----------------------------------------------------------------------------
-- 시스템 모드 (BACKTEST | PAPER | PILOT | FULL_LIVE)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS system_mode (
  id BIGSERIAL PRIMARY KEY,
  mode VARCHAR(20) NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC')
);

-- -----------------------------------------------------------------------------
-- 시스템 설정 키-값 (JSONB)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS system_config (
  id BIGSERIAL PRIMARY KEY,
  config_key VARCHAR(100) NOT NULL,
  config_value JSONB NOT NULL,
  updated_by VARCHAR(100),
  updated_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC')
);

-- -----------------------------------------------------------------------------
-- 사고/이벤트 로그 (incident_repo)
-- SE-64: Audit logging requirement
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS incident_log (
  id BIGSERIAL PRIMARY KEY,
  severity VARCHAR(20) NOT NULL,
  category VARCHAR(100),
  message TEXT NOT NULL,
  related_snapshot_key VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE INDEX IF NOT EXISTS idx_incident_created
  ON incident_log(created_at DESC);

-- -----------------------------------------------------------------------------
-- 명령 로그 (command_repo)
-- SE-64: Audit logging requirement
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS command_log (
  id BIGSERIAL PRIMARY KEY,
  command_type VARCHAR(100) NOT NULL,
  issued_by VARCHAR(100),
  command_payload JSONB NOT NULL,
  status VARCHAR(50) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE INDEX IF NOT EXISTS idx_command_created
  ON command_log(created_at DESC);

-- -----------------------------------------------------------------------------
-- 시드 데이터 (최초 1회)
-- -----------------------------------------------------------------------------
INSERT INTO system_mode (mode, changed_by)
SELECT 'PAPER', 'SYSTEM_INIT'
WHERE NOT EXISTS (SELECT 1 FROM system_mode);

INSERT INTO system_config (config_key, config_value, updated_by)
SELECT 'pilot_config',
       '{"pilot_step":"P1","pilot_cap_pct":0.01,"strike_enabled":false,"daily_entry_limit":1}'::jsonb,
       'SYSTEM_INIT'
WHERE NOT EXISTS (
  SELECT 1 FROM system_config WHERE config_key = 'pilot_config'
);
