---
description: Rapid prototyping of Oracle Forms modernization. Calls /investigate-form for analysis, then generates React code.
tier: 3
---

# /modernize-form

**Purpose:** Generate modern React code from an Oracle Form by calling the reusable `/investigate-form` analysis module, then implementing UI components.

> 
> **Architecture:** This workflow is an **OUTPUT WORKFLOW**. It calls the shared `/investigate-form` module for analysis, then focuses on React code generation.

**Input:** `[FormID]` - e.g., `JUSE0005`, `JCSE0012`, `JCSE0090`
**Diagram:** `../skills/legacy-system-oracle-forms/references/diagrams/workflows/form-discovery.mmd`

---

## Spec-Kitty Lifecycle Integration

This workflow follows the 6-step Spec-Kitty lifecycle:

| Step | Command | Description | This Workflow |
|------|---------|-------------|---------------|
| 1 | `/spec-kitty.specify` | WHAT to build | Phase 0.5 (spec.md) |
| 2 | `/spec-kitty.plan` | HOW to build | Phase 0.5 (plan.md) |
| 3 | `/spec-kitty.tasks` | Work packages | Phase 0.6 (tasks.md, WP files) |
| 3.5 | `spec-kitty implement` | Create worktree | **Phase 0.7** |
| 4 | `/spec-kitty.implement` | Execute code | Phases 1-5 |
| 5 | `/spec-kitty.review` | Quality gates | Phase 6.5 |
| 6 | `/spec-kitty.accept` | Validate readiness | Phase 7 (Step 24) |
| 7 | `/spec-kitty_retrospective` | Capture learnings | Phase 7 (Step 25) |
| 8 | `/spec-kitty.merge` | Merge + cleanup | Phase 7 (Step 27) |

---

## Phase 0: Pre-Flight (MANDATORY)

> **IMPORTANT**: You MUST be on `main` branch before running spec-kitty.
> Spec-kitty will create the feature branch automatically.

```bash
# Create feature branch and folder structure
spec-kitty agent feature create-feature "modernize-form-[FormID]" --json
```
*This primitive command handles branch creation and folder scaffolding without interactive prompts.*

---

## Phase 0.5: Spec & Plan (MANDATORY)
**STOP**: Before running any analysis or code generation, you MUST establish the plan.

### Step 0a: Run Context Analysis
```bash
python .agent/skills/context-bundler/scripts/manifest_manager.py init --target [FormID] --type form
```
Review the generated bundle for form understanding.

### Step 0b: Create spec.md
Create `kitty-specs/###-modernize-form-[FormID]/spec.md` with:
- Form identity and purpose
- UI structure (tabs, blocks)
- Database dependencies
- Business rules
- Acceptance criteria

### Step 0c: Create plan.md  
Create `kitty-specs/###-modernize-form-[FormID]/plan.md` with:
- Component creation plan
- File modifications
- Verification steps

### Step 0d: Human Review Gate
1. Open `spec.md` and `plan.md` for the user.
2. **ASK**: "I have created the Spec and Plan. Please review. Do you want to refine the scope or proceed?"
3. **WAIT** for explicit user approval ("Proceed", "Go", "Execute").

---

## Phase 0.6: Tasks & Work Packages (MANDATORY)

### Step 0e: Create tasks.md
Create `kitty-specs/###-modernize-form-[FormID]/tasks.md` with:
- Subtask registry (T001, T002...)
- Work packages (WP01, WP02...)
- Implementation phases

### Step 0f: Create WP Prompt Files
Create work package prompts in `kitty-specs/###-modernize-form-[FormID]/tasks/`:
- `WP01-analysis-planning.md`
- `WP02-implementation.md`
- (Additional WPs as needed)

Each WP file MUST include:
```yaml
---
work_package_id: "WP##"
title: "Work Package Title"
lane: "planned"
dependencies: ["WP##"]  # or empty
subtasks: ["T###", "T###"]
---
```

### Step 0g: Finalize Tasks (Commit to Main)
```bash
spec-kitty agent feature finalize-tasks --json
```
This parses dependencies and commits tasks to main.

---

## Phase 0.7: Create Worktree (MANDATORY for Clean Merge)

> **⚠️ CRITICAL**: This step creates the isolated workspace that enables `spec-kitty merge` to work properly.

### Step 0h: Create Implementation Worktree
```bash
spec-kitty implement WP01
```

**What this does:**
1. Creates `.worktrees/###-modernize-form-[FormID]-WP01/` directory
2. Checks out a feature branch for this work package
3. Sets up isolated workspace for implementation

**After running:**
- You are now in the worktree directory
- All implementation happens here (Phases 1-5)
- When done, `spec-kitty merge` will work correctly

### For Multiple Work Packages
If you have WP01 (planning) and WP02 (implementation):
```bash
# Complete WP01 first
spec-kitty implement WP01
# ... do WP01 work ...
spec-kitty agent tasks move-task WP01 --to done --note "Complete"

# Then WP02 (with dependency on WP01)
spec-kitty implement WP02 --base WP01
# ... do WP02 work ...
```

---

# 🚀 QUICK START

## Phase 1: Analysis (Call /investigate-form)

### Step 1: Initialize Expert Persona
```bash
view_file tools/ai-resources/prompts/personas/Oracle_Forms_Expert_System_Prompt.md
```

### Step 2: Run Investigation Module
```bash
/investigate-form [FormID]
```

**What this does:**
1. Initializes context (`.agent/skills/context-bundler/scripts/manifest_manager.py init --target [FormID] --type form`)
2. Runs the **Recursive Context Spiral** (Level 1-4 dependency tracing)
3. Executes **Multi-Pass Mining**:
   - Pass 1: Blocks → Data Contracts (API Endpoints)
   - Pass 2: Triggers → Custom Hooks (useEffect, Zod)
   - Pass 3: UI Layout → Component Hierarchy (Tabs, Modals)
   - Pass 4: Navigation → Routing (React Router)
   - Pass 5: Security → Auth Guards (RBAC)
4. Performs **Dependency & Lineage Analysis**

**Output:** Fully populated `temp/context-bundles/[FormID]_context.md`

> **⚠️ DO NOT PROCEED until `/investigate-form` completes successfully.**

### Step 3: Verify Context Completeness
```bash
view_file temp/context-bundles/[FormID]_context.md
```
Confirm the bundle contains all extraction targets.

---

## Phase 2: Configuration Strategy

### Step 4: Review Role-Based Configuration
**CRITICAL**: Review the **UI Role Based Configuration Strategy** before proceeding.
```bash
view_file plugins/legacy system/references/architecture/UI_Role_Based_Configuration_Strategy.md
```

### Step 5: Generate UI Config
```bash
python scripts/generate_ui_config.py --target [FormID]
```
*Generates:* `sandbox/ui/src/rules/[FormID]_Rules.ts`

### Step 6: Visual & Layout Reconstruction
Find legacy screenshots to map the visual hierarchy:
```bash
find_by_name --pattern "*[FormID]*" --directory docs/screenshots/LegacyOracle
```

### Modernization Mapping Table
| Source Artifact | Extract | Modern Equivalent |
|-----------------|---------|-------------------|
| **Form.mmb** (Menu) | Menu structure, Roles | `MenuBar.tsx`, `generate_ts_rules.py` |
| **Form.fmb** (Canvas) | Blocks, Windows | `PageLayout.tsx`, `<Modal />`, `<Tabs />` |
| **Form.fmb** (TabPage) | Tab Canvases | `<Tabs />` component |
| **Form.fmb** (Items) | Fields, LOVs, Radios | `Input`, `Select`, `Checkbox` components |
| **Form.pll** (Library) | Shared Logic | `src/hooks/use[LibName].ts`, `src/utils/` |
| **Form.olb** (ObjLib) | Styles | `src/theme/`, `@bcgov/design-tokens` |
| **Database** (Pkg/Tab) | CRUD, Procedures | `.NET API Endpoints`, `DomainModels` |

---

## Phase 3: Sandbox Setup

### Step 7: Initialize Sandbox Structure
```powershell
$formId = "[FormID]"
$sandboxPath = "sandbox"
New-Item -ItemType Directory -Force -Path "$sandboxPath/ui/src/pages", "$sandboxPath/api", "$sandboxPath/context/$formId"
```

### Step 8: Standard Dependencies
Ensure `sandbox/ui/package.json` includes:
- `@bcgov/design-tokens` (Mandatory for theming)

---

## Phase 4: Implementation (Code & Design)

### Step 9: Ensure Index CSS Alignment
Check `sandbox/ui/src/index.css`:
- Must import `@bcgov/design-tokens/css/variables.css`.
- Must contain `.dashboard-grid` and `.dashboard-button-card` classes.

### Step 10: Create Form Page Component (Modular Building Blocks)
Create `sandbox/ui/src/pages/[FormID].tsx`:

- **Role-Based Rules**: Import from `../rules/[FormID]_Rules`
- **Theming**: Use BC Design System tokens
- **Architecture**: You MUST use the **Modular Building Blocks** pattern. Do not build one massive monolithic React component. Instead:
  1. Build small, pure, independent UI components in `sandbox/ui/src/components/` (e.g. `<CustomerSearch />`, `<OrderDetails />`).
  2. Build a single convenience wrapper (the specific Form Page) in `src/pages/` that simply orchestrates the smaller building blocks using standard React layout patterns.
  3. Map Oracle blocks to these distinct React components.

### Step 11: Quality Assurance (Gap Analysis)
1. **XML vs React Audit**: Every Block → Section/Grid?
2. **Every Canvas[Tab]** → Tab component?
3. **Every LOV** → Search/Select component?

### Step 12: Register Form in Router
Update `sandbox/ui/src/App.tsx` with route for `/[FormID]`.

### Step 13: User Approval Gate
**STOP**: Present implementation plan to User. Ask: "Does this capture the complexity of [FormID]?"
**Only proceed** when User approves.

---

## Phase 5: Run & Iterate

### Step 14: Install Dependencies
```bash
cd sandbox/ui && npm install
```

### Step 15: Run Development Server
```bash
cd sandbox/ui && npm run dev
```
Opens at: **http://localhost:3030/**

---

## Phase 6: Documentation Feedback

### Step 16: Update Form Overview (Gaps & Insights)
If modernization reveals gaps in existing Overview:
```bash
view_file legacy-system/oracle-forms-overviews/forms/[FormID]-Overview.md
# Update with discovered dependencies, business rules
```

### Step 17: Register New Business Rules
```bash
python scripts/business_rules_inventory_manager.py --source [FormID] --description "Title" --priority P2
```

### Step 18: Post-Processing Pipeline
```bash
python scripts/enrich_links_v2.py --file [OverviewFile]
/codify-rlm-distill [OverviewFile]
python scripts/update_analysis_tracking.py [FormID] --notes "Modernized to React"
```

---

## Phase 6.5: Review & Quality Gates (MANDATORY)

### Step 19: Update Work Package Status
Mark work packages as `lane: "for_review"` in their frontmatter.

### Step 20: Run Quality Review
```bash
/spec-kitty.review
```

This performs:
- Dependency check validation
- Code review against acceptance criteria
- Definition of Done verification

### Step 21: Approve or Request Changes
**If approved**: Move WP to `lane: "done"`
```bash
spec-kitty agent tasks move-task WP02 --to done --note "Review passed: implementation complete"
```

**If changes needed**: Provide feedback and return to implementation.

---

## Phase 7: Feature Completion — Deterministic Closure Protocol (MANDATORY)

> **Every step below is MANDATORY.** Skipping any step is a protocol violation.
> The closure chain is: **Review → Accept → Retrospective → Merge → Verify → Intel Sync**

### Step 22: Update tasks.md
Mark all work packages and subtasks as complete:
```markdown
- [x] T001: Context analysis
- [x] WP01: Analysis & Planning
```

### Step 23: Review each WP
```bash
spec-kitty agent workflow review --task-id <WP-ID>
```
Repeat for each WP. Verify all WPs are in `done` lane:
```bash
/spec-kitty.status
```

### Step 24: Accept feature
```bash
cd <PROJECT_ROOT>
spec-kitty accept --mode local --feature <SLUG>
```
> **Known Issue**: If accept fails with "missing shell_pid", use `--lenient` flag.

### Step 25: Retrospective (MANDATORY — not optional)
```bash
/spec-kitty_retrospective
```
**PROOF**: `kitty-specs/<SPEC-ID>/retrospective.md` must exist and be committed.

The retrospective includes the **Boy Scout Rule**: identify one improvement action:
- [ ] **Fix Code**: Repair a bug found during execution
- [ ] **Fix Docs**: Clarify a confusing workflow step
- [ ] **Log Task**: Create backlog item if too large

### Step 26: Pre-merge safety check
```bash
cd <PROJECT_ROOT>
git status
git worktree list
spec-kitty merge --feature <SLUG> --dry-run
```
Verify: in main repo root, clean status, no conflicts.

### Step 27: Merge from main repo
```bash
cd <PROJECT_ROOT>
spec-kitty merge --feature <SLUG>
```

> **LOCATION RULE**: ALWAYS run merge from the **main repository root**.
> NEVER `cd` into a worktree to merge. The `@require_main_repo` decorator blocks this.

If merge fails mid-way:
```bash
spec-kitty merge --feature <SLUG> --resume
```

### Step 28: Post-merge verification
```bash
git log --oneline -5
git worktree list
git branch
git status
```
Verify:
- [ ] Merge commit(s) visible in log
- [ ] No orphaned worktrees remain
- [ ] WP branches deleted
- [ ] Working tree is clean

### Step 29: Intelligence sync
```bash
python scripts/enrich_links_v2.py --file [OverviewFile]
python scripts/update_analysis_tracking.py [FormID] --notes "Modernized to React"
```

---

# 🔄 ITERATION COMMANDS

## Nuke and Restart UI Only
```powershell
cd sandbox
Remove-Item -Recurse -Force ui
New-Item -ItemType Directory -Force -Path "ui/src/components"
```

## Full Reset
```powershell
cd sandbox
Remove-Item -Recurse -Force ui, api, context -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path "ui/src/components", "api", "context"
```

---

# 🎯 OUTPUT EXPECTATIONS

After running this workflow, you should have:
1. ✅ **Running React app** at http://localhost:3030/
2. ✅ **Form layout** matching Oracle Forms block structure
3. ✅ **Mock data** representing typical records
4. ✅ **Modern BC Gov theme** with professional styling
5. ✅ **Basic CRUD UI** (list, add, edit buttons)
6. ✅ **Complete spec-kitty artifacts** (spec.md, plan.md, tasks.md, WP files)

---

# 📝 NOTES
- **Sandbox is gitignored** - safe to throw away and restart
- **Mock data first** - don't need real API initially
- **Compare with screenshots** - iterate until visual match
- **Reuse CSS** - same theme works across forms
- **Follow full spec-kitty lifecycle** - Quality gates are mandatory

// turbo-all

