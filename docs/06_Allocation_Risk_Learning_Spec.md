06_Allocation_Risk_Learning_Spec.md
Document ID: AEGIS-X-ARL-v1.0
Owner: Strategic Command / Risk Office
Classification: Core Decision Engine Specification
________________________________________
1. Purpose
본 문서는 다음 엔진의 수학적·논리적 정의를 제공한다:
1.	Allocation Engine
2.	Risk Engine
3.	Learning Engine
4.	Capital Optimizer
본 문서의 정의는 구현 코드보다 상위 개념이다.
________________________________________
2. Allocation Engine Specification
________________________________________
2.1 Equity Budget Determination
입력
•	Global Regime
•	Risk Mode
•	Growth Multiplier
•	Kelly Fraction
•	Capacity Cap
기본 Equity Budget (Global 기준)
Global Regime	Equity Budget
Goldilocks	0.85
Sideways	0.65
Tapering	0.45
Crisis	0.20
________________________________________
2.2 Risk Scaling
Effective Equity Budget =
    Base Equity Budget
    × Risk Mode Scale
    × Growth Multiplier
Risk Mode Scale:
Mode	Scale
ON	1.0
NEUTRAL	0.7
OFF	0.3
________________________________________
2.3 Market Allocation (Softmax 기반)
Strength_i =
    0.4 * Growth_i
  + 0.4 * Stress_i
  + 0.2 * Liquidity_i

Share_i = softmax(Strength_i / temperature)
Final Market Allocation:
Market_i = Effective Equity Budget × Share_i
________________________________________
2.4 Capacity Constraint
Final Market_i =
    min(
        Market_i,
        Capacity_i,
        Risk Cap_i
    )
________________________________________
3. Risk Engine Specification
________________________________________
3.1 Risk Mode Determination
Drawdown Rule
DD	Mode
> -5%	ON
≤ -5%	NEUTRAL
≤ -10%	OFF
Volatility Rule
Vol Spike = 5D Vol / 20D Vol
Vol Spike	Action
≥ 1.5	Strike 50% reduction
≥ 1.8	Strike disabled
≥ 2.2	Market 30% reduction
________________________________________
3.2 Pre-Trade Gate
입력:
•	Proposed Order
•	Current Exposure
•	Risk Caps
•	Capacity
출력:
•	ALLOW
•	SCALE_DOWN
•	REJECT
________________________________________
3.3 Hard Constraints
•	Single Position ≤ 12%
•	Strike ≤ 15%
•	Market ≤ 70%
•	ADV Participation ≤ 2%
________________________________________
4. Learning Engine Specification
________________________________________
4.1 Fleet Efficiency Score
Efficiency =
    0.4 * normalized_expectancy
  + 0.4 * normalized_sharpe
  - 0.2 * normalized_drawdown
________________________________________
4.2 Capital Reweighting
Adjusted Weight =
    Base Weight
    + learning_rate × Efficiency Delta
Constraint:
•	Δ ≤ ±5%p per cycle
________________________________________
4.3 Feature Weight Update
w_new = w_old + lr × (mean_win - mean_loss)
Bounds:
•	w ∈ [0,1]
•	Normalize Σw = 1
________________________________________
4.4 ROE Parameter Adjustment
risk_per_trade_new =
    risk_old + 0.001 if expectancy_high
    risk_old - 0.001 if expectancy_low
Bounds:
•	0.5% ≤ risk_per_trade ≤ 1.5%
________________________________________
5. Capital Optimizer Specification
________________________________________
5.1 Kelly-lite
f* = edge / variance
kelly_fraction = f* × 0.3 (default)
________________________________________
5.2 Final Exposure Formula
Final Exposure =
    Risk Budget
    × Kelly Fraction
    × Growth Multiplier
________________________________________
5.3 High-Water Mark Logic
•	New Equity High → +0.1% risk_per_trade
•	DD ≥ -8% → -0.2% risk_per_trade
________________________________________
6. Priority Hierarchy
Risk Engine > Allocation > Learning > Capital Optimizer
Learning cannot override Risk Caps.
________________________________________
7. Monitoring Outputs
API Endpoints:
•	/api/allocation/state
•	/api/risk/state
•	/api/learning/state
•	/api/capital/state
________________________________________
8. Failure Handling
Component	Failure Action
Learning	Freeze learning
Capital Optimizer	Revert to Base Allocation
Risk Engine	Default to OFF
Allocation	Freeze positions
________________________________________
9. Audit Logging
All parameter changes must generate:
{
  "decision_type": "LEARNING_UPDATE",
  "old_value": 0.01,
  "new_value": 0.012,
  "reason": "Expectancy > threshold"
}
________________________________________
10. Verification Criteria
•	DD Trigger test
•	Vol Spike test
•	Kelly stability test
•	Capacity overflow test
•	Learning bounded test
