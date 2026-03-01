# backend/app/workers/engine_worker.py — SE-64: Worker produces snapshots via snapshot_repo only.
from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import ProgrammingError

from backend.app.core.snapshot_keys import get_required_snapshot_keys_for_cycle
from backend.app.core.snapshot_repo import insert_snapshot, insert_snapshot_sync
from backend.app.engines.regime_engine import compute_regime
from backend.app.engines.allocation_engine import compute_allocation
from backend.app.engines.fleet_budget_engine import compute_fleet_budget
from backend.app.engines.core_engine import compute_core_force


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _regime_inputs_from_db(db: Session) -> dict:
    """Build regime engine input from DB (worker may read). ext_event_raw 없으면 0으로 처리."""
    try:
        r = db.execute(text("SELECT COUNT(*) AS c FROM ext_event_raw")).scalar()
        count = int(r) if r is not None else 0
    except ProgrammingError:
        db.rollback()
        count = 0  # 테이블 미존재 시 마이그레이션 재실행 권장
    return {"events_count": count, "trend_score": 0.0, "volatility_state": "normal"}


def _build_placeholder_snapshots(now: str, regime_payload: dict | None = None) -> dict:
    """Phase 0-1/1: placeholder payload; regime_current uses regime_engine output when provided."""
    keys = get_required_snapshot_keys_for_cycle()
    payloads = {
        "engine_heartbeat": {"status": "alive", "ts_utc": now},
        "comm_health": {"status": "unknown", "ts_utc": now},
        "regime_current": regime_payload or {"regime": "unknown", "ts_utc": now},
        "operation_mode": {"mode": "Backtest", "ts_utc": now},
        "llm_status": {"status": "unknown", "ts_utc": now},
        "risk_guard": {"status": "unknown", "ts_utc": now},
    }
    return {k: payloads.get(k, {"ts_utc": now}) for k in keys}


async def run_single_cycle(db: AsyncSession) -> None:
    # (Phase 0-2+에서 async 경로 사용 — 동일 6종 키, SSOT: snapshot_keys)
    now = _utc_now_iso()
    snapshots = _build_placeholder_snapshots(now)
    for k, payload in snapshots.items():
        await insert_snapshot(
            db,
            snapshot_key=k,
            snapshot_data=payload,
            freshness_status="GREEN",
            source_name="engine_worker",
            refresh_rate_sec=60,
        )


def run_single_cycle_sync(db: Session) -> None:
    # Phase 1+2: regime_current from regime_engine; allocation_matrix, fleet_budget_snapshot, core_force_state from engines
    now = _utc_now_iso()
    inputs = _regime_inputs_from_db(db)
    regime_payload = compute_regime(inputs)
    snapshots = _build_placeholder_snapshots(now, regime_payload=regime_payload)
    for k, payload in snapshots.items():
        insert_snapshot_sync(
            db,
            snapshot_key=k,
            snapshot_data=payload,
            freshness_status="GREEN",
            source_name="engine_worker",
            refresh_rate_sec=60,
        )
    allocation_payload = compute_allocation(regime_payload)
    insert_snapshot_sync(db, snapshot_key="allocation_matrix", snapshot_data=allocation_payload, freshness_status="GREEN", source_name="engine_worker", refresh_rate_sec=300)
    fleet_payload = compute_fleet_budget(allocation_payload, None)
    insert_snapshot_sync(db, snapshot_key="fleet_budget_snapshot", snapshot_data=fleet_payload, freshness_status="GREEN", source_name="engine_worker", refresh_rate_sec=300)
    core_input = {"regime_current": regime_payload, "battlefield_state": {}, "allocation_matrix": allocation_payload, "fleet_budget_snapshot": fleet_payload, "risk_guard": snapshots.get("risk_guard"), "macro_context": {}, "portfolio_growth_rate": 0.0}
    core_payload = compute_core_force(core_input)
    insert_snapshot_sync(db, snapshot_key="core_force_state", snapshot_data=core_payload, freshness_status="GREEN", source_name="core_engine", refresh_rate_sec=3600)
