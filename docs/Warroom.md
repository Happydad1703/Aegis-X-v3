# Warroom (CIC) Data Transparency Rule v1.0
🔒 기본 원칙
CIC/Dashboard에 표시되는 모든 데이터는 반드시 다음 4요소를 포함해야 한다.
실명제(Real Identity Source)
Timestamp (UTC + Local)
Refresh Rate
Data Freshness Indicator
이 4개가 없는 데이터는 “운영 화면에 표시 금지”.

1️⃣ 실명제 (Real Identity)
모든 데이터 블록은 반드시 출처를 실명으로 표기해야 함.
예시
LLM의 경우:
Source: OpenAI GPT-4.1 (REGIME_PROMPT_v2.3)
Source: Gemini 1.5 (Fallback Mode)
“LLM”이라는 모호한 표현 금지. 반드시 모델명 명시.

2️⃣ Timestamp 표기 규칙
모든 데이터에는:
Data Timestamp (UTC)
Local Time (KST)
둘 다 명기.
예시 UI 표기
Regime: Tapering
Updated: 2026-03-01 09:35:12 UTC
Local: 2026-03-01 18:35:12 KST

3️⃣ Refresh Rate 명시
각 데이터 블록 우측 상단에 반드시:
Refresh: 5 min
또는
Real-time (KIS stream)
또는
Hourly

4️⃣ Data Freshness Indicator (색상 규칙)
예:
Regime refresh 5분
12분 지났으면 Yellow
16분 지났으면 Red
Red 상태에서는:
해당 데이터에 의존한 전략 진입 금지(Pre-Trade Gate 연동)

5️⃣ CIC UI 적용 구조
모든 패널 공통 Header 구조
[Panel Name]
Source:
Timestamp:
Refresh:
Freshness:
Confidence:

예: Crisis Probability 카드
Crisis Probability: 0.62
Source: Hybrid Model v3.4
Data Time (UTC): 2026-03-01 09:30:00
Refresh: 5 min
Freshness: GREEN
Confidence: 0.74

6️⃣ 실명제 범위 확대
실명제는 사람 이름이 아니라 “책임 엔진/모델 식별”을 의미.
아래도 실명제 대상:
Risk Mode 결정
Allocation 변경
Retract 실행
Emergency Stop 실행
Mode 변경
Strategy Promotion
예:
Decision: Retract-2 Activated
Triggered By: Self-Healing Structural Alarm
Executed By: User (Manual)
Timestamp: ...

7️⃣ 실명제 + Timestamp는 법적·감사 방어선
이 구조는 다음을 방지:
“언제 계산된 값인지 모르는 숫자”
“이전 장 데이터로 현재 판단”
“LLM hallucination이 언제 반영되었는지 모름”
“누가 Stop을 눌렀는지 불명확”
Private System이라도 책임 체계는 기관급으로 유지.

8️⃣ API 설계 반영 (중요)
CIC용 API는 단순 값 반환 금지.
모든 응답은 다음 구조로 반환:
{
  "value": 0.62,
  "source": "Hybrid Model v3.4",
  "timestamp_utc": "2026-03-01T09:30:00Z",
  "refresh_interval_sec": 300,
  "freshness_status": "GREEN",
  "confidence": 0.74
} Warroom 전체 Data Governance 규칙
금지사항
timestamp 없는 데이터 표시 금지
source 없는 수치 표시 금지
refresh interval 없는 데이터 표시 금지
stale 상태인데도 진입 허용 금지

🔟 Emergency Stop과의 연동
Data Freshness가 RED인 핵심 모듈:
Regime
KIS Balance
Risk Engine
Macro Context
중 2개 이상이면:
Auto Freeze New Entries
CIC에 “DATA STALE WARNING” 표시

결론
이 원칙을 적용하면 Warroom은:
단순 Dashboard가 아니라
투명한 전투지휘통제실(Command & Control Center)
이 됩니다.
DB 기록 규칙 + DB-only UI 원칙 + 스케줄/리프레시 자원 최적화 설계

0) 핵심 원칙(요청사항을 규정으로 고정)
R0. DB-First / DB-Only
외부기관으로부터 획득한 원천 데이터(Raw)와 엔진 처리 결과(Result)는 반드시 DB에 기록
모든 프로세스/알고리즘의 입력 데이터는 DB에서만 조회
처리 결과도 DB에 기록
Warroom/CIC/Control Panel은 DB에서만 읽어 렌더링(엔진 메모리나 외부 API 직접 참조 금지)
→ 결론: “DB가 SSOT(단일 진실 공급원)”이며, UI는 DB 읽기 전용 Consumer.

1) DB 기록/조회 아키텍처(권장)
1.1 파이프라인 표준 흐름(강제)
External Source → Ingest → DB(raw_event) → Process Engine reads DB → DB(result_event) → CIC reads DB
1.2 “직접 호출 금지” 규칙
UI가 외부 API를 직접 호출: 금지
UI가 엔진 메모리(캐시)를 직접 조회: 금지
엔진이 외부 API 결과를 DB에 쓰지 않고 바로 처리: 금지
엔진이 DB 없이 파일/메모리만 입력으로 사용: 금지(예외는 시스템 부팅/비상 fallback만)

2) DB 스키마 원칙(최소 필수 테이블)
이미 PostgreSQL을 Docker로 고정했으므로, PostgreSQL을 이벤트 스토어 + 최신 스냅샷 저장소로 씁니다.
2.1 원천 이벤트 (Raw)
ext_event_raw
id
source_name (FRED/ECOS/DART/NAVER/…/KIS)
entity_key (예: DGS10, 722Y001, 공시번호, 뉴스 URL hash, symbol)
payload_jsonb (원문/원문요약/메타 포함)
data_ts_utc (원천 데이터 시각)
ingested_ts_utc (수집 시각)
refresh_interval_sec (스케줄 기준)
fetch_latency_ms
status (OK/EMPTY/ERROR)
error_code, error_msg
2.2 처리 결과 (Result)
engine_result
id
engine_name (Regime/Allocation/Risk/Fleet/Twin/Meta/SelfHeal)
engine_version
input_ref (입력으로 사용한 raw_event/result_event의 reference)
result_jsonb
computed_ts_utc
refresh_interval_sec
compute_latency_ms
confidence
freshness_status (GREEN/YELLOW/RED)
2.3 최신 스냅샷(빠른 UI용)
engine_snapshot
snapshot_key (예: regime_current, allocation_current, risk_current, cic_multi_target_view)
snapshot_jsonb
asof_ts_utc
refresh_interval_sec
freshness_status
중요: UI Latency 최소화는 “event table을 매번 스캔”하지 않고, snapshot 테이블/뷰를 읽게 해서 해결합니다.

3) Warroom/CIC는 DB만 읽고, Latency는 “DB Snapshot”으로 줄인다
사용자 요구가 “DB로부터만”인데도 느려지지 않게 하려면:
엔진은 결과를 engine_result에 저장(감사용)
동시에 최신값은 engine_snapshot에 upsert(빠른 조회용)
CIC는 engine_snapshot만 조회(평상시)
필요 시 “드릴다운” 버튼으로 engine_result / ext_event_raw를 열람(감사/근거)
3.1 CIC 데이터 계약(필수 메타)
모든 snapshot/result는 반드시:
Source(실명제)
Timestamp(UTC+KST)
Refresh interval
Freshness
Compute latency / Fetch latency
를 포함해야 함(이전 요구사항과 완전 합치)

4) 스케줄/리프레시: “죽지 않는 시스템” 설계
요구하신 핵심: PC 자원(CPU/GPU, RAM, 네트워크, 포트)을 참조해서 가장 합리적으로.
4.1 스케줄러가 해야 하는 일(정의)
스케줄러는 단순 타이머가 아니라 “자원 오케스트레이터”입니다.
각 태스크의 기본 주기(Refresh Rate)
우선순위(Tier: critical / normal / low)
동시 실행 제한(Concurrency)
자원 기반 스로틀링(CPU/RAM/네트워크)
장애 시 백오프/격리(Self-Healing lite)
4.2 Refresh Tier 개념(권장)
critical_only: 살아남기(위험감지, KIS sync, 핵심 리스크)만
normal: 기본 운영
low_resource: PC 자원 부족 시 자동 다운시프트
(이미 refresh_schedule.yaml 개념이 있으니, 이를 “운영 통제 정책”으로 승격)
4.3 자원 피드백 루프(핵심)
스케줄러는 매 실행 사이클마다:
CPU 사용률
RAM 사용률
네트워크 오류율/응답 지연
DB latency
를 읽고, scan_multiplier를 자동 조정합니다.
예시 정책(권장):
CPU > 85% 3분 지속 → scan_multiplier +0.5
RAM > 85% → heavy tasks(LLM batch, SEC) 일시 중단
네트워크 에러율 > 10% → 외부 뉴스 수집 백오프
DB write latency > 임계치 → event batch size 감소
4.4 “죽지 않는” 실패 처리(강제)
모든 ingest/engine task는:
타임아웃
재시도(제한)
서킷브레이커(연속 실패 시 일정 시간 중지)
실패 로그 DB 기록
을 의무화합니다.

5) 이 요구사항을 SE 문서에 반영(업데이트 포인트)
이 원칙은 단순 구현 선택이 아니라 아키텍처 불변 규칙이므로 아래 문서에 반영되어야 합니다.
02_SAD: DB-First / DB-Only 아키텍처, snapshot 전략
04_DDD: ext_event_raw / engine_result / engine_snapshot 구조(SSOT)
11_GOV: 모든 처리 입력/출력이 DB에 기록되는 감사 체계
14_TVP: “DB 기록 누락 시 FAIL” 테스트 케이스 추가
16_CM: 스케줄/리프레시 정책 파일을 형상관리 항목으로 고정
(신규 권장) 18_CIC_Warroom_Spec.md: CIC는 snapshot only 읽기 원칙 + 드릴다운 근거

6) 다음 구현 단계(책임개발자 제안: 가장 먼저 할 것)
당장 가장 큰 레버리지는 2가지입니다.
A) DB Event/Snapshot 계약 확정
ext_event_raw, engine_result, engine_snapshot 최소 스키마 확정
CIC는 snapshot만 읽는 규칙 확정
B) 스케줄러에 “자원 피드백” 붙이기
scan_multiplier 자동 조정
circuit breaker & backoff 표준화
실패/지연을 DB에 기록해서 CIC에 표시(실명제+timestamp+refresh 포함)
📘18_CIC_Warroom_Spec.md
Document ID: AEGIS-X-CIC-v1.0
Owner: Strategic Command / Control Engineering
Classification: Warroom Command & Control Specification

1. Purpose
본 문서는 Aegis-X Warroom (CIC: Command & Control Center)의:
DB-First UI 원칙
Data Transparency 규칙
Mode Management
Control Actions (Freeze / Retract / Emergency Stop)
Snapshot 기반 저지연 설계
스케줄 자원 최적화 연동
을 정의한다.
CIC는 단순 대시보드가 아니라 지휘 통제 계층이다.

2. Absolute Architectural Rule
2.1 DB-Only Read Principle (불변 규칙)
Warroom/CIC는 오직 PostgreSQL DB에서만 데이터를 읽는다.
외부기관 API를 직접 호출하지 않는다.
엔진 메모리 캐시를 직접 읽지 않는다.
DB에 기록되지 않은 데이터는 표시 금지.
위반 시 → 설계 오류.

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

4. Required DB Tables
4.1 ext_event_raw
원천 데이터 기록 (모든 외부기관)

4.2 engine_result
엔진 계산 결과 기록

4.3 engine_snapshot
CIC 고속 조회용

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

6. Freshness Logic
elapsed_time = now - timestamp
RED 상태 데이터 2개 이상 → 자동 Freeze New Entries

7. Operating Modes
M0 — Historical Verification
Twin DB 기반
실거래 금지
M1 — Paper Trade
실시간 데이터
주문 미전송
M2 — Pilot Live
KIS 단일 계좌
자본 제한
주문 제한
M3 — Full Live
완전 자동 실행
Mode 전환은 순차적 상승만 허용 (M0→M1→M2→M3)
하향은 언제든 가능.

8. Control Actions
8.1 Freeze New Entries
신규 진입 차단
기존 포지션 유지
DB 기록 필수 (decision_object)

8.2 Retract
위험 회피 후퇴 모드
즉시 실행:
risk_mode = NEUTRAL
strike_disable = TRUE
equity_budget = predefined_profile
hedge_expand = TRUE
Retract 단계:

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
사용자 확인 2단계
Incident Log 기록
decision_object 생성

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

10. Scheduler Resource Optimization
10.1 Resource Monitoring Inputs
CPU %
RAM %
DB write latency
Network error rate
10.2 Adaptive Scan Multiplier
if CPU > 85%:
    scan_multiplier += 0.5
if DB latency high:
reduce batch size
if repeated API errors:
activate circuit breaker

11. Circuit Breaker Standard
연속 실패 ≥ N회:
해당 source 일시 중단
상태 DB 기록
CIC에 “DEGRADED SOURCE” 표시

12. Latency Minimization Strategy
CIC는:
engine_snapshot만 조회
heavy JSON 처리 금지
join 최소화
index 필수
권장:
snapshot_key index
engine_name index
data_ts_utc index

13. Data Integrity Dependency
CIC는 다음 핵심 snapshot이 RED이면:
Regime
Risk
KIS balance
Allocation
2개 이상 RED → Auto Freeze

14. Audit Integration
모든 Control Action은:
decision_object 기록
incident_log 기록(레벨2 이상)
user_id 기록
timestamp 기록

15. Warroom Layout Specification
Top Status Bar
Mode
Risk Mode
Health Index
Crisis Probability
Data Integrity
Center
SAA Radar
Multi-Target View
Allocation %
Right Panel (Control)
Mode Selector
Freeze
Retract
Emergency Stop
Bottom
Decision Log
Incident Log
LLM Usage Log

16. Fail-Safe Rule
DB 연결 불가 시:
Auto Freeze
Emergency Stop 권고 표시
모드 자동 M1 이하로 강등

17. Security Alignment
모든 Control API는 인증 필요
Role-based access
Emergency Stop은 2단계 인증 가능

18. Verification Requirements
TVP 추가 항목:
DB-only read test
snapshot latency < 200ms
freeze action propagation test
retract profile enforcement test
emergency flatten simulation test

Final Definition
Warroom (CIC)는:
DB 기반
투명성 기반
통제 기반
자원 최적화 기반
Private but Institutional-grade
지휘통제실이다.

다음 단계로:
CIC DB 스키마 SQL 초안 작성
Control API FastAPI 코드 스켈레톤 작성
Snapshot 갱신 엔진 설계
스케줄러 자원 피드백 로직 구체화
어느 것부터 구현 단계로 들어가시겠습니까?
Warroom CIC나 Dashboard & Control Panel은 사업적으로 최신의 트렌드를 반영한 charming한 상업용 Web based 프로그램으로 Background에서는 API 엔진이 가동되고, Forground에서는 Dashboard and Control panel 형태로 운영되어야 합니다. 필요시 전체화면모드오 Web page형태를 선태가능하게 하고"상단(Header), 좌측//메뉴, 하단(Footer)는 중요한 정보(뉴스/공시/주요한 상황전파)등이 아래에서 위로 흘러가도록 함. 상단의 header Block의 하단부위에는 외부뉴스원/공시/자료 회사와의 통신상태와 그를 바탕으로 산출된 시스템의 건강상태, 산정된 Regime (Goldilock/stead/tapering/crisic), Operation Mode Selection Button Operation Mode(Backtest, Paper Trade, Pilot trade, Full Live), LLM status, API Engine Status/Condtion
좋습니다. 지금 요구사항을 상업용(Commercial-grade) Web Warroom CIC로 해석해서, “최신 트렌드 + charming UI + 실시간 통제 + DB-only 원칙 + 오조작 방지”를 동시에 만족하는 화면/정보구조(IA) + 레이아웃 + 컴포넌트 스펙을 아래처럼 제안합니다.
(이 내용은 그대로 19_CIC_Web_UI_UX_Spec.md로 옮겨도 되는 수준으로 작성했습니다.)

1) 제품 형태 정의
1.1 운영 형태
Foreground: Web-based Dashboard & Control Panel (Warroom CIC)
Background: API Engine(ingest/process/scheduler) + DB snapshots
데이터 원칙: 화면은 DB snapshot만 읽는다 (직접 외부 API 호출 금지)
1.2 표시 모드
Normal Web App 모드 (헤더/좌측 메뉴/푸터 포함)
Full Screen Warroom 모드 (F11급 몰입형, 불필요 UI 최소화)
Web Page 형태(읽기 전용 뷰): 공유/보고용 (Control 기능 숨김 가능)

2) 전체 레이아웃(요청사항을 그대로 반영)
Layout Grid (권장)
Top Header (고정)
Left Sidebar Menu (고정, 접기/펼치기)
Main Canvas (스크롤, 카드/차트 중심)
Bottom Footer Ticker (고정, 아래→위 흐름)
요청하신 “상단(Header), 좌측 메뉴, 하단(Footer)”는 고정.
Footer는 하단에서 위로 흘러가는 상황전파(뉴스/공시/알림) 전용.

3) Header Block – “지휘 통제 상태바” 설계 (최상단 핵심)
Header는 “3초 판단”이 목적입니다.
아래 요소를 왼쪽→오른쪽 순으로 배치 권장.
3.1 Connection & Engine Health Strip (Header 하단부)
요청하신 항목을 Badge/Chip로 배치합니다.
External Sources Comm Status (DB snapshot 기반)
FRED / ECOS / DART / NEWS / KIS / Yahoo(시세)
각 소스: OK / DEGRADED / FAIL + asof_ts + latency
System Health (Health Index 0~1 + 색상)
Regime: Goldilocks / Sideways / Tapering / Crisis (색상)
Operation Mode Selector: Backtest / Paper / Pilot / Full Live
LLM Status
Provider(실명) + 모델 + fallback 여부 + last call + latency
API Engine Status
Scheduler Running 여부
Queue depth
Last cycle duration
DB write latency
Header 표시 규칙(필수)
각 Badge는 반드시:
Source(실명)
Timestamp(UTC+KST)
Refresh Interval
Freshness(G/Y/R)
를 hover tooltip로 노출 (항상 명기 원칙 유지)

4) Left Sidebar – 메뉴 구조(Information Architecture)
4.1 메뉴 섹션(권장 IA)
Command Overview
Warroom Home
System Health
Comms / Data Integrity
Market & Regime
Regime Dashboard
Macro Context
News Sentiment
Capital & Allocation
SAA Radar
Market Allocation
Exposure / Variance by Symbol
Fleets
Multi-Target View (core/tactical/strike)
Fleet Strategy Summary
ROE / Engagement Monitor
AAR / Performance
Control
Mode Control
Freeze / Retract / Emergency Stop
Pilot Caps
Audit
Decision Log
Incident Log
LLM Usage Log
Settings
Refresh Tier (normal / low_resource / critical_only)
Notification rules
4.2 Sidebar UX
접기/펼치기
“Full Screen” 시 자동 접기 가능
알림 뱃지(Incident/Fail) 표시

5) Footer – “상황전파 스트림” (아래에서 위로 흐름)
요청하신 “아래→위로 흘러가도록”을 그대로 구현합니다.
5.1 Footer Ticker 3-Track(권장)
Track A: Breaking News (뉴스)
Track B: Disclosures (공시)
Track C: System Alerts (Incident / Health / Data Integrity)
각 항목은:
headline
source_name
timestamp
impact_tag(시장영향 추정)
click → 상세 팝업(근거 raw_event drilldown)
이 Footer는 “정보 흘려보내기”가 아니라
클릭 시 DB에 저장된 원문 근거를 즉시 보여주는 게 핵심입니다.

6) Main Canvas – Dashboard & Control Panel 구성
6.1 Home (Warroom Overview) 구성(권장)
(A) SAA Radar (Market/Asset allocation)
(B) Multi-Target View (군별 타겟 종목 카드)
(C) Current Allocation % (variance_by_symbol 상위 12)
(D) Risk & Self-Healing Panel
Risk Mode
DD / Vol spike
Alarm Level
(E) Execution Panel
Orders / Fills / Failures
Slippage, Reject reason
6.2 Control Panel은 “오른쪽 도킹 패널” 권장
사용자가 어디 페이지에 있어도 Control은 항상 접근 가능
단, 위험 조작은 Arm → Execute 2단계

7) Control UX – Emergency Stop / Retract / Freeze / Mode
7.1 공통 안전장치(필수)
Arm 토글(Control 활성화)
Press & Hold 2~3초
실행 시 Reason 필수 입력 (짧은 문구)
실행 결과는 즉시 화면에 “결정 로그”로 표시 (Decision Object)
7.2 Mode Selection Button
Backtest / Paper / Pilot / Full Live
상향 전환은 조건 충족 시만 Enabled:
Data Integrity OK
KIS OK (Pilot/Full)
Risk Engine OK
Snapshot Freshness GREEN 비율 기준
7.3 Retract Button (고위험 예상)
R1/R2/R3 선택 UI 제공
선택 시 “전환 후 목표 Exposure”를 즉시 보여주고 실행
7.4 Emergency Stop
Freeze only / Flatten 옵션
Flatten은 최종 확인(문구 입력) + hold

8) “최신 트렌드 + charming” UI 스타일 가이드(권장)
카드 기반 레이아웃 + soft shadow + 2xl rounded
상태(OK/DEGRADED/FAIL)는 배지/칩 + 아이콘
차트는 단순/명확 (과도한 3D 금지)
다크모드 기본 제공(워룸에 적합)
애니메이션은 “정보성”만 (업데이트/경보 강조)

9) 실시간성/Latency 최소화: DB Snapshot + Push 업데이트
DB-only 원칙을 유지하면서도 빠르게 하려면:
9.1 “Snapshot 기반 조회”
UI는 engine_snapshot만 읽는다(기본)
상세 근거는 drilldown으로 engine_result/ext_event_raw를 조회
9.2 업데이트 방식(권장)
SSE(Web Push) 또는 WebSocket으로 “snapshot_key 변경 이벤트”만 push
실제 데이터는 push로 보내지 않고, UI가 해당 snapshot_key를 재조회
이렇게 하면:
UI는 DB-only 원칙 유지
트래픽 최소화
Latency 최소화(변경된 것만 재조회)

10) 구현에 필요한 API(최소 세트)
UI는 전부 DB snapshot을 읽되, API는 “DB를 읽어주는 게이트” 역할만 합니다.
GET /api/cic/snapshot?keys=...
GET /api/cic/health
GET /api/cic/footer-stream (뉴스/공시/알림)
POST /api/cic/control (freeze/retract/stop/mode_change)
모든 응답은 반드시:
source, timestamp, refresh, freshness, latency 메타 포함

11) 다음 단계(제가 바로 이어서 만들 수 있는 것)
원하시면 다음 중 하나를 즉시 작성/제공하겠습니다(질문 없이 진행 가능):
19_CIC_Web_UI_UX_Spec.md 정식 SE 문서 버전(방금 내용을 문서화)
Wireframe 수준 화면 설계(페이지별 컴포넌트 트리/배치)
API Contract 상세(요청/응답 JSON + snapshot_key 목록)
Control Safety State Machine(Arm/Execute/Log/Incident)
원하시는 출력 형태가 “문서(19번)”이면, 다음 답변에서 바로 정식 문서로 작성해 드리겠습니다.
나머지 중앙에 좌측의 메뉴트리에서 최종 선택된 목적/기능/명령 수행결과를 보여 주거나, Monitoring 공간으로 사용하며 가능하면 한 화면에 밀도있게 데이터를 배치하고 한화면을 벋어 나는 데이터이거나 흘러가는 데이터인 경에도 Head/Footer/Left Menu Bar는 고정되어 있어야 합니다.
알겠습니다. 요청하신 내용은 **Warroom CIC의 “고정 프레임 + 고밀도 메인 캔버스”**라는 UI 시스템 규칙으로 확정하면 됩니다. 아래는 레이아웃 불변 규칙 + 메인 캔버스 설계 규격 + 데이터가 넘치거나 흐르는 경우 처리 규칙을 “구현 가능한 수준”으로 정리한 것입니다. (이 내용은 바로 19번 UI/UX 스펙 문서의 핵심 챕터가 됩니다.)

1) Layout 불변 규칙: “Fixed Frame, Dense Canvas”
R1. 고정 프레임(항상 고정)
Header: 고정(sticky)
Left Menu: 고정(sticky)
Footer Ticker: 고정(sticky)
고정 프레임은 Main Canvas 스크롤과 독립되어야 한다.
즉, 메인 콘텐츠가 아무리 길어도 Header/Footer/Left는 절대 스크롤로 사라지지 않음.
R2. 스크롤은 Main Canvas만
페이지 내 스크롤은 오직 중앙 Main Canvas 영역에서만 발생
Footer의 “흐름(아래→위)”은 자체 애니메이션/가상리스트로 처리(페이지 스크롤과 분리)

2) 중앙 Main Canvas 역할 정의
중앙 Main Canvas는 좌측 메뉴에서 선택한 “최종 목적”을 수행하는 공간이며, 2가지 모드를 가진다.
2.1 Result View (명령 수행 결과 뷰)
사용자가 특정 기능/명령(예: Retract 실행, Mode 변경, Pilot cap 적용, Twin 실행)을 수행하면
그 결과를 즉시, 밀도 높게, 요약→상세 순으로 표시
2.2 Monitoring View (모니터링 뷰)
운용 중 핵심 KPI/상태/리스크/실행/타겟/전략/근거를
한 화면에서 “상황판” 형태로 고밀도 표시

3) “한 화면 고밀도” 데이터 배치 규칙 (정보 압축 규격)
3.1 기본 레이아웃: 12-column Grid + 카드
Main Canvas는 12컬럼 그리드 기반
카드 단위로 배치하되, 카드 내부는 표/스파크라인/칩 중심(텍스트 최소화)
권장 기본:
상단 1행: 4~6개 KPI 카드(각 2~3컬럼)
중단: 큰 패널 2개(각 6컬럼) 또는 8+4 분할
하단: 로그/리스트 1개(12컬럼)
3.2 요약 → 드릴다운(Drilldown) 구조
기본 화면은 요약 지표 + Top N
상세는:
카드 클릭 → 오른쪽 Drawer(패널) 또는 Modal
혹은 “Detail” 탭으로 전환
이렇게 해야 한 화면 밀도를 올리면서도 가독성 유지
3.3 “Top N 규칙”으로 화면 폭발 방지
Multi-Target: Fleet별 Top 8 (기본)
Current Allocation: Top 12 (기본)
Orders/Fills: 최근 20건 (기본)
News/Disclosures: 최근 30건(기본)
더 보고 싶으면 “More”로 드릴다운.

4) 화면을 벗어나는 데이터 처리 규칙
요청하신 “한 화면을 벗어나는 데이터”는 아래 3가지로 분류하고, 처리법을 고정합니다.
4.1 Overflow Data (너무 많은 데이터)
해결책: 가상 스크롤(virtual list) + 페이지네이션
메인 Canvas만 스크롤, 프레임 고정 유지
4.2 Streaming Data (흘러가는 데이터)
Footer Ticker: 아래→위 흐름(요청사항)
Main Canvas 내부에서도 실시간 스트림이 필요하면:
“Pinned Latest” (상단 1~3개 고정)
아래는 가상리스트로 자연 스크롤
자동 스크롤은 기본 OFF(사용자 읽기 방해 방지)
“Follow Live” 토글로 ON 가능
4.3 Wide Data (가로로 긴 데이터: 테이블/행동 로그)
해결책: 카드 내부에서 가로 스크롤 허용(단, 카드 높이는 제한)
또는 Column 숨김/표시 토글 제공
“Export CSV” 버튼은 Drilldown에서 제공

5) Sticky 유지 구현 규칙(기술적 UI 규약)
5.1 고정 영역 높이 규정
Header: 72px(예시) + 하단 Health Strip 36px
Footer: 56px(예시)
Left Menu: 가변(전체 높이), 접기 가능
5.2 Main Canvas 뷰포트 계산
Main Canvas height = 100vh - header - footer
Main Canvas만 overflow-y: auto
Left Menu는 overflow-y: auto 가능(메뉴가 길 때) but “고정” 유지

6) Monitoring View의 “표준 한 화면 구성”(추천 템플릿)
좌측 메뉴에서 “Warroom Home” 선택 시 중앙은 다음 1-screen 밀도 템플릿을 사용:
Row 1 (상단 KPI, 1줄)
System Health / Crisis Prob / Regime / Mode / KIS Sync / Data Integrity
Row 2 (전투 핵심 2패널)
SAA Radar (좌 7~8컬럼)
Risk & Alarms (우 4~5컬럼)
Row 3 (종목/타겟/실행)
Multi-Target View (좌 6)
Current Allocation Top 12 (우 6)
Row 4 (로그/근거)
Decision Log + Incident Log 탭(12)
이 구조면 “한 화면에 밀도 있게”가 가능하면서, 스크롤은 필요 최소로 줄어듭니다.

7) Result View의 표준 구성(명령 수행 결과)
예: Retract 실행 후 중앙 캔버스는 다음 순서로 결과를 보여줍니다.
Result Banner (성공/실패, 결정ID, 실행자, 시간)
Before vs After (Exposure/Mode/Disable flags)
Affected Fleets (Strike disable 여부, Tactical scale)
Orders Generated (있으면)
Audit Links (Decision Object / Incident / Snapshot key)
이때도 Header/Footer/Left는 고정.

8) DB-only + 메타데이터 표시 원칙과의 결합
중앙 캔버스의 모든 카드/테이블도 동일 규칙 적용:
Source(실명)
Timestamp(UTC+KST)
Refresh Rate
Freshness
(선택) Latency/Confidence
표시는:
카드 오른쪽 상단에 축약(예: asof 09:31Z · 5m · GREEN)
Hover 시 상세 툴팁

9) 다음 산출물(바로 제공 가능)
이제 요구사항이 충분히 구체화됐습니다. 제가 다음 중 하나를 즉시 만들어 드릴 수 있습니다.
19_CIC_Web_UI_UX_Spec.md 정식 문서(레이아웃/컴포넌트/상호작용 규칙 포함)
Warroom Home / Control / Audit 화면별 컴포넌트 트리(React 기준)
“Sticky Frame” 레이아웃을 구현하는 CSS/레이아웃 코드 스켈레톤(Tailwind 기준)

이제까지 합의된 DB-First / DB-Only / Single KIS / Win11 Env Key / Docker PostgreSQL / Snapshot 기반 저지연 / 실명제+Timestamp+Refresh Meta / Sticky Frame UI / Emergency & Retract 통제 / 자원 적응형 스케줄링을 모두 반영한