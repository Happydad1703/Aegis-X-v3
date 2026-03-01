29_Battlefield_Definition_Spec.md
Document ID: AEGIS-X-BF-v1.0
Owner: Strategic Command
Classification: Strategic Domain Definition
________________________________________
1. Purpose
본 문서는 Aegis-X에서 말하는 “전장(Battlefield)”의 공식 정의, 계층 구조, 운용 원칙을 규정한다.
전장은 단순 시장이 아니라:
전략·자본·리스크·통제의 적용 공간(Unit of Strategic Control)
이다.
________________________________________
2. Battlefield의 정의
2.1 Battlefield = 전략 운용 단위 시장 공간
Battlefield는 다음 조건을 만족하는 자율 전략 공간이다:
1.	독립적 Regime 상태를 가질 수 있다.
2.	독립적 Allocation Weight를 가진다.
3.	독립적 Risk Profile을 가질 수 있다.
4.	독립적 Fleet Target Set을 가진다.
5.	독립적 Crisis Probability를 가진다.
________________________________________
3. Battlefield 계층 구조
Battlefield는 3계층으로 정의한다.
________________________________________
Level 1: Global Theater
예:
•	Korea
•	US
•	Global Macro
이 레벨은 거시적 전략 공간이다.
________________________________________
Level 2: Market Battlefield
예:
•	KOSPI
•	KOSDAQ
•	S&P500
•	NASDAQ
•	USD/KRW
•	KTB (국채)
이 레벨이 실제 Warroom에서 “전장”으로 표시되는 기본 단위다.
________________________________________
Level 3: Tactical Sub-Field
예:
•	KOSPI Large Cap
•	KOSDAQ Small Cap
•	AI Sector
•	Semiconductor Sector
•	2차전지
Fleet가 실제 교전하는 공간이다.
________________________________________
4. Aegis-X 기본 Battlefield 구성 (v1.0 Baseline)
현재 Private/Single KIS 계좌 전제에서:
Primary Battlefields
•	🇰🇷 KOSPI
•	🇰🇷 KOSDAQ
•	💱 USD/KRW
•	🏦 KTB(국채 ETF 등)
(확장 가능하나 기본은 위 4개)
________________________________________
5. Battlefield의 속성(Attribute Contract)
각 Battlefield는 반드시 다음 속성을 가진다.
{
  "battlefield_id": "KOSPI",
  "theater": "Korea",
  "regime_state": "Goldilocks",
  "crisis_probability": 0.32,
  "allocation_weight": 0.45,
  "risk_mode": "ON",
  "freshness_status": "GREEN",
  "last_update_utc": "...",
  "data_source": "Hybrid Regime v3.4"
}
________________________________________
6. Battlefield와 Regime의 관계
6.1 Regime은 Battlefield별로 독립 계산 가능
예:
•	KOSPI → Goldilocks
•	KOSDAQ → Tapering
•	USD/KRW → Crisis Bias
Warroom 상단에는:
•	Global Regime (가중 평균)
•	Battlefield별 Regime Badge
를 동시에 표시해야 한다.
________________________________________
7. Battlefield와 Allocation의 관계
Allocation은 2단계로 구성된다.
Total Capital
    ↓
Battlefield Allocation
    ↓
Fleet Allocation
    ↓
Symbol Allocation
예:
•	KOSPI 40%
•	KOSDAQ 25%
•	USD/KRW 15%
•	Bond 20%
________________________________________
8. Battlefield Risk Isolation
Battlefield 단위로:
•	DD 계산
•	Volatility 계산
•	Exposure 계산
•	Crisis Probability 계산
가능해야 한다.
Retract는 Battlefield별로도 가능해야 한다.
예:
•	KOSDAQ만 Retract-2
•	KOSPI 유지
________________________________________
9. Warroom UI 반영 방식
Header 표시
Global Regime: Tapering
KOSPI: Goldilocks
KOSDAQ: Tapering
USD/KRW: Neutral
색상 Badge로 표시.
________________________________________
중앙 Canvas
Battlefield 선택 시:
•	해당 Battlefield 전용 SAA Radar
•	해당 Battlefield Fleet Targets
•	해당 Battlefield Risk Panel
•	해당 Battlefield Execution Log
________________________________________
10. Battlefield 전환 규칙
Battlefield는:
•	동시 다중 모니터링 가능
•	단일 전장 집중 모드 지원 (Focus Mode)
•	Fullscreen 전장 모드 지원
________________________________________
11. Battlefield Emergency Scope
Emergency Stop은:
•	Global 적용 가능
•	Battlefield 단위 적용 가능
예:
•	Global Stop
•	KOSDAQ Stop only
________________________________________
12. Battlefield Snapshot DB 설계
snapshot_key 예:
•	battlefield_KOSPI_status
•	battlefield_KOSDAQ_status
•	battlefield_USDKRW_status
각 snapshot은:
•	regime
•	allocation
•	risk
•	crisis_prob
•	freshness
•	latency
________________________________________
13. Scheduler와 Battlefield 관계
Battlefield별 refresh_interval 가능:
예:
•	KOSPI: 5분
•	USD/KRW: 1분
•	Bond: 10분
자원 부족 시:
•	Tactical Sub-Field refresh 우선 축소
•	Core Battlefield 유지
________________________________________
14. Battlefield 정의의 전략적 의미
Battlefield 정의가 명확해야:
•	Retract가 정확히 어디에 적용되는지
•	Risk가 격리되는지
•	Allocation이 붕괴되지 않는지
•	Crisis 전염을 막을 수 있는지
결정된다.
________________________________________
결론
Aegis-X에서 Battlefield는:
•	단순 시장이 아니라
•	전략 운용 단위
•	자본 배분 단위
•	리스크 격리 단위
•	통제 단위
이다.
