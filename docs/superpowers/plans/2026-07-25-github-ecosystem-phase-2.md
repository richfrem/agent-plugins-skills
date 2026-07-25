# GitHub Ecosystem Phase 2 (Repository Operational Memory) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Phase 2 of the GitHub Ecosystem: Issue Lifecycle Ownership (`gh_issue_close.py`), `issue-resolution-reviewer` sub-agent, `friction-cluster-agent` (hotspot analysis), GitHub Projects v2 custom field integration, and multi-stage rollout configuration.

**Architecture:** Python scripts in `plugins/dev-utils/skills/github-issue-agent/scripts/` handle issue closure with `resolution:*` labels (`fixed`, `superseded`, `wont-fix`, `obsolete`, `accepted-debt`) and candidate merging. Sub-agents under `plugins/agent-agentic-os/agents/` run periodic closed-issue verification (`issue-resolution-reviewer`) and friction hotspot clustering (`friction-cluster-agent`), feeding learnings directly into `os-improvement-loop` and `self-evolution-policy.md`.

**Tech Stack:** Python 3.8+ (standard library only), `pytest`, `gh` CLI (mocked in unit tests), `json`.

## Global Constraints

- Source of truth is `plugins/`; `.agents/` receives copies via `python3 plugins/plugin-manager/scripts/plugin_add.py plugins/ -y`.
- Dry-run mode (`--dry-run`) remains default for all mutating CLI operations.
- All unit tests MUST use mocked `gh` CLI calls (`unittest.mock` / `pytest`) — ZERO live network calls in unit test suite.
- Maintain single-responsibility design across skills/agents to avoid topology fragmentation.

---

### Task 1: Issue Lifecycle Closure & Resolution Operations (`gh_issue_close.py`)

**Files:**
- Create: `plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_close.py`
- Modify: `plugins/dev-utils/skills/github-issue-agent/issue-taxonomy.json`
- Modify: `plugins/dev-utils/skills/github-issue-agent/issue-taxonomy.md`
- Test: `plugins/dev-utils/skills/github-issue-agent/tests/test_gh_issue_close.py`

**Interfaces:**
- Consumes: Taxonomy validator, secret redaction scanner
- Produces: `close_issue(issue_number: int, resolution: str, comment: str, execute: bool = False) -> dict`

- [ ] **Step 1: Write failing unit test for issue closure with resolution label**

```python
# plugins/dev-utils/skills/github-issue-agent/tests/test_gh_issue_close.py
from unittest.mock import patch, MagicMock
from plugins.dev_utils.skills.github_issue_agent.scripts.gh_issue_close import close_issue

@patch("subprocess.run")
def test_close_issue_dry_run(mock_run):
    res = close_issue(issue_number=42, resolution="resolution:fixed", comment="Fixed in PR #453", execute=False)
    assert res["would_execute"] is False
    assert res["action"] == "close_issue"
    assert res["issue_number"] == 42
    assert res["resolution"] == "resolution:fixed"
    mock_run.assert_not_called()

@patch("subprocess.run")
def test_close_issue_invalid_resolution_fails(mock_run):
    res = close_issue(issue_number=42, resolution="resolution:invalid_res", comment="Fixed", execute=False)
    assert res["success"] is False
    assert any("Invalid resolution" in err for err in res["errors"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest plugins/dev-utils/skills/github-issue-agent/tests/test_gh_issue_close.py -v`  
Expected: FAIL (module not found)

- [ ] **Step 3: Implement `gh_issue_close.py`**

```python
#!/usr/bin/env python3
"""
GitHub Issue Closure Script
=====================================
Purpose:
    Closes GitHub issues with mandatory resolution labels and structured explanation comments.

Layer: Codify
Key Input Dependencies:
    - issue-taxonomy.json
    - redaction_gate.py
    - gh_issue_taxonomy_validate.py
"""

import sys, os, subprocess, json
from typing import Dict, Any
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from redaction_gate import scan_for_secrets
from gh_issue_taxonomy_validate import load_taxonomy

VALID_RESOLUTIONS = ["resolution:fixed", "resolution:superseded", "resolution:wont-fix", "resolution:obsolete", "resolution:accepted-debt"]

def close_issue(issue_number: int, resolution: str, comment: str, execute: bool = False) -> Dict[str, Any]:
    if resolution not in VALID_RESOLUTIONS:
        return {"success": False, "errors": [f"Invalid resolution '{resolution}'. Must be one of {VALID_RESOLUTIONS}"]}
        
    is_clean, findings = scan_for_secrets(comment)
    if not is_clean:
        return {"success": False, "errors": findings}
        
    payload = {
        "action": "close_issue",
        "issue_number": issue_number,
        "resolution": resolution,
        "comment": comment,
        "would_execute": execute
    }
    
    if not execute:
        payload["success"] = True
        return payload
        
    # Execute live gh CLI calls
    try:
        # Add comment and resolution label
        subprocess.run(["gh", "issue", "comment", str(issue_number), "--body", comment], check=True)
        subprocess.run(["gh", "issue", "edit", str(issue_number), "--add-label", resolution], check=True)
        subprocess.run(["gh", "issue", "close", str(issue_number)], check=True)
        payload["success"] = True
    except Exception as e:
        payload["success"] = False
        payload["errors"] = [str(e)]
        
    return payload
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest plugins/dev-utils/skills/github-issue-agent/tests/test_gh_issue_close.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugins/dev-utils/skills/github-issue-agent/
git commit -m "feat(dev-utils): implement gh_issue_close.py with resolution label validation and unit tests"
```

---

### Task 2: Friction Hotspot Clustering Engine (`friction_cluster_agent.py`)

**Files:**
- Create: `plugins/dev-utils/skills/github-issue-agent/scripts/friction_cluster_agent.py`
- Test: `plugins/dev-utils/skills/github-issue-agent/tests/test_friction_cluster.py`

**Interfaces:**
- Consumes: JSON array of GitHub issue objects
- Produces: `cluster_friction_issues(issues: list[dict]) -> dict` (identifying top friction areas, recurring failure classes, and recommended Agentic OS rule/skill updates)

- [ ] **Step 1: Write failing unit test for friction clustering**

```python
# plugins/dev-utils/skills/github-issue-agent/tests/test_friction_cluster.py
from plugins.dev_utils.skills.github_issue_agent.scripts.friction_cluster_agent import cluster_friction_issues

def test_cluster_friction_issues():
    issues = [
        {"number": 1, "title": "Script x.py failed on missing dependency", "labels": [{"name": "area:scripts"}, {"name": "type:friction"}]},
        {"number": 2, "title": "Script y.py failed on missing dependency", "labels": [{"name": "area:scripts"}, {"name": "type:friction"}]},
        {"number": 3, "title": "Doc link broken in README", "labels": [{"name": "area:docs"}, {"name": "type:documentation"}]}
    ]
    report = cluster_friction_issues(issues)
    assert report["total_issues"] == 3
    assert "area:scripts" in report["top_areas"]
    assert report["top_areas"]["area:scripts"] == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest plugins/dev-utils/skills/github-issue-agent/tests/test_friction_cluster.py -v`  
Expected: FAIL (module not found)

- [ ] **Step 3: Implement `friction_cluster_agent.py`**

```python
#!/usr/bin/env python3
"""
Friction Hotspot Clustering Engine
=====================================
Purpose:
    Parses open and closed GitHub friction issues to aggregate hotspots, recurring failure classes, and map debt.

Layer: Retrieve / Curate
"""

from typing import List, Dict, Any
from collections import Counter

def cluster_friction_issues(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    area_counts = Counter()
    type_counts = Counter()
    
    for issue in issues:
        labels = [l["name"] for l in issue.get("labels", []) if isinstance(l, dict) and "name" in l]
        for label in labels:
            if label.startswith("area:") or label.startswith("plugin:"):
                area_counts[label] += 1
            elif label.startswith("type:"):
                type_counts[label] += 1
                
    return {
        "total_issues": len(issues),
        "top_areas": dict(area_counts.most_common(5)),
        "top_types": dict(type_counts.most_common(5)),
        "recommendations": [
            f"Review {area} ({count} friction events)" for area, count in area_counts.items() if count >= 2
        ]
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest plugins/dev-utils/skills/github-issue-agent/tests/test_friction_cluster.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugins/dev-utils/skills/github-issue-agent/
git commit -m "feat(dev-utils): implement friction hotspot clustering engine with unit tests"
```

---

### Task 3: Issue Resolution Reviewer Agent Definition

**Files:**
- Create: `plugins/agent-agentic-os/agents/issue-resolution-reviewer.agent.md`

**Interfaces:**
- Consumes: Closed issues, `gh_issue_close.py` resolution metadata
- Produces: Periodic audit logs assessing whether closed issue fixes eliminated friction or caused regressions.

- [ ] **Step 1: Implement `issue-resolution-reviewer.agent.md`**

```markdown
---
name: issue-resolution-reviewer
description: >
  Audits closed GitHub issues to verify whether root causes were genuinely resolved,
  if follow-on execution friction appeared, or if systemic improvements were retained.
---

# Identity: Issue Resolution Reviewer

You perform post-closure quality audits on resolved repository issues.

## Primary Responsibilities
1. Inspect closed GitHub issues with `resolution:fixed` or `resolution:superseded` labels.
2. Check recent test runs, execution logs, and script friction events to confirm zero regression.
3. If friction recurs, reopen the issue or create a parent root-cause consolidation issue.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/agent-agentic-os/agents/issue-resolution-reviewer.agent.md
git commit -m "feat(agentic-os): add issue-resolution-reviewer agent definition"
```

---

### Task 4: Integration Test Suite & Ecosystem Reinstall Pass

**Files:**
- Modify: `.agents/` (via `python3 plugins/plugin-manager/scripts/plugin_add.py plugins/ -y`)

- [ ] **Step 1: Run full unit test suite**

Run: `python3 -m pytest plugins/dev-utils/skills/github-issue-agent/tests/ -v`  
Expected: PASS (100% pass rate across all Phase 1 + Phase 2 tests)

- [ ] **Step 2: Reinstall plugins into `.agents/`**

Run: `python3 plugins/plugin-manager/scripts/plugin_add.py plugins/ -y`  
Expected: Success for all plugins

- [ ] **Step 3: Symlink diagnosis pass**

Run: `python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose`  
Expected: All links OK
