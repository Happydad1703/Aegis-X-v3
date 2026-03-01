from __future__ import annotations

import math

def aggression_factor(G: float, Amax: float = 1.4, Amin: float = 0.7, k: float = 0.2) -> float:
    if G <= 0:
        return Amax
    val = Amax - k * math.log(G)
    return max(Amin, min(Amax, val))
