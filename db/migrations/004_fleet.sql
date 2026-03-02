-- 004: Fleet table + order_log.fleet_id for Fleet <-> Order relationship (efficient joins).
-- Optional: fleet groups orders by strategy (CORE/SWING/STRIKE).

CREATE TABLE IF NOT EXISTS fleet (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  config JSONB,
  created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC')
);

ALTER TABLE order_log ADD COLUMN IF NOT EXISTS fleet_id BIGINT REFERENCES fleet(id);
CREATE INDEX IF NOT EXISTS idx_order_log_fleet_id ON order_log(fleet_id);
