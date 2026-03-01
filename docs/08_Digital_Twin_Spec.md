08_Digital_Twin_Spec.md
Document ID: AEGIS-X-TWIN-v1.0
Owner: Strategy Lab / Meta-Control
Classification: Simulation & Validation Specification
________________________________________
1. Purpose
Digital Twin은 다음을 보장한다:
1.	전략 변경의 사전 검증
2.	Learning/ROE 파라미터의 과적합 방지
3.	Capacity Scaling 영향 평가
4.	Crisis 대응 능력 검증
5.	Live 전략 대비 상대 성능 비교
________________________________________
2. Twin Operating Modes
________________________________________
2.1 Backtest Mode
•	과거 데이터 완전 재생
•	이벤트 시퀀스 순차 처리
•	실제 스케줄러와 동일 로직 실행
입력
•	Historical Ledger
•	Historical macro_context
•	Historical price series
________________________________________
2.2 Walk-Forward Mode
Train Window → Test Window → Roll Forward
예:
•	24개월 학습
•	6개월 테스트
•	3개월 단위 이동
목적:
•	시간 일반화 검증
________________________________________
2.3 Parallel Shadow Mode
•	Live와 동일 시그널
•	가상 자본
•	다른 파라미터 세트
•	실시간 비교
________________________________________
3. Simulation Core Architecture
Historical Replay Engine
    ↓
Regime Engine
    ↓
Allocation Engine
    ↓
Risk Engine
    ↓
Fleet Execution Emulator
    ↓
Slippage Model
    ↓
PnL Engine
    ↓
Learning Engine
Live와 동일 코드 경로를 사용해야 한다.
________________________________________
4. Execution Emulator
________________________________________
4.1 Slippage Model
slippage = k × (order_size / ADV)^α
기본:
•	k = 0.5
•	α = 0.6
Strike는 k 1.5배 적용.
________________________________________
4.2 Market Impact Model
impact_cost = λ × volatility × participation_rate
impact_cost > expected_edge × 0.5
→ Trade skip
________________________________________
4.3 Partial Fill Simulation
•	Volume-weighted execution
•	30% 이상 체결 실패 시 Cancel
________________________________________
5. Capacity Scaling Simulation
Twin은 다음 자본 배율 테스트를 수행한다:
•	1×
•	5×
•	10×
•	20×
각 배율에서:
•	CAGR
•	DD
•	Sharpe
•	Impact Cost Ratio
측정
________________________________________
6. Performance Metrics
________________________________________
6.1 Core Metrics
Metric	Description
CAGR	연환산 성장률
Max DD	최대 낙폭
Sharpe	위험조정 수익
Sortino	하방 위험조정
Calmar	CAGR / DD
________________________________________
6.2 Regime-Segmented Metrics
Goldilocks CAGR
Sideways CAGR
Tapering CAGR
Crisis CAGR
Crisis 구간 방어 실패 시 승격 불가.
________________________________________
6.3 Stability Metrics
•	Rolling Sharpe variance
•	Tail loss frequency
•	Trade distribution skew
________________________________________
7. Monte Carlo Robustness Test
________________________________________
7.1 Trade Shuffle
•	거래 순서 랜덤 재배열
•	100회 반복
•	DD 평균 및 95% 구간 측정
________________________________________
7.2 Noise Injection
•	Price ± random noise
•	Slippage 1.2× 확대
•	Execution delay random
전략 성과 유지 여부 평가.
________________________________________
8. Strategy Promotion Criteria
전략 승격 조건:
1.	Sharpe ≥ Live + 0.1
2.	Max DD ≤ Live + 2%
3.	Crisis CAGR ≥ 0
4.	Monte Carlo DD 95% ≤ 1.2× Live
5.	Capacity 5× 시 Sharpe 유지 ≥ 80%
모두 충족해야 승격 가능.
________________________________________
9. Failure Criteria
다음 중 하나라도 충족하면 Reject:
•	Crisis 구간 DD > 25%
•	Tail loss frequency 증가 > 30%
•	Sharpe instability score > threshold
•	Capacity 10×에서 edge 붕괴
________________________________________
10. Logging Requirements
Twin 실행마다:
{
  "simulation_id": "...",
  "strategy_version": "...",
  "parameters": {...},
  "metrics": {...},
  "promotion_status": "PASS/FAIL"
}
PostgreSQL strategy_lab_log에 기록.
________________________________________
11. Governance Integration
•	Twin 통과 결과는 Meta-Control에 제출
•	Governance Layer에 Decision Object 생성
•	승격 시 전략 lineage 기록
________________________________________
12. Risk Interaction
Twin에서도 Risk Engine 완전 적용.
•	Risk Caps
•	DD Trigger
•	Mode Switch
비활성화 금지.
________________________________________
13. Verification Checklist
Test	Required
Backtest consistency	✔
Walk-forward	✔
Monte Carlo	✔
Crisis robustness	✔
Capacity scaling	✔
Shadow mode 30일	✔