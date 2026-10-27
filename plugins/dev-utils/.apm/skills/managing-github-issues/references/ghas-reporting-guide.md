# Guide: Producing a GHAS Report

Reusable lessons from the Crow and Raven reviews (2026-10-27), adapted from
`GHAS-REPORTING-GUIDE.md` in `richfrem/crow-raven-analysis`. This reference is
self-contained: the source repository and its local reports are not required.

Use for requests to report on GitHub Advanced Security (GHAS), CodeQL alerts,
Dependabot alerts, secret scanning, or repository security posture. Reporting is
read-only against GitHub; write the requested local report without changing
settings, dismissing alerts, uploading SARIF, or filing issues. Publishing
validated findings is a separately authorized `log` operation.

## Contents

- [Establish access](#establish-access)
- [Collect alert data and history](#collect-alert-data-and-history)
- [Review repository configuration](#review-repository-configuration)
- [Map scanner coverage](#map-scanner-coverage)
- [Ground claims in code](#ground-claims-in-code)
- [Report structure](#report-structure)
- [Prompt template](#prompt-template)
- [Pitfalls and worked lessons](#pitfalls-and-worked-lessons)
- [Official references](#official-references)

## Establish access

An agent can report only what its authenticated identity can read. Record the
repository, report time, token visibility, and endpoint outcomes first. Discover
available GitHub connector tools before using the CLI; capability names vary by
installation. Prefer a connector when it supports the required read operations.

CLI fallback, run for the selected repository:

```bash
for endpoint in code-scanning/alerts dependabot/alerts secret-scanning/alerts; do
  echo "$endpoint"
  gh api "repos/OWNER/REPO/$endpoint?per_page=1" --jq 'length'
done
gh api repos/OWNER/REPO --jq '.permissions'
```

This probe returns a first-page count, not a total. Record HTTP errors instead of
turning them into zero counts. The JSON filter avoids printing alert bodies.

| Response | Interpretation |
|---|---|
| Successful empty array | No visible alerts for that query; feature enablement and scan coverage need separate evidence |
| Successful non-empty array | Visible alerts exist; paginate before reporting totals |
| `403` | Access or feature restrictions prevent a conclusion; alert state is unknown |
| `404` | Feature/resource may be absent or hidden from this identity; do not infer a clean result |

Admin-only endpoint failures are visibility limits, not vulnerabilities. If access
is unavailable, continue with readable evidence and state the limitation; request
a metadata-only owner export when needed. Never request broader credentials in chat.

## Collect alert data and history

Use explicit state filters and pagination for full counts. Code scanning uses
`open`, `fixed`, and `dismissed`; Dependabot and secret scanning have different
state vocabularies, so consult their endpoint documentation.

```bash
gh api --paginate "repos/OWNER/REPO/code-scanning/alerts?state=open&per_page=100" \
  --jq '.[] | {number, state, html_url, rule_id: .rule.id, tool: .tool.name}'
gh api --paginate "repos/OWNER/REPO/code-scanning/alerts?state=fixed&per_page=100" \
  --jq '.[] | {number, state, html_url}'
gh api --paginate "repos/OWNER/REPO/code-scanning/alerts?state=dismissed&per_page=100" \
  --jq '.[] | {number, state, html_url}'
gh api "repos/OWNER/REPO/code-scanning/analyses?per_page=10" \
  --jq '.[] | {tool: .tool.name, ref, commit_sha, created_at, error}'
gh api --paginate "repos/OWNER/REPO/dependabot/alerts?state=open&per_page=100" \
  --jq '.[] | {number, state, html_url, severity: .security_advisory.severity}'
gh api --paginate "repos/OWNER/REPO/secret-scanning/alerts?state=open&per_page=100" \
  --jq '.[] | {number, state, secret_type, created_at, html_url}'
```

Inspect relevant resolved/dismissed history as well as open alerts. Analysis
records establish which scanner ran, on which ref/commit, when, and whether it
reported an error. A scanner other than CodeQL does not prove CodeQL ran. If the
bounded analysis sample is insufficient, paginate or explicitly limit the claim.

Secret-scanning API responses can contain the actual `secret` field. Select only
safe metadata before tool output reaches the conversation or report. Never print
raw responses, retrieve secret values for a report, or include them in examples.
Use equivalent field filtering with connectors; if they cannot suppress values,
use a safe metadata-only path instead.

## Review repository configuration

Alerts show scanner observations. Configuration shows available controls. Check:

- `.github/dependabot.yml` or `.yaml`, including relevant package ecosystems and
  `github-actions` updates.
- `SECURITY.md` in a supported repository location.
- Workflow `permissions`, checkout credential persistence, `pull_request_target`
  and `workflow_run` boundaries, full-SHA Action pinning, and expression values
  interpolated into `run` scripts.
- Rulesets and branch protection, including relevant scope and enforcement;
  `gh api repos/OWNER/REPO/rulesets` is one read-only starting point.
- Secret scanning and push protection settings, where visible.

Separate missing controls, unknown settings, and demonstrated vulnerabilities.
Inspect existing validation before calling an interpolation pattern exploitable.
Do not enable features or change repository configuration as part of reporting.

## Map scanner coverage

CodeQL can find taint-flow and pattern defects, but an empty dashboard does not
prove authorization, concurrency, lifecycle, installer-integrity, or process
cleanup invariants. Coverage depends on the language, queries, configuration,
revision, and paths actually analyzed. Avoid categorical claims that CodeQL can
never detect a vulnerability class.

For each manual finding, record an appropriate CWE when supported, whether CodeQL
would likely detect it, and the evidence for that assessment. Mark the mapping as
a prediction unless the applicable analysis was actually run. Secret scanning is
not a general audit of local runtime credential handling or child environments.

## Ground claims in code

Read the implementation, callers, and defenses before retaining a code finding.
Record the revision, file, line, failure condition, preconditions, impact, and fix.
Search hits such as disabled TLS verification, ambient child-process environments,
or shell execution are leads, not proof of exploitability.

Keep evidence separate from severity: use `CONFIRMED`, `SUSPECTED`, `NON LIQUET`, or
`REFUTED` as appropriate. Cite the rule or contract before claiming an invariant
breach. A clean automated scan is not evidence that a manual candidate is safe;
likewise, reviewer suspicion is not evidence of a High or Critical issue.

## Report structure

Write one Markdown report per repository, since owners, access, and audiences vary:

1. Executive summary, date/revision, access limits, and GHAS feature-state table.
2. Severity-sorted findings table with IDs, evidence status, CWE where justified,
   predicted/observed CodeQL coverage, and links to details or local draft issues.
3. Short details per finding: mechanism, source evidence, prerequisites, fix.
4. Verified controls worth preserving.
5. Recommended remediation order.
6. Limits: unreadable endpoints, unreviewed code, scans not run, and nothing filed
   unless separately authorized.

Severity means demonstrated impact and reachability, not effort. Distinguish
reliability defects and configuration hardening from exploitable vulnerabilities;
a race or atomicity bug may still be security-relevant when its impact proves it.
Avoid declaring the repository safe solely because alert counts are zero.

## Prompt template

```text
Produce a GHAS report for OWNER/REPO.
1. Probe access to code scanning, Dependabot and secret scanning; record unknowns.
2. Collect paginated alerts, relevant history, and recent analysis records.
   Select safe metadata only; never expose secret values.
3. Review repository security configuration, workflows and visible rulesets.
4. Verify existing observations against a pinned revision and cite file/line,
   preconditions, impact, evidence status, CWE and predicted CodeQL coverage.
5. Write one Markdown report: summary, feature states, severity-sorted findings
   with links, details, verified controls, remediation order and limits.
Do not run new scans, change settings, upload results, or file issues as part of
this report. Mark predictions and inaccessible data explicitly.
```

## Pitfalls and worked lessons

- Crow's initial review could read code scanning and Dependabot, but secret
  scanning returned 404. Raven returned 403 for all three. These were dated
  observations, not reusable facts about either repository's current state.
- A missing update configuration, mutable Action tags, or absent reporting policy
  may deserve hardening without generating scanner alerts.
- An opt-in insecure setting is not automatically a confirmed vulnerability;
  evaluate its reachability, disclosure, intended use, and actual impact.
- A report must distinguish enabled scanning from a successful analysis on the
  relevant revision, and a first-page count from a complete inventory.
- Draft locally before publishing. An issue request still needs deduplication,
  redaction, taxonomy validation, and the authorized `log` workflow.

## Official references

- [Code scanning REST API](https://docs.github.com/en/rest/code-scanning/code-scanning)
- [Dependabot alerts REST API](https://docs.github.com/en/rest/dependabot/alerts)
- [Secret scanning REST API](https://docs.github.com/en/rest/secret-scanning/secret-scanning)
- [REST API pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)
