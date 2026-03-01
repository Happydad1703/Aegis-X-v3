# 위임 및 상시 지시 (Delegation of Authority and Standing Order)

**발령:** 기획/계획/관리 및 감독자 · 최고 통수권자  
**대상:** 시스템 구축 책임 수행 주체 (개발·검증·운영)  
**효력:** 시스템 완성까지 지속

---

## 1. 위임 선언

기획/계획/관리 및 감독자이자 최고 통수권자로서, **Aegis-X v3 자동자산운용 시스템을 완성까지** 이르는 일에 대한 **책임과 권한**을 위임한다.

**위임 범위**
- 지금까지 수립된 **SE Documentation** 및 **추진계획(Implementation Priority Roadmap)** · **TEMP(Test & Evaluation Master Plan)** · **프로세스 정합 세부설계/점검계획**을 **기준**으로 시스템 구축을 완료할 권한과 책임.

**목표**
- **실패하지 않는** 시스템 (안정성·3원칙·Safety Priority·Never-Stop 아키텍처)
- **수익을 극대화**할 수 있는 자동자산운용 시스템 완성

---

## 2. 상시 지시 (Standing Order)

시스템이 **멈추지 않고** 추진계획에 따라 진행되도록, 아래를 **상시 지시**로 둔다.

| # | 지시 | 내용 |
|---|------|------|
| 1 | **기준 준수** | 모든 설계·구현·검증은 **SE Documentation**, **Cursor SOO (SE-LOCKED)**, **TEMP**, **Implementation Priority Roadmap**, **Process_Alignment_Detailed_Design_and_Check_Plan**에 정합되게 수행한다. |
| 2 | **추진 순서** | **Phase 0-2 → Phase 1 → Phase 2 → Phase 3** 순서를 지킨다. Phase 완료 판정 후 다음 Phase로 진입한다. |
| 3 | **멈추지 않음** | 불확실한 경우에도 **보수적 전환**(모드 전환, 신규 진입 차단, 리스크 축소, DB 기록)으로 다음 행동을 수행한다. "결정이 안 나서 멈춤"은 허용하지 않는다. |
| 4 | **품질 관문** | PR/커밋 시 **계약 테스트(contract + engine_loop)** 필수 통과. SOO PR 체크(engines 무 DB/네트워크, API/UI 무 계산, snapshot_repo 외 무 write)를 통과한 후에만 병합한다. |
| 5 | **문서 동기화** | 모듈·스키마·API·UI·Telegram 변경 시 **Module Master, Schema Master, Signal Interface, 점검계획**에 반영하고, 필요 시 Alignment 점검을 수행한다. |

---

## 3. 구속 문서 (Binding References)

실행 시 다음 문서가 **최우선 기준**이다.

| 문서 | 용도 |
|------|------|
| **Cursor_SOO_Phase0_1.md** | 절대 규칙(3원칙·Safety)·Data Flow·Module Structure·DB/Snapshot·Warroom·LLM·Coding Rules |
| **Implementation_Priority_Roadmap.md** | Phase 0-2/1/2/3 추진 순서·작업 ID·완료 판정·의존성 |
| **Test_Evaluation_Master_Plan.md** | 검증 이행(TEMP §10)·계약 테스트·진단 스크립트·Production Gate |
| **Process_Alignment_Detailed_Design_and_Check_Plan.md** | 프로세스맵·Module/Schema/Signal/UI 세부설계·점검계획 |
| **SE_Complete_Alignment_Structure_Math_Gate_LLM.md** | SE-39/50/64/58/65 정합·Regime·Gate·LLM Mesh |
| **14_Test_Verification_Validation_Plan_TVP.md** | Unit/Integration/System/Acceptance·Crisis·Governance 검증 요구 |
| **docs/00_~65_** (SE 문서군) | 요구사항·아키텍처·인터페이스·스키마·UI·운영 명세 |

---

## 4. 실행 시 다음 액션 (Next Actions)

위임 및 상시 지시에 따라, **중단 없이** 아래 순서로 진행한다.

1. **Phase 0-2 완료**  
   API/Health가 DB 스냅샷 기반으로 응답, 계약 테스트 유지. (Implementation_Priority_Roadmap § Phase 0-2)

2. **Phase 1 착수**  
   Ingest 1소스 → Regime → 스냅샷, Warroom 6종 표시, Pre-Trade Gate 골격. (동 로드맵 § Phase 1)

3. **이후 Phase 2 → Phase 3**  
   Allocation/Risk/Core/Execution, 이어서 LLM·지속검증·TVP 상위 검증.

4. **매 PR/커밋**  
   `pytest backend/tests/test_contract_*.py backend/tests/test_engine_loop.py -v` 실행 및 SOO PR 체크 준수.

---

## 5. 확인

- 위임은 **시스템 완성까지** 유효하다.
- 상시 지시는 **추가 지시가 있을 때까지** 적용된다.
- 실행 주체는 위 **구속 문서**와 **상시 지시**에 따라 책임과 권한을 행사한다.

---

*Ref: Cursor_SOO_Phase0_1.md, Implementation_Priority_Roadmap.md, Test_Evaluation_Master_Plan.md, Process_Alignment_Detailed_Design_and_Check_Plan.md, SE_Complete_Alignment_Structure_Math_Gate_LLM.md*
