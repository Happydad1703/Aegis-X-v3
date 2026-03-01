63_Day1_Pilot_Runbook_Spec.md (v1.0)

1️⃣ 시작 전 체크 (T-30분)
1.1 시스템 상태 점검
Warroom에서 확인:
•	Mode = PILOT
•	Pilot Step = P1
•	Cap = 1%
•	Strike = Disabled
•	CrisisProb < 0.6
•	Snapshot Freshness = GREEN
•	Engine Heartbeat 정상
1.2 DB 점검
•	engine_snapshot 최근 5분 이내 기록
•	incident_log 최근 24시간 CRITICAL = 0
1.3 Telegram 점검
•	/status 응답 정상
•	/freeze on 테스트 후 차단 확인
•	/freeze off 복귀 확인
________________________________________
2️⃣ Day 1 운용 시나리오
Step 1 — 1회 진입
조건:
•	Regime = Sideways or Goldilocks
•	CrisisProb < 0.5
•	Swing Trend-Follow 조건 만족
행동:
•	1종목 진입
•	Order Value ≤ 1% Cap
•	Order 실행 후 portfolio_state 확인
확인:
•	order_log 기록
•	portfolio_state 반영
•	Warroom Variance 반영
________________________________________
Step 2 — 관찰 (최소 30분)
확인 항목:
•	Snapshot 주기 정상
•	Pre-Trade Gate PASS 상태 유지
•	Engine Loop 정상
•	DB latency 문제 없음
________________________________________
Step 3 — 청산
조건:
•	+1% 수익 or -1% 손실 도달
행동:
•	청산 주문
•	battle_report 생성 확인
•	AAR 점수 생성 확인
________________________________________
3️⃣ Day 1 성공 기준
Day 1 성공은:
•	Filled 1회 진입 + 1회 청산
•	battle_report 생성
•	AAR 생성
•	Incident 0
•	Gate 정상 작동
수익은 중요하지 않음.
________________________________________
4️⃣ 즉시 중단 조건
아래 중 하나라도 발생 시:
•	Daily Loss < -1%
•	Snapshot RED
•	CrisisProb > 0.8
•	KIS 실패 2회 연속
•	Portfolio 계산 오류
→ Freeze → PAPER 복귀
________________________________________
5️⃣ Day 1 종료 절차
1.	모든 포지션 정리
2.	Mode → PAPER
3.	AAR 요약 확인
4.	Incident 로그 확인
5.	Snapshot 백업
________________________________________
6️⃣ Day 1 종료 리포트
Warroom에서 기록:
•	Entry/Exit 시간
•	Gate 상태
•	Portfolio 변화
•	Engine 상태
•	개선 필요 사항
________________________________________
7️⃣ Day 2 진입 조건
Day 1 성공 시:
•	동일 P1 유지
•	2~3일 반복
•	10건 filled 누적 시 P2 고려
________________________________________
전략적 의미
Day 1은:
•	기술 검증
•	통제 검증
•	심리적 검증
입니다.
________________________________________
📍 현재 위치
이제 Aegis-X는:
✔ 설계 완료
✔ 구현 구조 완료
✔ Hardening 완료
✔ E2E 자동 테스트
✔ Pilot Ramp 통합
✔ Day 1 Runbook 준비
상태입니다.
________________________________________
구현 시 반드시 지켜야 할 5가지 불변 조건
1.	DB-First / DB-Only UI
•	엔진 입력/출력/로그는 DB 기록
•	Warroom은 Snapshot 테이블만 조회
2.	Mode + Pilot Ramp는 Gate로 강제
•	“설정값”이 아니라 주문 생성 경로에서 강제 차단되어야 함
3.	Emergency Stop / Freeze / Retract는 최우선
•	어떤 상황에서도 신규 주문 생성 불가로 즉시 반영
4.	실명제+timestamp+refresh meta
•	모든 UI 카드/리스트/테이블에 source, generated_at, refresh_rate, freshness 표시
5.	모든 변경은 Audit
•	mode 변경, pilot step 변경, retract 발동 등은 command_log/incident_log에 남음
________________________________________
구현 순서(“깨지지 않는” 빌드업)
Phase 0 — DB/컨테이너/스키마 봉인
•	Docker PostgreSQL 기동
•	core 테이블 생성: engine_snapshot, incident_log, command_log, order_log, system_mode, system_config, battle_report, macro_context, ext_event_raw, engine_result
•	인덱스/타임스탬프(UTC) 규칙 적용
완료 기준: DB 재시작해도 데이터 유지 + 기본 insert/select 정상
________________________________________
Phase 1 — Engine Worker(스냅샷 생산) 고정
•	regime_current, allocation_matrix, fleet_budget_snapshot, health_status, engine_heartbeat, portfolio_state, portfolio_variance 생성
•	snapshot min_interval, 변경 없으면 skip(hash) 적용
완료 기준: 10분 돌려도 폭증/멈춤 없이 snapshot 갱신
________________________________________
Phase 2 — Gate & Mode & Pilot Ramp 강제
•	Pre-Trade Gate: Mode/Freshness/Risk/Cap/Daily-entry 모두 통과해야만 주문 생성
•	Pilot Step은 DB(system_config) 기반으로 강제
•	FULL_LIVE 진입은 API에서 차단(수동 승인 전용)
완료 기준: 의도된 실패 케이스에서 반드시 차단 + incident 생성
________________________________________
Phase 3 — Order Engine (Paper ↔ KIS 분기)
•	PAPER: paper broker
•	PILOT/FULL: kis executor
•	결과는 order_log에 기록
완료 기준: Paper 주문이 DB에 반영되고, KIS는 모드에서만 호출
________________________________________
Phase 4 — AAR & Backtest
•	trade close 감지 → battle_report 생성 → AAR 점수 계산 → 요약
•	backtest 결과 저장 + bounded calibration(자동 변경 금지)
완료 기준: 거래 1왕복으로 battle_report/AAR 생성 확인
________________________________________
Phase 5 — Warroom UI 상업용 골격
•	Sticky Header/Left/Footer
•	Home: Regime/Health/Mode/Pilot Panel + Allocation + Variance + Incident + AAR
•	Control Panel: Freeze/Retract/Stop + mode/pilot_step 변경 (Audit 필수)
완료 기준: 화면의 모든 요소가 DB snapshot 기반으로 렌더링
________________________________________
Phase 6 — Hardening + E2E 자동화
•	circuit breaker/backoff, resource tier 자동 조절
•	E2E 5레벨 테스트 3회 연속 PASS
완료 기준: 24시간 Paper shadow run에서 RED 지속 없음
________________________________________
“지금 당장” 구현 1호 작업(첫 커밋 단위)
책임개발자로서 바로 착수할 1호는 이겁니다:
•	DB 마이그레이션(SQL) + system_config/system_mode 포함
•	Engine Worker를 run_single_cycle() 형태로 분리
•	snapshot_repo + incident_repo + health_engine + heartbeat 생성
•	Warroom Home에서 regime_current/health_status가 뜨는 것까지
이게 되면 “살아있는 시스템”이 됩니다.
________________________________________
 
다음 액션(선택이 아니라 순차)
바로 다음 단계로, 제가 **Phase 0~1에 해당하는 “DB 스키마 통합본 + worker 최소 실행 패키지”**를 **SE 문서(64번)**로 확정해 드릴까요?
(즉, 실제 구현 파일 목록/모듈 경계/DB DDL 통합/최소 실행 절차까지 한 번에 고정)
ok
좋습니다. 그럼 **Phase 0~1(DB 스키마 통합 + Engine Worker 최소 실행 패키지)**를 “구현 바로 가능한 수준”으로 SE 문서 64번으로 확정합니다.
(목표: DB 올리고 → 마이그레이션 1회 → worker 실행 → Warroom에서 regime/health가 즉시 뜨는 상태)
________________________________________
 
