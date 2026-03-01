07_Fleet_Execution_Spec.md
Document ID: AEGIS-X-FLEET-v1.0
Owner: Operational Command (Fleet Control)
Classification: Execution & Tactical Doctrine Specification
________________________________________
1. Purpose
본 문서는 Market × Fleet 단위의 다음 절차를 정의한다:
1.	Universe Filtering
2.	Candidate Scoring
3.	Target Selection
4.	Rules of Engagement (ROE)
5.	Execution Engine
6.	Position Monitoring
7.	After Action Report (AAR)
8.	Conflict & Constraint Handling
________________________________________
2. Fleet Doctrine Definition
Aegis-X는 4개 Fleet으로 구성된다.
Fleet	Horizon	Objective	Risk Profile
Core	중기~장기	CAGR + 안정성	중간
Tactical	단기~중기	Sharpe 개선	중간~높음
Strike	초단기	변동성 수확	높음
Reserve	방어	자본 보존	낮음
________________________________________
3. Execution Lifecycle
Universe → Score → Select → ROE → Pre-trade Gate → Execute → Monitor → AAR
각 단계는 독립 로그를 생성해야 한다.
________________________________________
4. Universe Filtering Specification
________________________________________
4.1 입력
•	Market (KOSPI/KOSDAQ/etc.)
•	Fleet
•	Liquidity Data
•	Volatility Data
•	Risk Constraints
________________________________________
4.2 필터 조건 (기본값)
조건	기준
최소 거래대금	≥ 20억
가격 하한	≥ 1000원
변동성 상한	Fleet별 다름
거래정지/관리종목	제외
________________________________________
4.3 출력
{
  "market": "KOSDAQ",
  "fleet": "tactical",
  "universe_size": 142,
  "filtered_symbols": [...]
}
________________________________________
5. Candidate Scoring Specification
________________________________________
5.1 Feature Vector
예시:
•	Trend Score
•	Volume Spike
•	News Sentiment
•	Relative Strength
•	Volatility Compression
•	Sector Momentum
________________________________________
5.2 점수 공식
Score =
    w1*trend
  + w2*volume
  + w3*sentiment
  + w4*relative_strength
가중치는 Learning Engine이 업데이트.
________________________________________
5.3 정규화
•	각 feature ∈ [-1,1]
•	Score ∈ [0,1]
________________________________________
6. Target Selection
________________________________________
6.1 Selection Rule
•	Top N (Fleet별 다름)
•	Sector Exposure ≤ 35%
•	Single Position ≤ 12%
________________________________________
6.2 출력 예
{
  "selected_targets": [
    {"symbol": "A12345", "score": 0.78, "proposed_weight": 0.12}
  ]
}
________________________________________
7. Rules of Engagement (ROE)
________________________________________
7.1 ROE JSON Schema
{
  "entry": {
    "signal_type": "breakout",
    "conditions": {...}
  },
  "position_sizing": {
    "model": "vol_adjusted",
    "risk_per_trade": 0.01
  },
  "exit": {
    "stop_loss": {...},
    "take_profit": {...},
    "time_stop": 10
  }
}
________________________________________
7.2 Fleet별 기본 ROE 차이
Fleet	Stop	Holding	Risk
Core	넓음	길게	낮음
Tactical	중간	중간	중간
Strike	짧음	매우 짧음	높음
________________________________________
8. Pre-Trade Risk Gate Integration
Execution 전 반드시 Risk Engine 호출:
result = risk_pretrade_check(order)
결과:
•	ALLOW
•	SCALE_DOWN
•	REJECT
________________________________________
9. Execution Engine
________________________________________
9.1 Order Type
Capital Size	Execution
Small	Market/Limit
Large	VWAP/TWAP/Iceberg
________________________________________
9.2 Slippage Model
slippage = k × (order_size / ADV)^α
________________________________________
9.3 Partial Fill Handling
•	30초 미체결 → 가격 재조정
•	3회 실패 → REJECT + Incident Log
________________________________________
10. Position Monitoring
________________________________________
10.1 Metrics
•	Unrealized PnL
•	MFE / MAE
•	Holding Period
•	Risk Utilization
________________________________________
10.2 Stop Enforcement
•	Hard Stop
•	Time Stop
•	Risk Mode Stop Override
________________________________________
11. After Action Report (AAR)
________________________________________
11.1 AAR Schema
{
  "position_id": "...",
  "result": {
    "pnl": ...,
    "return_pct": ...,
    "mae": ...,
    "mfe": ...
  },
  "roe_compliance": true,
  "risk_gate_override": false
}
________________________________________
11.2 AAR 저장소
•	PostgreSQL strategy_log
•	Ledger event_type=AAR_EVENT
________________________________________
12. Conflict Handling (Future Ready)
________________________________________
12.1 Cross-Fleet Conflict
조건:
•	동일 Symbol 반대 포지션
•	동일 Sector 과집중
행동:
•	우선순위: Core > Tactical > Strike
•	낮은 우선순위 포지션 축소
________________________________________
13. Failure Handling
Failure	Action
Broker API fail	신규 진입 중단
Partial Fill 지속	Order cancel
Risk Engine unavailable	Execution freeze
Slippage 급증	Strike disable
________________________________________
14. Audit Requirements
각 단계에서 Decision Object 생성:
•	UNIVERSE_DECISION
•	SCORE_DECISION
•	TARGET_DECISION
•	EXECUTION_DECISION
•	EXIT_DECISION
________________________________________
15. Verification Requirements
•	Universe filter test
•	Score reproducibility test
•	ROE bounded test
•	Pre-trade gate integration test
•	Slippage stress test
•	Conflict resolution test
