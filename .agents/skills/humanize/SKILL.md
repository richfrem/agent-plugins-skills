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
5. **Channel fit** -- Would this work in the specified channel? Does it meet
   any character or length limits?

If any of these fail, fix before returning.

---

## Output Format

**Default:** Return the rewritten text only -- no preamble, no explanation,
no "Here is the humanized version:". Just the text.

**Add a note only when:**
- A claim was removed because it had no source support:
  *(Removed: "X" -- no supporting detail in source. Add if you have one.)*
- A length limit may have been violated -- note the count
- An ambiguity in the original was resolved one way -- note the interpretation

**When the user asks for explanation:** Walk through 2-3 of the most
significant changes and why. Keep it brief. Focus on what changed in
voice and rhythm, not just what was deleted.

---

## Edge Cases

**"Make it sound like me"** -- Read `references/voice-profile/my-voice.md`
first. Extract voice patterns: sentence length, how they open paragraphs,
whether they use fragments, their preferred register, recurring vocabulary.
Apply those patterns. If no profile exists, ask the user for 1-2 examples
of their writing before rewriting.

**Minimal AI contamination** -- If the text is mostly fine but has a few
patterns, do targeted surgery rather than a full rewrite. Preserve what
is working.

**Heavy AI contamination** -- If nearly every sentence has a pattern, do a
full rewrite. Do not try to patch it. Rewrite from the core message outward.

**Soulless but technically correct** -- The fix is not removing patterns.
It is adding a point of view, a specific detail, or a human beat. Make a
small creative choice and flag it if needed.

**Formal writing (legal, regulatory, academic)** -- Some register is
intentional. Do not over-humanize. Focus only on removing AI patterns that
would not appear in competent human writing of that type.

---

## Reference Files

Read these when needed (Progressive Disclosure -- do not load all at once):

- `references/patterns.md` -- Full AI pattern catalog with bad to good rewrites
- `references/channel-rules.md` -- Channel-specific rules and hard limits
- `references/voice-profile/README.md` -- How users set up their voice profile
- `references/voice-profile/my-voice.md` -- User's personal voice samples (if populated)
