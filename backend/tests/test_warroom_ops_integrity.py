from __future__ import annotations

import inspect
from pathlib import Path

from backend.app.api import control
from backend.app.core.snapshot_keys import ALLOWED_SNAPSHOT_KEYS
from backend.app.core import snapshot_repo
from backend.app.workers import engine_worker
from backend.app.execution import comm_health_service
from backend.app.core import portfolio_reconciliation_service
from backend.app.core import execution_feedback_service


def test_incident_trigger_snapshot_keys_exist() -> None:
    required = {
        "risk_guard",
        "comm_health",
        "portfolio_ground_truth",
        "execution_orders_latest",
    }
    missing = sorted(required.difference(ALLOWED_SNAPSHOT_KEYS))
    assert not missing, f"incident trigger snapshot keys missing: {missing}"


def test_incident_trigger_snapshots_are_queryable_via_snapshot_repo() -> None:
    assert callable(snapshot_repo.get_latest_snapshot_sync)
    assert callable(snapshot_repo.get_latest_snapshot)


def test_incident_trigger_snapshot_writers_exist() -> None:
    src_engine_worker = inspect.getsource(engine_worker)
    src_comm_health = inspect.getsource(comm_health_service)
    src_reconcile = inspect.getsource(portfolio_reconciliation_service)
    src_feedback = inspect.getsource(execution_feedback_service)

    # risk_guard is written by engine_worker via placeholder snapshot map / cycle writer.
    assert '"risk_guard"' in src_engine_worker
    assert 'snapshot_key="comm_health"' in src_comm_health
    assert 'snapshot_key="portfolio_ground_truth"' in src_reconcile
    assert 'snapshot_key="execution_orders_latest"' in src_feedback


def test_emergency_command_availability_in_control_layer() -> None:
    # Command endpoint supported set
    required_command_types = {"EMERGENCY_STOP", "RETRACT", "SET_MODE"}
    missing = sorted(required_command_types.difference(control.ALLOWED_COMMANDS))
    assert not missing, f"missing command_type(s) in ALLOWED_COMMANDS: {missing}"

    # RESUME is supported as dedicated endpoint in control layer.
    route_paths = {getattr(r, "path", "") for r in control.router.routes}
    assert "/api/control/resume" in route_paths


def test_runbook_presence_guard() -> None:
    root = Path(__file__).resolve().parents[2]
    runbook = root / "docs" / "ai_memory" / "WARROOM_INCIDENT_CHECKLIST.md"
    assert runbook.is_file(), f"missing runbook file: {runbook}"


def test_office_home_context_files_presence_guard() -> None:
    root = Path(__file__).resolve().parents[2]
    required = (
        root / "docs" / "ai_memory" / "AI_CONTEXT_INDEX.md",
        root / "docs" / "ai_memory" / "AI_SESSION_STATE.md",
        root / "docs" / "ai_memory" / "OFFICE_HOME_HANDOFF_PROTOCOL.md",
    )
    missing = [str(p) for p in required if not p.is_file()]
    assert not missing, f"missing Office/Home context file(s): {missing}"

