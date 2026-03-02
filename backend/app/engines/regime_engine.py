# engines/regime_engine.py — SE-05 Regime, SE-39 Regime Math: pure dict in → dict out.
# NO DB, NO I/O. Output shape = regime_current.snapshot_data contract (SE_Complete_Alignment §1).
#
# === 수식 고착화 (LaTeX 정의) ===
# Crisis probability (이벤트 기반 프록시):
#   $$ p_{\text{crisis}} = \min(0.95,\; c_0 + c_1 \cdot n_{\text{events}}), \quad c_0=0.1,\; c_1=0.01 $$
# Regime label 경계 (trend_score 기준):
#   $$ \text{Goldilocks if } \tau > 0.3,\quad \text{Tapering if } \tau < -0.3,\quad \text{else Sideways} $$
# 상수: CRISIS_CAP=0.95, CRISIS_BASE=0.1, CRISIS_EVENT_COEF=0.01, TREND_THRESHOLD=0.3

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

# 수식 기반 상수 (고착화). 변경 시 SE 변경 승인 필요.
CRISIS_CAP = 0.95
CRISIS_BASE = 0.1
CRISIS_EVENT_COEF = 0.01
TREND_THRESHOLD = 0.3
CRISIS_REGIME_THRESHOLD = 0.7  # p_crisis >= this → label Crisis
CONFIDENCE_CRISIS = 0.6
CONFIDENCE_GOLDILOCKS = 0.75
CONFIDENCE_TAPERING = 0.7
CONFIDENCE_SIDEWAYS = 0.8


def compute_regime(inputs: dict) -> dict:
    """
    Pure: inputs → regime_current snapshot_data.
    수식: p_crisis = min(CRISIS_CAP, CRISIS_BASE + CRISIS_EVENT_COEF * n_events); regime by trend/crisis.
    """
    inp_str = json.dumps(inputs, sort_keys=True, default=str)
    generated_inputs_hash = hashlib.sha256(inp_str.encode()).hexdigest()[:16]

    events = inputs.get("events_count", 0)
    crisis_probability = min(CRISIS_CAP, CRISIS_BASE + (events * CRISIS_EVENT_COEF))
    trend_score = inputs.get("trend_score", 0.0)
    volatility_state = inputs.get("volatility_state", "normal")

    if crisis_probability >= CRISIS_REGIME_THRESHOLD:
        regime_label = "Crisis"
        confidence_score = CONFIDENCE_CRISIS
    elif trend_score > TREND_THRESHOLD:
        regime_label = "Goldilocks"
        confidence_score = CONFIDENCE_GOLDILOCKS
    elif trend_score < -TREND_THRESHOLD:
        regime_label = "Tapering"
        confidence_score = CONFIDENCE_TAPERING
    else:
        regime_label = "Sideways"
        confidence_score = CONFIDENCE_SIDEWAYS

    return {
        "regime_label": regime_label,
        "crisis_probability": round(crisis_probability, 4),
        "trend_score": round(trend_score, 4),
        "volatility_state": volatility_state,
        "confidence_score": round(confidence_score, 4),
        "generated_inputs_hash": generated_inputs_hash,
        "computed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
