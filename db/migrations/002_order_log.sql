-- 002: order_log (SE-51 Order Execution)
-- Phase 2-5: paper_executor / kis_executor write via order_repo only.

CREATE TABLE IF NOT EXISTS order_log (
  id BIGSERIAL PRIMARY KEY,
  symbol VARCHAR(50) NOT NULL,
  side VARCHAR(10) NOT NULL,
  quantity NUMERIC NOT NULL,
  mode VARCHAR(20) NOT NULL,
  execution_status VARCHAR(50) NOT NULL,
  execution_payload JSONB,
  created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE INDEX IF NOT EXISTS idx_order_log_created ON order_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_order_log_mode ON order_log(mode);
