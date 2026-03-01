# 합참·SRC·각군 참모 R&R별 LLM 점검 결과 (Aegis-X v3)

**목적**: 개별 LLM 통신 점검 후, 합동참모본부(JCS)·전략사령부(STRATCOM)·자원/리스크(SRC)·각군(Force)의 역할(R&R)에 따른 LLM 사용 경로 및 점검 방법을 정리한다.

---

## 1. 개별 LLM 통신 점검 (선행 수행)

**실행**: `python scripts/check_comm.py`

| LLM (Provider) | 점검 결과 | v3에서 담당 역할 (LLM_Staffing_Fallback_Plan 기준) |
|----------------|-----------|------------------------------------------------------|
| **OpenAI** | OK / SKIP / FAIL | JCS(합참)·Regime/위기판단, 고추론 Primary |
| **Gemini** | OK / OK(rate limited) / SKIP / FAIL | JCS Secondary, STRATCOM 장문맥 보조 |
| **Anthropic (Claude)** | (check_comm 미포함 시 수동 점검) | STRATCOM Primary, JCS Secondary |
| **DeepSeek** | (check_comm 미포함 시 수동 점검) | Strike Force 등 경량/비용 효율 |

- **전투 준비**: DB + 최소 1개 LLM 성공 시 "전투 준비 완료".  
- v3: 키는 **Windows 11 환경변수**만 사용. `backend/app/core/env_keys.py`에서 조회.

---

## 2. R&R ↔ LLM 매핑 (v3 설계)

| 조직/보직 | Primary LLM | Secondary | Tertiary | 임무(요약) |
|-----------|-------------|-----------|----------|------------|
| **JCS(합참/CIC)** | 고추론(OpenAI 등) | 대체 고추론(Claude 등) | 로컬 규칙/룰엔진 | Regime/위기판단, 모드전환, E-Stop/Retract 결심 |
| **STRATCOM(전략)** | 장문맥/분석(Claude 등) | 대체 장문맥(Gemini 등) | 로컬 규칙 | 산업 Bias/테마/장기 가드레일 |
| **SRC(자원/리스크)** | 계산/정책 모델 | 대체 | 로컬 Safe Matrix | 자원배분, 노출량, 한도/레버리지 규율 — **LLM 없이 로직만** 가능 |
| **Core Force** | 펀더멘털/구조추세 | 대체 | 룰기반 | 저회전 복리/추세 유지 |
| **Swing Force** | 패턴/수급 모델 | 대체 | 룰기반 | 중단기 타점/후퇴/익절 |
| **Strike Force** | 초단기/민첩(DeepSeek 등) | 대체 경량 | 룰기반 즉시청산 | 지연=손실 → 보수적 즉시정리 |
| **Reserve** | 로컬 룰엔진 | 경량 요약 | N/A | 블랙아웃 시 동결·청산·보고 |

※ 모델명은 설정 테이블(DB/설정)로 관리. 코드에 모델명 하드코딩 금지.

---

## 3. 기능 수행 경로 점검 (v3)

점검 항목:

1. **통신 점검**: `python scripts/check_comm.py` — FRED, OpenAI, Gemini, KIS 순으로 OK/SKIP/FAIL 출력.
2. **엔진 순수성**: `engines/`는 DB/HTTP/LLM 직접 호출 금지. LLM 호출은 **gates** 또는 **intelligence/llm_gateway** 등 전용 레이어에서만.
3. **Snapshot 소비**: Warroom/CIC는 `engine_snapshot`만 조회. `llm_status` 스냅샷으로 LLM 가용성 표시 (Phase 4 연동 시).
4. **Safety 우선순위**: EmergencyStop > Retract > Mode > Strategy. LLM 실패 시 Tertiary(로컬 규칙) 또는 Freeze/Reduce.

v3에 **check_jcs_llm_rr.py** 같은 R&R 전용 스크립트가 있으면, 동일하게 “역할별 → Task → provider·모델” 일치 여부를 점검하면 됨.

---

## 4. 수행 결과 확인 방법 (v3)

| 역할 | 수행 경로 | 결과 확인 |
|------|-----------|-----------|
| JCS | macro_context·ext_event_raw → Regime 엔진(입력) → (LLM 사용 시 llm_gateway) → regime_current 스냅샷 | `GET /api/snapshot/regime_current`, Warroom Regime 카드 |
| STRATCOM | regime_current·battlefield → Allocation/Fleet Budget 엔진 → allocation_matrix, fleet_budget_snapshot | `GET /api/snapshot/allocation_matrix`, Allocation 패널 |
| SRC | allocation·risk 로직 (LLM 없음) → risk_guard 등 스냅샷 | `GET /api/snapshot/risk_guard`, Risk Control |
| Fleet | JCS/STRATCOM 스냅샷만 참조, LLM 직접 호출 없음 | Orders & Execution, Fleet 페이지 |
| LLM 상태 | Health Check → llm_status 스냅샷 (Phase 4) | `GET /api/snapshot/llm_status`, Header |

---

## 5. 실행 순서 요약 (v3)

1. **개별 LLM·API 통신 점검**: `python scripts/check_comm.py`
2. (Phase 4 이후) **R&R별 LLM 경로 점검**: 예) `scripts/check_jcs_llm_rr.py` 또는 동등 스크립트
3. **DB·스냅샷 확인**: `GET /api/health`, `GET /api/snapshot/{key}` — engine_heartbeat, comm_health, regime_current, operation_mode, llm_status, risk_guard

---

## 6. 참조 문서

- **LLM 스태핑/폴백**: `docs/LLM_Staffing_Fallback_Plan.md`
- **환경변수**: `docs/ENV_Windows11_API_Keys.md`, `backend/app/core/env_keys.py`
- **v2 R&R 점검**: `AEGIS-X_v2/docs/합참_SRC_각군_LLM_RR_점검_결과.md`
