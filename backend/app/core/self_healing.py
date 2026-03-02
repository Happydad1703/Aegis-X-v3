# core/self_healing.py — Institutional Freeze: Self-Healing → Gate Link.
# Level 1 → Strike Disable; Level 2 → Budget × 0.7; Level 3 → EmergencyStop=True.
# No engine modification; config/gate layer only.

from __future__ import annotations

from typing import Any

CONFIG_KEY_STRIKE_DISABLED = "self_healing_strike_disabled"
CONFIG_KEY_BUDGET_MULTIPLIER = "self_healing_budget_multiplier"
CONFIG_KEY_EMERGENCY_STOP = "gate_emergency_stop_active"


def apply_self_healing(db: Any, level: int) -> None:
    """
    Apply Self-Healing → Gate Link by risk level.
    Level 1 → Strike Disable (config).
    Level 2 → Budget × 0.7 (config).
    Level 3 → EmergencyStop=True (config).
    """
    from backend.app.core.config_service import set_config
    if level >= 1:
        set_config(db, CONFIG_KEY_STRIKE_DISABLED, {"active": True}, "self_healing")
    if level >= 2:
        set_config(db, CONFIG_KEY_BUDGET_MULTIPLIER, {"multiplier": 0.7}, "self_healing")
    if level >= 3:
        set_config(db, CONFIG_KEY_EMERGENCY_STOP, {"active": True}, "self_healing")


def clear_self_healing(db: Any) -> None:
    """Reset self-healing state (e.g. after recovery)."""
    from backend.app.core.config_service import set_config
    set_config(db, CONFIG_KEY_STRIKE_DISABLED, {"active": False}, "self_healing")
    set_config(db, CONFIG_KEY_BUDGET_MULTIPLIER, {"multiplier": 1.0}, "self_healing")
    set_config(db, CONFIG_KEY_EMERGENCY_STOP, {"active": False}, "self_healing")
