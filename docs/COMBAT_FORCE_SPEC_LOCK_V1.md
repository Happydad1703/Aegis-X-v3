# Core / Swing / Strike — I/O 계약 완전 잠금 (Spec Lock v1.0)

문서화 + 코드 계약 + 테스트 기준. Cursor 임의 구현 방지용.

---

## 🔵 Core Engine Contract

**입력 (dict)**

| 키 | 타입 | 설명 |
|----|------|------|
| regime | str | Goldilocks \| Bull \| Crisis \| Tapering \| Sideways |
| crisis_prob | float | 위기 확률 0~1 |
| price | float | 현재가 |
| ma60 | float | 60일 이평 |
| ma120 | float | 120일 이평 |
| ma120_slope | float | 120일 이평 기울기 |
| relative_strength_rank | float | 상대강도 순위 (0~1, 낮을수록 강함) |
| current_position | float | 현재 포지션 비중 |

**출력 (dict)**

| 키 | 타입 | 설명 |
|----|------|------|
| action | "HOLD" \| "ENTER" \| "EXIT" | 행동 |
| target_weight | float | 목표 비중 |
| stop_loss | float | 손절 비율 (wide structural) |
| reason | str | 사유 |

**수식 Lock**

- **ENTER** iff: regime ∈ {Goldilocks, Bull} AND ma60 > ma120 AND ma120_slope > 0 AND relative_strength_rank ≤ 0.20
- **EXIT** iff: ma60 < ma120 OR regime == "Crisis"
- **stop_loss** = -0.20 (고정)

---

## 🟡 Swing Engine Contract

**입력 (dict)**

| 키 | 타입 |
|----|------|
| regime | str |
| price | float |
| ma20 | float |
| ma60 | float |
| volume_ratio | float |
| breakout_10d | bool |
| holding_days | int |

**출력 (dict)**

| 키 | 타입 |
|----|------|
| signal | "BUY" \| "SELL" \| "HOLD" |
| position_size | float |
| stop_loss | float |
| max_holding_days | int |

**수식 Lock**

- **BUY**: regime ∈ {Bull, Sideways} AND ma20 > ma60 AND breakout_10d == True AND volume_ratio ≥ 1.2
- **SELL**: ma20 < ma60 OR holding_days > 15 OR 손절 -8%

---

## 🔴 Strike Engine Contract

**입력 (dict)**

| 키 | 타입 |
|----|------|
| regime | str |
| price | float |
| vol_spike | float |
| z_score | float |
| holding_days | int |

**출력 (dict)**

| 키 | 타입 |
|----|------|
| entry | bool |
| exit | bool |
| tp | float |
| sl | float |

**수식 Lock**

- **entry**: regime != "Crisis" AND vol_spike ≥ 1.5 AND z_score ≤ -2
- **exit**: +5% TP OR -3% SL OR holding_days ≥ 3
- tp = 0.05, sl = -0.03

---

## 🛡 Gate 강제 (pre_trade / gate_chain)

- if emergency_stop: return BLOCK
- if retract: reduce_allocation()
- if freshness_status != "GREEN": return BLOCK
- if risk_guard dd < -0.10: block_strike()

---

## 🧪 필수 자동 검증 테스트

- test_engine_purity: engines 모듈에 sqlalchemy/kis 미포함
- test_required_snapshot_keys: engine_heartbeat, operation_mode, comm_health, llm_status, regime_current, risk_guard 존재
- test_core_enter_logic: Bull, ma60>ma120, ma120_slope>0, RS≤20% → action=="ENTER"
- test_swing_buy_logic: Bull, ma20>ma60, breakout_10d, volume_ratio≥1.2 → signal=="BUY"
- test_strike_entry_logic: regime!="Crisis", vol_spike≥1.5, z_score≤-2 → entry==True

---

## ⚠ 엔진은 주문 전송하지 않음

- Core/Swing/Strike는 **시그널/타겟/손절 규칙**만 산출.
- 실제 주문은 **Execution Layer** (paper_executor / kis_executor)만 수행.
- KIS 통신은 **execution/kis_executor.py** 단일 창구.
