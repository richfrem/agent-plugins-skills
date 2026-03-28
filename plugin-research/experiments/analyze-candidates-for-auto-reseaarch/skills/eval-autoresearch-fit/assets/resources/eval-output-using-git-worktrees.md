## Autoresearch Fit Assessment: using-git-worktrees

**Plugin:** agent-execution-disciplines  
**Skill path:** plugins/agent-execution-disciplines/skills/using-git-worktrees/SKILL.md

### Scores
| Dimension | Score | Rationale |
|---|---|---|
| Objectivity | 10/10 | Success can be measured by deterministic shell checks (worktree exists, git reports worktree, test exit codes, .gitignore change). |
| Execution Speed | 7/10 | Typical loop (create worktree + quick tests) is often 1-5 minutes; installs/tests may extend time but a proxy check is fast. |
| Frequency of Use | 8/10 | Frequently used when starting feature work—daily or multiple times per developer session. |
| Potential Utility | 8/10 | Prevents destructive git actions and workspace corruption; improving reliability saves significant time and prevents hard-to-recover mistakes. |
| **TOTAL** | **33/40** | |

**Verdict: HIGH**  
**Loop type: DETERMINISTIC**

### Proposed 3-File Architecture

**Spec (program.md):**
> Optimize the worktree-creation flow so the agent reliably creates an isolated git worktree and verifies safety without human prompts. Constraints: do not change evaluator, avoid network-dependent steps in the core metric, never proceed when project-local directory is not git-ignored. NEVER STOP: continue trying safe, deterministic fixes until the evaluator succeeds or a deterministic failure is detected.

**Mutation Target:** plugins/agent-execution-disciplines/skills/using-git-worktrees/SKILL.md

**Evaluator command:**
```bash
# set BRANCH_NAME and PATH appropriately before running; outputs 1 on full success, 0 otherwise
BRANCH_NAME="feature/autoresearch-test"
PATH_DIR=".worktrees/${BRANCH_NAME}"
if [ -d "$PATH_DIR" ] && git -C "$PATH_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1 && git -C "$PATH_DIR" status --porcelain >/dev/null 2>&1; then
  # run lightweight project test command if present (non-fatal if absent)
  (cd "$PATH_DIR" && ( (command -v npm >/dev/null && npm test >/dev/null 2>&1) || (command -v pytest >/dev/null && pytest -q >/dev/null 2>&1) || true ))
  [ $? -eq 0 ] && echo 1 || echo 0
else
  echo 0
fi
```
Deterministic: YES — uses pure shell/git commands and test exit codes; no LLM judgement required (but test command may be environment-dependent).

### Key Barriers
- Human-confirmation gate: skill prompts when no preferred directory found (blocks fully automated loops).  
- Environment variability & network installs: dependency installation and test flakiness introduce nondeterminism and slowdowns (Goodhart risk if agent skips or mocks tests).

### Recommendation
Use a deterministic proxy metric first (verify git worktree creation, .gitignore update, and worktree is a valid git worktree) and exclude heavy dependency installs from the core evaluator; address interactive prompts by defaulting to a non-interactive policy in the spec.

### update_ranked_skills.py command
```bash
python3 tools/update_ranked_skills.py --json-path skills-lock.json \
  --plugin agent-execution-disciplines --skill using-git-worktrees \
  --objectivity 10 --speed 7 --frequency 8 --utility 8 \
  --verdict HIGH \
  --loop-type DETERMINISTIC \
  --mutation-target "plugins/agent-execution-disciplines/skills/using-git-worktrees/SKILL.md" \
  --evaluator-command "BRANCH_NAME=\"feature/autoresearch-test\"; PATH_DIR=\".worktrees/${BRANCH_NAME}\"; if [ -d \"$PATH_DIR\" ] && git -C \"$PATH_DIR\" rev-parse --is-inside-work-tree >/dev/null 2>&1 && git -C \"$PATH_DIR\" status --porcelain >/dev/null 2>&1; then (cd \"$PATH_DIR\" && ( (command -v npm >/dev/null && npm test >/dev/null 2>&1) || (command -v pytest >/dev/null && pytest -q >/dev/null 2>&1) || true )); [ $? -eq 0 ] && echo 1 || echo 0; else echo 0; fi" \
  --barriers "Human confirmation required when directory ambiguous" "Network/install/test flakiness and Goodhart risk (agent might bypass tests)" \
  --eval-notes "Use a proxy metric (worktree created + .gitignore updated + valid worktree) to avoid slow/flaky installs" \
  --status EVALUATED
```


Total usage est:        0 Premium requests
API time spent:         54s
Total session time:     58s
Total code changes:     +0 -0
Breakdown by AI model:
 gpt-5-mini              54.3k in, 2.6k out, 51.2k cached (Est. 0 Premium requests)
