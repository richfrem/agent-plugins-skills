# MAF Hands-On Experiment Analysis

**Date:** 2026-05-31  
**Source:** `/Users/richardfremmerlid/Projects/MicrosoftAgentFramework/01_Basics`  
**MAF version tested:** `Microsoft.Agents.AI 1.6.1` (post-1.0 GA; assessment covered 1.0)  
**Provider used:** Gemini via OpenAI-compatible endpoint (`gemini-3.1-flash-lite-preview`)  
**Context:** 12 working C# examples built to validate the theoretical assessment before deciding what patterns to port back

---

## What Was Built

| # | File | Tested |
|---|------|--------|
| 1 | `HelloWorldExample.cs` | `AsAIAgent()`, `RunAsync`, `RunStreamingAsync`, token usage, multi-provider detection |
| 2 | `StructuredOutputExample.cs` | `RunAsync<T>()` typed classification against a schema mirroring `session-brief.md` fields |
| 3 | `MessageTypesExample.cs` | Text, image, URL, and low-level `FunctionCallContent` / `FunctionResultContent` primitives |
| 4 | `ChatRolesExample.cs` | Manual history injection to prime conversation context |
| 5 | `AgentSessionExample.cs` | Multi-turn session vs stateless — token cost difference confirmed empirically |
| 6 | `MemoryExample.cs` | `SerializeSessionAsync` / `DeserializeSessionAsync` round-trip |
| 7 | `ToolsExample.cs` | `AIFunctionFactory.Create()` with safe-path `ReadFile` / `WriteFile` / `ListFiles` / `AskUserQuestion` |
| 8 | `SimpleRagExample.cs` | `TextSearchProvider` keyword RAG over all plugin markdown — 3 snippets per query |
| 9 | `ObservabilityExample.cs` | OpenTelemetry via `.AsBuilder().UseOpenTelemetry()` |
| 10 | `WorkflowsExample.cs` | `Executor<TInput, TOutput>` typed pipeline, `InProcessExecution`, no AI required |
| 11 | `AgentSkillsExample.cs` | Custom `SkillMdContextProvider : AIContextProvider` — direct SKILL.md injection |
| 12 | `AgentManifestExample.cs` | Full harness over real `exploration-cycle-plugin`: manifest loader, skill isolation, handoff routing, write-file markers |

---

## Key Findings

### 1. Gemini Has a Compatibility Gap with AgentSkillsProvider

MAF's built-in `AgentSkillsProvider` uses a `load_skill` tool for progressive disclosure — the model requests specific skills by calling the tool, and the framework loads them on demand. This fails on Gemini's OpenAI-compatible endpoint with a `thought_signature` error.

**Workaround (confirmed working):** Custom `SkillMdContextProvider : AIContextProvider` that reads SKILL.md files from disk and injects them as system messages via `ProvideAIContextAsync` — no tool calls at all:

```csharp
protected override ValueTask<AIContext> ProvideAIContextAsync(
    InvokingContext context, CancellationToken ct)
{
    var messages = Directory
        .GetFiles(_skillsDirectory, "SKILL.md", SearchOption.AllDirectories)
        .Select(f => new ChatMessage(ChatRole.System, $"## Loaded Skill\n\n{File.ReadAllText(f)}"));
    return new ValueTask<AIContext>(new AIContext { Messages = [.. messages] });
}
```

Regular `AIFunctionFactory.Create()` function calling (Example 7) works fine with Gemini. The issue is specific to `AgentSkillsProvider`'s built-in `load_skill` tool mechanism.

**Implication for plugin architecture:** SKILL.md files work as a cross-provider open standard. The content format needs no changes. The injection mechanism differs by runtime (context provider injection in MAF vs system-prompt embedding in Claude Code CLI).

---

### 2. Two Skill Injection Patterns — Different Trade-offs

The experiments revealed two distinct approaches, each with different trade-offs:

| Approach | Used in | When called | Separation | Complexity |
|---|---|---|---|---|
| `AIContextProvider` injection | Example 11 | Before every model call | Skills separate from instructions | Requires provider wiring |
| Embedded in instructions | Example 12 | Once at agent construction | Skills baked into system prompt | Simpler; no wiring |

**Example 12's approach** — reading skills once and appending to the agent's instruction string — is more reliable for static SKILL.md files that don't change between calls, and avoids any provider compatibility concerns. Skills are scoped per-agent via the `dependencies:` frontmatter field; the loader truncates at 15,000 chars per skill to prevent context overload.

**Takeaway:** For plugin SKILL.md files that are read-only at runtime, the embedded-in-instructions approach is simpler and safer across providers.

---

### 3. SKILL.md Open Standard Confirmed Cross-Runtime

SKILL.md files (Anthropic open standard, Dec 2025) were tested loading into MAF via a custom `AIContextProvider`. They parse and inject correctly without any format changes. The same files installed in `exploration-cycle-plugin/skills/` work in:

- Claude Code CLI (native)
- GitHub Copilot CLI (native)
- Gemini CLI (native)
- MAF via `AIContextProvider` injection (confirmed hands-on)

This confirms the plugin architecture's portability claim. The `.md` file is the portable interface definition; the injection mechanism is runtime-specific.

---

### 4. Agent Manifests Load Cleanly Into MAF — One Frontmatter Difference

The `AgentManifestLoader` in Example 12 parses real `exploration-cycle-plugin` `*-agent.md` files. The production plugin uses:

```yaml
dependencies: ["skill:exploration-workflow", "agent:vibe-orchestrator"]
```

The toy agents in the MAF project use the older format:

```yaml
skills:
  - travel-advisor
```

The loader handles both. The `dependencies:` array format is what the real plugin uses; the `skills:` list is a toy-only holdover. **No format change needed in the plugin files.**

The `AgentManifestLoader` also builds a three-way alias index per agent (file stem, stem-without-`-agent` suffix, frontmatter `name:` field), so routing by any of these works. This is the same aliasing pattern Claude Code uses when resolving agent names.

---

### 5. Typed Routing vs Text Token Routing — Both Confirmed Working

Example 2 tested `RunAsync<IntakeClassification>()` — the model returns a typed C# object with a `RecommendedHandoffAgent` field. This is deterministic routing with schema enforcement.

Example 12 uses `[HANDOFF:agent-name]` text tokens — the model appends the token, the host parses it with regex and validates against a whitelist.

Both work. The trade-off:

| Approach | Determinism | Provider dependency | Schema error risk | Complexity |
|---|---|---|---|---|
| `RunAsync<T>()` typed | High — schema validated | High — requires structured output support | Low | Medium |
| `[HANDOFF:]` token | Medium — text parsing | Low — works with any model | Medium — model may omit or misplace token | Low |

The plugin architecture's `[HANDOFF:]` token approach is lower-friction across providers but requires the host to handle malformed output. The structured output approach is cleaner but tightly coupled to structured output support (Gemini: partial support; older models: unreliable).

**Recommendation confirmed:** Keep `[HANDOFF:]` tokens for CLI-layer agent routing where model support varies. Adopt `RunAsync<T>()` only in SDK-level C# harnesses where provider support is guaranteed.

---

### 6. AllowedHandoffs Whitelist Is the C# Equivalent of Dispatch Authorization

Example 12 implements a compile-time handoff whitelist:

```csharp
private static readonly Dictionary<string, string[]> AllowedHandoffs =
    new(StringComparer.OrdinalIgnoreCase)
    {
        ["intake-agent"] = ["vibe-orchestrator", "vibe-orchestrator-agent"],
    };
```

Any `[HANDOFF:]` token pointing to an unlisted target is rejected with `InvalidOperationException`. The model cannot route to an agent that isn't in this table, regardless of what it emits.

This is the C# equivalent of the v1.3 SQLite `approvals` table and `check_dispatch_authorization()` function. Both enforce that the orchestrator can only transition to pre-declared next states — a deterministic finite automaton over the routing graph.

**This pattern is the single most important security primitive** both in the MAF harness and in the Python dispatch layer. The implementation in C# confirms the v1.3 design is sound.

---

### 7. WorkspaceTools Path Traversal Prevention — Same Pattern as sandbox_runner.py

Example 12's `WorkspaceTools` and Example 7's `ToolsExample` both implement the same sandboxing pattern:

```csharp
var full = Path.GetFullPath(Path.Combine(root, relativePath));
if (!full.StartsWith(root, StringComparison.OrdinalIgnoreCase))
    return "[Rejected: path traversal detected]";
```

Reads allowed from plugin root OR workspace. Writes allowed to workspace only. This is byte-for-byte equivalent to the Python `sandbox_runner.py` pattern from the v1.3 spec:

```python
full = (base / relative).resolve()
if not str(full).startswith(str(allowed_root)):
    raise PermissionError("Path traversal rejected")
```

**The C# reference implementation confirms the Python design.** Both resolve the path before comparing — the correct approach. Naive string prefix checks without `resolve()` / `GetFullPath()` are bypassable with `../..` sequences.

---

### 8. Handoff Envelope — Context Continuity Pattern

When a handoff occurs, Example 12 builds an envelope carrying context to the receiving agent:

```csharp
var envelope = BuildHandoffEnvelope(prevManifest, handoffTarget, response, input, transcript);
```

The envelope includes: from-agent name, reason, last 8 turns (truncated at 300 chars each), and the user's latest message. The receiving agent is bootstrapped with this envelope as its first message so it doesn't start blind.

This matches the `exploration-cycle-plugin`'s handoff pattern exactly. The C# implementation confirms:
- 8 prior turns is a reasonable window (enough context, doesn't blow the budget)
- 300-char truncation per turn is sufficient for routing context
- The receiving agent must be explicitly told not to repeat the previous agent's intake questions

---

### 9. MAF 1.6.1 vs Assessment's 1.0 — Provider Capability Matrix Updated

The project uses `Microsoft.Agents.AI 1.6.1` (not 1.0 GA which the assessment covered). No API-breaking changes were observed between 1.0 and 1.6.1 — the core patterns (`AsAIAgent`, `RunAsync`, `CreateSessionAsync`, `AIContextProviders`) are stable.

No Azure or Foundry credentials were needed. **Gemini (free tier, no billing setup) ran all 12 examples.** The one exception is AgentSkillsProvider's `load_skill` tool — see Finding 1.

---

### 10. OpenTelemetry Wiring — One Line

```csharp
_mafAgent = chatClient.AsAIAgent()
    .AsBuilder()
    .UseOpenTelemetry(sourceName: "maf-example-9")
    .Build();
```

Every `RunAsync` call automatically produces traces: what was sent, what came back, how long it took. In production these route to Azure Monitor / Datadog / Jaeger. Console exporter used here for local visibility.

This is the same `pip install opentelemetry-sdk` integration listed in the assessment's "Adopted Instead" table. The C# wiring confirms how thin the integration is — one method call on the builder.

---

## What This Changes in the Prior Assessment

The theoretical assessment (see `microsoft-agent-framework-assessment.md`) holds up well. The hands-on findings refine three claims:

| Claim | Assessment Said | Experiment Found |
|---|---|---|
| Gemini compatibility | "Works via OpenAI-compatible endpoint" | True for function calling and core API; false for `AgentSkillsProvider`'s `load_skill` tool |
| SKILL.md in MAF | Theoretical — documented in assessment | Confirmed hands-on: files parse and inject correctly with custom provider |
| Agent manifest portability | Theoretical | Confirmed: real `exploration-cycle-plugin` agents load and run in MAF harness without changes |
| "No Azure needed" | Stated based on docs | Confirmed empirically — all 12 examples ran on Gemini free tier |

The assessment's core recommendation — do not adopt MAF, adopt specific primitives independently — is unchanged. These experiments validated which specific primitives work and how to implement them.

---

## Patterns Worth Porting to the Python Plugin Ecosystem

The following specific patterns from the experiments are directly applicable:

### P1. Direct Skill Injection (not tool-based loading)

The `SkillMdContextProvider` pattern — read SKILL.md files from disk, inject as context before model call — is more reliable than tool-based progressive disclosure across providers. The Python equivalent is the context-builder pattern in `os-improvement-loop` and `dispatch.py`: read the relevant SKILL.md, inject at the top of the prompt, not as a tool result.

### P2. Per-Agent Skill Scoping with Budget Cap

Each agent loads only its declared `dependencies: ["skill:X"]`, not all skills. Skills are truncated at a char budget. In Python/Claude Code CLI, this translates to: when building a dispatch prompt, include only the SKILL.md files declared in the target agent's manifest frontmatter, capped at a token budget. Prevents context overflow and role bleed between agents.

### P3. Three-Way Alias Index for Agent Resolution

Agent ID resolution: file stem → also index as stem-without-`-agent` suffix → also index by frontmatter `name:` field. This means `"vibe-orchestrator"`, `"vibe-orchestrator-agent"`, and the name field all resolve to the same file. The Python dispatch layer should build the same index when routing handoffs.

### P4. Handoff Envelope with Turn Windowing

When dispatching a subagent that receives a handoff, inject the last N turns (8 is the empirically tested value) truncated at ~300 chars/turn as the opening context block. Include from-agent name, reason, and user's latest message explicitly. Do not rely on the receiving agent to reconstruct context from scratch.

### P5. Workspace/Plugin Read-Write Split

Read-only access to plugin root (SKILL.md, agent manifests, references). Write access to workspace root only. Path traversal blocked by resolving to absolute path before comparing against root. This is already in v1.3 `sandbox_runner.py` — the C# experiment confirms the design is correct.

---

## Patterns Not Worth Porting

### Runtime C# workflow orchestration

`WorkflowBuilder` + `Executor<TIn, TOut>` is useful in typed .NET applications but unnecessary for SKILL.md-driven agent loops where the model handles step sequencing. The Python equivalent — `state_engine.py` + task leasing — is already doing the correct thing for this use case.

### AgentSkillsProvider progressive disclosure

The built-in tool-based skill loading has provider compatibility issues and adds roundtrip overhead. Direct injection (P1 above) is simpler and more reliable.

### Session serialization for CLI workflows

`SerializeSessionAsync` is valuable for web application / API contexts where sessions persist across HTTP requests. For CLI-driven agent loops, the conversation history is already managed by the Claude Code session itself. No additional serialization layer needed.

---

## Open Questions From Experiments

1. **Structured output reliability across providers:** `RunAsync<T>()` works in C# with schema enforcement. What's the failure rate in practice when the model is supposed to populate `RecommendedHandoffAgent`? Not tested at scale — worth a small eval run before adopting typed routing in any Python harness.

2. **Multi-agent session token cost:** Example 5 shows empirically that session history doubles input tokens per turn for a 3-turn conversation. At scale (12+ component workflows), the accumulation effect matches the assessment's "quadratic tax" concern. The v1.3 SQLite state plane addresses this by keeping only the relevant task context in each dispatch, not the full session history.

3. **Gemini `thought_signature` — fixed in a later Gemini version?** The compatibility gap may be resolved in a future Gemini API update. Worth retesting when Gemini Flash 2.x or 3.x stabilizes on the OpenAI-compatible endpoint.
