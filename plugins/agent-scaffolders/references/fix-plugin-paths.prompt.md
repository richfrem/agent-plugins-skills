# Plugin Path Portability Fix Ruleset

## Rule 1: Self-referential script paths → `./scripts/`
If a file inside `plugins/A/` references `plugins/A/scripts/foo.py`, replace with `./scripts/foo.py`.

**BEFORE:** `python plugins/agent-agentic-os/scripts/evaluate.py`
**AFTER:**  `python ./scripts/evaluate.py`

---

## Rule 2: Environment-specific install paths → `scripts/` relative to skill root
Hardcoded install paths break across different harnesses and global installations.

**BEFORE:** `python .agents/skills/os-lab-scorer/scripts/evaluate.py`
**AFTER:**  `python scripts/evaluate.py` (relative to skill directory)

---

## Rule 3: Cross-skill references → Portable skill citation
When referencing another skill's documents or rules, cite the skill by name or use a relative markdown link.

**BEFORE:** `plugins/cli-agents/skills/copilot-cli-agent/references/foo.md`
**AFTER:**  `Refer to the 'copilot-cli-agent' skill (or relative link within package)`

---

## Rule 4: Absolute machine paths `/Users/<name>/...` → `<USER_HOME>/...`
Full computer paths must be neutralized.

**BEFORE:** `e.g. "./plugins/link-checker"`
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

**BEFORE:** `` `{{SKILL_EVAL_SOURCE}}` | `<APS_ROOT>/plugins/agent-agentic-os/skills/os-lab-scorer` ``
**AFTER:**  `` `{{SKILL_EVAL_SOURCE}}` | Path to installed `os-lab-scorer` (see [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md)) ``

---

## 🚫 CRITICAL: DO NOT Change These

- **Variable-gated paths**: `<APS_ROOT>/plugins/`, `$APS_ROOT/plugins/`, `$PLUGIN_NAME`.
- **Generic placeholder examples**: `plugins/my-plugin`, `plugins/<plugin-name>`, `plugins/link-checker`.
- **GitHub URLs**: `https://github.com/.../plugins/...`.

---

## Output Format

Output ONLY the corrected file. No explanation. No markdown fences.
