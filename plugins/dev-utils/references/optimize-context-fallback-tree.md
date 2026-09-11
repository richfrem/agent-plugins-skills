# Procedural Fallback Tree: Optimize Context

## 1. `.claude/` Directory Empty or Absent
- **Condition**: `.claude/` has no duplicate skill symlinks.
- **Action**: Report clean for Pass 1 and proceed to instruction file auditing.

## 2. `plugins/` Directory Not Found
- **Condition**: Current directory is not a plugin repository root or has no `plugins/`.
- **Action**: Skip scanner; warn user that plugin deduplication requires canonical `plugins/` directory.

## 3. Instruction Files Already Lean (<= 80 lines)
- **Condition**: All target instruction files meet the token efficiency budget.
- **Action**: Report files compliant and suggest no rewrite.

## 4. User Declines Instruction Rewrite
- **Condition**: User refuses proposed lean rewrite during interactive confirmation.
- **Action**: Skip Phase 3 rewrite, retaining existing instruction files unchanged.
