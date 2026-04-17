---
concept: command-template-spec-kittyimplement-documentation-mission
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/.kittify/missions/documentation/command-templates/implement.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.330029+00:00
cluster: reference
content_hash: 5b23526c3f774603
---

# Command Template: /spec-kitty.implement (Documentation Mission)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Implement documentation work packages using Divio templates and generators.
---

# Command Template: /spec-kitty.implement (Documentation Mission)

**Phase**: Generate
**Purpose**: Create documentation from templates, invoke generators for reference docs, populate templates with content.

## ⚠️ CRITICAL: Working Directory Requirement

**After running `spec-kitty implement WP##`, you MUST:**

1. **Run the cd command shown in the output** - e.g., `cd .worktrees/###-feature-WP##/`
2. **ALL file operations happen in this directory** - Read, Write, Edit tools must target files in the workspace
3. **NEVER write deliverable files to the main repository** - This is a critical workflow error

**Why this matters:**
- Each WP has an isolated worktree with its own branch
- Changes in main repository will NOT be seen by reviewers looking at the WP worktree
- Writing to main instead of the workspace causes review failures and merge conflicts

**Verify you're in the right directory:**
```bash
pwd
# Should show: /path/to/repo/.worktrees/###-feature-WP##/
```

<details><summary>PowerShell equivalent</summary>

```powershell
Get-Location
# Should show: C:\path\to\repo\.worktrees\###-feature-WP##\
```

</details>

---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Implementation Workflow

Documentation implementation follows the standard workspace-per-WP model:
- **Worktrees used** - Each WP has its own worktree with dedicated branch (same as code missions)
- **Templates populated** - Use Divio templates as starting point
- **Generators invoked** - Run JSDoc/Sphinx/rustdoc to create API reference
- **Content authored** - Write tutorial/how-to/explanation content in worktree
- **Quality validated** - Check accessibility, links, build before merging
- **Release prepared (optional)** - Draft `release.md` when publish is in scope

---

## Per-Work-Package Implementation

### For WP01: Structure & Generator Setup

**Objective**: Create directory structure and configure doc generators.

**Steps**:
1. Create docs/ directory structure:
   ```bash
   mkdir -p docs/{tutorials,how-to,reference/api,explanation}
   ```
   <details><summary>PowerShell equivalent</summary>

   ```powershell
   'tutorials','how-to','reference\api','explanation' | ForEach-Object { New-Item -ItemType Directory -Force -Path "docs\$_" }
   ```

   </details>
2. Create index.md landing page:
   ```markdown
   # {Project Name} Documentation

   Welcome to the documentation for {Project Name}.

   ## Getting Started

   - [Tutorials](tutorials/) - Learn by doing
   - [How-To Guides](how-to/) - Solve specific problems
   - [Reference](reference/) - Technical specifications
   - [Explanation](explanation/) - Understand concepts
   ```
3. Configure generators (per plan.md):
   - For Sphinx: Create docs/conf.py from template
   - For JSDoc: Create jsdoc.json from template
   - For rustdoc: Update Cargo.toml with metadata
4. Create build script:
   ```bash
   #!/bin/bash
   # build-docs.sh

   # Build Python docs with Sphinx
   sphinx-build -b html docs/ docs/_build/html/

   # Build JavaScript docs with JSDoc
   npx jsdoc -c jsdoc.json

   # Build Rust docs
   cargo doc --no-deps

   echo "Documentation built successfully!"
   ```
5. Test build: Run build script, verify no errors

**Deliverables**:
- docs/ directory structure
- index.md landing page
- Generator configs (conf.py, jsdoc.json, Cargo.toml)
- build-docs.sh script
- Successful test build

---

### For WP02-05: Content Creation (Tutorials, How-Tos, Reference, Explanation)

**Objective**: Write documentation content using Divio templates.

**Steps**:
1. **Select appropriate Divio template**:
   - Tutorial: Use `templates/divio/tutorial-template.md`
   - How-To: Use `templates/divio/howto-template.md`
   - Reference: Use `templates/divio/reference-template.md` (for manual reference)
   - Explanation: Use `templates/divio/explanation-template.md`



*(content truncated)*

## See Also

- [[command-template-spec-kittyplan-documentation-mission]]
- [[command-template-spec-kittyreview-documentation-mission]]
- [[command-template-spec-kittyspecify-documentation-mission]]
- [[command-template-spec-kittytasks-documentation-mission]]
- [[command-template-spec-kittytasks-research-mission]]
- [[command-template-spec-kittytasks-research-mission]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/.kittify/missions/documentation/command-templates/implement.md`
- **Indexed:** 2026-04-17T06:42:10.330029+00:00
