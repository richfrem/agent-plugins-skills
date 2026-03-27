# Acceptance Criteria

This document defines the formal testing schema and acceptance thresholds for this agent skill, as required by the Agent Skills Open Standard.

## Test Scenarios

### Scenario 1: Standard Execution
- **Trigger**: [Agent receives the standard invocation request]
- **Expected Behavior**: The agent should successfully parse inputs and invoke the designated tools/scripts.
- **Success Metric**: Valid output is generated without standard error or unhandled exceptions.

### Scenario 2: Error Handling
- **Trigger**: [User provides invalid context or missing parameters]
- **Expected Behavior**: Agent detects the missing information via progressive disclosure and prompts the user.
- **Success Metric**: Graceful failure without hallucinating parameters.
