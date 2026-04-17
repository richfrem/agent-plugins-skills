---
concept: quick-wins-concrete-improvements-inspired-by-superpowers
source: research-docs
source_file: superpowers/quick-wins.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.464635+00:00
cluster: skill
content_hash: 9899f26e5801766b
---

# Quick Wins: Concrete Improvements Inspired by superpowers

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Quick Wins: Concrete Improvements Inspired by superpowers

> **ADR Constraints Applied (revised after antigravity review)**
> All implementation paths comply with ADR-002 (hub-and-spoke scripts),
> ADR-003 (zero duplication / file-level symlinks only), and ADR-004
> (self-contained plugins at deploy time, cross-plugin symlinks in source).
> "Copy" only happens at install time via plugin_installer.py / npx skills add.

---

## Quick Win 1: Add verification-before-completion as a Canonical Skill

**What to build/change:**
Create a new dedicated plugin `plugins/agent-execution-disciplines/` to own
universal workflow execution skills canonically (verification, TDD, debugging,
code review). Canonicalize the first skill there:

```
plugins/agent-execution-disciplines/
  plugin.json
  skills/
    verification-before-completion/
      SKILL.md              <- single authoritative source
```

Do NOT put this SKILL.md inside `agent-agentic-os` or `exploration-cycle-plugin`.
Do NOT create a cross-plugin SKILL.md symlink -- ADR-001 Rule 1 restricts
cross-plugin symlinks to scripts that resolve inside the plugin's own boundary;
SKILL.md is an agent instruction file, not a script.

The correct multi-plugin access pattern per ADR-001 layer 3 is Agent Skill
Delegation: once `agent-execution-disciplines` is installed, any other installed
skill can reference `verification-before-completion` by name in its agent
instructions (e.g., "trigger the verification-before-completion skill") without
any cross-plugin symlinks at all.

Bridge-install the new plugin:
```bash
python ./plugin_installer.py --plugin plugins/agent-execution-disciplines
```

Also add a line to `agents/os-learning-loop.md` Phase 2: friction events of type
`false_completion_claim` trigger this skill. Register in `plugins/tool_inventory.json`.

**Inspired by:** `superpowers/skills/verification-before-completion/SKILL.md` -
the Iron Law table, Common Failures table, and rationalization prevention block.

**Effort:** Small (under 2 hours - new plugin scaffold is minimal)

**Expected impact:** High. The most common failure in long-horizon agentic workflows
is agents claiming success without running verification commands. This skill closes
that gap, and the new `agent-execution-disciplines` plugin becomes the home for
QW3, QW4, QW5, and QW6 as well - one install gives all of them.

---

## Quick Win 2: Harden the SessionStart Hook (POSIX-safe wrapper around Python kernel)

**What to build/change:**
Do NOT replace `update_memory.py` with a bash script. The Python event bus
(`kernel.py`) must remain the state orchestrator. Instead, rewrite the bash
wrapper in `plugins/agent-agentic-os/hooks/` to be POSIX-safe and then invoke
the Python orchestrator with the resolved platform context:

1. Add platform detection (`CURSOR_PLUGIN_ROOT` / `CLAUDE_PLUGIN_ROOT` / fallback)
2. Add a trigger guard: fire only on `startup|clear|compact`, skip `--resume`
   (currently missing - causes re-injection on resumed sessions)
3. Use `printf` instead of heredoc to avoid the bash 5.3+ hang (confirmed bug
   in superpowers RELEASE-NOTES.md v5.0.3 fix #572)
4. Emit `hookSpecificOutput.additionalContext` vs `additional_context` based on
   detected platform
5. Pass the resolved `PLUGIN_ROOT` as an argument to `update_memory.py` / `kernel.py`
   so the Python layer is platform-aware without doing its own shell detection

**Inspired by:** `superpowers/hooks/session-start` (POSIX-safe bash, platform
detection, --resume guard, printf fix all documented in RELEASE-NOTES.md v5.0.3).

**Effort:** Small (2-4 hours)

**Expected impact:** Medium. Prevents double context injection on --resume (silent
corruption). Adds multi-platform portability as a foundation for Cursor/Codex support.

---

## Quick Win 3: Add Systematic Debugging Skill to agent-agentic-os

**What to build/change:**
Port `superpowers/skills/systematic-debugging/SKILL.md` and its reference files
(`root-cause-tracing.md`, `defense-in-depth.md`, `condition-

*(content truncated)*

## See Also

- [[quick-start-zero-context-guide]]
- [[analysis-questions-by-file-type]]
- [[bae-quick-start-guided-exploration-process]]
- [[analysis-questions-by-file-type]]
- [[quick-start-zero-context-guide]]
- [[agent-worktree-quick-reference]]

## Raw Source

- **Source:** `research-docs`
- **File:** `superpowers/quick-wins.md`
- **Indexed:** 2026-04-17T06:42:10.464635+00:00
