# AI Pattern Catalog

Full reference of structural and voice patterns that make writing read as
synthetic. Use this during Phase 1 (Diagnose) and Phase 2 (Fingerprint Scan).

## How to Use

During rewriting, scan for any pattern in the Structural or Voice tables. If
found, apply the Fix column. Trust the Read-Aloud Test over this list -- if a
phrase sounds like a person saying it, it is fine even if it technically
matches a pattern.

---

## Structural Patterns

These are habits the model learned are "good writing" that now read as
machine-generated.

| Pattern | Example | Why It Is AI | Fix |
|---------|---------|-------------|-----|
| Triadic parallelism | "It's fast, reliable, and scalable." | LLM default parallel list construction | Pick two, or prose-ify: "It's fast and surprisingly reliable." |
| Em dash pivot | "The results were surprising -- and illuminating." | Forced drama beat | New sentence. Or drop the second clause entirely. |
| Semicolon bridge | "The data was clear; the team agreed." | Sounds like careful writing, reads as stiff | Period. Two sentences. |
| Nested qualification | "While it's true that X, it's also important to note that Y..." | Hedge stack | State Y directly. Drop the hedge. |
| Colon-pivot header-speak | "Innovation: A New Approach" | Sounds like a slide deck | Rewrite as a sentence. |
| Symmetrical sentence lengths | Every sentence 18-22 words | Metronomic rhythm, no variation | Mix short punchy sentences with longer ones. |
| Passive voice everywhere | "The decision was made by the team." | Diffuses agency | "The team decided." Name the actor. |
| Bullet-ification | Everything broken into 3-5 bullet points | LLM's default output mode | Prose, unless bullets genuinely help scanning |
| The list that ends with "and more" | "Skills, tools, frameworks, and more." | Infinite padding | Name the specific things or omit the list |

---

## Voice Patterns (Hollow Filler)

Phrases that take up space but carry no information or personality.

| Pattern | Why It Is AI | Fix |
|---------|-------------|-----|
| "It's worth noting that..." | Throat-clear filler before the real point | Delete it. State the thing directly. |
| "Let's dive in." | Empty section opener | Start with the first real point |
| "At the end of the day..." | Cliche pivot to a conclusion | State the conclusion |
| "That being said..." | Filler pivot | New sentence. No pivot needed. |
| "In today's world..." | Generic scene-setting | Cut or make it specific: "In Q4 last year..." |
| "It goes without saying that..." | If it goes without saying, don't say it | Cut entirely |
| "With that in mind..." | Empty bridge | New sentence with the actual point |
| "I'm excited to share..." | Hollow enthusiasm | Lead with the news, not the feeling |
| "...and that's okay." | Hollow reassurance | Cut entirely or replace with specifics |
| "I hope this finds you well." | Email padding opener | Remove. Start with the purpose. |
| "Please don't hesitate to reach out." | Sign-off padding | Remove or replace with: "Questions? Email me." |
| "Following up on our conversation..." | Email subject filler | Use the actual topic as the subject line |

---

## AI Adjectives (Vague Tech Vocabulary)

Adjectives that gesture at quality without naming anything specific. When
spotted, replace with what the thing actually does.

| Word | Replace With |
|------|-------------|
| Seamless | Describe how: "No login required", "one-click setup" |
| Robust | Describe what it handles: "Works even when the API is down" |
| Powerful | Name the capability: "Processes 10k rows in under a second" |
| Comprehensive | List what it covers, or just cut |
| Cutting-edge | Name the technology or approach |
| Innovative | Describe what is new about it |
| World-class | Cut. Replace with a specific credential or result. |
| Transformative | Name the transformation |
| Streamlined | Describe what was removed or simplified |
| Value-add | Name the value |

---

## Enthusiasm Without Specificity

AI models generate enthusiasm synthetically without attaching it to anything
real. These phrases signal that the model filled a "positive tone" requirement
with no content.

| Signal | Fix |
|--------|-----|
| "Thrilled to announce..." | State the announcement |
| "Delighted to share..." | Share it |
| "Proud of the work we've done..." | Describe the work |
| "Excited about the possibilities..." | Name one possibility |
| "Grateful for the journey..." | Name what you are grateful for |

---

## Structural Grammar Habits

Patterns at the sentence level that accumulate and create a machine-written
feel even when individual instances seem harmless.

| Pattern | Note |
|---------|------|
| Starting 3+ consecutive sentences with "The" | Monotonous. Vary openings. |
| Every paragraph ending with a summary sentence | Real writing does not always wrap up cleanly |
| "Not only X, but also Y" | "X. Also Y." or just pick one |
| "First... Second... Third..." | Fine occasionally, overused as default org |
| Ending sections with "In conclusion..." | Remove. The last paragraph is the conclusion. |
| "As mentioned above..." | Restructure so it does not need referencing |
