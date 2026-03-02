# core/metascore.py — SE-50 Phase 2: MetaScore 수식 고착화.
# MetaScore = a*Sharpe + b*Expectancy - c*MaxDrawdown
# 계수 (a, b, c)는 system_config에 저장, 버전 관리.

from __future__ import annotations

# 기본 계수 (system_config 없을 때). SE-50 예시: 0.5*Sharpe + 0.3*WinRate - 0.2*MaxDD
DEFAULT_METASCORE_PARAMS = {
    "a": 0.5,   # Sharpe
    "b": 0.3,   # Expectancy (or WinRate)
    "c": 0.2,   # MaxDrawdown
    "version": 1,
}

CONFIG_KEY_METASCORE_PARAMS = "metascore_params"


def get_metascore_params(db) -> dict:
    """DB system_config에서 metascore_params 로드. 없으면 DEFAULT_METASCORE_PARAMS."""
    try:
        from backend.app.core.config_service import get_config
        out = get_config(db, CONFIG_KEY_METASCORE_PARAMS)
        if isinstance(out, dict) and "a" in out and "b" in out and "c" in out:
            return {
                "a": float(out.get("a", DEFAULT_METASCORE_PARAMS["a"])),
                "b": float(out.get("b", DEFAULT_METASCORE_PARAMS["b"])),
                "c": float(out.get("c", DEFAULT_METASCORE_PARAMS["c"])),
                "version": int(out.get("version", 1)),
            }
    except Exception:
        pass
    return dict(DEFAULT_METASCORE_PARAMS)


def compute_metascore(sharpe: float, expectancy: float, max_drawdown: float, params: dict | None = None) -> float:
    """
    MetaScore = a*Sharpe + b*Expectancy - c*MaxDrawdown
    max_drawdown는 보통 음수(예: -0.15)로 전달되므로, 빼기면 더해짐.
    """
    p = params or DEFAULT_METASCORE_PARAMS
    a, b, c = float(p.get("a", 0.5)), float(p.get("b", 0.3)), float(p.get("c", 0.2))
    return round(a * sharpe + b * expectancy - c * abs(max_drawdown), 6)


def compute_metascore_from_db(db, sharpe: float, expectancy: float, max_drawdown: float) -> float:
    """DB에서 계수 로드 후 MetaScore 계산."""
    params = get_metascore_params(db)
    return compute_metascore(sharpe, expectancy, max_drawdown, params)
