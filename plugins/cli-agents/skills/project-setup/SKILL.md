---
name: project-setup
plugin: cli-agents
description: >-
  Interactive skill to scaffold and optimize configuration files for both Claude Code (.claude/)
  and Google ADK/Gemini (.agents/) directories. Trigger with "set up project", "scaffold agent config", 
  "setup cli agent settings", or "configure agents for this project".
allowed-tools: Bash, Read, Write
---

# Unified Agent Project Setup

You are an expert configuration architect. Your job is to interactively discover a project's needs and scaffold config files for Claude Code (.claude/) and Google ADK/Gemini (.agents/) rules.

This setup path is valid only after the consuming repository has installed its
plugins and completed `os-init` plus `os-health-check`. If either prerequisite
is missing, report the remediation and do not pretend the environment is ready.
After the prerequisite check, establish one reusable local capability baseline
for provider availability, low/medium/high model preferences, fallback order,
and non-secret constraints. Follow `../../references/capability-profile-contract.md`
and keep credentials, tokens, prompts, and raw provider output out of the profile.

Use this single dispatcher for all supported project runtimes. Read the provider
references as needed rather than routing to separate setup skills:

| Runtime | Reference |
|---|---|
| Claude Code | `../../references/claude-directory-spec.md`, `../../references/claude-settings-schema.md` |
| Antigravity / Google ADK | `../../references/antigravity-directory-spec.md`, `../../references/gemini-cli-commands.md` |
| Codex, Copilot, Agy, or local LLM | capability profile and the corresponding CLI-agent or local-LLM skill |

The retired `claude-project-setup` and `antigravity-project-setup` entries are
not separate runtime paths; preserve their provider-specific requirements in
these references and choose the applicable target during this interview.

---

## Capability Baseline (once per project setup)

Deep analysis belongs in project setup. Establish the capability baseline before
asking downstream workflow questions, and do this setup interview only once per
project unless the environment or preferences change.

1. Load `context/agent-capability-profile.json` with
   `../../scripts/capability_profile.py` when it exists.
2. If it is missing, partial, invalid, or stale, perform lightweight current
   probes for the user's installed/authenticated CLIs and consult the current
   model catalogs. Run the interactive questions below one question at a time;
   do not infer answers from the host agent or ask the whole matrix as one
   compound question.
3. Record unavailable optional providers as unavailable. Never infer access
   from the repository author, the host agent, or a static catalog entry.
4. If the profile is ready, show a concise summary and ask only about changes;
   **do not repeat deep environment or model analysis** during later review or
   implementation gates.

### Capability baseline questions

Ask the user to confirm the user-confirmed provider inventory one question at a
time. For each provider, ask: “Is `<provider>` available for this project?
(available: Yes/No).” Then ask separately: “Do you have an active subscription, account,
license, or other access for `<provider>` for this project? (Yes/No/Unknown).”
Confirm only the installation/callability portion with a safe probe before
recording it:

- Codex CLI — `codex`
- Agy CLI — `agy`
- Claude CLI — `claude`
- GitHub Copilot CLI — `gh copilot`
- Local LLM runtime — the configured local bridge/runtime

Installed alone never counts as available. For each provider, record
`installed`, `access_confirmed`, `access_status`, `project_authorized`, and the
derived `available` value. For any work-account provider, ask a separate
project authorization question: “Do you authorize this provider's work
account for this project's tasks? (Yes/No/Unknown).” Set `available: true` only
when the user confirms access, the user confirms project authorization, and
the safe probe succeeds. If the CLI is installed but the user has no
subscription or access, record `installed: true`, `access_status:
no_subscription` (or the appropriate non-secret state), and `available: false`.
If access exists but project authorization is pending or denied, record
`project_authorized: false` and `available: false`.

For every provider with `available: true`, ask separately which
catalog-supported model should be preferred for low, medium, and high effort.
Before asking model questions, read the `update-cli-models` skill. It is the
sole authority for current model IDs, capability tiers, pricing, catalog-copy
resolution, and synchronization; project-setup does not duplicate model catalog policy.
Show only IDs supported by that authority, recommend a
proportional choice, and ask the user to choose or confirm each recommendation.
Then ask for fallback order and non-secret constraints. A Yes answer without a
successful probe or with Unknown access is recorded as unverified/unavailable
with the exact refresh action; it is never silently enabled.

Write the complete result using the profile contract. The resulting JSON
contains each provider's `available: true/false` value and any confirmed
`model_tiers` selections, so later pipeline stages must read the profile and
must not repeat this setup interview. Never store credentials, tokens, prompts,
or raw provider output. If the profile is missing or stale, route back to project setup before offering model choices.

Model catalog authority is delegated to `update-cli-models`; read that skill
for master-catalog, installed-copy, tier, pricing, and synchronization rules.
If the authority or a required catalog is unavailable, report the exact missing
path and refresh action; do not invent model choices or dispatch.

The profile is the canonical machine-readable source. It is reused by later plan and implementation review gates. `context/memory/environment.md`, when present,
is a human-readable environment summary and compatibility fallback, not a
second competing preference store. Project setup establishes preferences but
does not authorize reviewer dispatch. Do not dispatch an internal reviewer
until a later review gate has obtained the user's explicit runtime/model/effort
choice.

---

## Phase 1: Discovery Interview

Ask the user the following questions to decide which setups to generate:

1. **Target Runtimes**: Are we configuring for Claude Code (`.claude/`), Google ADK/Gemini CLI (`.agents/`), or both?
2. **Project Type**: What kind of project is this (monorepo, web application, Python backend, etc.)?
3. **Core commands**: Most common dev commands (build, test, lint, dev server)?
4. **Agent Persona**: What primary identity or specific coding domains need scoped rules?
5. **Available providers**: Confirm which of Codex, Claude Code, Copilot,
   Antigravity/Agy, and local LLMs are available to this user on this machine.
   Record unavailable optional providers instead of assuming access.
6. **Model preferences**: Which accessible model should be preferred for low,
   medium, and high effort work? Validate selections against current catalogs.
7. **Constraints**: Are there workplace, network, quota, or privacy constraints
   affecting provider selection? Record descriptions only, never credentials.

---

## Phase 2: Plan Recap

Present the generated setup plan:
```markdown
### Agent Configuration Scaffolding Plan
* **Claude Code Configs**: (.claude/settings.json, CLAUDE.md)
* **Google ADK Configs**: (.agents/config.json, GEMINI.md)
* **Rules / Prompts**: Scoped conventions files

> Proceed? (yes / adjust)
```

Wait for user approval before writing files.

---

## Phase 3: Scaffold

Scaffold files according to the respective standards:
* **Claude Code**: Limit `CLAUDE.md` to <200 lines and place domain rules under `.claude/rules/`.
* **Google ADK**: Initialize `.agents/config.json`, `.agents/skills/` and create modular rules using `@` imports in `GEMINI.md`.

After scaffolding, write or refresh the confirmed provider availability and
model-tier preferences in `context/agent-capability-profile.json` using the
profile contract. Keep provider-specific setup in the existing references:
Codex, Claude Code, Copilot, Antigravity/Agy, and local LLMs may each be
unavailable. When a provider is unavailable or a profile is incomplete, report
the exact refresh action and continue without silently selecting it. Downstream
review transitions must consume this baseline and ask the user for an explicit
internal runtime/model/effort choice before dispatch.
