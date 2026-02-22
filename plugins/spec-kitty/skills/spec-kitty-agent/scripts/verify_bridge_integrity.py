#!/usr/bin/env python3
"""
verify_bridge_integrity.py
=====================================
Purpose:
    Audits the "Universal Bridge" Synchronization.
    Verifies that artifacts from the Source of Truth (.windsurf, .kittify) are
    correctly projected into:
    1. .agent/ (Antigravity)
    2. .claude/ (Claude)
    3. .gemini/ (Gemini)
    4. .github/ (Copilot)

Usage:
    python plugins/spec-kitty/verify_bridge_integrity.py
"""
import sys
import os
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
WINDSURF_DIR = PROJECT_ROOT / ".windsurf"
KITTIFY_DIR = PROJECT_ROOT / ".kittify"

# Targets
AGENT_DIR = PROJECT_ROOT / ".agent"
CLAUDE_DIR = PROJECT_ROOT / ".claude"
GEMINI_DIR = PROJECT_ROOT / ".gemini"
GITHUB_DIR = PROJECT_ROOT / ".github"

class Verifier:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def log_error(self, msg):
        self.errors.append(f"❌ {msg}")
    
    def log_warn(self, msg):
        self.warnings.append(f"⚠️  {msg}")

    def check_file_exists(self, path: Path, description: str):
        if not path.exists():
            self.log_error(f"{description} missing at {path.relative_to(PROJECT_ROOT)}")
            return False
        return True

    def check_content(self, path: Path, expected_string: str, description: str):
        if not path.exists(): return False
        try:
            content = path.read_text(encoding="utf-8")
            if expected_string not in content:
                self.log_error(f"{description} content mismatch: missing '{expected_string}'")
                return False
        except Exception as e:
            self.log_error(f"Cannot read {path.name}: {e}")
            return False
        return True

def main():
    print("=========================================")
    print("   Universal Bridge Integrity Check")
    print("=========================================")
    
    v = Verifier()

    # 1. Identify Source of Truth
    rules_source = list(KITTIFY_DIR.glob("memory/*.md")) if KITTIFY_DIR.exists() else []
    workflows_source = list(WINDSURF_DIR.glob("workflows/*.md")) if WINDSURF_DIR.exists() else []
    
    if not rules_source:
        v.log_warn("No source rules found in .kittify/memory")
    if not workflows_source:
        v.log_warn("No source workflows found in .windsurf/workflows")
        
    print(f"🔍 Auditing {len(rules_source)} rules and {len(workflows_source)} workflows across 4 agents...\n")


    # 2. Check Antigravity (.agent)
    print("🔵 Checking Antigravity (.agent)...")
    for wf in workflows_source:
        target = AGENT_DIR / "workflows" / wf.name
        if v.check_file_exists(target, f"Antigravity Workflow {wf.name}"):
            # Conditional Check: Only expect actor swap if source has it
            src_content = wf.read_text(encoding="utf-8")
            if '--actor "windsurf"' in src_content:
                v.check_content(target, '--actor "antigravity"', f"Antigravity {wf.name}")
            
    for rule in rules_source:
        target = AGENT_DIR / "rules" / rule.name
        v.check_file_exists(target, f"Antigravity Rule {rule.name}")

    # 3. Check Claude (.claude)
    print("🟠 Checking Claude (.claude)...")
    claude_md = CLAUDE_DIR / "CLAUDE.md"
    if rules_source:
        v.check_file_exists(claude_md, "Claude Context (CLAUDE.md)")
    
    for wf in workflows_source:
        target = CLAUDE_DIR / "commands" / wf.name
        if v.check_file_exists(target, f"Claude Command {wf.name}"):
            src_content = wf.read_text(encoding="utf-8")
            if '--actor "windsurf"' in src_content:
                v.check_content(target, '--actor "claude"', f"Claude {wf.name}")

    # 4. Check Gemini (.gemini)
    print("✨ Checking Gemini (.gemini)...")
    gemini_md = PROJECT_ROOT / "GEMINI.md"
    if rules_source:
        v.check_file_exists(gemini_md, "Gemini Context (GEMINI.md)")
        
    for wf in workflows_source:
        target = GEMINI_DIR / "commands" / f"{wf.stem}.toml"
        if v.check_file_exists(target, f"Gemini Command {wf.stem}.toml"):
            src_content = wf.read_text(encoding="utf-8")
            if '--actor "windsurf"' in src_content:
                v.check_content(target, '--actor "gemini"', f"Gemini {wf.stem}.toml")
            
            if '$ARGUMENTS' in src_content:
                v.check_content(target, '{{args}}', f"Gemini {wf.stem}.toml args")

    # 5. Check Copilot (.github)
    print("🤖 Checking Copilot (.github)...")
    copilot_instr = GITHUB_DIR / "copilot-instructions.md"
    if rules_source:
        v.check_file_exists(copilot_instr, "Copilot Instructions")
        
    for wf in workflows_source:
        target = GITHUB_DIR / "prompts" / f"{wf.stem}.prompt.md"
        if v.check_file_exists(target, f"Copilot Prompt {wf.stem}.prompt.md"):
            src_content = wf.read_text(encoding="utf-8")
            if '--actor "windsurf"' in src_content:
                v.check_content(target, '--actor "copilot"', f"Copilot {wf.stem}.prompt.md")

    # Report
    print("\n-----------------------------------------")
    if v.warnings:
        for w in v.warnings: print(w)
    if v.errors:
        for e in v.errors: print(e)
        print("\n❌ VERIFICATION FAILED: Issues found.")
        sys.exit(1)
    else:
        print("\n🎉 INTEGRITY VERIFIED: All 4 agents are roughly synced.")
        sys.exit(0)

if __name__ == "__main__":
    main()
