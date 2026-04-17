---
concept: humanize
source: plugin-code
source_file: voice-writer/skills/humanize/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.443688+00:00
cluster: patterns
content_hash: 3370dca42cb393cf
---

# Humanize

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: humanize
description: >
  This skill should be used when the user wants to "humanize this", "make this
  sound less AI", "rewrite this naturally", "remove AI patterns", "make this
  more conversational", "this sounds robotic", "edit for voice or tone", or
  pastes text that reads like LLM output (parallel structure in threes, em
  dashes, semicolons, hedging phrases, hollow affirmations). Also trigger for
  "make this sound like me", "clean up this draft", or "rewrite this for
  LinkedIn/email/Slack". Use this skill even for a single sentence if the
  user's intent is to make writing feel more human. Do NOT use for pure
  grammar correction or style guide work unrelated to humanizing AI patterns.
allowed-tools: Read
---

# Humanize

Transform stiff, AI-flavored, or over-polished writing into something that
sounds like it came from an actual person -- with a distinct voice, natural
rhythm, and the small imperfections that signal authenticity.

---

## Input Context

The user provides text to humanize. They may also provide:

- **Voice context**: "write like a senior engineer", "this is for my LinkedIn"
- **Channel**: email, social post, blog, Slack, internal memo
- **Tone direction**: "warmer", "more direct", "less formal"

If none of these are provided, infer them from the text. Ask only if the
target voice is genuinely ambiguous and would change the output significantly.

If the user has placed writing samples in
`references/voice-profile/my-voice.md`, read that file before rewriting.
It contains their preferred sentence patterns, register, and vocabulary. Apply
those patterns instead of projecting a generic voice.

---

## Phase 1: Diagnose

Before rewriting, read the text as a human editor would. Identify internally:

1. **AI fingerprints** -- which structural patterns are present?
2. **What's actually being said** -- strip the structure, find the real content
3. **Who should be saying it** -- what kind of person, in what context?
4. **What's missing** -- real writing usually has a point of view, a concrete
   detail, or a light edge that has been smoothed away

Do this quickly and internally. Do not narrate this to the user unless asked.

For a full catalog of AI patterns and their fixes, read:
`references/patterns.md`

---

## Phase 2: Rewrite

Apply these principles in order:

**Voice first, fixes second.** Do not just remove bad patterns. Replace them
with something that has character. A human does not just avoid em dashes --
they use shorter sentences, or fragments, or a question.

**One idea per sentence, usually.** Most AI text over-compounds. Break it up.
Short sentences are not unsophisticated -- they are confident.

**Concrete over abstract.** Replace vague abstractions with specifics wherever
possible. "Improved performance" becomes "cut load time in half." "Valuable
insights" -- name one. If there is no specific to reach for, cut the claim.

**Preserve the actual content.** Never add claims, details, or assertions not
present in the source. Never invent examples. If something needs elaboration,
flag it for the user -- do not fabricate it.

**Register calibration.** Match the register to the channel. Read
`references/channel-rules.md` for channel-specific constraints (LinkedIn,
email, blog, Slack). Character limits in that file are hard limits.

**Natural emphasis.** Real writers use bold and italics sparingly and only for
genuine emphasis. If the text over-emphasizes, strip it.

---

## Phase 3: Quality Check

Run these mentally before returning output:

1. **Read-aloud test** -- Does it sound like a person is actually saying this?
   Any phrases you would never hear in speech?
2. **Fingerprint scan** -- Any surviving em dashes doing decoration work? Any
   triads? Any hollow pivots (see `references/patterns.md`)?
3. **Content fidelity** -- Did anything get added that was not in the source?
   Did any meaning get lost?
4. **Voice consistency** -- Is the register consistent from start to finish?
5. **Ch

*(content truncated)*

## See Also

*(No related concepts found yet)*

## Raw Source

- **Source:** `plugin-code`
- **File:** `voice-writer/skills/humanize/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.443688+00:00
