# Acceptance Criteria: optimize-agent-instructions

## Trigger Accuracy

- Fires on requests to optimize/audit/improve/clean CLAUDE.md, GEMINI.md, or copilot-instructions.md
- Fires on "apply Karpathy principles" requests
- Does NOT fire on: skill improvements, plugin creation, bug fixes, README updates, or other non-instruction-file tasks

## Output Quality

### Discovery Phase
- [ ] Detects which instruction files exist before asking questions
- [ ] Asks about active AI platforms (Claude Code, Copilot, Gemini CLI)
- [ ] Asks about Super-RAG stack presence
- [ ] Asks about project-specific rules to preserve

### Audit Phase
- [ ] Scores each file against the 12-point Quality Checklist
- [ ] Reports audit score before making any changes
- [ ] Identifies stale AI artifacts specifically (e.g. "Would you like X configured?")
- [ ] Identifies foreign content from other projects

### Rewrite Phase
- [ ] Gets confirmation before writing each file
- [ ] Preserves valid project-specific rules
- [ ] Applies all four Karpathy principles in project-specific language
- [ ] Adds platform-specific sections (Gemini tool mapping, etc.)
- [ ] Never creates files that didn't already exist unless asked

### Completion
- [ ] All three files score 10/12 or better after rewrite
- [ ] No stale artifacts remain
- [ ] Gemini tool mapping present in GEMINI.md only
- [ ] copilot-instructions.md framed as authoritative (not "a copy of CLAUDE.md")
- [ ] Super-RAG table present if stack is installed

## Anti-patterns to Avoid

- Writing files without reading them first
- Removing valid project-specific rules
- Adding sections that don't apply to the project
- Copy-pasting Karpathy principles verbatim without adapting to the domain
- Creating CLAUDE.md / GEMINI.md / copilot-instructions.md if they don't exist (unless asked)
