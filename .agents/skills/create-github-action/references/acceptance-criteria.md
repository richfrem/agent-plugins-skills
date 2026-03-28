# Acceptance Criteria

[PASSED] The generated `.github/workflows/` YAML file is syntactically valid and explicitly lists the triggering events.
[PASSED] Any secrets referenced in the workflow are properly parameterized as `${{ secrets.NAME }}` placeholders.
[FAILED] The generated action hardcodes API tokens or sensitive credentials directly into the YAML.
[FAILED] The `env:` context grants the workflow more runner privileges than requested by the user.
