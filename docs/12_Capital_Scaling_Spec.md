12_Capital_Scaling_Spec.md
Document ID: AEGIS-X-SCALE-v1.0
Owner: Strategic Command / Execution Desk
Classification: Capital Capacity & Liquidity Management Specification
________________________________________
1. Purpose
본 문서는 다음을 정의한다:
1.	전략·Fleet·자산군별 Capacity 계산 방식
2.	Liquidity-Aware Allocation 제약
3.	Market Impact 모델
4.	대규모 자본 Execution 알고리즘 전환 기준
5.	Multi-Strategy Diversification 규칙
6.	Scaling Stress Test 요구사항
________________________________________
2. Capacity Model
________________________________________
2.1 종목 단위 Capacity
Capacity_symbol =
    ADV × participation_rate × liquidity_factor
기본값
•	ADV: 최근 20일 평균 거래대금
•	participation_rate:
o	Core: 3%
o	Tactical: 2%
o	Strike: 1%
•	liquidity_factor:
o	Large Cap: 1.0
o	Mid Cap: 0.8
o	Small Cap: 0.6
________________________________________
2.2 Fleet 단위 Capacity
Capacity_fleet =
Σ Capacity_symbol (선정 종목 기준)
________________________________________
2.3 Market 단위 Capacity
Capacity_market =
Σ Capacity_symbol (해당 Market 전체 유니버스)
________________________________________
3. Liquidity-Aware Allocation Constraint
Allocation Engine 최종 배분은 다음을 초과할 수 없다:
Final Allocation =
min(
    Regime Allocation,
    Risk Cap,
    Capacity Cap
)
Capacity Cap 위반 시:
•	Strike 우선 축소
•	Tactical 축소
•	Core 유지
________________________________________
4. Market Impact Model
________________________________________
4.1 Impact Cost 함수
impact ≈ k × (order_size / ADV)^α
기본값:
•	k = 0.5
•	α = 0.6
Strike는 k × 1.5
________________________________________
4.2 Impact Threshold Rule
if impact_cost > expected_edge × 0.5:
    trade = REJECT
________________________________________
5. Execution Scaling Levels
자본 규모에 따라 Execution 모드를 전환한다.
________________________________________
Stage 1: < 50억
•	시장가/리밋
•	단일 주문 허용
•	Strike 전략 유지 가능
________________________________________
Stage 2: 50억~300억
•	VWAP/TWAP 적용
•	Strike 비중 자동 축소
•	유동성 하위 20% 종목 제외
________________________________________
Stage 3: 300억 이상
•	Iceberg 주문 필수
•	대형주 중심
•	Cross-Asset 비중 확대
•	Strike 전략 최소화
________________________________________
6. Participation Limit
Fleet	Max Participation
Core	3%
Tactical	2%
Strike	1%
Violation 시:
•	Order 자동 분할
•	시간 분산 실행
________________________________________
7. Cross-Asset Expansion Rule
자본 증가 시:
Equity Ratio ↓
Bond Ratio ↑
FX Hedge ↑
Index ETF ↑
Strike 전략은 비선형적으로 감소.
________________________________________
8. Multi-Strategy Diversification
Meta-Control은 다음 기준으로 전략 비중 조정:
Strategy Weight_i ∝ Meta Score_i × Capacity_i
제약:
•	단일 전략 ≤ 70%
•	상관계수 > 0.8 전략 동시 50% 초과 금지
________________________________________
9. Scaling Stress Test Requirements
Twin Lab에서 반드시 수행:
자본 배율 테스트
•	1×
•	5×
•	10×
•	20×
측정 항목
•	CAGR 유지율
•	Sharpe 유지율
•	DD 증가폭
•	Impact Cost Ratio
•	Execution 실패율
________________________________________
9.1 통과 기준
•	Sharpe 유지 ≥ 80%
•	DD 증가 ≤ 30%
•	Impact Cost ≤ 총수익의 20%
•	Execution 실패율 ≤ 5%
________________________________________
10. Liquidity Shock Simulation
다음 상황 시뮬레이션:
•	ADV 50% 감소
•	Vol 2배 증가
•	Spread 2배 확대
전략 생존 여부 확인.
________________________________________
11. Scaling Governance Requirement
자본 2배 이상 증가 시:
•	Capacity 재산정 필수
•	Scaling Twin 재실행 필수
•	Governance 승인 필수
________________________________________
12. Risk Interaction
Scaling이 Risk Engine을 약화시키면 안 된다.
우선순위:
Self-Healing
    >
Risk
    >
Capacity
    >
Allocation
Capacity는 Risk보다 하위 제약이다.
________________________________________
13. Monitoring Dashboard
Warroom에 추가:
Metric	Value
Current AUM	180억
Max Capacity	240억
Capacity Utilization	75%
Impact Ratio	12%
Strike Utilization	8%
________________________________________
14. Failure Handling
Condition	Action
Capacity 95% 초과	신규 진입 중단
Impact 급증	Strike 즉시 중단
Execution 실패율 > 10%	Mode downgrade
Liquidity Shock 감지	Equity 자동 30% 축소
________________________________________
15. Verification Checklist
•	Capacity 계산 재현성 테스트
•	Participation limit 테스트
•	Impact 모델 회귀 테스트
•	10× Scaling Twin 테스트
•	Liquidity Shock 시뮬레이션