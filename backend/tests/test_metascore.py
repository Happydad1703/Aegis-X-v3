# backend/tests/test_metascore.py — MetaScore Lock: a*Sharpe + b*Expectancy - c*MaxDrawdown.

from __future__ import annotations

import pytest


class TestMetaScoreLock:
    """Store a,b,c in system_config; deterministic recomputation."""

    def test_metascore_formula_deterministic(self):
        """Same inputs + same params → same MetaScore (recomputation)."""
        from backend.app.core.metascore import compute_metascore, DEFAULT_METASCORE_PARAMS
        params = dict(DEFAULT_METASCORE_PARAMS)
        a, b, c = params["a"], params["b"], params["c"]
        sharpe, expectancy, max_dd = 1.0, 0.6, -0.10
        m1 = compute_metascore(sharpe, expectancy, max_dd, params)
        m2 = compute_metascore(sharpe, expectancy, max_dd, params)
        assert m1 == m2
        # Formula: a*Sharpe + b*Expectancy - c*|MaxDD|
        expected = a * sharpe + b * expectancy - c * abs(max_dd)
        assert abs(m1 - expected) < 1e-6

    def test_metascore_params_from_default(self):
        """Without DB, default a,b,c yield consistent result."""
        from backend.app.core.metascore import compute_metascore, DEFAULT_METASCORE_PARAMS
        out = compute_metascore(0.5, 0.3, -0.08, None)
        assert isinstance(out, (int, float))
        assert out == compute_metascore(0.5, 0.3, -0.08, DEFAULT_METASCORE_PARAMS)
