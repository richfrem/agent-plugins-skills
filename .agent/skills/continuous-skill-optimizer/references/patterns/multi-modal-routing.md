# Multi-Modal Input Normalization

**Use Case:** Commands that accept external context (images, code files, design URLs, database schemas) and must deterministically route the input based on what the user provided.

## The Core Mechanic

Agents natively struggle with input ambiguity. If a command simply says "Review the design", the agent might hallucinate a design, politely decline, or assume it should search the web. A Multi-Modal router explicitly teaches the agent how to handle the three primary modalities of context injection.

### Implementation Standard

Inside the command file (before the execution block), embed this three-branch router instruction:

```markdown
## Input Resolution
Determine the modality of the user's input before acting:
1. **Live System Pull:** If a URL or specific system ID is provided, fetch the artifact via the appropriate connector.
2. **Local Reference:** If a local file path is referenced, use file reading tools to ingest it.
3. **Conversational Description:** If neither is present, gracefully ask the user to share the artifact, upload a screenshot, or describe the problem in chat. Do not proceed until context is gathered.
```
