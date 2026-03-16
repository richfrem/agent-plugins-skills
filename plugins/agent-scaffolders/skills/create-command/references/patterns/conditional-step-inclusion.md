# Conditional Step Inclusion

**Use Case:** Multi-step workflows that can be optionally "supercharged" with extra tool integrations, but must run successfully even if those tools are missing.

## The Core Mechanic

Rather than embedding messy `if/else` logic deep inside workflow steps, evaluate tool availability at the **Step Header** level. If the required tool is not present, the entire step is gracefully cleanly skipped.

### Implementation Standard

Format the workflow steps in the command file like this:

```markdown
### Step 1: Extract Core Competencies
[Always run this step using the provided document.]

### Step 2: Corroborate via Cloud Storage (If Connected)
If **~~cloud storage** is connected via MCP:
- Search for past performance reviews and append context.
If **~~cloud storage** is NOT connected, skip this step entirely and proceed to Step 3.

### Step 3: Synthesis
[Always run this step.]
```

This makes the workflow highly readable to developers and completely deterministic for the agent to execute.
