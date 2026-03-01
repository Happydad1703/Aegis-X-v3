05_Regime_Engine_Spec.md
Document ID: AEGIS-X-REGIME-v1.0
________________________________________
1. Regime Axes
•	Liquidity
•	Growth
•	Policy Pressure
•	Stress
________________________________________
2. Hybrid Model
Regime Score =
0.4 Structured Event
+0.4 Factor Engine
+0.2 LLM Bias
________________________________________
3. LLM Staffing Plan
사용 LLM
Model	역할	Primary	Fallback
OpenAI	Narrative 분석	Primary	Claude
Claude	Context reasoning	Secondary	Gemini
Gemini	뉴스 요약	Secondary	OpenAI
DeepSeek	Cost-efficient batch	Batch	—
________________________________________
4. LLM Fallback Plan
•	Primary 모델 실패 시 Secondary 호출
•	2회 실패 시:
o	Structured + Factor만으로 Regime 계산
o	Confidence 감소
•	LLM 장애 지속 시 Incident 생성
________________________________________
5. Staffing Plan (Human Oversight)
Role	Responsibility
Strategy Dev	전략 설계
Risk Officer	리스크 승인
Governance Officer	감사·로그 검토
System Engineer	인프라 관리
________________________________________
6. Drift Detection
•	5일 이동 평균 변화
•	Narrative shift score
•	Crisis probability 변화
________________________________________
추가 포함 사항
External Source Monitoring
•	check_comm.py → 통신
•	verify_data_integrity.py → 데이터 유입
•	verify_db_consumer_pipeline.py → DB 소비 검증
________________________________________
현재 상태
이제 Aegis-X는:
•	Charter 확정
•	요구사항 명문화
•	아키텍처 정의
•	외부 인터페이스 통제 문서화
•	데이터 구조 정의
•	Regime AI 고도화 명세화
•	LLM Staffing & Fallback 정의