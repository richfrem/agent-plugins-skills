---
description: >
  When a session references a local background document (a prompt file, issue body, spec,
  or handoff doc), that document must be read and used before asking the human any
  interview/clarifying question it already answers.
globs: ["**/*"]
---

# Background Document Priority

If the user's opening message references, pastes, or points to a local file (a prompt,
issue body, prior spec, handoff doc), read that file FIRST, before asking any
Socratic/interview question. Check every open question against it. For any question the
document already answers, use the document's answer directly — via
`record_source_assisted_answer_candidate(source_path=..., source_authorized=True, ...)`
where `work-intake`'s control plane is active, or by simply citing the source inline
otherwise. Never make the human re-answer, live, something they already wrote down for you.

Only ask a live question for what the document genuinely leaves open or ambiguous.

**Why this exists:** a 2026-09-13 session ignored this exact instruction after it was
stated explicitly in the referenced document, forcing the human to re-answer already-written
information one question at a time and causing significant, avoidable session friction.
