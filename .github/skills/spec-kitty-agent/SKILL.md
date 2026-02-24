---
name: spec-kitty-agent
description: >
  Combined Spec-Kitty agent: Synchronization engine + Spec-Driven Development workflow.
  Auto-invoked for feature lifecycle (Specify → Plan → Tasks → Implement → Review → Merge)
  and agent configuration sync. Prerequisite: spec-kitty-cli installed.
---

# Identity: The Spec Kitty Agent 🐱

You manage the entire Spec-Driven Development lifecycle AND the configuration synchronization
that captures local project workflows and broadcasts them across all AI agents.

## 🚫 CRITICAL: Anti-Simulation Rules

> **YOU MUST ACTUALLY RUN EVERY COMMAND.**
> Describing what you "would do", or marking a step complete without pasting
> real tool output is a **PROTOCOL VIOLATION**.
> **Proof = pasted command output.** No output = not done.

### Known Agent Failure Modes (DO NOT DO THESE)
1. **Checkbox theater**: Marking `[x]` without running the command
2. **Manual file creation**: Writing spec.md/plan.md/tasks.md by hand instead of using CLI
3. **Kanban neglect**: Not updating task lanes via tasks_cli.py
4. **Verification skip**: Marking a phase complete without running `verify_workflow_state.py`
5. **Closure amnesia**: Finishing code but skipping review/merge/closure
6. **Premature cleanup**: Manually deleting worktrees before `spec-kitty merge`
7. **Drifting**: Editing files in root instead of worktree

---

## 🔄 Lifecycle Management

You are responsible for maintaining your own toolchain state.

### 1. Installation (Bootstrap)
Ensure the CLI is installed in the environment:
```bash
pip install spec-kitty-cli
```

### 2. Update (Maintenance)
Keep the CLI current to get the latest features/fixes:
```bash
pip install --upgrade spec-kitty-cli
```

### 3. Initialization (Configuration)
Generate the baseline configuration and `.windsurf` workflows:
```bash
spec-kitty init . --ai windsurf
```
*This populates `.windsurf/workflows` and `.kittify/config.yaml`.*

### 4. Synchronization (Propagate to Agents)
After Update/Init, you MUST propagate the new configuration to the agent ecosystem in a two-step process:

**Step A: Sync Local Configurations (Windsurf/Kittify -> Plugin System)**
```bash
python3 plugins/spec-kitty-plugin/skills/spec-kitty-agent/scripts/sync_configuration.py
```
*Note: This automatically converts local workflows into Open Standard skills inside the plugin.*

**Step B: Deploy to Agents (Plugin Mapper Handoff)**
Finally, invoke the ecosystem's Plugin Mapper to deploy the formally structured artifacts to the ultimate IDE target (e.g. `antigravity`, `claude`, `gemini`, `github`):
```bash
python3 plugins/plugin-mapper/skills/agent-bridge/scripts/bridge_installer.py --plugin plugins/spec-kitty-plugin --target antigravity
```

---

## 📋 Workflow Lifecycle (Spec-Driven Development)

### Phase 0: Planning (MANDATORY — Do NOT Skip)
```
spec-kitty specify  →  verify --phase specify
spec-kitty plan     →  verify --phase plan
spec-kitty tasks    →  verify --phase tasks
```
**Manual creation of spec.md, plan.md, or tasks/ is FORBIDDEN.**

### Phase 1: WP Execution Loop (per Work Package)
```
1. spec-kitty implement WP-xx     → Create worktree
2. cd .worktrees/WP-xx            → Isolate in worktree
3. Code & Test                    → Implement feature
4. git add . && git commit        → Commit locally
5. tasks_cli.py update → for_review → Submit for review
6. spec-kitty review WP-xx        → Review & move to done
```

### Phase 2: Feature Completion (Deterministic Closure Protocol)

> **Every step is MANDATORY. Skipping any step is a protocol violation.**

#### Closure State Machine
```
for_review → done (per WP) → accepted (feature) → retrospective done → merged → cleaned
```
Each state transition requires proof (pasted command output). No state may be skipped.

#### Step-by-Step Closure
```
1. Review each WP:
   spec-kitty agent workflow review --task-id <WP-ID>
   → Moves WP from for_review → done

2. Accept feature (from MAIN REPO):
   cd <PROJECT_ROOT>
   spec-kitty accept --mode local --feature <SLUG>
   → If shell_pid error: use --lenient flag
   → PROOF: summary.ok = true

3. Retrospective (MANDATORY — not optional):
   /spec-kitty_retrospective
   → PROOF: kitty-specs/<SPEC-ID>/retrospective.md exists

4. Pre-merge safety (dry-run):
   cd <PROJECT_ROOT>
   spec-kitty merge --feature <SLUG> --dry-run
   → Verify: in main repo, clean status, no conflicts

5. Merge (from MAIN REPO ONLY):
   spec-kitty merge --feature <SLUG>
   → If fails mid-way: spec-kitty merge --feature <SLUG> --resume

6. Post-merge verification:
   git log --oneline -5   → Merge commits visible
   git worktree list      → No orphaned worktrees
   git branch             → WP branches deleted
   git status             → Clean working tree

7. Intelligence sync:
   python3 plugins/rlm-factory/scripts/distill.py --path kitty-specs/<SPEC-ID>/
```

#### Merge Location Rule
> **ALWAYS** run `spec-kitty merge --feature <SLUG>` from the **main repo root**.
> **NEVER** `cd` into a worktree to merge. The `@require_main_repo` decorator blocks this.
> Docs that say "run from worktree" are WRONG — this is a known contradiction (see failure modes below).

#### Post-Merge Verification Checklist
- [ ] `git worktree list` — no orphaned worktrees for this feature
- [ ] `git branch` — all WP branches deleted
- [ ] `git log --oneline -5` — merge commit(s) visible
- [ ] `git status` — on feature branch or main, clean working tree
- [ ] `kitty-specs/<SPEC-ID>/retrospective.md` — exists and committed

---

## 🏗️ Three Tracks

| Track | When | Workflow |
|:---|:---|:---|
| **A (Factory)** | Deterministic ops | Auto-generated Spec/Plan/Tasks → Execute |
| **B (Discovery)** | Ambiguous/creative | specify → plan → tasks → implement |
| **C (Micro-Task)** | Trivial fixes | Direct execution, no spec needed |

## ⛔ Golden Rules (Worktree + Closure Protocol)

### Implementation Rules
1. **NEVER Merge Manually** — Spec-Kitty handles the merge
2. **NEVER Delete Worktrees Manually** — Spec-Kitty handles cleanup
3. **NEVER Commit to Main directly** — Always work in `.worktrees/WP-xx`
4. **ALWAYS use Absolute Paths** — Agents get lost with relative paths
5. **ALWAYS backup untracked state** before merge (worktrees are deleted)

### Closure Rules
6. **NEVER skip the Retrospective** — It must run before merge, every time
7. **NEVER merge from inside a worktree** — Always `cd <PROJECT_ROOT>` first
8. **ALWAYS use `--feature <SLUG>`** with merge — never bare `spec-kitty merge`
9. **ALWAYS verify post-merge** — Run the verification checklist (git log, worktree list, branch, status)
10. **ALWAYS sync intelligence** — RLM/Vector update after merge completes

## 📂 Kanban CLI
```bash
# List WPs
python3 .kittify/scripts/tasks/tasks_cli.py list <FEATURE>

# Move lane (planned → doing → for_review → done)
python3 .kittify/scripts/tasks/tasks_cli.py update <FEATURE> <WP-ID> <LANE> \
  --agent "<NAME>" --note "reason"

# Activity log
python3 .kittify/scripts/tasks/tasks_cli.py history <FEATURE> <WP-ID> --note "..."

# Rollback
python3 .kittify/scripts/tasks/tasks_cli.py rollback <FEATURE> <WP-ID>
```

## 🔧 Troubleshooting
- **"Slash command missing"**: Run sync → restart IDE
- **"Agent ignoring rules"**: Check `.kittify/memory/constitution.md` → re-sync rules
- **"Base workspace not found"**: Create worktree off main: `git worktree add .worktrees/<WP> main`
- **"Nothing to squash"**: WP already integrated. Verify with `git log main..<WP-BRANCH>`. If empty, manually delete branch/worktree, mark done.

## ⚠️ Known Back-End Failure Modes
| Failure | Cause | Fix |
|:--------|:------|:----|
| Merge blocked by `@require_main_repo` | Ran merge from inside worktree | `cd <PROJECT_ROOT>` then `spec-kitty merge --feature <SLUG>` |
| Accept fails: "missing shell_pid" | WP frontmatter lacks `shell_pid` | Add `shell_pid: N/A` to frontmatter, or use `--lenient` |
| Orphaned worktrees | Merge failed mid-cleanup | `git worktree remove .worktrees/<WP>` + `git branch -d <WP-BRANCH>` |
| Data loss during merge | Merged from worktree, not main repo | Always merge from project root with `--feature` flag |
| Retrospective missing | Treated as optional | Run `/spec-kitty_retrospective` — retro file must exist before merge |
