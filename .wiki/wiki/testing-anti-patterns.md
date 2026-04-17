---
concept: testing-anti-patterns
source: plugin-code
source_file: agent-execution-disciplines/references/testing-anti-patterns.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.187677+00:00
cluster: test
content_hash: ef4b09f1eaef88fb
---

# Testing Anti-Patterns

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Testing Anti-Patterns

**Load this reference when:** writing or changing tests, adding mocks, or tempted to add test-only methods to production code.

## Overview

Tests must verify real behavior, not mock behavior. Mocks are a means to isolate, not the thing being tested.

**Core principle:** Test what the code does, not what the mocks do.

**Following strict TDD prevents these anti-patterns.**

## The Iron Laws

```
1. NEVER test mock behavior
2. NEVER add test-only methods to production classes
3. NEVER mock without understanding dependencies
```

## Anti-Pattern 1: Testing Mock Behavior

**The violation:**
```typescript
// NO: Testing that the mock exists
test('renders sidebar', () => {
  render(<Page />);
  expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
});
```

**Why this is wrong:**
- You're verifying the mock works, not that the component works
- Test passes when mock is present, fails when it's not
- Tells you nothing about real behavior

**The fix:**
```typescript
// YES: Test real component or don't mock it
test('renders sidebar', () => {
  render(<Page />);  // Don't mock sidebar
  expect(screen.getByRole('navigation')).toBeInTheDocument();
});
```

### Gate Function

```
BEFORE asserting on any mock element:
  Ask: "Am I testing real component behavior or just mock existence?"

  IF testing mock existence:
    STOP - Delete the assertion or unmock the component

  Test real behavior instead
```

## Anti-Pattern 2: Test-Only Methods in Production

**The violation:**
```typescript
// NO: destroy() only used in tests
class Session {
  async destroy() {  // Looks like production API!
    await this._workspaceManager?.destroyWorkspace(this.id);
  }
}
```

**Why this is wrong:**
- Production class polluted with test-only code
- Dangerous if accidentally called in production
- Violates YAGNI and separation of concerns

**The fix:**
```typescript
// YES: Test utilities handle test cleanup
// Session has no destroy() - it's stateless in production

// In test-utils/
export async function cleanupSession(session: Session) {
  const workspace = session.getWorkspaceInfo();
  if (workspace) {
    await workspaceManager.destroyWorkspace(workspace.id);
  }
}
```

### Gate Function

```
BEFORE adding any method to production class:
  Ask: "Is this only used by tests?"

  IF yes:
    STOP - Don't add it
    Put it in test utilities instead
```

## Anti-Pattern 3: Mocking Without Understanding

**The violation:**
```typescript
// NO: Mock breaks test logic
test('detects duplicate server', () => {
  // Mock prevents config write that test depends on!
  vi.mock('ToolCatalog', () => ({
    discoverAndCacheTools: vi.fn().mockResolvedValue(undefined)
  }));
  await addServer(config);
  await addServer(config);  // Should throw - but won't!
});
```

**The fix:**
```typescript
// YES: Mock at correct level
test('detects duplicate server', () => {
  vi.mock('MCPServerManager'); // Just mock slow server startup
  await addServer(config);  // Config written
  await addServer(config);  // Duplicate detected correctly
});
```

### Gate Function

```
BEFORE mocking any method:
  STOP - Don't mock yet

  1. Ask: "What side effects does the real method have?"
  2. Ask: "Does this test depend on any of those side effects?"
  3. Ask: "Do I fully understand what this test needs?"

  IF depends on side effects:
    Mock at lower level (the actual slow/external operation)
    NOT the high-level method the test depends on
```

## Anti-Pattern 4: Incomplete Mocks

**The violation:**
```typescript
// NO: Partial mock - only fields you think you need
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' }
  // Missing: metadata that downstream code uses
};
// Later: breaks when code accesses response.metadata.requestId
```

**The Iron Rule:** Mock the COMPLETE data structure as it exists in reality.

**The fix:**
```typescript
// YES: Mirror real API completeness
const mockResponse = {
  status: 'success',
  

*(content truncated)*

## See Also

- [[context-folder-patterns]]
- [[optimizer-engine-patterns-reference-design]]
- [[optimizer-engine-patterns-reference-design]]
- [[context-folder-patterns]]
- [[context-folder-patterns]]
- [[optimizer-engine-patterns]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-execution-disciplines/references/testing-anti-patterns.md`
- **Indexed:** 2026-04-17T06:42:09.187677+00:00
