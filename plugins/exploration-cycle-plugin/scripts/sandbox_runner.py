# plugins/exploration-cycle-plugin/scripts/sandbox_runner.py
"""
sandbox_runner.py — Process Hygiene, Container Wrapping, and HMAC Envelopes
"""
import hashlib
import hmac as _hmac
import json
import os
import secrets
import shutil
import signal
import subprocess
import time
from collections import OrderedDict
from pathlib import Path

ALLOWED_ENV = frozenset({"PATH", "HOME", "TMPDIR", "LANG", "LC_ALL"})
BLOCKED_ENV = frozenset({
    "PYTHONPATH", "PYTHONSTARTUP", "PYTHONHOME",
    "LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "DYLD_LIBRARY_PATH",
    "NODE_OPTIONS", "NODE_PATH",
})
TIMEOUT_SECONDS = 300
GRACE_SECONDS = 10
NONCE_CACHE_MAX = 10_000


def _build_clean_env(extra_vars: dict | None = None) -> dict:
    env = {k: os.environ[k] for k in ALLOWED_ENV if k in os.environ}
    if extra_vars:
        for k, v in extra_vars.items():
            if k not in BLOCKED_ENV:
                env[k] = v
    return env


def _terminate_with_grace(proc: subprocess.Popen, grace: int = GRACE_SECONDS) -> None:
    if proc.poll() is not None:
        return
    proc.send_signal(signal.SIGTERM)
    deadline = time.time() + grace
    while time.time() < deadline:
        if proc.poll() is not None:
            return
        time.sleep(0.1)
    if proc.poll() is None:
        proc.kill()
        proc.wait()


def run_hygienic(cmd: list, timeout: int = TIMEOUT_SECONDS,
                 extra_vars: dict | None = None) -> subprocess.CompletedProcess:
    env = _build_clean_env(extra_vars)
    proc = subprocess.Popen(cmd, shell=False, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return subprocess.CompletedProcess(
            args=cmd, returncode=proc.returncode,
            stdout=stdout, stderr=stderr,
        )
    except subprocess.TimeoutExpired:
        _terminate_with_grace(proc, grace=GRACE_SECONDS)
        stdout, stderr = proc.communicate()
        raise


def _detect_container_runtime() -> str | None:
    for runtime in ("podman", "docker"):
        if shutil.which(runtime) is not None:
            return runtime
    return None


def run_containerized(cmd: list, session_id: str, dispatch_id: str,
                       allowed_paths_ro: list | None = None,
                       allowed_paths_rw: list | None = None,
                       timeout: int = TIMEOUT_SECONDS) -> subprocess.CompletedProcess:
    """Run cmd inside a read-only container. ro paths get ':ro', rw paths are writable."""
    runtime = _detect_container_runtime()
    if not runtime:
        raise RuntimeError("No container runtime (podman/docker) available")

    container_cmd = [
        runtime, "run", "--rm",
        "--network=none", "--cpus=1.0", "--memory=512m", "--read-only",
        f"--label=agentic_os_session={session_id}",
        f"--label=agentic_os_dispatch={dispatch_id}",
    ]
    for path in (allowed_paths_ro or []):
        container_cmd.extend(["-v", f"{path}:{path}:ro"])
    for path in (allowed_paths_rw or []):
        container_cmd.extend(["-v", f"{path}:{path}"])

    container_cmd.extend(["python:3.11-slim"] + cmd)

    proc = subprocess.Popen(container_cmd, shell=False,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return subprocess.CompletedProcess(
            args=container_cmd, returncode=proc.returncode,
            stdout=stdout, stderr=stderr,
        )
    except subprocess.TimeoutExpired:
        _terminate_with_grace(proc, grace=GRACE_SECONDS)
        _stdout, _stderr = proc.communicate()
        raise


def _cleanup_stale_containers(session_id: str) -> None:
    runtime = _detect_container_runtime()
    if not runtime:
        return
    try:
        result = subprocess.run(
            [runtime, "ps", "-a", "-q", f"--filter=label=agentic_os_session={session_id}"],
            capture_output=True, text=True, timeout=10
        )
        for cid in result.stdout.splitlines():
            cid = cid.strip()
            if cid:
                subprocess.run([runtime, "rm", "-f", cid], capture_output=True, timeout=10)
    except Exception:
        pass
