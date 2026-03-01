16_Config_Management_Plan.md
Document ID: AEGIS-X-CM-v1.0
Owner: System Engineering Office
Classification: Configuration & Change Control Specification
________________________________________
1. Purpose
본 문서는 Aegis-X의 다음 항목에 대한 형상관리 방침을 정의한다:
1.	Source Code
2.	Strategy Versions
3.	Configuration Files
4.	Environment Variables
5.	LLM Models & Prompt Versions
6.	Database Schema
7.	Documentation Sets
목표:
무단 변경 방지, 변경 추적, 재현 가능성 보장
________________________________________
2. Configuration Item (CI) 정의
________________________________________
2.1 Code CI
•	/app
•	/scripts
•	/api
•	/broker
•	/data
모든 코드 변경은 Git Commit 필수.
________________________________________
2.2 Strategy CI
Strategy Object는 형상 항목이다.
{
  "strategy_id": "AegisX_v3.4",
  "regime_model_version": "...",
  "allocation_profile_version": "...",
  "roe_profile_version": "...",
  "risk_profile_version": "...",
  "learning_profile_version": "...",
  "capital_profile_version": "..."
}
전략은 코드와 분리된 버전 관리 대상.
________________________________________
2.3 Configuration Files
•	config/refresh_schedule.yaml
•	.env (환경 변수)
•	LLM routing config
•	Risk parameter file
________________________________________
2.4 Database Schema CI
•	PostgreSQL schema definition
•	migration script
•	table versioning
________________________________________
2.5 Documentation CI
•	/docs/*.md
•	version header 필수
________________________________________
3. Versioning Policy
________________________________________
3.1 Semantic Versioning
MAJOR.MINOR.PATCH
변경 유형	버전 증가
구조 변경	MAJOR
기능 추가	MINOR
버그 수정	PATCH
________________________________________
3.2 Strategy Versioning
AegisX_v3.4
규칙:
•	전략 파라미터 변경 → MINOR 증가
•	구조 변경 → MAJOR 증가
________________________________________
4. Change Control Process
________________________________________
4.1 Change Request (CR) 단계
1.	Change Proposal 작성
2.	Impact Analysis 수행
3.	Twin Simulation 실행
4.	Risk 검토
5.	Governance 승인
6.	Deployment
________________________________________
4.2 Change Request Template
{
  "change_id": "CR-2026-03-01-01",
  "type": "Strategy Update",
  "affected_components": ["Allocation Engine"],
  "risk_assessment": "Medium",
  "twin_result": "PASS",
  "approval_status": "Approved"
}
________________________________________
5. Environment Variable Management
________________________________________
5.1 Key Storage Policy
•	Git commit 금지
•	OS 환경변수 사용
•	분기별 Rotation
•	Access Log 유지
________________________________________
5.2 Key Inventory
Key	Owner	Rotation
FRED_API_KEY	Data Team	6개월
KIS_APP_KEY	Execution	3개월
OPENAI_API_KEY	AI Team	3개월
________________________________________
6. LLM Configuration Management
________________________________________
6.1 Model Routing Version
•	Primary Model
•	Secondary Fallback
•	Structured-only mode
변경 시 Governance 승인 필수.
________________________________________
6.2 Prompt Versioning
모든 시스템 프롬프트는 버전 포함:
REGIME_PROMPT_v2.3
LLM 사용 로그에 prompt_version 기록.
________________________________________
7. Database Migration Policy
•	모든 Schema 변경은 migration script 작성
•	Production 전 Twin DB에서 테스트
•	Rollback script 필수
________________________________________
8. Deployment Control
________________________________________
8.1 Deployment Types
Type	설명
Hotfix	긴급 수정
Minor Release	기능 개선
Major Release	구조 변경
________________________________________
8.2 Production Gate
Deployment 전 필수 조건:
•	check_comm OK
•	data_integrity OK
•	Twin PASS
•	Governance 승인
________________________________________
9. Backup & Rollback
________________________________________
9.1 Daily Backup
•	PostgreSQL dump
•	Ledger snapshot
•	state_ledger backup
________________________________________
9.2 Rollback Rule
•	이전 전략 버전 유지
•	DB migration rollback 가능
•	Strategy downgrade 가능
________________________________________
10. Configuration Audit
분기별 점검:
•	Strategy Version Consistency
•	Env Key Rotation
•	LLM Routing 변경 여부
•	DB Schema Drift 여부
________________________________________
11. Configuration Freeze Policy
다음 상황 시 변경 금지:
•	Crisis Mode
•	Structural Alarm 상태
•	Incident Level ≥ 3
________________________________________
12. Verification Checklist
•	Git commit traceability 확인
•	Strategy version mismatch 검사
•	Prompt version mismatch 검사
•	DB schema hash 비교