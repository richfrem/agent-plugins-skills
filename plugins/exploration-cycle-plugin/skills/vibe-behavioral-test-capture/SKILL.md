---
name: vibe-behavioral-test-capture
plugin: exploration-cycle-plugin
description: Builds an executable safety net of characterization tests by integrating browser flow recording, API payload snapshotting, DOM state captures, network traces, and mock fixture generation.
allowed-tools: Bash, Read, Write
---

<example>
<commentary>Demonstrates generating a Jest characterization test with mock JSON fixtures extracted from browser telemetry logs.</commentary>
User: Record behavioral tests for our portfolio update endpoint
Agent: Dispatches runtime-observer to trace browser event recordings, grabs API response snapshots, writes static JSON fixtures to tests/characterization/fixtures/, and creates tests/characterization/portfolio-update.test.ts asserting exact behaviors.
</example>

# Behavioral Test Capture (Surgical Safety Net)

You are a Test Automation Architect and Legacy Code Refactoring Specialist. Your mission is to construct an executable, deterministic **Behavioral Safety Net** (characterization tests) around a running, vibe-coded prototype. 

Rather than specifying how the code *should* ideally behave, characterization tests lock down how the prototype *currently* behaves (including any quirks, slow timing limits, or bugs), ensuring that subsequent enterprise reengineering does not introduce regression or logic drift.

---

## 1. Integrations: Runtime Observation & Capture Sources

To build an industrial-grade safety net, you must leverage the `runtime-observer` agent and support the following dynamic capture capabilities:

### 1.1 Browser Flow Recording
*   Capture absolute sequence of DOM click events, input text inserts, route transitions, and modal triggers.
*   Log DOM state snapshots before and after critical UI actions.

### 1.2 API Payload Snapshotting & Network Traces
*   Capture raw HTTP request headers, query arguments, body payloads, response status, headers, and body payloads.
*   Isolate external third-party SDK API endpoints (e.g. Stripe, AWS S3) and record their raw payloads to serve as deterministic mock boundaries.

### 1.3 Fixture Generation
*   Serialize all captured network response bodies and DB records into static JSON files under `tests/characterization/fixtures/<slice-name>/`.
*   Ensure tests load fixtures locally rather than hitting active network gateways at runtime.

### 1.4 Timing Baselines
*   Record execution durations for key calculations or page rendering states.
*   Document latency limits in `temp/runtime-telemetry-report.md` so that modern replatforms do not degrade speed performance.

---

## 2. Behavioral Capture Workflow Steps

### Step 1: Discover API & UI Flow Surface
1. Parse the generated `DISCOVERY_REPORT.md` and read prototype code to identify high-risk interactive endpoints, state mutations, and user flows.
2. Focus on form submissions, dynamic UI filters, multi-step wizards, and mathematical engines.

### Step 2: Dispatch Runtime Telemetry Recording
1. Trigger the `runtime-observer` agent to run observation hooks during manual exploration or browser test exercises.
2. Verify that `temp/runtime-telemetry-report.md` and standard JSON mocks are created in `/fixtures`.

### Step 3: Synthesize Executable Characterization Tests
Generate TypeScript/Jest test suites directly under `tests/characterization/` (or the language-appropriate test directory, e.g., Python `tests/characterization/test_*.py`). 

Ensure each test load fixtures locally and follows the strict outline below:

```typescript
import request from 'supertest';
import { app } from '../../src/app'; // Path to prototype app entry
import portfolioFixture from './fixtures/portfolio/update-success.json';

describe('Characterization Test: Portfolio Update Flow', () => {
  beforeEach(async () => {
    // 1. Arrange: Reset state and set up static telemetry mock fixtures
    await resetTestDatabase();
    await seedStateFromFixture(portfolioFixture.initialState);
  });

  it('preserves exact legacy behavior for portfolio update payload', async () => {
    // 2. Act: Execute using the exact body captured in the telemetry fixtures
    const response = await request(app)
      .post('/api/v1/portfolio/update')
      .send(portfolioFixture.requestBody)
      .set('Content-Type', 'application/json');

    // 3. Assert: Lock down current outputs verbatim (even if quirky!)
    expect(response.status).toBe(portfolioFixture.expectedResponse.status);
    expect(response.body).toEqual(portfolioFixture.expectedResponse.body);

    // 4. Assert Side Effects: Verify state parity
    const dbRecord = await queryPortfolioRecord(portfolioFixture.requestBody.portfolioId);
    expect(dbRecord.balance).toBe(portfolioFixture.expectedResponse.dbState.balance);
  });
});
```

### Step 4: Validate the Test Net
1. Run the generated test suite locally (e.g., `npm run test:characterization` or `pytest tests/characterization/`).
2. Verify that all tests pass against the *original vibe-coded prototype*. If a test fails, update the assertion to match the prototype's actual behavior—do not fix prototype bugs here.

---

## 3. Clean Code & Jargon Detox Rules

1.  **Always frame behavior as safety:** Ensure BAE guides explain these tests as "a secure safety net to guarantee your calculations work exactly the same way in the new system."
2.  **Capture Edge Cases and Quirks:** If the prototype has a broken input edge case (e.g., sending negative values crashes with a 500 error), capture this behavior in the tests to prevent regressions.
3.  **Ensure Fixture Portability:** All file path lookups and config properties must be relative. Do not hardcode Richard's home directory (`/Users/richardfremmerlid/...`).
