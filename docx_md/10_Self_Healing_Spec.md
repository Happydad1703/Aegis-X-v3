10_Self_Healing_Spec.md
Document ID: AEGIS-X-HEAL-v1.0
Owner: Strategic Command / Risk Office
Classification: System Survivability & Recovery Specification
________________________________________
1. Purpose
Self-Healing Layer의 목적:
1.	급격한 시장 충격 격리
2.	구조적 Drift 감지 및 전략 재보정
3.	시스템 성능 붕괴 조기 탐지
4.	Emergency Fallback 전략 실행
5.	자본 보존 최우선 확보
________________________________________
2. Alarm Hierarchy
Self-Healing은 3단계 경보 체계를 사용한다.
________________________________________
🔹 Level 1: Tactical Alarm (충격 경보)
Trigger 조건:
•	30일 Rolling Sharpe < 0
•	Portfolio DD ≤ -8%
•	Vol Spike ≥ 1.8
•	Crisis Probability ≥ 0.7
행동:
•	Strike 100% 중단
•	Tactical 50% 축소
•	신규 진입 일시 정지 (3~5일)
________________________________________
🔹🔹 Level 2: Structural Alarm (구조 경보)
Trigger 조건 (2개 이상):
•	Regime 예측 정확도 급락
•	Crisis 구간 방어 실패
•	Factor 상관 구조 급변
•	LLM Narrative Shift 급증
•	Meta Score 급락
행동:
•	Learning Engine Freeze
•	Evolution Proposal 강제 생성
•	Twin 재검증 실행
•	Equity Budget 자동 30% 축소
________________________________________
🔹🔹🔹 Level 3: Systemic Alarm (시스템 붕괴)
Trigger 조건:
•	2개 이상 LIVE 전략 동시 실패
•	3개월 CAGR < 0
•	Rolling DD ≤ -15%
•	Crisis 대응 실패 + Tail Loss 급증
행동:
•	Equity Exposure ≤ 20%
•	Bond/FX Hedge 확대
•	모든 전략 SHADOW 전환
•	Fallback Strategy 즉시 실행
•	Incident Report 생성
________________________________________
3. System Health Index
Self-Healing은 단일 지표를 유지한다.
System Health =
0.25 Regime Integrity
+0.25 Strategy Stability
+0.25 Risk Stability
+0.25 Performance Stability
범위: 0 ~ 1
Health	Mode
≥ 0.75	NORMAL
0.5~0.75	ALERT
0.3~0.5	RECOVERY
< 0.3	EMERGENCY
________________________________________
4. Regime Integrity Test
목적: Regime Engine 오류 탐지
검증:
Expected Return (Regime i)
vs
Actual Return (Regime i)
3회 연속 불일치 → Integrity Score 감소
Integrity < 0.5 → Structural Alarm
________________________________________
5. Drift Detection Model
________________________________________
5.1 Regime Drift
•	5일 이동 평균 기울기
•	20일 대비 방향성 급변
________________________________________
5.2 Correlation Drift
•	Rolling Covariance Matrix
•	Eigenvalue 구조 변화
Eigenvalue 급변 → Structural Alarm 가중치 증가
________________________________________
6. Shock Containment Mode
발동 시:
FREEZE_NEW_ENTRIES = TRUE
risk_per_trade = risk_per_trade × 0.5
equity_budget = equity_budget × 0.7
최소 유지 기간: 3 거래일
________________________________________
7. Fallback Strategy Specification
Fallback 전략은 반드시:
•	단순 추세 기반
•	저레버리지
•	Cross-Asset Hedge 포함
•	DD ≤ 10% 목표
예:
•	200일 이동평균 기반
•	USD Hedge
•	Bond 40%
________________________________________
8. Recovery Protocol
System Health ≥ 0.6 회복 시:
1.	Strike 점진적 복구
2.	Learning 재개
3.	Risk Mode 정상화
단계적 복구 (20%씩 증가)
________________________________________
9. Governance Integration
Level 2 이상 Alarm 시 자동 생성:
{
  "incident_id": "...",
  "alarm_level": "STRUCTURAL",
  "trigger_metrics": {...},
  "actions_taken": [...],
  "health_index": 0.42
}
PostgreSQL incident_log 기록 필수.
________________________________________
10. Interaction Hierarchy
Self-Healing
    >
Risk Engine
    >
Meta-Control
    >
Strategy
Self-Healing은 모든 하위 레이어를 override 가능.
________________________________________
11. Verification Tests
Test	Required
Vol Spike simulation	✔
DD breach simulation	✔
Crisis replay	✔
Regime misclassification test	✔
Multi-strategy failure test	✔
Fallback activation test	✔
________________________________________
12. Dashboard Requirements
Warroom System Health Panel:
Metric	Value	Status
Health Index	0.68	YELLOW
Alarm Level	1	Tactical
Regime Integrity	0.71	OK
Strategy Stability	0.52