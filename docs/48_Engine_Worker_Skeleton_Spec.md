47_Engine_Worker_Skeleton_Spec.md (v1.0)
1) Worker 역할(필수)
1.	DB에서 입력 데이터 조회(원칙 준수)
2.	Regime 계산(또는 stub)
3.	Allocation Matrix v2 계산(또는 stub)
4.	Fleet Budget(FBGC) 계산
5.	Strike/Swing/Core 상태 계산(최소 status snapshot)
6.	Snapshot 생성/업서트
7.	incident 생성(RED 조건)
UI는 engine_snapshot만 읽고, Worker가 snapshot을 생산한다.
________________________________________
2) 실행 모델(PC Feasible)
•	단일 프로세스 + 주기 루프(우선)
•	추후 분리: ingest_worker / engine_worker / bot_worker
권장 주기(초기)
•	engine tick: 60초
•	regime refresh: 300초(5분)
•	macro refresh: ingest에서 처리
________________________________________
3) 폴더 구조(backend 확장)
backend/
 ├─ app/
 │   ├─ main.py
 │   ├─ db.py
 │   ├─ routers/...
 │   ├─ workers/
 │   │   ├─ engine_worker.py
 │   │   ├─ snapshot_repo.py
 │   │   ├─ incident_repo.py
 │   │   ├─ regime_engine.py
 │   │   ├─ allocation_engine.py
 │   │   ├─ fleet_budget_engine.py
 │   │   └─ risk_engine.py
 │   └─ utils/
 │       ├─ timeutil.py
 │       └─ hashing.py
 ├─ scripts/
 │   └─ run_engine_worker.ps1
 └─ .env
________________________________________
✅ 4) DB Contract: Snapshot Upsert 규칙
engine_snapshot는 최신 1건만 유지하는 방식도 가능하지만,
감사/추적을 위해 append + latest 조회를 유지합니다.
다만 불필요한 폭증 방지를 위해:
•	snapshot_key별 “최소 생성 간격(min_interval_sec)” 적용
________________________________________
🧠 5) 코드 스켈레톤
5.1 workers/snapshot_repo.py
from sqlalchemy import text
from datetime import datetime, timezone

def insert_snapshot(db, snapshot_key: str, snapshot_data: dict, freshness_status: str, source_name: str):
    q = text("""
        INSERT INTO engine_snapshot (snapshot_key, snapshot_data, freshness_status, source_name, generated_at)
        VALUES (:k, :d::jsonb, :fs, :src, :ts)
    """)
    db.execute(q, {
        "k": snapshot_key,
        "d": __import__("json").dumps(snapshot_data),
        "fs": freshness_status,
        "src": source_name,
        "ts": datetime.now(timezone.utc)
    })
    db.commit()

def get_latest_snapshot_time(db, snapshot_key: str):
    q = text("""
        SELECT generated_at
        FROM engine_snapshot
        WHERE snapshot_key = :k
        ORDER BY generated_at DESC
        LIMIT 1
    """)
    row = db.execute(q, {"k": snapshot_key}).fetchone()
    return row[0] if row else None
________________________________________
5.2 workers/incident_repo.py
from sqlalchemy import text
from datetime import datetime, timezone
import json

def create_incident(db, severity: str, category: str, message: str, related_snapshot_key: str | None = None):
    q = text("""
        INSERT INTO incident_log (severity, category, message, related_snapshot_key, created_at)
        VALUES (:sev, :cat, :msg, :rel, :ts)
    """)
    db.execute(q, {
        "sev": severity,
        "cat": category,
        "msg": message,
        "rel": related_snapshot_key,
        "ts": datetime.now(timezone.utc)
    })
    db.commit()
________________________________________
5.3 workers/regime_engine.py (v1 stub → v1.0로 확장 가능)
from datetime import datetime, timezone

def compute_regime(input_data: dict) -> dict:
    # TODO: 실제 수학 모델(PS/VS/LM/SN) 연결
    # 현재는 Stub: 항상 Sideways
    return {
        "regime_state": "Sideways",
        "regime_score": 0.4,
        "crisis_probability": 0.25,
        "confidence": 0.6,
        "inputs": {"note": "stub"},
        "computed_at_utc": datetime.now(timezone.utc).isoformat()
    }
________________________________________
5.4 workers/allocation_engine.py (v2 stub)
def compute_allocation(regime: dict) -> dict:
    # TODO: W_b = Base + α*RegimeScore - β*CrisisProb 정규화 구현
    # stub
    return {
        "battlefields": {
            "KOSPI": 0.40,
            "KOSDAQ": 0.30,
            "US_PROXY": 0.20,
            "HEDGE": 0.10
        },
        "method": "stub_v2",
        "inputs": {
            "regime_state": regime.get("regime_state"),
            "crisis_probability": regime.get("crisis_probability")
        }
    }
________________________________________
5.5 workers/fleet_budget_engine.py (FBGC 구현 최소판)
import math

def aggression_factor(growth_multiple: float, amax=1.4, amin=0.7, k=0.2) -> float:
    if growth_multiple <= 0:
        return amax
    return max(amin, amax - k * math.log(growth_multiple))

def compute_fleet_budget(growth_multiple: float) -> dict:
    A = aggression_factor(growth_multiple)
    strike_base = 0.20
    swing_base  = 0.35
    core_base   = 0.35
    reserve_base= 0.10

    strike = strike_base * A
    core   = core_base + (strike_base - strike)
    swing  = swing_base
    reserve= 1.0 - (strike + swing + core)

    # guard
    if reserve < 0:
        reserve = 0.0

    return {
        "growth_multiple": growth_multiple,
        "aggression_factor": A,
        "weights": {
            "STRIKE": round(strike, 4),
            "SWING": round(swing, 4),
            "CORE": round(core, 4),
            "RESERVE": round(reserve, 4)
        }
    }
________________________________________
5.6 workers/risk_engine.py (Strike Gate 최소판)
def apply_strike_risk_gate(fleet_budget: dict, regime: dict) -> dict:
    crisis = float(regime.get("crisis_probability", 0.0))
    weights = fleet_budget["weights"].copy()

    # CrisisProb > 0.65 => Strike 0
    if crisis > 0.65:
        weights["CORE"] += weights["STRIKE"]
        weights["STRIKE"] = 0.0

    fleet_budget["weights"] = weights
    fleet_budget["risk_gate"] = {
        "strike_disabled": crisis > 0.65,
        "crisis_probability": crisis
    }
    return fleet_budget
________________________________________
5.7 workers/engine_worker.py (핵심 루프)
import time
from datetime import datetime, timezone
from app.db import SessionLocal
from app.workers.snapshot_repo import insert_snapshot, get_latest_snapshot_time
from app.workers.incident_repo import create_incident
from app.workers.regime_engine import compute_regime
from app.workers.allocation_engine import compute_allocation
from app.workers.fleet_budget_engine import compute_fleet_budget
from app.workers.risk_engine import apply_strike_risk_gate

MIN_INTERVAL = {
    "regime_current": 60,
    "allocation_matrix": 60,
    "fleet_budget_snapshot": 60,
    "health_status": 60
}

def should_write(db, key: str) -> bool:
    last = get_latest_snapshot_time(db, key)
    if not last:
        return True
    delta = (datetime.now(timezone.utc) - last).total_seconds()
    return delta >= MIN_INTERVAL.get(key, 60)

def run_loop():
    while True:
        db = SessionLocal()
        try:
            # 1) input_data는 DB에서 가져오는 것이 원칙.
            #    MVP에서는 stub로 시작 (추후 ext_event_raw/macro_context 조회 연결)
            input_data = {}

            # 2) Regime
            regime = compute_regime(input_data)
            if should_write(db, "regime_current"):
                insert_snapshot(db, "regime_current", regime, "GREEN", "RegimeEngine")

            # 3) Allocation
            alloc = compute_allocation(regime)
            if should_write(db, "allocation_matrix"):
                insert_snapshot(db, "allocation_matrix", alloc, "GREEN", "AllocationEngine")

            # 4) Fleet Budget (growth_multiple은 DB에서 읽어야 하지만 MVP에서는 1.0)
            fleet_budget = compute_fleet_budget(growth_multiple=1.0)
            fleet_budget = apply_strike_risk_gate(fleet_budget, regime)

            if should_write(db, "fleet_budget_snapshot"):
                insert_snapshot(db, "fleet_budget_snapshot", fleet_budget, "GREEN", "FleetBudgetEngine")

            # 5) incident 예시(RED 조건)
            if regime.get("crisis_probability", 0) > 0.75:
                create_incident(db, "CRITICAL", "CRISIS_PROB", "Crisis probability exceeded 0.75", "regime_current")

        except Exception as e:
            try:
                create_incident(db, "CRITICAL", "ENGINE_ERROR", str(e), None)
            except Exception:
                pass
        finally:
            db.close()

        time.sleep(60)

if __name__ == "__main__":
    run_loop()
________________________________________
🟦 6) Windows 11 실행 스크립트 (PowerShell)
scripts/run_engine_worker.ps1
$env:PYTHONPATH = (Resolve-Path "..\").Path
python ..\app\workers\engine_worker.py
________________________________________
✅ 7) Warroom에서 즉시 확인 가능한 것
Engine Worker를 돌리면 DB에 다음 snapshot이 쌓입니다:
•	regime_current
•	allocation_matrix
•	fleet_budget_snapshot
따라서 React Warroom에서 fetchSnapshot("regime_current") 호출이 즉시 살아납니다.
________________________________________
 
47_Engine_Worker_Skeleton_Spec.md이제 Mode Execution Layer를 고정합니다.
이 레이어는 Aegis-X에서 가장 중요한 “사고 방지 장치”입니다.
어떤 모드에서 어떤 행동이 허용되는가를 수학적으로 봉인한다.
________________________________________
