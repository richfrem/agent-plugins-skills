# Priority Matrix & Projects v2 Guide

## Priority Ranking Rules
Priority is determined from three signals:
1. **Friction Tier (`tier:0` .. `tier:3`)**: Systemic failures (Tier 3) immediately yield **P0**.
2. **Blockage (`blocking`, `type:blocker`)**: Active work blockages increase priority level.
3. **Occurrence Frequency**: Repeated friction events escalate priority.

### Priority Matrix
- **P0 (Critical / Systemic)**: Tier 3 friction OR (Blocking AND frequency >= 3)
- **P1 (High Priority)**: Tier 2 friction OR Blocking OR frequency >= 4
- **P2 (Medium Priority)**: Tier 1 friction OR frequency >= 2
- **P3 (Low Priority)**: Default / backlog items

---

## Python API Interface

```python
from plugins.dev_utils.skills.github_issue_prioritizer.scripts.gh_issue_prioritize import (
    prioritize_issue,
    generate_projects_v2_payload
)

# Calculate issue priority
issue = {
    "number": 42,
    "title": "Build runner sandbox crash",
    "labels": [{"name": "tier:3"}, {"name": "blocking"}],
    "occurrence_count": 5
}
result = prioritize_issue(issue)
# result["priority"] -> "P0"
# result["priority_label"] -> "priority:P0"

# Generate GitHub Projects v2 GraphQL mutation payload
payload = generate_projects_v2_payload(
    project_id="PVT_kwDOA12345",
    item_id="PVTI_lADOA12345",
    field_id="PVTF_priority123",
    single_select_option_id="opt_p0_123"
)
```
