import os
import subprocess

skill_path = "plugins/gemini-cli/skills/gemini-cli-agent/SKILL.md"
evals_path = "plugins/gemini-cli/skills/gemini-cli-agent/evals/evals.json"

with open(skill_path, "r") as f:
    skill_content = f.read()

with open(evals_path, "r") as f:
    evals_content = f.read()

prompt = f"""You are an expert at optimizing SKILL.md routing accuracy.
CURRENT SKILL:
{skill_content}

EVALS:
{evals_content}

ISSUE: precision=0.6364, recall=1.0000. It's triggering too eagerly on false positives like: 'install the gemini cli on my machine', 'run a security audit using copilot instead', 'what is google gemini?', 'help me set up my google cloud account'. It is also missing <example> XML blocks which drops the heuristic score.

CONSTRAINTS: 
1. Fix the 'description' to be extremely specific. Clarify that it is for execution and piping, NOT setup, NOT other CLIs, and NOT general knowledge.
2. Add a positive and negative <example> block in the description to fix the heuristic and provide few-shot examples.
3. OUTPUT RAW SKILL.md ONLY. No markdown code fences, no commentary, no thinking text. Just the file contents."""

print("Running gemini proposer...")
result = subprocess.run(
    ["gemini", "-p", prompt],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("Gemini failed:", result.stderr)
else:
    proposed_content = result.stdout.strip()
    if proposed_content.startswith("```markdown"):
        proposed_content = proposed_content.replace("```markdown\n", "")
        proposed_content = proposed_content.replace("```", "")
    elif proposed_content.startswith("```"):
        proposed_content = proposed_content.replace("```\n", "")
        proposed_content = proposed_content.replace("```", "")
        
    with open("proposed-skill.md", "w") as f:
        f.write(proposed_content)
    print("Proposed skill saved to proposed-skill.md")
