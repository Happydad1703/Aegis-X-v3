# Aegis-X SE 완전 정합 설계 (Structure + Math + Gate + LLM)

3원칙, Snapshot Flow, Core Force 교리, LLM Mesh를 **SE-39 / SE-50 / SE-64 / SE-65** 기준으로 모듈 단위까지 정렬한 정합 문서.

---

## 1. SE-39 (Regime 수학) ↔ Snapshot 계약

### 규칙

- Regime 판단은 **수학식 기반**
- **엔진 순수 함수** (dict in → dict out)
- 결과는 **snapshot 저장**
- **UI는 읽기만**

### 구조

```
engine_worker
  └─ regime_engine(dict in → dict out)
        └─ snapshot_repo.insert_snapshot("regime_current")
```

### Snapshot Contract — `regime_current`

`regime_current.snapshot_data` MUST contain:

| 필드 | 용도 |
|------|------|
| `regime_label` | 레짐 식별 |
| `crisis_probability` | 위기 확률 |
| `trend_score` | 추세 점수 |
| `volatility_state` | 변동성 상태 |
| `confidence_score` | 신뢰도 |
| `generated_inputs_hash` | 재현성 확보용 |

- ❗ **Regime 계산을 API에서 하면 SE-39 위반**
- ❗ **DB 직접 읽으면 Engine Purity 위반**

---

## 2. SE-50 (Pre-Trade Gate) ↔ Wide Stop 통합

Core Force **Wide Stop**는 전략이 아니라 **Gate 영역**이다.

### 우선순위 (SE 철학과 일치)

1. EmergencyStop  
2. → Retract  
3. → Mode Override  
4. → Risk Gate  
5. → Pre-Trade Gate  
6. → Strategy Signal  

### Wide Stop 통합 방식

- **Core Engine**이 `structural_trend_status = ACTIVE | BROKEN` 를 **snapshot**에 기록
- **Pre-Trade Gate**가:

  ```text
  if structural_trend_status == "BROKEN":
      block_trade()
  ```

즉,

- **엔진** = "상태 판단"
- **Gate** = "행동 허용/차단"

**이 분리가 깨지면 SE-50 위반.**

---

## 3. SE-64 (DB/Snapshot/Worker) ↔ 완전 정합

SE-64가 강제하는 것:

- 모든 상태는 **DB에 저장**
- **Worker만** snapshot 생성
- **API는 read-only**

현재 구조는 정합.

### 필수 Snapshot Key (최소)

- `engine_heartbeat`
- `llm_status`
- `comm_health`
- `regime_current`
- `risk_guard`
- `operation_mode`

**없으면 SE-64 불완전.**  
→ 코드 SSOT: `backend/app/core/snapshot_keys.py`

---

## 4. SE-58 + LLM Mesh 정합

LLM은 **결정권자가 아니라 보조 분석자**이다.

### 정합 구조

```
engine_worker
   ├─ collect DB snapshots
   ├─ llm_gateway (Multi-provider)
   │      ├─ Primary
   │      ├─ Secondary
   │      └─ Fallback (LKS)
   └─ pass result to engines
```

- **엔진은 LLM 호출 금지.** (엔진 순수 함수 유지)

### Blackout Ladder (수학적 단계)

1. Primary timeout  
2. → Secondary timeout  
3. → Tertiary timeout  
4. → LKS load from DB  
5. → Gate → Execution Freeze  
6. → incident_log 기록  

**LLM 실패가 시스템 중단으로 이어지면 SE 철학 위반.**

---

## 5. SE-65 Directory Lock 정합 점검

| 계층 | 허용 | 금지 |
|------|------|------|
| **engines** | 수학 계산 | DB import |
| **gates** | ROE 판단 | 전략 계산 |
| **workers** | snapshot 생성 | 매매 실행 |
| **execution** | 주문 실행 | 전략 판단 |
| **api** | snapshot read | 계산 |

**현재 설계와 충돌 없음.**

---

## 6. Core Force 전략 최종 판정

당신의 Core Force 교리:

- 120MA 구조 추세 유지
- 저회전
- Wide Stop
- RS 상위 20%
- Swing → Core 승격

→ **SE-39 / SE-50 / SE-64와 충돌 없음**  
→ 단, **승격 조건은 AAR/성과 DB 기반**으로 계산해야 정합 (메모리 카운트 금지).

---

## 7. 지금 시스템은 어디까지 왔는가?

| 항목 | 상태 |
|------|------|
| **아키텍처 안정성** | 매우 높음 |
| **철학 정합성** | 일치 |
| **위험 구간** | LLM 계층이 engines 안으로 들어갈 경우 |

---

*Ref: 39_Regime_Engine_Mathematical_Spec, 50_Pre_Trade_Gate_Spec, 64_Phase0_1_DB_and_MinWorker, 65_Final_Directory_Architecture_Lock, Cursor_Guardrails_SE_Enforcement.md, CoreForce_Structural_Trend_Mapping.md, LLM_Staffing_Fallback_Plan.md*
