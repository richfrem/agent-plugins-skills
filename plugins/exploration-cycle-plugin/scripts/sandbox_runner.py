"""
sandbox_runner.py — Process Hygiene, Container Wrapping, and HMAC Envelopes

Purpose:
    Security-sensitive control plane component (see ADR-007) providing:
    fail-closed path boundary enforcement, hygienic subprocess execution with
    a stripped environment and isolated cwd, optional container-wrapped
    execution (podman/docker), and HMAC-signed envelopes with nonce replay
    protection for dispatch authorization.

Key Input Dependencies:
    - subprocess/container runtime (podman or docker, for run_containerized)
    - Session HMAC key file (generated via generate_session_key)
    - OrderedDict nonce_cache (caller-managed, for verify_envelope replay protection)
"""
import hashlib
import hmac as _hmac
import json
import os
import secrets
import shutil
import signal
import subprocess
import tempfile
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


def _assert_under_root(full: Path, root: Path, label: str = "path") -> None:
    """Fail-closed descendant path check. resolve() eliminates symlink escapes."""
    try:
        full.resolve().relative_to(root.resolve())
    except ValueError:
        raise PermissionError(
            f"Path traversal rejected: {full} is outside {root} ({label})"
        )


def _build_clean_env(extra_vars: dict | None = None) -> dict:
    """Build an environment dict containing only ALLOWED_ENV keys plus safe extra_vars."""
    env = {k: os.environ[k] for k in ALLOWED_ENV if k in os.environ}
    if extra_vars:
        for k, v in extra_vars.items():
            if k not in BLOCKED_ENV:
                env[k] = v
    return env


def _terminate_with_grace(proc: subprocess.Popen, grace: int = GRACE_SECONDS) -> None:
    """Send SIGTERM and wait up to grace seconds before force-killing the process."""
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
    """Run cmd with a stripped environment and an isolated, auto-cleaned-up cwd."""
    env = _build_clean_env(extra_vars)
    cwd = tempfile.mkdtemp(prefix="agentic_sandbox_")
    try:
        proc = subprocess.Popen(cmd, shell=False, env=env, cwd=cwd,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            return subprocess.CompletedProcess(
                args=cmd, returncode=proc.returncode,
                stdout=stdout, stderr=stderr,
            )
        except subprocess.TimeoutExpired:
            _terminate_with_grace(proc)
            proc.wait()
            raise
    finally:
        shutil.rmtree(cwd, ignore_errors=True)


def _detect_container_runtime() -> str | None:
    """Return the first available container runtime ('podman' or 'docker'), or None."""
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

    _cleanup_stale_containers(session_id)

    container_cmd = [
        runtime, "run", "--rm",
        "--network=none", "--cpus=1.0", "--memory=512m", "--read-only",
        f"--label=agentic_os_session={session_id}",
        f"--label=agentic_os_dispatch={dispatch_id}",
        *_container_user_flag(),
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


def _container_user_flag() -> list[str]:
    """Return --user uid:gid for the current process.

    On Windows (no os.getuid), checks WINDOWS_CONTAINER_USER env var first.
    Raises RuntimeError if neither is available — silent nobody:nogroup fallback
    can run as effective root inside Docker Desktop on Windows (SEC-003).
    """
    try:
        return ["--user", f"{os.getuid()}:{os.getgid()}"]
    except AttributeError:
        win_user = os.environ.get("WINDOWS_CONTAINER_USER")
        if win_user:
            return ["--user", win_user]
        raise RuntimeError(
            "Containerized dispatch on Windows requires the WINDOWS_CONTAINER_USER "
            "environment variable (format: 'uid:gid'). Docker Desktop's user mapping "
            "differs from Linux — verify the account is unprivileged before setting."
        )


def _cleanup_stale_containers(session_id: str) -> None:
    """Force-remove any containers labeled with this session_id from a prior run."""
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


# ---------------------------------------------------------------------------
# HMAC Envelope Sign / Verify
# ---------------------------------------------------------------------------

def generate_session_key(key_path: Path) -> bytes:
    """Generate a 32-byte random session key, written atomically with mode 0600."""
    key = os.urandom(32)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(str(key_path), flags, 0o600)
    try:
        os.write(fd, key)
    finally:
        os.close(fd)
    return key


def load_session_key(key_path: Path) -> bytes:
    """Read the raw session HMAC key bytes from key_path."""
    return key_path.read_bytes()


def cleanup_session_key(key_path: Path) -> None:
    """Overwrite then unlink session key file.

    The overwrite pass reduces key recovery risk on HDDs with magnetic remnants.
    It is NOT sufficient for SSDs with wear-leveling — the OS may write to a
    different physical page and the original bytes may persist in spare blocks.
    """
    if key_path.exists():
        key_path.write_bytes(os.urandom(key_path.stat().st_size))
        key_path.unlink()


def sign_envelope(payload: dict, key: bytes) -> dict:
    """Sign payload with a random nonce and HMAC-SHA256 token; return the envelope dict."""
    nonce = secrets.token_hex(16)
    payload_bytes = json.dumps(payload, sort_keys=True).encode()
    token = _hmac.new(key, payload_bytes + nonce.encode(), hashlib.sha256).hexdigest()
    return {"payload": payload, "nonce": nonce, "token": token}


def verify_envelope(envelope: dict, key: bytes, nonce_cache: OrderedDict) -> bool:
    """Timing-safe HMAC verification with nonce deduplication."""
    nonce = envelope.get("nonce", "")
    if not nonce or nonce in nonce_cache:
        return False
    token = envelope.get("token") or ""
    if not isinstance(token, str):
        return False
    payload_bytes = json.dumps(envelope.get("payload", {}), sort_keys=True).encode()
    expected = _hmac.new(key, payload_bytes + nonce.encode(), hashlib.sha256).hexdigest()
    if not _hmac.compare_digest(expected, token):
        return False
    if len(nonce_cache) >= NONCE_CACHE_MAX:
        nonce_cache.popitem(last=False)
    nonce_cache[nonce] = True
    return True
