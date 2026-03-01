57_Global_Follow_The_Sun_Architecture_Spec.md (v1.0)
________________________________________
1️⃣ 전략 원칙
Follow-the-Sun은
“모든 시장에 다 들어간다”가 아닙니다.
정확한 정의는:
시간대를 확장하되
자본은 선택적으로 투입한다.
________________________________________
2️⃣ 전장 계층 구조
Tier 0 — Master Main Base
	KOSPI
	KOSDAQ
✔ 실자본 운용 중심
✔ Core/Swing/Strike 전부 운용
________________________________________
Tier 1 — Strategic Extension (시간대 연결용)
	US Proxy (SPY / QQQ 등 ETF proxy)
	USD Index / Bond Proxy
✔ Regime Intelligence 강화 목적
✔ Paper/Pilot 제한 운용
________________________________________
Tier 2 — Intelligence Only
	EU Index Proxy
	Asia Ex-KR Proxy
✔ 뉴스/매크로 분석용
✔ 직접 자본 투입 금지 (초기)
________________________________________
3️⃣ 시간대 전략 (UTC 기준)
Asia Session (00:00~08:00 UTC)
    └─ KR Focus

EU Session (08:00~13:00 UTC)
    └─ Intelligence Mode

US Session (13:00~21:00 UTC)
    └─ US Proxy Swing / Paper

Night Cycle (21:00~00:00 UTC)
    └─ Risk Compression / Backtest
________________________________________
4️⃣ Session-Based Engine Behavior
4.1 Session 감지
from datetime import datetime, timezone

def get_current_session():
    hour = datetime.now(timezone.utc).hour

    if 0 <= hour < 8:
        return "ASIA"
    elif 8 <= hour < 13:
        return "EU"
    elif 13 <= hour < 21:
        return "US"
    else:
        return "NIGHT"
________________________________________
4.2 Session별 정책
Session	Strike	Swing	Core	Notes
ASIA	FULL	FULL	FULL	KR 실전
EU	0	0	유지	정보수집
US	제한	가능	유지	Proxy
NIGHT	0	0	유지	Risk 압축
________________________________________
5️⃣ Capital Allocation 확장 로직
기존 Allocation Matrix에 Session Bias 추가:
W_final=W_base×RegimeBias×SessionBias

________________________________________
Session Bias 예시
def session_bias(session):
    if session == "ASIA":
        return 1.0
    if session == "US":
        return 0.6
    if session == "EU":
        return 0.3
    return 0.2
________________________________________
6️⃣ Follow-the-Sun 운용 모델
구조
KR 장 종료
   ↓
US Proxy 감시
   ↓
글로벌 뉴스/매크로 반영
   ↓
KR 장 시작 시 반영
즉:
미국 → 한국으로 정보 전파.
________________________________________
7️⃣ Warroom 확장
Header에 추가:
	Current Session
	Active Battlefield
	Session Bias %
	Time to Next Session
________________________________________
8️⃣ Global Intelligence Layer
LLM 분업 구조:
역할	LLM
STRATCOM	GPT-4 / Claude
Macro Intel	Gemini
News Filtering	DeepSeek
Tactical Filter	Local Model
LLM는 Regime 영향 최대 ±0.2로 제한.
________________________________________
9️⃣ 자본 규모별 확장 정책
자본 규모	Global 확장 수준
< 1X	KR Only
1X~3X	US Proxy 제한
3X~10X	일부 ETF 실전
10X+	다중 전장
초기 단계:
👉 US는 Paper 또는 Pilot 소액만.
________________________________________
🔟 위험 통제
Follow-the-Sun 확장에서 반드시 추가할 것:
	Overnight Gap Risk Filter
	USD 급변 동기화
	글로벌 VIX 연동
CrisisProb 계산 시:
	VIX 급등 → CrisisProb 보정
________________________________________
🔥 전략적 의미
이 설계는:
	무리한 글로벌 확장 금지
	시간대 확장만 허용
	자본은 KR 중심
	글로벌은 정보 우위 확보용

 
🎯 현재 시스템 위치
Aegis-X는 이제:
✔ Master Base (KR)
✔ Global Intelligence
✔ Session-Aware Allocation
✔ Risk Compression Night Mode
를 갖추었습니다.
________________________________________
 
