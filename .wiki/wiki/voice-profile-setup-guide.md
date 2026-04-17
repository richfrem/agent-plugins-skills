---
concept: voice-profile-setup-guide
source: plugin-code
source_file: voice-writer/skills/humanize/references/voice-profile/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.445019+00:00
cluster: your
content_hash: c869568436cc35a3
---

# Voice Profile Setup Guide

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Voice Profile Setup Guide

This folder is where you teach the agent your writing voice.

When the `humanize` skill is asked to "make this sound like me", it reads
`my-voice.md` in this folder first to understand your specific style before
rewriting anything. The more examples you provide, the more accurately it
can calibrate.

---

## What to Put Here

Create or edit `my-voice.md` with 2-5 examples of your actual writing. These
can be anything you have written and are happy with -- emails, posts, memos,
messages, or paragraphs from documents.

**Good sources:**
- A LinkedIn post you wrote that performed well or felt "right"
- A well-received email where the tone landed exactly how you intended
- A Slack message that summed up a situation clearly
- A paragraph from a report or memo you re-read and thought "yes, that is exactly what I meant"

**What makes a good sample:**
- It is something you actually wrote, not something AI wrote for you
- You would be happy to use it again as-is
- It represents how you sound at your best in that context

---

## Format to Use in `my-voice.md`

Use the following format for each sample. The `[channel]` tag helps the agent
understand context (it does not apply LinkedIn voice to email rewrites):

```
[channel: linkedin]
Spent the last three months rewriting our onboarding. The old version took
nine steps and 45 minutes. New version: four steps, under ten minutes.
Numbers matter, but the thing I did not expect was that support tickets
dropped 30% the week after launch.

---

[channel: email]
Hi Sarah,

The Q3 report is attached. One number to flag: churn in the enterprise tier
is up 8% vs last quarter. Worth a quick call before Thursday's board meeting.
Available Monday or Tuesday afternoon if that works.

---

[channel: slack]
Quick update -- the deploy is rolled back. Still investigating root cause.
Will post an update by 3pm.
```

---

## Tips

- **One channel per sample** -- do not mix a LinkedIn post style with an email
- **3+ samples is ideal** -- more samples = better calibration
- **Update it over time** -- if your voice evolves, add new samples
- **Do not include AI-generated writing** -- that would teach the agent the wrong thing

---

## Privacy Note

This file lives locally in your project. It is never shared or uploaded anywhere
unless you choose to commit it. Add `references/voice-profile/my-voice.md` to
`.gitignore` if you want to keep it private:

```
references/voice-profile/my-voice.md
```

---

## Files in This Folder

| File | Purpose |
|------|---------|
| `README.md` | This guide -- how to use the voice profile folder |
| `my-voice.md` | Your writing samples (add your own content here) |


## See Also

- [[project-setup-reference-guide]]
- [[project-setup-guide]]
- [[project-setup-guide]]
- [[setup-guide]]
- [[my-voice-profile]]
- [[project-setup-reference-guide]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `voice-writer/skills/humanize/references/voice-profile/README.md`
- **Indexed:** 2026-04-17T06:42:10.445019+00:00
