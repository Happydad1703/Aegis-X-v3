18_CIC_Warroom_Spec.md
Document ID: AEGIS-X-CIC-v1.0
Owner: Strategic Command / Control Engineering
Classification: Warroom Command & Control Specification
________________________________________
1. Purpose
본 문서는 Aegis-X Warroom (CIC: Command & Control Center)의:
•	DB-First UI 원칙
•	Data Transparency 규칙
•	Mode Management
•	Control Actions (Freeze / Retract / Emergency Stop)
•	Snapshot 기반 저지연 설계
•	스케줄 자원 최적화 연동
을 정의한다.
CIC는 단순 대시보드가 아니라 지휘 통제 계층이다.
________________________________________
2. Absolute Architectural Rule
2.1 DB-Only Read Principle (불변 규칙)
1.	Warroom/CIC는 오직 PostgreSQL DB에서만 데이터를 읽는다.
2.	외부기관 API를 직접 호출하지 않는다.
3.	엔진 메모리 캐시를 직접 읽지 않는다.
4.	DB에 기록되지 않은 데이터는 표시 금지.
위반 시 → 설계 오류.
________________________________________
3. Data Flow Architecture
External Source
    ↓
Ingest Engine
    ↓
ext_event_raw (DB)
    ↓
Processing Engine
    ↓
engine_result (DB)
    ↓
engine_snapshot (DB)
    ↓
CIC (Read-Only)
CIC는 반드시 engine_snapshot를 기본 데이터 소스로 사용한다.
________________________________________
4. Required DB Tables
4.1 ext_event_raw
원천 데이터 기록 (모든 외부기관)
Column	Description
id	PK
source_name	FRED/ECOS/DART/KIS/NEWS/LLM
entity_key	Symbol/Series/Doc ID
payload_jsonb	원천 데이터
data_ts_utc	데이터 시각
ingested_ts_utc	수집 시각
refresh_interval_sec	스케줄 기준
fetch_latency_ms	수집 지연
status	OK/ERROR
error_msg	에러
________________________________________
4.2 engine_result
엔진 계산 결과 기록
Column	Description
engine_name	Regime/Risk/Allocation/...
engine_version	vX.X
input_ref	참조 데이터
result_jsonb	계산 결과
computed_ts_utc	계산 시각
compute_latency_ms	계산 지연
refresh_interval_sec	주기
confidence	신뢰도
freshness_status	GREEN/YELLOW/RED
________________________________________
4.3 engine_snapshot
CIC 고속 조회용
Column	Description
snapshot_key	regime_current 등
snapshot_jsonb	최신 값
asof_ts_utc	기준 시각
refresh_interval_sec	갱신 주기
freshness_status	상태
________________________________________
5. Mandatory Data Transparency Contract
모든 CIC 패널은 다음 메타데이터를 반드시 표시해야 한다:
Source:
Timestamp (UTC):
Local Time (KST):
Refresh Interval:
Freshness Status:
Confidence:
Latency (optional):
해당 정보가 없는 값은 표시 금지.
________________________________________
6. Freshness Logic
elapsed_time = now - timestamp
Condition	Status
≤ 1× refresh	GREEN
≤ 2× refresh	YELLOW
> 2× refresh	RED
RED 상태 데이터 2개 이상 → 자동 Freeze New Entries
________________________________________
7. Operating Modes
M0 — Historical Verification
•	Twin DB 기반
•	실거래 금지
M1 — Paper Trade
•	실시간 데이터
•	주문 미전송
M2 — Pilot Live
•	KIS 단일 계좌
•	자본 제한
•	주문 제한
M3 — Full Live
•	완전 자동 실행
Mode 전환은 순차적 상승만 허용 (M0→M1→M2→M3)
하향은 언제든 가능.
________________________________________
8. Control Actions
8.1 Freeze New Entries
•	신규 진입 차단
•	기존 포지션 유지
•	DB 기록 필수 (decision_object)
________________________________________
8.2 Retract
위험 회피 후퇴 모드
즉시 실행:
risk_mode = NEUTRAL
strike_disable = TRUE
equity_budget = predefined_profile
hedge_expand = TRUE
Retract 단계:
Level	Equity Target
R1	30–40%
R2	20–30%
R3	10–20%
________________________________________
8.3 Emergency Stop
최고 단계
옵션 1: Freeze Only
옵션 2: Freeze + Flatten
즉시 실행:
FREEZE_NEW_ENTRIES = TRUE
AUTO_EXECUTION = DISABLED
Flatten 옵션 시:
close_all_positions()
실행 시:
•	사용자 확인 2단계
•	Incident Log 기록
•	decision_object 생성
________________________________________
9. Control API Contract
POST /api/cic/control
{
  "action": "freeze | retract | emergency_stop | mode_change",
  "level": "R1/R2/R3 (if retract)",
  "requested_by": "USER",
  "reason": "manual or alarm",
  "current_mode": "M2"
}
Response:
{
  "status": "EXECUTED",
  "decision_id": "...",
  "timestamp_utc": "...",
  "new_state": {...}
}
________________________________________
10. Scheduler Resource Optimization
10.1 Resource Monitoring Inputs
•	CPU %
•	RAM %
•	DB write latency
•	Network error rate
10.2 Adaptive Scan Multiplier
if CPU > 85%:
    scan_multiplier += 0.5
if DB latency high:
reduce batch size
if repeated API errors:
activate circuit breaker
________________________________________
11. Circuit Breaker Standard
연속 실패 ≥ N회:
•	해당 source 일시 중단
•	상태 DB 기록
•	CIC에 “DEGRADED SOURCE” 표시
________________________________________
12. Latency Minimization Strategy
CIC는:
•	engine_snapshot만 조회
•	heavy JSON 처리 금지
•	join 최소화
•	index 필수
권장:
•	snapshot_key index
•	engine_name index
•	data_ts_utc index
________________________________________
13. Data Integrity Dependency
CIC는 다음 핵심 snapshot이 RED이면:
•	Regime
•	Risk
•	KIS balance
•	Allocation
2개 이상 RED → Auto Freeze
________________________________________
14. Audit Integration
모든 Control Action은:
•	decision_object 기록
•	incident_log 기록(레벨2 이상)
•	user_id 기록
•	timestamp 기록
________________________________________
15. Warroom Layout Specification
Top Status Bar
•	Mode
•	Risk Mode
•	Health Index
•	Crisis Probability
•	Data Integrity
Center
•	SAA Radar
•	Multi-Target View
•	Allocation %
Right Panel (Control)
•	Mode Selector
•	Freeze
•	Retract
•	Emergency Stop
Bottom
•	Decision Log
•	Incident Log
•	LLM Usage Log
________________________________________
16. Fail-Safe Rule
DB 연결 불가 시:
•	Auto Freeze
•	Emergency Stop 권고 표시
•	모드 자동 M1 이하로 강등
________________________________________
17. Security Alignment
•	모든 Control API는 인증 필요
•	Role-based access
•	Emergency Stop은 2단계 인증 가능
________________________________________
18. Verification Requirements
TVP 추가 항목:
•	DB-only read test
•	snapshot latency < 200ms
•	freeze action propagation test
•	retract profile enforcement test
•	emergency flatten simulation test
________________________________________
Final Definition
Warroom (CIC)는:
•	DB 기반
•	투명성 기반
•	통제 기반
•	자원 최적화 기반
•	Private but Institutional-grade
지휘통제실이다.
________________________________________