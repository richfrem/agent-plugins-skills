---
name: vibe-browser-audit
description: Audits prototype UI/UX and behavior utilizing Chrome DevTools Protocol (CDP), Playwright, or Puppeteer to produce comprehensive discovery reports on layouts, styling, and state.
---

# Visual & Functional Browser Audit (vibe-browser-audit)

Performs comprehensive visual and functional inspections of running prototypes using browser automation, producing detailed discovery reports.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Only audit local or permitted prototype URLs; never execute intrusive automation on unauthorized endpoints.
- Separate core logic salvage ("Preservation Gems") from technical debt to be remediated.
- Always output standardized discovery reports directly to `exploration/captures/DISCOVERY_REPORT.md`.

## Quick start
1. Confirm prototype is running on designated port (e.g., `http://localhost:3000`).
2. Launch Playwright or CDP crawler to capture DOM trees, design tokens, and network interactions.
3. Compile findings into `exploration/captures/DISCOVERY_REPORT.md`.

## Workflow
1. **Connection Setup**: Verify prototype URL and initialize Playwright/Puppeteer/CDP connection.
2. **Visual UX Audit**: Crawl every distinct page, modal, and drawer; catalog component trees and design tokens.
3. **Behavioral Audit**: Trigger user flows, capture HTTP traffic schemas, and record console logs.
4. **Logic & Debt Analysis**: Classify business logic to preserve versus technical debt to remediate.
5. **Report Compilation**: Write exhaustive `DISCOVERY_REPORT.md` into `exploration/captures/`.

## Verification
- Confirm `exploration/captures/DISCOVERY_REPORT.md` exists and includes all four standard sections.
- Verify screen crawl captures all major application routes and states.
- Ensure API schemas and payload contracts are accurately documented.

## References
- [acceptance-criteria.md](references/acceptance-criteria.md)
