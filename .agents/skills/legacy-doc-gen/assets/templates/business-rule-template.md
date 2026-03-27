# BR-NNNN: [Rule Title]

## Metadata
*   **ID:** BR-NNNN
*   **Status:** [Active | Deprecated | Needs Review]
*   **Category:** [Validation | Calculation | Access Control | Workflow]
*   **Complexity:** [Low | Medium | High]

## Description
[Clear, plain English description of the rule. What is the business intent?]

## logic (Pseudocode)
```text
IF [Condition]
THEN [Action/Constraint]
ELSE [Alternative]
```

## Related Factors
*   **Roles:** [Roles that this rule applies to, e.g. JRS_CROWN_INQUIRY]
*   **Parameters:** [Form parameters that toggle this rule, e.g. P_ALLOW_AGENCY_SEARCH_YN]
*   **Events/Triggers:** [What triggers this rule? e.g. court_class='Y']
*   **Related Rules:** [Links to other BR-NNNN files, e.g. [[BR-0002]]]

## Business Scenarios

### Scenario 1: [Description]
*   **Condition:** [Context]
*   **Outcome:** [Result]

### Scenario 2: [Description]
*   **Condition:** [Context]
*   **Outcome:** [Result]

## Technical Implementation

### Source Locations
[List all known implementations of this rule in the legacy system]

| Component ID | File | Block/Trigger | Notes |
| :--- | :--- | :--- | :--- |
| **JCSE0030** | `jcse0030_fmb.xml` | `POST-QUERY` | Implements access level check |
| **JUSLIB** | `juslib.pll` | `check_access` | Shared function |

### Code Snippet (Example)
```plsql
-- Relevant extracted logic
IF :GLOBAL.USER_ACCESS < 2 THEN
  Raise_Application_Error(...);
END IF;
```

### Data Flow
*   **Inputs:** [What data influences this rule?]
*   **Outputs:** [What results from this rule being applied]
*   **Persistence:** [Where/how the results are stored]

## Modernization Strategy
*   **Target Layer:** [Backend API | Database | Frontend | Workflow Engine]
*   **Recommendation:** [How should this be implemented in the new system?]
*   **Related Business Processes:** [Processes affected by this rule]

## Stakeholder Questions
- [ ] Question 1?
