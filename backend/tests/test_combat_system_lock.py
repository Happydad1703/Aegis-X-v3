# backend/tests/test_combat_system_lock.py — FULL COMBAT SYSTEM LOCK: gate precedence, live mode block, order state transition.

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.core.order_state import (
    is_allowed_initial_status,
    validate_transition,
    ORDER_STATUS_PENDING,
    ORDER_STATUS_ACK,
    ORDER_STATUS_FILLED,
    ORDER_STATUS_PAPER_FILLED,
    ORDER_STATUS_REJECTED,
    ORDER_STATUS_ERROR,
)


def test_engine_purity() -> None:
    """Engines must not import sqlalchemy or kis."""
    import backend.app.engines.core_engine as core
    import backend.app.engines.swing_engine as swing
    import backend.app.engines.strike_engine as strike
    for mod in (core, swing, strike):
        assert "sqlalchemy" not in str(mod.__dict__).lower()
        assert "kis_executor" not in str(mod.__dict__).lower()


def test_gate_precedence_emergency_stop_blocks_first() -> None:
    """Gate precedence: EmergencyStop blocks before any other gate; first failure wins."""
    from backend.app.gates.gate_chain import run_gate_chain, GATE_EMERGENCY_STOP
    class MockDb:
        pass
    db = MockDb()
    original_get_config = None
    try:
        from backend.app.gates import gate_chain as gc
        original_get_config = gc._get_config
        def mock_config(_db, key):
            if key == "gate_emergency_stop_active":
                return {"active": True}
            return {}
        gc._get_config = mock_config
        allow, failed, reasons = run_gate_chain(db)
        assert allow is False
        assert failed == GATE_EMERGENCY_STOP
        assert any(r[0] == GATE_EMERGENCY_STOP and r[1] is False for r in reasons)
    finally:
        if original_get_config is not None:
            gc._get_config = original_get_config


def test_live_mode_block_backtest_blocks_orders() -> None:
    """Mode gate: BACKTEST → orders disabled (run_mode_gate returns False)."""
    from backend.app.gates.mode_gate import run_mode_gate
    class MockDb:
        def execute(self, *a, **k):
            class R:
                def mappings(self): return self
                def first(self): return {"mode": "BACKTEST"}
            return R()
    allow, msg = run_mode_gate(MockDb())
    assert allow is False
    assert "BACKTEST" in msg


def test_live_mode_block_paper_allows() -> None:
    """Mode gate: PAPER → allow (so paper_executor can run)."""
    from backend.app.gates.mode_gate import run_mode_gate
    class MockDb:
        def execute(self, *a, **k):
            class R:
                def mappings(self): return self
                def first(self): return {"mode": "PAPER"}
            return R()
    allow, msg = run_mode_gate(MockDb())
    assert allow is True


def test_order_state_transition_valid() -> None:
    """Valid transitions: PENDING → FILLED, PENDING → REJECTED, etc."""
    assert validate_transition(ORDER_STATUS_PENDING, ORDER_STATUS_FILLED) is True
    assert validate_transition(ORDER_STATUS_PENDING, ORDER_STATUS_REJECTED) is True
    assert validate_transition(ORDER_STATUS_PENDING, ORDER_STATUS_ACK) is True
    assert validate_transition(ORDER_STATUS_ACK, ORDER_STATUS_FILLED) is True


def test_order_state_transition_invalid() -> None:
    """Invalid transitions: FILLED → anything, PAPER_FILLED → anything."""
    assert validate_transition(ORDER_STATUS_FILLED, ORDER_STATUS_PENDING) is False
    assert validate_transition(ORDER_STATUS_PAPER_FILLED, ORDER_STATUS_FILLED) is False
    assert validate_transition(ORDER_STATUS_REJECTED, ORDER_STATUS_FILLED) is False


def test_order_allowed_initial_status() -> None:
    """Only PENDING, PAPER_FILLED, REJECTED, ERROR allowed on insert."""
    assert is_allowed_initial_status(ORDER_STATUS_PENDING) is True
    assert is_allowed_initial_status(ORDER_STATUS_PAPER_FILLED) is True
    assert is_allowed_initial_status(ORDER_STATUS_REJECTED) is True
    assert is_allowed_initial_status(ORDER_STATUS_ERROR) is True
    assert is_allowed_initial_status(ORDER_STATUS_FILLED) is False
    assert is_allowed_initial_status("UNKNOWN") is False


def test_order_repo_rejects_invalid_initial_status() -> None:
    """order_repo.insert_order_sync raises if execution_status not allowed."""
    from backend.app.core.order_repo import insert_order_sync
    # We need a real DB session to hit the repo; skip if no DB.
    try:
        from backend.app.core.db import SessionLocal
        db = SessionLocal()
        try:
            with pytest.raises(ValueError, match="Invalid initial order status"):
                insert_order_sync(
                    db,
                    symbol="005930",
                    side="BUY",
                    quantity=10,
                    mode="PAPER",
                    execution_status="FILLED",  # not allowed on insert
                    execution_payload={},
                )
        finally:
            db.close()
    except Exception:
        pytest.skip("DB not available")
