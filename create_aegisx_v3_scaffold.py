"""
Aegis-x v3 scaffold generator (SE-65 Architecture Lock)

Usage (PowerShell):
  python .\create_aegisx_v3_scaffold.py --root "C:\dev\Aegis-x_v3"
  python .\create_aegisx_v3_scaffold.py --root "C:\dev\Aegis-x_v3" --force

Notes:
- Windows 11 friendly
- No external dependencies
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass(frozen=True)
class FileSpec:
    relpath: str
    content: str


DIRS = [
    "backend/app/core",
    "backend/app/engines",
    "backend/app/gates",
    "backend/app/execution",
    "backend/app/workers",
    "backend/app/api",
    "backend/app/models",
    "backend/app/utils",
    "backend/tests/e2e",
    "backend/tests/unit",
    "backend/tests/fixtures",
    "docs",
]

FILES: Dict[str, str] = {
    # Root
    "README.md": """# Aegis-x v3

Design Freeze: SE-01 ~ SE-65 (Architecture Lock)

Key invariants:
- DB-First / UI reads snapshots only
- Mode enforcement: BACKTEST / PAPER / PILOT / FULL_LIVE
- Pilot Ramp: P1~P4 via system_config + Gate enforcement
- Pre-trade multi-gate risk system
- Follow-the-sun session policy
- Capital scaling strategy

""",
    ".env.example": """# PostgreSQL
POSTGRES_PASSWORD=change_me

# App DB URL (example)
DATABASE_URL=postgresql+psycopg2://aegis_user:change_me@localhost:5432/aegis

# KIS (single account)
KIS_APP_KEY=
KIS_APP_SECRET=
KIS_CANO=
KIS_ACNT_PRDT_CD=

# LLM keys (Windows user env vars recommended; keep empty here)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
DEEPSEEK_API_KEY=
""",
    "docker-compose.yml": """version: "3.9"
services:
  aegis_postgres:
    image: postgres:15
    container_name: aegis_pg
    restart: always
    environment:
      POSTGRES_DB: aegis
      POSTGRES_USER: aegis_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - aegis_pg_data:/var/lib/postgresql/data
volumes:
  aegis_pg_data:
""",
    # Backend entry
    "backend/main.py": """from fastapi import FastAPI

app = FastAPI(title="Aegis-x v3")

# Routers (attach later)
# from app.api import health, control, cic, pilot
# app.include_router(health.router, prefix="/api")
# app.include_router(control.router, prefix="/api")
# app.include_router(cic.router, prefix="/api")
# app.include_router(pilot.router, prefix="/api")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
""",
    # Core
    "backend/app/core/db.py": """from __future__ import annotations

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "")

# NOTE: tune pool sizing later in hardening phase
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=3,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
    "backend/app/core/snapshot_repo.py": """from __future__ import annotations

import json
from sqlalchemy import text

def insert_snapshot(db, snapshot_key: str, snapshot_data: dict, freshness_status: str,
                    source_name: str, refresh_rate_sec: int | None = None) -> None:
    q = text(\"\"\"
        INSERT INTO engine_snapshot (snapshot_key, snapshot_data, freshness_status, source_name, refresh_rate_sec)
        VALUES (:k, :d::jsonb, :f, :s, :r)
    \"\"\")
    db.execute(q, {
        "k": snapshot_key,
        "d": json.dumps(snapshot_data, ensure_ascii=False),
        "f": freshness_status,
        "s": source_name,
        "r": refresh_rate_sec
    })
    db.commit()

def get_latest_snapshot(db, snapshot_key: str) -> dict | None:
    q = text(\"\"\"
        SELECT snapshot_data, freshness_status, source_name, refresh_rate_sec, generated_at
        FROM engine_snapshot
        WHERE snapshot_key = :k
        ORDER BY generated_at DESC
        LIMIT 1
    \"\"\")
    row = db.execute(q, {"k": snapshot_key}).fetchone()
    if not row:
        return None
    return {
        "snapshot_data": row[0],
        "freshness_status": row[1],
        "source_name": row[2],
        "refresh_rate_sec": row[3],
        "generated_at": row[4],
    }
""",
    "backend/app/core/incident_repo.py": """from __future__ import annotations

from sqlalchemy import text

def create_incident(db, severity: str, category: str, message: str,
                    related_snapshot_key: str | None = None) -> None:
    q = text(\"\"\"
        INSERT INTO incident_log (severity, category, message, related_snapshot_key)
        VALUES (:s, :c, :m, :k)
    \"\"\")
    db.execute(q, {"s": severity, "c": category, "m": message, "k": related_snapshot_key})
    db.commit()
""",
    "backend/app/core/command_repo.py": """from __future__ import annotations

import json
from sqlalchemy import text

def log_command(db, command_type: str, issued_by: str, payload: dict, status: str) -> None:
    q = text(\"\"\"
        INSERT INTO command_log (command_type, issued_by, command_payload, status)
        VALUES (:t, :u, :p::jsonb, :s)
    \"\"\")
    db.execute(q, {
        "t": command_type,
        "u": issued_by,
        "p": json.dumps(payload, ensure_ascii=False),
        "s": status
    })
    db.commit()
""",
    "backend/app/core/mode_service.py": """from __future__ import annotations

from sqlalchemy import text

VALID_MODES = ["BACKTEST", "PAPER", "PILOT", "FULL_LIVE"]

def get_current_mode(db) -> str:
    q = text(\"\"\"
        SELECT mode
        FROM system_mode
        ORDER BY changed_at DESC
        LIMIT 1
    \"\"\")
    row = db.execute(q).fetchone()
    return row[0] if row else "PAPER"
""",
    "backend/app/core/config_service.py": """from __future__ import annotations

import json
from sqlalchemy import text

def get_config(db, key: str) -> dict | None:
    q = text(\"\"\"
        SELECT config_value
        FROM system_config
        WHERE config_key = :k
        ORDER BY updated_at DESC
        LIMIT 1
    \"\"\")
    row = db.execute(q, {"k": key}).fetchone()
    return row[0] if row else None

def set_config(db, key: str, value: dict, updated_by: str) -> None:
    q = text(\"\"\"
        INSERT INTO system_config (config_key, config_value, updated_by)
        VALUES (:k, :v::jsonb, :u)
    \"\"\")
    db.execute(q, {"k": key, "v": json.dumps(value, ensure_ascii=False), "u": updated_by})
    db.commit()
""",
    "backend/app/core/resource_monitor.py": """from __future__ import annotations

# Placeholder for hardening phase (psutil etc.)
def detect_resource_tier() -> str:
    return "normal"
""",
    # Engines (DB I/O 금지: 입력 dict -> 출력 dict)
    "backend/app/engines/regime_engine.py": """from __future__ import annotations

from datetime import datetime, timezone

def compute_regime(inputs: dict) -> dict:
    # TODO: implement real regime math (Goldilocks/Sideways/Tapering/Crisis)
    return {
        "regime_state": "Sideways",
        "regime_score": 0.0,
        "crisis_probability": 0.2,
        "inputs_summary": inputs,
        "computed_at_utc": datetime.now(timezone.utc).isoformat()
    }
""",
    "backend/app/engines/allocation_engine.py": """from __future__ import annotations

def compute_allocation(regime: dict) -> dict:
    # TODO: implement allocation matrix from regime
    return {
        "base_weights": {"CORE": 0.35, "SWING": 0.35, "STRIKE": 0.20, "RESERVE": 0.10},
        "regime_state": regime.get("regime_state"),
    }
""",
    "backend/app/engines/fleet_budget_engine.py": """from __future__ import annotations

def compute_fleet_budget(allocation: dict, pilot_config: dict | None) -> dict:
    weights = allocation.get("base_weights", {})
    if pilot_config and not pilot_config.get("strike_enabled", False):
        weights = dict(weights)
        weights["STRIKE"] = 0.0
        # push remainder to RESERVE (simple MVP)
        remain = 1.0 - (weights.get("CORE", 0) + weights.get("SWING", 0) + weights.get("STRIKE", 0))
        weights["RESERVE"] = max(0.0, remain)

    return {"weights": weights}
""",
    "backend/app/engines/capital_scaling.py": """from __future__ import annotations

import math

def aggression_factor(G: float, Amax: float = 1.4, Amin: float = 0.7, k: float = 0.2) -> float:
    if G <= 0:
        return Amax
    val = Amax - k * math.log(G)
    return max(Amin, min(Amax, val))
""",
    "backend/app/engines/health_engine.py": """from __future__ import annotations

from datetime import datetime, timezone

def compute_health_status(inputs: dict) -> dict:
    # TODO: inputs will include snapshot times, db status, kis status, llm status, etc.
    return {
        "snapshot_freshness": "GREEN",
        "critical_incidents_last_hour": 0,
        "generated_at_utc": datetime.now(timezone.utc).isoformat()
    }
""",
    "backend/app/engines/strike_engine.py": "# TODO: Strike engine spec\n",
    "backend/app/engines/swing_engine.py": "# TODO: Swing engine spec\n",
    "backend/app/engines/core_engine.py": "# TODO: Core engine spec\n",
    # Gates
    "backend/app/gates/pre_trade_gate.py": """from __future__ import annotations

def run_pre_trade_gate() -> tuple[bool, list]:
    # TODO: Mode/Freshness/Risk/Cap/Daily-entry gates in strict order
    return True, [("PLACEHOLDER", True, "OK")]
""",
    "backend/app/gates/cap_gate.py": "# TODO: cap gate\n",
    "backend/app/gates/risk_gate.py": "# TODO: risk gate\n",
    "backend/app/gates/freshness_gate.py": "# TODO: freshness gate\n",
    "backend/app/gates/mode_gate.py": "# TODO: mode gate\n",
    "backend/app/gates/crisis_gate.py": "# TODO: crisis gate\n",
    # Execution
    "backend/app/execution/paper_executor.py": "# TODO: paper executor\n",
    "backend/app/execution/kis_executor.py": "# TODO: kis executor\n",
    # Workers
    "backend/app/workers/engine_worker.py": """from __future__ import annotations

from datetime import datetime, timezone

from app.core.snapshot_repo import insert_snapshot
from app.core.config_service import get_config
from app.engines.regime_engine import compute_regime
from app.engines.allocation_engine import compute_allocation
from app.engines.fleet_budget_engine import compute_fleet_budget
from app.engines.health_engine import compute_health_status

def run_single_cycle(db) -> None:
    # 1) Heartbeat
    hb = {"engine_loop_alive": True, "timestamp_utc": datetime.now(timezone.utc).isoformat()}
    insert_snapshot(db, "engine_heartbeat", hb, "GREEN", "EngineWorker", refresh_rate_sec=60)

    # 2) Health (MVP)
    health = compute_health_status({})
    insert_snapshot(db, "health_status", health, health.get("snapshot_freshness", "GREEN"), "HealthEngine", refresh_rate_sec=60)

    # 3) Regime → Allocation → Fleet Budget
    regime = compute_regime({})
    insert_snapshot(db, "regime_current", regime, "GREEN", "RegimeEngine", refresh_rate_sec=120)

    allocation = compute_allocation(regime)
    insert_snapshot(db, "allocation_matrix", allocation, "GREEN", "AllocationEngine", refresh_rate_sec=120)

    pilot_config = get_config(db, "pilot_config")
    fleet_budget = compute_fleet_budget(allocation, pilot_config)
    insert_snapshot(db, "fleet_budget_snapshot", fleet_budget, "GREEN", "FleetBudgetEngine", refresh_rate_sec=120)

    # 4) Portfolio state (MVP placeholder)
    portfolio_state = {"total_equity": 0, "cash": 0, "positions": [], "timestamp_utc": datetime.now(timezone.utc).isoformat()}
    insert_snapshot(db, "portfolio_state", portfolio_state, "GREEN", "PortfolioStateEngine", refresh_rate_sec=120)
""",
    "backend/app/workers/ingest_worker.py": "# TODO: ingest worker (ext_event_raw)\n",
    # API routers
    "backend/app/api/health.py": """from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.snapshot_repo import get_latest_snapshot

router = APIRouter()

@router.get("/health")
def api_health(db: Session = Depends(get_db)):
    return {
        "engine_heartbeat": get_latest_snapshot(db, "engine_heartbeat"),
        "health_status": get_latest_snapshot(db, "health_status"),
    }
""",
    "backend/app/api/control.py": "# TODO: control router (mode, freeze, retract, stop)\n",
    "backend/app/api/cic.py": "# TODO: CIC router (DB snapshots only)\n",
    "backend/app/api/pilot.py": "# TODO: pilot router (pilot_step changes + audit)\n",
    # Models
    "backend/app/models/schemas.py": "# TODO: pydantic schemas\n",
    # Utils
    "backend/app/utils/time_utils.py": """from __future__ import annotations

from datetime import datetime, timezone

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
""",
    # Docs placeholder
    "docs/SE-65_Final_Directory_Architecture_Lock_Spec.md": """# SE-65 Final Directory Architecture Lock Spec
Design Freeze: v3.0

This folder structure must not be changed without a version bump and changelog entry.
""",
}


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def create_scaffold(root: Path, force: bool) -> None:
    ensure_dir(root)

    # Create directories
    for d in DIRS:
        ensure_dir(root / d)

    # Make packages importable (add __init__.py)
    init_dirs = [
        "backend/app",
        "backend/app/core",
        "backend/app/engines",
        "backend/app/gates",
        "backend/app/execution",
        "backend/app/workers",
        "backend/app/api",
        "backend/app/models",
        "backend/app/utils",
    ]
    for d in init_dirs:
        write_file(root / d / "__init__.py", "", force=False)

    # Write files
    for rel, content in FILES.items():
        write_file(root / rel, content, force=force)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Create Aegis-x v3 scaffold (SE-65)")
    ap.add_argument("--root", required=True, help="Target root folder, e.g. C:\\dev\\Aegis-x_v3")
    ap.add_argument("--force", action="store_true", help="Overwrite existing stub files")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    create_scaffold(root, force=args.force)
    print(f"[OK] Aegis-x v3 scaffold created at: {root}")


if __name__ == "__main__":
    main()