# core/timezone_service.py — 24/7 Follow-the-Sun. Session windows from system_config (no hardcode).
# NO engine modification. Exposes get_current_session(now_utc) -> "KR" | "US" | "OFF".

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

CONFIG_KEY_SESSION_WINDOWS = "follow_the_sun_windows"

# Defaults only when config missing (configurable via system_config)
_DEFAULT_KR_START = "00:00"
_DEFAULT_KR_END = "06:30"
_DEFAULT_US_START = "13:00"
_DEFAULT_US_END = "20:00"


def _parse_time_utc(s: str) -> tuple[int, int]:
    """Parse "HH:MM" or "HH:MM:SS" to (hour, minute)."""
    parts = s.strip().split(":")
    h = int(parts[0]) if parts else 0
    m = int(parts[1]) if len(parts) > 1 else 0
    return h, m


def _minutes_since_midnight(h: int, m: int) -> int:
    return h * 60 + m


def _in_window(now: datetime, start_str: str, end_str: str) -> bool:
    """True if now (UTC) time-of-day falls in [start, end) UTC. Handles cross-midnight."""
    now_min = now.hour * 60 + now.minute
    sh, sm = _parse_time_utc(start_str)
    eh, em = _parse_time_utc(end_str)
    start_min = _minutes_since_midnight(sh, sm)
    end_min = _minutes_since_midnight(eh, em)
    if start_min <= end_min:
        return start_min <= now_min < end_min
    return now_min >= start_min or now_min < end_min


def get_current_session(now_utc: datetime | str, db: Any = None) -> str:
    """
    Returns "KR" | "US" | "OFF" from session windows in system_config.
    Session windows: { "KR": {"start_utc": "00:00", "end_utc": "06:30"}, "US": {...} }.
    """
    if isinstance(now_utc, str):
        try:
            now_utc = datetime.fromisoformat(now_utc.replace("Z", "+00:00"))
        except Exception:
            now_utc = datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)

    windows = None
    if db is not None:
        try:
            from backend.app.core.config_service import get_config
            windows = get_config(db, CONFIG_KEY_SESSION_WINDOWS)
        except Exception:
            pass

    if not isinstance(windows, dict):
        windows = {
            "KR": {"start_utc": _DEFAULT_KR_START, "end_utc": _DEFAULT_KR_END},
            "US": {"start_utc": _DEFAULT_US_START, "end_utc": _DEFAULT_US_END},
        }

    kr = windows.get("KR") or {}
    us = windows.get("US") or {}
    if isinstance(kr, dict) and _in_window(now_utc, kr.get("start_utc", _DEFAULT_KR_START), kr.get("end_utc", _DEFAULT_KR_END)):
        return "KR"
    if isinstance(us, dict) and _in_window(now_utc, us.get("start_utc", _DEFAULT_US_START), us.get("end_utc", _DEFAULT_US_END)):
        return "US"
    return "OFF"


def get_session_multiplier(session: str, db: Any = None) -> float:
    """KR=1.0, US=configurable (e.g. 0.7), OFF=0.0. From system_config follow_the_sun_multipliers."""
    if session == "OFF":
        return 0.0
    if session == "KR":
        mult = 1.0
    else:
        mult = 0.7
    if db is not None:
        try:
            from backend.app.core.config_service import get_config
            cfg = get_config(db, "follow_the_sun_multipliers")
            if isinstance(cfg, dict):
                mult = float(cfg.get(session, mult))
        except Exception:
            pass
    return max(0.0, min(1.0, mult))
