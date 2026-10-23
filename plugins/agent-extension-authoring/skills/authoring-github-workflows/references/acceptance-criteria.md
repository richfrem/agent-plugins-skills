# Acceptance Criteria: authoring-github-workflows

Merged verbatim from the two retired skills; one section per mode.

## Mode: create-github-action

[PASSED] The generated `.github/workflows/` YAML file is syntactically valid and explicitly lists the triggering events.
[PASSED] Any secrets referenced in the workflow are properly parameterized as `${{ secrets.NAME }}` placeholders.
[FAILED] The generated action hardcodes API tokens or sensitive credentials directly into the YAML.
[FAILED] The `env:` context grants the workflow more runner privileges than requested by the user.

## Mode: create-agentic-workflow

[PASSED] The generated `.agent.md` correctly includes the boilerplate kill switch phrase for Target C.
[PASSED] The generated `.yml` or script correctly registers the invocation pattern (`workflow_dispatch` etc).
[PASSED] Supports generating Target A (Custom Copilot Agent `.agent.md`), Target B (gh-aw Workflow `.md`), and Target C (CI/CD Smart Failure agent).
[PASSED] Support for validating generated configurations with `validate_github_agent.py`.
[FAILED] The tool list uses `--allow-all-tools` in production instead of a restricted set.
