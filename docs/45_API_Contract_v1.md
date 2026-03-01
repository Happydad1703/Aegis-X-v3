# 45_API_Contract_v1 (FastAPI)
Read Endpoints
GET /api/snapshot/{snapshot_key}
GET /api/snapshot/latest?key=regime_current
GET /api/health
GET /api/mode
응답 형식:
{
  "snapshot_key": "regime_current",
  "data": {...},
  "freshness_status": "GREEN",
  "generated_at": "2026-03-01T12:30:00Z"
}

Control Endpoints
POST /api/control/freeze
POST /api/control/retract
POST /api/control/stop
POST /api/mode/set
모든 POST는:
role 확인
command_log 기록
snapshot 갱신
incident 생성 가능