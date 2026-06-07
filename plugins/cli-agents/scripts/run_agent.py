#!/usr/bin/env python3
"""
run_agent (CLI) — unified sub-agent dispatcher
================================================

Canonical script for the cli-agents plugin. Lives once in plugins/cli-agents/scripts/
and is symlinked into each skill's scripts/ directory per the hub-and-spoke policy.

Usage:
    python scripts/run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> "<INSTRUCTION>" \
        [cli=copilot] [model=<default>] [isolated=false]

Arguments:
    persona_file  Persona markdown path, or /dev/null to skip.
    input_file    Task prompt / source file path, or /dev/null to skip.
    output_file   Path where output is saved (also streamed to stdout).
    instruction   Task instruction string.
    cli           Target CLI: copilot | gemini | agy | claude  (default: copilot)
    model         Model identifier passed to the CLI. Defaults per CLI:
                    copilot → gpt-5-mini
                    gemini  → gemini-3-flash-preview
                    claude  → haiku-4.5
                    agy     → (no model arg — agy chooses its own)
    isolated      "true" to append isolation footer blocking tool use. (default: false)

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

import os
import shutil
import subprocess
import sys
import tempfile

# ── Defaults per CLI ──────────────────────────────────────────────────────────
_DEFAULT_MODELS = {
    "copilot": "gpt-5-mini",
    "gemini": "gemini-3-flash-preview",
    "claude": "haiku-4.5",
    "agy": None,  # agy selects its own model
}

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

def _build_cmd_copilot(model: str, prompt_file: str) -> list[str]:
    if sys.platform == "win32":
        ps = f'$p = Get-Content -Raw "{prompt_file}"; copilot --yolo --model {model} -p $p'
        return ["powershell", "-NoProfile", "-Command", ps]
    return ["copilot", "--yolo", "--model", model, "-p", f"@{prompt_file}"]


def _build_cmd_gemini(model: str, prompt: str) -> list[str]:
    binary = "gemini" if shutil.which("gemini") else None
    if binary:
        return ["gemini", "--yolo", "-m", model, "-p", prompt]
    if shutil.which("npx"):
        return ["npx", "--yes", "@google/gemini-cli@latest", "--yolo", "-m", model, "-p", prompt]
    print("Error: neither 'gemini' nor 'npx' found in PATH.")
    sys.exit(1)


def _build_cmd_agy(prompt_file: str) -> list[str]:
    return ["agy", "--dangerously-skip-permissions", "-p", f"@{prompt_file}"]


def _build_cmd_claude(model: str, prompt: str) -> list[str]:
    return ["claude", "--model", model, "-p", prompt]


# ── Main orchestrator ─────────────────────────────────────────────────────────

def run_agent(
    persona_file: str,
    input_file: str,
    output_file: str,
    instruction: str,
    cli: str = "copilot",
    model: str | None = None,
    isolated: bool = False,
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

    # CLIs that take a prompt file reference (@file)
    uses_file = cli in ("copilot", "agy")

    prompt_tmp: str = ""
    try:
        if uses_file:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tf:
                tf.write(prompt)
                prompt_tmp = tf.name

        if cli == "copilot":
            cmd: list[str] = _build_cmd_copilot(model, prompt_tmp)
        elif cli == "gemini":
            cmd = _build_cmd_gemini(model, prompt)
        elif cli == "agy":
            cmd = _build_cmd_agy(prompt_tmp)
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



if __name__ == "__main__":
    if len(sys.argv) < 5 or len(sys.argv) > 8:
        print(
            "Usage: run_agent.py <PERSONA_FILE> <INPUT_FILE> <OUTPUT_FILE> \"<INSTRUCTION>\"\n"
            "                    [cli=copilot] [model=<default>] [isolated=false]"
        )
        sys.exit(1)

    _cli = sys.argv[5] if len(sys.argv) >= 6 else "copilot"
    _model = sys.argv[6] if len(sys.argv) >= 7 else None
    _isolated = sys.argv[7].lower() == "true" if len(sys.argv) == 8 else False

    run_agent(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], _cli, _model, _isolated)
