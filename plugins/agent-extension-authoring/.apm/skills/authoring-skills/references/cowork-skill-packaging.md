# Authoring Skills for Copilot Cowork

## Contents

- [Use this route when](#use-this-route-when)
- [Author the skill](#author-the-skill)
- [Package the skill](#package-the-skill)

## Use this route when

Use this reference when a user wants to create or adapt an Agent Skill specifically for
Microsoft 365 Copilot Cowork. Use `authoring-skills` for the individual skill's content
and portability. Use `packaging-copilot-cowork-plugins` for the M365 app manifest,
icons, validation, ZIP creation, provisioning, and sharing.

If a new APM-native source plugin is also needed, use `authoring-plugins` to create the
repository-side plugin structure first. That source plugin is distinct from the M365
Cowork app package.

## Author the skill

1. Author the skill as a self-contained Agent Skill with a `SKILL.md` whose `name`
   matches its folder and whose description says what it does and when to use it.
2. Keep references and assets in the skill folder and use portable relative links.
   Preserve the skill's source representation and tests; don't edit an installed copy.
3. Do not imply Cowork runs bundled Python, shell scripts, or local executables. Scripts
   in the skill's `scripts/` folder are packaged with it, but runtime access to APIs or
   data that must reliably run should be a separately hosted remote MCP connector.
   Keep references, assets and scripts within Cowork's limits (20 companion files, 5 MB
   each, 10 MB total per skill); `evals/` and `tests/` are not packaged.
4. Audit the skill with `authoring-skills` before copying it into a Cowork project.
   Check the current Microsoft package rules and skill companion-file limits as part of
   the packaging step.

## Package the skill

Use `packaging-copilot-cowork-plugins` after authoring. It places the selected skill
folder under `appPackage/skills/<skill-slug>/`, registers the folder in the M365
`manifest.json`, ensures the required icons are present, validates the built ZIP, and
guides any approved provisioning or sharing.

Do not treat `.claude-plugin/plugin.json` or `apm.yml` as the M365 manifest, and do not
put APM plugin metadata into the upload ZIP unless the current Microsoft package
specification explicitly requires it.
