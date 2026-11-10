#!/usr/bin/env python3
"""
run_agent — multi-LLM task router
===================================

Routes one bounded task to one selected backend. This is the task router;
`routing_proxy.py` is a separate API compatibility shim for interactive
model-replacement sessions (Mode A) and is not involved here.

Lives in the cli-agent skill's scripts/ directory as a git-tracked file.

Usage (preferred — named-flag form):
    python scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" \\
        --cli llama --model gemma-4-12b --max-tokens 200

    Optional local preferences:
        --cli codex --tier medium --profile context/agent-capability-profile.json

Usage (legacy — positional form, backward compat):
    python scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" \\
        [cli=copilot] [model=<default>] [isolated=false]

Arguments:
    persona_file  Persona markdown path, or /dev/null to skip.
    input_file    Task prompt / source file path, or /dev/null to skip.
    output_file   Path where output is saved (also streamed to stdout).
    instruction   Task instruction string.

Flags (named-flag mode):
    --cli, -c     Backend target (default: copilot):
                    copilot → GitHub Copilot CLI
                    gemini  → Gemini CLI
                    claude  → Claude CLI
                    agy     → Antigravity (Agy) CLI
                    codex   → Codex / OpenAI-compatible CLI (prompt via stdin)
                    llama   → optimized local Gemma host (direct HTTP to llama-server :8089)
    --model, -m   Model identifier. Defaults per backend:
                    copilot → mai-code-1.1-flash
                    gemini  → gemini-3-flash-preview
                    claude  → claude-haiku-4-5
                    agy     → gemini-3.8-flash-low (loaded from cheapest_models.json)
                    codex   → gpt-5.6-luna
                    llama   → gemma-4-12b
    --max-tokens  Max output tokens for cli=llama (default: 120).
    --isolated    Isolation mode: append safety footer to prompt; suppress dangerous CLI
                  permission flags (--yolo, --dangerously-skip-permissions).
    --profile     Optional validated local capability profile for provider/tier preferences.

Prompt assembly:
    persona + input   →  persona / ---SOURCE--- input / ---INSTRUCTION--- instruction
    input only        →  input / ---INSTRUCTION--- instruction
    instruction only  →  instruction

Purpose:
    See "Routes one bounded task..." above.

Key Input Dependencies:
    - Persona/input files (or /dev/null to skip)
    - references/cheapest_models.json (optional, overrides default model per backend)
    - CLI backend binary on PATH (copilot, gemini, claude, agy, codex) or a
      local llama-server instance (--cli llama)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from model_catalog import CatalogContractError, load_catalog, select_model
from capability_profile import ProfileStatus, load_profile

# ── Defaults per CLI ──────────────────────────────────────────────────────────
def _load_default_models() -> dict[str, str | None]:
    """Return hardcoded default models, overridden by cheapest_models.json if present."""
    defaults = {
        "copilot": "mai-code-1.1-flash",
        "gemini": "gemini-3-flash-preview",
        "claude": "claude-haiku-4-5",
        "agy": "gemini-3.8-flash-low",
        "codex": "gpt-5.6-luna",
        "cursor": "grok-2",
        "llama": "gemma-4-12b",
    }
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        ref_path = os.path.join(script_dir, "..", "references", "cheapest_models.json")
        if os.path.exists(ref_path):
            with open(ref_path, "r") as f:
                data = json.load(f)
                for cli, info in data.items():
                    if "model" in info:
                        defaults[cli] = info["model"]
    except Exception:
        pass
    return defaults

_DEFAULT_MODELS = _load_default_models()

RATE_LIMIT_KEYWORDS = (
    "rate limit",
    "rate_limit",
    "ratelimit",
    "429",
    "too many requests",
    "resourceexhausted",
    "resource_exhausted",
    "quota exceeded",
    "exceeded your current quota",
    "insufficient_quota",
    "usage limit",
    "credit balance is too low",
    "hit the message limit",
    "resets in",
    "at capacity",
    "please try a different model",
    "overloaded",
    "not logged in",
)


def _is_rate_limit_or_capacity_error(error_text: str, returncode: int = 1) -> bool:
    """Return True if the failure appears to be a rate limit, quota exhaustion, or capacity error."""
    lower = error_text.lower()
    return any(kw in lower for kw in RATE_LIMIT_KEYWORDS)


class BackendExecutionError(Exception):
    """Raised when a CLI backend fails during execution."""

    def __init__(self, cli: str, returncode: int, output: str):
        self.cli = cli
        self.returncode = returncode
        self.output = output
        self.is_rate_limit = _is_rate_limit_or_capacity_error(output, returncode)
        super().__init__(f"Backend '{cli}' failed with code {returncode}")


_LLAMA_MAX_TOKENS_DEFAULT = 120  # bounded output for agent subtasks

_LLAMA_SERVER_URL = "http://localhost:8089/v1/chat/completions"

_STREAMING_CLIS = {"copilot", "agy"}  # use Popen + line-by-line; others use subprocess.run


# ── Path helpers ──────────────────────────────────────────────────────────────

def resolve_path(provided_path: str) -> str:
    """Resolve against CWD then plugin root; return as-is if neither exists."""
    if os.path.exists(provided_path):
        return provided_path
    script_dir = os.path.dirname(os.path.realpath(__file__))
    plugin_root = os.path.dirname(script_dir)
    fallback = os.path.join(plugin_root, provided_path)
    return fallback if os.path.exists(fallback) else provided_path


def read_file_or_empty(path: str) -> str:
    """Read file; return empty string for /dev/null or missing files."""
    if path in ("/dev/null", "nul", "") or not os.path.exists(path):
        return ""
    try:
        with open(path, "r") as f:
            return f.read()
    except (OSError, IOError):
        return ""


# ── Prompt assembly ───────────────────────────────────────────────────────────

def build_prompt(persona: str, source: str, instruction: str, isolated: bool) -> str:
    """Assemble the full prompt from persona/source/instruction, with an optional isolation footer."""
    parts = []
    has_persona = bool(persona.strip())
    has_source = bool(source.strip())
    has_instruction = bool(instruction.strip())

    if has_persona:
        parts.append(persona)
    if has_source:
        parts.append(f"---SOURCE---\n{source}\n---END SOURCE---")
    if has_instruction:
        label = "---INSTRUCTION---\n" if (has_persona or has_source) else ""
        parts.append(f"{label}{instruction}")
    if isolated:
        parts.append(
            "You are operating as an isolated sub-agent. "
            "Do NOT use tools. Do NOT access filesystem. Only use the provided input."
        )

    return "\n\n".join(["\n"] + parts)


# ── CLI command builders ───────────────────────────────────────────────────────

def _build_cmd_copilot(model: str, prompt_file: str, isolated: bool = False) -> list[str]:
    """Copilot CLI. --yolo is suppressed when isolated=True."""
    yolo = [] if isolated else ["--yolo"]
    if sys.platform == "win32":
        flags = " ".join(yolo)
        ps = f'$p = Get-Content -Raw "{prompt_file}"; copilot {flags} --model {model} -p $p'
        return ["powershell", "-NoProfile", "-Command", ps]
    return ["copilot"] + yolo + ["--model", model, "-p", f"@{prompt_file}"]


def _build_cmd_gemini(model: str, prompt: str, isolated: bool = False) -> list[str]:
    """Gemini CLI. --yolo is suppressed when isolated=True."""
    yolo = [] if isolated else ["--yolo"]
    binary = "gemini" if shutil.which("gemini") else None
    if binary:
        return ["gemini"] + yolo + ["-m", model, "-p", prompt]
    if shutil.which("npx"):
        return ["npx", "--yes", "@google/gemini-cli@latest"] + yolo + ["-m", model, "-p", prompt]
    print("Error: neither 'gemini' nor 'npx' found in PATH.")
    sys.exit(1)


def _build_cmd_agy(
    model: str,
    prompt_file: str,
    isolated: bool = False,
    effort: str | None = None,
    print_timeout: str | None = None,
) -> list[str]:
    """Agy CLI. --dangerously-skip-permissions is suppressed when isolated=True."""
    cmd = ["agy"]
    if model:
        cmd += ["--model", model]
    if effort:
        if effort not in {"low", "medium", "high"}:
            raise ValueError(f"Unsupported agy effort: {effort}")
        cmd += ["--effort", effort]
    if print_timeout:
        cmd += ["--print-timeout", print_timeout]
    if not isolated:
        cmd += ["--dangerously-skip-permissions"]
    cmd += ["-p", f"@{prompt_file}"]
    return cmd


def _build_cmd_claude(model: str, prompt: str, isolated: bool = False, effort: str | None = None) -> list[str]:
    """Claude CLI. --dangerously-skip-permissions is suppressed when isolated=True."""
    cmd = ["claude"] + ([] if isolated else ["--dangerously-skip-permissions"])
    if effort:
        if effort not in {"low", "medium", "high"}:
            raise ValueError(f"Unsupported Claude effort: {effort}")
        cmd += ["--effort", effort]
    return cmd + ["--model", model, "-p", prompt]


def _build_cmd_codex(model: str) -> list[str]:
    """Codex exec — prompt is piped via stdin ('-').

    Passing large multiline prompts as a positional shell argument hits OS ARG_MAX
    limits and exposes the prompt in process listings. Stdin is the correct path
    for non-interactive codex exec per official docs.
    """
    return ["codex", "exec", "--model", model, "-"]


def _build_cmd_cursor(model: str | None, prompt: str, isolated: bool = False) -> list[str]:
    """Cursor CLI (agent). --mode plan is used when isolated=True."""
    cmd = ["agent", "-p", prompt, "--output-format", "text"]
    if model:
        cmd += ["--model", model]
    if isolated:
        cmd += ["--mode", "plan"]
    else:
        cmd += ["--trust"]
    return cmd


def _call_llama_direct(
    prompt: str, model: str, output_file: str,
    max_tokens: int = _LLAMA_MAX_TOKENS_DEFAULT,
) -> None:
    """POST directly to llama-server :8089/v1/chat/completions (non-streaming, no proxy).

    The request has a bounded timeout (min(300 s, --timeout)). A timeout abandons THIS request only: the shared inference server is
    never signalled, stopped or restarted by run_agent. Usage is read from the response's own `usage` field when present."""
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "max_tokens": max_tokens,
    }).encode("utf-8")
    req = urllib.request.Request(
        _LLAMA_SERVER_URL, data=payload,
        headers={"Content-Type": "application/json"},
    )
    started = _time.time()
    _OPTS.seen["final_timeout"] = False
    limit = min(300, _OPTS.timeout) if _OPTS.timeout else 300
    try:
        with urllib.request.urlopen(req, timeout=limit) as resp:
            data = json.loads(resp.read())
    except (TimeoutError, OSError) as e:      # URLError and socket timeouts are OSError subclasses
        timeout = isinstance(e, TimeoutError) or "timed out" in str(e)
        _record_attempt(backend="llama", status="timeout" if timeout else "failed", started=started, ended=_time.time(),
                        usage={"total_tokens": None, "source": "request did not complete"}, note="HTTP request abandoned; server untouched")
        if timeout:
            _OPTS.seen["final_timeout"] = True
        print(f"Error: cannot reach llama-server at {_LLAMA_SERVER_URL}: {e}")
        print("  Start it with: ./run_server.sh")
        sys.exit(1)
    text = data["choices"][0]["message"]["content"]
    u = data.get("usage") or {}
    total = u.get("total_tokens") if isinstance(u.get("total_tokens"), int) else None
    usage = {"total_tokens": total, "tokens_in": u.get("prompt_tokens"), "tokens_out": u.get("completion_tokens"), "source": "llama-server response usage"} if total is not None \
        else {"total_tokens": None, "source": "response carried no usage"}
    _OPTS.seen["usage"] = usage
    _record_attempt(backend="llama", status="ok", started=started, ended=_time.time(), usage=usage)
    with open(output_file, "w") as f:
        f.write(text)
    sys.stdout.write(text)
    if not text.endswith("\n"):
        sys.stdout.write("\n")


# ── Main orchestrator ─────────────────────────────────────────────────────────

def _catalog_key_for_cli(cli: str) -> str:
    """Map CLI aliases to the authoritative runtime catalog key."""
    return "agy" if cli == "gemini" else cli


def _resolve_catalog_model(cli: str, tier: str, preferred_model: str | None = None) -> str:
    """Resolve a catalog-backed model, failing closed when the contract is invalid."""
    if cli in ("llama", "cursor"):
        return _DEFAULT_MODELS.get(cli) or ""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    catalog_path = os.path.join(
        script_dir, "..", "references", f"{_catalog_key_for_cli(cli)}-models.json"
    )
    cheapest = None
    cheapest_path = os.path.join(script_dir, "..", "references", "cheapest_models.json")
    try:
        with open(cheapest_path, "r", encoding="utf-8") as handle:
            cheapest = json.load(handle).get(_catalog_key_for_cli(cli), {}).get("model")
        catalog = load_catalog(Path(catalog_path))
        catalog_preference = preferred_model or (cheapest if tier == "low" else None)
        return select_model(catalog, tier, preferred_model=catalog_preference)
    except (OSError, json.JSONDecodeError, CatalogContractError) as exc:
        raise ValueError(f"Unable to resolve a valid model catalog for {cli}: {exc}") from exc


def _resolve_cli_and_model(
    cli: str,
    model: str | None,
    tier: str = "low",
    profile_path: str | None = None,
) -> tuple:
    """Validate/lowercase the cli name, resolve the default model, and inject Homebrew PATH on macOS."""
    cli = cli.lower()
    if cli not in _DEFAULT_MODELS:
        print(f"Error: unknown cli '{cli}'. Choose from: {', '.join(_DEFAULT_MODELS)}")
        sys.exit(1)

    if tier not in ("low", "medium", "high"):
        raise ValueError(f"Unsupported capability tier: {tier}")

    if model is None and profile_path:
        profile_result = load_profile(Path(profile_path))
        provider = profile_result.profile.get("providers", {}).get(cli, {})
        preferred = provider.get("model_tiers", {}).get(tier) if isinstance(provider, dict) else None
        if profile_result.status is ProfileStatus.READY and provider.get("available") is True and preferred:
            try:
                model = _resolve_catalog_model(cli, tier, preferred_model=preferred)
            except RuntimeError:
                # A stale or withdrawn preference must never block dispatch.
                model = None

    if model is None:
        model = _resolve_catalog_model(cli, tier)

    # Homebrew path injection for macOS
    if os.path.exists("/opt/homebrew/bin") and "/opt/homebrew/bin" not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"/opt/homebrew/bin:{os.environ['PATH']}"

    return cli, model


def _maybe_write_prompt_tmp(cli: str, prompt: str) -> str:
    """Write prompt to a temp file for CLIs that need file/stdin reference; return '' otherwise."""
    if cli not in ("copilot", "agy", "codex"):
        return ""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tf:
        tf.write(prompt)
        return tf.name


def _build_cli_cmd(
    cli: str,
    model: str,
    prompt: str,
    prompt_tmp: str,
    isolated: bool,
    effort: str | None = None,
    print_timeout: str | None = None,
) -> list[str]:
    """Dispatch to the correct command builder for the given backend."""
    if cli == "copilot":
        return _build_cmd_copilot(model, prompt_tmp, isolated)
    if cli == "gemini":
        return _build_cmd_gemini(model, prompt, isolated)
    if cli == "agy":
        return _build_cmd_agy(model, prompt_tmp, isolated, effort, print_timeout)
    if cli == "codex":
        return _build_cmd_codex(model)
    if cli == "cursor":
        return _build_cmd_cursor(model, prompt, isolated)
    cmd = _build_cmd_claude(model, prompt, isolated or _OPTS.clean_context, effort)  # claude
    if _OPTS.clean_context:
        cmd += ["--setting-sources", "project", "--disable-slash-commands", "--tools", ""]
    return cmd



# ── Launch controls (enforced here; see references/execution-contract.md "Enforced vs instructed") ──
import dispatch_guard as _guard  # sibling module in this directory
import time as _time
import signal as _signal
import tempfile as _tempfile
import json as _json
import re as _re
import threading as _threading


class _ExecOpts:
    """Per-invocation controls. Defaults reproduce the historical behavior exactly."""
    cwd: str | None = None
    timeout: float | None = None
    clean_context: bool = False
    seen: dict = {}


_OPTS = _ExecOpts()


def _parse_usage(cli: str, text: str) -> dict:
    """Vendor-reported usage when the CLI prints it; otherwise unknown (never zero)."""
    m = _re.search(r"tokens used\s*[:\n]?\s*([\d,]+)", text or "", _re.I)
    if m:
        return {"total_tokens": int(m.group(1).replace(",", "")), "source": f"{cli} stdout"}
    return {"total_tokens": None, "source": "not reported by backend"}


def _kill_group(proc) -> None:
    try:
        os.killpg(os.getpgid(proc.pid), _signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        proc.kill()


def _record_attempt(**rec) -> None:
    """One entry per backend attempt (fallbacks included) so a caller can account every launch; usage stays null when unknown."""
    rec.setdefault("usage", {"total_tokens": None, "source": "not reported by backend"})
    _OPTS.seen.setdefault("attempts", []).append(rec)


def _execute_cli_command(cmd: list, cli: str, output_file: str, prompt_tmp: str) -> None:
    """Run the CLI command. EVERY subprocess path launches the worker as the leader of its own session/process group, so a timeout,
    cancellation or error stops the worker and its descendants (dispatch_guard.terminate_group) before ownership is released or a
    fallback starts. Partial output is preserved. Streaming CLIs are read line by line; others are collected with communicate()."""
    executable = shutil.which(cmd[0])
    if not executable:
        raise FileNotFoundError(f"Selected executable is unavailable: {cmd[0]}")
    cmd = [executable, *cmd[1:]]
    # Probe before opening the output, without including task input in diagnostics.
    version = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=10)
    version_text = version.stdout.strip() if version.returncode == 0 else f"unavailable (--version exit {version.returncode})"
    print(f"[run_agent] executable={executable} version={version_text or 'unavailable'}")
    _OPTS.seen.update({"executable": executable, "version": version_text, "cli": cli})
    kw = {"cwd": _OPTS.cwd} if _OPTS.cwd else {}
    kw["start_new_session"] = True            # the worker owns a fresh session/group (POSIX); non-POSIX falls back to taskkill /T
    print(f"[run_agent] python={sys.executable} version={sys.version.split()[0]}")
    started = _time.time()
    _OPTS.seen["final_timeout"] = False          # reflects only the most recent attempt (a later non-timeout failure must not report "timeout")
    stdin_f = open(prompt_tmp, "r") if cli == "codex" else None      # codex reads the prompt from stdin
    proc = None
    timed_out = {"v": False}
    cleanup: dict = {}
    captured: list[str] = []
    try:
        proc = subprocess.Popen(cmd, stdin=stdin_f or subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, **kw)

        def _on_timeout():
            timed_out["v"] = True
            cleanup.update(_guard.terminate_group(proc))

        timer = None
        if _OPTS.timeout:
            timer = _threading.Timer(_OPTS.timeout, _on_timeout); timer.daemon = True; timer.start()
        with open(output_file, "w") as out_f:
            if cli in _STREAMING_CLIS:
                for line in (proc.stdout or []):
                    sys.stdout.write(line); sys.stdout.flush(); out_f.write(line); captured.append(line)
                proc.wait()
            else:
                out, _ = proc.communicate()
                captured.append(out or "")
                out_f.write(out or ""); sys.stdout.write(out or "")
        if timer:
            timer.cancel()
            if timed_out["v"]:
                timer.join(30)                 # the watcher is still confirming cleanup; wait for its verdict before deciding anything
        text = "".join(captured)
        usage = _parse_usage(cli, text)
        _OPTS.seen["usage"] = usage
        if timed_out["v"]:
            _OPTS.seen["final_timeout"] = True
            if not cleanup.get("confirmed", False):
                _OPTS.seen["cleanup_unconfirmed"] = True
            _record_attempt(backend=cli, status="timeout", exit=proc.returncode, started=started, ended=_time.time(), usage=usage,
                            cleanup=cleanup, partial_output=bool(text))
            raise subprocess.TimeoutExpired(cmd, _OPTS.timeout)
        _record_attempt(backend=cli, status="ok" if proc.returncode == 0 else "failed", exit=proc.returncode, started=started,
                        ended=_time.time(), usage=usage)
        if proc.returncode != 0:
            raise BackendExecutionError(cli, proc.returncode, text)
    finally:
        if stdin_f:
            stdin_f.close()
        if proc is not None and proc.poll() is None:              # cancellation (SIGTERM/Ctrl-C/exception): never leave the group behind
            res = _guard.terminate_group(proc)
            if not res.get("confirmed", False):
                _OPTS.seen["cleanup_unconfirmed"] = True


def _run_agent_core(
    persona_file: str,
    input_file: str,
    output_file: str,
    instruction: str,
    cli: str = "claude",
    model: str | None = None,
    isolated: bool = False,
    max_tokens: int = _LLAMA_MAX_TOKENS_DEFAULT,
    require_input: bool = False,
    tier: str = "low",
    profile_path: str | None = None,
    effort: str | None = None,
    print_timeout: str | None = None,
    executable: str | None = None,
    fallback_chain: list[str] | str | None = None,
    allow_copilot: bool = False,
) -> None:
    """Assemble the prompt and dispatch it across primary and fallback backends."""
    # Parse fallback chain
    if isinstance(fallback_chain, str):
        chain_backends = [c.strip().lower() for c in fallback_chain.split(",") if c.strip()]
    elif isinstance(fallback_chain, (list, tuple)):
        chain_backends = [c.strip().lower() for c in fallback_chain if c.strip()]
    else:
        chain_backends = []

    primary_cli = cli.lower()
    full_chain = [primary_cli] + [c for c in chain_backends if c != primary_cli]

    # Boundary check: strictly enforce --allow-copilot for GitHub Copilot
    for candidate in full_chain:
        if candidate == "copilot" and not allow_copilot:
            raise ValueError(
                "Governance Guard: GitHub Copilot is provisioned strictly for enterprise/work repositories. "
                "To explicitly authorize Copilot in the dispatch or fallback chain, pass --allow-copilot."
            )

    persona = read_file_or_empty(resolve_path(persona_file))
    resolved_input = resolve_path(input_file)
    source = read_file_or_empty(resolved_input)
    if require_input and not source.strip():
        raise ValueError(f"Required input is missing or empty: {input_file}")
    prompt = build_prompt(persona, source, instruction, isolated)

    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

    errors: list[tuple[str, Exception]] = []

    for idx, target_cli in enumerate(full_chain):
        is_fallback = idx > 0
        current_model = model if not is_fallback else None
        target_cli, resolved_model = _resolve_cli_and_model(target_cli, current_model, tier, profile_path)

        if is_fallback:
            print(f"[run_agent] Executing fallback #{idx} via backend={target_cli} model={resolved_model}...")

        # llama: direct HTTP to llama-server, no subprocess or temp file needed
        if target_cli == "llama":
            try:
                _call_llama_direct(prompt, resolved_model, output_file, max_tokens=max_tokens)
                print(f"[run_agent] {target_cli} complete → {output_file}")
                return
            except Exception as err:
                errors.append((target_cli, err))
                is_rate = _is_rate_limit_or_capacity_error(str(err))
                if is_rate and idx < len(full_chain) - 1:
                    print(f"[run_agent] Quota/capacity limit on {target_cli}. Failing over to '{full_chain[idx + 1]}'...")
                    continue
                print(f"Error executing {target_cli}: {err}")
                sys.exit(1)

        prompt_tmp: str = ""
        try:
            prompt_tmp = _maybe_write_prompt_tmp(target_cli, prompt)
            cmd = _build_cli_cmd(target_cli, resolved_model, prompt, prompt_tmp, isolated, effort, print_timeout)
            if executable and not is_fallback:
                cmd[0] = executable
            print(f"[run_agent] backend={target_cli} model={resolved_model} effort={effort or 'provider-default'}")
            _execute_cli_command(cmd, target_cli, output_file, prompt_tmp)
            print(f"[run_agent] {target_cli} complete → {output_file}")
            return  # Success

        except BackendExecutionError as err:
            errors.append((target_cli, err))
            if err.is_rate_limit and idx < len(full_chain) - 1:
                next_backend = full_chain[idx + 1]
                print(f"[run_agent] Quota/capacity limit on {target_cli} (exit {err.returncode}). Failing over to '{next_backend}'...")
                if os.path.exists(output_file):
                    try:
                        os.remove(output_file)
                    except OSError:
                        pass
                continue
            elif not err.is_rate_limit:
                print(f"Error executing {target_cli}: task error (not a quota/rate-limit issue). Halting without fallback.")
                sys.exit(err.returncode)
            else:
                print(f"Error executing {target_cli}: rate limit encountered and fallback chain exhausted.")
                sys.exit(err.returncode)
        except (OSError, RuntimeError, subprocess.TimeoutExpired, FileNotFoundError) as error:
            errors.append((target_cli, error))
            if _OPTS.seen.get("cleanup_unconfirmed"):
                print(f"Error executing {target_cli}: worker cleanup not confirmed; refusing to start a fallback or release ownership early.")
                sys.exit(1)
            if idx < len(full_chain) - 1:
                print(f"[run_agent] System error on {target_cli} ({error}). Failing over to '{full_chain[idx + 1]}'...")
                continue
            print(f"Error executing {target_cli}: {error}")
            sys.exit(1)
        finally:
            if prompt_tmp and os.path.exists(prompt_tmp):
                try:
                    os.remove(prompt_tmp)
                except OSError:
                    pass

    print(f"[run_agent] All {len(full_chain)} backends in fallback chain failed: {[e[0] for e in errors]}")
    sys.exit(1)



def run_agent(*args, cwd: str | None = None, allowed_root: str | None = None, claim_dir: str | None = None,
              unit: str | None = None, owner: str | None = None, claim_token: str | None = None, timeout: float | None = None,
              clean_context: bool = False, result_json: str | None = None, **kwargs) -> None:
    """Supported dispatch entry point. Positional/keyword parameters are those of `_run_agent_core` (unchanged).

    Added, all optional (omitting them keeps the historical behavior): cwd + allowed_root (worktree boundary),
    claim_dir + unit + owner (duplicate-launch prevention), timeout (seconds, process-group kill on streaming path),
    clean_context (claude only: neutral cwd, project-only settings, no slash commands/tools; NOT probed here),
    result_json (structured return of status, checks, limitations, usage). A failed launch check exits 2 BEFORE launch.
    """
    started = _time.time()
    if timeout is not None and timeout <= 0:
        raise ValueError("timeout must be > 0 seconds")
    checks: list[dict] = []
    enforced = []
    limitations = ["clean-context flags are requested, not probed: run dispatch_guard.py context-check on a stream-json probe to verify"
                   if clean_context else None]
    status, exit_code, error = "ok", 0, None
    claimed, own_token, claim_mode = False, None, None
    _OPTS.cwd, _OPTS.timeout, _OPTS.clean_context, _OPTS.seen = cwd, timeout, clean_context, {}
    own_tmp = None
    _prev = {}
    if _threading.current_thread() is _threading.main_thread():
        def _term(signum, frame):
            raise SystemExit(128 + signum)
        for _s in (_signal.SIGTERM, _signal.SIGHUP):
            _prev[_s] = _signal.signal(_s, _term)
    try:
        if cwd is not None and allowed_root is not None:
            r = _guard.check_cwd(cwd, allowed_root)
            checks.append({"name": "cwd_boundary", **r}); enforced.append("cwd_boundary")
            if not r["ok"]:
                raise _LaunchRefused(r["detail"])
        elif cwd is not None:
            limitations.append("cwd given without allowed_root: boundary not enforced")
        if claim_dir:
            if not (unit and owner):
                raise _LaunchRefused("claim_dir requires unit and owner")
            if claim_token:
                # The caller (e.g. work_loop) acquired the claim BEFORE creating any artifacts. Verify, never re-acquire or release it:
                # exactly one party holds the claim, so loop and executor cannot conflict.
                ok = _guard.verify_claim(claim_dir, unit, claim_token)
                checks.append({"name": "unit_claim", "ok": ok, "detail": "pre-acquired claim verified by token" if ok else "claim token not held"}); enforced.append("unit_claim")
                claim_mode = "caller-held (verified)"
                if not ok:
                    raise _LaunchRefused(f"unit {unit}: supplied claim token is not the active claim")
            else:
                r = _guard.claim(claim_dir, unit, owner)
                checks.append({"name": "unit_claim", "ok": r["ok"], "detail": r.get("why") or r["owner"]}); enforced.append("unit_claim")
                if not r["ok"]:
                    raise _LaunchRefused(f"unit {unit} already owned by {r['owner']}")
                claimed, own_token, claim_mode = True, r["token"], "executor-acquired"
        if clean_context:
            tgt = (args[4] if len(args) > 4 else kwargs.get("cli", "claude")).lower()
            fb = kwargs.get("fallback_chain") or (args[14] if len(args) > 14 else None) or []
            fb = [x.strip().lower() for x in (fb.split(",") if isinstance(fb, str) else fb) if x.strip()]
            if tgt != "claude" or any(x != "claude" for x in fb):
                raise _LaunchRefused(f"clean_context is only supported for claude with no non-claude fallback (got {tgt}, fallback {fb})")
            if cwd is not None:
                raise _LaunchRefused("clean_context chooses a neutral cwd itself; do not pass cwd")
            own_tmp = _tempfile.mkdtemp(prefix="clean-ctx-")
            _OPTS.cwd = own_tmp
            checks.append({"name": "clean_context_cwd", "ok": True, "detail": own_tmp}); enforced.append("clean_context_cwd")
        _run_agent_core(*args, **kwargs)
        _OPTS.seen.setdefault("usage", {"total_tokens": None, "source": "backend not run through a subprocess"})
    except _LaunchRefused as e:
        status, exit_code, error = "refused", 2, str(e)
        print(f"[run_agent] launch refused: {e}")
    except SystemExit as e:
        exit_code = e.code if isinstance(e.code, int) else 1
        status = "ok" if exit_code == 0 else ("timeout" if _OPTS.seen.get("final_timeout") else "failed")
        error = None if exit_code == 0 else (f"backend timed out after {timeout}s" if status == "timeout" else f"backend exited {exit_code}")
    except BaseException as e:      # noqa: BLE001 - record then re-raise: a crash must never leave status "ok"
        status, exit_code, error = "failed", 1, f"{type(e).__name__}: {e}"
        raise
    finally:
        if claimed:
            _guard.release(claim_dir, unit, token=own_token)      # only the claim THIS invocation acquired
        ended = _time.time()
        if result_json:
            seen = _OPTS.seen
            res = {"schema": 1, "status": status, "exit_code": exit_code, "error": error, "unit": unit, "owner": owner,
                   "backend": seen.get("cli"), "executable": seen.get("executable"), "version": seen.get("version"),
                   "cwd": _OPTS.cwd, "started": started, "ended": ended, "duration_s": round(ended - started, 3),
                   "output_file": (args[2] if len(args) > 2 else kwargs.get("output_file")),
                   "checks": checks, "enforced_by_code": enforced,
                   "instructed_only": ["no git writes by the worker", "stay inside the assigned scope", "report limitations honestly"],
                   "limitations": [x for x in limitations if x], "usage": seen.get("usage", {"total_tokens": None, "source": "not run"}),
                   "attempts": seen.get("attempts", []), "claim_mode": claim_mode, "cleanup_confirmed": not seen.get("cleanup_unconfirmed", False)}
            os.makedirs(os.path.dirname(os.path.abspath(result_json)), exist_ok=True)
            with open(result_json, "w") as f:
                _json.dump(res, f, indent=1)
        for _s, _h in _prev.items():
            _signal.signal(_s, _h)
        _OPTS.cwd = _OPTS.timeout = None; _OPTS.clean_context = False
    if own_tmp:
        import shutil as _sh
        _sh.rmtree(own_tmp, ignore_errors=True)
    if status in ("refused", "failed", "timeout"):
        sys.exit(exit_code)


class _LaunchRefused(Exception):
    pass


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Two calling conventions are supported:
    #
    # Named-flag (preferred):
    #   run_agent.py P I O "INSTR" --cli llama --model gemma-4-12b --max-tokens 200
    #
    # Legacy positional (backward compat — sys.argv[5] is a bare word, not a flag):
    #   run_agent.py P I O "INSTR" [cli] [model] [isolated]

    if len(sys.argv) < 5:
        print(
            "Usage: run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> \"<INSTRUCTION>\"\n"
            "       Named-flag form (preferred):\n"
            "         [--cli copilot] [--model <default>] [--max-tokens 120] [--isolated]\n"
            "       Legacy positional form:\n"
            "         [cli=copilot] [model=<default>] [isolated=false]"
        )
        sys.exit(1)

    if len(sys.argv) >= 6 and not sys.argv[5].startswith("-"):
        # Legacy positional mode — keep old behaviour exactly
        _cli = sys.argv[5] if len(sys.argv) >= 6 else "copilot"
        _model = sys.argv[6] if len(sys.argv) >= 7 else None
        _isolated = sys.argv[7].lower() == "true" if len(sys.argv) == 8 else False
        run_agent(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
                  _cli, _model, _isolated)
    else:
        # Named-flag mode via argparse
        parser = argparse.ArgumentParser(
            prog="run_agent.py",
            description="Multi-LLM task router — routes one bounded task to one backend.",
        )
        parser.add_argument("persona_file", help="Persona markdown path, or /dev/null")
        parser.add_argument("input_file", help="Task input file path, or /dev/null")
        parser.add_argument("output_file", help="Output file path")
        parser.add_argument("instruction", help="Task instruction string")
        parser.add_argument(
            "--cli", "-c", default="copilot",
            choices=list(_DEFAULT_MODELS.keys()),
            help="Backend target (default: copilot)",
        )
        parser.add_argument("--model", "-m", default=None,
                            help="Model identifier (default: per backend)")
        parser.add_argument(
            "--tier", choices=("low", "medium", "high"), default="low",
            help="Capability/cost tier used when --model is omitted (default: low)",
        )
        parser.add_argument(
            "--profile",
            default=None,
            help="Optional validated local capability profile for provider/tier preferences.",
        )
        parser.add_argument(
            "--max-tokens", type=int, default=_LLAMA_MAX_TOKENS_DEFAULT,
            help=f"Max output tokens for cli=llama (default: {_LLAMA_MAX_TOKENS_DEFAULT})",
        )
        parser.add_argument(
            "--isolated", action="store_true",
            help="Isolation mode: append safety footer; suppress --yolo / dangerous flags",
        )
        parser.add_argument(
            "--effort", choices=("low", "medium", "high"), default=None,
            help="Reasoning effort for Claude or agy (low, medium, or high).",
        )
        parser.add_argument("--executable", help="Explicit CLI executable path; takes precedence over PATH.")
        parser.add_argument(
            "--print-timeout", default=None,
            help="Explicit Agy print wait ceiling, for example 15m0s.",
        )
        parser.add_argument(
            "--require-input", action="store_true",
            help="Fail before dispatch when input_file is missing or empty.",
        )
        parser.add_argument(
            "--fallback-chain",
            default=None,
            help="Comma-separated fallback backends to attempt on rate-limit/capacity failure (e.g. 'agy,codex').",
        )
        parser.add_argument(
            "--allow-copilot",
            action="store_true",
            default=False,
            help="Explicit user authorization required to use GitHub Copilot in dispatch or fallback chain (enterprise/work boundary guard).",
        )
        parser.add_argument("--cwd", help="Run the backend in this directory (a worktree).")
        parser.add_argument("--allowed-root", help="Refuse to launch unless --cwd resolves inside this root.")
        parser.add_argument("--claim-dir", help="Directory for unit ownership claims; a second claim of --unit is refused before launch.")
        parser.add_argument("--unit"); parser.add_argument("--owner")
        parser.add_argument("--claim-token", help="Token of a claim the CALLER already acquired for --unit; the executor verifies it and never releases it.")
        parser.add_argument("--timeout", type=float, help="Seconds; kills the backend process group on the streaming path.")
        parser.add_argument("--clean-context", action="store_true", help="claude only: neutral cwd, project-only settings, no slash commands or tools.")
        parser.add_argument("--result-json", help="Write the structured execution result (status, checks, limitations, usage).")
        args = parser.parse_args()
        # Keep the public capability tier and agy reasoning effort aligned when
        # callers select an explicit model but omit --effort. This prevents an
        # empty effort value from reaching agy and failing after dispatch starts.
        if args.cli == "agy" and args.effort is None:
            args.effort = args.tier
        run_agent(args.persona_file, args.input_file, args.output_file, args.instruction,
                  args.cli, args.model, args.isolated, args.max_tokens, args.require_input,
                  args.tier, args.profile, args.effort, args.print_timeout, args.executable,
                  fallback_chain=args.fallback_chain, allow_copilot=args.allow_copilot,
                  cwd=args.cwd, allowed_root=args.allowed_root, claim_dir=args.claim_dir, unit=args.unit, owner=args.owner, claim_token=args.claim_token,
                  timeout=args.timeout, clean_context=args.clean_context, result_json=args.result_json)
