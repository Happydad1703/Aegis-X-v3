-- 003: Hash chain columns for engine_snapshot and order_log (SE-50 Phase 3).
-- current_hash = SHA256(previous_hash + payload_json + timestamp). Worker level only; UI never computes.

-- engine_snapshot: prev_hash = previous row's self_hash, self_hash = SHA256(prev_hash || snapshot_data || generated_at)
ALTER TABLE engine_snapshot ADD COLUMN IF NOT EXISTS prev_hash VARCHAR(64);
ALTER TABLE engine_snapshot ADD COLUMN IF NOT EXISTS self_hash VARCHAR(64);

-- order_log: same idea
ALTER TABLE order_log ADD COLUMN IF NOT EXISTS prev_hash VARCHAR(64);
ALTER TABLE order_log ADD COLUMN IF NOT EXISTS self_hash VARCHAR(64);
