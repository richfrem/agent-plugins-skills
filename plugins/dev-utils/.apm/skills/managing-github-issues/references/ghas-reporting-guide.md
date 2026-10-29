# Guide: Producing a GHAS Report

Reusable lessons from the Crow and Raven reviews (2026-10-27), adapted from
`GHAS-REPORTING-GUIDE.md` in `richfrem/crow-raven-analysis`. This reference is
self-contained: the source repository and its local reports are not required.

Use for requests to report on GitHub Advanced Security (GHAS), CodeQL alerts,
Dependabot alerts, secret scanning, or repository security posture. Reporting is
read-only against GitHub; write the requested local report without changing
settings, dismissing alerts, uploading SARIF, or filing issues. Submitting a private vulnerability report, creating a draft advisory, uploading SARIF, and
publishing a public issue/advisory are separate external writes. Prepare the complete payload first
and execute only the submission the user authorized. The issue `log` mode does not create advisories.

## Contents

- [Establish access](#establish-access)
- [Collect alert data and history](#collect-alert-data-and-history)
- [Review repository configuration](#review-repository-configuration)
- [Map scanner coverage](#map-scanner-coverage)
- [Ground claims in code](#ground-claims-in-code)
- [Report structure](#report-structure)
- [Submit privately through GitHub](#submit-privately-through-github)
- [Submit through gh api](#submit-through-gh-api)
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

## Submit privately through GitHub

A local GHAS posture report and a vulnerability submission are different deliverables. A user may
legitimately authorize both. Preparing a vulnerability report is not public disclosure. Follow the
repository's security policy; do not post sensitive details in a public issue merely because the
private submission is unavailable. Keep a reusable guide generic: target findings belong in the
private report, not in this skill package.

### Select the correct workflow

| Purpose and role | GitHub interface | REST endpoint for the same operation |
|---|---|---|
| Reporter sends a vulnerability to maintainers; private reporting must be enabled | Security and quality → Advisories → Report a vulnerability; typically `https://github.com/OWNER/REPO/security/advisories/new` | `POST /repos/OWNER/REPO/security-advisories/reports` |
| Repository administrator/security manager creates a private draft advisory | Security and quality → Advisories → New draft security advisory | `POST /repos/OWNER/REPO/security-advisories` |
| Publish an accepted advisory or create a public issue | Separate publication workflow | Not part of either private-creation command below |

The same URL area can present different forms according to role; read the heading and visibility
notice. A private report normally enters triage; a maintainer advisory begins as a draft. Repository
write access alone does not establish permission to create a maintainer-owned advisory. Check the
current API permission requirements; fine-grained tokens need Repository security advisories write
permission for these POST endpoints. If API permission is unavailable but the signed-in browser
allows private reporting, use the browser rather than requesting credentials in chat.

### Fill the vulnerability-report form

Prepare these fields in the report before opening or automating the form. Include enough content
for maintainers to reproduce and fix the defect without access to the reporter's local issue files.

| Form field | What to include | API mapping |
|---|---|---|
| Title | A concise mechanism and affected component; avoid unsupported severity claims | `summary` (the short API title) |
| Summary | The failure, prerequisites, affected users, bounded impact and evidence status | A `## Summary` section inside `description` |
| Details | Pinned revision, file/line links, sourced invariant, entry-to-sink trace, defenses assessed and remediation | `## Details` inside `description` |
| Proof of concept | Complete safe reproduction, synthetic inputs, commands, expected/observed outcome, cleanup and execution limits | `## Proof of concept` inside `description` |
| Impact | Demonstrated authority/data/effects, affected parties, conditions, and what was not established | `## Impact` inside `description` |
| Ecosystem | The actual ecosystem; use Other for unsupported/custom distribution, not an invented npm/PyPI registration | `vulnerabilities[].package.ecosystem`; Other maps to `other` |
| Package name | Actual package/workflow/component identity, appropriate to that ecosystem | `vulnerabilities[].package.name` |
| Affected versions | Supply a verified exact version/range in the product row; a commit in Details alone does not satisfy publication metadata | `vulnerabilities[].vulnerable_version_range` |
| Patched versions | Only verified fixed versions; leave unknown/unset if no fix is established | `vulnerabilities[].patched_versions` (omit or null when unknown) |
| Severity | Evidence-based categorical severity, or an independently calculated CVSS vector; unknown when unassessed | `severity` OR `cvss_vector_string`, never both |
| Weaknesses/CWE | Supported mechanism-specific CWE IDs, where the form offers them | `cwe_ids` |
| Vulnerable functions | Exact functions when applicable; do not invent them for a configuration-only defect | `vulnerabilities[].vulnerable_functions` |
| CVE/credits, if shown in a maintainer form | Existing identifiers and agreed attribution only; do not imply a CVE was issued | Maintainer-advisory fields such as `cve_id` and `credits`; check that endpoint's schema |

The web form's Summary text area is **not** the API `summary`: that API field is the short title.
Combine the four narrative text areas into one Markdown `description`. A maintainer form with one
Description area can use the same sections. Repeat affected-product rows only for independently
substantiated products; group a compound chain clearly and avoid counting the same root cause twice.

For non-versioned repository automation, explain the audited commit and configuration observation in
Details. Do not turn one tested revision into an unsupported all-versions range or call a release
patched before verifying the fix. Private intake can accept an incomplete affected-product row and
then show **Required information missing: list affected version(s)**. Record that as accepted for triage
but **not publication-ready**; do not call the metadata complete just because the POST returned 201.

A **No known CVE** notice is normal before an identifier is assigned; it does not invalidate a
private report. Maintain CVE assignment separately from required affected-version metadata and
optional patched-version suggestions. Maintainers can request a CVE through GitHub when appropriate;
never invent an identifier or request/publicize one without the authorized maintainer workflow.

Before submission, verify `vulnerabilities[].vulnerable_version_range` for every affected product.
When exactly one release is established, use an exact value such as `= 1.2.3`, with the tag-to-commit
mapping recorded in Details. Do not invent `<= 1.2.3` or `< next-version` from one tested release.
Resolve annotated tags to their target commit; package metadata by itself does not prove the release
contains the audited code. For a genuinely non-versioned target, explain that limitation and coordinate
with maintainers instead of falsely claiming publication readiness. Unknown patched versions remain
unset; a patched-version suggestion is different from an affected-version requirement.

Review the filled form, including private visibility, target, counts and attachment contents, before
clicking its submission button. Record the returned advisory/report URL and state. Creating a private
report or draft is not publishing it; later publication is a separately authorized action.

## Submit through gh api

The GitHub CLI can call the REST API; there is no need to turn a private vulnerability into `gh issue create`.
The following is an example template, **not** a command to run during a read-only GHAS review.
Replace every example value and complete the narrative before using it. Store payloads under ignored
`temp/`, never credentials or private findings in this public skill folder.

Save `temp/security-report.json` as valid JSON. The deliberately synthetic example has no patch claim:

```json
{
  "summary": "Authorization check is omitted on the example export path",
  "description": "## Summary\nDescribe verified behavior and prerequisites.\n\n## Details\nInclude revision, source trace, defenses, fix and acceptance criteria.\n\n## Proof of concept\nInclude complete synthetic reproduction and actual observations.\n\n## Impact\nSeparate demonstrated impact from unverified consequences.",
  "severity": "high",
  "vulnerabilities": [
    {
      "package": {"ecosystem": "other", "name": "example-component"},
      "vulnerable_version_range": "= 1.2.3"
    }
  ],
  "cwe_ids": ["CWE-862"]
}
```

Before an external write:

1. Check private reporting and the actor's visible permissions without retrieving secret values:
   `gh api repos/OWNER/REPO/private-vulnerability-reporting` and
   `gh api repos/OWNER/REPO --jq '.permissions'`.
2. Deduplicate against accessible private reports/advisories and relevant issues; inaccessible private
   history is an explicit limit. Do not disclose details in public just to search for duplicates.
3. Check each affected-product row has a supported `vulnerable_version_range`; distinguish
   submission acceptance from publication readiness. Parse the JSON locally, inspect the exact payload, run `redaction_gate.py`'s `scan_for_secrets`
   on the title/description/attachments, and verify versions, counts, CWE and severity. The issue body
   taxonomy applies to public issue mode, not to advisory endpoint fields.
4. Confirm the user's authorization covers the chosen private POST and target repository. No POST
   endpoint below has a server-side dry-run: local payload validation is the preview. Do not try a
   live POST as a test or assume `gh api --dry-run` exists.

**Reporter submission**, only after that review and authorization:

```bash
gh api --method POST "repos/OWNER/REPO/security-advisories/reports" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2026-03-10" \
  --input temp/security-report.json \
  --jq '{ghsa_id,html_url,state,summary}'
```

**Maintainer private draft**, only for an authorized administrator/security manager using a reviewed
payload accepted by the advisory-creation endpoint:

```bash
gh api --method POST "repos/OWNER/REPO/security-advisories" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2026-03-10" \
  --input temp/security-report.json \
  --jq '{ghsa_id,html_url,state,summary}'
```

Use authenticated `gh` configuration; do not put a token in the payload, terminal output or report.
`--input` preserves real JSON newlines and avoids shell-interpolated Markdown. `gh api` handles a
single chosen POST here; it does not publish the resulting advisory. Do not add a subsequent update
that changes its state to published without separate authorization.

A successful creation returns HTTP 201 and a GHSA/URL. Verify the returned state (`triage` for a
report or `draft` for a maintainer draft) rather than claiming it was published. If needed, read back
`gh api repos/OWNER/REPO/security-advisories/GHSA-ID --jq '{ghsa_id,html_url,state,summary}'` when your
identity can access it. Record access limits if read-back is denied. On 403/404 check role, feature
availability and token permissions; on 422 inspect field validation. After a timeout/ambiguous result,
check for an existing submission before retrying to avoid duplicates. Do not retry by creating a public issue.

### Correct affected-version metadata after private submission

Read the current advisory first so updating the product list preserves every existing product:

```bash
gh api "repos/OWNER/REPO/security-advisories/GHSA-ID" \
  --jq '{ghsa_id,state,vulnerabilities}'
```

Prepare `temp/advisory-version-update.json` containing the **complete existing** `vulnerabilities`
array with the verified range added. Updating an array can replace its entire value. Preserve actual
package names, ecosystems, existing patched-version data and vulnerable functions; do not copy these
synthetic example values onto a real advisory:

```json
{
  "vulnerabilities": [
    {
      "package": {"ecosystem": "other", "name": "example-component"},
      "vulnerable_version_range": "= 1.2.3"
    }
  ]
}
```

After reviewing the diff/redaction and obtaining authorization for that metadata correction:

```bash
gh api --method PATCH "repos/OWNER/REPO/security-advisories/GHSA-ID" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2026-03-10" \
  --input temp/advisory-version-update.json \
  --jq '{ghsa_id,html_url,state,vulnerabilities}'
```

Advisory collaborators may have update rights; role/token restrictions still apply. In the GUI, edit
the advisory's affected-products row and save the verified affected version. If the reporter cannot
edit it, provide the exact proposed range and evidence to maintainers rather than creating a duplicate.
Do not change the advisory state or publish it to fix metadata. Read back the range and verify the
required-information warning is resolved where visible; other missing fields may still block publication.

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

Submission references (checked 2026-10-28):
- [Private reporter and maintainer advisory REST endpoints](https://docs.github.com/en/rest/security-advisories/repository-advisories)
- [Creating a maintainer draft](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/fix-reported-vulnerabilities/create-repository-advisory)
- [Advisory field and version guidance](https://docs.github.com/en/code-security/tutorials/fix-reported-vulnerabilities/write-security-advisories)
