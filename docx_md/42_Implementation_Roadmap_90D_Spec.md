42_Implementation_Roadmap_90D_Spec.md (v1.0)
0) 90일 운영 원칙
•	DB-First / DB-Only UI: Warroom은 Snapshot만 읽는다.
•	Docker PostgreSQL 단일 SSOT: 모든 입력/출력/로그/결정은 DB에 기록.
•	Single KIS Account: 실거래/파일럿 모두 동일 계좌, 단 모드로 제한.
•	Fail-safe 우선: 공격적 운용은 허용하되, Kill Switch는 보수적으로.
•	Telegram 먼저: 모바일/메신저는 Telegram 알림+제한 명령부터.
________________________________________
1) 90일 목표 상태(Definition of Done)
시스템이 “완성”되었다고 판단할 최소조건
1.	Mode 4단계 (Backtest / Paper / Pilot / Full Live) 작동
2.	Regime → Allocation → Fleet(Budget) → Risk → Order Gate 일관 실행
3.	Emergency / Freeze / Retract가 UI+Telegram에서 발동되고 DB에 감사로그 남음
4.	AAR 자동 생성 + 파라미터 bounded update(±10%)
5.	Warroom에서 실명제+timestamp+refresh meta가 모든 카드/리스트에 표시
6.	24시간 운용에서 Snapshot Freshness RED가 지속적으로 누적되지 않음(자원 적응형 스케줄링)
________________________________________
2) Week-by-Week 실행 계획
Week 1–2: “플랫폼 뼈대 봉인” (DB/스키마/스냅샷)
산출물
•	Docker PostgreSQL compose + 백업/복구 스크립트(Windows 11 PowerShell)
•	CIC/Engine 공용 DB 스키마 v1:
o	ext_event_raw, macro_context, engine_result, engine_snapshot
o	decision_log, incident_log, command_log, llm_usage_log, messenger_log, engine_error_log
•	Snapshot Key 카탈로그(필수 키 목록) + 인덱스 전략
•	“DB-only 계약”을 강제하는 API Read Layer 기본 구현
완료 기준
•	로컬에서 DB 컨테이너 재시작해도 데이터 유지
•	샘플 snapshot 10종 생성/조회 OK
•	모든 테이블 insert가 UTC timestamp, source_name 포함
________________________________________
Week 3–4: “Ingest & State Ledger SSOT” (수집과 계좌 상태)
산출물
•	외부자료 ingest 파이프라인(최소 가동 세트)
o	뉴스(2종 이상) + DART + FRED/ECOS + 시세(Proxy)
•	KIS 동기화 → state_ledger(파일) + DB 기록 동시 유지(감사/검색용)
•	verify_data_integrity 수준의 DB 기반 검증 리포트(48h window)
완료 기준
•	24시간 동안 최소 1회/소스 데이터 DB 유입 확인
•	KIS 상태(잔고/포지션/주문) 스냅샷이 주기적으로 DB에 기록
•	Freshness(녹/황/적) 계산이 동작
________________________________________
Week 5–6: “Regime Engine v1 + CrisisProb + Alerts”
산출물
•	Regime Engine v1 구현(PS/VS/LM + 제한적 SN)
•	regime_current snapshot 생성
•	CrisisProb 로직 + 안정성 필터(연속 스냅샷 기반)
•	Incident 트리거(RED/DEGRADED) + Telegram 알림(읽기 전용)
완료 기준
•	KOSPI/KOSDAQ/US Proxy 별 Regime snapshot이 주기적으로 생성
•	CrisisProb 급등/데이터 stale/DB latency 상승 시 incident 생성 + Telegram 알림 발송
•	LLM은 “서사 점수(-1~+1)”로만 제한 적용
________________________________________
Week 7–8: “Allocation Matrix v2 + Force Budget Curve + Risk Gate”
산출물
•	Global Battlefield Allocation Matrix v2 구현(정규화 포함)
•	Force Budget Growth Curve(FBGC) + Strike/Swing/Core/Reserve 배분
•	Strike Risk Engine(연속손실/일일 손실/변동성/위기) 강제 적용
•	주문 실행 전 Pre-Trade Gate:
o	Data Freshness Gate
o	Risk Gate(DD/일손실)
o	Mode Gate(Paper/Pilot/Full)
완료 기준
•	Regime 변화에 따라 Allocation이 일관되게 변하고 DB에 기록
•	Strike가 위기 조건에서 자동 0%로 떨어짐(테스트 케이스 통과)
•	Gate 위반 시 주문이 생성되지 않음 + incident 기록
________________________________________
Week 9–10: “Paper Trading End-to-End + Warroom Home”
산출물
•	Paper Trading 모드 구현(주문/체결 mock 또는 paper broker)
•	Warroom Home(Sticky Frame + Dense Canvas) 1페이지 완성
o	Header health strip
o	Battlefield heatmap
o	Fleet snapshot(Core/Swing/Strike/Reserve)
o	Allocation/Variance Top N
o	Decision/Incident 로그 탭
•	SSE/WebSocket: snapshot_key 변경 이벤트 push(데이터는 재조회)
완료 기준
•	Paper 모드에서 “감시→배분→교전(모의)→결과”가 1사이클 이상 자동 수행
•	Warroom 화면 모든 카드에 source/timestamp/refresh 표시
•	1시간 이상 운용 시 UI 멈춤/폭주 없이 갱신
________________________________________
Week 11–12: “Pilot Trade 제한 실행 + 통제(Freeze/Retract/Stop)”
산출물
•	Pilot 모드(실 KIS 주문) + Cap 제한
o	총 노출 상한, 종목당 상한, 일손실 상한
•	Control Panel:
o	Freeze / Retract(R1/R2/R3) / Emergency Stop
o	Arm→Press&Hold→Confirm(Reason) 절차
•	Telegram 제한 명령:
o	/status, /freeze on|off, /retract r1|r2|r3, /confirm code
완료 기준
•	Pilot 모드에서 “1종목, 1회 주문” 제한 테스트 통과
•	Emergency Stop이 즉시 신규진입 차단 + (옵션) Flatten 수행
•	모든 조치가 decision_log/command_log/messenger_log에 감사기록
________________________________________
Week 13: “AAR 자동화 + 학습 루프(제한 업데이트)”
산출물
•	trade → battle_report → AAR Score 계산 파이프라인
•	Fleet/Regime/전략모듈별 성과 집계
•	bounded parameter update(±10%) 적용 + 변경 이력 저장
•	Warroom AAR/Performance 페이지 추가(핵심만)
완료 기준
•	Pilot/Paper 결과로 AAR가 자동 생성되고 요약이 Warroom에 노출
•	파라미터 변경은 bounded rule 준수 + 승인 정책(자동/수동) 적용 가능
________________________________________
3) 운영 안정화 체크리스트(매주 공통)
•	DB write latency, snapshot freshness, engine cycle time
•	KIS sync 성공률
•	incident 발생률(주당)
•	RED 발생 시 자동 조치(Strike 0, Freeze 권고, Retract) 작동 여부
•	CPU/RAM/network 사용량에 따른 refresh tier 자동/수동 전환
________________________________________
4) 승격 기준(Mode Promotion Gate)
Paper → Pilot
•	Data Integrity 7일 연속 OK
•	Gate 위반률 < 1%
•	주문/체결/로그 누락 0건
Pilot → Full Live (추천)
•	Pilot 20~50건 교전 데이터 확보
•	Max DD, Daily Loss cap 준수(위반 0)
•	AAR/성과지표가 최소 기준 충족(예: 손익 양수 + 변동성 조정 성과)
________________________________________
5) 제가 “지금 당장” 착수하는 1순위 작업(다음 커밋 단위)
Day 1 착수 패키지
1.	DB 스키마 v1 (tables + indexes)
2.	snapshot_key 카탈로그 파일
3.	FastAPI read-only snapshot API 골격
4.	Warroom Home에 필요한 최소 snapshot 10종 생성 스텁

