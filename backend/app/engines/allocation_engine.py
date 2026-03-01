# engines/allocation_engine.py — SE-36: pure dict in → allocation_matrix snapshot_data out.

from __future__ import annotations


def compute_allocation(regime: dict) -> dict:
    """Pure: regime (regime_current snapshot_data) → allocation_matrix snapshot_data."""
    label = regime.get("regime_label", "Sideways")
    crisis = regime.get("crisis_probability", 0.2)
    base = {"CORE": 0.35, "SWING": 0.35, "STRIKE": 0.20, "RESERVE": 0.10}
    if crisis >= 0.7:
        base = {"CORE": 0.5, "SWING": 0.25, "STRIKE": 0.0, "RESERVE": 0.25}
    elif label == "Goldilocks":
        base = {"CORE": 0.30, "SWING": 0.35, "STRIKE": 0.25, "RESERVE": 0.10}
    return {"base_weights": base, "regime_label": label, "crisis_probability": crisis}
