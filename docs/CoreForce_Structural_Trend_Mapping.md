# Core Force → Snapshot 스키마 매핑 문서 (Cursor 구현용)

아래는 Cursor가 그대로 엔진에 구현하도록 설계된  
**문장 → 입력 dict → 출력 dict → snapshot_key** 매핑 규격입니다.

---

## 1. 목적

Core Force 평시 운용 교리를  
**SE-64 Snapshot 기반 아키텍처**에 정합되도록  
엔진 **순수 함수(dict→dict)** 형태로 고정한다.

---

## 2. 입력 Snapshot (Read-Only Source)

Core Engine은 **DB를 직접 읽지 않는다**.  
engine_worker가 다음 dict를 구성하여 전달한다.

```python
core_input = {
    "regime_current": {...},          # Snapshot
    "battlefield_state": {...},       # MA, RSI, Volume 등 계산 완료 데이터
    "allocation_matrix": {...},
    "fleet_budget_snapshot": {...},
    "risk_guard": {...},
    "macro_context": {...}
}
```

---

## 3. 전략 규칙 → 수학 조건 매핑

### Rule 1: 구조적 추세 유지

**전략 문장**  
120MA 기울기 양(+) & 60MA > 120MA 유지 시 포지션 유지

**엔진 수학 조건**

```python
trend_ok = (
    battlefield_state["ma60"] > battlefield_state["ma120"]
    and battlefield_state["ma120_slope"] > 0
)
```

**출력**

```python
{
    "structural_trend_status": "ACTIVE" if trend_ok else "BROKEN"
}
```

---

### Rule 2: 저회전 (Low Turnover)

**전략 문장**  
불필요한 교전 금지

**엔진 조건**

```python
if trend_ok:
    trade_signal = "HOLD"
else:
    trade_signal = "REVIEW"
```

⚠ **실제 매매 실행은 gate 레이어에서 결정** (엔진은 신호만 반환)

---

### Rule 3: 복리 확대 (CoreWeight 자동 증가)

**입력**  
`portfolio_growth_rate`

**규칙**

```python
if portfolio_growth_rate > threshold:
    core_weight_adjustment = +delta
else:
    core_weight_adjustment = 0
```

**출력**

```python
{
    "core_weight_delta": core_weight_adjustment
}
```

---

### Rule 4: Wide Stop

**전략 문장**  
120MA 이탈 시 구조 붕괴 판단

**조건**

```python
if price < battlefield_state["ma120"]:
    structural_trend_status = "BROKEN"
```

---

### Rule 5: Swing → Core 승격

**입력**  
`swing_success_count`, `relative_strength_percentile`, `regime_alignment`

**조건**

```python
promotion_candidate = (
    swing_success_count >= 3
    and relative_strength_percentile >= 80
    and regime_alignment is True
)
```

**출력**

```python
{
    "promotion_list": [...]
}
```

---

## 4. 최종 엔진 출력 dict

```python
core_output = {
    "structural_trend_status": "...",
    "trade_signal": "...",
    "core_weight_delta": ...,
    "promotion_list": [...],
    "meta": {
        "source_name": "core_engine",
        "refresh_rate_sec": 3600
    }
}
```

---

## 5. Snapshot 기록 (Single Write Path)

engine_worker에서만 기록. **core/snapshot_repo.py** 경유.

```python
insert_snapshot_sync(
    db,
    snapshot_key="core_force_state",
    snapshot_data=core_output,
    freshness_status="GREEN",
    source_name="core_engine",
    refresh_rate_sec=3600,
)
```

**구현 시**: `core_force_state`를 `backend/app/core/snapshot_keys.py`의 `ALLOWED_SNAPSHOT_KEYS`에 추가하여 API가 조회 가능하게 한다.

---

## 6. 절대 금지

- 엔진에서 **DB 접근** 금지
- 엔진에서 **매매 실행** 금지
- **API에서 계산** 금지
- **snapshot_repo 외** INSERT 금지

---

## 7. UI 매핑 (Warroom)

| UI 패널       | snapshot_key      |
|---------------|-------------------|
| Core Status   | core_force_state  |
| Structural Trend | regime_current |
| Allocation    | allocation_matrix |
| Risk          | risk_guard        |

---

## 8. 결과

Core Force 전략은 다음 흐름으로 고정된다.

**자연어 교리** → **수학 조건** → **엔진 순수 함수** → **snapshot 저장** → **UI read-only**

---

## 9. Core Force vs SE 문서 정합 (코딩 시 필수 3조항)

Core 전략을 SE와 100% 맞추려면 아래 3가지를 **스냅샷 키/게이트**로 명시해야 한다.

| # | 요구사항 | 구현 위치 |
|---|----------|-----------|
| 1 | **구조적 추세 유지 조건**을 **정량 판정 결과**로 스냅샷에 기록 | `engine_snapshot`: 예) `core_trend_ok`, `ma60_over_ma120`, `ma120_slope_positive` 등 판정 결과를 `core_force_state`(또는 `core_policy_state`) snapshot_data에 포함 |
| 2 | **Wide Stop / 구조 붕괴 청산** 조건을 **Pre-Trade Gate·Risk Gate**로 내림 | 단순 전략 설명이 아니라, 모드/리트랙트/이머전시와 함께 **우선순위가 있는 규칙**으로 gates/에서 적용 |
| 3 | **Swing→Core 승격** 로직은 “성공 3회” 등 조건을 **AAR/성과 테이블(또는 snapshot_data)**로 추적 | DB-first 원칙: **메모리상 카운트 금지**. `swing_success_count` 등은 DB 또는 snapshot에 기록·조회하여 사용 |

---

*Ref: 전략_파라미터_매핑_규격.md, Cursor_Guardrails_SE_Enforcement.md, SE_Complete_Alignment_Structure_Math_Gate_LLM.md (SE-39/50/64), 07_Fleet_Execution_Spec.md*
