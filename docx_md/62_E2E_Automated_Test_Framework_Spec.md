62_E2E_Automated_Test_Framework_Spec.md (v1.0)

이제 통합 E2E(End-to-End) 테스트 자동화 체계를 설계·구현합니다.
목표는 단순 유닛 테스트가 아니라:
Regime → Allocation → Fleet → Gate → Order → Portfolio → AAR
전 과정을 “버튼 한 번”으로 자동 검증
하는 것입니다.

1️⃣ E2E 테스트 철학
E2E 테스트는 다음을 검증합니다:
1.	DB 입력 → Engine Worker → Snapshot 생성 정상
2.	Pre-Trade Gate 차단 로직 정상
3.	Mode 분기 정상
4.	Pilot Cap 정상 적용
5.	Order → Portfolio → AAR 연결 정상
6.	Crisis 상황에서 자동 통제 정상
________________________________________
2️⃣ 테스트 레벨 구성
Level 1: Engine Loop Integrity
Level 2: Gate Enforcement
Level 3: Order Lifecycle
Level 4: Crisis Stress
Level 5: Pilot Ramp Transition
________________________________________
3️⃣ 테스트 실행 구조
새 폴더:
backend/tests/
   ├── e2e_runner.py
   ├── test_engine_loop.py
   ├── test_gates.py
   ├── test_order_flow.py
   ├── test_crisis.py
   └── test_pilot_ramp.py
________________________________________
4️⃣ 공통 테스트 유틸
tests/test_utils.py
from app.db import SessionLocal

def get_test_db():
    return SessionLocal()

def clear_orders(db):
    db.execute("DELETE FROM order_log")
    db.commit()
________________________________________
5️⃣ Level 1 — Engine Loop Integrity
test_engine_loop.py
from app.workers.engine_worker import run_single_cycle
from app.db import SessionLocal

def test_engine_snapshot_creation():
    db = SessionLocal()
    run_single_cycle(db)

    result = db.execute(
        "SELECT COUNT(*) FROM engine_snapshot"
    ).scalar()

    assert result > 0
run_single_cycle()는 기존 run_loop를 1회 실행하도록 분리 필요.
________________________________________
6️⃣ Level 2 — Gate Enforcement
test_gates.py
def test_crisis_blocks_order():
    regime_snapshot = {"crisis_probability": 0.95}
    portfolio_snapshot = {"drawdown": -0.01, "daily_loss": -0.01}

    ok, report = run_pre_trade_gate(
        db, "PILOT", regime_snapshot, portfolio_snapshot
    )

    assert ok is False
________________________________________
7️⃣ Level 3 — Order Lifecycle
test_order_flow.py
def test_order_to_portfolio_to_aar():
    db = get_test_db()

    order = {
        "symbol": "TEST",
        "side": "BUY",
        "quantity": 1,
        "price": 1000
    }

    execute_order(db, None, order)

    portfolio = get_latest_snapshot(db, "portfolio_state")
    assert portfolio is not None

    # Close position
    order2 = {
        "symbol": "TEST",
        "side": "SELL",
        "quantity": 1,
        "price": 1100
    }

    execute_order(db, None, order2)

    battle = db.execute(
        "SELECT COUNT(*) FROM battle_report"
    ).scalar()

    assert battle >= 1
________________________________________
8️⃣ Level 4 — Crisis Stress
test_crisis.py
def test_strike_disabled_in_crisis():
    regime = {"crisis_probability": 0.9}

    fleet = {"weights": {"STRIKE": 0.2}}

    result = apply_strike_risk_gate(fleet, regime)

    assert result["weights"]["STRIKE"] == 0
________________________________________
9️⃣ Level 5 — Pilot Ramp Transition
test_pilot_ramp.py
def test_pilot_cap_enforced():
    pilot_config = {
        "pilot_cap_pct": 0.01,
        "strike_enabled": False,
        "daily_entry_limit": 1
    }

    order = {"quantity": 10, "price": 1000}
    portfolio = {"total_equity": 100000}

    ok, msg = cap_gate(order, portfolio, pilot_config)

    assert ok is False
________________________________________
🔟 E2E Runner
tests/e2e_runner.py
import pytest

def run_all():
    pytest.main(["tests"])
PowerShell:
python -m pytest backend/tests
________________________________________
11️⃣ E2E 성공 기준
Pilot 전환 허용 조건:
•	모든 테스트 PASS
•	3회 연속 실행 PASS
•	DB clean 상태 유지
•	Snapshot 생성 정상
________________________________________
12️⃣ Warroom E2E Panel (권장)
System Control Panel에:
•	Run E2E Test 버튼
•	결과 PASS/FAIL 표시
•	마지막 실행 시간 표시
________________________________________
🔥 전략적 의미
이제 Aegis-X는:
✔ 설계
✔ 실행
✔ 통제
✔ 학습
✔ 확장
✔ 스케일링
✔ 안정화
✔ 자동 테스트
까지 갖추었습니다.
________________________________________
 
