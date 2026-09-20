#!/usr/bin/env python3
"""
control_plane/receipt_provenance.py
===================================

Purpose:
    Human-only receipt operations for auth-ciba-increment-b T15 (issue #639), the regression for the
    2026-09-19 incident where an agent recorded a review-skip receipt on the human's behalf.
    A review skip and the revocation of a receipt are decisions only a human at a terminal may make:
    both refuse without a TTY, require the human to type a confirmation, force the actor to `human`,
    and record provenance `human-interactive` in the append-only `receipt_audit` trail.
    (`--human-confirmed` and `--actor human` on the command line prove nothing about who typed them.)

Key Input Dependencies:
    - control_plane/adapters.py (verification_receipts provenance columns, receipt_audit table)
    - agent_control.py ControlPlane (record_review_skip); a real terminal for the confirmation

Key Functions:
    - record_human_skip()   -- interactive, human-only review-skip receipt
    - invalidate_receipt()  -- interactive, human-only revocation; the receipt stops satisfying gates
    - receipt_history()     -- read-only audit trail rows for a task
    - ReceiptError          -- refusal (no terminal, wrong confirmation, unknown receipt)
"""

import os
import sqlite3
import sys
from typing import Any, Callable, Dict, List, Optional

from control_plane.isolation_check import DEFAULT_AGENT_NAME, _resolve_agent_identity


class ReceiptError(Exception):
    """A human-only receipt operation was refused."""


def _is_tty() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def _require_human(tty_fn: Optional[Callable[[], bool]], what: str, agent_uid: Optional[int]) -> None:
    """Refuse without a terminal AND when running as the agent account (a pty alone proves nothing: an
    agent can allocate one). Same-account agents remain a documented residual (decision D4)."""
    resolved = agent_uid if agent_uid is not None else _resolve_agent_identity(DEFAULT_AGENT_NAME, None, None)[0]
    if resolved is not None and hasattr(os, "geteuid") and os.geteuid() == resolved:
        raise ReceiptError(f"{what} is a human decision and cannot be made from the agent account; run it as yourself, the human.")
    _require_terminal(tty_fn, what)


def _require_terminal(tty_fn: Optional[Callable[[], bool]], what: str) -> None:
    if not (tty_fn or _is_tty)():
        raise ReceiptError(
            f"{what} is a human decision and needs an interactive terminal. Run it yourself in your own "
            "terminal; an agent must not run it or supply the confirmation."
        )


def record_human_skip(
    cp: Any,
    task_id: str,
    phase: str,
    reason: str,
    *,
    tty_fn: Optional[Callable[[], bool]] = None,
    input_fn: Callable[[str], str] = input,
    out: Callable[[str], None] = print,
    agent_uid: Optional[int] = None,
) -> str:
    """Record a review skip after the human confirms; actor is forced to human."""
    _require_human(tty_fn, "Skipping a review", agent_uid)
    out(f"You are recording that YOU chose to skip the optional agent review ('{phase}') for task {task_id}.")
    out(f"Reason: {reason}")
    out("This records your choice. It does NOT move the task to another state.")
    out("NEXT: the agent will coordinate the transition to the next step on your go-ahead.")
    resp = input_fn(f"Type the phase name ({phase}) or YES to confirm: ").strip()
    if resp not in (phase, "YES"):
        raise ReceiptError("Confirmation did not match; nothing was recorded.")
    return cp.record_review_skip(task_id, phase, "human", reason, provenance="human-interactive")


def invalidate_receipt(
    cp: Any,
    receipt_id: int,
    reason: str,
    *,
    tty_fn: Optional[Callable[[], bool]] = None,
    input_fn: Callable[[str], str] = input,
    out: Callable[[str], None] = print,
    agent_uid: Optional[int] = None,
) -> None:
    """Invalidate a receipt after the human types its id; the audit trail keeps both events."""
    _require_human(tty_fn, "Invalidating a receipt", agent_uid)
    out(f"You are invalidating receipt {receipt_id}. Reason: {reason}")
    if input_fn(f"Type the receipt id ({receipt_id}) to confirm: ").strip() != str(receipt_id):
        raise ReceiptError("Confirmation did not match; the receipt was not changed.")
    try:
        cp._persistence.invalidate_receipt(receipt_id, "human", reason)
    except ValueError as exc:
        raise ReceiptError(str(exc)) from exc


def receipt_history(conn: sqlite3.Connection, task_id: str) -> List[Dict[str, Any]]:
    """Return the append-only receipt audit rows for a task, oldest first."""
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM receipt_audit WHERE task_id = ? ORDER BY audit_id", (task_id,)).fetchall()
    return [dict(r) for r in rows]
