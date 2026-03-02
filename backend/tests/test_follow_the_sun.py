# backend/tests/test_follow_the_sun.py — 24/7 Follow-the-Sun minimal safe build (Section 7).

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
    """Skip if system_config table does not exist (e.g. DB not migrated)."""
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


class TestSessionSwitchUniverseOnly:
    """1. Session switch changes universe only."""

    def test_universe_selector_kr_returns_korea_universe(self):
        from backend.app.core.universe_selector import universe_selector, KOREA_UNIVERSE
        u = universe_selector("KR")
        assert u.get("session") == "KR"
        assert u.get("market") == KOREA_UNIVERSE.get("market")

    def test_universe_selector_us_returns_us_universe(self):
        from backend.app.core.universe_selector import universe_selector, US_UNIVERSE
        u = universe_selector("US")
        assert u.get("session") == "US"
        assert u.get("market") == US_UNIVERSE.get("market")

    def test_universe_selector_off_returns_empty_universe(self):
        from backend.app.core.universe_selector import universe_selector, EMPTY_UNIVERSE
        u = universe_selector("OFF")
        assert u.get("session") == "OFF"
        assert u.get("market") is None


class TestEnginesRemainPure:
    """2. Engines remain pure (no SQL)."""

    def test_regime_engine_accepts_universe_input_no_sql(self):
        from backend.app.engines.regime_engine import compute_regime
        inputs = {"events_count": 0, "trend_score": 0.0, "volatility_state": "normal", "universe": {"session": "KR", "symbols": []}}
        out = compute_regime(inputs)
        assert isinstance(out, dict)
        assert "regime_label" in out or "regime" in out

    def test_allocation_engine_pure_dict_in_dict_out(self):
        from backend.app.engines.allocation_engine import compute_allocation
        regime = {"regime_label": "Sideways", "crisis_probability": 0.1}
        out = compute_allocation(regime)
        assert isinstance(out, dict)
        assert "base_weights" in out


class TestOffSessionBlocksNewTrades:
    """3. OFF session blocks new trades (gate layer)."""

    def test_off_session_blocks_gate_chain(self, sync_db):
        if not _system_config_available(sync_db):
            pytest.skip("system_config table not available")
        from backend.app.core.snapshot_repo import insert_snapshot_sync
        from backend.app.gates.gate_chain import run_gate_chain
        from backend.app.core.config_service import set_config
        set_config(sync_db, "gate_emergency_stop_active", {"active": False}, "test")
        set_config(sync_db, "gate_retract_active", {"active": False}, "test")
        insert_snapshot_sync(
            sync_db,
            snapshot_key="active_session",
            snapshot_data={"session": "OFF", "ts_utc": "2025-01-01T12:00:00Z"},
            freshness_status="GREEN",
            source_name="test",
            refresh_rate_sec=60,
        )
        allow, failed_gate, _ = run_gate_chain(sync_db)
        assert allow is False
        assert failed_gate == "Session"


class TestUsdExposureTriggersRiskGate:
    """4. USD exposure violation triggers risk gate."""

    def test_high_usd_exposure_blocks_risk_gate(self, sync_db):
        if not _system_config_available(sync_db):
            pytest.skip("system_config table not available")
        from backend.app.core.snapshot_repo import insert_snapshot_sync
        from backend.app.gates.risk_gate import run_risk_gate
        from backend.app.core.config_service import set_config
        set_config(sync_db, "usd_risk_limits", {"usd_limit": 0.3, "fx_vol_cap": 0.15}, "test")
        insert_snapshot_sync(
            sync_db,
            snapshot_key="usd_exposure_status",
            snapshot_data={"usd_exposure_ratio": 0.5, "fx_volatility": 0.05, "ts_utc": "2025-01-01T12:00:00Z"},
            freshness_status="GREEN",
            source_name="test",
            refresh_rate_sec=300,
        )
        # risk_gate uses risk_guard first; if no usd there, falls back to usd_exposure_status
        insert_snapshot_sync(
            sync_db,
            snapshot_key="risk_guard",
            snapshot_data={"portfolio_dd": None, "vol_spike": None, "usd_exposure_ratio": 0.5, "fx_volatility": 0.05},
            freshness_status="GREEN",
            source_name="test",
            refresh_rate_sec=60,
        )
        ok, msg = run_risk_gate(sync_db)
        assert ok is False
        assert "USD" in msg or "0.5" in msg

    def test_fx_volatility_spike_blocks_risk_gate(self, sync_db):
        if not _system_config_available(sync_db):
            pytest.skip("system_config table not available")
        from backend.app.core.snapshot_repo import insert_snapshot_sync
        from backend.app.gates.risk_gate import run_risk_gate
        from backend.app.core.config_service import set_config
        set_config(sync_db, "usd_risk_limits", {"usd_limit": 0.5, "fx_vol_cap": 0.10}, "test")
        insert_snapshot_sync(
            sync_db,
            snapshot_key="risk_guard",
            snapshot_data={"portfolio_dd": None, "vol_spike": None, "usd_exposure_ratio": 0.2, "fx_volatility": 0.25},
            freshness_status="GREEN",
            source_name="test",
            refresh_rate_sec=60,
        )
        ok, msg = run_risk_gate(sync_db)
        assert ok is False
        assert "FX" in msg or "0.25" in msg


class TestSnapshotContainsSessionMetadata:
    """5. Snapshot contains session metadata."""

    def test_allowed_snapshot_keys_include_session_keys(self):
        from backend.app.core.snapshot_keys import ALLOWED_SNAPSHOT_KEYS
        for key in ("active_session", "session_state", "timezone", "usd_exposure_status"):
            assert key in ALLOWED_SNAPSHOT_KEYS

    def test_is_allowed_snapshot_key_session_keys(self):
        from backend.app.core.snapshot_keys import is_allowed_snapshot_key
        assert is_allowed_snapshot_key("active_session") is True
        assert is_allowed_snapshot_key("session_state") is True
        assert is_allowed_snapshot_key("timezone") is True
        assert is_allowed_snapshot_key("usd_exposure_status") is True


class TestGatePriorityOrderUnchanged:
    """6. Gate priority order unchanged."""

    def test_gate_order_still_linear(self):
        from backend.app.gates.gate_chain import GATE_ORDER, GATE_EMERGENCY_STOP, GATE_RETRACT, GATE_MODE, GATE_RISK
        assert GATE_ORDER[0] == GATE_EMERGENCY_STOP
        assert GATE_ORDER[1] == GATE_RETRACT
        assert GATE_MODE in GATE_ORDER
        assert GATE_RISK in GATE_ORDER

    def test_session_multiplier_kr_one_off_zero(self):
        from backend.app.core.timezone_service import get_session_multiplier
        assert get_session_multiplier("KR", None) == 1.0
        assert get_session_multiplier("OFF", None) == 0.0
        assert 0 < get_session_multiplier("US", None) <= 1.0


class TestTimezoneSession:
    """get_current_session returns KR | US | OFF from config or defaults."""

    def test_get_current_session_without_db_uses_defaults(self):
        from backend.app.core.timezone_service import get_current_session
        # 02:00 UTC -> KR window 00:00-06:30
        from datetime import datetime, timezone
        kr_time = datetime(2025, 1, 1, 2, 0, 0, tzinfo=timezone.utc)
        assert get_current_session(kr_time, None) == "KR"
        us_time = datetime(2025, 1, 1, 15, 0, 0, tzinfo=timezone.utc)
        assert get_current_session(us_time, None) == "US"
        off_time = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        assert get_current_session(off_time, None) == "OFF"


class TestSessionAllocationHelper:
    """Section 6: session_multiplier applied to fleet_budget at read time."""

    def test_apply_session_multiplier_adds_key(self):
        from backend.app.core.session_allocation import apply_session_multiplier_to_fleet_budget
        fleet = {"weights": {"CORE": 0.35}, "regime_label": "Sideways"}
        session_state = {"snapshot_data": {"session_multiplier": 0.7}}
        out = apply_session_multiplier_to_fleet_budget(fleet, session_state)
        assert out.get("session_multiplier") == 0.7
        assert out.get("weights") == fleet["weights"]
        assert out.get("regime_label") == "Sideways"
