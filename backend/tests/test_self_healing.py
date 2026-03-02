# backend/tests/test_self_healing.py — Institutional Freeze: Self-Healing → Gate Link.
# Level 1 → Strike Disable; Level 2 → Budget × 0.7; Level 3 → EmergencyStop=True.

from __future__ import annotations

import pytest


def _sync_db_available() -> bool:
    try:
        from backend.app.core.db import SessionLocal
        return SessionLocal is not None
    except Exception:
        return False


def _system_config_available(db) -> bool:
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1 FROM system_config LIMIT 1"))
        return True
    except Exception:
        db.rollback()
        return False


@pytest.fixture
def sync_db():
    if not _sync_db_available():
        pytest.skip("SessionLocal not available")
    from backend.app.core.db import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestSelfHealingGateLink:
    """Automatic trigger: Level 3 → EmergencyStop=True."""

    def test_level3_sets_emergency_stop(self, sync_db):
        """Apply Level 3 → gate_emergency_stop_active is True; gate chain blocks."""
        if not _system_config_available(sync_db):
            pytest.skip("system_config table not available")
        from backend.app.core.self_healing import apply_self_healing, clear_self_healing
        from backend.app.core.config_service import get_config
        from backend.app.gates.gate_chain import run_gate_chain, GATE_EMERGENCY_STOP
        apply_self_healing(sync_db, 3)
        cfg = get_config(sync_db, "gate_emergency_stop_active")
        assert isinstance(cfg, dict) and cfg.get("active") is True
        allow, failed_gate, _ = run_gate_chain(sync_db)
        assert allow is False
        assert failed_gate == GATE_EMERGENCY_STOP
        clear_self_healing(sync_db)

    def test_level1_sets_strike_disabled(self, sync_db):
        """Level 1 → self_healing_strike_disabled config set."""
        if not _system_config_available(sync_db):
            pytest.skip("system_config table not available")
        from backend.app.core.self_healing import apply_self_healing, clear_self_healing
        from backend.app.core.config_service import get_config
        apply_self_healing(sync_db, 1)
        cfg = get_config(sync_db, "self_healing_strike_disabled")
        assert isinstance(cfg, dict) and cfg.get("active") is True
        clear_self_healing(sync_db)

    def test_level2_sets_budget_multiplier(self, sync_db):
        """Level 2 → self_healing_budget_multiplier = 0.7."""
        if not _system_config_available(sync_db):
            pytest.skip("system_config table not available")
        from backend.app.core.self_healing import apply_self_healing, clear_self_healing
        from backend.app.core.config_service import get_config
        apply_self_healing(sync_db, 2)
        cfg = get_config(sync_db, "self_healing_budget_multiplier")
        assert isinstance(cfg, dict) and cfg.get("multiplier") == 0.7
        clear_self_healing(sync_db)
