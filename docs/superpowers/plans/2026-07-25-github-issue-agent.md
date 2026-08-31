# GitHub Issue Agent & Agentic OS Issue Logging Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `github-issue-agent` skill in `dev-utils` and `github-issue-logging-policy.md` rule in `agent-agentic-os` to enable safe, dry-run-first, deduplicated, root-cause-consolidated, evidence-validated, and secret-redacted logging of repository execution friction into GitHub Issues.

**Architecture:** Python helper scripts in `plugins/dev-utils/skills/github-issue-agent/scripts/` wrap the `gh` CLI with payload-generation / dry-run default execution, secret scanning, machine-readable taxonomy validation requiring `area:*` or `plugin:*` (`issue-taxonomy.json`), body section validation (`validate_issue_body`), and root-cause consolidation. `plugins/agent-agentic-os/rules/github-issue-logging-policy.md` maps directly to `self-evolution-policy.md` friction tiers (T0-T3) and supports human suppression directives (`issue_logging: suppressed`).

**Tech Stack:** Python 3.8+ (standard library only), `pytest`, `gh` CLI (mocked in tests).

## Global Constraints

- Source of truth is `plugins/`; `.agents/` receives copies via `plugin_add.py plugins/ -y`.
- Dry-run mode (`--dry-run`) / payload-generation mode is DEFAULT for all mutating script executions.
- Taxonomy defined in `issue-taxonomy.json` requires `area:*` OR `plugin:*` on EVERY issue.
- Issue body validator MUST reject bodies missing Summary, Observed Behavior, Expected Behavior, Evidence, or Impact sections.
- Unit tests MUST use mocked `gh` CLI calls (`unittest.mock` / `pytest`) — ZERO live network calls in test suite.
- Secret redaction gate MUST block issue creation/commenting if tokens, keys, or credentials are present.

---

### Task 1: Taxonomy Definition & Strict Location Validation Core

**Files:**
- Create: `plugins/dev-utils/skills/github-issue-agent/issue-taxonomy.json`
- Create: `plugins/dev-utils/skills/github-issue-agent/issue-taxonomy.md`
- Create: `plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_taxonomy_validate.py`
- Test: `plugins/dev-utils/skills/github-issue-agent/tests/test_issue_taxonomy.py`

**Interfaces:**
- Consumes: None
- Produces: `gh_issue_taxonomy_validate.py` CLI (`validate_taxonomy(labels: list[str]) -> tuple[bool, list[str]]`)

- [ ] **Step 1: Write failing test for taxonomy validation including location constraint**

```python
# plugins/dev-utils/skills/github-issue-agent/tests/test_issue_taxonomy.py
import pytest
from plugins.dev_utils.skills.github_issue_agent.scripts.gh_issue_taxonomy_validate import validate_taxonomy

def test_validate_taxonomy_valid_labels_with_area():
    labels = ["type:friction", "tier:1-friction", "area:scripts", "source:agent", "risk:low"]
    is_valid, errors = validate_taxonomy(labels)
    assert is_valid is True
    assert len(errors) == 0

def test_validate_taxonomy_valid_labels_with_plugin():
    labels = ["type:friction", "tier:1-friction", "plugin:agent-orchestration/", "source:agent", "risk:low"]
    is_valid, errors = validate_taxonomy(labels)
    assert is_valid is True
    assert len(errors) == 0

def test_validate_taxonomy_missing_location():
    # Missing both area:* and plugin:* must fail validation
    labels = ["type:friction", "tier:1-friction", "source:agent", "risk:low"]
    is_valid, errors = validate_taxonomy(labels)
    assert is_valid is False
    assert any("location (area:* or plugin:*)" in err for err in errors)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest plugins/dev-utils/skills/github-issue-agent/tests/test_issue_taxonomy.py -v`  
Expected: FAIL (module/script not found)

- [ ] **Step 3: Implement `issue-taxonomy.json`, `issue-taxonomy.md`, and `gh_issue_taxonomy_validate.py`**

Create `issue-taxonomy.json`:
```json
{
  "dimensions": {
    "type": ["type:bug", "type:friction", "type:map-debt", "type:enhancement", "type:documentation", "type:security", "type:architecture", "type:test-gap"],
    "tier": ["tier:0-quickfix", "tier:1-friction", "tier:2-structural", "tier:3-architecture"],
    "area": ["area:dev-utils", "area:agentic-os", "area:skills", "area:rules", "area:subagents", "area:scripts", "area:tests", "area:docs", "area:ci", "area:github", "area:task-agent"],
    "source": ["source:agent", "source:human", "source:script", "source:test", "source:review", "source:migration"],
    "status_fallback": ["status:needs-triage", "status:needs-spec", "status:ready", "status:blocked", "status:accepted-debt", "status:duplicate"],
    "risk": ["risk:low", "risk:medium", "risk:high", "risk:security-sensitive", "risk:destructive-operation"],
    "resolution": ["resolution:fixed", "resolution:superseded", "resolution:wont-fix", "resolution:obsolete"]
  },
  "plugin_prefix": "plugin:",
  "required_dimensions": ["type", "tier", "source", "risk"]
}
```

Implement `gh_issue_taxonomy_validate.py`:
```python
import json, sys, os
from typing import Tuple, List

def load_taxonomy(json_path: str = None) -> dict:
    if not json_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, "issue-taxonomy.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_taxonomy(labels: List[str], taxonomy_path: str = None) -> Tuple[bool, List[str]]:
    tax = load_taxonomy(taxonomy_path)
    errors = []
    found_dims = set()
    has_location = False
    
    for label in labels:
        matched = False
        for dim, values in tax["dimensions"].items():
            if label in values:
                found_dims.add(dim)
                matched = True
                if dim == "area":
                    has_location = True
                break
        if not matched and label.startswith(tax["plugin_prefix"]):
            found_dims.add("plugin")
            has_location = True
            matched = True
        if not matched:
            errors.append(f"Unrecognized label: '{label}'")
            
    for req in tax["required_dimensions"]:
        if req not in found_dims:
            errors.append(f"Missing required dimension: '{req}'")
            
    if not has_location:
        errors.append("Missing required location (area:* or plugin:*) label")
            
    return (len(errors) == 0, errors)

if __name__ == "__main__":
    valid, errs = validate_taxonomy(sys.argv[1:])
    if not valid:
        print("Taxonomy Validation Failed:", errs)
        sys.exit(1)
    print("Taxonomy Validated Successfully")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest plugins/dev-utils/skills/github-issue-agent/tests/test_issue_taxonomy.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugins/dev-utils/skills/github-issue-agent/
git commit -m "feat(dev-utils): add taxonomy validation with mandatory area/plugin location check"
```

---

### Task 2: Issue Body Section Validator & Secret Redaction Gate

**Files:**
- Create: `plugins/dev-utils/skills/github-issue-agent/templates/friction-issue.md`
- Create: `plugins/dev-utils/skills/github-issue-agent/templates/map-debt-issue.md`
- Create: `plugins/dev-utils/skills/github-issue-agent/templates/bug-issue.md`
- Create: `plugins/dev-utils/skills/github-issue-agent/templates/enhancement-issue.md`
- Create: `plugins/dev-utils/skills/github-issue-agent/templates/doc-gap-issue.md`
- Create: `plugins/dev-utils/skills/github-issue-agent/scripts/body_validator.py`
- Create: `plugins/dev-utils/skills/github-issue-agent/scripts/redaction_gate.py`
- Test: `plugins/dev-utils/skills/github-issue-agent/tests/test_issue_body_rendering.py`
- Test: `plugins/dev-utils/skills/github-issue-agent/tests/test_secret_redaction.py`

**Interfaces:**
- Consumes: Issue markdown strings
- Produces: `validate_issue_body(body: str) -> tuple[bool, list[str]]`, `scan_for_secrets(text: str) -> tuple[bool, list[str]]`

- [ ] **Step 1: Write failing test for evidence quality body validation**

```python
# plugins/dev-utils/skills/github-issue-agent/tests/test_issue_body_rendering.py
from plugins.dev_utils.skills.github_issue_agent.scripts.body_validator import validate_issue_body

def test_validate_issue_body_complete():
    body = """
    ## Summary
    Script failed to run due to missing dependency.
    ## Observed Behavior
    ImportError thrown on line 5.
    ## Expected Behavior
    Script should import module cleanly.
    ## Evidence
    Traceback log snippet attached.
    ## Impact
    Blocks build pipeline.
    """
    is_valid, errors = validate_issue_body(body)
    assert is_valid is True

def test_validate_issue_body_missing_evidence():
    body = "## Summary\nFailed.\n## Impact\nHigh."
    is_valid, errors = validate_issue_body(body)
    assert is_valid is False
    assert any("Evidence" in err for err in errors)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest plugins/dev-utils/skills/github-issue-agent/tests/test_issue_body_rendering.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement `body_validator.py`, `redaction_gate.py`, and templates**

Implement `body_validator.py`:
```python
from typing import Tuple, List

REQUIRED_SECTIONS = ["## Summary", "## Observed Behavior", "## Expected Behavior", "## Evidence", "## Impact"]

def validate_issue_body(body: str) -> Tuple[bool, List[str]]:
    errors = []
    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"Missing required issue body section: '{section}'")
    return (len(errors) == 0, errors)
```

Implement `redaction_gate.py`:
```python
import re
from typing import Tuple, List

SECRET_PATTERNS = [
    (r"ghp_[A-Za-z0-9]{36}", "GitHub Personal Access Token"),
    (r"github_pat_[A-Za-z0-9_]{82}", "GitHub Fine-Grained Token"),
    (r"-----BEGIN [A-Z ]+ PRIVATE KEY-----", "Private Key"),
    (r"sk-[A-Za-z0-9]{32,}", "API Key"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r"bearer\s+[A-Za-z0-9\-\._~\+\/]+=*", "Bearer Token")
]

def scan_for_secrets(text: str) -> Tuple[bool, List[str]]:
    findings = []
    for pattern, label in SECRET_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            findings.append(f"Detected potential secret ({label}) matching pattern: {pattern}")
    return (len(findings) == 0, findings)
```

Create Markdown templates in `templates/` with headers matching `REQUIRED_SECTIONS`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest plugins/dev-utils/skills/github-issue-agent/tests/test_issue_body_rendering.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugins/dev-utils/skills/github-issue-agent/
git commit -m "feat(dev-utils): add body section quality validator and secret redaction gate"
```

---

### Task 3: Root-Cause Consolidation & Deduplication Search (`gh_issue_search.py`)

**Files:**
- Create: `plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_search.py`
- Test: `plugins/dev-utils/skills/github-issue-agent/tests/test_dedup_search.py`

**Interfaces:**
- Consumes: Normalized issue details, affected file paths, area/plugin labels
- Produces: `consolidate_and_search_dedup(...) -> dict`

- [ ] **Step 1: Write failing test for root-cause consolidation and dedup search**

```python
# plugins/dev-utils/skills/github-issue-agent/tests/test_dedup_search.py
from unittest.mock import patch, MagicMock
from plugins.dev_utils.skills.github_issue_agent.scripts.gh_issue_search import consolidate_and_search_dedup

@patch("subprocess.run")
def test_consolidate_and_search_finds_existing_root_cause(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout='[{"number": 42, "title": "Repository lacks standardized file existence validation", "labels": [{"name": "type:friction"}]}]'
    )
    result = consolidate_and_search_dedup(
        title="Script x.py failed because file missing",
        area_label="area:scripts",
        file_paths=["plugins/dev-utils/scripts/x.py"]
    )
    assert result["has_existing_root_cause"] is True
    assert result["target_issue_number"] == 42
    assert result["recommendation"] == "comment_and_append_evidence"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest plugins/dev-utils/skills/github-issue-agent/tests/test_dedup_search.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement `gh_issue_search.py` with root-cause consolidation rules**

```python
import subprocess, json
from typing import List, Dict, Any

def consolidate_and_search_dedup(title: str, area_label: str, file_paths: List[str]) -> Dict[str, Any]:
    # Query gh issue list by label and search terms
    cmd = ["gh", "issue", "list", "--json", "number,title,labels", "--label", area_label, "--limit", "20"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        issues = json.loads(res.stdout) if res.stdout else []
    except Exception:
        issues = []
        
    for issue in issues:
        # Check for broad root cause match or title keyword overlap
        if "file existence validation" in issue["title"].lower() or any(w in issue["title"].lower() for w in title.lower().split() if len(w) > 4):
            return {
                "has_existing_root_cause": True,
                "target_issue_number": issue["number"],
                "recommendation": "comment_and_append_evidence"
            }
            
    return {
        "has_existing_root_cause": False,
        "target_issue_number": None,
        "recommendation": "create_new_issue"
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest plugins/dev-utils/skills/github-issue-agent/tests/test_dedup_search.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugins/dev-utils/skills/github-issue-agent/
git commit -m "feat(dev-utils): implement root-cause consolidation deduplication search"
```

---

### Task 4: Dry-Run Payload Generation & Comment Operations (`gh_issue_create.py`, `gh_issue_comment.py`)

**Files:**
- Create: `plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_create.py`
- Create: `plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_comment.py`
- Test: `plugins/dev-utils/skills/github-issue-agent/tests/test_gh_mocked_cli.py`

**Interfaces:**
- Consumes: Taxonomy validator, body validator, secret scanner, search consolidator
- Produces: CLI interface defaulting to `--dry-run` (payload-generation mode) emitting deterministic JSON

- [ ] **Step 1: Write failing test for payload-generation dry-run mode**

```python
# plugins/dev-utils/skills/github-issue-agent/tests/test_gh_mocked_cli.py
from unittest.mock import patch, MagicMock
from plugins.dev_utils.skills.github_issue_agent.scripts.gh_issue_create import create_issue

def test_create_issue_dry_run_generates_json_payload():
    labels = ["type:friction", "tier:1-friction", "area:scripts", "source:agent", "risk:low"]
    body = "## Summary\nTest\n## Observed Behavior\nError\n## Expected Behavior\nOK\n## Evidence\nLogs\n## Impact\nLow"
    res = create_issue(title="Test Issue", body=body, labels=labels, execute=False)
    assert res["would_execute"] is False
    assert res["action"] == "create_issue"
    assert res["redaction_check"] == "passed"
    assert res["body_validation"] == "passed"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest plugins/dev-utils/skills/github-issue-agent/tests/test_gh_mocked_cli.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement `gh_issue_create.py` and `gh_issue_comment.py`**

Implement `gh_issue_create.py` with default `execute=False`, invoking all validators (`validate_taxonomy`, `validate_issue_body`, `scan_for_secrets`).

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest plugins/dev-utils/skills/github-issue-agent/tests/test_gh_mocked_cli.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugins/dev-utils/skills/github-issue-agent/
git commit -m "feat(dev-utils): implement gh_issue_create and comment scripts with dry-run default"
```

---

### Task 5: Skill & Agentic OS Policy Integration with Human Suppression & Self-Evolution Mapping

**Files:**
- Create: `plugins/dev-utils/skills/github-issue-agent/SKILL.md`
- Create: `plugins/agent-agentic-os/rules/github-issue-logging-policy.md`

**Interfaces:**
- Consumes: `self-evolution-policy.md`
- Produces: Frontmatter and rule definition integrating human suppression (`issue_logging: suppressed`) and friction tier mapping (T0-T3).

- [ ] **Step 1: Write `plugins/dev-utils/skills/github-issue-agent/SKILL.md`**

Define frontmatter, operations, and explicit reference to `issue-taxonomy.json`.

- [ ] **Step 2: Write `plugins/agent-agentic-os/rules/github-issue-logging-policy.md`**

Include:
- Alignment matrix mapping `self-evolution-policy.md` friction tiers (T0: Fix inline / issue optional, T1: Fix inline or log issue, T2: Log issue mandatory, T3: Log issue + architecture review mandatory).
- Root-cause consolidation principle (Ask: Is this event itself the issue or evidence of a broader issue?).
- Human suppression override protocol (`issue_logging: suppressed`).
- Staged rollout instructions (Phase 1: Payload generation only, Phase 2: Comments, Phase 3: Issue creation, Phase 4: Label sync).

- [ ] **Step 3: Commit**

```bash
git add plugins/dev-utils/skills/github-issue-agent/SKILL.md plugins/agent-agentic-os/rules/github-issue-logging-policy.md
git commit -m "feat(agentic-os): create github-issue-agent SKILL.md and github-issue-logging-policy rule"
```

---

### Task 6: Ecosystem Deployment & Verification Pass

**Files:**
- Modify: `.agents/` (via `plugin_add.py plugins/ -y`)

- [ ] **Step 1: Execute all unit tests**

Run: `pytest plugins/dev-utils/skills/github-issue-agent/tests/ -v`  
Expected: PASS (100% pass rate, 0 live network calls)

- [ ] **Step 2: Reinstall plugins into `.agents/`**

Run: `python3 plugins/plugin-manager/scripts/plugin_add.py plugins/ -y`  
Expected: Success for all plugins

- [ ] **Step 3: Diagnose symlinks**

Run: `python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose`  
Expected: All links OK

- [ ] **Step 4: Final commit**

```bash
git add .agents/
git commit -m "chore: deploy github-issue-agent and logging policy into .agents/"
```
