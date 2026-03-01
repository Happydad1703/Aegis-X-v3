11_Governance_Audit_Spec.md
Document ID: AEGIS-X-GOV-v1.0
Owner: Governance Office / Risk Committee
Classification: Institutional Governance & Audit Specification
________________________________________
1. Purpose
Governance Layer의 목적:
1.	모든 의사결정의 완전 추적성 확보
2.	전략 변경·리스크 변경의 승인 기록
3.	LLM 사용 이력 및 개입 범위 기록
4.	사고 발생 시 완전 재현 가능성 확보
5.	규제·외부 감사 대응 구조 확보
________________________________________
2. Governance Principles
1.	Traceability First – 모든 결정은 재구성 가능해야 함
2.	No Silent Change – 자동 변경도 반드시 기록
3.	Separation of Power – 전략·리스크·감사 분리
4.	Immutable Logging – 로그 수정 불가
5.	Explainability by Design – 인간이 이해 가능한 설명 포함
________________________________________
3. Decision Object Standard
모든 시스템 의사결정은 아래 스키마를 따른다.
{
  "decision_id": "DEC_20260315_001",
  "timestamp_utc": "...",
  "layer": "Allocation / Risk / Meta / SelfHealing",
  "input_snapshot_ref": "...",
  "logic_version": "...",
  "parameters_before": {...},
  "parameters_after": {...},
  "explanation": "Human-readable explanation",
  "approved_by": "AUTO / RiskOfficer / Governance",
  "parent_decision_id": "...",
  "hash": "..."
}
________________________________________
4. Immutable Audit Trail
4.1 Append-Only Ledger
•	모든 Decision Object는 append-only 저장
•	삭제·수정 금지
4.2 Hash Chain 구조
previous_hash → current_hash
변조 시 체인 붕괴.
4.3 Daily Snapshot
•	매일 1회 Audit Snapshot 생성
•	외부 저장소(오프라인 백업) 보관
________________________________________
5. Approval Flow Matrix
Action	Strategy Dev	Risk Officer	Governance
Strategy Promotion	✔	✔	✔
Risk Parameter 변경	✖	✔	✔
LLM Model 변경	✔	✔	✔
Emergency Mode 진입	AUTO	✔ (post)	✔
________________________________________
6. LLM Governance
________________________________________
6.1 LLM Usage Logging
모든 LLM 호출 기록:
{
  "llm_provider": "OpenAI",
  "model": "gpt-4",
  "prompt_hash": "...",
  "response_hash": "...",
  "purpose": "Regime Bias",
  "fallback_used": false,
  "latency_ms": 842
}
저장 위치:
•	PostgreSQL llm_usage_log
________________________________________
6.2 LLM Fallback Chain
Primary 실패 시:
OpenAI → Claude → Gemini → Structured Only Mode
Fallback 발생 시:
•	Confidence 감소
•	Incident 기록
________________________________________
6.3 Prompt Injection 방어
•	외부 뉴스는 Raw → Sanitized → Structured Event
•	LLM에 직접 원문 전달 금지
•	시스템 프롬프트 외부 노출 금지
________________________________________
7. Incident Management Framework
________________________________________
7.1 Incident Levels
Level	Example
1	API 일시 장애
2	Regime 오판
3	Risk Cap 초과
4	Systemic Alarm
________________________________________
7.2 Incident Object
{
  "incident_id": "...",
  "severity": 3,
  "trigger": "...",
  "actions_taken": [...],
  "resolution_status": "OPEN / CLOSED",
  "postmortem_required": true
}
________________________________________
8. External Data Governance
________________________________________
8.1 통신 점검
•	check_comm.py 주 1회 자동 실행
•	결과 PostgreSQL comm_check_log 저장
________________________________________
8.2 데이터 무결성 점검
•	verify_data_integrity.py 일 1회
•	FAIL 발생 시 Alert
________________________________________
9. Access Control Model
________________________________________
9.1 Role Definition
Role	Permission
Strategy Dev	전략 제안
Risk Officer	리스크 승인
Governance Officer	최종 승인
System Engineer	인프라 관리
________________________________________
9.2 Key Management
•	API Key는 환경변수
•	Git 저장 금지
•	분기별 Rotation
•	키 사용 이력 기록
________________________________________
10. Reporting Framework
월간 자동 보고서 포함:
1.	Regime Distribution
2.	Asset Allocation 변화
3.	Strategy 변경 이력
4.	Risk Event 요약
5.	LLM 사용 통계
6.	Incident Summary
________________________________________
11. Audit Retention Policy
Data	Retention
Decision Objects	영구
LLM Logs	3년
Incident Logs	영구
Strategy Lab Results	5년
________________________________________
12. Governance Override Hierarchy
Governance
   >
Self-Healing
   >
Risk Engine
   >
Meta-Control
   >
Strategy
Governance는 최종 권한 보유.
________________________________________
13. Verification Checklist
항목	Required
Decision chain integrity test	✔
Hash tamper detection test	✔
LLM fallback simulation	✔
Incident escalation test	✔
Approval workflow test	✔
Key rotation audit	✔