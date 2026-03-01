60_Pilot_Ramp_Plan_1pct_to_20pct.md (v1.0)

(1) 1% 자본으로 극소 Pilot → (2) 5% → (3) 10% → (4) 20% Cap의 단계 승격(4-Step Ramp) 으로 고정합니다.
“빠르게 키우되, 시스템을 먼저 증명”하는 가장 현실적인 경로입니다.

📘60_Pilot_Ramp_Plan_1pct_to_20pct.md (v1.0)
1) 핵심 원칙
•	Pilot은 수익 극대화가 아니라 시스템 검증.
•	승격은 자동이 아니라 Gate 통과 기반(조건 미달이면 유지/후퇴).
•	모든 주문은 Pre-Trade Gate + Mode Gate + Cap Gate를 통과해야 함.
•	Emergency Stop은 무조건 최우선(발동 시 즉시 신규진입 차단).
________________________________________
2) 4-Step Ramp 정의
Step P1 — 1% Pilot (Smoke Test)
•	자본 Cap: 총자본의 1%
•	일 최대 신규 진입: 1회
•	동시 보유: 1종목
•	허용 전략: Swing 1개 모듈만(Trend-Follow)
•	Strike: 0 (완전 비활성)
•	목표: 주문→체결→포트폴리오 계산→AAR 생성까지 E2E 무결성 확인
승격 조건(둘 다 충족)
•	Filled 주문 10건 누적, 로그 누락 0
•	Gate 위반/차단 로직이 의도대로 작동(차단 케이스 3개 이상 재현)
________________________________________
Step P2 — 5% Pilot (Stability Test)
•	자본 Cap: 5%
•	일 최대 신규 진입: 2회
•	동시 보유: 2종목
•	허용 전략: Swing 2개 모듈(Trend-Follow + Pullback)
•	Strike: 0 (유지)
•	목표: 변동 구간에서 Risk/DD/Daily cap 정상 반응 확인
승격 조건
•	2주(또는 20건 교전) 동안:
o	Daily Loss Cap 위반 0
o	CRITICAL incident 0
o	portfolio_state 계산 불일치 0
________________________________________
Step P3 — 10% Pilot (Controlled Aggression)
•	자본 Cap: 10%
•	일 최대 신규 진입: 3회
•	동시 보유: 3종목
•	허용 전략: Swing 풀세트 + Core “신규진입” 제한적 허용
•	Strike: 0.2×(기본 Strike) × Pilot multiplier(0.5) 로 매우 제한
•	목표: Strike가 들어와도 폭주하지 않음을 검증
승격 조건
•	Strike 포함 30건 교전:
o	Loss streak 대응(Strike 0) 자동 작동 3회 이상 확인
o	MaxDD 동적 제한 준수(위반 0)
________________________________________
Step P4 — 20% Pilot Cap (Pre-Live)
•	자본 Cap: 20% (Pilot 상한)
•	일 최대 신규 진입: 5회(권장 3회 유지)
•	동시 보유: 5종목(권장 3~4)
•	Strike: Pilot multiplier 유지(0.5) + CrisisGate 엄격
•	목표: Full Live 전 마지막 안정성/효율성 검증
Full Live 검토 조건(참고)
•	50건 이상 교전
•	CRITICAL incident 0 (최근 30일)
•	DD/일손실 상한 위반 0
•	Backtest 대비 실전 성과 괴리 허용 범위 내
________________________________________
3) “후퇴(De-escalation)” 규칙
아래 중 하나라도 발생 시 즉시 이전 Step으로 후퇴(또는 PAPER 복귀):
•	Daily Loss Cap 1회라도 위반
•	Snapshot Freshness RED가 5분 이상 지속
•	KIS 주문 실패 연속 3회
•	portfolio_state 불일치 감지(체결/수량/평가금액 mismatch)
________________________________________
4) Warroom에 반드시 추가할 Pilot Ramp 패널
Header 옆에 작게 고정 표시:
•	Pilot Step: P1/P2/P3/P4
•	Cap: 1%/5%/10%/20%
•	오늘 신규 진입 횟수 / 상한
•	Strike Enabled? (Y/N)
•	승격까지 남은 조건(예: “Filled 3/10”)
________________________________________
5) 지금 당장 해야 하는 “첫 실행 체크” (P1 시작 전)
1.	Mode = PILOT 이지만 **Cap=1%**로 강제(새 변수 pilot_cap_pct)
2.	Strike = 0 강제
3.	Paper 1건/실거래 1건을 각각 수행해 order_log→portfolio_state 일치 확인
4.	Telegram에서 /freeze on 후 주문이 차단되는지 확인
5.	/freeze off 후 정상 복귀 확인
________________________________________
6) 구현 메모(필수 변수)
•	system_mode.mode (PILOT)
•	pilot_step (P1~P4)
•	pilot_cap_pct (0.01 / 0.05 / 0.10 / 0.20)
•	strike_enabled (P1,P2=false; P3,P4=true)
•	daily_entry_limit
이 값들은 DB 테이블(system_config) 로 저장하는 것이 안전합니다.
________________________________________
 
이제 **Pilot Ramp를 시스템에 “구조적으로 봉인”**합니다.
단순 운영 규칙이 아니라:
DB에 기록되고
Gate에 강제되며
UI에 표시되고
Audit 로그가 남는 구조
로 만듭니다.
