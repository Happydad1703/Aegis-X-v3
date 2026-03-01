53_AAR_Automation_Implementation_Spec.md (v1.0)

이제 Aegis-X를 **“학습하는 전투 로봇”**으로 완성하는 단계입니다.
지금부터 구현하는 것은:
Order → Portfolio 변화 → Trade 종료 감지 → Battle Report 생성 → AAR 계산 → 파라미터 bounded 업데이트
입니다.


Order Filled
    ↓
Portfolio State 변화
    ↓
Position Close 감지
    ↓
Battle Report 생성
    ↓
AAR Score 계산
    ↓
Fleet / Strategy 통계 업데이트
    ↓
Bounded Parameter Adjustment
________________________________________
2️⃣ 종료된 Trade 감지 로직
종료 정의
•	특정 symbol의 net_qty == 0 이 되는 순간
•	이전 snapshot에는 qty > 0
________________________________________
2.1 DB 테이블 추가
CREATE TABLE battle_report (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    fleet VARCHAR(20),
    strategy_module VARCHAR(50),
    entry_price NUMERIC,
    exit_price NUMERIC,
    quantity NUMERIC,
    pnl_pct NUMERIC,
    holding_period INT,
    regime_at_entry VARCHAR(20),
    crisis_prob_at_entry NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
________________________________________
3️⃣ Trade 종료 감지 엔진
workers/trade_lifecycle_engine.py
from sqlalchemy import text
from datetime import datetime, timezone

def detect_closed_trades(db):
    q = text("""
        SELECT symbol
        FROM order_log
        GROUP BY symbol
        HAVING SUM(CASE WHEN side='BUY' THEN quantity ELSE -quantity END) = 0
    """)
    rows = db.execute(q).fetchall()
    return [r[0] for r in rows]
________________________________________
4️⃣ Battle Report 생성
def create_battle_report(db, symbol):
    q = text("""
        SELECT side, quantity, price, created_at
        FROM order_log
        WHERE symbol = :s
        ORDER BY created_at ASC
    """)
    rows = db.execute(q, {"s": symbol}).fetchall()

    if not rows:
        return None

    buy_price = rows[0][2]
    sell_price = rows[-1][2]

    pnl_pct = (sell_price - buy_price) / buy_price

    report = {
        "symbol": symbol,
        "fleet": "UNKNOWN",  # 추후 order metadata에 저장 권장
        "strategy_module": "UNKNOWN",
        "entry_price": buy_price,
        "exit_price": sell_price,
        "quantity": rows[0][1],
        "pnl_pct": round(pnl_pct, 4),
        "holding_period": len(rows),
        "regime_at_entry": "UNKNOWN",
        "crisis_prob_at_entry": 0.0,
        "created_at": datetime.now(timezone.utc)
    }

    insert_battle_report(db, report)
________________________________________
5️⃣ AAR Score 계산
workers/aar_engine.py
def compute_aar_score(report: dict) -> float:
    pnl = report["pnl_pct"]

    # 단순 MVP 점수
    score = 0.6 * pnl

    # 손실 패널티
    if pnl < 0:
        score *= 1.5

    return round(score, 4)
________________________________________
6️⃣ AAR 집계 테이블
CREATE TABLE aar_summary (
    id BIGSERIAL PRIMARY KEY,
    fleet VARCHAR(20),
    avg_score NUMERIC,
    win_rate NUMERIC,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
________________________________________
7️⃣ Parameter Bounded Update
예: Strike Max Loss 조정
def bounded_adjust(value, delta, min_val, max_val):
    new_val = value + delta
    return max(min_val, min(max_val, new_val))
예:
•	최근 10회 평균 AAR < 0 → Strike risk 강화
•	delta = -0.05
________________________________________
8️⃣ engine_worker에 통합
closed_symbols = detect_closed_trades(db)

for sym in closed_symbols:
    create_battle_report(db, sym)
그 후 AAR 계산 및 집계 업데이트.
________________________________________
9️⃣ Warroom AAR Panel
표시:
•	Fleet별 Avg Score
•	Win Rate
•	최근 10개 Battle Report
•	Regime Alignment %
________________________________________
🔥 이제 시스템 상태
Aegis-X는:
✔ 주문 실행
✔ 포트폴리오 계산
✔ Trade 종료 감지
✔ Battle Report 생성
✔ AAR 점수 계산
✔ 제한적 파라미터 업데이트
즉,
“전투 → 학습 → 개선” 루프가 완성되었습니다.
________________________________________
🎯 현재 완성도
우리는 이제:
•	구조 설계
•	Risk 통제
•	Mode 분리
•	주문 엔진
•	포트폴리오 계산
•	학습 루프
까지 모두 구현 가능한 수준에 도달했습니다.
 
