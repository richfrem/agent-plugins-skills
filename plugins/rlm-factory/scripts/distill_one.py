#!/usr/bin/env python3
"""
distill_one.py
=====================================

Purpose:
    Single-file distillation smoke test. Reads one file, calls the specified
    agent CLI to generate an RLM summary, then injects the result into the
    correct cache directory via inject_summary.py.

    Use this to verify the full pipeline works end-to-end before running the
    full swarm batch.

Usage:
    # 1. Copilot (GPT-5 mini)
    python3 ./scripts/distill_one.py --profile wiki --file plugin-research/superpowers/decision.md --engine copilot

    # 2. Gemini (Gemini-3 Flash Preview)
    python3 ./scripts/distill_one.py --profile wiki --file plugin-research/superpowers/quick-wins.md --engine gemini --model gemini-3-flash-preview

    # 3. Claude (Haiku-4.5)
    python3 ./scripts/distill_one.py --profile wiki --file plugin-research/superpowers/capabilities-matrix.md --engine claude --model haiku-4.5

    # Dry-run: print the prompt but don't call the CLI:
    python3 ./scripts/distill_one.py --profile wiki --file plugins/adr-manager/README.md --dry-run

Related:
    - inject_summary.py  (cache persistence)
    - rlm_config.py      (profile + path resolution)
    - swarm_run.py       (batch version of this script)
"""

import sys
import shlex
import argparse
import subprocess
from pathlib import Path

# ─── PATH BOOTSTRAP ─────────────────────────────────────────────────────────
def _find_project_root(start: Path) -> Path:
    for p in [start.resolve()] + list(start.resolve().parents):
        if (p / ".git").is_dir():
            return p
    return start.resolve().parents[3]

PROJECT_ROOT = _find_project_root(Path(__file__))
SCRIPT_DIR   = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# ─── AUGMENT PATH for subprocesses ─────────────────────────────────────────
# Antigravity runs with a stripped PATH. Add common locations for CLI tools.
import os
_extra_paths = [
    "/opt/homebrew/bin",
    "/usr/local/bin",
    os.path.expanduser("~/.local/bin"),
    os.path.expanduser("~/.npm-global/bin"),
    os.path.expanduser("~/n/bin"),
    "/usr/local/share/npm/bin",
]
for _p in _extra_paths:
    if _p not in os.environ.get("PATH", "") and Path(_p).exists():
        os.environ["PATH"] = _p + ":" + os.environ.get("PATH", "")

try:
    from rlm_config import RLMConfig
except ImportError as e:
    print(f"❌ Cannot import rlm_config: {e}")
    sys.exit(1)

# ─── ENGINE DEFAULTS ─────────────────────────────────────────────────────────
ENGINE_DEFAULTS = {
    "copilot": "gpt-5-mini",
    "gemini":  "gemini-3-flash-preview",
    "claude":  "claude-haiku-4-5",
}


def build_llm_cmd(engine: str, model: str, prompt_payload: str) -> tuple[list[str], str]:
    """
    Build the CLI command list and the stdin payload for the given engine.

    Returns:
        (cmd_args, stdin_text)
    """
    engine = engine.lower()

    if engine == "claude":
        return (
            ["claude", "--model", model, "-p", prompt_payload, "--no-session-persistence"],
            ""  # claude reads -p, no stdin needed
        )
    elif engine == "gemini":
        return (
            ["gemini", "--model", model, "-p", prompt_payload],
            ""
        )
    elif engine == "copilot":
        # Copilot CLI ignores -p; prepend instruction to stdin
        return (
            ["copilot", "--model", model],
            prompt_payload
        )
    else:
        print(f"❌ Unknown engine: {engine}. Choose from: copilot, gemini, claude")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Single-file RLM distillation smoke test"
    )
    parser.add_argument("--profile",  required=True,  help="RLM profile name (from rlm_profiles.json)")
    parser.add_argument("--file",     required=True,  help="Path to the file to summarize (relative to project root)")
    parser.add_argument("--engine",   default="copilot", choices=["copilot", "gemini", "claude"],
                        help="AI CLI engine to use (default: copilot)")
    parser.add_argument("--model",    default=None,
                        help="Model override. Defaults to engine's recommended free model.")
    parser.add_argument("--dry-run",  action="store_true",
                        help="Print the prompt payload but do not call the CLI or write cache.")
    args = parser.parse_args()

    # ─── RESOLVE CONFIG ──────────────────────────────────────────────────────
    try:
        config = RLMConfig(profile_name=args.profile)
    except SystemExit:
        sys.exit(1)

    model = args.model or ENGINE_DEFAULTS.get(args.engine, "gpt-5-mini")

    file_path = PROJECT_ROOT / args.file
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8")
    rel_path = str(file_path.relative_to(PROJECT_ROOT))

    # ─── LOAD PROMPT TEMPLATE ────────────────────────────────────────────────
    prompt_template = config.prompt_template
    if not prompt_template:
        # Inline fallback
        prompt_template = (
            "Summarize the architectural purpose of this file in 2-3 concise sentences.\n"
            "File: {file_path}\n\n{content}\n\n# Distilled Summary:"
        )

    prompt_payload = prompt_template.format(file_path=rel_path, content=content)

    print(f"🔍 Distilling: {rel_path}")
    print(f"   Engine : {args.engine}")
    print(f"   Model  : {model}")
    print(f"   Profile: {args.profile}")
    print(f"   Cache  : {config.cache_path}")
    print("-" * 60)

    if args.dry_run:
        print("⚙️  DRY RUN — prompt payload preview (first 500 chars):")
        print(prompt_payload[:500])
        print("...")
        return

    # ─── CALL CLI ────────────────────────────────────────────────────────────
    cmd_args, stdin_text = build_llm_cmd(args.engine, model, prompt_payload)

    print(f"🚀 Calling: {' '.join(shlex.quote(a) for a in cmd_args[:3])} ...")
    try:
        proc = subprocess.run(
            cmd_args,
            input=stdin_text or None,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        print(f"❌ CLI binary '{args.engine}' not found on PATH.")
        print(f"   Make sure you have the {args.engine} CLI installed and authenticated.")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("❌ CLI call timed out after 120s.")
        sys.exit(1)

    if proc.returncode != 0 or not proc.stdout.strip():
        print(f"❌ CLI returned exit code {proc.returncode}")
        print(proc.stderr[:500] if proc.stderr else "(no stderr)")
        sys.exit(1)

    summary = proc.stdout.strip()

    print(f"\n✅ Summary received ({len(summary)} chars):")
    print("-" * 60)
    print(summary)
    print("-" * 60)

    # ─── INJECT INTO CACHE ───────────────────────────────────────────────────
    inject_script = SCRIPT_DIR / "inject_summary.py"
    inject_cmd = [
        sys.executable, str(inject_script),
        "--profile", args.profile,
        "--file",    rel_path,
        "--summary", summary,
    ]

    print(f"\n💾 Injecting into cache...")
    inject_proc = subprocess.run(inject_cmd, capture_output=True, text=True)
    if inject_proc.returncode == 0:
        print(inject_proc.stdout.strip())
        print(f"\n🎉 Done! Check: {config.cache_path}")
    else:
        print(f"❌ inject_summary.py failed:")
        print(inject_proc.stderr or inject_proc.stdout)
        sys.exit(1)


if __name__ == "__main__":
    main()
