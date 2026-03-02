# backend/tests/test_snapshot_integrity.py — SE-50 Phase 5: Required keys after engine cycle.

from __future__ import annotations

import pytest


def _sync_db_available() -> bool:
    try:
        from backend.app.core.db import SessionLocal
        return SessionLocal is not None
    except Exception:
        return False


def _engine_snapshot_available(db) -> bool:
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1 FROM engine_snapshot LIMIT 1"))
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


class TestSnapshotIntegrity:
    """After one engine cycle: regime_current, allocation_matrix, fleet_budget_snapshot, risk_guard, llm_status, operation_mode, engine_heartbeat."""

    def test_required_keys_defined(self):
        from backend.app.core.snapshot_integrity import REQUIRED_SNAPSHOT_KEYS
        assert "regime_current" in REQUIRED_SNAPSHOT_KEYS
        assert "allocation_matrix" in REQUIRED_SNAPSHOT_KEYS
        assert "engine_heartbeat" in REQUIRED_SNAPSHOT_KEYS

    def test_check_returns_bool_and_missing_list(self, sync_db):
        if not _engine_snapshot_available(sync_db):
            pytest.skip("engine_snapshot table not available")
        from backend.app.core.snapshot_integrity import check_snapshot_integrity
        ok, missing = check_snapshot_integrity(sync_db)
        assert isinstance(ok, bool)
        assert isinstance(missing, list)
        if not ok:
            assert len(missing) > 0
