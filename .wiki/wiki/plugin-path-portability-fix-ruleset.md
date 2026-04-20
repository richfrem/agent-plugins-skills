---
concept: plugin-path-portability-fix-ruleset
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/fix-plugin-paths/references/fix-plugin-paths.prompt.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.090941+00:00
cluster: rule
content_hash: e980005def6f8767
---

# Plugin Path Portability Fix Ruleset

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Plugin Path Portability Fix Ruleset

## Rule 1: Self-referential script paths → `./scripts/`
If a file inside `plugins/A/` references `plugins/A/scripts/foo.py`, replace with `./scripts/foo.py`.

**BEFORE:** `python plugins/agent-agentic-os/scripts/evaluate.py`
**AFTER:**  `python ./scripts/evaluate.py`

---

## Rule 2: Environment-specific `.agents/skills/<skill>/scripts/` paths → `scripts/`
These are environment-specific and break across installations.

**BEFORE:** `python .agents/skills/os-eval-runner/scripts/evaluate.py`
**AFTER:**  `python scripts/evaluate.py`

---

## Rule 3: Cross-skill `plugins/<plugin>/skills/<skill>/` paths → `.agents/skills/<skill>/`
When referencing another skill's files, use the installed location.

**BEFORE:** `plugins/copilot-cli/skills/copilot-cli-agent/references/foo.md`
**AFTER:**  `.agents/skills/copilot-cli-agent/references/foo.md`

---

## Rule 4: Absolute machine paths `/Users/<name>/...` → `<USER_HOME>/...`
Full computer paths must be neutralized.

**BEFORE:** `e.g. "/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/link-checker"`
**AFTER:**  `e.g. "<USER_HOME>/Projects/agent-plugins-skills/plugins/link-checker"`

---

## Rule 5: Skill-internal template/asset paths with `<APS_ROOT>/plugins/<self>/` → relative
When a skill references its OWN assets via an absolute or APS_ROOT path, use a relative path.

**BEFORE:**
```
<APS_ROOT>/plugins/agent-agentic-os/assets/templates/eval-instructions.template.md
# (symlink → plugins/agent-agentic-os/assets/templates/...)
```
**AFTER:**
```
assets/templates/eval-instructions.template.md
```

---

## Rule 6: Template placeholder `{{PLUGIN_DIR}}` → `{{SKILL_PATH}}`
Rename this variable to the established standard when it appears as a placeholder.

**BEFORE:** `{{PLUGIN_DIR}}`
**AFTER:**  `{{SKILL_PATH}}`

---

## Rule 7: `{{SKILL_EVAL_SOURCE}}` examples → INSTALL.md reference
Replace hardcoded path examples for `SKILL_EVAL_SOURCE` with a pointer to INSTALL.md.

**BEFORE:** `` `{{SKILL_EVAL_SOURCE}}` | `<APS_ROOT>/plugins/agent-agentic-os/skills/os-eval-runner` ``
**AFTER:**  `` `{{SKILL_EVAL_SOURCE}}` | Path to installed `os-eval-runner` (see [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md)) ``

---

## 🚫 CRITICAL: DO NOT Change These

- **Variable-gated paths**: `<APS_ROOT>/plugins/`, `$APS_ROOT/plugins/`, `$PLUGIN_NAME`.
- **Generic placeholder examples**: `plugins/my-plugin`, `plugins/<plugin-name>`, `plugins/link-checker`.
- **GitHub URLs**: `https://github.com/.../plugins/...`.

---

## Output Format

Output ONLY the corrected file. No explanation. No markdown fences.


## See Also

- [[identity-plugin-path-portability-enforcer]]
- [[identity-plugin-path-portability-enforcer]]
- [[optimization-program-fix-plugin-paths]]
- [[optimization-program-fix-plugin-paths]]
- [[adr-manager-plugin]]
- [[test-scenario-bank-agentic-os-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/fix-plugin-paths/references/fix-plugin-paths.prompt.md`
- **Indexed:** 2026-04-17T06:42:10.090941+00:00
