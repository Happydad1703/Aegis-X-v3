# core/universe_selector.py — 24/7 Follow-the-Sun. Session → universe dict. No strategy change.
# Engines receive universe as input dict only; no engine logic change.

from __future__ import annotations

# Placeholder universes (minimal; configurable via system_config in future)
KOREA_UNIVERSE = {"session": "KR", "symbols": [], "market": "KRX"}
US_UNIVERSE = {"session": "US", "symbols": [], "market": "US"}
EMPTY_UNIVERSE = {"session": "OFF", "symbols": [], "market": None}


def universe_selector(session: str) -> dict:
    """
    if session == "KR": return korea_universe
    elif session == "US": return us_universe
    else: return empty_universe
    """
    if session == "KR":
        return dict(KOREA_UNIVERSE)
    if session == "US":
        return dict(US_UNIVERSE)
    return dict(EMPTY_UNIVERSE)
