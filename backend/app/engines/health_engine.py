from __future__ import annotations

from datetime import datetime, timezone

def compute_health_status(inputs: dict) -> dict:
    # TODO: inputs will include snapshot times, db status, kis status, llm status, etc.
    return {
        "snapshot_freshness": "GREEN",
        "critical_incidents_last_hour": 0,
        "generated_at_utc": datetime.now(timezone.utc).isoformat()
    }
