# backend/tests/test_llm_blackout.py — SE-50 Phase 4: Blackout triggers freeze, incident_log written.

from __future__ import annotations

import pytest


def _sync_db_available() -> bool:
    try:
        from backend.app.core.db import SessionLocal
        return SessionLocal is not None
    except Exception:
        return False


def _tables_available(db) -> bool:
    """system_config and incident_log required for blackout tests."""
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1 FROM system_config LIMIT 1"))
        db.execute(text("SELECT 1 FROM incident_log LIMIT 1"))
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


class TestLLMBlackout:
    """Mock all LLM providers fail → on_blackout → incident_log + execution freeze."""

    def test_on_blackout_sets_config_and_incident(self, sync_db):
        """on_blackout records incident and sets llm_blackout_active (Execution Freeze)."""
        if not _tables_available(sync_db):
            pytest.skip("system_config or incident_log not available")
        from backend.app.core.llm_gateway import on_blackout
        from backend.app.core.config_service import get_config
        from sqlalchemy import text
        on_blackout(sync_db)
        cfg = get_config(sync_db, "llm_blackout_active")
        assert isinstance(cfg, dict) and cfg.get("active") is True
        r = sync_db.execute(text("SELECT 1 FROM incident_log WHERE category = 'LLM_BLACKOUT' ORDER BY created_at DESC LIMIT 1")).fetchone()
        assert r is not None
        # Clear for other tests
        from backend.app.core.config_service import set_config
        set_config(sync_db, "llm_blackout_active", {"active": False}, "test")

    def test_blackout_blocks_gate_chain(self, sync_db):
        """When llm_blackout_active, gate chain returns allow=False."""
        if not _tables_available(sync_db):
            pytest.skip("system_config or incident_log not available")
        from backend.app.core.config_service import set_config
        set_config(sync_db, "gate_emergency_stop_active", {"active": False}, "test")
        set_config(sync_db, "gate_retract_active", {"active": False}, "test")
        set_config(sync_db, "llm_blackout_active", {"active": True}, "test")
        from backend.app.gates.gate_chain import run_gate_chain
        allow, failed_gate, _ = run_gate_chain(sync_db)
        assert allow is False
        assert failed_gate == "LLMBlackout"
        set_config(sync_db, "llm_blackout_active", {"active": False}, "test")
