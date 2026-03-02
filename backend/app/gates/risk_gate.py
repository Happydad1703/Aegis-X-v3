# gates/risk_gate.py — SE-50: Risk Gate. Level 1 Tactical + USD/FX extension (Section 3).
# Portfolio DD ≤ -8% OR VolSpike ≥ 1.8 OR usd_exposure_ratio > usd_limit OR fx_volatility > fx_vol_cap → block.

from __future__ import annotations

# SE-39/50 수식 고착화 상수
DD_BLOCK_THRESHOLD = -0.08   # -8%
STRIKE_BLOCK_DD = -0.10     # dd < -10% → block_strike() (Spec Lock v1.0)
VOL_SPIKE_BLOCK_THRESHOLD = 1.8
# USD/FX defaults when config missing
DEFAULT_USD_LIMIT = 0.5
DEFAULT_FX_VOL_CAP = 0.15


def _get_usd_limits(db) -> tuple[float, float]:
    """usd_limit, fx_vol_cap from system_config usd_risk_limits."""
    try:
        from backend.app.core.config_service import get_config
        cfg = get_config(db, "usd_risk_limits")
        if isinstance(cfg, dict):
            return float(cfg.get("usd_limit", DEFAULT_USD_LIMIT)), float(cfg.get("fx_vol_cap", DEFAULT_FX_VOL_CAP))
    except Exception:
        pass
    return DEFAULT_USD_LIMIT, DEFAULT_FX_VOL_CAP


def run_risk_gate(db) -> tuple[bool, str]:
    """
    risk_guard + usd_exposure_status (DB) 기반.
    DD/VolSpike 기존. 추가: usd_exposure_ratio <= usd_limit, fx_volatility <= fx_vol_cap.
    Violation 시 Level 1/2 alarm (incident_log) and block.
    """
    try:
        from backend.app.core.snapshot_repo import get_latest_snapshot_sync
    except Exception:
        return False, "snapshot_repo unavailable"
    row = get_latest_snapshot_sync(db, "risk_guard")
    if not row:
        return True, "no risk_guard snapshot"
    data = row.get("snapshot_data") or {}
    if not isinstance(data, dict):
        return True, "risk_guard invalid"
    dd = data.get("portfolio_dd")
    vol = data.get("vol_spike")
    if dd is not None and isinstance(dd, (int, float)) and dd <= DD_BLOCK_THRESHOLD:
        return False, f"Portfolio DD {dd} <= {DD_BLOCK_THRESHOLD}"
    if vol is not None and isinstance(vol, (int, float)) and vol >= VOL_SPIKE_BLOCK_THRESHOLD:
        return False, f"Vol spike {vol} >= {VOL_SPIKE_BLOCK_THRESHOLD}"

    # USD/FX extension: usd_exposure_ratio, fx_volatility (risk_guard or usd_exposure_status)
    usd_ratio = data.get("usd_exposure_ratio")
    fx_vol = data.get("fx_volatility")
    if usd_ratio is None or fx_vol is None:
        row2 = get_latest_snapshot_sync(db, "usd_exposure_status")
        if row2 and isinstance(row2.get("snapshot_data"), dict):
            d2 = row2["snapshot_data"]
            if usd_ratio is None:
                usd_ratio = d2.get("usd_exposure_ratio")
            if fx_vol is None:
                fx_vol = d2.get("fx_volatility")
    usd_limit, fx_vol_cap = _get_usd_limits(db)
    if usd_ratio is not None and isinstance(usd_ratio, (int, float)) and usd_ratio > usd_limit:
        try:
            from backend.app.core.incident_repo import create_incident
            create_incident(db, "WARNING", "USD_EXPOSURE", f"usd_exposure_ratio {usd_ratio} > {usd_limit}", "risk_guard")
        except Exception:
            pass
        return False, f"USD exposure {usd_ratio} > {usd_limit}"
    if fx_vol is not None and isinstance(fx_vol, (int, float)) and fx_vol > fx_vol_cap:
        try:
            from backend.app.core.incident_repo import create_incident
            create_incident(db, "WARNING", "FX_VOLATILITY", f"fx_volatility {fx_vol} > {fx_vol_cap}", "risk_guard")
        except Exception:
            pass
        return False, f"FX volatility {fx_vol} > {fx_vol_cap}"
    return True, "risk OK"


def get_strike_blocked(db) -> bool:
    """Spec Lock v1.0: risk_guard dd < -0.10 → block Strike 전략만. Executor가 STRIKE intent 필터링 시 사용."""
    try:
        from backend.app.core.snapshot_repo import get_latest_snapshot_sync
    except Exception:
        return False
    row = get_latest_snapshot_sync(db, "risk_guard")
    if not row or not isinstance(row.get("snapshot_data"), dict):
        return False
    dd = row["snapshot_data"].get("portfolio_dd")
    if dd is None or not isinstance(dd, (int, float)):
        return False
    return float(dd) < STRIKE_BLOCK_DD
