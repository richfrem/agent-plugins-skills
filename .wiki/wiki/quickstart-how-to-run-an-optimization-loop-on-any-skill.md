---
concept: quickstart-how-to-run-an-optimization-loop-on-any-skill
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-eval-runner/QUICKSTART.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.144419+00:00
cluster: plugin-code
content_hash: d27c55e3cbbac478
---

# Quickstart: How to Run an Optimization Loop on Any Skill

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Quickstart: How to Run an Optimization Loop on Any Skill

> **Prerequisites:**
> - The target skill folder must be inside a **git repository**. Run `git init && git add . && git commit -m "init"` first if needed.
> - **Python 3.8+** must be available as `python`.

You only need two things:
1. A copy of the **target skill folder** you want to improve.
2. The **os-eval-runner** engine (the stateless evaluator).

## 0. Fresh Repo? Hardened Bootstrap (Do This First)

> Skip this section if you already have `os-eval-runner` installed and a git repo initialized.

Before running any loops, ensure the environment is clean and correctly linked. Follow these steps exactly:

1. **Check Git Remote**:
   ```bash
   git remote -v
   ```
   If the remote is blank, **stop and ask the user** for the repository URL (e.g., `https://github.com/richfrem/test-skill-eval-loop`).

2. **Initialize Local Git** (if not already a repo):
   ```bash
   git init && git add . && git commit -m "init"
   ```

3. **Delete Old Config (Clean Slate)**:
   Ensure no stale metadata blocks the new installation:
   ```bash
   rm -rf .agent .agents .gemini .claude
   ```

4. **Install Skill via GitHub Hub**:
   Consult the authoritative installation hub for current deployment commands:

   > ### 👉 [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md)
   > ⚠️ **Known CLI Issues:** The `-y` flag may crash on some versions — if so, run without it and respond to prompts manually. You will see a list of agent environments; press **Enter** to accept defaults.

5. **Final Seed & Push**:
   Confirm everything is staged and push to the remote:
   ```bash
   git add . && git commit -m "seed: hardened bootstrap"
   git push origin main
   ```

6. **Verify Python 3**:
   Ensure `python` is available (v3.8+).
   ```bash
   python --version
   ```

---

## 1. Scaffold the Experiment (One-Time)

```bash
python scripts/init_autoresearch.py \
    --experiment-dir .agents/skills/your-target-skill \
    --mutation-target SKILL.md
```

This deploys:
- `references/program.md` — your optimization spec
- `evals/evals.json` — test cases
- `evals/results.tsv` — ledger header

## 2. Customize the Experiment (You Do This Once)

**Edit `references/program.md`**
Fill in the Notes section:
- What exactly you are optimizing
- Desired target `quality_score` (e.g. 0.95)
- Any special constraints

**Edit `evals/evals.json`**
Replace every `REPLACE` placeholder with real test prompts and correct `should_trigger` values.
*Important: This is the most critical step. Poor or incomplete test cases lead to meaningless optimization.*

## 3. Establish the Baseline

```bash
python scripts/evaluate.py \
    --skill .agents/skills/your-target-skill \
    --baseline \
    --desc "initial baseline"
git add .agents/skills/your-target-skill/evals/
git commit -m "baseline: initial evaluation snapshot"
git push origin main
```
*This records the starting score, creates the SHA256 snapshot, and PUSHES the state to the remote repository so future agents can see the baseline.*

> **Note:** If you later update `evals.json` to add better test cases, you can safely re-run with `--baseline` again. The `--baseline` flag intentionally bypasses the SHA256 check so you can re-baseline without being blocked.

## 4. Run the Autonomous Loop

Your main agent (or Triple-Loop Retrospective) repeatedly runs:

```bash
# Example single iteration
python scripts/evaluate.py \
    --skill .agents/skills/your-target-skill \
    --desc "improved trigger phrasing for edge case X"
```

**Behavior:**
- `exit 0` (KEEP) → Agent should `git add` + `git commit`
- `exit 1` (DISCARD) → `evaluate.py` already reverted the files automatically

The loop continues until you stop it manually or the target score in `program.md` is reached.

---

### Tips for Success
- Start with a HIGH viability skill from your ranked list.
- Ensure `evals/evals.json` contains a good mix of positive and adversarial (negative) examples.
- On

*(content truncated)*

## See Also

- [[skill-optimization-guide-karpathy-loop]]
- [[autoresearch-overview-applying-the-karpathy-loop-to-any-target]]
- [[autoresearch-overview-applying-the-karpathy-loop-to-any-target]]
- [[skill-optimization-guide-karpathy-loop]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-eval-runner/QUICKSTART.md`
- **Indexed:** 2026-04-17T06:42:10.144419+00:00
