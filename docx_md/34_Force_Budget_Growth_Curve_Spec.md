34_Force_Budget_Growth_Curve_Spec.md (v1.0)

이제 Force Budget Growth Curve (FBGC) 를 수학적으로 고정하겠습니다.
목표는:
초기에는 공격적으로,
자본이 커질수록 자동으로 안정화.
________________________________________

1) 정의
기준 변수
	C_0: 초기 자본
	C_t: 현재 자본
	G=C_t/C_0 : 성장배율
	A(G): Aggression Factor (0.6 ~ 1.4 범위 권장)
________________________________________
2) Aggression Factor 함수
공격성은 성장배율이 커질수록 감소해야 합니다.
부드럽게 감소시키기 위해 로그 기반 감소 함수를 사용합니다.
A(G)=max⁡(A_min,"  " A_max-k⋅ln⁡(G))

권장 파라미터
	A_max=1.4(초기 공격성)
	A_min=0.7(최종 보수성)
	k=0.2
예시
성장배율 G	A(G)
1.0	1.40
2.0	1.26
3.0	1.18
5.0	1.08
10.0	0.94
20.0	0.78
→ 10배 이상 성장하면 자동으로 거의 균형형으로 전환.
________________________________________
3) Fleet Budget 공식
기본 초기 배분(공격형 기준):
Strike_base  = 0.20
Swing_base   = 0.35
Core_base    = 0.35
Reserve_base = 0.10
Strike 조정
Strike(G)=Strike_base×A(G)

Core 조정
Core(G)=Core_base+(Strike_base-Strike(G))

즉, Strike가 줄어든 만큼 Core가 자동 증가.
Swing은 완충역할
Swing(G)=Swing_base

Reserve는 Crisis 확장 가능
Reserve(G)=1-(Strike+Swing+Core)

________________________________________
4) Growth Phase별 직관적 모습
성장배율	Strike	Swing	Core	Reserve
1x	28%	35%	27%	10%
2x	25%	35%	30%	10%
5x	22%	35%	33%	10%
10x	19%	35%	36%	10%
20x	15%	35%	40%	10%
(Strike 감소 → Core 증가 구조)
________________________________________
5) Drawdown 기반 즉시 축소 로직 (중요)
성장배율과 별개로, DD 발생 시 즉시 공격성 축소:
A_effective=A(G)×(1-DD_ratio)

예:
	DD = -5% → 공격성 5% 감소
	DD = -10% → 공격성 10% 감소
DD 회복 시 점진 복구.
________________________________________
6) Crisis Override (강제 규칙)
조건:
	CrisisProb > 0.75
	Daily Loss < -3%
	Portfolio DD < -10%
즉시:
Strike = 0
Swing  = 0.5 × 기존
Core   = 기존 유지
Reserve = 잔여 전부
________________________________________
7) DB Snapshot 항목 추가
fleet_budget_snapshot
{
  "capital": C_t,
  "growth_multiple": G,
  "aggression_factor": A(G),
  "strike_weight": ...,
  "swing_weight": ...,
  "core_weight": ...,
  "reserve_weight": ...,
  "timestamp_utc": "...",
  "freshness_status": "GREEN"
}
Warroom에서 실시간 표시.
________________________________________
8) 전략적 의미
이 구조의 장점:
	초기에는 기동타격대가 가속기 역할
	자본 증가 시 자동으로 Core 중심 전환
	Drawdown 발생 시 즉시 수축
	Crisis 시 완전 방어 모드
→ “공격은 선택, 방어는 자동”
________________________________________
 
이제 Strike Force 전용 Risk Engine을 고정합니다.
목표는 단 하나입니다:
공격은 날카롭게,
폭주는 불가능하게.
Strike는 자본 가속기이지만,
전체 시스템을 위협할 수 있는 유일한 요소이기도 합니다.
따라서 Strike는 전체 시스템과 다른 규율을 적용합니다.