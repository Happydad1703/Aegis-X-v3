# engines/fleet_budget_engine.py — SE-34: pure dict in → fleet_budget_snapshot out.

from __future__ import annotations


def compute_fleet_budget(allocation: dict, pilot_config: dict | None) -> dict:
    """Pure: allocation (allocation_matrix snapshot_data) + optional pilot_config → fleet_budget_snapshot."""
    weights = dict(allocation.get("base_weights", {"CORE": 0.35, "SWING": 0.35, "STRIKE": 0.20, "RESERVE": 0.10}))
    if pilot_config and not pilot_config.get("strike_enabled", True):
        weights["STRIKE"] = 0.0
        remain = 1.0 - (weights.get("CORE", 0) + weights.get("SWING", 0) + weights.get("STRIKE", 0))
        weights["RESERVE"] = max(0.0, remain)
    return {"weights": weights, "regime_label": allocation.get("regime_label")}
