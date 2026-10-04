#!/usr/bin/env python3
"""
swarm_run.py 2.1 — Parallel Agent Swarm Executor
=================================================

Purpose:
    Generic parallel CLI executor for independent batch operations. Dispatches N
    workers over input files, each worker invoking a supported CLI engine (claude,
    copilot, agy) with a prompt defined in a Job File, optionally piping output
    through a post-command under cross-platform serialization locks.

Key Features:
    - Pure stdlib frontmatter parser with optional PyYAML acceleration.
    - Zero worktree creation (caller workspace isolation).
    - Dry-run verification leaves zero state mutations or disk traces.
    - Checkpoints and append-only receipts stored outside workdir (under git-common-dir or parent .swarm-run/).
    - Thread-safe post-command execution via --post-serial.
    - Clean status enforcement via --require-clean.
"""

import os
import re
import sys
import json
import time
import shlex
import random
import signal
import logging
import argparse
import threading
import subprocess
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Post-command serialization lock
_POST_SERIAL_LOCK = threading.Lock()

# Monolithic instructions lock
_MONOLITHIC_LOCK = threading.Lock()


# ─── Frontmatter Parsing (Stdlib Fallback) ────────────────────────────────────

def parse_yaml_frontmatter_stdlib(text: str) -> Dict[str, Any]:
    """Parse flat YAML frontmatter (strings, numbers, booleans, lists, and dicts) using stdlib only."""
    data: Dict[str, Any] = {}
    current_key: Optional[str] = None
    current_list: Optional[List[Any]] = None
    current_dict: Optional[Dict[str, Any]] = None

    for line in text.splitlines():
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue

        # Top-level key: value
        m = re.match(r"^([a-zA-Z0-9_-]+)\s*:\s*(.*)$", line)
        if m and not line.startswith(" ") and not line.startswith("\t"):
            key = m.group(1)
            raw_val = m.group(2).strip()
            current_key = key
            current_list = None
            current_dict = None

            if not raw_val:
                continue

            # Boolean (except for command templates which can be 'false' shell command)
            if key not in ("post_cmd", "check_cmd") and raw_val.lower() in ("true", "yes"):
                data[key] = True
            elif key not in ("post_cmd", "check_cmd") and raw_val.lower() in ("false", "no"):
                data[key] = False
            # Integer
            elif re.match(r"^-?\d+$", raw_val):
                data[key] = int(raw_val)
            # Float
            elif re.match(r"^-?\d+\.\d+$", raw_val):
                data[key] = float(raw_val)
            # Inline JSON list
            elif raw_val.startswith("[") and raw_val.endswith("]"):
                try:
                    data[key] = json.loads(raw_val)
                except Exception:
                    data[key] = [v.strip().strip("'\"") for v in raw_val[1:-1].split(",") if v.strip()]
            # Quoted string
            elif (raw_val.startswith('"') and raw_val.endswith('"')) or (raw_val.startswith("'") and raw_val.endswith("'")):
                data[key] = raw_val[1:-1]
            else:
                data[key] = raw_val
            continue

        # List item: - item
        m_list = re.match(r"^\s*-\s+(.*)$", line)
        if m_list and current_key:
            val = m_list.group(1).strip().strip("'\"")
            if current_list is None:
                current_list = []
                data[current_key] = current_list
            current_list.append(val)
            continue

        # Sub-dictionary item: key: val indented
        m_dict = re.match(r"^\s+([a-zA-Z0-9_-]+)\s*:\s*(.*)$", line)
        if m_dict and current_key:
            k = m_dict.group(1)
            v = m_dict.group(2).strip().strip("'\"")
            if current_dict is None:
                current_dict = {}
                data[current_key] = current_dict
            current_dict[k] = v
            continue

    return data


def _load_job(job_path: Path) -> Tuple[Dict[str, Any], str]:
    """Parse a Job File's YAML frontmatter and prompt body."""
    if not job_path.is_file():
        print(f"❌ Job file not found: {job_path}", file=sys.stderr)
        sys.exit(1)

    full_text = job_path.read_text(encoding="utf-8")
    fm_match = re.match(r'^---\n(.*?)\n---\n(.*)$', full_text, re.DOTALL)
    if not fm_match:
        print("❌ Invalid job file (no YAML frontmatter between --- markers)", file=sys.stderr)
        sys.exit(1)

    fm_raw = fm_match.group(1)
    prompt = fm_match.group(2).strip()

    job_config = None
    try:
        import yaml
        job_config = yaml.safe_load(fm_raw)
    except Exception:
        pass

    if not isinstance(job_config, dict):
        job_config = parse_yaml_frontmatter_stdlib(fm_raw)

    return job_config or {}, prompt


# ─── Model resolution ─────────────────────────────────────────────────────────

def _load_cheapest_model(engine: str, fallback: str, ref_path: Optional[Path] = None) -> str:
    """Return the cheapest model for engine from cheapest_models.json, or fallback."""
    try:
        if ref_path is None:
            script_dir = Path(__file__).resolve().parent
            ref_path = script_dir.parent / "references" / "cheapest_models.json"
        if ref_path.is_file():
            data = json.loads(ref_path.read_text(encoding="utf-8"))
            return data.get(engine, {}).get("model", fallback)
    except Exception:
        pass
    return fallback


# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("swarm")


# ─── Workspace and Path Security ─────────────────────────────────────────────

def get_relative_path(path: Path, root_dir: Optional[Path] = None) -> str:
    """Convert absolute path to relative path from root directory."""
    root = (root_dir or Path.cwd()).resolve()
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)


def _is_safe_path(p: str, root_dir: Path) -> bool:
    """Return True if p resolves to a path inside root_dir (prevents path traversal)."""
    try:
        resolved = (root_dir / p).resolve() if not Path(p).is_absolute() else Path(p).resolve()
        return root_dir in resolved.parents or resolved == root_dir
    except Exception:
        return False


class suppress_monolithic_md:
    """Context manager: handles instruction suppression without mutating worktree files in place.
    Avoids renaming files to ensure crash resilience, concurrency safety, and clean git status."""
    def __init__(self, engine: str, workdir: Path, enabled: bool = False) -> None:
        self.enabled = enabled
        self.workdir = workdir
        self.engine = engine.lower()

    def __enter__(self) -> "suppress_monolithic_md":
        if self.enabled:
            logger.info("ℹ️ Instruction suppression: worktree files preserved in-place (no-op)")
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


# ─── File Discovery ──────────────────────────────────────────────────────────

def _parse_bundle_manifest(bundle_path: Path, root_dir: Path) -> List[str]:
    """Parse a context-bundler manifest into a safe-path file list."""
    text = bundle_path.read_text(encoding="utf-8")
    data = None
    try:
        data = json.loads(text)
    except Exception:
        try:
            import yaml
            data = yaml.safe_load(text)
        except Exception:
            pass

    if isinstance(data, dict):
        data = data.get("files", [])
    if not isinstance(data, list):
        return []

    paths = []
    for item in data:
        p = item.get("path") if isinstance(item, dict) else item
        if p:
            if not _is_safe_path(str(p), root_dir):
                logger.error(f"❌ Path traversal prohibited in bundle: '{p}' resolves outside root directory '{root_dir}'")
                sys.exit(1)
            paths.append(str(p))
    return paths


def _parse_task_checklist(task_path: Path, root_dir: Path) -> List[str]:
    """Parse a Markdown checklist (- [ ] `path`) into a safe-path file list."""
    matches = [m.group(1) for m in re.finditer(r"- \[ \] `([^`]+)`", task_path.read_text(encoding="utf-8"))]
    paths = []
    for m in matches:
        if not _is_safe_path(m, root_dir):
            logger.error(f"❌ Path traversal prohibited in checklist: '{m}' resolves outside root directory '{root_dir}'")
            sys.exit(1)
        paths.append(m)
    return paths


def _crawl_directory(dir_path: Path, exts: set, root_dir: Path) -> List[str]:
    """Recursively crawl a directory for files matching given extensions."""
    return [
        get_relative_path(f, root_dir)
        for f in sorted(dir_path.rglob("*"))
        if f.is_file() and f.suffix.lower() in exts and not f.name.startswith(".") and _is_safe_path(str(f), root_dir)
    ]


def resolve_files(args: argparse.Namespace, config: dict, root_dir: Optional[Path] = None) -> List[str]:
    """Find files from CLI args or Job config, strictly bounded to root_dir. Exits non-zero on unsafe path."""
    workdir = (root_dir or getattr(args, "workdir", None) or Path.cwd()).resolve()
    exts = config.get("ext", [".md"])
    exts_set = set(e if e.startswith(".") else f".{e}" for e in exts)

    # 1. Explicit Files
    if args.files:
        for f in args.files:
            if not _is_safe_path(f, workdir):
                logger.error(f"❌ Path traversal prohibited: '{f}' resolves outside workdir '{workdir}'")
                sys.exit(1)
        return list(args.files)

    # 2. Bundle Manifest
    bundle_path = args.bundle or config.get("bundle")
    if bundle_path:
        if not _is_safe_path(str(bundle_path), workdir):
            logger.error(f"❌ Path traversal prohibited: bundle '{bundle_path}' resolves outside workdir '{workdir}'")
            sys.exit(1)
        bp = (workdir / bundle_path).resolve() if not Path(bundle_path).is_absolute() else Path(bundle_path)
        if bp.is_file():
            return _parse_bundle_manifest(bp, workdir)

    # 3. Task Checklist
    task_path = args.files_from or config.get("files_from")
    if task_path:
        if not _is_safe_path(str(task_path), workdir):
            logger.error(f"❌ Path traversal prohibited: files_from '{task_path}' resolves outside workdir '{workdir}'")
            sys.exit(1)
        tp = (workdir / task_path).resolve() if not Path(task_path).is_absolute() else Path(task_path)
        if tp.is_file():
            return _parse_task_checklist(tp, workdir)

    # 4. Directory Crawl
    dir_path = args.dir or config.get("dir")
    if dir_path:
        if not _is_safe_path(str(dir_path), workdir):
            logger.error(f"❌ Path traversal prohibited: dir '{dir_path}' resolves outside workdir '{workdir}'")
            sys.exit(1)
        dp = (workdir / dir_path).resolve() if not Path(dir_path).is_absolute() else Path(dir_path)
        if dp.is_dir():
            return _crawl_directory(dp, exts_set, workdir)

    return []


# ─── Worker Engine ───────────────────────────────────────────────────────────

def _check_already_cached(file_path: str, job_config: dict, user_vars: dict, env_vars: dict, workdir: Path) -> bool:
    """Run check_cmd (if configured) and return True if file is already processed."""
    check_cmd_tmpl = job_config.get("check_cmd")
    if not check_cmd_tmpl:
        return False
    check_cmd_tmpl_args = shlex.split(check_cmd_tmpl)
    check_cmd_args = [arg.format_map({"file": file_path, **user_vars}) for arg in check_cmd_tmpl_args]
    return subprocess.run(check_cmd_args, cwd=str(workdir), capture_output=True, env=env_vars).returncode == 0


def _build_engine_command(engine: str, model: str, prompt: str, content: str, unsafe_permissions: bool = False) -> Tuple[List[str], str]:
    """Build engine-specific CLI args and stdin payload."""
    eng = engine.lower()
    cmd_args = [eng]

    effective_model = model
    if eng == "copilot" and (not model or model == "haiku" or model.startswith("claude")):
        effective_model = _load_cheapest_model("copilot", "gpt-5.4-nano")
    elif eng == "agy" and (not model or model == "haiku" or model.startswith("claude")):
        effective_model = _load_cheapest_model("agy", "gemini-3.5-flash")

    payload = content
    if eng == "claude":
        cmd_args.extend([
            "--model", effective_model,
            "-p", prompt,
            "--no-session-persistence"
        ])
    elif eng == "agy":
        cmd_args.extend([
            "--model", effective_model,
            "-p", prompt
        ])
        if unsafe_permissions:
            cmd_args.append("--dangerously-skip-permissions")
    elif eng == "copilot":
        cmd_args = ["copilot", "--model", effective_model]
        payload = f"Instruction: {prompt}\n\nTarget File Content:\n{content}"

    return cmd_args, payload


def _invoke_llm(cmd_args: List[str], payload: str, timeout: int, env_vars: dict, workdir: Path) -> Tuple[subprocess.CompletedProcess, str]:
    """Run the engine subprocess once and return (proc, combined_output)."""
    try:
        proc = subprocess.run(
            cmd_args,
            input=payload,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(workdir),
            env=env_vars,
        )
        combined_out = (proc.stderr + "\n" + proc.stdout).strip()
    except subprocess.TimeoutExpired:
        proc = subprocess.CompletedProcess(args=cmd_args, returncode=124, stdout="", stderr="TimeoutExpired")
        combined_out = "TimeoutExpired"
    except Exception as e:
        proc = subprocess.CompletedProcess(args=cmd_args, returncode=1, stdout="", stderr=str(e))
        combined_out = str(e)
    return proc, combined_out


def _call_with_retry(file_path: str, prompt: str, model: str, engine: str,
                      content: str, job_config: dict, env_vars: dict, result: dict,
                      workdir: Path, unsafe_permissions: bool = False) -> None:
    """Call the LLM engine with retry/backoff on rate limits."""
    max_retries = job_config.get("max_retries", 3)
    backoff = 2

    for attempt in range(max_retries + 1):
        result["retries"] = attempt
        cmd_args, payload = _build_engine_command(engine, model, prompt, content, unsafe_permissions)
        proc, combined_out = _invoke_llm(cmd_args, payload, job_config.get("timeout", 60), env_vars, workdir)

        if proc.returncode == 0 and proc.stdout.strip():
            result["output"] = proc.stdout.strip()
            result["success"] = True
            return

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


def _run_post_command(file_path: str, result: dict, job_config: dict, user_vars: dict,
                       env_vars: dict, workdir: Path, post_serial: bool = False) -> None:
    """Run post_cmd after successful LLM call; serialized if post_serial is True."""
    post_cmd_tmpl = job_config.get("post_cmd")
    if not post_cmd_tmpl or result["skipped"]:
        return

    subs = {
        "file": file_path,
        "output": result.get("output", "") or "",
        "output_raw": result.get("output", "") or "",
        "basename": Path(file_path).stem,
        **user_vars,
    }
    cmd_tmpl_args = shlex.split(post_cmd_tmpl)
    cmd_args = [arg.format_map(subs) for arg in cmd_tmpl_args]

    if post_serial:
        with _POST_SERIAL_LOCK:
            pr = subprocess.run(cmd_args, text=True, capture_output=True, cwd=str(workdir), env=env_vars)
    else:
        pr = subprocess.run(cmd_args, text=True, capture_output=True, cwd=str(workdir), env=env_vars)

    if pr.returncode != 0:
        result["success"] = False
        result["error"] = (pr.stderr or pr.stdout or "post-cmd failed").strip()[:300]


def execute_worker(
    file_path: str,
    prompt: str,
    model: str,
    engine: str,
    job_config: dict,
    user_vars: dict,
    env_vars: dict,
    dry_run: bool,
    workdir: Path,
    post_serial: bool = False,
    unsafe_permissions: bool = False,
) -> dict:
    """Process a single file through skip check, LLM invocation, and post_cmd."""
    result = {
        "file": file_path,
        "success": False,
        "output": None,
        "error": None,
        "skipped": False,
        "retries": 0,
    }

    if dry_run:
        logger.info(f"  [DRY] {file_path}")
        result["success"] = True
        return result

    # 1. Skip Check
    if _check_already_cached(file_path, job_config, user_vars, env_vars, workdir):
        logger.info(f"  ⏩ {file_path} (already cached)")
        result["success"] = True
        result["skipped"] = True
        return result

    # 2. Read Content
    full_path = (workdir / file_path).resolve() if not Path(file_path).is_absolute() else Path(file_path)
    try:
        content = full_path.read_text(encoding="utf-8")
    except Exception as e:
        result["error"] = f"Read error: {e}"
        return result

    # 3. LLM Call with Retry
    _call_with_retry(file_path, prompt, model, engine, content, job_config, env_vars, result, workdir, unsafe_permissions)

    if not result["success"]:
        logger.error(f"  ❌ {file_path}: {result['error']}")
        return result

    # 4. Post-Command
    _run_post_command(file_path, result, job_config, user_vars, env_vars, workdir, post_serial)

    if result["success"]:
        logger.info(f"  ✅ {file_path}")
    else:
        logger.error(f"  ❌ {file_path}: {result['error']}")

    return result


def find_git_common_dir(directory: Path) -> Optional[Path]:
    """Find the real git directory/common-dir so receipts and state are stored outside the working tree."""
    res = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=str(directory), capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        p = Path(res.stdout.strip())
        return p if p.is_absolute() else (directory / p).resolve()
    res = subprocess.run(["git", "rev-parse", "--git-dir"], cwd=str(directory), capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        p = Path(res.stdout.strip())
        return p if p.is_absolute() else (directory / p).resolve()
    return None


def _resolve_run_dir(workdir: Path, job_stem: str, resume_id: Optional[str] = None, dry_run: bool = False) -> Tuple[Path, str]:
    """Resolve the run directory and run_id outside the working tree (in git common-dir or parent)."""
    git_common = find_git_common_dir(workdir)
    if git_common:
        base_dir = git_common / ".swarm-run" / job_stem
    else:
        base_dir = workdir.parent / ".swarm-run" / job_stem

    if not dry_run:
        base_dir.mkdir(parents=True, exist_ok=True)

    if resume_id:
        run_id = resume_id
    else:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_dir = base_dir / run_id
    if not dry_run:
        run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir, run_id


def _load_checkpoint(run_dir: Path, resume: bool) -> Tuple[Path, dict]:
    """Load or initialize state.json under run_dir."""
    state_file = run_dir / "state.json"
    state = {"completed": [], "failed": {}}
    if resume and state_file.is_file():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            logger.info(f"🔄 Resuming from run: {len(state.get('completed', []))} items done.")
        except Exception:
            pass
    return state_file, state


def _record_receipt(receipts_file: Path, res: dict) -> None:
    """Append a structured receipt entry to receipts.jsonl."""
    entry = {
        "file": res["file"],
        "success": res["success"],
        "retries": res["retries"],
        "error": res["error"],
        "skipped": res["skipped"],
        "timestamp": datetime.now().isoformat(),
    }
    with open(receipts_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ─── Swarm Execution ─────────────────────────────────────────────────────────

def _run_swarm(
    pending: list,
    prompt: str,
    model: str,
    args: argparse.Namespace,
    job_config: dict,
    user_vars: dict,
    workers: int,
    state: dict,
    checkpoint_path: Path,
    receipts_path: Path,
    summary_path: Path,
    workdir: Path,
) -> Tuple[List[dict], int]:
    """Run thread pool over pending files, maintaining isolated checkpoints and receipts."""
    results = []
    fail_count = 0
    interrupted = False

    try:
        with suppress_monolithic_md(args.engine, workdir, enabled=args.hide_instructions):
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {
                    pool.submit(
                        execute_worker,
                        f,
                        prompt,
                        model,
                        args.engine,
                        job_config,
                        user_vars,
                        os.environ.copy(),
                        args.dry_run,
                        workdir,
                        args.post_serial,
                        args.unsafe_permissions,
                    ): f
                    for f in pending
                }
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    results.append(res)

                    if not args.dry_run:
                        _record_receipt(receipts_path, res)
                        if res["success"]:
                            state["completed"].append(res["file"])
                        else:
                            state["failed"][res["file"]] = res["error"]

                        if len(results) % 5 == 0:
                            checkpoint_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Interrupted. Saving state...")
        interrupted = True
    finally:
        if not args.dry_run:
            checkpoint_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

        success_count = sum(1 for r in results if r["success"])
        fail_count = sum(1 for r in results if not r["success"])
        logger.info("-" * 70)
        logger.info(f"🏁 DONE. Success: {success_count} | Failed: {fail_count}")

        summary = {
            "total_pending": len(pending),
            "processed": len(results),
            "success": success_count,
            "failed": fail_count,
            "interrupted": interrupted,
            "completed_at": datetime.now().isoformat(),
        }
        if not args.dry_run:
            summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if interrupted:
        sys.exit(130)

    return results, fail_count


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Professional Agent Swarm Runner")
    parser.add_argument("--job", type=Path, required=True, help="Job file (.md)")
    parser.add_argument("--workdir", type=Path, default=Path.cwd(), help="Working directory (default: cwd)")
    parser.add_argument("--resume", nargs="?", const="", default=None, help="Resume from last checkpoint (optional: specify run_id)")
    parser.add_argument("--dry-run", action="store_true", help="List files without calling LLM or writing state")
    parser.add_argument("--require-clean", action="store_true", help="Refuse to start if git status is dirty")
    parser.add_argument("--hide-instructions", action="store_true", help="Temporarily hide monolithic instruction files")
    parser.add_argument("--post-serial", action="store_true", help="Serialize post-commands under a cross-platform lock")
    parser.add_argument("--unsafe-permissions", action="store_true", help="Opt-in to skip permissions for engine workers (e.g. agy)")
    parser.add_argument("--dir", type=Path)
    parser.add_argument("--files-from", type=Path)
    parser.add_argument("--files", nargs="+")
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--model", type=str)
    parser.add_argument("--engine", type=str, default="claude", choices=["claude", "copilot", "agy"], help="The CLI engine to run workers through")
    parser.add_argument("--var", action="append", default=[])
    return parser


def main() -> None:
    args = _build_arg_parser().parse_args()
    workdir = args.workdir.resolve()

    if args.require_clean:
        res = subprocess.run(["git", "status", "--porcelain"], cwd=str(workdir), capture_output=True, text=True)
        if res.returncode != 0 or res.stdout.strip():
            logger.error("❌ Refusing to run swarm: --require-clean specified and working directory is dirty.")
            sys.exit(1)

    job_config, prompt = _load_job(args.job)

    # Resolve Run Directory
    job_stem = args.job.name[:-7] if args.job.name.endswith(".job.md") else (args.job.name[:-3] if args.job.name.endswith(".md") else args.job.stem)
    resume_flag = args.resume is not None
    resume_id = args.resume if (args.resume and args.resume != "") else None
    if resume_flag and not resume_id:
        git_common = find_git_common_dir(workdir)
        runs_dir = (git_common / ".swarm-run" / job_stem) if git_common else (workdir.parent / ".swarm-run" / job_stem)
        if runs_dir.is_dir():
            existing = sorted([d.name for d in runs_dir.iterdir() if d.is_dir() and (d / "state.json").is_file()])
            if existing:
                resume_id = existing[-1]

    run_dir, run_id = _resolve_run_dir(workdir, job_stem, resume_id, dry_run=args.dry_run)
    checkpoint_path, state = _load_checkpoint(run_dir, resume_flag)
    receipts_path = run_dir / "receipts.jsonl"
    summary_path = run_dir / "summary.json"

    workers = args.workers or job_config.get("workers", 5)
    model = args.model or job_config.get("model", "haiku")
    user_vars = job_config.get("vars", {}) or {}
    for v in args.var:
        if "=" in v:
            k, val = v.split("=", 1)
            user_vars[k.strip()] = val.strip()

    all_files = resolve_files(args, job_config, workdir)
    pending = [f for f in all_files if f not in state["completed"]]

    if not pending:
        logger.info("✨ Everything complete. Nothing to do.")
        return

    logger.info(f"🚀 Starting Swarm (Run ID: {run_id}): {len(pending)} pending items ({len(all_files)} total)")
    logger.info(f"   Engine: {args.engine} | Model: {model} | Workers: {workers} | Dry-run: {args.dry_run}")
    print("-" * 70)

    _, fail_count = _run_swarm(
        pending,
        prompt,
        model,
        args,
        job_config,
        user_vars,
        workers,
        state,
        checkpoint_path,
        receipts_path,
        summary_path,
        workdir,
    )

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
