# backend/tests/test_24h_simulation.py — PHASE 8: Full 24h cycle simulation (KR → US → OFF).

from __future__ import annotations

from datetime import datetime, timezone

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


class TestFull24hSimulation:
    """Simulate 24h: KR → US → OFF. Session switch, risk, OFF blocks, snapshot metadata."""

    def test_session_switch_updates_universe(self):
        """Session switch (KR → US → OFF) changes universe only; engines get dict."""
        from backend.app.core.timezone_service import get_current_session
        from backend.app.core.universe_selector import universe_selector
        # KR window (e.g. 02:00 UTC)
        kr_time = datetime(2025, 1, 1, 2, 0, 0, tzinfo=timezone.utc)
        assert get_current_session(kr_time, None) == "KR"
        u_kr = universe_selector("KR")
        assert u_kr.get("session") == "KR"
        # US window (e.g. 15:00 UTC)
        us_time = datetime(2025, 1, 1, 15, 0, 0, tzinfo=timezone.utc)
        assert get_current_session(us_time, None) == "US"
        u_us = universe_selector("US")
        assert u_us.get("session") == "US"
        # OFF
        off_time = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        assert get_current_session(off_time, None) == "OFF"
        u_off = universe_selector("OFF")
        assert u_off.get("session") == "OFF"
        assert u_kr is not u_us and u_us is not u_off

    def test_off_blocks_new_trades(self, sync_db):
        """OFF session → block new trades (gate layer)."""
        if not _system_config_available(sync_db):
            pytest.skip("system_config not available")
        from backend.app.core.snapshot_repo import insert_snapshot_sync
        from backend.app.gates.gate_chain import run_gate_chain
        from backend.app.core.config_service import set_config
        set_config(sync_db, "gate_emergency_stop_active", {"active": False}, "test")
        set_config(sync_db, "gate_retract_active", {"active": False}, "test")
        insert_snapshot_sync(
            sync_db,
            snapshot_key="active_session",
            snapshot_data={"session": "OFF", "ts_utc": "2025-01-01T10:00:00Z"},
            freshness_status="GREEN",
            source_name="test",
            refresh_rate_sec=60,
        )
        allow, failed_gate, _ = run_gate_chain(sync_db)
        assert allow is False
        assert failed_gate == "Session"

    def test_snapshot_records_session_metadata(self):
        """Snapshot keys include active_session, session_state, timezone, usd_exposure_status."""
        from backend.app.core.snapshot_keys import ALLOWED_SNAPSHOT_KEYS
        for key in ("active_session", "session_state", "timezone", "usd_exposure_status"):
            assert key in ALLOWED_SNAPSHOT_KEYS

    def test_no_sql_in_engines(self):
        """No architecture violation: engines contain NO SQL."""
        import os
        engines_dir = os.path.join(os.path.dirname(__file__), "..", "app", "engines")
        if not os.path.isdir(engines_dir):
            pytest.skip("engines dir not found")
        sql_keywords = ("SELECT ", "INSERT ", "UPDATE ", "DELETE ", "text(", "execute(")
        for fname in os.listdir(engines_dir):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(engines_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            for kw in sql_keywords:
                assert kw not in content, f"engines must not contain SQL; found {kw!r} in {fname}"

    def test_single_write_path_snapshot(self):
        """Only snapshot_repo writes to engine_snapshot (contract)."""
        import os
        backend = os.path.join(os.path.dirname(__file__), "..")
        for root, _, files in os.walk(backend):
            for f in files:
                if not f.endswith(".py"):
                    continue
                path = os.path.join(root, f)
                rel = os.path.relpath(path, backend)
                if "engines" in rel or "tests" in rel:
                    continue
                with open(path, "r", encoding="utf-8") as file:
                    text = file.read()
                if "INSERT INTO engine_snapshot" in text or "insert into engine_snapshot" in text.lower():
                    assert "snapshot_repo" in rel, f"Only snapshot_repo may INSERT engine_snapshot; found in {rel}"
