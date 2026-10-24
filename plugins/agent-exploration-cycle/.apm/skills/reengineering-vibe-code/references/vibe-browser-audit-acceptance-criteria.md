# Acceptance Criteria: vibe-browser-audit

## Correct Behaviors

- **Correct:** Vibe-browser-audit checks the target URL and runs validation checks to ensure the server is responsive before launching browser drivers.
- **Correct:** Vibe-browser-audit executes Playwright/Puppeteer/CDP commands to extract structural DOM layouts and styles without skipping interactive modals or tabs.
- **Correct:** Vibe-browser-audit intercepts and logs the complete list of HTTP traffic (endpoints, statuses, payload schemas) during interactive flows.
- **Correct:** Vibe-browser-audit compiles all findings into a structured `DISCOVERY_REPORT.md` written to `exploration/captures/`.

## Incorrect Behaviors

- **Incorrect:** Vibe-browser-audit generates a placeholder `DISCOVERY_REPORT.md` without executing active browser inspections.
- **Incorrect:** Vibe-browser-audit overlooks secondary UI screens (modals, drawers, multi-step sub-forms) or ignores console logs and warnings.
- **Incorrect:** Vibe-browser-audit hardcodes sensitive environment URLs or local credentials inside its browser-automation code.
