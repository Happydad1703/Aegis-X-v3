51_Order_Execution_Engine_Spec.md (v1.0)
이제 Order Execution Engine을 고정합니다.
이 단계는:
Pre-Trade Gate를 통과한 주문만
Mode에 맞게
Paper / Pilot / Full Live로 분기 실행하는 계층
입니다.

1️⃣ 역할
Order Execution Engine은 다음을 수행합니다:
1.	Pre-Trade Gate 호출
2.	Mode 판별
3.	Paper 또는 KIS 실행 분기
4.	실행 결과 DB 기록
5.	Snapshot 갱신
________________________________________
2️⃣ 주문 실행 흐름
Strategy Engine
    ↓
Order Proposal
    ↓
Pre-Trade Gate
    ↓
Order Execution Engine
    ↓
Paper Broker OR KIS API
    ↓
order_log 기록
    ↓
portfolio_state snapshot 갱신
________________________________________
3️⃣ DB 테이블 추가
3.1 order_log
CREATE TABLE order_log (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    side VARCHAR(10),
    quantity NUMERIC,
    price NUMERIC,
    mode VARCHAR(20),
    execution_status VARCHAR(20),
    execution_payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
________________________________________
4️⃣ Paper Broker 구현
paper_broker.py
import uuid
from datetime import datetime, timezone

def execute_paper_order(symbol, side, quantity, price):
    return {
        "order_id": str(uuid.uuid4()),
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price,
        "status": "FILLED",
        "executed_at": datetime.now(timezone.utc).isoformat()
    }
________________________________________
5️⃣ KIS Execution Wrapper
(실 API는 이미 존재한다고 가정, wrapper만 설계)
kis_executor.py
def execute_kis_order(kis_client, symbol, side, quantity, price):
    response = kis_client.place_order(
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price
    )
    return response
________________________________________
6️⃣ Order Engine Orchestrator
order_engine.py
from app.gates.pre_trade_gate import run_pre_trade_gate
from app.services.mode_service import get_current_mode, is_kis_enabled
from app.workers.incident_repo import create_incident
from app.brokers.paper_broker import execute_paper_order
from app.brokers.kis_executor import execute_kis_order
from sqlalchemy import text

def execute_order(db, kis_client, order_proposal):
    mode = get_current_mode(db)

    # snapshot 조회
    regime_snapshot = get_latest_snapshot(db, "regime_current")
    portfolio_snapshot = get_latest_snapshot(db, "portfolio_state")

    allowed, report = run_pre_trade_gate(
        db,
        mode,
        regime_snapshot["snapshot_data"],
        portfolio_snapshot["snapshot_data"]
    )

    if not allowed:
        create_incident(db, "CRITICAL", "ORDER_BLOCKED", str(report))
        return None

    # Mode 분기
    if mode == "PAPER":
        result = execute_paper_order(**order_proposal)

    elif mode in ["PILOT", "FULL_LIVE"] and is_kis_enabled(mode):
        result = execute_kis_order(kis_client, **order_proposal)

    else:
        return None

    # DB 기록
    insert_order_log(db, order_proposal, result, mode)

    return result
________________________________________
7️⃣ order_log 기록 함수
def insert_order_log(db, order_proposal, result, mode):
    q = text("""
        INSERT INTO order_log
        (symbol, side, quantity, price, mode, execution_status, execution_payload)
        VALUES (:s, :sd, :q, :p, :m, :st, :pl::jsonb)
    """)
    db.execute(q, {
        "s": order_proposal["symbol"],
        "sd": order_proposal["side"],
        "q": order_proposal["quantity"],
        "p": order_proposal["price"],
        "m": mode,
        "st": result.get("status"),
        "pl": __import__("json").dumps(result)
    })
    db.commit()
________________________________________
8️⃣ 주문 이후 Snapshot 갱신
Order 실행 후 반드시:
•	portfolio_state 갱신
•	portfolio_variance snapshot 재생성
•	fleet_budget_snapshot 재계산
엔진 Worker가 다음 tick에서 자동 갱신.
________________________________________
9️⃣ Safety Layer
Full Live 보호
FULL_LIVE일 경우:
•	추가 Confirm Token 필요
•	Daily Cap 초과 시 자동 차단
•	주문당 최대 금액 제한
________________________________________
🔥 현재 상태
이제 Aegis-X는:
✔ Regime 판단
✔ Allocation 계산
✔ Fleet Budget 분배
✔ Risk Gate
✔ Mode Enforcement
✔ Pre-Trade Gate
✔ Order Execution Engine
즉, Paper → Pilot → Live까지 가능한 구조를 갖췄습니다.
________________________________________
🎯 다음 순차 과업
이제 남은 핵심은:
1️⃣ Portfolio State 실시간 계산 모듈
2️⃣ AAR 자동 생성 연결
3️⃣ Warroom UI를 실제 밀도 높은 상업용 형태로 확장
책임개발자로서 판단:
👉 다음은 Portfolio State Engine을 구현해야 합니다.
왜냐하면
Order가 실행되었는데 자산 상태 계산이 부정확하면
Allocation과 Risk가 무너집니다.
계속 진행합니다.
ok
좋습니다.
이제 Portfolio State Engine (PSE) 을 구현합니다.
이 엔진은 Aegis-X의 “재무제표”입니다.
모든 Risk, Allocation, Gate, AAR는 이 데이터를 기반으로 작동합니다.
주문보다 더 중요한 것이 Portfolio State입니다.
계산이 틀리면 모든 것이 틀립니다.
________________________________________
