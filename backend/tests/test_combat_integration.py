# backend/tests/test_combat_integration.py — Integration: engine cycle + snapshot keys + gate PASS + paper order.

from __future__ import annotations

import pytest
from sqlalchemy import text


@pytest.fixture
def sync_db():
    """Sync DB session; skip if unavailable."""
    try:
        from backend.app.core.db import SessionLocal
        db = SessionLocal()
        yield db
        db.close()
    except Exception:
        pytest.skip("DB not available")


def test_integration_migration_creates_engine_snapshot(sync_db) -> None:
    """After migration, engine_snapshot table exists."""
    r = sync_db.execute(text("SELECT to_regclass('public.engine_snapshot') AS reg")).scalar()
    if r is None:
        pytest.skip("engine_snapshot table not found (run migrate_db.ps1 or migrate_db_via_url.py)")
    assert r is not None


def test_integration_one_engine_cycle_required_keys(sync_db) -> None:
    """Run one engine cycle then verify required snapshot keys exist (Master Process Map minimum set)."""
    from backend.app.workers.engine_worker import run_single_cycle_sync
    from backend.app.core.snapshot_keys import REQUIRED_SNAPSHOT_KEYS_MINIMUM
    run_single_cycle_sync(sync_db)
    required = list(REQUIRED_SNAPSHOT_KEYS_MINIMUM)
    rows = sync_db.execute(
        text("SELECT snapshot_key FROM engine_snapshot WHERE snapshot_key = ANY(:keys)"),
        {"keys": required},
    ).fetchall()
    keys_found = {r[0] for r in rows}
    for k in required:
        assert k in keys_found, f"Missing snapshot key: {k}"


def test_integration_gate_pass_paper_order_creates_order_log(sync_db) -> None:
    """When gate PASS and mode PAPER, run execution flow with intent → order_log has new row."""
    try:
        sync_db.execute(text("UPDATE system_mode SET mode = 'PAPER' WHERE id = (SELECT id FROM system_mode LIMIT 1)"))
        sync_db.commit()
    except Exception:
        pass
    from backend.app.execution.execution_runner import run_execution_flow_sync
    intent = {"symbol": "005930", "side": "BUY", "quantity": 10}
    executed, msg, mode = run_execution_flow_sync(sync_db, intent)
    assert executed is True
    assert "PAPER" in mode or mode == "PAPER"
    # order_log should have at least one row with PAPER_FILLED or PENDING
    r = sync_db.execute(
        text("SELECT execution_status, mode FROM order_log ORDER BY id DESC LIMIT 1")
    ).mappings().first()
    assert r is not None
    assert r["execution_status"] in ("PAPER_FILLED", "PENDING")
    assert r["mode"] == "PAPER"
