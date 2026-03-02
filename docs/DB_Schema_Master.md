# DB Schema Master — Tables, Keys, Retention

Source of truth: db/migrations/. ORM: backend/app/database/models.py (aligned).

---

## Tables

| Table | Purpose | Key columns |
|-------|---------|-------------|
| ext_event_raw | Ingest input | id, event_type, source_name, payload, received_at |
| engine_snapshot | Engine outputs (snapshot_repo only) | id, snapshot_key, snapshot_data, freshness_status, source_name, refresh_rate_sec, generated_at, prev_hash, self_hash |
| system_mode | Operation mode | id, mode, changed_by, changed_at |
| system_config | Config key-value (JSONB) | id, config_key, config_value, updated_by, updated_at |
| incident_log | Incidents (incident_repo only) | id, severity, category, message, related_snapshot_key, created_at |
| command_log | Commands (command_repo only) | id, command_type, issued_by, command_payload, status, created_at |
| order_log | Execution (order_repo only) | id, symbol, side, quantity, mode, execution_status, execution_payload, created_at, prev_hash, self_hash, fleet_id (FK) |
| fleet | Strategy grouping (004) | id, name, config, created_at |

Fleet ↔ Order: order_log.fleet_id references fleet(id). ORM: backend/app/database/models.py (Fleet, OrderLog with relationship).

---

## Single write path

- engine_snapshot → snapshot_repo only  
- ext_event_raw → event_repo only  
- incident_log → incident_repo only  
- command_log → command_repo only  
- order_log → order_repo only  

---

## Retention (policy)

- engine_snapshot: retain/archive by generated_at (e.g. 30 days).  
- order_log: audit (e.g. 7 years KR).  
- incident_log, command_log: per audit policy.  
- ext_event_raw: prune by received_at (e.g. 7 days).
