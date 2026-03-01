40_AAR_Automated_Learning_Loop_Spec.md (v1.0)
________________________________________
1️⃣ 목적
AAR(After Action Review)은 단순 리포트가 아닙니다.
Aegis-X에서 AAR은:
	교전 결과 수집
	원인 분해
	전략/Regime 정합도 평가
	파라미터 자동 조정
까지 포함하는 피드백 엔진입니다.
________________________________________
2️⃣ AAR 구조
각 교전은 다음 구조로 DB에 기록됩니다.
snapshot_key = battle_report
{
  "battlefield": "KOSPI",
  "fleet": "Swing",
  "symbol": "005930",
  "entry_price": 71500,
  "exit_price": 74200,
  "holding_period_days": 6,
  "pnl_pct": 3.8,
  "risk_reward_ratio": 1.9,
  "regime_at_entry": "Goldilocks",
  "regime_score": 1.3,
  "crisis_prob": 0.22,
  "volatility_at_entry": 0.18,
  "strategy_module": "Trend-Follow",
  "timestamp_exit_utc": "..."
}
________________________________________
3️⃣ AAR 분석 4계층 구조
Layer 1: Trade Performance
Layer 2: Regime Alignment
Layer 3: Strategy Effectiveness
Layer 4: Capital Efficiency
________________________________________
4️⃣ Layer 1 — Trade Performance Score
TPS=0.5×PnL+0.3×R:R+0.2×HoldingEfficiency

HoldingEfficiency:
	목표 기간 대비 효율
________________________________________
5️⃣ Layer 2 — Regime Alignment Score
교전 당시 Regime과 전략 정합성 평가.
예:
	Crisis에서 Strike 실행 → -1
	Goldilocks에서 Core 실행 → +1
RAS=StrategySuitability×RegimeConfidence

________________________________________
6️⃣ Layer 3 — Strategy Effectiveness
최근 N회(예: 20회) 전략별 평균 성과:
	Win Rate
	Avg R:R
	Volatility Adjusted Return
SES=0.4×WinRate+0.4×AvgRR+0.2×VolAdjReturn

________________________________________
7️⃣ Layer 4 — Capital Efficiency Score
자본 대비 효율:
CES=PnL/AllocatedCapital

________________________________________
8️⃣ 통합 AAR Score
AAR_Score=0.35×TPS+0.25×RAS+0.25×SES+0.15×CES

________________________________________
9️⃣ 자동 학습 루프
9.1 Strike 조정
	최근 10회 AAR 평균 < 기준 → Strike Risk 강화
	Loss streak 패턴 반복 → 포지션 축소
________________________________________
9.2 Swing 조정
	특정 모듈 성과 저하 → 해당 모듈 가중치 20% 감소
	특정 섹터 반복 실패 → 산업 Bias 재평가
________________________________________
9.3 Core 조정
	Regime misalignment 빈번 → 신규 진입 조건 강화
	특정 산업 장기 부진 → Core 후보 제외
________________________________________
🔟 Regime 정확도 피드백
Regime 예측 정확도 계산:
RegimeAccuracy=RegimeAlignedProfitableTrades/TotalTrades

Accuracy < 55% → Regime 가중치 재조정
________________________________________
11️⃣ 자동 파라미터 조정 규칙
파라미터는 ±10% 범위 내에서만 자동 조정.
예:
	Strike MaxLoss 1% → 0.9% ~ 1.1% 범위
	Swing Bias 1.2 → 1.08 ~ 1.32 범위
극단적 변화 금지.
________________________________________
12️⃣ Warroom 표시 항목
AAR Dashboard:
	Fleet별 평균 AAR Score
	Regime Accuracy %
	Strategy Module Heatmap
	Learning Adjustment Status
________________________________________
13️⃣ 학습 루프 흐름
Engagement
   ↓
Battle Report
   ↓
AAR Score 계산
   ↓
Parameter Update (bounded)
   ↓
Next Allocation
________________________________________
14️⃣ 전략적 의미
이제 Aegis-X는:
✔ 전투를 기록한다
✔ 전투를 평가한다
✔ 전투에서 배운다
✔ 스스로 조정한다
________________________________________