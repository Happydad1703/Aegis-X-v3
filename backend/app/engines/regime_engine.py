# engines/regime_engine.py — SE-05 Regime, SE-39 Regime Math: pure dict in → dict out.
# NO DB, NO I/O. Output shape = regime_current.snapshot_data contract (SE_Complete_Alignment §1).

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone


def compute_regime(inputs: dict) -> dict:
    """
    Pure function: inputs (from DB/worker) → regime_current snapshot_data.
    SE-39 contract: regime_label, crisis_probability, trend_score, volatility_state, confidence_score, generated_inputs_hash.
    """
    # Deterministic hash for reproducibility (SE-39 generated_inputs_hash)
    inp_str = json.dumps(inputs, sort_keys=True, default=str)
    generated_inputs_hash = hashlib.sha256(inp_str.encode()).hexdigest()[:16]

    # Placeholder logic: when inputs have no real macro data, return neutral regime
    events = inputs.get("events_count", 0)
    crisis_probability = min(0.95, 0.1 + (events * 0.01))
    trend_score = inputs.get("trend_score", 0.0)
    volatility_state = inputs.get("volatility_state", "normal")

    if crisis_probability >= 0.7:
        regime_label = "Crisis"
        confidence_score = 0.6
    elif trend_score > 0.3:
        regime_label = "Goldilocks"
        confidence_score = 0.75
    elif trend_score < -0.3:
        regime_label = "Tapering"
        confidence_score = 0.7
    else:
        regime_label = "Sideways"
        confidence_score = 0.8

    return {
        "regime_label": regime_label,
        "crisis_probability": round(crisis_probability, 4),
        "trend_score": round(trend_score, 4),
        "volatility_state": volatility_state,
        "confidence_score": round(confidence_score, 4),
        "generated_inputs_hash": generated_inputs_hash,
        "computed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
