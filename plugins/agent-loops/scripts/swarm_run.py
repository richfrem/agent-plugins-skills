#!/usr/bin/env python
r"""
swarm_run.py 2.0
================

Purpose:
    Generic parallel Claude CLI executor. Dispatches N workers over a set of
    input files, each worker running Claude with a prompt defined in a Job File,
    then optionally pipes the output through a post-command (e.g. cache injector).

Key Input Dependencies:
    - Job File (.md file with YAML frontmatter + prompt body)
    - Input files (discovered via --files, --dir, --bundle, or --files-from)
    - Claude CLI installed and configured
    - Optional: context-bundler manifest (JSON/YAML)
    - Optional: shell commands for post-processing (post_cmd, check_cmd)

Key Functions:
    - get_relative_path(): Convert absolute path to relative
    - resolve_files(): Discover input files from various sources
    - run_worker(): Execute Claude with prompt and handle output

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
      python/scripts/inject_summary.py
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
    python/scripts/swarm_run.py \
        --job ../../resources/jobs/my_job.job.md \
        --dir docs/

    # 2. Resume after interruption (rate limit, Ctrl+C, crash)
    python/scripts/swarm_run.py \\
        --job ../../resources/jobs/my_job.job.md \
        --dir docs/ --resume

    # 3. Dry run to verify which files would be processed
    python/scripts/swarm_run.py \
        --job ../../resources/jobs/my_job.job.md \
        --dir docs/ --dry-run

    # 4. Override model and worker count at runtime
    python/scripts/swarm_run.py \\
        --job my_job.md --dir docs/ --model sonnet --workers 3

    # 5. Process specific files only
    python/scripts/swarm_run.py \\
        --job my_job.md --files docs/README.md docs/ARCHITECTURE.md

    # 6. Use a context-bundler manifest
    python/scripts/swarm_run.py \\
        --job my_job.md --bundle ../../output/manifest.json

    # 7. Pass custom variables (available as {key} in post_cmd)
    python/scripts/swarm_run.py \\
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
import subprocess
import concurrent.futures
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    print("❌ PyYAML not found. Run: pip install pyyaml")
    sys.exit(1)

# ─── Model resolution ─────────────────────────────────────────────────────────

def _load_cheapest_model(engine: str, fallback: str, ref_path: "Path | None" = None) -> str:
    """Return the cheapest model for engine from cheapest_models.json, or fallback."""
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


# ─── LOGGING ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("swarm")

# ─── HELPERS ────────────────────────────────────────────────────────────────


def get_relative_path(path: Path) -> str:
    """Convert absolute path to relative path from current working directory."""
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
        """Resolve the monolithic instruction filename and backup path for the given engine."""
        self.filename = f"{engine.upper()}.md"
        if engine.lower() == "copilot":
            self.filename = ".github/copilot-instructions.md"
        self.src = Path.cwd() / self.filename
        self.bak = Path.cwd() / f".{Path(self.filename).name}.swarm_bak"

    def __enter__(self) -> "suppress_monolithic_md":
        """Rename the instruction file out of the way if present."""
        if self.src.exists():
            self.src.rename(self.bak)
            logger.info(f"🔒 Temporarily hid {self.filename} (restored on exit)")
        return self

    def __exit__(self, *exc: object) -> bool:
        """Restore the instruction file from its backup if present."""
        if self.bak.exists():
            self.bak.rename(self.src)
            logger.info(f"🔓 Restored {self.filename}")
        return False

# ─── FILE DISCOVERY ─────────────────────────────────────────────────────────

def _is_safe_path(p: str, root_dir: Path) -> bool:
    """Return True if p resolves to a path inside root_dir (prevents path traversal)."""
    try:
        resolved = Path(p).resolve()
        return root_dir in resolved.parents or resolved == root_dir
    except Exception:
        return False


def _parse_bundle_manifest(bundle_path: Path, root_dir: Path) -> list[str]:
    """Parse a context-bundler manifest (JSON/YAML) into a safe-path file list."""
    text = bundle_path.read_text()
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        data = yaml.safe_load(text)

    if isinstance(data, dict):
        data = data.get("files", [])
    paths = []
    for item in data:
        p = item.get("path") if isinstance(item, dict) else item
        if p and _is_safe_path(str(p), root_dir):
            paths.append(str(p))
    return paths


def _parse_task_checklist(task_path: Path, root_dir: Path) -> list[str]:
    """Parse a Markdown checklist (`- [ ] \\`path\\`` lines) into a safe-path file list."""
    matches = [m.group(1) for m in re.finditer(r"- \[ \] `(.+)`", task_path.read_text())]
    return [m for m in matches if _is_safe_path(m, root_dir)]


def _crawl_directory(dir_path: Path, exts: set) -> list[str]:
    """Recursively crawl a directory for files matching the given extensions."""
    return [
        get_relative_path(f)
        for f in sorted(dir_path.rglob("*"))
        if f.is_file() and f.suffix.lower() in exts and not f.name.startswith(".")
    ]


def resolve_files(args: argparse.Namespace, config: dict) -> list[str]:
    """Find files from CLI args or Job config."""
    exts = config.get("ext", [".md"])
    exts = set(e if e.startswith(".") else f".{e}" for e in exts)

    root_dir = Path.cwd().resolve()

    # 1. Explicit Files
    if args.files:
        return [f for f in args.files if _is_safe_path(f, root_dir)]

    # 2. Bundle Manifest (JSON/YAML)
    bundle_path = args.bundle or config.get("bundle")
    if bundle_path:
        bundle_path = Path(bundle_path)
        if bundle_path.exists():
            return _parse_bundle_manifest(bundle_path, root_dir)

    # 3. Task Checklist
    task_path = args.files_from or config.get("files_from")
    if task_path:
        task_path = Path(task_path)
        if task_path.exists():
            return _parse_task_checklist(task_path, root_dir)

    # 4. Directory Crawl
    dir_path = args.dir or config.get("dir")
    if dir_path:
        dir_path = Path(dir_path)
        if dir_path.exists() and _is_safe_path(str(dir_path), root_dir):
            return _crawl_directory(dir_path, exts)

    return []

# ─── WORKER ENGINE ───────────────────────────────────────────────────────────

def _check_already_cached(file_path: str, job_config: dict, user_vars: dict, env_vars: dict) -> bool:
    """Run check_cmd (if configured) and return True if the file is already processed."""
    check_cmd_tmpl = job_config.get("check_cmd")
    if not check_cmd_tmpl:
        return False
    check_cmd_tmpl_args = shlex.split(check_cmd_tmpl)
    check_cmd_args = [arg.format_map({"file": file_path, **user_vars}) for arg in check_cmd_tmpl_args]
    return subprocess.run(check_cmd_args, capture_output=True, env=env_vars).returncode == 0


def _build_engine_command(engine: str, model: str, prompt: str, content: str) -> tuple[list, str]:
    """Build engine-specific CLI args and stdin payload for a single LLM call attempt."""
    cmd_args = [engine.lower()]

    # Apply intelligent default models if the 'haiku' placeholder or no model is provided
    effective_model = model
    if engine.lower() == "copilot" and (not model or model == "haiku" or model.startswith("claude")):
        effective_model = _load_cheapest_model("copilot", "gpt-5.4-nano")
    elif engine.lower() == "agy" and (not model or model == "haiku" or model.startswith("claude")):
        effective_model = _load_cheapest_model("agy", "gemini-3.5-flash")

    payload = content
    if engine.lower() == "claude":
        cmd_args.extend([
            "--model", effective_model,
            "-p", prompt,
            "--no-session-persistence"
        ])
    elif engine.lower() == "agy":
        cmd_args.extend([
            "--model", effective_model,
            "--dangerously-skip-permissions",
            "-p", prompt
        ])
    elif engine == "copilot":
        cmd_args = [
            "copilot", "--model", effective_model
        ]
        # Copilot CLI ignores stdin if -p is present. We must prepend the prompt.
        payload = f"Instruction: {prompt}\n\nTarget File Content:\n{content}"

    return cmd_args, payload


def _invoke_llm(cmd_args: list, payload: str, timeout: int, env_vars: dict) -> tuple:
    """Run the engine subprocess once and return (proc, combined_stdout_stderr)."""
    try:
        proc = subprocess.run(
            cmd_args,
            input=payload,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env_vars
        )
        combined_out = (proc.stderr + "\n" + proc.stdout).strip()
    except subprocess.TimeoutExpired:
        proc = subprocess.CompletedProcess(args=cmd_args, returncode=1, stdout="", stderr="TimeoutExpired")
        combined_out = "TimeoutExpired"
    except Exception as e:
        proc = subprocess.CompletedProcess(args=cmd_args, returncode=1, stdout="", stderr=str(e))
        combined_out = str(e)
    return proc, combined_out


def _call_with_retry(file_path: str, prompt: str, model: str, engine: str,
                      content: str, job_config: dict, env_vars: dict, result: dict) -> None:
    """Call the LLM engine with retry/backoff on rate limits; mutates result in place."""
    max_retries = job_config.get("max_retries", 3)
    backoff = 2

    for attempt in range(max_retries + 1):
        result["retries"] = attempt
        cmd_args, payload = _build_engine_command(engine, model, prompt, content)
        proc, combined_out = _invoke_llm(cmd_args, payload, job_config.get("timeout", 60), env_vars)

        if proc.returncode == 0 and proc.stdout.strip():
            # SUCCESS
            result["output"] = proc.stdout.strip()
            result["success"] = True
            return

        # ERROR HANDLING
        if "hit your limit" in combined_out.lower() or "rate limit" in combined_out.lower():
            if attempt < max_retries:
                wait = (backoff ** attempt) + random.uniform(0, 1)
                logger.warning(f"  ⌛ {file_path}: Rate limit. Backing off {wait:.1f}s...")
                time.sleep(wait)
                continue
            else:
                result["error"] = "RATE_LIMIT_EXCEEDED"
                return

        result["error"] = combined_out.strip()[:200]
        if attempt < max_retries:
            time.sleep(1)
            continue
        return


def _run_post_command(file_path: str, result: dict, job_config: dict, user_vars: dict, env_vars: dict) -> None:
    """Run post_cmd (if configured) after a successful LLM call; mutates result on failure."""
    post_cmd_tmpl = job_config.get("post_cmd")
    if not post_cmd_tmpl or result["skipped"]:
        return
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


def _new_worker_result(file_path: str) -> dict:
    """Build the initial per-file worker result dict."""
    return {
        "file": file_path,
        "success": False,
        "output": None,
        "error": None,
        "skipped": False,
        "retries": 0
    }


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
    result = _new_worker_result(file_path)

    if dry_run:
        logger.info(f"  [DRY] {file_path}")
        result["success"] = True
        return result

    # 1. Skip Check
    if _check_already_cached(file_path, job_config, user_vars, env_vars):
        logger.info(f"  ⏩ {file_path} (already cached)")
        result["success"] = True
        result["skipped"] = True
        return result

    # 2. Read content
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception as e:
        result["error"] = f"Read error: {e}"
        return result

    # 3. LLM Call with Retry
    _call_with_retry(file_path, prompt, model, engine, content, job_config, env_vars, result)

    if not result["success"]:
        return result

    # 4. Post-Command
    _run_post_command(file_path, result, job_config, user_vars, env_vars)

    if result["success"]:
        logger.info(f"  ✅ {file_path}")
    else:
        logger.error(f"  ❌ {file_path}: {result['error']}")

    return result

# ─── MAIN ───────────────────────────────────────────────────────────────────

def _build_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser for swarm_run.py."""
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
    parser.add_argument("--engine", type=str, default="claude", choices=["claude", "copilot", "agy"], help="The CLI engine to run workers through (gemini is deprecated — use agy)")
    parser.add_argument("--var", action="append", default=[])
    return parser


def _load_job(job_path: Path) -> tuple:
    """Parse a Job File's YAML frontmatter and prompt body; exits on invalid format."""
    full_text = job_path.read_text()
    # Use regex to safely parse frontmatter — split("---", 2) breaks on embedded --- in body
    fm_match = re.match(r'^---\n(.*?)\n---\n(.*)$', full_text, re.DOTALL)
    if not fm_match:
        print("❌ Invalid job file (no YAML frontmatter)")
        sys.exit(1)
    job_config = yaml.safe_load(fm_match.group(1)) or {}
    prompt = fm_match.group(2).strip()
    return job_config, prompt


def _load_checkpoint(job_stem: str, resume: bool) -> tuple:
    """Load the swarm checkpoint state file if --resume is set."""
    checkpoint_path = Path(f".swarm_state_{job_stem}.json")
    state = {"completed": [], "failed": {}}
    if resume and checkpoint_path.exists():
        state = json.loads(checkpoint_path.read_text())
        logger.info(f"🔄 Resuming from checkpoint: {len(state['completed'])} items done.")
    return checkpoint_path, state


def _resolve_overrides(args: argparse.Namespace, job_config: dict) -> tuple:
    """Resolve workers/model/vars from CLI overrides or Job config."""
    workers = args.workers or job_config.get("workers", 5)
    model = args.model or job_config.get("model", "haiku")
    user_vars = job_config.get("vars", {}) or {}
    for v in args.var:
        k, val = v.split("=", 1)
        user_vars[k.strip()] = val.strip()
    return workers, model, user_vars


def _run_swarm(pending: list, prompt: str, model: str, args: argparse.Namespace,
               job_config: dict, user_vars: dict, workers: int,
               state: dict, checkpoint_path: Path) -> tuple:
    """Run the thread pool over pending files, checkpointing every 5 completions."""
    results = []
    try:
        with suppress_monolithic_md(args.engine):
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {
                    pool.submit(execute_worker, f, prompt, model, args.engine, job_config, user_vars, os.environ.copy(), args.dry_run): f
                    for f in pending
                }
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    results.append(res)
                    if res["success"]:
                        state["completed"].append(res["file"])
                    else:
                        state["failed"][res["file"]] = res["error"]

                    # Checkpoint every 5 files
                    if len(results) % 5 == 0:
                        checkpoint_path.write_text(json.dumps(state, indent=2))
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Interrupted. Saving state...")
    finally:
        checkpoint_path.write_text(json.dumps(state, indent=2))

        # Summary
        success_count = sum(1 for r in results if r["success"])
        fail_count = sum(1 for r in results if not r["success"])
        logger.info("-" * 70)
        logger.info(f"🏁 DONE. Success: {success_count} | Failed: {fail_count}")

    return results, fail_count


def main() -> None:
    """CLI entry point: parse args, load job, resolve files, run the swarm, report results."""
    args = _build_arg_parser().parse_args()
    job_config, prompt = _load_job(args.job)
    checkpoint_path, state = _load_checkpoint(args.job.stem, args.resume)
    workers, model, user_vars = _resolve_overrides(args, job_config)

    # Resolve Files
    all_files = resolve_files(args, job_config)
    pending = [f for f in all_files if f not in state["completed"]]

    if not pending:
        logger.info("✨ Everything complete. Nothing to do.")
        return

    logger.info(f"🚀 Starting Swarm: {len(pending)} pending items ({len(all_files)} total)")
    logger.info(f"   Engine: {args.engine} | Model: {model} | Workers: {workers} | Dry-run: {args.dry_run}")
    print("-" * 70)

    _, fail_count = _run_swarm(pending, prompt, model, args, job_config, user_vars, workers, state, checkpoint_path)

    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
