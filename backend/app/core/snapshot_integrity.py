# core/snapshot_integrity.py — SE-50 Phase 5: Required keys after engine cycle.

from __future__ import annotations

from sqlalchemy import text

REQUIRED_SNAPSHOT_KEYS = (
    "regime_current",
    "allocation_matrix",
    "fleet_budget_snapshot",
    "risk_guard",
    "llm_status",
    "operation_mode",
    "engine_heartbeat",
)


def check_snapshot_integrity(db) -> tuple[bool, list[str]]:
    """Returns (all_present, list of missing keys)."""
    missing = []
    for key in REQUIRED_SNAPSHOT_KEYS:
        r = db.execute(
            text("SELECT 1 FROM engine_snapshot WHERE snapshot_key = :k ORDER BY generated_at DESC LIMIT 1"),
            {"k": key},
        ).fetchone()
        if not r:
            missing.append(key)
    return (len(missing) == 0, missing)
