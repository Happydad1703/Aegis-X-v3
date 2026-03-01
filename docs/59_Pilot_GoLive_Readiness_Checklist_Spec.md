59_Pilot_GoLive_Readiness_Checklist_Spec.md (v1.0)

이제 **Pilot 운영 전 최종 통합 검증 체크리스트 (Go-Live Readiness Gate)**를 확정합니다.
이 문서는 단순 점검표가 아니라:
PILOT 모드로 전환하기 전에
반드시 “기계적으로 통과”해야 하는 조건 집합
입니다.

1️⃣ 운영 전제
•	단일 KIS 계좌
•	PostgreSQL Docker 정상
•	DB-First 원칙 100% 준수
•	Warroom은 snapshot만 읽음
•	Mode는 기본 PAPER
________________________________________
2️⃣ A. 인프라 무결성 체크
A-1 DB 상태
•	PostgreSQL 컨테이너 24시간 무중단
•	DB write latency < 50ms
•	Connection pool overflow 없음
•	engine_snapshot 48시간 정상 기록
•	최근 24시간 RED freshness 없음
A-2 Engine Worker
•	engine_heartbeat 60초 이내 갱신
•	engine_error_log 최근 24시간 CRITICAL 0건
•	Snapshot min_interval 정상 작동
A-3 Ingest
•	최소 3개 외부 소스 24시간 정상 수집
•	macro_context 최근 6시간 내 갱신
•	verify_data_integrity.py 통과
________________________________________
3️⃣ B. Risk & Mode 무결성
B-1 Mode Enforcement
•	BACKTEST → 주문 불가 확인
•	PAPER → KIS 호출 없음 확인
•	PILOT → Capital Cap 적용 확인
•	FULL_LIVE → 수동 승인 없이는 진입 불가
B-2 Pre-Trade Gate 테스트
•	CrisisProb > 0.8 → 주문 차단 확인
•	DD 초과 → 주문 차단 확인
•	Snapshot stale → 주문 차단 확인
•	Emergency Stop → 즉시 차단 확인
________________________________________
4️⃣ C. Portfolio & Accounting 검증
•	order_log → portfolio_state 정확 반영
•	포지션 0 → battle_report 생성 확인
•	AAR 점수 정상 계산
•	Fleet exposure 합 = 100%
•	Capital Scaling G 계산 정확
________________________________________
5️⃣ D. Pilot Cap 조건
Pilot 모드에서:
•	총자본의 20% 이내 사용
•	단일 종목 ≤ 5%
•	Strike 자동 50% 축소
•	Daily Loss Cap 동적 적용
•	Max DD 동적 적용
________________________________________
6️⃣ E. Global Session 검증
•	Session 감지 정상
•	ASIA에서만 실전 활성
•	US Session은 제한 또는 Paper
•	NIGHT에서 Strike 0 확인
________________________________________
7️⃣ F. Warroom UI 검증
Header:
•	Mode 표시
•	CrisisProb 표시
•	Freshness 표시
•	Session 표시
•	Capital Scaling 표시
Pages:
•	Allocation Matrix 정상 표시
•	Portfolio Variance Top N 표시
•	Incident Feed 표시
•	AAR Summary 표시
________________________________________
8️⃣ G. Telegram 긴급 통제
•	/status 정상 응답
•	/freeze on 작동
•	/retract r1 작동
•	Mode 하향만 허용
•	FULL_LIVE 상향 불가 확인
________________________________________
9️⃣ H. Stress Test (필수)
시나리오 1 — 급락
•	CrisisProb 강제 0.9
•	Strike 자동 0
•	신규 주문 차단
시나리오 2 — DB 중단
•	DB kill 후 복구
•	Worker 재연결
•	Incident 기록 확인
시나리오 3 — KIS 실패
•	KIS 오류 3회
•	Mode 자동 PAPER 전환
________________________________________
🔟 Pilot Go 조건
아래 5개 모두 만족 시 PILOT 전환 가능:
1.	7일 연속 PAPER 무사고
2.	Gate 위반률 < 1%
3.	Portfolio 계산 오류 0건
4.	Incident CRITICAL 0건 (최근 72시간)
5.	Backtest Sharpe > 0.5 & MDD 허용범위 내
________________________________________
11️⃣ Pilot 운영 규칙
Pilot 단계에서는:
•	1일 최대 3회 신규 진입
•	1종목 동시 보유 금지
•	1회 교전 최대 손실 1%
Pilot은 “수익 극대화 단계”가 아니라:
시스템 검증 단계
입니다.
________________________________________
🔥 Pilot 성공 후
Pilot 30~50 교전 데이터 확보 후:
•	AAR 안정성 검증
•	Crisis 반응 정확도 확인
•	DD 제한 위반 0건
→ 그때 Full Live 검토
________________________________________
 
