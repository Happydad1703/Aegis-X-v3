# core/order_state.py — Order log state transition enforcement (FULL COMBAT SYSTEM LOCK).
# Valid statuses and allowed transitions only. No illegal state changes.

from __future__ import annotations

# Allowed execution_status values (order_log)
ORDER_STATUS_PENDING = "PENDING"
ORDER_STATUS_ACK = "ACK"
ORDER_STATUS_PARTIAL_FILL = "PARTIAL_FILL"
ORDER_STATUS_FILLED = "FILLED"
ORDER_STATUS_REJECTED = "REJECTED"
ORDER_STATUS_CANCELLED = "CANCELLED"
ORDER_STATUS_ERROR = "ERROR"
ORDER_STATUS_PAPER_FILLED = "PAPER_FILLED"  # Paper mode: simulated fill in one step

ALL_ORDER_STATUSES = frozenset({
    ORDER_STATUS_PENDING,
    ORDER_STATUS_ACK,
    ORDER_STATUS_PARTIAL_FILL,
    ORDER_STATUS_FILLED,
    ORDER_STATUS_REJECTED,
    ORDER_STATUS_CANCELLED,
    ORDER_STATUS_ERROR,
    ORDER_STATUS_PAPER_FILLED,
})

# Allowed initial status on insert (first write)
ALLOWED_INITIAL_STATUSES = frozenset({
    ORDER_STATUS_PENDING,      # Live: send to KIS, then update to ACK/FILLED/REJECTED
    ORDER_STATUS_PAPER_FILLED, # Paper: simulated fill immediately
    ORDER_STATUS_REJECTED,     # Gate blocked or pre-check failed
    ORDER_STATUS_ERROR,        # Executor error before send
})

# Valid transitions: from_status -> set(of to_status)
VALID_TRANSITIONS = {
    ORDER_STATUS_PENDING: {ORDER_STATUS_ACK, ORDER_STATUS_PARTIAL_FILL, ORDER_STATUS_FILLED, ORDER_STATUS_REJECTED, ORDER_STATUS_CANCELLED, ORDER_STATUS_ERROR},
    ORDER_STATUS_ACK: {ORDER_STATUS_PARTIAL_FILL, ORDER_STATUS_FILLED, ORDER_STATUS_REJECTED, ORDER_STATUS_CANCELLED, ORDER_STATUS_ERROR},
    ORDER_STATUS_PARTIAL_FILL: {ORDER_STATUS_FILLED, ORDER_STATUS_CANCELLED, ORDER_STATUS_ERROR},
    ORDER_STATUS_FILLED: set(),   # terminal
    ORDER_STATUS_REJECTED: set(), # terminal
    ORDER_STATUS_CANCELLED: set(),# terminal
    ORDER_STATUS_ERROR: set(),   # terminal
    ORDER_STATUS_PAPER_FILLED: set(),  # terminal (paper)
}


def is_allowed_initial_status(status: str) -> bool:
    """True if status is allowed on insert_order."""
    return status in ALLOWED_INITIAL_STATUSES


def validate_transition(from_status: str, to_status: str) -> bool:
    """True if transition from_status -> to_status is allowed."""
    if from_status not in VALID_TRANSITIONS:
        return False
    return to_status in VALID_TRANSITIONS[from_status]
