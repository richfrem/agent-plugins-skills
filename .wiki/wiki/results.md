---
concept: results
source: plugin-code
source_file: agent-scaffolders/skills/create-skill/evals/experiments/2026-03-13_194300/results.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.178325+00:00
cluster: skill
content_hash: f2d97febc9c16c4c
---

# Results

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/skills/create-skill/evals/experiments/2026-03-13_194300/results.json -->
{
  "exit_reason": "max_iterations (8)",
  "original_description": "Interactive initialization script that acts as a Skill Designer and Architect. Generates a compliant Agent Skill containing strict YAML frontmatter, optimal interaction designs, and L4 patterns based on diagnostic questioning.",
  "best_description": "Interactive initialization script that acts as a Skill Designer and Architect. Generates a compliant Agent Skill containing strict YAML frontmatter, optimal interaction designs, and L4 patterns based on diagnostic questioning.",
  "best_score": "1/2",
  "best_train_score": "2/4",
  "best_test_score": "1/2",
  "final_description": "Use this skill to interactively scaffold a new Agent Skill directory and SKILL.md focused on trigger quality and verifiable behavior. Produces strict YAML frontmatter (trigger text), a concise goal, testable acceptance criteria, evals/evals.json with positive and near\u2011miss prompts, and a procedural fallback flow. Runs a short diagnostic interview to capture edge cases and outputs a ready-to-edit skill folder. Invoke for requests like \u201cscaffold a new skill <name>\u201d or \u201cgenerate SKILL.md with frontmatter, acceptance criteria, eval prompts and fallback flows.\u201d Not for unrelated infra/CI tasks.",
  "iterations_run": 8,
  "holdout": 0.34,
  "train_size": 4,
  "test_size": 2,
  "history": [
    {
      "iteration": 1,
      "description": "Interactive initialization script that acts as a Skill Designer and Architect. Generates a compliant Agent Skill containing strict YAML frontmatter, optimal interaction designs, and L4 patterns based on diagnostic questioning.",
      "decision": "keep",
      "notes": "new best on train set",
      "train_passed": 2,
      "train_failed": 2,
      "train_total": 4,
      "train_results": [
        {
          "query": "Please scaffold a new skill called log-sanitizing with proper SKILL.md frontmatter.",
          "should_trigger": true,
          "trigger_rate": 0.0,
          "triggers": 0,
          "runs": 2,
          "pass": false
        },
        {
          "query": "Add a new MCP server integration for postgres tools.",
          "should_trigger": false,
          "trigger_rate": 0.0,
          "triggers": 0,
          "runs": 2,
          "pass": true
        },
        {
          "query": "Generate an Agent Skill with acceptance criteria, eval prompts, and fallback tree.",
          "should_trigger": true,
          "trigger_rate": 0.0,
          "triggers": 0,
          "runs": 2,
          "pass": false
        },
        {
          "query": "Convert this plugin into a GitHub Actions workflow.",
          "should_trigger": false,
          "trigger_rate": 0.0,
          "triggers": 0,
          "runs": 2,
          "pass": true
        }
      ],
      "test_passed": 1,
      "test_failed": 1,
      "test_total": 2,
      "test_results": [
        {
          "query": "What does gradient descent mean?",
          "should_trigger": false,
          "trigger_rate": 0.0,
          "triggers": 0,
          "runs": 2,
          "pass": true
        },
        {
          "query": "Help me design a new agent skill and ask me discovery questions first.",
          "should_trigger": true,
          "trigger_rate": 0.0,
          "triggers": 0,
          "runs": 2,
          "pass": false
        }
      ],
      "passed": 2,
      "failed": 2,
      "total": 4,
      "results": [
        {
          "query": "Please scaffold a new skill called log-sanitizing with proper SKILL.md frontmatter.",
          "should_trigger": true,
          "trigger_rate": 0.0,
          "triggers": 0,
          "runs": 2,
          "pass": false
        },
        {
          "query": "Add a new MCP server integration for postgres tools.",
          "should_trigger": false,
          "trigger_rate": 0.0,
          "triggers": 0,
          "runs": 2,
          "pass": true
        },
        {
          "query": "Generate an Agent Skill with acc

*(content truncated)*

<!-- Source: plugin-code/copilot-cli/skills/copilot-cli-agent/evals/experiments/2026-03-13_182514/results.json -->
{
  "exit_reason": "max_iterations (10)",
  "original_description": "Copilot CLI sub-agent system for persona-based analysis. Use when piping large contexts to GitHub Copilot models for security audits, architecture reviews, QA analysis, or any specialized analysis requiring a fresh model context.",
  "best_description": "Copilot CLI sub-agent system for persona-based analysis. Use when piping large contexts to GitHub Copilot models for security audits, architecture reviews, QA analysis, or any specialized analysis requiring a fresh model context.",
  "best_score": "1/2",
  "best_train_score": "2/4",
  "best_test_score": "1/2",
  "final_description": "Copilot CLI sub-agent system for persona-based analysis. Use when piping large conte

*(combined content truncated)*

## See Also

- [[load-and-validate-eval-results-data-from-tsv]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/skills/create-skill/evals/experiments/2026-03-13_194300/results.json`
- **Indexed:** 2026-04-27T05:21:04.178325+00:00
