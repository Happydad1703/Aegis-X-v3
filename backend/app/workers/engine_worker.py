# backend/app/workers/engine_worker.py — SE-64: Worker produces snapshots via snapshot_repo only.
# 11_Governance_Audit_Spec: Regime/Allocation 결심 시 Hash Chain 기록.
from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import ProgrammingError

from backend.app.core.snapshot_keys import get_required_snapshot_keys_for_cycle
from backend.app.core.snapshot_repo import insert_snapshot, insert_snapshot_sync
from backend.app.core.timezone_service import get_current_session, get_session_multiplier
from backend.app.core.universe_selector import universe_selector
from backend.app.engines.regime_engine import compute_regime
from backend.app.engines.allocation_engine import compute_allocation
from backend.app.engines.fleet_budget_engine import compute_fleet_budget
from backend.app.engines.core_engine import compute_core_force
from backend.app.engines.swing_engine import compute_swing
from backend.app.engines.strike_engine import compute_strike
from backend.app.core.audit_chain import append_audit_event


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
    # Phase 1+2 + Follow-the-Sun: session from timezone_service, universe from universe_selector; pass universe to engines
    now = _utc_now_iso()
    now_dt = datetime.now(timezone.utc)
    session = get_current_session(now_dt, db)
    universe = universe_selector(session)
    session_multiplier = get_session_multiplier(session, db)

    inputs = _regime_inputs_from_db(db)
    inputs["universe"] = universe
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
    # 11_Governance: Regime/Allocation 결심 Hash Chain 기록 (감사 추적)
    try:
        append_audit_event("regime", {"regime_label": regime_payload.get("regime_label"), "ts_utc": now}, payload_preview=(regime_payload.get("regime_label") or "")[:80])
        append_audit_event("allocation", {"regime_label": allocation_payload.get("regime_label"), "base_weights": allocation_payload.get("base_weights"), "ts_utc": now}, payload_preview=(str(allocation_payload.get("base_weights", "")))[:120])
    except Exception:
        pass
    fleet_payload = compute_fleet_budget(allocation_payload, None)
    insert_snapshot_sync(db, snapshot_key="fleet_budget_snapshot", snapshot_data=fleet_payload, freshness_status="GREEN", source_name="engine_worker", refresh_rate_sec=300)

    # Spec Lock v1.0: Core/Swing/Strike contract inputs from regime + battlefield (worker만 DB/외부 참조)
    regime_label = regime_payload.get("regime_label") or "Sideways"
    battlefield = {}  # TODO: from battlefield_state snapshot when available
    core_contract = {
        "regime": regime_label,
        "crisis_prob": float(regime_payload.get("crisis_probability", 0)),
        "price": float(battlefield.get("price", 0)),
        "ma60": float(battlefield.get("ma60", 0)),
        "ma120": float(battlefield.get("ma120", 0)),
        "ma120_slope": float(battlefield.get("ma120_slope", 0)),
        "relative_strength_rank": float(battlefield.get("relative_strength_rank", 0.5)),
        "current_position": float(battlefield.get("current_position", 0)),
    }
    core_payload = compute_core_force(core_contract)
    insert_snapshot_sync(db, snapshot_key="core_force_state", snapshot_data=core_payload, freshness_status="GREEN", source_name="core_engine", refresh_rate_sec=3600)
    insert_snapshot_sync(db, snapshot_key="targets_core", snapshot_data=core_payload, freshness_status="GREEN", source_name="core_engine", refresh_rate_sec=3600)

    swing_contract = {
        "regime": regime_label,
        "price": float(battlefield.get("price", 0)),
        "ma20": float(battlefield.get("ma20", 0)),
        "ma60": float(battlefield.get("ma60", 0)),
        "volume_ratio": float(battlefield.get("volume_ratio", 0)),
        "breakout_10d": bool(battlefield.get("breakout_10d", False)),
        "holding_days": int(battlefield.get("holding_days", 0)),
    }
    swing_payload = compute_swing(swing_contract)
    insert_snapshot_sync(db, snapshot_key="swing_force_state", snapshot_data=swing_payload, freshness_status="GREEN", source_name="swing_engine", refresh_rate_sec=300)
    insert_snapshot_sync(db, snapshot_key="targets_swing", snapshot_data=swing_payload, freshness_status="GREEN", source_name="swing_engine", refresh_rate_sec=300)

    strike_contract = {
        "regime": regime_label,
        "price": float(battlefield.get("price", 0)),
        "vol_spike": float(battlefield.get("vol_spike", 0)),
        "z_score": float(battlefield.get("z_score", 0)),
        "holding_days": int(battlefield.get("holding_days", 0)),
    }
    strike_payload = compute_strike(strike_contract)
    insert_snapshot_sync(db, snapshot_key="strike_force_state", snapshot_data=strike_payload, freshness_status="GREEN", source_name="strike_engine", refresh_rate_sec=300)
    insert_snapshot_sync(db, snapshot_key="targets_strike", snapshot_data=strike_payload, freshness_status="GREEN", source_name="strike_engine", refresh_rate_sec=300)

    # Follow-the-Sun: session snapshots (Section 5). Do NOT modify existing snapshot structure.
    insert_snapshot_sync(db, snapshot_key="active_session", snapshot_data={"session": session, "ts_utc": now}, freshness_status="GREEN", source_name="engine_worker", refresh_rate_sec=60)
    insert_snapshot_sync(db, snapshot_key="session_state", snapshot_data={"session": session, "session_multiplier": session_multiplier, "ts_utc": now}, freshness_status="GREEN", source_name="engine_worker", refresh_rate_sec=60)
    insert_snapshot_sync(db, snapshot_key="timezone", snapshot_data={"session": session, "utc": now}, freshness_status="GREEN", source_name="engine_worker", refresh_rate_sec=60)
    insert_snapshot_sync(db, snapshot_key="usd_exposure_status", snapshot_data={"usd_exposure_ratio": 0.0, "fx_volatility": 0.0, "ts_utc": now}, freshness_status="GREEN", source_name="engine_worker", refresh_rate_sec=300)
