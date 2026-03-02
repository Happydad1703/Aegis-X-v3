# Execution Rules of Engagement (ROE) — FULL COMBAT LOCK

KIS is the **only** execution gateway. No US market in this phase; KR scope only.

---

## 1. Who may send orders

- **Only** the execution layer: `execution/paper_executor.py` (PAPER), `execution/kis_executor.py` (KIS).
- Engines **never** call KIS or write order_log directly. They produce signals/intents only (P2, P3).

---

## 2. Gate precedence (enforced order)

Execution is allowed **only if** all of the following pass, in order:

1. **EmergencyStop** — not active (system_config)
2. **Retract** — not active
3. **LLMBlackout** — not active (Execution Freeze)
4. **Session** — not OFF (Follow-the-Sun)
5. **Mode** — not BACKTEST (BACKTEST → orders disabled)
6. **Risk** — risk_guard / USD-FX within limits
7. **Freshness** — critical snapshots within age limit
8. **Pre-Trade** — structural_trend OK (core_force_state action ≠ EXIT blocking)
9. **Strategy** — pass

First failure → BLOCK; no order sent. Implemented in `gates/gate_chain.run_gate_chain(db)`.

---

## 3. Mode vs execution path

| Mode | Orders | Execution path |
|------|--------|----------------|
| BACKTEST | Disabled | Gate blocks (mode_gate) |
| PAPER | Simulated | paper_executor → order_log (PAPER_FILLED) |
| PILOT / FULL_LIVE | Real (when gate PASS) | kis_executor → KIS API → order_log (PENDING → ACK/FILLED/REJECTED) |

Never send live orders unless Mode is PILOT or FULL_LIVE and all gates pass.

---

## 4. Order state transitions (order_log)

Allowed **initial** status on insert: `PENDING`, `PAPER_FILLED`, `REJECTED`, `ERROR`.

Valid transitions (enforced in `core/order_repo.update_order_status_sync`):

- PENDING → ACK | PARTIAL_FILL | FILLED | REJECTED | CANCELLED | ERROR
- ACK → PARTIAL_FILL | FILLED | REJECTED | CANCELLED | ERROR
- PARTIAL_FILL → FILLED | CANCELLED | ERROR
- FILLED | REJECTED | CANCELLED | ERROR | PAPER_FILLED → (terminal, no transition)

---

## 5. KIS executor behavior

- **Retry**: up to 3 attempts with exponential backoff (1s, 2s, 4s).
- **Rate limit**: caller responsibility; executor does not throttle.
- **Failure**: on final failure, order status set to ERROR; incident_log written via incident_repo.
- **KR only**: no US symbols or venues in this phase.

---

## 6. Paper executor

- Writes one row to order_log with `execution_status=PAPER_FILLED` via order_repo only.
- No KIS call. Optional push_event for notifications.

---

## 7. Run flow (recommended)

1. Build order intent from engine outputs (worker or strategy).
2. Call `run_gate_chain(db)`. If not allow → log and stop.
3. If allow: call `run_execution_flow_sync(db, intent)` → dispatches to paper or KIS by mode.
