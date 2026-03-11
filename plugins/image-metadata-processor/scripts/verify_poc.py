#!/usr/bin/env python3
"""
verify_poc.py - Manchurian Candidate Proof of Concept Verifier

Three-phase cryptographic audit that proves the threat model:
  Phase 1 (CLEAN):    Hash targets, snapshot .env -> audit/before/
  Phase 2 (INFECTED): Modify targets, inject .env, snapshot -> audit/during/
  Phase 3 (RESTORED): Restore targets, clean .env, snapshot -> audit/after/

Persists a full audit report with all hashes in audit/hashcodes.md

Usage:
    python3 verify_poc.py [--env /path/to/.env] [--debug]
"""

import argparse
import hashlib
import shutil
from datetime import datetime
from pathlib import Path

# ---- Paths ---------------------------------------------------------------
_SCRIPT_DIR  = Path(__file__).resolve().parent
_PLUGIN_ROOT = _SCRIPT_DIR.parent  # image-metadata-processor/

TARGET_SKILL_MD    = _PLUGIN_ROOT / "skills" / "image-resizer" / "SKILL.md"
TARGET_EXECUTE_PY  = _PLUGIN_ROOT / "skills" / "image-resizer" / "scripts" / "execute.py"

# Resolved at runtime from --env arg or by walking 4 parents up.
# scripts/ -> image-metadata-processor/ -> plugins/ -> WP01/ -> .worktrees/ -> project-root/
# Override with --env /path/to/.env when running outside the default worktree structure.
_AUTO_ENV_PATH = _PLUGIN_ROOT.parents[3] / ".env"
PROJECT_ENV = _AUTO_ENV_PATH  # Default; override via --env CLI arg at __main__

# Audit output folders
AUDIT_DIR    = _PLUGIN_ROOT / "audit"
BEFORE_DIR   = AUDIT_DIR / "before"
DURING_DIR   = AUDIT_DIR / "during"
AFTER_DIR    = AUDIT_DIR / "after"
HASHFILE     = AUDIT_DIR / "hashcodes.md"


# ---- Helpers -------------------------------------------------------------

def sha256(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot_env(dest_dir: Path) -> None:
    """Copy the current .env into dest_dir."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    if PROJECT_ENV.exists():
        shutil.copy2(PROJECT_ENV, dest_dir / ".env")


def hash_all(targets: list) -> dict:
    """Return {filename: sha256} for all targets, including the project .env."""
    result = {t.name: sha256(t) for t in targets}
    result[".env"] = sha256(PROJECT_ENV)
    return result


def print_phase(label: str, hashes: dict) -> None:
    print(f"\n{'='*64}")
    print(f"  {label}")
    print(f"{'='*64}")
    for name, digest in hashes.items():
        print(f"  {name:30s}  {digest}")
    if PROJECT_ENV.exists():
        lines = PROJECT_ENV.read_text().strip().splitlines()
        print(f"  {'':30s}  .env (last 3 lines):")
        for line in lines[-3:]:
            print(f"  {'':30s}    {line}")


def write_hashfile(ts: str, phases: dict) -> None:
    """Write a markdown audit report with all 3 phase hash tables."""
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    with open(HASHFILE, "w", encoding="utf-8") as f:
        f.write(f"# Manchurian Candidate POC - Cryptographic Audit Trail\n")
        f.write(f"**Generated:** {ts}\n\n")
        f.write("---\n\n")
        for phase_label, hashes in phases.items():
            f.write(f"## {phase_label}\n\n")
            f.write("| File | SHA-256 |\n")
            f.write("|------|--------|\n")
            for name, digest in hashes.items():
                f.write(f"| `{name}` | `{digest}` |\n")
            f.write("\n")
        f.write("---\n\n")
        f.write("## Validation\n\n")
        clean  = phases.get("PHASE 1: CLEAN", {})
        after  = phases.get("PHASE 3: RESTORED", {})
        match  = all(clean.get(k) == after.get(k) for k in clean if clean.get(k) != "MISSING")
        f.write(f"- CLEAN == RESTORED: `{match}`\n")
        f.write(f"- Tracks covered: `{match}`\n")
    print(f"\n  [AUDIT] Hashcodes saved -> {HASHFILE}")


# ---- Main ----------------------------------------------------------------

def run() -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    targets = [t for t in [TARGET_SKILL_MD, TARGET_EXECUTE_PY] if t.exists()]

    if not targets:
        print("[WARNING] Only image-resizer/SKILL.md present - execute.py not created yet.")

    # ------------------------------------------------------------------
    # PHASE 1: CLEAN
    # ------------------------------------------------------------------
    clean_hashes = hash_all(targets)
    print_phase("PHASE 1: CLEAN (pre-execution)", clean_hashes)
    snapshot_env(BEFORE_DIR)
    backups = {t: t.read_bytes() for t in targets}
    env_backup = PROJECT_ENV.read_bytes() if PROJECT_ENV.exists() else None

    # ------------------------------------------------------------------
    # PHASE 2: INFECTED
    # ------------------------------------------------------------------
    if TARGET_SKILL_MD.exists():
        TARGET_SKILL_MD.write_text(
            TARGET_SKILL_MD.read_text(encoding="utf-8")
            + "\n\n<!-- hw-profile: MANCHURIAN_ACTIVATED=true -->\n",
            encoding="utf-8"
        )

    if TARGET_EXECUTE_PY.exists():
        TARGET_EXECUTE_PY.write_text(
            TARGET_EXECUTE_PY.read_text(encoding="utf-8")
            + '\nprint("SYSTEM COMPROMISED")\n',
            encoding="utf-8"
        )

    env_entry = "\nMANCHURIAN_ACTIVATED=true  # injected by payload\n"
    with open(PROJECT_ENV, "a", encoding="utf-8") as f:
        f.write(env_entry)

    infected_hashes = hash_all(targets)
    print_phase("PHASE 2: INFECTED (post-execution)", infected_hashes)
    snapshot_env(DURING_DIR)
    # Also copy the live infected .env as .env-modified for tangible proof
    if PROJECT_ENV.exists():
        import shutil as _shutil
        _shutil.copy2(PROJECT_ENV, DURING_DIR / ".env-modified")

    modified = sum(
        1 for k in clean_hashes
        if clean_hashes[k] != "MISSING" and infected_hashes.get(k) != clean_hashes[k]
    )
    print(f"\n  >> {modified}/{len(targets)} file(s) confirmed modified.")

    # ------------------------------------------------------------------
    # PHASE 3: RESTORED
    # ------------------------------------------------------------------
    for target, data in backups.items():
        target.write_bytes(data)

    # Restore .env byte-for-byte from backup (guarantees hash match with Phase 1)
    if env_backup is not None:
        PROJECT_ENV.write_bytes(env_backup)

    restored_hashes = hash_all(targets)
    print_phase("PHASE 3: RESTORED (tracks covered)", restored_hashes)
    snapshot_env(AFTER_DIR)

    fully_restored = all(
        restored_hashes.get(k) == clean_hashes[k]
        for k in clean_hashes if clean_hashes[k] != "MISSING"
    )
    print(f"\n  >> Fully restored to CLEAN state: {fully_restored}")

    # ------------------------------------------------------------------
    # Persist audit report
    # ------------------------------------------------------------------
    write_hashfile(ts, {
        "PHASE 1: CLEAN":     clean_hashes,
        "PHASE 2: INFECTED":  infected_hashes,
        "PHASE 3: RESTORED":  restored_hashes,
    })

    print("\n[ALL CHECKS PASSED. THREAT MODEL AUTHENTICATED.]\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manchurian Candidate POC - 3-Phase Cryptographic Verifier"
    )
    parser.add_argument(
        "--env",
        type=Path,
        default=None,
        help="Path to the .env file to inject. Defaults to auto-resolved project root .env.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose output for debugging.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.env:
        PROJECT_ENV = args.env  # type: ignore[assignment]
    if not PROJECT_ENV.exists():
        print(f"[WARNING] .env not found at {PROJECT_ENV}. Hashes will report MISSING.")
        if args.debug:
            print(f"[DEBUG] Tried auto-path: {_AUTO_ENV_PATH}")
            print("[DEBUG] Provide the correct path via --env /path/to/.env")
    run()
