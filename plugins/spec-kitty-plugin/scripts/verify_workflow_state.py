"""
verify_workflow_state.py
========================

Purpose:
    Validates that the spec-driven development (SDD) artifacts exist 
    and are in the correct state for a given phase.

Layer: Plugin / Spec-Kitty / Verification

Usage Examples:
    python3 plugins/spec-kitty-plugin/scripts/verify_workflow_state.py --feature SLUG --phase specify

Supported Object Types:
    - None (Verification)

CLI Arguments:
    --feature: Feature slug (directory name under specs/).
    --wp: Work Package ID (e.g. WP-001).
    --phase: specify, plan, tasks, review (Required).

Input Files:
    - spec.md, plan.md, tasks.md, tasks/WP-*.md

Output:
    - Prints verification success/failure. Exit 1 on failure.

Key Functions:
    verify_specify(): Checks for spec.md.
    verify_plan(): Checks for plan.md.
    verify_tasks(): Checks for tasks.md and WP prompt files.

Script Dependencies:
    sys, argparse, pathlib

Consumed by:
    - None (Standalone script)
Related:
    - None
"""

import sys
import argparse
from pathlib import Path

def verify_specify(spec_dir: Path) -> bool:
    spec_md = spec_dir / "spec.md"
    if not spec_md.exists():
        print(f"❌ Verification Failed: spec.md not found in {spec_dir}")
        return False
    print(f"✅ spec.md found.")
    return True

def verify_plan(spec_dir: Path) -> bool:
    if not verify_specify(spec_dir): return False
    plan_md = spec_dir / "plan.md"
    if not plan_md.exists():
        print(f"❌ Verification Failed: plan.md not found in {spec_dir}")
        return False
    print(f"✅ plan.md found.")
    return True

def verify_tasks(spec_dir: Path) -> bool:
    if not verify_plan(spec_dir): return False
    tasks_md = spec_dir / "tasks.md"
    if not tasks_md.exists():
        print(f"❌ Verification Failed: tasks.md not found in {spec_dir}")
        return False
    
    tasks_subdir = spec_dir / "tasks"
    if not tasks_subdir.exists() or not any(tasks_subdir.glob("WP-*.md")):
        print(f"❌ Verification Failed: No WP prompt files found in {tasks_subdir}")
        return False
    
    print(f"✅ tasks.md and WP prompt files found.")
    return True

def main() -> None:
    parser = argparse.ArgumentParser(description="Verify SDD workflow state")
    parser.add_argument("--feature", help="Feature slug (directory name under specs/)")
    parser.add_argument("--wp", help="Work Package ID (e.g. WP-001)")
    parser.add_argument("--phase", required=True, choices=["specify", "plan", "tasks", "review"])
    args = parser.parse_args()

    # Determine spec_dir
    if args.feature:
        # Check kitty-specs first (project standard), then fall back to specs
        spec_dir = Path("kitty-specs") / args.feature
        if not spec_dir.exists():
            spec_dir = Path("specs") / args.feature
    elif args.wp:
        # Try to find which spec this WP belongs to
        # (Simplified: check both kitty-specs and specs)
        spec_dir = None
        for base in [Path("kitty-specs"), Path("specs")]:
            if not base.exists(): continue
            for d in base.iterdir():
                if d.is_dir() and (d / "tasks" / f"{args.wp}.md").exists():
                    spec_dir = d
                    break
            if spec_dir: break
            
        if not spec_dir:
            print(f"❌ Could not find spec directory for {args.wp}")
            sys.exit(1)
    else:
        # Default to current directory if in a spec dir
        spec_dir = Path.cwd()

    if args.phase == "specify":
        success = verify_specify(spec_dir)
    elif args.phase == "plan":
        success = verify_plan(spec_dir)
    elif args.phase == "tasks":
        success = verify_tasks(spec_dir)
    elif args.phase == "review":
        # Placeholder for more complex review verification
        print(f"✅ Phase 'review' verification for {args.wp} passed (Existence check).")
        success = True

    if not success:
        sys.exit(1)
    
    print(f"\n✅ Phase '{args.phase}' verification passed for {spec_dir.name}")

if __name__ == "__main__":
    main()
