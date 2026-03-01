# 36_Global_Battlefield_Allocation_Matrix_v2.0

1️⃣ 전체 구조 개요
Allocation은 4단계로 결정됩니다.
Step 1: Capital Scale → Aggression Factor
Step 2: Regime & Crisis → Battlefield Weights
Step 3: Battlefield → Fleet Budget (Strike/Swing/Core/Reserve)
Step 4: Strike Risk Engine → Final Adjustment

2️⃣ Step 1 — Capital Scale 적용
이미 정의된:

이 Aggression Factor는 Strike 비율에만 적용됩니다.

3️⃣ Step 2 — Battlefield Weight 계산
각 Battlefield의 Weight:

권장 파라미터:
α = 0.05
β = 0.20
모든 Battlefield Weight는 정규화.

예시 (공격형 상황)

4️⃣ Step 3 — Fleet 내부 분배
각 Battlefield 내부에서:

Swing은 완충 역할 유지.

예시 (G=1, A=1.4)
Strike = 0.20 × 1.4 = 0.28
Core = 0.35 - 0.08 = 0.27
Swing = 0.35
Reserve = 0.10

5️⃣ Step 4 — Strike Risk Engine 통합
Strike는 추가로 조정됩니다.
최종 Strike Weight:

조건 발생 시:
Loss streak ≥ 3 → Strike = 0
CrisisProb > 0.65 → Strike = 0
DailyLoss > 3% → Strike = 0

6️⃣ Crisis Override (전역)
조건:
Global CrisisProb > 0.75
Portfolio DD < -10%
즉시:
Strike = 0
Swing = 0.5 × 기존
Core 유지
Reserve = 잔여

7️⃣ Allocation 안정성 확보
최종 Weight 합은 항상 1.
정규화 단계:


8️⃣ Warroom 표시 항목
Allocation Panel에는 다음이 표시됩니다:
Growth Multiple (G)
Aggression Factor
Battlefield Weights
Fleet Weights
Strike Final Adjustment Ratio
Crisis Override Status

9️⃣ 이 구조의 전략적 의미
✔ 초기 소규모 자본 → Strike가 가속
✔ 성장하면 자동 안정화
✔ Crisis 발생 시 자동 방어
✔ DD 발생 시 자동 축소
✔ Strike는 절대 폭주 불가

🔥 지금 상태
Aegis-X는 이제:
Growth-aware
Risk-aware
Regime-aware
Crisis-aware
Volatility-aware
자본 배분 시스템을 갖추었습니다.


이제 Swing Force Strategy & Risk Engine을 고정합니다.
Strike는 가속기,
Core는 장기 복리 엔진이라면,
Swing은 현금 흐름과 안정적 성장의 중추입니다.
공격형 성장 단계에서 Swing이 무너지면 전체가 불안정해집니다.
따라서 Swing은 Strike보다 훨씬 정교하고, Core보다 유연해야 합니다.

📘37_Swing_Force_Strategy_and_Risk_Engine_Spec.md (v1.0)

1️⃣ 설계 목표
Swing Force의 역할:
중단기 추세 수익 확보
Regime 적응형 회전
Strike 손실 완충
Core 전환 후보 발굴

2️⃣ 전략 구조
Swing은 3개 전략 모듈로 구성됩니다.
Swing Engine
   ├─ Trend-Follow Module
   ├─ Sector Rotation Module
   └─ Pullback Continuation Module

3️⃣ Trend-Follow Module
조건
20MA > 60MA
RSI 50~65
Volume 증가
진입
Breakout 또는 MA pullback
청산
20MA 이탈
목표 R:R = 1.8~2.2

4️⃣ Sector Rotation Module
입력
Battlefield Industry Bias (STRATCOM 하달)
상대강도(RS)
조건
RS 상위 30%
Regime = Goldilocks or Sideways
특징
종목보다 섹터 중심
변동성 중간

5️⃣ Pullback Continuation
조건
강한 상승 후 3~5일 조정
거래량 감소
지지선 유지
진입
반등 시점

6️⃣ Swing Risk Engine
Swing은 Strike보다 완만하지만,
Core보다 훨씬 빠릅니다.

6.1 포지션 제한
단일 종목 ≤ 8%
Battlefield 내 총 Swing ≤ 40%

6.2 손실 제한
개별 종목 손절: -2%
Swing Daily Loss: -4%
Swing DD Cap: -7%
초과 시 Swing Budget 50% 축소.

6.3 Regime 기반 가중

7️⃣ Swing Allocation 공식


8️⃣ Strike와의 상호작용
조건:
Strike 비활성화 시 → Swing Budget 10% 증가
Strike 연속 손실 발생 → Swing이 완충

9️⃣ Core와의 상호작용
Swing에서 3회 이상 성공 + Regime 지속 → Core 후보 승격
즉:
Swing은 Core 인큐베이터.

🔟 Crisis Override
CrisisProb > 0.75:
Swing = 0.5 × 기존
Core 유지
Reserve 확대

11️⃣ DB Snapshot 구조
snapshot_key = swing_force_status
{
  "swing_exposure": ...,
  "regime_bias": ...,
  "daily_pnl": ...,
  "drawdown": ...,
  "activation_status": "ACTIVE",
  "rotation_sector": "...",
  "timestamp_utc": "..."
}

12️⃣ 전략적 의미
Swing은:
Strike의 공격성 완충
Core의 장기성 연결
현금 흐름 유지
즉, 시스템 안정성의 핵심.

🔥 현재 상태
우리는:
✔ Strike Risk Engine
✔ Swing Strategy Engine
✔ Growth-based Allocation
✔ Crisis Override
까지 완성했습니다.

이제 Core Force (중장기군) Compound Optimization Engine을 고정합니다.
Strike는 가속기,
Swing은 현금 흐름,
Core는 인생을 바꾸는 복리 엔진입니다.
Core가 안정적·지속적으로 복리 성장을 만들어내야
자본이 커졌을 때 시스템이 무너지지 않습니다.