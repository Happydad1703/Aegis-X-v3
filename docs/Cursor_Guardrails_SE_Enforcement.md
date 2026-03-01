# Cursor Guardrails — SE 철학/알고리즘 코드 강제 (Aegis-X v3)

**목적**: “전략 서술(개념)”이 “코딩 규격(강제 룰)”으로 내려갈 때 빠지는 고리를 막고, Cursor가 SE를 **그대로** 구현하도록 검증·잠금을 건다.

---

## A. 3원칙을 ‘규칙’이 아닌 ‘검증(Tests/Lint)’으로 강제

| 원칙 | 금지 사항 | 강제 방법 |
|------|------------|-----------|
| **DB-Only Read** | API에서 engine_snapshot 외 테이블(ext_event_raw, order_log 등) 직접 조회 | `test_contract_api_db_only_read.py`: api/·main.py에 ext_event_raw, order_log 문자열 금지 |
| **Strict Engine Purity** | engines/ 내 DB 세션·SQLAlchemy·외부 I/O | `test_contract_ui_never_calls_compute.py`: api/·main에서 engines import 금지; engines/ 내 forbidden import는 internal_simulation 또는 별도 스캔 |
| **Single Write Path** | snapshot_repo 외에서 INSERT engine_snapshot | `test_contract_single_write_path.py`: INSERT/UPDATE는 지정 repo 모듈만 허용 |

**실행**  
- `pytest backend/tests/test_contract_*.py`  
- (선택) `python scripts/internal_simulation.py` — 규칙 위반 스캔  
- PR 체크리스트: 위 테스트 통과 후 커밋

---

## B. Snapshot Key 단일 소스(SSOT) 고정

- **파일**: `backend/app/core/snapshot_keys.py`
- **내용**: `ALLOWED_SNAPSHOT_KEYS` (frozenset), `is_allowed_snapshot_key()`, `get_required_snapshot_keys_for_cycle()`
- **규칙**: 문서(카탈로그)와 코드에 키를 중복 정의하지 않는다. API·engine_worker·테스트는 이 모듈만 참조.
- **효과**: API는 화이트리스트 밖 키를 절대 반환하지 않음.

---

## B'. DB-First를 “스키마”로 강제

- **engine_snapshot** 레코드에는 payload + meta가 **항상** 있어야 함:
  - `snapshot_data` (JSONB), `generated_at`, `source_name`, `refresh_rate_sec`, `freshness_status`
- Warroom이 요구한 **실명제 + timestamp + refresh metadata**는  
  → UI에서 만들지 말고 **DB에 있는 meta를 그대로 표출**하는 계약으로 고정.

---

## B''. Force 조직/전술을 “스냅샷 키 계약”으로 내리기

전술을 코드 안에서 즉흥 계산하지 않도록, 아래 키 계약으로 고정한다.  
**전략 = 스냅샷에 기록된 판정값**, UI/API는 이를 **보여주기만** 한다.

| 스냅샷 키(예시) | 용도 |
|-----------------|------|
| `core_policy_state` | Core 판정 결과: trend_ok, wide_stop_state, bias_ok, promote_candidates[] |
| `promotion_queue` | Swing 승격 후보 |
| `industry_bias_state` | STRATCOM 산업 bias / RS Top 20% 여부 |

- 구현 시 `snapshot_keys.ALLOWED_SNAPSHOT_KEYS`에 추가하고, 엔진은 dict→dict로 판정 결과만 산출 후 snapshot_repo로 기록.

---

## C. “전략 문장(자연어)” ↔ “엔진 파라미터(수치/규칙)” 변환 규격

- **문서**: `docs/전략_파라미터_매핑_규격.md`
- **목적**: “120MA 기울기 +, 60MA > 120MA면 유지” 같은 전략 서술이 **어디에서** 어떤 **입력 dict/조건식**으로 내려가는지 고정.
- **규칙**  
  - 조건 평가 → **engines**(regime_engine/core_engine)에서 계산 → snapshot 기록 → UI/API는 **읽기만**.  
  - API에서 계산 금지(DB-Only Read 위반).  
  - 엔진이 DB 직접 읽기 금지(순수 함수).  
  - 스냅샷 저장은 **snapshot_repo** 경유만(Single Write Path).

---

## D. LLM 스태핑을 “엔진/게이트 레벨”로 격리

- **원칙**: “LLM은 지능을 빌려쓰되, **생존은 하드로직**.”
- **llm_gateway**(또는 동등 모듈)  
  - 호출 실패 시 **결정(Decision)을 만들려 하지 않음**.  
  - 기존 DB의 **Last-Known Strategy** 스냅샷 유지 + **Execution Freeze** 등 보수적 ROE로 전환.  
- **격리**: LLM 장애는 “전략 논의(JCS/STRATCOM/AAR)”가 아니라 **시스템 생존(ROE)** 문제로, 게이트·실행 레이어에서 처리.

---

## 괴리 발생 대표 지점 (Core Force 예시)

| 질문 | 정답 (코드 위치) |
|------|------------------|
| 120MA/60MA 조건은 어디에서 평가하나? | **engines**(core_engine/regime_engine)에서 계산 → snapshot 기록 → UI/API는 읽기만 |
| “저회전(거래 억제)”는 어디에서 강제하나? | **gates**(pre_trade_gate, risk_gate)에서 ROE로 강제 |
| “승격(Swing→Core)”은 어디에서 결정하나? | 엔진에서 승격 후보를 **스냅샷**으로 산출; 실행은 gate/command로 분리(직접 매매로 이어지면 위험) |

---

## 참조

- **SE 완전 정합 (Structure + Math + Gate + LLM)**: `docs/SE_Complete_Alignment_Structure_Math_Gate_LLM.md` — SE-39/50/64/58/65 모듈 단위 정합, regime_current·Wide Stop·LLM Mesh·Directory Lock.
- **SOO (1페이지 명령문)**: `docs/Cursor_SOO_Phase0_1.md`
- **전략→파라미터 매핑**: `docs/전략_파라미터_매핑_규격.md`
- **Core Force → Snapshot 스키마**: `docs/CoreForce_Structural_Trend_Mapping.md` — Cursor 구현용 입력/출력 dict, Rule 1~5, core_force_state, UI 매핑.
- **Hard Lock**: `docs/Cursor_Developer_Mode_Hard_Lock.md`
