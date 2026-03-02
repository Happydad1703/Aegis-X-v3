# backend/tests/test_gates.py — SE: EmergencyStop / Retract / Freeze precedence; mode gate blocks BACKTEST.
# Verification_Playbook: pytest backend/tests/test_gates.py

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
        pytest.skip("SessionLocal not available (DB not configured)")
    from backend.app.core.db import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_emergency_stop_blocks_first(sync_db) -> None:
    """EmergencyStop > all: when active, no execution allowed."""
    if not _system_config_available(sync_db):
        pytest.skip("system_config table not available")
    from backend.app.core.config_service import set_config
    from backend.app.gates.gate_chain import run_gate_chain, GATE_EMERGENCY_STOP
    set_config(sync_db, "gate_emergency_stop_active", {"active": True}, "test")
    allow, failed_gate, _ = run_gate_chain(sync_db)
    assert allow is False
    assert failed_gate == GATE_EMERGENCY_STOP
    set_config(sync_db, "gate_emergency_stop_active", {"active": False}, "test")
    set_config(sync_db, "gate_retract_active", {"active": False}, "test")


def test_retract_blocks_when_active(sync_db) -> None:
    """Retract > Mode/Strategy: when active, execution blocked at Retract gate."""
    if not _system_config_available(sync_db):
        pytest.skip("system_config table not available")
    from backend.app.core.config_service import set_config
    from backend.app.gates.gate_chain import run_gate_chain, GATE_RETRACT
    set_config(sync_db, "gate_emergency_stop_active", {"active": False}, "test")
    set_config(sync_db, "gate_retract_active", {"active": True}, "test")
    allow, failed_gate, _ = run_gate_chain(sync_db)
    assert allow is False
    assert failed_gate == GATE_RETRACT
    set_config(sync_db, "gate_retract_active", {"active": False}, "test")


def test_freeze_behavior_backtest_blocks_orders(sync_db) -> None:
    """Mode gate: BACKTEST → block new orders (Freeze: no execution)."""
    from backend.app.gates.mode_gate import run_mode_gate
    class MockDb:
        def execute(self, *a, **k):
            class R:
                def scalar(self):
                    return None
                def mappings(self):
                    return self
                def first(self):
                    return {"mode": "BACKTEST"}
            return R()
    allow, msg = run_mode_gate(MockDb())
    assert allow is False
    assert "BACKTEST" in msg or "block" in msg.lower()


def test_mode_paper_allows(sync_db) -> None:
    """Mode gate: PAPER → allow (paper_executor can run)."""
    from backend.app.gates.mode_gate import run_mode_gate
    class MockDb:
        def execute(self, *a, **k):
            class R:
                def scalar(self):
                    return None
                def mappings(self):
                    return self
                def first(self):
                    return {"mode": "PAPER"}
            return R()
    allow, msg = run_mode_gate(MockDb())
    assert allow is True


def test_precedence_emergency_stop_before_retract() -> None:
    """Safety precedence: EmergencyStop checked before Retract (mock, no DB)."""
    from backend.app.gates.gate_chain import run_gate_chain, GATE_EMERGENCY_STOP, GATE_RETRACT
    import backend.app.gates.gate_chain as gc
    orig = gc._get_config
    def mock(_db, key):
        if key == "gate_emergency_stop_active":
            return {"active": True}
        if key == "gate_retract_active":
            return {"active": True}
        return {}
    gc._get_config = mock
    try:
        allow, failed, _ = run_gate_chain(None)
        assert allow is False
        assert failed == GATE_EMERGENCY_STOP  # first in chain wins
    finally:
        gc._get_config = orig
