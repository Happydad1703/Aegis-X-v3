# Aegis-x v3 SE Master Index

This directory contains the full Software Engineering Documentation Set.

**Design Status**: Frozen (v3.0)

**참조 기준(Reference)**: `D:\AEGIS-X_v3\docx_md` — docs의 SE 문서는 docx_md 내 문서를 참조하여 Realign된 버전입니다.

All implementation must strictly follow these documents.

---

## 참조 소스 및 Realign

- **참조 경로**: `D:\AEGIS-X_v3\docx_md`
- **적용 방법**: docx_md 내 모든 문서를 docs/ 로 복사하여 동기화. docs/ 의 00_~65_ 계열 및 관련 문서는 docx_md와 일치합니다.
- **실라인 체크리스트**: [System_Realignment_Checklist.md](./System_Realignment_Checklist.md) — DB·엔진·게이트·실행·API가 docx_md/64·65·43 등 명세와 일치하는지 점검.

---

## docx_md 기준 문서 구성 (00 ~ 65)

| 번호 | 문서 | 비고 |
|------|------|------|
| 00~04 | 00_System_Charter, 01_Stakeholder_Requirements_SRS, 02_System_Architecture_SAD, 03_External_Interface_Control_Document_ICD, 04_Data_Architecture_DDD | 헌장, SRS, SAD, ICD, DDD |
| 05~12 | 05_Regime_Engine_Spec, 06_Allocation_Risk_Learning_Spec, 07_Fleet_Execution_Spec, 08_Digital_Twin_Spec, 09_Meta_Control_Spec, 10_Self_Healing_Spec, 11_Governance_Audit_Spec, 12_Capital_Scaling_Spec | 엔진·실행·Twin·메타·자기치유·거버넌스·스케일링 |
| 14~18 | 14_Test_Verification_Validation_Plan_TVP, 15_Risk_Register, 16_Config_Management_Plan, 17_Security_Model, 18_CIC_Warroom_Spec | TVP, 리스크, 형상, 보안, CIC Warroom |
| 29~43 | 29_Battlefield_Definition, 30_Global_Force_Follow_The_Sun, 31_Force_Organization, 32_Warroom_IA, 33_Ubiquitous_Command, 34~39 Force/Regime, 40_AAR_Learning, 41_Execution_Deployment, 42_Roadmap_90D, 43_DB_Schema_v1_Core_Spec.sql, 43_1_MVP_Infrastructure | 전장·부대·Warroom·실행·로드맵·DB 스키마 |
| 47~65 | 47/48_Engine_Worker_Skeleton, 49_Mode_Execution_Layer, 50_Pre_Trade_Gate, 51_Order_Execution, 52_Portfolio_State, 53~62 AAR/Pilot/Test, 63_Day1_Pilot_Runbook, 64_Phase0_1_DB_and_MinWorker, 65_Final_Directory_Architecture_Lock | 워커·게이트·실행·파일럿·Phase0·구조 락 |

---

## 기존 SE_01~SE_64와의 관계

- **SE_01 ~ SE_64**: 기존 모듈/전략별 스펙 (시스템 비전, 부대 구조, 레짐, 자본 배분, Strike/Swing/Core/Reserve 등). docx_md의 00_~65_ 번호 체계와 내용상 대응되며, **권장 참조는 docx_md** 입니다.
- **65_Final_Directory_Architecture_Lock_Spec.md**: 디렉터리/아키텍처 동결 — `/backend/app/` 구조 변경 금지, DB-First, Gate/Mode/Risk 체계.

---

## SE 완전 정합 설계 (Structure + Math + Gate + LLM)

- **[SE_Complete_Alignment_Structure_Math_Gate_LLM.md](./SE_Complete_Alignment_Structure_Math_Gate_LLM.md)** — SE-39(Regime 수학·snapshot 계약), SE-50(Pre-Trade Gate·Wide Stop), SE-64(DB/Snapshot/Worker), SE-58(LLM Mesh), SE-65(Directory Lock) 모듈 단위 정합. regime_current 스냅샷 계약, Core Force 최종 판정, 위험 구간 명시.

## 위임 및 상시 지시

- **[Delegation_of_Authority_and_Standing_Order.md](./Delegation_of_Authority_and_Standing_Order.md)** — 기획/관리·최고 통수권자로부터 시스템 완성까지 책임·권한 위임. 상시 지시(기준 준수, 추진 순서, 멈추지 않음, 품질 관문, 문서 동기화). 구속 문서 및 Next Actions.

## 추진계획 (우선순위 기반 구현 로드맵)

- **[Implementation_Priority_Roadmap.md](./Implementation_Priority_Roadmap.md)** — 책임개발자 관점 추진계획. 중요도(P0~P3)·긴급도(U0~U3), Phase 0-2(API/Health) → Phase 1(파이프라인·Warroom) → Phase 2(전략·리스크·실행) → Phase 3(LLM·안정화). 의존성·완료 판정·체크포인트.

## Test & Evaluation Master Plan (Verification 준비)

- **[Test_Evaluation_Master_Plan.md](./Test_Evaluation_Master_Plan.md)** — 검증 수준(Contract/Unit/Integration/System/Acceptance), Phase 0-1 필수 검증(계약 테스트·엔진 1사이클·진단 스크립트), 실행 순서, RTM 요약, 진입/완료 기준, 지속 검증, Production Gate. TVP(14) 연계.

## 프로세스 정합 세부설계 및 점검계획

- **[Process_Alignment_Detailed_Design_and_Check_Plan.md](./Process_Alignment_Detailed_Design_and_Check_Plan.md)** — 프로세스맵·알고리즘·DB·Dashboard & Control·Push to Telegram의 SE 정합 확인용 **세부설계**(Module Master, Schema Master, Signal Interface, UI/UX) 및 **점검계획**(Alignment/Sync/통합 점검, SE 문서별 점검표, 주기·산출물).

## 프로세스·모듈·DB·Warroom 매핑

- **[SE_Process_Module_DB_Warroom_Mapping_Table.md](./SE_Process_Module_DB_Warroom_Mapping_Table.md)** — 정보획득 → 분석 → 기록 → 전장별 Regime → 군별 자원·전략 → 후보군 선정 → Target Lock-on → 교전수칙 → 교전 → 전투결과보고 → 종합분석 → 시스템 튜닝의 전체 프로세스와 모듈·DB·Warroom CIC/Dashboard 연결고리 1:1 매핑.

## 한국 소스·LLM R&R

- **[한국_뉴스_기업정보_소스_정리.md](./한국_뉴스_기업정보_소스_정리.md)** — 한국 뉴스·공시·매크로 소스, API Key 환경변수, v3 모듈 위치 (env_keys, check_comm, ICD).
- **[합참_SRC_각군_LLM_RR_점검_결과.md](./합참_SRC_각군_LLM_RR_점검_결과.md)** — JCS/STRATCOM/SRC/각군 R&R별 LLM 매핑, 통신 점검 순서, v3 결과 확인 방법.
- **[외부기관_목록_및_통신점검.md](./외부기관_목록_및_통신점검.md)** — 외부기관 종합 테이블, env_keys·check_comm·저장소(DB) 연결, v3 관련 파일.
- **[외부기관_모듈_LLM_프로세스결과_DB_매칭테이블.md](./외부기관_모듈_LLM_프로세스결과_DB_매칭테이블.md)** — 외부기관(뉴스/정보/매크로/공시/브로커/LLM) → 모듈 → LLM 역할 → 프로세스 결과 → DB 테이블·snapshot_key 매칭.
- **[입력DB_프로세싱_출력DB_대시보드_매칭테이블.md](./입력DB_프로세싱_출력DB_대시보드_매칭테이블.md)** — 입력 DB → 프로세싱(모듈/LLM) → 출력 DB · Warroom Dashboard 매칭.
- **[CoreForce_Structural_Trend_Mapping.md](./CoreForce_Structural_Trend_Mapping.md)** — Core Force 문장→입력/출력 dict→snapshot_key 스키마 매핑 (Cursor 구현용).
- **[Yahoo_RapidAPI_연동.md](./Yahoo_RapidAPI_연동.md)** — Yahoo Finance (RapidAPI) 시세 연동: 키 발급, Basic 제약, v3 연동 시 env_keys·check_comm·모듈 경로.

## 런처·원격 접속·Push 알림

- **[Launcher_and_Remote_Access.md](./Launcher_and_Remote_Access.md)** — 바탕화면/툴바 바로가기, 단일·복수 디스플레이(Warroom/Dashboard 분할), WSL 터미널 링크, Mobile(S24 Ultra) 원격 접속, Telegram/Kakao Push(시장개시·종료·target·매매성립·AAR·Freeze/Retract/E-Stop).

## 시스템 운용 매뉴얼

- **[System_Operations_Manual.md](./System_Operations_Manual.md)** — 운용자·관리자용 매뉴얼. 개요·전제조건, 초기 설정, 일일/시작 절차, 런처·Warroom 사용, 제어 동작, 스크립트 참조, 원격·모바일·Push, 장애 대응, 참조 문서.
- **[Stability_Check_Result_and_Followup.md](./Stability_Check_Result_and_Followup.md)** — 실행 안정성 점검 결과 분석, 실패 원인(DB 연결 불일치), 후속조치(포트·.env·재점검), 적용한 코드 변경 요약.
- **[Stability_Check_Report_Unresolvable.md](./Stability_Check_Report_Unresolvable.md)** — 재실행 결과·자체 해결 불가 사항 보고(호스트 5433 포트 충돌, 필요한 환경 조치).

---

## Change Management

- Any modification requires version bump.
- Regression impact must be analyzed.
- Audit record mandatory.
- docx_md 수정 시 docs/ 에 동기화 후 실라인 체크리스트 실행 권장.
