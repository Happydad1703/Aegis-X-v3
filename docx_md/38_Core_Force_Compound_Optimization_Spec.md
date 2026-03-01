38_Core_Force_Compound_Optimization_Spec.md (v1.0)

이제 Core Force (중장기군) Compound Optimization Engine을 고정합니다.
Strike는 가속기,
Swing은 현금 흐름,
Core는 인생을 바꾸는 복리 엔진입니다.
Core가 안정적·지속적으로 복리 성장을 만들어내야
자본이 커졌을 때 시스템이 무너지지 않습니다.
________________________________________

________________________________________
1️⃣ Core Force의 철학
Core는:
	고빈도 거래 금지
	추세 + 산업 메가트렌드 중심
	변동성보다 구조적 성장에 베팅
	자본 증가 시 비중 확대
목표:
CAGR 극대화 + DD 통제
________________________________________
2️⃣ Core 전략 구조
Core는 3개의 계층으로 구성됩니다.
Core Engine
   ├─ Structural Trend Module
   ├─ Industry Megatrend Module
   └─ Regime Alignment Filter
________________________________________
3️⃣ Structural Trend Module
조건
	60MA > 120MA
	120MA 기울기 > 0
	Market Regime = Goldilocks / Sideways
특징
	장기 추세 확인 후 진입
	추세 붕괴 시만 청산
________________________________________
4️⃣ Industry Megatrend Module
입력:
	STRATCOM 산업 Bias
	글로벌 ETF 상대강도
	산업 뉴스 요약 (LLM 보조)
조건:
	RS 상위 20%
	산업 모멘텀 지속 ≥ 2주
________________________________________
5️⃣ Regime Alignment Filter
Regime과 정합되지 않으면 Core 신규 진입 금지.
Regime	Core Bias
Goldilocks	적극
Sideways	선택적
Tapering	방어적
Crisis	신규 진입 금지
________________________________________
6️⃣ Core Risk Engine
Core는 Strike보다 느리지만,
리스크 통제는 반드시 존재합니다.
________________________________________
6.1 포지션 제한
	단일 종목 ≤ 10%
	Battlefield Core ≤ 50%
________________________________________
6.2 손절 기준
Core는 넓은 손절 사용:
	구조적 추세 붕괴
	120MA 이탈
	DD -12% 초과 시 축소
________________________________________
6.3 Core DD Cap
	Core 전체 DD -15% → Core 30% 축소
	Portfolio DD -10% → Core 방어 모드
________________________________________
7️⃣ Compound Optimization 모델
Core는 재투자 구조를 가집니다.
복리 성장:
C_(t+1)=C_t×(1+r_core)

하지만 Drawdown 민감도 감소를 위해:
AdjustedReturn=r_core×(1-VolatilityRatio)

________________________________________
8️⃣ Growth 기반 자동 확대
Growth Multiple G가 증가할수록:
CoreWeight=CoreBase+(1-A(G))×0.2

즉, 자본이 커질수록 Core 비중 자동 증가.
________________________________________
9️⃣ Core → Swing → Strike 관계
	Swing에서 성공한 종목 → Core 승격
	Strike에서 강한 테마 발견 → Swing으로 전환
	Core는 절대 Strike로 전환하지 않음
________________________________________
🔟 Crisis Override
CrisisProb > 0.75:
Core 유지
Swing 축소
Strike 0
Reserve 확대
Core는 완전 청산하지 않음
(장기 복리 엔진 보호)
________________________________________
11️⃣ DB Snapshot 구조
snapshot_key = core_force_status
{
  "core_exposure": ...,
  "trend_alignment_score": ...,
  "industry_bias": ...,
  "core_drawdown": ...,
  "regime_alignment": "...",
  "timestamp_utc": "..."
}
________________________________________
12️⃣ 전략적 의미
이제 시스템은:
	Strike → 가속
	Swing → 유지
	Core → 복리
	Reserve → 방어
완전한 4군 구조를 가졌습니다.