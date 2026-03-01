39_Regime_Engine_Mathematical_Spec.md (v1.0)
________________________________________
1️⃣ Regime Engine의 목적
Regime Engine은:
시장의 “상태(State)”를 정량적으로 정의하는 함수
입니다.
단순 감성 판단이 아니라,
구조화된 점수 시스템 + 확률 기반 분류 모델입니다.
________________________________________
2️⃣ Regime 4상태 정의
Regime	의미	Score
Goldilocks	성장 + 안정	+2
Sideways	방향성 약함	+1
Tapering	유동성 축소	-1
Crisis	시스템 리스크	-2
________________________________________
3️⃣ 입력 변수 구조
Regime Engine은 4개 계층 신호를 통합합니다.
Layer A: Price Structure
Layer B: Volatility
Layer C: Liquidity & Macro
Layer D: Sentiment & News
________________________________________
4️⃣ Layer A — Price Structure Score (PS)
PS=0.4×TrendScore+0.3×BreadthScore+0.3×MomentumScore

TrendScore:
	Index 60MA > 120MA → +1
	반대 → -1
BreadthScore:
	상승 종목 비율 > 60% → +1
	< 40% → -1
MomentumScore:
	RSI(14) 50~65 → +1
	< 40 → -1
________________________________________
5️⃣ Layer B — Volatility Score (VS)
VS=-(CurrentVol-MeanVol)/StdVol

Vol 급등 시 점수 하락.
정규화 후 -2 ~ +2 범위로 제한.
________________________________________
6️⃣ Layer C — Liquidity & Macro Score (LM)
입력:
	금리 추세
	달러 지수
	장단기 금리차
	유동성 지표
예:
	금리 하락 + 달러 약세 → +1
	금리 급등 + 달러 강세 → -1
________________________________________
7️⃣ Layer D — Sentiment & News Score (SN)
LLM은 여기서만 사용.
구성:
	글로벌 뉴스 요약
	정책 발표
	지정학 리스크
LLM 출력은 -1 ~ +1 범위로 제한.
LLM 가중치는 최대 20%로 제한.
________________________________________
8️⃣ 통합 Regime Score
RegimeScore=0.35×PS+0.25×VS+0.25×LM+0.15×SN

________________________________________
9️⃣ Crisis Probability 계산
CrisisProb는 Logistic 모델 사용:
CrisisProb=1/(1+e^(-k(RegimeScore+VolSpike+MacroShock)) )

권장 k = 1.2
________________________________________
🔟 Regime 분류 기준
RegimeScore	Regime
≥ +1.0	Goldilocks
0 ~ +1.0	Sideways
-1.0 ~ 0	Tapering
≤ -1.0	Crisis
________________________________________
11️⃣ 안정성 필터
Regime은 3연속 동일 방향 변동 시에만 확정.
즉:
	단발성 변동으로 상태 변경 금지.
	최소 3 스냅샷 연속 유지.
________________________________________
12️⃣ Regime Engine과 Force 연결
Regime	Strike	Swing	Core
Goldilocks	적극	적극	확대
Sideways	중간	기본	유지
Tapering	축소	축소	선택
Crisis	0	축소	방어
________________________________________
13️⃣ DB Snapshot 구조
snapshot_key = regime_current
{
  "price_score": ...,
  "vol_score": ...,
  "macro_score": ...,
  "sentiment_score": ...,
  "regime_score": ...,
  "regime_state": "Goldilocks",
  "crisis_probability": ...,
  "confidence": ...,
  "timestamp_utc": ...
}
