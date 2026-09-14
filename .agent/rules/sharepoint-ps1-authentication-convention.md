---
trigger: always_on
description: Standard PnP.PowerShell authentication pattern every .ps1 tenant-scripting tool in this repo must follow.
globs: ["*.ps1"]
---

## Standard SharePoint (.ps1) authentication pattern

**Applies to every live-tenant `.ps1` script in this repo** (`plugins/*/scripts/*.ps1`,
`plugins/*/skills/*/scripts/*.ps1`) **except scripts that explicitly document Certificate/App-Only
auth** (e.g. an unattended cert-based service script built per
`plugins/workbench-setup/references/app-registration-overview.md`'s App-Only scenario) — those
follow their own documented certificate flow instead, not this one.

Reference implementation:
`plugins/workbench-setup/scripts/test-spo-connection.ps1` (baseline) and
`plugins/sharepoint-content-publication/scripts/spo-page-copy-plan.ps1` (baseline +
`TenantAdminUrl`).

### The pattern

1. **Read connection details from `config.psd1`**, not hardcoded values. Support both schemas
   already in use across this repo:
   ```powershell
   param(
       [string]$ConfigPath = "$PSScriptRoot\..\..\..\config.psd1"
   )
   $raw = Import-PowerShellDataFile $ConfigPath
   $cfg = if ($raw.ContainsKey('Connection')) { $raw.Connection } else { $raw }
   ```
   Adjust the relative `..\..\..\` depth to the script's actual location under `plugins/`.

2. **Connect interactively (delegated auth)**, matching `AuthenticationMode = "Interactive"` in
   `config.psd1`:
   ```powershell
   Connect-PnPOnline -Url $cfg.SiteUrl -ClientId $cfg.ClientId -Tenant $cfg.TenantId -Interactive
   ```

3. **Pass `-TenantAdminUrl` whenever the script calls any cmdlet that needs tenant-admin-center
   context** (cross-site-collection operations such as `Copy-PnPPage`, anything documented by
   Microsoft/PnP as requiring the SharePoint Administrator role) — read it from
   `Authentication.TenantAdminUrl` in `config.psd1`, and let an explicit `-TenantAdminUrl` script
   parameter override it:
   ```powershell
   $connectParameters = @{ Url = $cfg.SiteUrl; ClientId = $cfg.ClientId; Tenant = $cfg.TenantId; Interactive = $true }
   if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
   Connect-PnPOnline @connectParameters
   ```
   Without this, cross-site-collection cmdlets fail with "Attempted to perform an unauthorized
   operation" even when the signed-in account genuinely has SharePoint Administrator rights — PnP
   guesses the admin center URL rather than being told it, and the guess isn't always right.

### Why

**Incident (2026-08-11):** `spo-page-copy-plan.ps1`'s `-Execute` path called `Copy-PnPPage` after
connecting only to the source site, with no `-TenantAdminUrl`. It failed against the real tenant
(`bcgov.sharepoint.com`) with "Unable to connect to the SharePoint Online Admin Center ... Attempted
to perform an unauthorized operation" — not a script logic bug, but a missing standard-auth
parameter. Fixed by adding a `-TenantAdminUrl` parameter, sourcing it from `config.psd1`'s
`Authentication.TenantAdminUrl`, and passing it through every `Connect-PnPOnline` call the script
makes. See `.agent/map-debt.md` for the full incident record if one is added.

### Applying this rule

- **New `.ps1` scripts**: follow this pattern from the start.
- **Existing `.ps1` scripts**: do not need a proactive retrofit sweep on their own, but when a
  script is touched for any other reason and it performs live tenant I/O, bring its connection
  logic in line with this pattern as part of that change.
- **Do not invent a different auth flow per script** (e.g. hardcoding `-Interactive` with no
  `-TenantAdminUrl` support, or a bespoke device-code flow) unless the operation genuinely requires
  something this pattern doesn't cover — if so, document why in that script's own header, don't
  silently diverge.
