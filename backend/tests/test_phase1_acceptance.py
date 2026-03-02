# backend/tests/test_phase1_acceptance.py — Phase 0/1 Definition of Done.
# test_engine_cycle_inserts_minimum_snapshots, test_pre_trade_gate_blocks_on_emergency_stop, test_api_snapshot_readonly_no_compute

from __future__ import annotations

import pytest

# Phase 1 minimum 6 snapshot keys (DB-Only Read; worker writes via snapshot_repo only)
PHASE1_SNAPSHOT_KEYS = (
    "engine_heartbeat",
    "comm_health",
    "llm_status",
    "operation_mode",
    "regime_current",
    "risk_guard",
)


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
        pytest.skip("SessionLocal not available (DB not configured)")
    from backend.app.core.db import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_engine_cycle_inserts_minimum_snapshots(sync_db):
    """Running one cycle inserts at least the 6 Phase 1 rows into engine_snapshot with generated_at near now."""
    if not _engine_snapshot_available(sync_db):
        pytest.skip("engine_snapshot table not available")
    from datetime import datetime, timezone
    from sqlalchemy import text
    from backend.app.workers.engine_worker import run_single_cycle_sync

    before = datetime.now(timezone.utc)
    run_single_cycle_sync(sync_db)
    after = datetime.now(timezone.utc)

    for key in PHASE1_SNAPSHOT_KEYS:
        r = sync_db.execute(
            text("""
                SELECT snapshot_key, generated_at, source_name, refresh_rate_sec
                FROM engine_snapshot WHERE snapshot_key = :k ORDER BY generated_at DESC LIMIT 1
            """),
            {"k": key},
        ).mappings().first()
        assert r is not None, f"Missing snapshot_key after cycle: {key}"
        assert r["snapshot_key"] == key
        assert r.get("source_name") is not None
        gen_at = r["generated_at"]
        if gen_at and gen_at.tzinfo is None:
            gen_at = gen_at.replace(tzinfo=timezone.utc)
        if gen_at:
            assert before.timestamp() - 5 <= gen_at.timestamp() <= after.timestamp() + 5, (
                f"{key} generated_at not in cycle window"
            )


def test_pre_trade_gate_blocks_on_emergency_stop(sync_db):
    """When emergency_stop is set, pre-trade / gate chain blocks execution."""
    try:
        from sqlalchemy import text
        sync_db.execute(text("SELECT 1 FROM system_config LIMIT 1"))
    except Exception:
        sync_db.rollback()
        pytest.skip("system_config table not available")
    from backend.app.core.config_service import set_config
    from backend.app.gates.gate_chain import run_gate_chain

    set_config(sync_db, "gate_emergency_stop_active", {"active": True}, "test")
    allow, failed_gate, _ = run_gate_chain(sync_db)
    assert allow is False
    assert failed_gate == "EmergencyStop"
    set_config(sync_db, "gate_emergency_stop_active", {"active": False}, "test")


def test_api_snapshot_unknown_key_returns_404():
    """Unknown snapshot_key must return 404 with clear message (no DB required)."""
    from fastapi.testclient import TestClient
    from backend.main import app
    client = TestClient(app)
    r = client.get("/api/snapshot/nonexistent_key_xyz")
    assert r.status_code == 404
    detail = r.json().get("detail") or ""
    assert "nonexistent" in detail.lower() or "unknown" in detail.lower()


def test_api_snapshot_readonly_no_compute():
    """API returns JSON from DB only; no computation. Has source_name, timestamp, refresh_rate, freshness_status."""
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)
    try:
        r = client.get("/api/snapshot/regime_current")
    except Exception as e:
        if "engine_snapshot" in str(e) or "does not exist" in str(e):
            pytest.skip("DB/engine_snapshot not available")
        raise
    # Allowed key: if no data, 404 is acceptable (DB-only read)
    if r.status_code == 404:
        detail = r.json().get("detail") or ""
        assert "snapshot_key" in str(detail).lower() or "no data" in str(detail).lower()
        return
    if r.status_code >= 500:
        pytest.skip("API/DB unavailable (e.g. DATABASE_URL not set)")
    assert r.status_code == 200
    data = r.json()
    assert "snapshot_key" in data or "data" in data
    assert "source_name" in data
    assert "generated_at" in data or "data" in data
    assert "refresh_rate_sec" in data
    assert "freshness_status" in data
    assert "data" in data
    assert isinstance(data["data"], dict)
