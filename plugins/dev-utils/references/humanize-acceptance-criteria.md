# Acceptance Criteria — Humanize Skill

This document specifies the validation criteria for confirming the correct operation of the `humanize` skill.

## 1. AI Pattern Detection and De-AI Calibration

- [ ] The skill successfully identifies common AI fingerprints (e.g. parallel triplets, excessive em dashes, hollow pivots, hedging).
- [ ] Rewritten text replaces AI patterns with varied sentence structures, conversational flow, and natural rhythm.

## 2. Voice and Profile Fidelity

- [ ] When the user has a custom profile in `references/voice-profile/my-voice.md`, the skill reads and applies the vocabulary, register, and sentence length patterns defined in that profile.
- [ ] The output retains the core facts, content, and meaning of the source text without inventing any new details.

## 3. Channel Compliance

- [ ] Output satisfies channel-specific limits (e.g. Slack brevity, LinkedIn style, email directness) as specified in `references/channel-rules.md`.
- [ ] By default, the skill returns only the rewritten text without conversational introductions or meta-puzzles (e.g. no "Here is the humanized version").
