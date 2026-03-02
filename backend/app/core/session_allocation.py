# core/session_allocation.py — 24/7 Section 6: global_capital -> session_allocation -> fleet_allocation.
# Do NOT change fleet_budget_engine. Multiply fleet_budget_snapshot by session_multiplier at read/use time.

from __future__ import annotations


def apply_session_multiplier_to_fleet_budget(
    fleet_budget_snapshot: dict,
    session_state_snapshot: dict | None,
) -> dict:
    """
    2-level: fleet_budget_snapshot * session_multiplier = effective session allocation.
    Returns fleet_budget_snapshot with "session_multiplier" key added; consumer multiplies weights if needed.
    Does NOT modify engine output structure; additive metadata only.
    """
    mult = 1.0
    if isinstance(session_state_snapshot, dict):
        data = session_state_snapshot.get("snapshot_data") if "snapshot_data" in session_state_snapshot else session_state_snapshot
        if isinstance(data, dict):
            mult = float(data.get("session_multiplier", 1.0))
    out = dict(fleet_budget_snapshot)
    out["session_multiplier"] = max(0.0, min(1.0, mult))
    return out
