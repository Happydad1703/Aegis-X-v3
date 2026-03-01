35_Strike_Force_Risk_Engine_Spec.md (v1.0)
________________________________________
1️⃣ 설계 철학
Strike Risk Engine의 4대 원칙:
	손실은 즉각 차단한다.
	연속 실패는 구조적 위험 신호로 간주한다.
	Crisis 환경에서는 자동 비활성화한다.
	Core 자본을 침식하지 못한다.
________________________________________
2️⃣ Risk Control Layer 구조
Strike는 4중 방어벽을 가집니다.
Layer 1: Position Risk
Layer 2: Trade Sequence Risk
Layer 3: Daily Risk
Layer 4: Systemic Risk
________________________________________
3️⃣ Layer 1 — Position Risk Control
3.1 단일 종목 최대 노출
Position_Size≤5%"  " of"  " Total_Capital

3.2 단일 포지션 최대 손실
Max_Loss_per_Trade=1%

손절은 자동. 수동 금지.
________________________________________
4️⃣ Layer 2 — Trade Sequence Control
4.1 연속 손실 제한
	2회 연속 손실 → 1시간 비활성화
	3회 연속 손실 → 해당일 Strike 종료
4.2 Win/Loss 변동성 분석
최근 10회:
	Win Rate < 30%
	R:R < 1.2
→ Strike Budget 50% 축소
________________________________________
5️⃣ Layer 3 — Daily Risk Control
5.1 Strike 전용 Daily Loss Cap
Strike_Daily_Loss≤3%"  " of"  " Strike_Capital

초과 시:
	즉시 Freeze Strike
	Reserve로 자금 이동
________________________________________
6️⃣ Layer 4 — Systemic Risk Control
6.1 Crisis Override
조건 중 하나라도 충족 시:
	CrisisProb > 0.65
	Market Intraday Drop < -2.5%
	Volatility Spike > 2σ
	Data Freshness RED
→ Strike = 0%
________________________________________
7️⃣ Volatility Adaptive Positioning
Strike는 변동성에 반비례해야 합니다.
Adjusted_Position=Base_Position×(Target_Vol)/(Current_Vol)

Vol 상승 시 자동 축소.
________________________________________
8️⃣ Capital Protection Rule
Strike는 Core를 침식할 수 없습니다.
If Strike_Capital < 70% of Initial_Strike_Budget:
    Strike Budget = Strike_Capital (No refill from Core)
Core → Strike 자본 재보충 금지.
________________________________________
9️⃣ Recovery Protocol
Strike가 비활성화되었을 경우:
재활성 조건:
	Regime = Goldilocks 또는 Sideways
	CrisisProb < 0.45
	1시간 이상 Vol 안정
________________________________________
🔟 Warroom 표시 항목
Strike Risk Panel:
	Strike Exposure %
	Today PnL
	Sequence Loss Count
	Volatility Index
	Activation Status (ACTIVE / COOLDOWN / LOCKED)
________________________________________
11️⃣ DB Snapshot 구조
snapshot_key = strike_risk_status
{
  "strike_capital": ...,
  "daily_pnl": ...,
  "loss_streak": ...,
  "volatility_ratio": ...,
  "activation_status": "ACTIVE",
  "aggression_factor": ...,
  "timestamp_utc": ...
}
________________________________________
12️⃣ 전략적 의미
Strike는:
	빠르게 돈을 벌 수 있다.
	빠르게 잃을 수도 있다.
따라서:
Strike는 자동화의 영역,
인간의 감정이 개입할 수 없는 영역으로 봉인해야 한다.