"""Bounded implementation-session loop, independent of lifecycle transitions."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


@dataclass(frozen=True)
class ImplementationEvent:
    kind: str
    round: int
    detail: str = ""


class TestCadence:
    """Enforce the implementation-session test order and one final-suite run."""

    __test__ = False

    def __init__(self) -> None:
        self._seen: list[str] = []

    def record(self, test_kind: str) -> None:
        if test_kind not in {"focused", "integration", "full"}:
            raise ValueError("test kind must be focused, integration, or full")
        if test_kind == "integration" and "focused" not in self._seen:
            raise ValueError("integration tests require focused tests first")
        if test_kind == "full":
            if "integration" not in self._seen:
                raise ValueError("full suite requires an integration checkpoint first")
            if "full" in self._seen:
                raise ValueError("full suite is permitted only once per implementation session")
        self._seen.append(test_kind)


def create_default_controller(
    queue_path: Path,
    dispatch: Callable[[int, dict], str],
    review: Callable[[int, dict, str], tuple[str, str]],
    fix: Optional[Callable[[int, dict, str, str], str]] = None,
    **kwargs: object,
) -> "ImplementationController":
    """Construct the canonical persistent implementation controller runtime."""
    return ImplementationController(
        PersistentTaskQueue(queue_path), dispatch, review, fix, **kwargs
    )


class PersistentTaskQueue:
    """Small JSON-backed queue for bounded implementation work packages."""

    def __init__(self, path: Path, *, max_tasks: int = 100) -> None:
        if max_tasks < 1:
            raise ValueError("max_tasks must be positive")
        self.path = Path(path)
        self.max_tasks = max_tasks
        self._tasks: list[dict] = self._read()

    def _read(self) -> list[dict]:
        if not self.path.exists():
            return []
        value = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
            raise ValueError("implementation queue must contain a JSON list of objects")
        return value

    def _write(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(self._tasks, indent=2), encoding="utf-8")
        temporary.replace(self.path)

    def enqueue(self, task_id: str, payload: object = None) -> None:
        if len(self._tasks) >= self.max_tasks:
            raise OverflowError("implementation queue bound exhausted")
        if any(task.get("id") == task_id for task in self._tasks):
            raise ValueError(f"duplicate implementation task: {task_id}")
        self._tasks.append({"id": task_id, "payload": payload, "status": "queued"})
        self._write()

    def pending(self) -> list[dict]:
        return [task for task in self._tasks if task.get("status") in {"queued", "in_progress"}]

    def set_status(self, task_id: str, status: str, *, detail: str = "") -> None:
        for task in self._tasks:
            if task.get("id") == task_id:
                task["status"] = status
                if detail:
                    task["detail"] = detail
                self._write()
                return
        raise KeyError(task_id)


class ImplementationController:
    """Owns queue continuation after worktree entry; lifecycle gates remain external."""

    def __init__(
        self,
        queue: PersistentTaskQueue,
        dispatch: Callable[[int, dict], str],
        review: Callable[[int, dict, str], tuple[str, str]],
        fix: Optional[Callable[[int, dict, str, str], str]] = None,
        *,
        max_rounds: int = 5,
        heartbeat_path: Optional[Path] = None,
        watchdog_timeout: float = 300.0,
        clock: Callable[[], float] = time.time,
        exit_verification: Optional[Callable[[], bool]] = None,
        on_event: Optional[Callable[[ImplementationEvent], None]] = None,
    ) -> None:
        self.queue, self.dispatch, self.review, self.fix = queue, dispatch, review, fix
        self.max_rounds = max_rounds
        self.heartbeat_path = Path(heartbeat_path) if heartbeat_path else None
        self.watchdog_timeout, self.clock = watchdog_timeout, clock
        self.exit_verification, self.on_event = exit_verification, on_event
        self.cadence = TestCadence()

    def run_verification(self, test_kind: str, runner: Callable[[], object]) -> object:
        """Run a verification command only when its cadence position is legal."""
        self.cadence.record(test_kind)
        return runner()

    def heartbeat(self, event: str = "HEARTBEAT") -> None:
        if self.heartbeat_path:
            self.heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
            self.heartbeat_path.write_text(
                json.dumps({"timestamp": self.clock(), "event": event}), encoding="utf-8"
            )

    def _emit(self, event: ImplementationEvent, events: list[ImplementationEvent]) -> None:
        self.heartbeat(event.kind)
        events.append(event)
        if self.on_event:
            self.on_event(event)

    def _watchdog_blocker(self) -> Optional[str]:
        if not self.heartbeat_path or not self.heartbeat_path.exists():
            return None
        try:
            timestamp = float(json.loads(self.heartbeat_path.read_text(encoding="utf-8"))["timestamp"])
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            return "heartbeat is unreadable"
        if self.clock() - timestamp > self.watchdog_timeout:
            return "heartbeat is stale"
        return None

    def run(self) -> list[ImplementationEvent]:
        events: list[ImplementationEvent] = []
        blocker = self._watchdog_blocker()
        if blocker:
            self._emit(ImplementationEvent("BLOCKED", 0, blocker), events)
            return events
        for task in self.queue.pending():
            if task.get("status") == "in_progress":
                self.queue.set_status(task["id"], "queued")
            self.queue.set_status(task["id"], "in_progress")
            task_id = task["id"]
            fix = self.fix or (lambda round_number, current, artifact, findings: artifact)
            task_events = run_implementation_session(
                lambda round_number: self.dispatch(round_number, task),
                lambda round_number, artifact: self.review(round_number, task, artifact),
                lambda round_number, artifact, findings: fix(round_number, task, artifact, findings),
                max_rounds=self.max_rounds,
                on_event=lambda event: self._emit(event, events),
            )
            terminal = task_events[-1].kind if task_events else "BLOCKED"
            self.queue.set_status(task_id, "complete" if terminal == "COMPLETE" else "blocked", detail=task_events[-1].detail)
            if terminal != "COMPLETE":
                return events
        if self.exit_verification:
            try:
                verified = self.exit_verification()
            except Exception as exc:
                self._emit(ImplementationEvent("BLOCKED", 0, f"exit verification failed: {exc}"), events)
                return events
            if not verified:
                self._emit(ImplementationEvent("BLOCKED", 0, "exit verification denied"), events)
                return events
        self._emit(ImplementationEvent("EXIT_VERIFICATION", 0, "implementation queue complete"), events)
        return events


def run_implementation_session(
    dispatch: Callable[[int], str],
    review: Callable[[int, str], tuple[str, str]],
    fix: Callable[[int, str, str], str],
    *,
    max_rounds: int = 5,
    on_event: Optional[Callable[[ImplementationEvent], None]] = None,
) -> list[ImplementationEvent]:
    """Run dispatch/review/fix rounds without invoking lifecycle transitions.

    The caller owns native or portable agent dispatch. A ``PASS`` review ends the
    session; ``BLOCKED`` or an exhausted bound ends it explicitly. The pipeline
    may consume the returned events when it performs exit verification.
    """
    if max_rounds < 1:
        raise ValueError("max_rounds must be positive")
    events: list[ImplementationEvent] = []

    def emit(event: ImplementationEvent) -> None:
        events.append(event)
        if on_event:
            on_event(event)

    for round_number in range(1, max_rounds + 1):
        try:
            result = dispatch(round_number)
        except Exception as exc:  # callback boundary: persist a visible blocker
            emit(ImplementationEvent("BLOCKED", round_number, f"dispatch failed: {exc}"))
            return events
        emit(ImplementationEvent("DISPATCHED", round_number, result))
        try:
            verdict, findings = review(round_number, result)
        except Exception as exc:
            emit(ImplementationEvent("BLOCKED", round_number, f"review failed: {exc}"))
            return events
        normalized = verdict.strip().upper()
        emit(ImplementationEvent("REVIEWED", round_number, f"{normalized}: {findings}"))
        if normalized == "PASS":
            emit(ImplementationEvent("COMPLETE", round_number, "review passed"))
            return events
        if normalized not in {"REVISE", "REJECT"}:
            emit(ImplementationEvent("BLOCKED", round_number, f"unknown review verdict: {verdict}"))
            return events
        if round_number == max_rounds:
            emit(ImplementationEvent("BLOCKED", round_number, "maximum review rounds exhausted"))
            return events
        try:
            fixed = fix(round_number, result, findings)
        except Exception as exc:
            emit(ImplementationEvent("BLOCKED", round_number, f"fix failed: {exc}"))
            return events
        emit(ImplementationEvent("FIX_DISPATCHED", round_number, fixed))
    return events
