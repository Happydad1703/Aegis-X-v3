37_Swing_Force_Strategy_and_Risk_Engine_Spec.md (v1.0)

이제 Swing Force Strategy & Risk Engine을 고정합니다.
Strike는 가속기,
Core는 장기 복리 엔진이라면,
Swing은 현금 흐름과 안정적 성장의 중추입니다.
공격형 성장 단계에서 Swing이 무너지면 전체가 불안정해집니다.
따라서 Swing은 Strike보다 훨씬 정교하고, Core보다 유연해야 합니다.
_
1️⃣ 설계 목표
Swing Force의 역할:
	중단기 추세 수익 확보
	Regime 적응형 회전
	Strike 손실 완충
	Core 전환 후보 발굴
________________________________________
2️⃣ 전략 구조
Swing은 3개 전략 모듈로 구성됩니다.
Swing Engine
   ├─ Trend-Follow Module
   ├─ Sector Rotation Module
   └─ Pullback Continuation Module
________________________________________
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
________________________________________
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
________________________________________
5️⃣ Pullback Continuation
조건
	강한 상승 후 3~5일 조정
	거래량 감소
	지지선 유지
진입
	반등 시점
________________________________________
6️⃣ Swing Risk Engine
Swing은 Strike보다 완만하지만,
Core보다 훨씬 빠릅니다.
________________________________________
6.1 포지션 제한
	단일 종목 ≤ 8%
	Battlefield 내 총 Swing ≤ 40%
________________________________________
6.2 손실 제한
	개별 종목 손절: -2%
	Swing Daily Loss: -4%
	Swing DD Cap: -7%
초과 시 Swing Budget 50% 축소.
________________________________________
6.3 Regime 기반 가중
Regime	Swing Bias
Goldilocks	1.2x
Sideways	1.0x
Tapering	0.8x
Crisis	0.5x
________________________________________
7️⃣ Swing Allocation 공식
Swing_final=Swing_base×RegimeBias×(1-CrisisProb)×(1-DD_ratio)

________________________________________
8️⃣ Strike와의 상호작용
조건:
	Strike 비활성화 시 → Swing Budget 10% 증가
	Strike 연속 손실 발생 → Swing이 완충
________________________________________
9️⃣ Core와의 상호작용
Swing에서 3회 이상 성공 + Regime 지속 → Core 후보 승격
즉:
Swing은 Core 인큐베이터.
________________________________________
🔟 Crisis Override
CrisisProb > 0.75:
Swing = 0.5 × 기존
Core 유지
Reserve 확대
________________________________________
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
________________________________________
12️⃣ 전략적 의미
Swing은:
	Strike의 공격성 완충
	Core의 장기성 연결
	현금 흐름 유지
즉, 시스템 안정성의 핵심.
________________________________________
🔥 현재 상태
우리는:
✔ Strike Risk Engine
✔ Swing Strategy Engine
✔ Growth-based Allocation
✔ Crisis Override
까지 완성했습니다.

 
