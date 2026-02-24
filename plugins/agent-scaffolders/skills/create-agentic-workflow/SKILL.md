---
name: create-agentic-workflow
description: Interactive initialization script that scaffolds a new Continuous AI "Smart Failure" Copilot action. Use when generating automated CI/CD agents that must review code or docs and break builds based on specific "Kill Switch" criteria.
---

# Agentic Workflow Scaffolder

You are tasked with generating a new **GitHub Agentic Workflow** pattern (also known as a Continuous AI or "Smart Failure" agent). 

Unlike generic skills or commands, Agentic DevOps pipelines do **not** belong natively in `plugins/`. Instead, they are tightly coupled to the host repository's `.github/` folder. This generator will create the Markdown Persona file and the YAML GitHub Action trigger directly in the `.github` directory.

## Execution Steps:

### 1. Gather Requirements
Ask the user for the following context before proceeding:
1. **Target**: Ask the user for the path to the Agent Skill directory they want to convert into a GitHub Action runner (e.g., `plugins/spec-kitty-plugin/skills/spec-kitty-analyze`).
2. **Auto-Trigger**: Ask the user if this workflow should be triggered automatically on Pull Requests and Pushes to main, or if it should be purely manual (triggered exclusively via `workflow_dispatch`). *Context for you (the agent): Some commands are meant to be manually triggerable on-demand in GitHub, while others are designed as strict "Smart Failure" quality gates that automatically run as part of the CI/CD pipeline.*

### 2. Scaffold the Workflow
You must execute the hidden deterministic `scaffold_agentic_workflow.py` script included in this plugin to guarantee perfect Open Standard compliance. 

Run the following bash command:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/scaffold_agentic_workflow.py --skill-dir <requested-skill-path> [--auto-trigger]
```
*(Append the `--auto-trigger` flag ONLY if the user confirmed they want the workflow to run automatically).*

The script will automatically parse the YAML frontmatter from the source skill, generate the Kill Switch logic, and create the `.github/agents/` persona and `.github/workflows/` runner files in the repository root.

### 3. Confirmation
Print a success message explaining to the user what was generated and reminding them that the `.github/workflows/` file requires the `COPILOT_GITHUB_TOKEN` secret to execute properly in GitHub Actions.
