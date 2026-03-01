# 새 대화 시 맥락 요약 (지휘 지시문)

**용도**: Chat/Composer를 새로 열 때 이 문서를 **@docs/Context_Summary_For_New_Chat.md** 로 첨부하거나, 아래 요약을 붙여넣으면 AI가 Aegis-X v3의 현재 단계와 결론을 즉시 반영할 수 있습니다.

---

## ⚡ 위임 및 상시 지시 (필수 확인)

**기획/계획/관리 및 최고 통수권자**로부터 **시스템 완성까지 책임과 권한이 위임**되어 있음.  
- **상시 지시:** 시스템을 **멈추지 말고** **추진계획(Implementation Priority Roadmap)** 에 따라 진행. SE Documentation · SOO · TEMP · 프로세스 정합 세부설계/점검계획을 기준으로 실행.  
- **목표:** 실패하지 않는 · 수익 극대화 자동자산운용 시스템 완성.  
- **상세:** **@docs/Delegation_of_Authority_and_Standing_Order.md** 참조.

---

## 프로젝트 정체

- **Aegis-X v3**: SE 문서(docx_md, 00~65) 기반 자산운용 시스템. 엄격한 DB-First, 모듈 경계, Single Write Path.

## 확정 전제 (변경 금지)

- **컨테이너**: `aegisx-db` / **DB**: `aegisx` / **유저**: postgres / **호스트 포트**: 5433  
- **.env**: `DATABASE_URL=postgresql+psycopg2://postgres:2041@localhost:5433/aegisx`  
- **마이그레이션**: PowerShell에서 `< file.sql` 사용 금지 → `Get-Content -Raw | docker exec -i ... psql` 파이프 방식.

## Chain of Command (절대 위반 금지)

1. **DB-Only Read**: UI·상위 계층은 `engine_snapshot`만 조회, 직접 계산 금지.  
2. **Strict Module Boundary**: `engines/`는 순수 함수(dict in, dict out), DB/SQL 금지.  
3. **Single Write Path**: 엔진 결과는 `core/snapshot_repo.py`를 통해서만 DB 기록.

## Snapshot 6종 키 (Phase 0-1 정본)

- `engine_heartbeat`, `comm_health`, `regime_current`, `operation_mode`, `llm_status`, `risk_guard`  
- 스크립트: 동기 `run_single_cycle_sync` + `SessionLocal`. API: 비동기 `get_db` + `AsyncSessionLocal` (Phase 0-2).

## 현재 단계 요약 (새 단계 시작 시 여기만 갱신)

- **외부 기관 통신**: 모든 API Key는 **Windows 11 환경변수**에 설정. `backend/app/core/env_keys.py`에서만 조회. 통신 확인: `python scripts/check_comm.py` (FRED, LLM, KIS). → docs/ENV_Windows11_API_Keys.md
- DB 마이그레이션은 **migrate_db.ps1**(파이프 방식), 컨테이너 **aegisx-db** 기준으로 적용 완료.
- Worker는 **run_engine_worker.ps1** → **run_engine_cycle.py**(동기)로 6종 스냅샷 적재.
- **추진 우선순위**: Phase 0-2(API/Health) → Phase 1(Ingest·Regime·Warroom) → Phase 2(Allocation·Risk·Core·Execution) → Phase 3(LLM·지속검증). → docs/Implementation_Priority_Roadmap.md
- **Phase 0-2 완료:** /api/health DB 기반+메타, CIC snapshot API Warroom 필수 메타 반환. 계약 테스트 4종 통과.
- **Phase 1 완료:** ingest_worker(heartbeat+FRED)→ext_event_raw(event_repo), regime_engine(SE-39), engine_worker→regime_current, Warroom /warroom 6종 카드+필수 props, Pre-Trade Gate(structural_trend/BROKEN→block_trade).
- **Phase 2 완료:** allocation_engine, fleet_budget_engine, core_engine(core_force_state), snapshot_keys+allocation_matrix/fleet_budget_snapshot/core_force_state, order_log(002), order_repo, paper_executor→order_log.
- **Phase 3 완료:** llm_gateway 골격(role, request_llm, get_health, get_lks/record_lks, on_blackout→incident_log).
- 다음: [ ] 실제 LLM 연동, verify_data_integrity 정기화, TVP System/Governance 검증.

## 참조 문서 (@ 로 첨부 권장)

- **@docs/Cursor_Developer_Mode_Hard_Lock.md** — Hard Architecture Lock 전조문 (필수)
- **@docs/Cursor_SOO_Phase0_1.md** — 1페이지 표준 운영문 (작업 시작 전 항상 읽고 따르기)
- **@docs/LLM_Staffing_Fallback_Plan.md** — LLM N+1 Fallback, LKS, Warroom 표시 규격
- **@docs/64_Phase0_1_DB_and_MinWorker_Package_Spec.md**  
- **@docs/65_Final_Directory_Architecture_Lock_Spec.md**  
- **@docs/Cursor_Final_Development_Strategy.md**  
- **@docs/Phase0_1_Run_Checklist.md**
- **@docs/Test_Evaluation_Master_Plan.md** — Test & Evaluation Master Plan (Contract/Unit/Integration·실행 순서·RTM·Production Gate, TVP 연계)
- **@docs/Implementation_Priority_Roadmap.md** — 추진계획·우선순위 로드맵 (Phase 0-2 → 1 → 2 → 3, 중요도/긴급도)
- **@docs/Delegation_of_Authority_and_Standing_Order.md** — 위임 및 상시 지시 (책임·권한 위임, 멈추지 말고 추진계획대로 진행)
- **@docs/SE_Process_Module_DB_Warroom_Mapping_Table.md** — 전체 프로세스·모듈·DB·Warroom 매핑
- **@docs/Process_Alignment_Detailed_Design_and_Check_Plan.md** — 프로세스 정합 세부설계(Module/Schema/Signal/UI) 및 점검계획(Alignment·Sync·통합·SE 문서별)
- **@docs/한국_뉴스_기업정보_소스_정리.md** — 한국 뉴스·공시·API Key 소스 (v3)
- **@docs/합참_SRC_각군_LLM_RR_점검_결과.md** — JCS/SRC/각군 LLM R&R 점검 (v3)
- **@docs/외부기관_목록_및_통신점검.md** — 외부기관 종합·통신점검·저장소 (v3)
- **@docs/외부기관_모듈_LLM_프로세스결과_DB_매칭테이블.md** — 외부기관·모듈·LLM 산출·DB 1:1 매칭
- **@docs/입력DB_프로세싱_출력DB_대시보드_매칭테이블.md** — 입력 DB → 프로세싱(모듈/LLM) → 출력 DB·Dashboard 매칭
- **@docs/Cursor_SOO_Phase0_1.md** — Cursor 1페이지 SOO (Phase 0-1 명령·검증·산출물)
- **@docs/Cursor_Guardrails_SE_Enforcement.md** — 3원칙 검증·SSOT·전략→파라미터·LLM 격리
- **@docs/SE_Complete_Alignment_Structure_Math_Gate_LLM.md** — SE-39/50/64/58/65 완전 정합 (Regime·Gate·Wide Stop·LLM Mesh·Directory Lock)
- **@docs/전략_파라미터_매핑_규격.md** — 전략 서술 ↔ 엔진 입력/조건식 매핑
- **@docs/CoreForce_Structural_Trend_Mapping.md** — Core Force 문장→입력/출력 dict→snapshot_key (Cursor 구현용)

## 계약 테스트 (설계 위반 시 빌드 실패)

- `test_one_cycle_produces_six_snapshot_keys` — 엔진 1사이클 후 6종 키·refresh_rate_sec·generated_at 존재 (SSOT: snapshot_keys)
- `test_ui_never_calls_compute` — UI/API에서 engines import 금지 (DB-Only Read)
- `test_single_write_path_only` — DB 쓰기는 repo 모듈만 허용
- `test_api_only_reads_engine_snapshot_no_forbidden_tables` — API에서 ext_event_raw, order_log 직접 조회 금지
- `test_engines_no_sqlalchemy_or_db` — engines/에서 SQLAlchemy import 금지 (Strict Engine Purity)

## Guardrails 요약

- **DB-first 스키마**: engine_snapshot 레코드에 payload + meta(generated_at, source_name, refresh_rate_sec, freshness_status) 필수. UI는 DB meta 그대로 표출.
- **Force 스냅샷 키 계약**: 전술 = 스냅샷 판정값. 예: core_policy_state, promotion_queue, industry_bias_state. (Cursor_Guardrails_SE_Enforcement.md B'', B'')
- **Core vs SE 정합 3조항**: (1) 구조추세 조건을 정량 스냅샷으로 기록 (2) Wide Stop은 Pre-Trade/Risk Gate (3) Swing→Core 승격은 AAR/DB 추적, 메모리 카운트 금지. (CoreForce_Structural_Trend_Mapping.md §9)
- **LLM 최소 4요구**: role 라우팅, llm_status에 provider별 지표, degradation→LKS+Freeze, incident/command_log 로깅. (LLM_Staffing_Fallback_Plan.md)
