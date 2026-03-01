58_Capital_Scaling_Strategy_Spec.md (v1.0

이제 **Capital Scaling Strategy (자본 성장 단계별 공격/방어 전환 수학화)**를 고정합니다.
이 단계는 단순 배분이 아니라:
자본 규모가 바뀌면
시스템의 “성격”이 바뀌도록 만드는 설계
입니다.

1️⃣ 기본 철학
초기 자본:
	공격적
	변동성 수용
	빠른 성장
자본이 커질수록:
	복리 유지
	리스크 축소
	Strike 비중 자동 감소
	Core 비중 자동 증가
________________________________________
2️⃣ 핵심 변수
G=CurrentEquity/InitialEquity

G = 성장 배수
________________________________________
3️⃣ Aggression Decay Function (ADF)
기존 FBGC 기반 확장.
A(G)=A_max-k⋅ln⁡(G)

제약:
A_min≤A(G)≤A_max

________________________________________
기본값
	Amax = 1.4
	Amin = 0.7
	k = 0.2
________________________________________
4️⃣ Fleet 비중 동적 변화
기본 초기 비중:
	Strike: 20%
	Swing: 35%
	Core: 35%
	Reserve: 10%
________________________________________
성장 배수 적용
Strike(G)=Strike_base×A(G)
Core(G)=Core_base+(Strike_base-Strike(G))

Swing은 완만 유지.
Reserve는 잔여.
________________________________________
5️⃣ 단계별 성격 변화
G	Strike	Core	성격
1x	20%	35%	공격적
2x	15%	40%	균형
3x	12%	43%	점진적 안정
5x	9%	46%	복리 중심
10x	7%	48%	방어 강화
________________________________________
6️⃣ Risk 강화 함수
Drawdown 허용치도 축소.
MaxDD(G)=MaxDD_base/√G

예:
	초기: -15%
	4x 성장 시: -7.5%
________________________________________
7️⃣ Daily Loss Cap 축소
DailyCap(G)=BaseCap/√G

________________________________________
8️⃣ Crisis 민감도 강화
CrisisThreshold(G)=BaseThreshold-0.1×〖log⁡〗_10 (G)

성장할수록 Crisis 민감도 증가.
________________________________________
9️⃣ 코드 구현
capital_scaling.py
import math

def aggression_factor(G, Amax=1.4, Amin=0.7, k=0.2):
    if G <= 0:
        return Amax
    val = Amax - k * math.log(G)
    return max(Amin, min(Amax, val))


def compute_scaled_fleet(G, strike_base=0.2, swing_base=0.35, core_base=0.35):
    A = aggression_factor(G)

    strike = strike_base * A
    core = core_base + (strike_base - strike)
    swing = swing_base
    reserve = 1 - (strike + swing + core)

    return {
        "growth_multiple": round(G, 4),
        "aggression_factor": round(A, 4),
        "weights": {
            "STRIKE": round(strike, 4),
            "SWING": round(swing, 4),
            "CORE": round(core, 4),
            "RESERVE": round(reserve, 4)
        }
    }


def scaled_max_dd(G, base_dd=-0.15):
    return base_dd / math.sqrt(G)


def scaled_daily_cap(G, base_cap=-0.03):
    return base_cap / math.sqrt(G)
________________________________________
🔟 Engine Worker 통합
engine_worker에서:
from app.scaling.capital_scaling import compute_scaled_fleet

G = portfolio_state["total_equity"] / initial_equity

scaled_weights = compute_scaled_fleet(G)
기존 Fleet Budget 대신 scaled 적용.
________________________________________
11️⃣ Warroom 표시
Header에 추가:
	Growth Multiple: 1.87x
	Aggression Factor: 1.12
	Dynamic DD Limit: -8.7%
	Dynamic Daily Cap: -1.9%
________________________________________
🔥 전략적 의미
이제 Aegis-X는:
✔ 초기에는 공격적
✔ 성장하면 자동으로 보수화
✔ 리스크 허용치 자동 축소
✔ Strike 자동 축소
✔ Core 자동 확대
즉,
자본이 커질수록 시스템이 스스로 “성숙”합니다.
________________________________________
🎯 현재 완성도
우리는 이제:
	전장 구조
	Force 체계
	Risk 통제
	Mode 통제
	Order Engine
	Portfolio Engine
	AAR 학습
	Backtest
	Follow-the-Sun
	Capital Scaling
까지 모두 설계 완료했습니다.
________________________________________
 
