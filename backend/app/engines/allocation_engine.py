# engines/allocation_engine.py — SE-36: pure dict in → allocation_matrix snapshot_data out.
# V3 알고리즘 수식 Locking: Kelly Criterion, Softmax 벡터 연산. LLM은 최종 해설만, 핵심 계산은 본 모듈.
#
# === 수식 고착화 (LaTeX 정의) ===
# Allocation_raw = Kelly Ratio × Regime Weight (정규화 전)
#   $$ \text{Allocation}_{\text{raw}} = f^* \times w_{\text{regime}} $$
# Softmax 정규화 후 base_weights:
#   $$ w_i = \frac{\exp(s_i - \max(\mathbf{s}))}{\sum_j \exp(s_j - \max(\mathbf{s}))}, \quad \mathbf{s} = \text{regime\_scores} $$
# Kelly Criterion:
#   $$ f^* = \frac{p \cdot b - q}{b}, \quad q=1-p, \quad b=\text{win/loss ratio} $$
# 상수: FLEET_KEYS = ["CORE", "SWING", "STRIKE", "RESERVE"] (고정)

from __future__ import annotations

import math
from typing import Dict, List, Union

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

# 수식 기반 상수 (고착화). 변경 시 SE 변경 승인 필요.
FLEET_KEYS = ("CORE", "SWING", "STRIKE", "RESERVE")
SOFTMAX_ROUND_DECIMALS = 6
KELLY_CLIP_FRACTION = 1.0  # f* 상한 (자본 대비)

# ---------- 수식 Locking (가독성·검증 가능성. 11_Governance, SE-36) ----------

def softmax(x: Union[List[float], "np.ndarray"]) -> List[float]:
    """
    Softmax: p_i = exp(x_i - max(x)) / sum(exp(x_j - max(x))).
    LaTeX: w_i = exp(s_i - max(s)) / sum_j exp(s_j - max(s)).
    """
    if _HAS_NUMPY:
        arr = np.asarray(x, dtype=float)
        e = np.exp(arr - np.max(arr))
        out = (e / e.sum()).tolist()
        return [round(v, SOFTMAX_ROUND_DECIMALS) for v in out]
    # Pure Python fallback
    x = list(map(float, x))
    m = max(x)
    ex = [math.exp(v - m) for v in x]
    s = sum(ex)
    return [round(v / s, SOFTMAX_ROUND_DECIMALS) for v in ex]


def kelly_fraction(win_probability: float, win_loss_ratio: float, fraction: float = KELLY_CLIP_FRACTION) -> float:
    """
    Kelly Criterion: f* = (p*b - q) / b, q = 1-p, b = win/loss ratio.
    LaTeX: f^* = (p b - (1-p)) / b. 반환값은 [0, fraction]으로 클리핑.
    """
    p = max(0.0, min(1.0, float(win_probability)))
    b = max(0.0, float(win_loss_ratio))
    q = 1.0 - p
    if b <= 0:
        return 0.0
    f = (p * b - q) / b
    f = max(0.0, min(float(fraction), f))
    return round(f, SOFTMAX_ROUND_DECIMALS)


def compute_allocation(regime: dict) -> dict:
    """
    Pure: regime → allocation_matrix.
    수식: Allocation_raw = Kelly Ratio × Regime Weight; 정규화는 Softmax(regime_scores).
    """
    label = regime.get("regime_label", "Sideways")
    crisis = float(regime.get("crisis_probability", 0.2))
    trend = float(regime.get("trend_score", 0.0))

    # 국면별 로그-스코어 s (FLEET_KEYS 순). 수식 고착화 상수.
    if crisis >= 0.7:
        log_scores = [1.2, 0.6, -1.0, 1.5]  # Crisis
    elif label == "Goldilocks":
        log_scores = [0.8, 1.0, 1.2, 0.3]   # Goldilocks
    elif label == "Tapering":
        log_scores = [0.5, 0.3, 0.2, 1.0]   # Tapering
    else:
        log_scores = [1.0, 1.0, 0.8, 0.6]   # Sideways

    weights = softmax(log_scores)
    base = dict(zip(FLEET_KEYS, weights))

    return {
        "base_weights": base,
        "regime_label": label,
        "crisis_probability": round(crisis, 4),
        "formula": "softmax(regime_scores)",  # 감사 추적용
    }
