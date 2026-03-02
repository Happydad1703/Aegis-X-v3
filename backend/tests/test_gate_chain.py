# backend/tests/test_gate_chain.py — SE-50 Phase 1: Gate priority linear chain.
# If EmergencyStop = True → all trades blocked.
# If Risk violation = True → strategy signal ignored.
# Strategy logic never executes before gate evaluation.

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


class TestGateChainOrder:
    """선형 우선순위: EmergencyStop → Retract → Mode → Risk → Freshness → PreTrade → Strategy."""

    def test_emergency_stop_blocks_all(self, sync_db):
        """If EmergencyStop = True → all trades blocked."""
        if not _system_config_available(sync_db):
            pytest.skip("system_config table not available")
        from backend.app.core.config_service import set_config, get_config
        set_config(sync_db, "gate_emergency_stop_active", {"active": True}, "test")
        from backend.app.gates.gate_chain import run_gate_chain, GATE_EMERGENCY_STOP
        allow, failed_gate, reasons = run_gate_chain(sync_db)
        assert allow is False
        assert failed_gate == GATE_EMERGENCY_STOP
        set_config(sync_db, "gate_emergency_stop_active", {"active": False}, "test")
        set_config(sync_db, "gate_retract_active", {"active": False}, "test")

    def test_retract_blocks_when_active(self, sync_db):
        """Retract active → execution blocked at Retract gate."""
        if not _system_config_available(sync_db):
            pytest.skip("system_config table not available")
        from backend.app.core.config_service import set_config
        set_config(sync_db, "gate_emergency_stop_active", {"active": False}, "test")
        set_config(sync_db, "gate_retract_active", {"active": True}, "test")
        from backend.app.gates.gate_chain import run_gate_chain, GATE_RETRACT
        allow, failed_gate, _ = run_gate_chain(sync_db)
        assert allow is False
        assert failed_gate == GATE_RETRACT
        set_config(sync_db, "gate_retract_active", {"active": False}, "test")

    def test_strategy_not_evaluated_before_gates(self, sync_db):
        """Strategy (execution allow) is only True when all prior gates pass."""
        if not _system_config_available(sync_db):
            pytest.skip("system_config table not available")
        from backend.app.gates.gate_chain import run_gate_chain, GATE_ORDER
        allow, failed_gate, reasons = run_gate_chain(sync_db)
        # If any gate before Strategy fails, allow is False and failed_gate is set
        if not allow:
            assert failed_gate in GATE_ORDER
            assert failed_gate != "Strategy"
        else:
            assert failed_gate == ""
            names = [r[0] for r in reasons]
            assert GATE_ORDER[-1] in names  # Strategy passed last


class TestRiskGate:
    """If Risk violation = True → strategy signal ignored (block at Risk gate)."""

    def test_risk_violation_blocks_when_dd_over_threshold(self, sync_db):
        """risk_guard snapshot with portfolio_dd <= -8% → block at Risk gate."""
        if not _system_config_available(sync_db):
            pytest.skip("system_config table not available")
        from backend.app.core.snapshot_repo import insert_snapshot_sync
        from backend.app.gates.gate_chain import run_gate_chain, GATE_RISK
        from backend.app.core.config_service import set_config
        set_config(sync_db, "gate_emergency_stop_active", {"active": False}, "test")
        set_config(sync_db, "gate_retract_active", {"active": False}, "test")
        insert_snapshot_sync(
            sync_db,
            snapshot_key="risk_guard",
            snapshot_data={"portfolio_dd": -0.09, "vol_spike": 1.0},
            freshness_status="GREEN",
            source_name="test",
            refresh_rate_sec=60,
        )
        allow, failed_gate, _ = run_gate_chain(sync_db)
        assert allow is False
        assert failed_gate == GATE_RISK
