09_Meta_Control_Spec.md
Document ID: AEGIS-X-META-v1.0
Owner: Strategic Command (JCS)
Classification: Strategy Lifecycle & Control Specification
________________________________________
1. Purpose
Meta-Control Layer의 목적:
1.	전략 성과를 정량 평가
2.	전략 간 비교 및 자본 재배분
3.	전략 승격·격리·퇴역 결정
4.	구조 붕괴 조기 감지
5.	전략 계보(Lineage) 관리
________________________________________
2. Strategy Object Definition
전략은 실행 코드가 아니라 버전된 구성 묶음이다.
{
  "strategy_id": "AegisX_v3.4",
  "regime_model": "REGIME_v2.1",
  "allocation_profile": "Balanced_TaperAware_v3",
  "roe_profile": "ROE_Set_6",
  "risk_profile": "Risk_v4.2",
  "learning_profile": "Adaptive_LR_0.02",
  "capital_profile": "KellyLite_0.35",
  "parent_strategy": "AegisX_v3.3",
  "created_at": "...",
  "status": "LIVE"
}
________________________________________
3. Strategy State Machine
SHADOW → CANDIDATE → LIVE → RETIRED
           ↑
        QUARANTINE
________________________________________
3.1 State Definitions
SHADOW
•	Twin 환경에서 테스트 중
•	실자본 없음
CANDIDATE
•	Twin 통과
•	소규모 자본 배정 대기
LIVE
•	실자본 운용 중
•	Meta-Control 모니터링 대상
QUARANTINE
•	성과 저하
•	신규 자본 배정 중단
•	재검증 대기
RETIRED
•	폐기
•	재활성화 불가
________________________________________
4. Strategy Evaluation Framework
________________________________________
4.1 Meta Score Formula
Meta Score =
  0.30 * normalized_cagr
+ 0.30 * normalized_sharpe
- 0.20 * normalized_dd
+ 0.10 * crisis_performance
- 0.10 * instability_penalty
________________________________________
4.2 Instability Penalty
instability =
rolling_sharpe_std × tail_loss_frequency
높을수록 불리.
________________________________________
4.3 Crisis Performance Weight
Crisis 구간 CAGR 가중치 1.5× 적용.
________________________________________
5. Strategy Promotion Rule
SHADOW → CANDIDATE 조건:
•	Twin Sharpe ≥ LIVE + 0.05
•	Max DD 악화 ≤ 2%
•	Crisis 성과 ≥ LIVE
•	Monte Carlo 안정성 통과
CANDIDATE → LIVE 조건:
•	30일 Shadow 실시간 검증 통과
•	Risk 승인
•	Governance 승인
________________________________________
6. Strategy Demotion / Quarantine Rule
다음 중 2개 이상 발생 시 QUARANTINE:
•	30일 Sharpe < 0
•	Rolling DD > 허용치
•	Crisis 대응 실패
•	Risk Mode OFF 빈도 과다
________________________________________
7. Retirement Rule
다음 발생 시 RETIRED:
•	3개월 CAGR < 0
•	Twin 재검증 실패
•	구조 Drift 적응 실패
________________________________________
8. Multi-Strategy Capital Allocation
Meta-Control은 복수 전략 동시 운용 가능.
strategy_weight_i = softmax(Meta Score_i)
제약:
•	단일 전략 ≤ 70%
•	최소 2개 전략 유지 권장
________________________________________
9. Strategy Lineage Tracking
모든 전략은 부모 전략을 가진다.
v3.1
  └── v3.2 (Kelly 조정)
        └── v3.3 (Tapering 방어 강화)
              └── v3.4 (FX Hedge 추가)
PostgreSQL strategy_lineage 테이블에 저장.
________________________________________
10. Evolution Trigger Integration
다음 발생 시 Evolution Proposal 요청:
•	Efficiency Score 급락
•	Regime Drift
•	Capacity 붕괴
•	Crisis 대응 실패
LLM은 Proposal 생성 → Twin 검증 → Meta 판단.
________________________________________
11. Capital Transition Protocol
전략 교체 시 즉시 100% 전환 금지.
권장 단계:
•	20% → 40% → 70% → 100%
•	각 단계 최소 5거래일 유지
________________________________________
12. Governance Integration
전략 상태 변경 시:
{
  "decision_type": "STRATEGY_STATE_CHANGE",
  "old_state": "CANDIDATE",
  "new_state": "LIVE",
  "meta_score": 0.78,
  "approved_by": "Meta-Control + Risk + Governance"
}
Audit Log 기록 필수.
________________________________________
13. Risk Interaction
Meta-Control은 Risk Engine을 우회할 수 없다.
우선순위:
Risk > Meta-Control > Strategy
________________________________________
14. Monitoring Dashboard Requirements
Warroom Meta Panel:
Strategy	State	Meta Score	DD	Sharpe	Weight
추가:
•	Strategy Drift Indicator
•	Evolution Pending Flag
•	Quarantine Alert
________________________________________
15. Verification Criteria
•	State transition test
•	Meta Score reproducibility test
•	Multi-strategy allocation test
•	Quarantine trigger test
•	Governance log validation