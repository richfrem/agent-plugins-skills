# voice-writer

Transform AI-generated or over-polished writing into authentic human voice.

The `humanize` skill diagnoses AI fingerprints (structural patterns, hollow
filler, vague adjectives), rewrites with real voice and rhythm, and optionally
calibrates to your personal writing style using a voice profile you maintain
locally.

---

## Installation

### Cross-agent via npx (recommended for end users)

```bash
npx skills add richfrem/agent-plugins-skills/plugins/voice-writer
```

Works across Claude Code, Antigravity / Gemini CLI, GitHub Copilot, Cursor,
Roo Code, and any other agent that supports the Agent Skills open standard.

### Full local deployment via bridge (Claude Code + Antigravity)

```bash
# From the agent-plugins-skills project root:
python ./plugin_installer.py --plugin plugins/voice-writer

# Or install all plugins at once:
python ./install_all_plugins.py
```

### Local development install

```bash
rm -rf .agents/ && npx skills add ./plugins/voice-writer --force
```

---

## Included Skills

### `humanize`

Rewrites AI-flavored or over-polished text so it sounds like a specific,
competent human wrote it.

**Trigger phrases:**
- "Humanize this"
- "Make this sound less AI"
- "Rewrite this naturally"
- "This sounds robotic"
- "Make it sound like me"
- "Edit for my voice/tone"
- "Clean up this draft for LinkedIn / email / Slack"

**Key capabilities:**
- Diagnoses and removes structural AI patterns (triads, em dash pivots, hollow filler)
- Calibrates to channel-specific constraints (LinkedIn hard limits, email length, Slack brevity)
- Reads your personal voice profile for "make it sound like me" requests
- Returns rewrite-only output by default (no preamble, no explanation)

---

## Voice Profile Setup

The skill can learn your specific writing voice. Populate:

```
skills/humanize/references/voice-profile/my-voice.md
```

with 2-5 examples of your own writing labelled by channel. See
`skills/humanize/references/voice-profile/README.md` for format instructions.

When you ask "make this sound like me", the agent reads your profile before
rewriting. The more samples you add, the more accurate the calibration.

> The profile file lives locally and is never shared. Add it to `.gitignore`
> if you want to keep it private.

---

## Plugin Structure

```
voice-writer/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── humanize/
│       ├── SKILL.md
│       └── references/
│           ├── patterns.md           # Full AI pattern catalog
│           ├── channel-rules.md      # Per-channel rules and hard limits
│           └── voice-profile/
│               ├── README.md         # Setup guide for users
│               └── my-voice.md       # Your writing samples (populate this)
└── README.md
```

---

## License

MIT
