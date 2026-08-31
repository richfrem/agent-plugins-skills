#!/usr/bin/env python
r"""
swarm_run.py 2.0
================

Purpose:
    Generic parallel Claude CLI executor. Dispatches N workers over a set of
    input files, each worker running Claude with a prompt defined in a Job File,
    then optionally pipes the output through a post-command (e.g. cache injector).

Key Input Dependencies:
    - job file (.job.md)        — YAML configuration and Markdown system prompt
    - manifest.json             — Optional context-bundler manifest for target file selection
    - cheapest_models.json      — Customizes the model choice by resolving recommended names
    - live filesystem           — Target directories crawled for files

WHAT IS A JOB FILE?
    A Job File is a single Markdown file (.md) that bundles ALL configuration
    and the prompt together. It has two parts:

    1. YAML Frontmatter (between --- delimiters) — Configuration:
       - model:      Claude model to use (haiku, sonnet, opus). Default: haiku
       - workers:    Number of parallel workers. Default: 5
       - timeout:    Seconds per worker before timeout. Default: 120
       - max_retries: Retry attempts on rate-limit errors. Default: 3
       - ext:        File extensions to include when using --dir. Default: [".md"]
       - post_cmd:   Shell command template run after each successful LLM call.
                     Placeholders: {file}, {output} (quoted), {output_raw},
                     {basename}, and any custom {vars}.
       - check_cmd:  Shell command to test if a file is already processed.
                     If exit code 0, the file is skipped. Placeholder: {file}.
       - vars:       Key-value pairs available as {key} in post_cmd/check_cmd.
       - dir:        Default directory to crawl (overridden by --dir CLI arg).
       - bundle:     Path to a context-bundler manifest JSON/YAML.

    2. Markdown Body (after the second ---) — The Prompt:
       This is the exact text sent to Claude as the system prompt. The file
       content being processed is piped to Claude's stdin.

    Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):
    ```
    ---
    model: haiku
    workers: 5
    timeout: 90
    ext: [".md"]
    post_cmd: >-
      python ./scripts/inject_summary.py
      --profile {profile} --file {file} --summary {output}
    vars:
      profile: project
    ---
    Summarize this document as a single dense paragraph for the cache.
    Start with "Document Review". Include key decisions, outcomes, and
    technical artifacts. Keep it under 200 words.
    ```

MODEL CHOICE:
    The --model flag (or `model:` in the job file) accepts any model alias
    supported by the `claude` CLI:
      - haiku   — Fastest, cheapest. Best for bulk summarization, docs, tests.
      - sonnet  — Balanced. Good for code review, analysis.
      - opus    — Most capable. Use for complex reasoning, architecture.
    Rule of thumb: use the cheapest model that produces acceptable quality.

FEATURES:
    - Checkpoint/Resume:  State saved to .swarm_state_<job>.json every 5 files.
                          Use --resume to skip already-completed files.
    - Retry with Backoff: Rate-limit errors trigger exponential backoff (2^n sec).
    - Verification Skip:  check_cmd in the job file short-circuits already-done work.
    - Dry Run:            --dry-run lists files that would be processed, no LLM calls.

FILE DISCOVERY (checked in this order):
    1. --files file1.md file2.md    Explicit file list
    2. --bundle manifest.json       Context-bundler manifest (JSON/YAML with "files" key)
    3. --files-from checklist.md    Markdown checklist (extracts `- [ ] \`path\``)
    4. --dir some/directory         Recursive crawl filtered by ext

USAGE EXAMPLES:
    # 1. Basic: Summarize all Documents
    python ./scripts/swarm_run.py \
        --job ../../resources/jobs/my_job.job.md \
        --dir docs/

    # 2. Resume after interruption (rate limit, Ctrl+C, crash)
    python ./scripts/swarm_run.py \\
        --job ../../resources/jobs/my_job.job.md \
        --dir docs/ --resume

    # 3. Dry run to verify which files would be processed
    python ./scripts/swarm_run.py \
        --job ../../resources/jobs/my_job.job.md \
        --dir docs/ --dry-run

    # 4. Override model and worker count at runtime
    python ./scripts/swarm_run.py \\
        --job my_job.md --dir docs/ --model sonnet --workers 3

    # 5. Process specific files only
    python ./scripts/swarm_run.py \\
        --job my_job.md --files docs/README.md docs/ARCHITECTURE.md

    # 6. Use a context-bundler manifest
    python ./scripts/swarm_run.py \\
        --job my_job.md --bundle ../../output/manifest.json

    # 7. Pass custom variables (available as {key} in post_cmd)
    python ./scripts/swarm_run.py \\
        --job my_job.md --dir src/ --var profile=staging --var env=prod
"""

import os
import re
import sys
import json
import time
import shlex
import random
import logging
import argparse
import platform as _platform
import subprocess
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import Any

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML not found. Run: python -m pip install pyyaml")
    sys.exit(1)

# ─── Model resolution ────────────────────────────────────────────────────────

def _load_cheapest_model(engine: str, fallback: str, ref_path: "Path | None" = None) -> str:
    """Return the cheapest model for engine from cheapest_models.json, or fallback.

    Consult references/cheapest_models.json for current model recommendations —
    model names change over time and should not be hardcoded inline.
    """
    try:
        if ref_path is None:
            script_dir = Path(__file__).resolve().parent
            ref_path = script_dir.parent / "references" / "cheapest_models.json"
        if ref_path.exists():
            data = json.loads(ref_path.read_text())
            return data.get(engine, {}).get("model", fallback)
    except Exception:
        pass
    return fallback

# ─── AUGMENT PATH for subprocesses ──────────────────────────────────────────
# Ensures CLI tools like `copilot`, `gemini`, `claude` are discoverable when
# this script is invoked by agents that strip the shell PATH.
_extra_paths = [
    "/opt/homebrew/bin",
    "/usr/local/bin",
    os.path.expanduser("~/.local/bin"),
    os.path.expanduser("~/.npm-global/bin"),
    os.path.expanduser("~/n/bin"),
    "/usr/local/share/npm/bin",
]
# VSCode Copilot Chat extension bundles the copilot CLI — path varies by OS
_vscode_copilot_dir = {
    "Darwin": os.path.expanduser(
        "~/Library/Application Support/Code/User/globalStorage/"
        "github.copilot-chat/copilotCli"
    ),
    "Windows": os.path.expanduser(
        "~/AppData/Roaming/Code/User/globalStorage/"
        "github.copilot-chat/copilotCli"
    ),
    "Linux": os.path.expanduser(
        "~/.config/Code/User/globalStorage/"
        "github.copilot-chat/copilotCli"
    ),
}.get(_platform.system())
if _vscode_copilot_dir:
    _extra_paths.append(_vscode_copilot_dir)

for _p in _extra_paths:
    if _p not in os.environ.get("PATH", "") and Path(_p).exists():
        os.environ["PATH"] = _p + ":" + os.environ.get("PATH", "")

# ─── LOGGING ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("swarm")

# ─── HELPERS ────────────────────────────────────────────────────────────────

def shell_quote(value: str) -> str:
    """Safe shell quoting for templates."""
    return "'" + value.replace("'", "'\\''") + "'"

def get_relative_path(path: Path) -> str:
    """Helper to convert absolute path to relative if it lies under current working directory."""
    root = Path.cwd().resolve()
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)


class suppress_monolithic_md:
    """Context manager: temporarily hides the monolithic instruction file (CLAUDE.md, GEMINI.md, etc.)
    to prevent the CLI from loading massive project context per worker call.
    Restores on exit, even after crash or Ctrl+C."""
    def __init__(self, engine: str) -> None:
        """Initialize the context manager with the appropriate engine instruction filename."""
        self.filename = f"{engine.upper()}.md"
        if engine.lower() == "copilot":
            self.filename = ".github/copilot-instructions.md"
        self.src = Path.cwd() / self.filename
        self.bak = Path.cwd() / f".{Path(self.filename).name}.swarm_bak"

    def __enter__(self) -> "suppress_monolithic_md":
        """Move the instruction file out of the workspace to hide it."""
        if self.src.exists():
            self.src.rename(self.bak)
            logger.info(f"🔒 Temporarily hid {self.filename} (restored on exit)")
        return self

    def __exit__(self, *exc: object) -> bool:
        """Restore the instruction file to its original location."""
        if self.bak.exists():
            self.bak.rename(self.src)
            logger.info(f"🔓 Restored {self.filename}")
        return False

# ─── FILE DISCOVERY ─────────────────────────────────────────────────────────

def _resolve_bundle(args: argparse.Namespace, config: dict, is_safe_path: Any) -> list[str]:
    """Helper to parse files from bundle path config/arg."""
    bundle_path = args.bundle or config.get("bundle")
    if not bundle_path:
        return []
    bundle_path = Path(bundle_path)
    if not bundle_path.exists():
        return []
    text = bundle_path.read_text()
    try:
        data = json.loads(text)
    except Exception:
        data = yaml.safe_load(text)
    if isinstance(data, dict):
        data = data.get("files", [])
    paths = []
    for item in data:
        p = item.get("path") if isinstance(item, dict) else item
        if p and is_safe_path(str(p)):
            paths.append(str(p))
    return paths


def _resolve_checklist(args: argparse.Namespace, config: dict, is_safe_path: Any) -> list[str]:
    """Helper to parse files from a task checklist file."""
    task_path = args.files_from or config.get("files_from")
    if not task_path:
        return []
    task_path = Path(task_path)
    if not task_path.exists():
        return []
    matches = [m.group(1) for m in re.finditer(r"- \[ \] `(.+)`", task_path.read_text())]
    return [m for m in matches if is_safe_path(m)]


def resolve_files(args: argparse.Namespace, config: dict) -> list[str]:
    """Find files from CLI args or Job config."""
    exts = config.get("ext", [".md"])
    exts = set(e if e.startswith(".") else f".{e}" for e in exts)
    root_dir = Path.cwd().resolve()

    def is_safe_path(p: str) -> bool:
        """Verify that the target path lies inside the current project root."""
        try:
            resolved = Path(p).resolve()
            return root_dir in resolved.parents or resolved == root_dir
        except Exception:
            return False

    if args.files:
        return [f for f in args.files if is_safe_path(f)]
    
    bundle_files = _resolve_bundle(args, config, is_safe_path)
    if bundle_files:
        return bundle_files

    checklist_files = _resolve_checklist(args, config, is_safe_path)
    if checklist_files:
        return checklist_files

    dir_path = args.dir or config.get("dir")
    if dir_path:
        dir_path = Path(dir_path)
        if dir_path.exists() and is_safe_path(str(dir_path)):
            return [
                get_relative_path(f)
                for f in sorted(dir_path.rglob("*"))
                if f.is_file() and f.suffix.lower() in exts and not f.name.startswith(".")
            ]

    return []

# ─── WORKER ENGINE ───────────────────────────────────────────────────────────

def _should_skip_file(file_path: str, job_config: dict, user_vars: dict, env_vars: dict) -> bool:
    """Run skip verification command to determine if file is already processed."""
    check_cmd_tmpl = job_config.get("check_cmd")
    if check_cmd_tmpl:
        check_cmd_tmpl_args = shlex.split(check_cmd_tmpl)
        check_cmd_args = [arg.format_map({"file": file_path, **user_vars}) for arg in check_cmd_tmpl_args]
        return subprocess.run(check_cmd_args, capture_output=True, env=env_vars).returncode == 0
    return False


def _build_llm_cmd_and_payload(file_path: str, content: str, prompt: str, model: str, engine: str) -> tuple[list[str], str]:
    """Return command line arguments and stdin payload for the chosen LLM engine."""
    cmd_args = [engine.lower()]
    effective_model = model
    if engine.lower() == "gemini" and (not model or model == "haiku" or model.startswith("claude")):
        effective_model = _load_cheapest_model("gemini", "gemini-3-pro-preview")
    elif engine.lower() == "copilot" and (not model or model == "haiku" or model.startswith("claude")):
        effective_model = _load_cheapest_model("copilot", "gpt-5-mini")

    payload = content
    if engine.lower() == "claude":
        cmd_args.extend(["--model", effective_model, "-p", prompt, "--no-session-persistence"])
    elif engine.lower() == "gemini":
        cmd_args.extend(["--model", effective_model, "-p", prompt])
    elif engine.lower() == "copilot":
        cmd_args = ["copilot", "--model", effective_model]
        payload = f"Instruction: {prompt}\n\nTarget File Content:\n{content}"
    return cmd_args, payload


def _run_post_command(file_path: str, result: dict, job_config: dict, user_vars: dict, env_vars: dict) -> None:
    """Run post processing shell command if defined in job configuration."""
    post_cmd_tmpl = job_config.get("post_cmd")
    if post_cmd_tmpl and not result["skipped"]:
        subs = {
            "file": file_path,
            "output": result["output"],
            "output_raw": result["output"],
            "basename": Path(file_path).stem,
            **user_vars
        }
        cmd_tmpl_args = shlex.split(post_cmd_tmpl)
        cmd_args = [arg.format_map(subs) for arg in cmd_tmpl_args]
        pr = subprocess.run(cmd_args, text=True, capture_output=True, env=env_vars)
        if pr.returncode != 0:
            result["success"] = False
            result["error"] = (pr.stderr or pr.stdout or "post-cmd failed").strip()[:300]


def _try_llm_execution(
    file_path: str,
    content: str,
    prompt: str,
    model: str,
    engine: str,
    job_config: dict,
    env_vars: dict,
    result: dict
) -> None:
    """Try to invoke the LLM command, retrying with exponential backoff on rate limits."""
    max_retries = job_config.get("max_retries", 3)
    backoff = 2
    for attempt in range(max_retries + 1):
        result["retries"] = attempt
        cmd_args, payload = _build_llm_cmd_and_payload(file_path, content, prompt, model, engine)
        try:
            proc = subprocess.run(
                cmd_args, input=payload, capture_output=True, text=True,
                timeout=job_config.get("timeout", 60), env=env_vars
            )
            combined_out = (proc.stderr + "\n" + proc.stdout).strip()
        except subprocess.TimeoutExpired:
            proc = subprocess.CompletedProcess(args=cmd_args, returncode=1, stdout="", stderr="TimeoutExpired")
            combined_out = "TimeoutExpired"
        except Exception as e:
            proc = subprocess.CompletedProcess(args=cmd_args, returncode=1, stdout="", stderr=str(e))
            combined_out = str(e)
        
        if proc.returncode == 0 and proc.stdout.strip():
            result["output"] = proc.stdout.strip()
            result["success"] = True
            break
        
        if "hit your limit" in combined_out.lower() or "rate limit" in combined_out.lower():
            if attempt < max_retries:
                wait = (backoff ** attempt) + random.uniform(0, 1)
                logger.warning(f"  ⌛ {file_path}: Rate limit. Backing off {wait:.1f}s...")
                time.sleep(wait)
                continue
            result["error"] = "RATE_LIMIT_EXCEEDED"
            break
        
        result["error"] = combined_out.strip()[:200]
        if attempt < max_retries:
            time.sleep(1)
            continue
        break


def execute_worker(
    file_path: str,
    prompt: str,
    model: str,
    engine: str,
    job_config: dict,
    user_vars: dict,
    env_vars: dict,
    dry_run: bool
) -> dict:
    """Processes a single file. Handles retry, skip, and post-cmd."""
    result = {
        "file": file_path, "success": False, "output": None,
        "error": None, "skipped": False, "retries": 0
    }
    if dry_run:
        logger.info(f"  [DRY] {file_path}")
        result["success"] = True
        return result

    if _should_skip_file(file_path, job_config, user_vars, env_vars):
        logger.info(f"  ⏩ {file_path} (already cached)")
        result["success"] = True
        result["skipped"] = True
        return result

    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception as e:
        result["error"] = f"Read error: {e}"
        return result

    _try_llm_execution(file_path, content, prompt, model, engine, job_config, env_vars, result)
    if not result["success"]:
        return result

    _run_post_command(file_path, result, job_config, user_vars, env_vars)
    if result["success"]:
        logger.info(f"  [OK] {file_path}")
    else:
        logger.error(f"  [ERROR] {file_path}: {result['error']}")
    return result

# ─── MAIN ───────────────────────────────────────────────────────────────────

def _parse_swarm_args() -> argparse.Namespace:
    """Setup and parse CLI arguments for the Swarm Runner."""
    parser = argparse.ArgumentParser(description="Professional Agent Swarm Runner")
    parser.add_argument("--job", type=Path, required=True, help="Job file (.md)")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--dry-run", action="store_true", help="Don't call LLM")
    parser.add_argument("--dir", type=Path)
    parser.add_argument("--files-from", type=Path)
    parser.add_argument("--files", nargs="+")
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--model", type=str)
    parser.add_argument("--engine", type=str, default="claude", choices=["claude", "gemini", "copilot"], help="The CLI engine to run workers through")
    parser.add_argument("--var", action="append", default=[])
    return parser.parse_args()


def _parse_job_and_state(args: argparse.Namespace) -> tuple[dict, str, Path, dict]:
    """Parse the job file structure and load the previous execution state if resuming."""
    full_text = args.job.read_text()
    if not full_text.startswith("---"): 
        print("[ERROR] Invalid job file (no YAML frontmatter)")
        sys.exit(1)
    
    parts = full_text.split("---", 2)
    job_config = yaml.safe_load(parts[1]) or {}
    prompt = parts[2].strip()

    checkpoint_path = Path(f".swarm_state_{args.job.stem}.json")
    state = {"completed": [], "failed": {}}
    if args.resume and checkpoint_path.exists():
        state = json.loads(checkpoint_path.read_text())
        logger.info(f"🔄 Resuming from checkpoint: {len(state['completed'])} items done.")
    return job_config, prompt, checkpoint_path, state


def _run_parallel_executor(
    pending: list,
    prompt: str,
    model: str,
    engine: str,
    job_config: dict,
    user_vars: dict,
    dry_run: bool,
    workers: int,
    state: dict,
    checkpoint_path: Path
) -> list:
    """Submit worker jobs to concurrent thread pool executor and record outputs."""
    results = []
    try:
        with suppress_monolithic_md(engine):
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {
                    pool.submit(execute_worker, f, prompt, model, engine, job_config, user_vars, os.environ.copy(), dry_run): f 
                    for f in pending
                }
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    results.append(res)
                    if res["success"]:
                        state["completed"].append(res["file"])
                    else:
                        state["failed"][res["file"]] = res["error"]
                    
                    if len(results) % 5 == 0:
                        checkpoint_path.write_text(json.dumps(state, indent=2))
    except KeyboardInterrupt:
        logger.warning("\n[WARN] Interrupted. Saving state...")
    finally:
        checkpoint_path.write_text(json.dumps(state, indent=2))
    return results


def main() -> None:
    """CLI entry point: parses args, resolves targets, runs workers parallelly, and manages checkpoints."""
    args = _parse_swarm_args()
    job_config, prompt, checkpoint_path, state = _parse_job_and_state(args)

    # Overrides
    workers = args.workers or job_config.get("workers", 5)
    model = args.model or job_config.get("model", "haiku")
    user_vars = job_config.get("vars", {}) or {}
    for v in args.var:
        k, val = v.split("=", 1)
        user_vars[k.strip()] = val.strip()

    # Resolve Files
    all_files = resolve_files(args, job_config)
    pending = [f for f in all_files if f not in state["completed"]]

    if not pending:
        logger.info("✨ Everything complete. Nothing to do.")
        return

    logger.info(f"[START] Starting Swarm: {len(pending)} pending items ({len(all_files)} total)")
    logger.info(f"   Engine: {args.engine} | Model: {model} | Workers: {workers} | Dry-run: {args.dry_run}")
    print("-" * 70)

    results = _run_parallel_executor(
        pending, prompt, model, args.engine, job_config, user_vars,
        args.dry_run, workers, state, checkpoint_path
    )
    
    success_count = sum(1 for r in results if r["success"])
    fail_count = sum(1 for r in results if not r["success"])
    logger.info("-" * 70)
    logger.info(f"🏁 DONE. Success: {success_count} | Failed: {fail_count}")
        
    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
