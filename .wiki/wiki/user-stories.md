---
concept: user-stories
source: plugin-code
source_file: exploration-cycle-plugin/scripts/user_story_capture_execute.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.378153+00:00
cluster: story
content_hash: 6a36a9f50f5cea10
---

# User Stories

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/exploration-cycle-plugin/scripts/user_story_capture_execute.py -->
#!/usr/bin/env python
"""
Purpose: User Story generator for the exploration cycle.
Reads exploration capture documents (session brief, BRD draft, problem framing)
and produces a structured Markdown story set in either:
  - standard format: "As a [user] I want [goal] so that [benefit]"
  - gherkin format: standard + Given/When/Then Acceptance Criteria blocks

Designed for CLI dispatch pattern in the exploration cycle:
  cat session-brief.md brd-draft.md | pythonexecute.py --output user-stories-draft.md
"""

import argparse
import sys
from datetime import date
from pathlib import Path


STANDARD_TEMPLATE = """\
# User Stories
Source: {sources}
Format: standard
Date: {today}
Status: DRAFT — Requires human review before backlog entry

> **Agent Instructions**: Derive user stories from the input captures.
> One story per row. Use the format: `As a [user type], I want [goal], so that [benefit]`.
> Assign priority from High / Medium / Low based on business impact in the captures.
> Mark any story you cannot confidently derive as `[NEEDS HUMAN INPUT]`.
> Do NOT invent scope not present in the source.

---

## Epic: [Extract high-level epic name from session brief]

### Core Slice (P0 — First Implementation)

| ID | As a... | I want to... | So that... | Priority | Status |
|----|---------|--------------|------------|----------|--------|
| US-001 | [user type from captures] | [goal extracted from FR or prototype observation] | [benefit — business outcome] | High | [UNCONFIRMED] |
| US-002 | [user type] | [goal] | [benefit] | High | [UNCONFIRMED] |
| US-003 | [NEEDS HUMAN INPUT: not enough context] | — | — | — | Gap |

### Later Scope (P1 / P2 — Deferred)

| ID | As a... | I want to... | So that... | Priority | Status |
|----|---------|--------------|------------|----------|--------|
| US-010 | [user type] | [deferred goal] | [benefit] | Low | [UNCONFIRMED] |

---

## Story Gaps & Prioritisation Questions

1. [Question about scope or ordering — aligned to a specific US gap]
2. [Is US-002 a P0 or P1? Unclear from captures]

---

## Out of Scope (Excluded from This Slice)

- [Features mentioned in captures but explicitly excluded]
"""

GHERKIN_TEMPLATE = """\
# User Stories with Acceptance Criteria (Gherkin)
Source: {sources}
Format: gherkin
Date: {today}
Status: DRAFT — Requires human review before backlog entry

> **Agent Instructions**: Derive user stories AND Acceptance Criteria from the input captures.
> For each story, include at least one Scenario in Given/When/Then format.
> Use `[NEEDS HUMAN INPUT]` for any story or AC you cannot confidently populate.
> Do NOT invent edge cases not implied by the captures.

---

## Epic: [Extract from session brief]

---

### US-001: [Short title extracted from captures]

**Story**: As a [user type], I want [goal], so that [benefit].
**Priority**: High
**Status**: [UNCONFIRMED]

**Acceptance Criteria**:

```gherkin
Scenario: Happy path — [short label]
  Given [precondition from captures]
  When [user action or system event]
  Then [expected system outcome]

Scenario: Edge case — [short label]
  Given [alternate precondition]
  When [edge case trigger]
  Then [expected outcome for edge case]
```

---

### US-002: [Short title]

**Story**: As a [user type], I want [goal], so that [benefit].
**Priority**: Medium
**Status**: [UNCONFIRMED]

**Acceptance Criteria**:

```gherkin
Scenario: [NEEDS HUMAN INPUT — not enough context to define AC from source]
```

---

## Story Gaps & Prioritisation Questions

1. [Gap mapped to a specific US]
2. [Ordering or priority question]

---

## Out of Scope

- [Excluded features]
"""

FORMAT_TEMPLATES = {
    "standard": STANDARD_TEMPLATE,
    "gherkin": GHERKIN_TEMPLATE,
}


def load_input(paths: list[str]) -> str:
    chunks = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"Warning: input file not found: {p}", file=sys.stderr)
            continue
        chunks.append(path.read_text(encoding="utf-8"))
    return "\n\n-

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/user-story-capture/scripts/execute.py -->
#!/usr/bin/env python3
"""
Purpose: User Story generator for the exploration cycle.
Reads exploration capture documents (session brief, BRD draft, problem framing)
and produces a structured Markdown story set in either:
  - standard format: "As a [user] I want [goal] so that [benefit]"
  - gherkin format: standard + Given/When/Then Acceptance Criteria blocks

Designed for CLI dispatch pattern in the exploration cycle:
  cat session-brief.md brd-draft.md | python3 execute.py --output user-stories-draft.md
"""

import argparse
import sys
from datetime import date
from pathlib import Path


STANDARD_TEMPLATE = """\
# User Stories
Source: {sources}
Format: standard
Date: {today}
Status: DRAFT — Requires human review before backlog entry

> **Agent Instructions**: Derive user s

*(combined content truncated)*

## See Also

- [[use-npx-to-lazily-execute-mermaid-cli-so-the-user-doesnt-need-to-globally-install-it]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/scripts/user_story_capture_execute.py`
- **Indexed:** 2026-04-27T05:21:04.378153+00:00
