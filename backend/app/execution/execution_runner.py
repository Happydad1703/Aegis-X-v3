# execution/execution_runner.py — Gate-first flow. Run gate_chain then dispatch to paper or KIS. FULL COMBAT LOCK.

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.gates.gate_chain import run_gate_chain
from backend.app.execution.paper_executor import execute_paper_from_intent_sync
from backend.app.execution.kis_executor import execute_kis_from_intent_sync, _current_mode


def run_execution_flow_sync(db: Session, intent: dict) -> tuple[bool, str, str]:
    """
    Run gate chain; if PASS, execute via paper or KIS (by mode). If BLOCK, do not write order.
    Returns: (executed, result_message, mode_used).
    """
    allow, failed_gate, reasons = run_gate_chain(db, context=None)
    if not allow:
        return False, f"BLOCKED:{failed_gate}", ""

    mode = _current_mode(db)
    if mode.upper() in ("PILOT", "FULL_LIVE", "LIVE"):
        order_id = execute_kis_from_intent_sync(db, intent)
        return order_id is not None, f"KIS order_id={order_id}" if order_id else "KIS skipped", mode
    # PAPER or BACKTEST (BACKTEST already blocked by gate; so PAPER here)
    execute_paper_from_intent_sync(db, intent, mode=mode or "PAPER")
    return True, "PAPER_FILLED", mode or "PAPER"
