# 🤖 Autonomous Schema Migration Agent Prompt (Eval Upgrades)

NOTE: i've moved your previous files into a folder.  temp/ubiquity-sweep/  so no longer at root of temp/s

## **Objective**
You are a Senior Agent Systems Engineer. Your mission is to perform a strict "Schema Migration Sweep" on our repository of AI agent capabilities. During a recent Ubiquity Sweep, several skills failed evaluation (Scoring ~0.21, F1 0.0) because their `evals/evals.json` files use a deprecated schema. You will upgrade these legacy files to the modern boolean schema and establish a fresh baseline.

## **Context & Target Identification**
* **The Target:** Skills that currently have an `evals/evals.json` file utilizing the old `expected_behavior` string schema. These can be identified by referencing the recent `phase2_results.json` where `score` is ~0.21 and `f1` is 0.0. Examples include `adr-management`, `os-eval-backport`, `obsidian-vault-crud`, etc.
* **The Blacklist:** You must **STRICTLY IGNORE** any skills related to `spec-kitty`. This is an externally wrapped repository, and we are accepting its current routing behavior as-is.

## **The Modern Schema Standard**
The new standard for `evals.json` requires a strict boolean `should_trigger` key. It must contain exactly:
* **3 Precise Positive (`should_trigger: true`)** test cases.
* **3 Hard Negative (`should_trigger: false`)** test cases (Adversarial prompts that share keywords with the skill but logically belong to a different tool).

```json
[
  {
    "user_prompt": "Specific request matching the skill's exact capability.",
    "should_trigger": true
  },
  {
    "user_prompt": "Request using similar keywords but requiring a different capability.",
    "should_trigger": false
  }
]