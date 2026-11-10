# Copilot Cowork Package Lifecycle

## Contents

- [Package model](#package-model)
- [Create from scratch](#create-from-scratch)
- [Check the toolchain](#check-the-toolchain)
- [Create a package with WIQD](#create-a-package-with-wiqd)
- [Convert an existing plugin](#convert-an-existing-plugin)
- [Validate and package](#validate-and-package)
- [Package locally without WIQD](#package-locally-without-wiqd)
- [Scaffold from an APM plugin](#scaffold-from-an-apm-plugin)
- [Skills over the 20-file limit](#skills-over-the-20-file-limit)
- [Supported file types](#supported-file-types)
- [Content checks](#content-checks)
- [What runs in Cowork and Chat](#what-runs-in-cowork-and-chat)
- [Share and deploy](#share-and-deploy)
- [Authoritative references](#authoritative-references)

## Package model

A Cowork plugin is distributed as a Microsoft 365 App Package ZIP. Its usual contents
are:

```text
appPackage/
  manifest.json
  color.png
  outline.png
  skills/
    <skill-folder>/
      SKILL.md
      references/          # optional; loaded on demand
      assets/              # optional
      scripts/             # optional; packaged as companion files
```

Source-only `evals/` and `tests/` folders stay in the repository and are not packaged.
Each skill may carry at most 20 companion files (any file other than `SKILL.md`), 5 MB
per file and 10 MB in total, so keep references, assets and scripts within that budget.

The manifest registers each skill folder. A remote MCP connector can be declared in the
manifest, but its server runs separately; it is not embedded as an executable server in
the ZIP. Keep server implementation and deployment in the source repository or hosting
environment, outside the package. Skills provide instructions and reference material.
Packaged `scripts/` travel with the skill, but do not assume Cowork executes them; put
anything that must reliably run behind the remote MCP connector.

Prefer WIQD-generated manifests and assets over hand-authoring. WIQD currently generates
manifest version 1.29; Microsoft examples may use 1.28, whose connector requirements
differ. Inspect the generated manifest and validate against the target channel's current
rules instead of copying an old sample.

## Create from scratch

For a source repository that needs both an authoring structure and a Cowork ZIP, use the
existing skills by name:

1. Use `authoring-plugins` when a new APM-native source plugin is needed. It creates the
   repository-side `.apm/skills/` structure; that APM plugin is not the M365 app package.
2. Use `authoring-skills` to create or audit the portable skill. Keep its `SKILL.md`,
   references, and any needed assets self-contained.
3. Use this skill to create the M365 package project. Place the selected skill folder
   under `appPackage/skills/<skill-slug>/`, register that folder in the M365
   `manifest.json`, and use the platform-required icons. Do not copy APM manifests into
   the upload ZIP or confuse `apm.yml` / `.claude-plugin/plugin.json` with the M365
   `manifest.json`.
4. Prefer WIQD for scaffold, validation, provisioning, and package creation. WIQD
   provides the M365 manifest and platform lifecycle; the source-authoring skills do
   not replace it.

Copy only the approved skill folder into the Cowork package; keep its APM source in the
repository. Include the skill's `references/`, `assets/` and `scripts/`; leave out
`evals/` and `tests/`. Prefer a remote MCP connector for runtime behavior that must run
reliably, rather than depending on Cowork executing packaged scripts.

## Check the toolchain

1. Read the current [WIQD installation guide](https://microsoft.github.io/wiqd/getting-started/installation/)
   and [CLI reference](https://aka.ms/wiqd/docs?id=cli/reference).
2. WIQD is preview software and may introduce breaking changes. Verify the available
   release and command syntax, then pin the exact tested version in the repository or
   CI setup. Do not substitute an unverified version or a floating `latest`.
3. Treat authentication and tenant operations as external side effects. Confirm the
   tenant and intended scope with the user before running login, provision, share,
   publish, or delete commands. Use the CLI's interactive login; never collect
   credentials in chat.
4. Keep generated environment files out of source control unless the user has reviewed
   them and confirmed they contain no secrets or tenant-specific sensitive data.

## Create a package with WIQD

Use the WIQD lifecycle for a new project or a project created with WIQD:

```console
wiqd auth login --interactive
wiqd plugin create --name <plugin-name>
wiqd plugin add skill --name "<Skill Display Name>"
wiqd plugin add connector --name "<Connector Name>" --description "<Purpose>" --url <remote-mcp-url>
```

Run commands from the project directory and include the appropriate environment option
if required by the pinned WIQD version. Add only the capabilities the user requested;
the connector command is optional. Do not invent endpoint URLs, OAuth registrations,
privacy/terms URLs, or user-facing skill content. Inspect generated paths and manifest
entries after each add operation. Keep skill folders self-contained and copy source
skills only with the user's authorization.

## Convert an existing plugin

Choose the conversion route based on whether the user needs a maintained WIQD project
or a publishable ZIP now:

- `wiqd plugin import --path <plugin-path>` can import Claude, Cursor, or Open Plugin
  sources, but Microsoft's current guidance says imported projects support only the
  read-only `validate`, `show`, and `list` operations. Do not assume they can be
  provisioned, packaged, or shared.
- For a publishable ZIP from a Claude/Open Plugin source, use Microsoft's current
  conversion route through the Microsoft 365 Agents Toolkit CLI (`atk`), following its
  current official documentation. The documented import requires privacy and terms
  URLs when the source has no round-trip metadata, then package the resulting project.
  Do not fall back to an older converter unless the current Microsoft instructions
  require it.

Before conversion, inspect source manifests, skills, and connector configuration.
Confirm required privacy and terms URLs with the user. Review the conversion report and
resulting manifest, especially generated connector authentication references; replace
placeholders only with verified values from the authorized owner. Do not claim
unsupported plugin features were converted: commands, sub-agents, hooks, and executable
directories may not have M365 equivalents.

## Validate and package

Use the commands and required environment flags documented for the pinned WIQD release.
The common lifecycle is:

```console
wiqd plugin validate --env <environment>
wiqd plugin provision --env <environment>
wiqd plugin package --env <environment>
wiqd plugin validate --mode deep --env <environment>
```

Static validation is an offline build-loop check and may not cover skills-only or
connector-only behavior. Deep validation checks the built ZIP using the platform's
validation rules. Provisioning generates environment information used by packaging, so
preserve the current release's required ordering. If the pinned CLI documents a
different deep-validation timing, follow it and verify that the final ZIP is the
artifact tested.

Inspect the ZIP without modifying the source: confirm its manifest, 192 x 192 color
icon, 32 x 32 outline icon, intended skill directories, and requested connector
declarations. Check that no access tokens, client secrets, local environment files,
development-only data, or unintended source files are present. Resolve errors and
rerun validation before delivering the artifact.

## Package locally without WIQD

Use the local packager only when the user explicitly needs a manually assembled ZIP or
WIQD is unavailable. It packages an existing `appPackage/` directory; it does not
provision an environment or run Microsoft's App Validation Library. Create that directory
from an APM plugin with `scaffold_cowork_package.py` (next section). WIQD and deep
validation remain the preferred route.

```console
python scripts/package_cowork_plugin.py --plugin-path <project-or-appPackage-path> --output-path <output.zip>
```

The script requires `manifest.json`, correctly sized PNG icons, and at least one
registered skill folder with `SKILL.md`. It keeps `references/`, `assets/` and `scripts/`,
excludes only source-only `evals/` and `tests/` directories (and reports them),
enforces the per-skill companion-file limits (20 files, 5 MB each, 10 MB total),
rejects symbolic links, hidden paths, and likely credential files, verifies ZIP
integrity, and refuses to replace an existing ZIP unless `--overwrite` is supplied.
Review package contents for secrets and run the platform's deep validation before
uploading.

## Scaffold from an APM plugin

`scripts/scaffold_cowork_package.py` creates an `appPackage/` directory from a plugin that
has `.apm/skills/<skill>/` and optionally `.claude-plugin/plugin.json`:

```console
python scripts/scaffold_cowork_package.py --apm-plugin <plugin> --output <dir>/appPackage \
  --developer-name "<name>" --website-url <https-url> --privacy-url <https-url> --terms-url <https-url> \
  [--skills a,b] [--name-short ..] [--name-full ..] [--description-short ..] [--accent-color #RRGGBB] \
  [--app-version 1.2.3] [--exclude-files scripts/server.py] [--drop-scripts-if-needed] \
  [--allow-extensions .ext] [--drop-extensions .ext]
```

It copies each skill's `SKILL.md`, `references/`, `assets/` and `scripts/` (not `evals/` or
`tests/`), generates both icons, and writes `manifest.json`. Privacy and terms URLs are
required arguments and are never invented; confirm them with the owner. The app id is a stable
GUID derived from the plugin name unless `--app-id` is given, so rebuilds update the same app.
The manifest is generated, not WIQD-authored, so run Microsoft's deep validation before upload.
Raise `--app-version` for every republish so the catalog treats it as an update.

## Skills over the 20-file limit

Cowork allows 20 companion files per skill. When a skill has more, the scaffold (or
`scripts/bundle_skill_companions.py`, which does one skill) bundles Markdown under
`references/<folder>/` and `assets/<folder>/` into `<folder>.md`, one section per source
guide with acceptance criteria last, and rewrites every link. If that is not enough it merges
loose guides under references into one `other.md` bundle. Next options are `--exclude-files`
for named files and `--drop-scripts-if-needed`. The source skill is never modified. A "Cowork
build" section listing what was bundled or left out is appended to the copied `SKILL.md`.

## Supported file types

Publish validation rejects file types it does not support ("File extension '.mmd' is not
supported ... in Microsoft 365 Copilot"). The tools use Microsoft Support's list of file formats
Microsoft 365 Copilot works with as an allowlist (see `SUPPORTED_COMPANION_EXTENSIONS` in
`cowork_package_constants.py`). That list is not confirmed to be the validator's exact list.
The scaffold and bundler filter other types and turn links to them into plain text; the packager
refuses them. Use `--allow-extensions` to keep a type Microsoft confirms and `--drop-extensions`
to remove one the validator rejects.

## Content checks

Before zipping, the packager checks that `manifest.json` has a GUID id, a version like 1.2.3,
name and description within their limits (30/100 and 80/4000 characters), https developer URLs
and an accent color; that each `SKILL.md` has frontmatter whose name matches its folder and a
description of at most 1024 characters; and that relative Markdown links in packaged files
point to existing files (a link to a folder is an error). Missing heading anchors are warnings.
`--skip-content-checks` turns this off and is not recommended.

## What runs in Cowork and Chat

Observed in tests, not guaranteed by Microsoft: a packaged skill's Python script ran with a real
interpreter in Cowork (exit code 0, correct output), and a generator script from a packaged skill
ran in Microsoft 365 Copilot Chat and returned its HTML file. A server script is not reachable
from outside the environment, and the environment can reset between tasks, so write results to
the task output folder. Prefer scripts that write files, and test by asking the agent to list the
skill folder and run the script, forbidding simulated output.

## Share and deploy

Sharing is a separate, explicitly approved step; a successful local package is not
evidence of tenant publication.

- Direct sharing uses `wiqd plugin share --scope users --email <approved-address>`.
  Confirm each recipient and target tenant first.
- Tenant-wide sharing uses `wiqd plugin share --scope tenant`; require explicit
  approval because it grants broad organizational access.
- Organization-managed deployment is an administrator action in the Microsoft 365
  admin center under **Agents > Tools > Registry**. Confirm target users/groups and
  administrative approval before upload or assignment.
- Users must authorize external connectors themselves. Do not describe a connector as
  authorized merely because it is listed in the package.
- Do not delete provisioned resources or revoke sharing unless the user explicitly
  requests that operation.

Report the package path, exact tool version, validation status, tenant/environment,
and which sharing or deployment steps were or were not completed.

## Authoritative references

- [Build plugins for Copilot Cowork](https://learn.microsoft.com/en-us/copilot/cowork/cowork-plugin-development) — package format, WIQD lifecycle, conversion, validation, and manual packaging guidance.
- [WIQD CLI reference](https://aka.ms/wiqd/docs?id=cli/reference) — current commands, options, environment flags, and import lifecycle support.
- [WIQD installation guide](https://microsoft.github.io/wiqd/getting-started/installation/) — supported installation methods and prerequisites.
- [Microsoft 365 Agents Toolkit CLI](https://aka.ms/copilot-cowork-plugin-conversion-script) — current Claude/Open Plugin conversion instructions.
