# Red Team Briefing

**Generated:** {timestamp}
**Status:** 🛑 WAITING FOR APPROVAL

## 1. Context & Claims
The agent has paused execution to request memory ingestion.
{claims_section}

## 2. Review Manifest
**Instructions:** You MUST inspect these files before approving.
{manifest_section}

## 3. Git Context
{diff_context}

## 4. Adversarial Prompts
**Challenge the Agent:** Copy/Paste these into the chat to verify integrity.
{prompts_section}

---
## Approval Instructions
If you are satisfied with this review:
1.  Run the `/approve` command (or `commit_ingest` tool).
2.  The system will sign and persist the memory.

If you are NOT satisfied:
1.  Reject the request (or simply do not approve).
2.  Instruct the agent to fix the defects.
