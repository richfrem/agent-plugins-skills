#!/usr/bin/env python3
"""
run_agent — multi-LLM task router
===================================

Routes one bounded task to one selected backend. This is the task router;
`routing_proxy.py` is a separate API compatibility shim for interactive
model-replacement sessions (Mode A) and is not involved here.

Lives once in plugins/cli-agents/scripts/ and is symlinked into each skill's
scripts/ directory per the hub-and-spoke policy.

Usage (preferred — named-flag form):
    python scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" \\
        --cli llama --model gemma-4-12b --max-tokens 200

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
                    copilot → gpt-5-mini
                    gemini  → gemini-3-flash-preview
                    claude  → haiku-4.5
                    agy     → (agy selects its own)
                    codex   → gpt-5-codex
                    llama   → gemma-4-12b
    --max-tokens  Max output tokens for cli=llama (default: 120).
    --isolated    Isolation mode: append safety footer to prompt; suppress dangerous CLI
                  permission flags (--yolo, --dangerously-skip-permissions).

Prompt assembly:
    persona + input   →  persona / ---SOURCE--- input / ---INSTRUCTION--- instruction
    input only        →  input / ---INSTRUCTION--- instruction
    instruction only  →  instruction

Symlink targets (file-level, per plugin-architecture-policy):
    skills/copilot-cli-agent/scripts/run_agent.py → ../../../scripts/run_agent.py
    skills/gemini-cli-agent/scripts/run_agent.py  → ../../../scripts/run_agent.py
    skills/agy-cli-agent/scripts/run_agent.py     → ../../../scripts/run_agent.py
    skills/claude-cli-agent/scripts/run_agent.py  → ../../../scripts/run_agent.py
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

# ── Defaults per CLI ──────────────────────────────────────────────────────────
_DEFAULT_MODELS = {
    "copilot": "gpt-5-mini",
    "gemini": "gemini-3-flash-preview",
    "claude": "haiku-4.5",
    "agy": None,          # agy selects its own model
    "codex": "gpt-5-codex",
    "llama": "gemma-4-12b",  # direct HTTP to llama-server :8089, no proxy
}

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
    parts = []
    has_persona = bool(persona.strip())
    has_source = bool(source.strip())
    has_instruction = bool(instruction.strip())

    if has_persona:
        parts.append(persona)
    if has_source:
        parts.append(f"---SOURCE---\n{source}" if has_persona else source)
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


def _build_cmd_agy(prompt_file: str, isolated: bool = False) -> list[str]:
    """Agy CLI. --dangerously-skip-permissions is suppressed when isolated=True."""
    if isolated:
        return ["agy", "-p", f"@{prompt_file}"]
    return ["agy", "--dangerously-skip-permissions", "-p", f"@{prompt_file}"]


def _build_cmd_claude(model: str, prompt: str) -> list[str]:
    return ["claude", "--model", model, "-p", prompt]


def _build_cmd_codex(model: str) -> list[str]:
    """Codex exec — prompt is piped via stdin ('-').

    Passing large multiline prompts as a positional shell argument hits OS ARG_MAX
    limits and exposes the prompt in process listings. Stdin is the correct path
    for non-interactive codex exec per official docs.
    """
    return ["codex", "exec", "--model", model, "-"]


def _call_llama_direct(
    prompt: str, model: str, output_file: str,
    max_tokens: int = _LLAMA_MAX_TOKENS_DEFAULT,
) -> None:
    """POST directly to llama-server :8089/v1/chat/completions (non-streaming, no proxy)."""
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
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read())
    except urllib.error.URLError as e:
        print(f"Error: cannot reach llama-server at {_LLAMA_SERVER_URL}: {e}")
        print("  Start it with: ./run_server.sh")
        sys.exit(1)
    text = data["choices"][0]["message"]["content"]
    with open(output_file, "w") as f:
        f.write(text)
    sys.stdout.write(text)
    if not text.endswith("\n"):
        sys.stdout.write("\n")


# ── Main orchestrator ─────────────────────────────────────────────────────────

def run_agent(
    persona_file: str,
    input_file: str,
    output_file: str,
    instruction: str,
    cli: str = "copilot",
    model: str | None = None,
    isolated: bool = False,
    max_tokens: int = _LLAMA_MAX_TOKENS_DEFAULT,
) -> None:
    cli = cli.lower()
    if cli not in _DEFAULT_MODELS:
        print(f"Error: unknown cli '{cli}'. Choose from: {', '.join(_DEFAULT_MODELS)}")
        sys.exit(1)

    if model is None:
        model = _DEFAULT_MODELS[cli] or ""

    # Homebrew path injection for macOS
    if os.path.exists("/opt/homebrew/bin") and "/opt/homebrew/bin" not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"/opt/homebrew/bin:{os.environ['PATH']}"

    persona = read_file_or_empty(resolve_path(persona_file))
    source = read_file_or_empty(resolve_path(input_file))
    prompt = build_prompt(persona, source, instruction, isolated)

    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

    # llama: direct HTTP to llama-server, no subprocess or temp file needed
    if cli == "llama":
        _call_llama_direct(prompt, model, output_file, max_tokens=max_tokens)
        print(f"[run_agent] llama complete → {output_file}")
        return

    # CLIs that need a temp file (prompt passed by file reference or stdin pipe)
    uses_file = cli in ("copilot", "agy", "codex")

    prompt_tmp: str = ""
    try:
        if uses_file:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tf:
                tf.write(prompt)
                prompt_tmp = tf.name

        if cli == "copilot":
            cmd: list[str] = _build_cmd_copilot(model, prompt_tmp, isolated)
        elif cli == "gemini":
            cmd = _build_cmd_gemini(model, prompt, isolated)
        elif cli == "agy":
            cmd = _build_cmd_agy(prompt_tmp, isolated)
        elif cli == "codex":
            cmd = _build_cmd_codex(model)
        else:  # claude
            cmd = _build_cmd_claude(model, prompt)

        if cli in _STREAMING_CLIS:
            with open(output_file, "w") as out_f:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in (proc.stdout or []):
                    sys.stdout.write(line)
                    sys.stdout.flush()
                    out_f.write(line)
                proc.wait()
            if proc.returncode != 0:
                print(f"Error: {cli} exited with code {proc.returncode}")
                sys.exit(proc.returncode)
        elif cli == "codex":
            # Codex reads prompt from stdin; prompt_tmp is piped as stdin
            with open(output_file, "w") as out_f, open(prompt_tmp, "r") as stdin_f:
                subprocess.run(cmd, stdin=stdin_f, stdout=out_f, stderr=subprocess.STDOUT, check=True)
        else:
            with open(output_file, "w") as out_f:
                subprocess.run(cmd, stdout=out_f, stderr=subprocess.STDOUT, check=True)

        print(f"[run_agent] {cli} complete → {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error executing {cli}: {e}")
        sys.exit(1)
    finally:
        if prompt_tmp and os.path.exists(prompt_tmp):
            os.remove(prompt_tmp)


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
            "--max-tokens", type=int, default=_LLAMA_MAX_TOKENS_DEFAULT,
            help=f"Max output tokens for cli=llama (default: {_LLAMA_MAX_TOKENS_DEFAULT})",
        )
        parser.add_argument(
            "--isolated", action="store_true",
            help="Isolation mode: append safety footer; suppress --yolo / dangerous flags",
        )
        args = parser.parse_args()
        run_agent(args.persona_file, args.input_file, args.output_file, args.instruction,
                  args.cli, args.model, args.isolated, args.max_tokens)
