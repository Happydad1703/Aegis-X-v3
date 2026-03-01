# 46_Warroom_Home_Component_Tree (React)
<WarroomLayout>
   <HeaderStatusBar />
   <LeftTreeMenu />
   <MainCanvas>
        <GlobalRegimeCard />
        <BattlefieldHeatmap />
        <AllocationMatrixPanel />
        <FleetStatusGrid>
            <StrikePanel />
            <SwingPanel />
            <CorePanel />
            <ReservePanel />
        </FleetStatusGrid>
        <PortfolioVarianceTopN />
        <IncidentFeed />
   </MainCanvas>
   <FooterTicker />
</WarroomLayout>

HeaderStatusBar 표시 항목
Mode
Regime
CrisisProb
DB Status
KIS Status
Snapshot Freshness
LLM Status
모든 항목은:
source_name
timestamp
refresh rate
를 함께 표시.


책임개발자로서 저는 다음 3단계를 동시에 진행하겠습니다:
DB 마이그레이션 스크립트 작성
FastAPI Snapshot 서버 골격 구현
Warroom Home 기본 화면 프로토타입 생성
다음으로 무엇을 바로 생성할까요?
A) FastAPI 서버 기본 코드
B) React Warroom 기본 프로젝트 구조
C) Docker + 전체 로컬 실행 스크립트
D) 전부 순차 생성
전부 순차 생성으로 진행합니다.
아래는 실제 구현을 바로 시작할 수 있는 최소 실행 골격(MVP Infrastructure Skeleton) 입니다.
📦 STEP 1 — Docker + PostgreSQL 실행 환경
1️⃣ docker-compose.yml
version: "3.9"

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
Windows 11 PowerShell:
docker compose up -d

📦 STEP 2 — FastAPI Snapshot Server Skeleton
2️⃣ 프로젝트 구조
backend/
 ├── app/
 │   ├── main.py
 │   ├── db.py
 │   ├── models.py
 │   ├── snapshot_service.py
 │   └── routers/
 │       ├── snapshot.py
 │       └── control.py
 ├── requirements.txt
 └── .env

requirements.txt
fastapi
uvicorn
psycopg2-binary
sqlalchemy
python-dotenv

db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

main.py
from fastapi import FastAPI
from app.routers import snapshot, control

app = FastAPI(title="Aegis-X API")

app.include_router(snapshot.router, prefix="/api/snapshot")
app.include_router(control.router, prefix="/api/control")

routers/snapshot.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal
from sqlalchemy import text

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{snapshot_key}")
def get_snapshot(snapshot_key: str, db: Session = Depends(get_db)):
    query = text("""
        SELECT snapshot_data, freshness_status, generated_at
        FROM engine_snapshot
        WHERE snapshot_key = :key
        ORDER BY generated_at DESC
        LIMIT 1
    """)
    result = db.execute(query, {"key": snapshot_key}).fetchone()

    if not result:
        return {"error": "Not found"}

    return {
        "snapshot_key": snapshot_key,
        "data": result[0],
        "freshness_status": result[1],
        "generated_at": result[2]
    }

routers/control.py
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.post("/freeze")
def freeze():
    return {
        "status": "FREEZE_TRIGGERED",
        "timestamp": datetime.utcnow()
    }

실행
uvicorn app.main:app --reload

📦 STEP 3 — React Warroom Skeleton
3️⃣ 프로젝트 생성
npx create-react-app warroom --template typescript

구조
warroom/
 ├── src/
 │   ├── layout/
 │   │   ├── WarroomLayout.tsx
 │   ├── components/
 │   │   ├── HeaderStatusBar.tsx
 │   │   ├── LeftTreeMenu.tsx
 │   │   ├── AllocationPanel.tsx
 │   │   ├── RegimeCard.tsx
 │   ├── pages/
 │   │   ├── Home.tsx
 │   └── services/
 │       ├── api.ts

services/api.ts
export async function fetchSnapshot(key: string) {
  const res = await fetch(`/api/snapshot/${key}`);
  return res.json();
}

RegimeCard.tsx
import React, { useEffect, useState } from "react";
import { fetchSnapshot } from "../services/api";

export default function RegimeCard() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetchSnapshot("regime_current").then(setData);
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div className="card">
      <h3>Regime</h3>
      <p>{data.data.regime_state}</p>
      <small>{data.generated_at}</small>
    </div>
  );
}

📦 STEP 4 — Telegram Bot Skeleton
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("System OK")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("status", status))

app.run_polling()


이제 Aegis-X는:
Docker DB 실행 가능
FastAPI 스냅샷 서버 가동 가능
React Warroom 기본 조회 가능
Telegram 봇 연결 가능
즉, 두뇌 + 몸 + UI + 원격 제어 골격이 모두 준비되었습니다.

(목표: Regime → Allocation → Fleet Budget → Risk → Snapshot 생성이 DB에 기록되고 Warroom이 즉시 조회 가능)
아래는 구현 가능한 수준의 SE 명세 + 파일 구조 + 핵심 코드 스켈레톤입니다. (Windows 11 / PowerShell 기준)

📘47_Engine_Worker_Skeleton_Spec.md (v1.0)
1) Worker 역할(필수)
DB에서 입력 데이터 조회(원칙 준수)
Regime 계산(또는 stub)
Allocation Matrix v2 계산(또는 stub)
Fleet Budget(FBGC) 계산
Strike/Swing/Core 상태 계산(최소 status snapshot)
Snapshot 생성/업서트
incident 생성(RED 조건)
UI는 engine_snapshot만 읽고, Worker가 snapshot을 생산한다.

2) 실행 모델(PC Feasible)
단일 프로세스 + 주기 루프(우선)
추후 분리: ingest_worker / engine_worker / bot_worker
권장 주기(초기)
engine tick: 60초
regime refresh: 300초(5분)
macro refresh: ingest에서 처리

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

✅ 4) DB Contract: Snapshot Upsert 규칙
engine_snapshot는 최신 1건만 유지하는 방식도 가능하지만,
감사/추적을 위해 append + latest 조회를 유지합니다.
다만 불필요한 폭증 방지를 위해:
snapshot_key별 “최소 생성 간격(min_interval_sec)” 적용

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

🟦 6) Windows 11 실행 스크립트 (PowerShell)
scripts/run_engine_worker.ps1
$env:PYTHONPATH = (Resolve-Path "..\").Path
python ..\app\workers\engine_worker.py

✅ 7) Warroom에서 즉시 확인 가능한 것
Engine Worker를 돌리면 DB에 다음 snapshot이 쌓입니다:
regime_current
allocation_matrix
fleet_budget_snapshot
따라서 React Warroom에서 fetchSnapshot("regime_current") 호출이 즉시 살아납니다.


이제 STEP 2 — DB 입력 연결 + Health Snapshot + Portfolio Variance Snapshot으로 진행합니다.
목표는 Worker가 stub가 아니라 실제 DB 입력을 읽고, Warroom이 즉시 의미 있는 데이터를 보게 하는 것입니다.

📘48_DB_Input_Integration_and_Health_Snapshot_Spec.md (v1.0)

1️⃣ Regime 입력을 DB에서 읽도록 연결
1.1 필요한 입력 (MVP 수준)
최근 60MA/120MA 대체용: 최근 N일 지수 수익률 평균 (index_proxy 테이블 or ext_event_raw)
최근 변동성 대체용: 최근 20개 수익률 표준편차
매크로 지표 1~2개 (예: 금리/달러 proxy) from macro_context
뉴스 카운트(최근 1시간) from ext_event_raw
실제 지표 테이블이 없으므로, MVP에서는 engine_result에 미리 저장된 proxy 값을 읽도록 설계.

1.2 regime_engine.py (DB 연결 버전)
from sqlalchemy import text
from datetime import datetime, timezone

def fetch_regime_inputs(db):
    # 1) 최근 index proxy (engine_result에서 읽는 MVP)
    q_price = text("""
        SELECT result_value
        FROM engine_result
        WHERE engine_name = 'market_proxy'
        ORDER BY computed_at DESC
        LIMIT 1
    """)
    row_price = db.execute(q_price).fetchone()
    price_data = row_price[0] if row_price else {}

    # 2) 최근 매크로
    q_macro = text("""
        SELECT indicator_name, value
        FROM macro_context
        ORDER BY observed_at DESC
        LIMIT 5
    """)
    macro_rows = db.execute(q_macro).fetchall()

    macro_data = {r[0]: float(r[1]) for r in macro_rows} if macro_rows else {}

    return {
        "price_data": price_data,
        "macro_data": macro_data
    }


def compute_regime(db) -> dict:
    inputs = fetch_regime_inputs(db)

    # MVP: price_data에 trend_score, vol_score가 이미 들어있다고 가정
    trend_score = inputs["price_data"].get("trend_score", 0.0)
    vol_score   = inputs["price_data"].get("vol_score", 0.0)

    # macro 단순 평균 (MVP)
    macro_vals = list(inputs["macro_data"].values())
    macro_score = sum(macro_vals)/len(macro_vals) if macro_vals else 0.0

    regime_score = 0.5*trend_score + 0.3*vol_score + 0.2*macro_score

    if regime_score >= 1.0:
        regime_state = "Goldilocks"
    elif regime_score >= 0.0:
        regime_state = "Sideways"
    elif regime_score >= -1.0:
        regime_state = "Tapering"
    else:
        regime_state = "Crisis"

    crisis_probability = min(1.0, max(0.0, ( -regime_score + 1 ) / 3 ))

    return {
        "regime_state": regime_state,
        "regime_score": round(regime_score, 4),
        "crisis_probability": round(crisis_probability, 4),
        "inputs_summary": {
            "trend_score": trend_score,
            "vol_score": vol_score,
            "macro_score": macro_score
        },
        "computed_at_utc": datetime.now(timezone.utc).isoformat()
    }

1.3 engine_worker.py 수정 (regime 호출 변경)
기존:
regime = compute_regime(input_data)
변경:
regime = compute_regime(db)

2️⃣ Health Status Snapshot 생성
Warroom Header에서 반드시 필요:
DB 연결 OK?
KIS sync 최근 성공?
Snapshot freshness?
Engine error 존재?

2.1 health_snapshot 생성 코드
workers/health_engine.py
from sqlalchemy import text
from datetime import datetime, timezone

def compute_health_status(db):
    # 1) 최근 snapshot 생성 시간
    q = text("""
        SELECT MAX(generated_at)
        FROM engine_snapshot
    """)
    last_snapshot = db.execute(q).scalar()

    now = datetime.now(timezone.utc)
    freshness = "GREEN"

    if last_snapshot:
        delta = (now - last_snapshot).total_seconds()
        if delta > 300:
            freshness = "RED"
        elif delta > 120:
            freshness = "YELLOW"

    # 2) 최근 엔진 에러
    q_err = text("""
        SELECT COUNT(*)
        FROM incident_log
        WHERE severity = 'CRITICAL'
          AND created_at > NOW() - INTERVAL '1 hour'
    """)
    err_count = db.execute(q_err).scalar()

    return {
        "snapshot_freshness": freshness,
        "critical_incidents_last_hour": err_count,
        "generated_at_utc": now.isoformat()
    }
engine_worker에 추가:
from app.workers.health_engine import compute_health_status

health = compute_health_status(db)
if should_write(db, "health_status"):
    insert_snapshot(db, "health_status", health, health["snapshot_freshness"], "HealthEngine")

3️⃣ Portfolio Variance Snapshot (현재 비중 Top N)
3.1 DB 가정
engine_result에 다음 key가 있다고 가정:
engine_name = 'portfolio_state'
result_value = { "positions": [ {symbol, weight}, ... ] }

3.2 variance_snapshot 생성
workers/portfolio_engine.py
from sqlalchemy import text
from datetime import datetime, timezone

def compute_portfolio_variance(db, top_n=10):
    q = text("""
        SELECT result_value
        FROM engine_result
        WHERE engine_name = 'portfolio_state'
        ORDER BY computed_at DESC
        LIMIT 1
    """)
    row = db.execute(q).fetchone()
    data = row[0] if row else {"positions": []}

    positions = data.get("positions", [])
    positions_sorted = sorted(positions, key=lambda x: x.get("weight", 0), reverse=True)

    return {
        "top_positions": positions_sorted[:top_n],
        "total_positions": len(positions),
        "generated_at_utc": datetime.now(timezone.utc).isoformat()
    }
engine_worker에 추가:
from app.workers.portfolio_engine import compute_portfolio_variance

variance = compute_portfolio_variance(db)
if should_write(db, "portfolio_variance"):
    insert_snapshot(db, "portfolio_variance", variance, "GREEN", "PortfolioEngine")

🔥 이제 Worker가 생산하는 Snapshot 목록
regime_current
allocation_matrix
fleet_budget_snapshot
health_status
portfolio_variance
Warroom Home에서 바로 의미 있는 화면 구성 가능.


이제 Mode Execution Layer를 고정합니다.
이 레이어는 Aegis-X에서 가장 중요한 “사고 방지 장치”입니다.
어떤 모드에서 어떤 행동이 허용되는가를 수학적으로 봉인한다.