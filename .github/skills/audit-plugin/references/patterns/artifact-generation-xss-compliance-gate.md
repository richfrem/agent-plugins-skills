# Artifact Generation XSS Compliance Gate

**Pattern Name**: Artifact Generation XSS Compliance Gate
**Category**: Output & Contracts
**Complexity Level**: L5 (Advanced Security Pattern)

## Description
Agents often require the capability to generate complete `.html` or `.svg` user interfaces as artifacts. However, giving an agent unconstrained write access to a DOM opens severe Cross-Site Scripting (XSS) vectors. If the agent hallucinates external asset imports or is manipulated into writing malicious inline scripts, it executes in the user's rendering context. This pattern establishes a non-negotiable compliance block that forbids specific tags and network requests within the emitted artifact.

## When to Use
- When generating web viewers, interactive dashboards, or SVG files.
- When creating any file format that supports embedded executable scripts (like PDF or HTML).

## Implementation Example
```markdown
### REQUIRED: Artifact Dom Generation Security
Before emitting the final HTML/SVG artifact, you MUST comply with these security boundaries:
1. NO EXTERNAL IMPORTS: You may not write any `<script src="...">` or `<link href="...">` tags other than the explicitly whitelisted CDNs defined in this template.
2. NO EXTERNAL MEDIA: Do not embed remote `<img>`, `<audio>`, or `<video>` tags linking to unverified domains.
3. STRICT DOM SCOPE: All of your generated Javascript MUST only target elements inside the `#app-container` div. You are forbidden from manipulating `document.body`, `window`, or triggering `localStorage`.
```

## Anti-Patterns
- Telling the agent to "write whatever HTML is needed to visualize the data" without explicitly restricting the imports.
- Relying on the host application's CSP (Content Security Policy) to catch the agent's mistakes, rather than preventing the agent from making the mistake upstream.
