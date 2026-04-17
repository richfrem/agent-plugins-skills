---
concept: the-lab-space-protocol-full-lifecycle
source: plugin-code
source_file: agent-agentic-os/skills/os-eval-runner/references/lab-space-protocol.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.162295+00:00
cluster: master
content_hash: 7ace265a0f1096fe
---

# The Lab-Space Protocol (Full Lifecycle)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# The Lab-Space Protocol (Full Lifecycle)

When a skill runs in a **lab repo** (a standalone test repo with copies of plugin files — not the master source), there is a mandatory handoff stage after the loop completes. Lab repos use real file copies; the master repo uses hub-and-spoke symlinks pointing to canonical sources. Changes must be reviewed and backported — never blindly copied.

**Lab runs with `os-eval-runner` installed as a peer:** When the lab repo has both the target skill and `os-eval-runner` installed side by side (the `os-eval-lab-setup` default), the improvement loop will sometimes propose changes to `os-eval-runner` itself — its SKILL.md, eval scripts, or evals. This is expected and productive: the agent finds the highest-leverage change available across all installed skills. The physical copy in the lab is safe to mutate. Treat these changes in backport review with extra scrutiny (see note in Stage 6 below).

## Stage 6: Backport to Master Repo

After the loop completes and the self-assessment survey is written:

**1. Commit and push everything:**
```bash
git add . && git commit -m "post-run: finalize all artifacts"
git push origin main
```

**2. Identify changed files:**
```bash
git log --oneline --name-only  # which commits changed what
git diff <baseline-commit> HEAD --name-only  # all files changed since baseline
```

**3. For each changed file, identify its master source:**

| Component | Skill Installer (Universal) | Claude Code Native |
|:---|:---|:---|
| `<plugin>/skills/<skill>/SKILL.md` | Deployed Skill | `plugins/<plugin>/skills/<skill>/SKILL.md` |
| `<plugin>/skills/<skill>/evals/evals.json` | Deployed Evals | `plugins/<plugin>/skills/<skill>/evals/evals.json` |
| `.agents/skills/os-eval-runner/` (if patched) | Deployed Engine | `plugins/agent-agentic-os/skills/os-eval-runner/` |

**4. For each file — read the diff and assess:**
- **Accept as-is**: change is clearly an improvement, apply verbatim
- **Adapt**: change direction is right but needs adjustment for master context
- **Reject**: change was eval-specific, doesn't generalize, or is a regression

> **Extra scrutiny for `os-eval-runner` changes:** If the loop mutated `eval_runner.py` or `evaluate.py` in the lab, verify the change does not introduce scoring bias that inflates future KEEP rates. The evaluator rewriting its own verdict logic to always exit 0 is the Goodhart failure mode for meta-circular runs. Check the score trajectory in `results.tsv` — a suspiciously high acceptance rate after the change is a red flag.

**5. Apply approved changes deliberately:**
```
# Never blind-copy. Read the diff, understand the intent, edit master files deliberately.
# The master uses symlinks — only update the canonical source file.
```

**6. Two-gate confirmation before applying to master:**

Do not apply any change to master until both gates are cleared:

**Gate 1 — Machine:** `evaluate.py` exited 0 (score ≥ baseline AND f1 ≥ baseline_f1). Confirm from `results.tsv`.

**Gate 2 — Three-perspective diff commentary** (write this before editing master files):
```
BACKPORT REVIEW: iter_NNN — "<desc>"
Score delta: +0.07 (0.82 → 0.89)

Test engineer view:
  Which eval inputs changed verdict? [list them]
  Are these the inputs we were targeting, or collateral?

Routing precision view:
  What similar-but-wrong request could now trigger this skill?

Regression view:
  Do any other installed skills have overlapping keywords with this change?
  grep -r "<new keyword>" .agents/skills/*/SKILL.md
```

For **unattended** (`os-nightly-evolver`) runs: write this commentary to
`temp/retrospectives/backport_[YYYYMMDD]_iter_NNN.md` and flag for human review
before applying. Do not auto-apply to master from unattended runs.

**7. Contribute evolved proposer prompt (if improved during the run):**

If `references/copilot_proposer_prompt.md` was mutated and accepted (KEEPed) during the run,
compare it against the canonical template. If it substantially improved proposal quali

*(content truncated)*

## See Also

- [[identity-the-eval-lab-setup-agent]]
- [[identity-the-eval-lab-setup-agent]]
- [[git-worktree-branch-lifecycle-protocol]]
- [[git-worktree-branch-lifecycle-protocol]]
- [[git-worktree-branch-lifecycle-protocol]]
- [[git-worktree-branch-lifecycle-protocol]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/skills/os-eval-runner/references/lab-space-protocol.md`
- **Indexed:** 2026-04-17T06:42:09.162295+00:00
