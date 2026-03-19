#!/usr/bin/env python3
"""
Scaffold GitHub Action
=====================================

Purpose:
    Scaffolds a traditional deterministic GitHub Actions CI/CD workflow YAML.
    Supports common categories: test, build, lint, deploy, release, security,
    maintenance, and custom. Does NOT involve AI at runtime.

    This is distinct from scaffold_agentic_workflow.py which creates AI-powered
    GitHub Agentic Workflows (Official format or Smart Failure pattern).

Layer: Codify

Usage:
    python scaffold_github_action.py --category <category> [OPTIONS]

    Options:
      --category {test,build,lint,deploy,release,security,maintenance,custom}
      --platform {python,nodejs,go,docker,dotnet,generic}
      --triggers TRIGGER [TRIGGER ...]  (pull_request, push, schedule, etc.)
      --name TEXT                        Human-readable workflow name
      --branch TEXT                      Branch for push triggers (default: main)

Related:
    - create-github-action/SKILL.md
    - scaffold_agentic_workflow.py  (for AI-powered workflows)
"""

import argparse
import textwrap
from pathlib import Path
from typing import Optional

# --- Trigger block builders ---

TRIGGER_MAP: dict[str, str] = {
    "pull_request": "  pull_request:",
    "push_main": "  push:\n    branches: [\"{branch}\"]",
    "schedule_weekly": "  schedule:\n    - cron: '0 9 * * 1'  # Mondays 9am UTC",
    "schedule_daily": "  schedule:\n    - cron: '0 8 * * *'  # Daily 8am UTC",
    "workflow_dispatch": "  workflow_dispatch:",
    "release": "  release:\n    types: [published]",
    "issues": "  issues:\n    types: [opened]",
}


def build_on_block(triggers: list[str], branch: str) -> str:
    """Build the `on:` trigger block from the list of trigger keys."""
    lines = []
    for t in triggers:
        raw = TRIGGER_MAP.get(t, f"  {t}:")
        lines.append(raw.replace("{branch}", branch))
    return "\n".join(lines) if lines else "  workflow_dispatch:"


# --- Platform setup steps ---

PLATFORM_SETUP: dict[str, str] = {
    "python": textwrap.dedent("""\
          - name: Set up Python
            uses: actions/setup-python@v5
            with:
              python-version: "3.12"

          - name: Cache pip dependencies
            uses: actions/cache@v4
            with:
              path: ~/.cache/pip
              key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
              restore-keys: ${{ runner.os }}-pip-

          - name: Install dependencies
            run: |
              python -m pip install --upgrade pip
              pip install -r requirements.txt"""),
    "nodejs": textwrap.dedent("""\
          - name: Set up Node.js
            uses: actions/setup-node@v4
            with:
              node-version: "20"
              cache: "npm"

          - name: Install dependencies
            run: npm ci"""),
    "go": textwrap.dedent("""\
          - name: Set up Go
            uses: actions/setup-go@v5
            with:
              go-version: "1.22"
              cache: true"""),
    "docker": textwrap.dedent("""\
          - name: Set up Docker Buildx
            uses: docker/setup-buildx-action@v3

          - name: Log in to GitHub Container Registry
            uses: docker/login-action@v3
            with:
              registry: ghcr.io
              username: ${{ github.actor }}
              password: ${{ secrets.GITHUB_TOKEN }}"""),
    "dotnet": textwrap.dedent("""\
          - name: Set up .NET
            uses: actions/setup-dotnet@v4
            with:
              dotnet-version: "8.0.x"

          - name: Restore dependencies
            run: dotnet restore"""),
    "generic": "",
}


# --- Category-specific job steps ---

def category_steps(category: str, platform: str, branch: str) -> str:
    """Return the core job steps for the given category + platform."""

    if category == "test":
        if platform == "python":
            return textwrap.dedent("""\
              - name: Run tests
                run: pytest --tb=short -q""")
        if platform == "nodejs":
            return textwrap.dedent("""\
              - name: Run tests
                run: npm test""")
        if platform == "go":
            return textwrap.dedent("""\
              - name: Run tests
                run: go test ./... -v""")
        if platform == "dotnet":
            return textwrap.dedent("""\
              - name: Run tests
                run: dotnet test --no-restore --verbosity normal""")
        return textwrap.dedent("""\
              - name: Run tests
                run: echo "Add your test command here" """)

    if category == "lint":
        if platform == "python":
            return textwrap.dedent("""\
              - name: Install linters
                run: pip install ruff mypy

              - name: Ruff lint
                run: ruff check .

              - name: Ruff format check
                run: ruff format --check .""")
        if platform == "nodejs":
            return textwrap.dedent("""\
              - name: Run ESLint
                run: npm run lint

              - name: Check formatting (Prettier)
                run: npx prettier --check .""")
        return textwrap.dedent("""\
              - name: Lint Markdown
                uses: DavidAnson/markdownlint-cli2-action@v16
                with:
                  globs: "**/*.md" """)

    if category == "build":
        if platform == "docker":
            return textwrap.dedent("""\
              - name: Build Docker image
                uses: docker/build-push-action@v5
                with:
                  context: .
                  push: false
                  tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
                  cache-from: type=gha
                  cache-to: type=gha,mode=max""")
        if platform == "nodejs":
            return textwrap.dedent("""\
              - name: Build
                run: npm run build

              - name: Upload build artifact
                uses: actions/upload-artifact@v4
                with:
                  name: dist
                  path: dist/""")
        if platform == "python":
            return textwrap.dedent("""\
              - name: Build package
                run: python -m build

              - name: Upload dist
                uses: actions/upload-artifact@v4
                with:
                  name: dist
                  path: dist/""")
        return textwrap.dedent("""\
              - name: Build
                run: echo "Add your build command here" """)

    if category == "deploy":
        return textwrap.dedent("""\
              - name: Deploy to GitHub Pages
                uses: JamesIves/github-pages-deploy-action@v4
                with:
                  folder: dist
                  branch: gh-pages""")

    if category == "release":
        if platform == "python":
            return textwrap.dedent("""\
              - name: Build release packages
                run: python -m build

              - name: Publish to PyPI
                uses: pypa/gh-action-pypi-publish@release/v1
                with:
                  password: ${{ secrets.PYPI_TOKEN }}""")
        if platform == "nodejs":
            return textwrap.dedent("""\
              - name: Publish to npm
                run: npm publish
                env:
                  NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}""")
        return textwrap.dedent("""\
              - name: Create GitHub Release
                uses: softprops/action-gh-release@v2
                with:
                  generate_release_notes: true
                  files: dist/*""")

    if category == "security":
        return textwrap.dedent("""\
              - name: Initialize CodeQL
                uses: github/codeql-action/init@v3
                with:
                  languages: python  # Adjust to your language

              - name: Autobuild
                uses: github/codeql-action/autobuild@v3

              - name: Perform CodeQL Analysis
                uses: github/codeql-action/analyze@v3

              - name: Run Trivy vulnerability scanner
                uses: aquasecurity/trivy-action@master
                with:
                  scan-type: "fs"
                  severity: "CRITICAL,HIGH" """)

    if category == "maintenance":
        return textwrap.dedent("""\
              - name: Close stale issues and pull requests
                uses: actions/stale@v9
                with:
                  stale-issue-message: "This issue has been automatically marked as stale."
                  stale-pr-message: "This PR has been automatically marked as stale."
                  days-before-stale: 60
                  days-before-close: 14""")

    # custom / fallback
    return textwrap.dedent("""\
              - name: Custom Step
                run: |
                  echo "Add your custom steps here" """)


def generate_github_action(
    category: str,
    platform: str,
    triggers: list[str],
    name: str,
    branch: str,
    workflows_dir: Path,
) -> Path:
    """
    Generates a traditional GitHub Actions YAML workflow file.

    Args:
        category: Workflow type (test, build, lint, deploy, release, etc.).
        platform: Target tech stack (python, nodejs, go, docker, etc.).
        triggers: List of GitHub event trigger keys.
        name: Human-readable workflow name.
        branch: Branch name for push triggers.
        workflows_dir: Target .github/workflows/ directory.

    Returns:
        Path to the created .yml file.
    """
    on_block = build_on_block(triggers, branch)
    setup = PLATFORM_SETUP.get(platform, "")
    steps_body = category_steps(category, platform, branch)

    # Permissions
    permissions_block = "  contents: read"
    if category in ("release", "deploy"):
        permissions_block = "  contents: write\n  packages: write"
    elif category in ("security",):
        permissions_block = "  contents: read\n  security-events: write"

    # Combine setup + steps (skip blank setup)
    all_steps = (setup + "\n\n" + steps_body).strip() if setup else steps_body

    yaml_content = textwrap.dedent(f"""\
    name: {name}

    on:
    {on_block}

    permissions:
    {permissions_block}

    jobs:
      {category}:
        name: {name}
        runs-on: ubuntu-latest
        steps:
          - name: Checkout repository
            uses: actions/checkout@v4

    {textwrap.indent(all_steps, '      ')}
    """)

    # Filename from category + platform
    slug = f"{category}-{platform}".replace("-generic", "")
    output_file = workflows_dir / f"{slug}.yml"
    output_file.write_text(yaml_content, encoding="utf-8")
    return output_file


if __name__ == "__main__":
    CATEGORIES = ["test", "build", "lint", "deploy", "release", "security", "maintenance", "custom"]
    PLATFORMS = ["python", "nodejs", "go", "docker", "dotnet", "generic"]
    TRIGGER_CHOICES = ["pull_request", "push_main", "schedule_weekly", "schedule_daily",
                       "workflow_dispatch", "release", "issues"]

    parser = argparse.ArgumentParser(
        description="Scaffold a traditional GitHub Actions CI/CD workflow.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
        Examples:
          # Python test suite on PRs
          python scaffold_github_action.py --category test --platform python --triggers pull_request push_main

          # Docker build on PRs
          python scaffold_github_action.py --category build --platform docker --triggers pull_request

          # Weekly maintenance (stale issues)
          python scaffold_github_action.py --category maintenance --triggers schedule_weekly

          # Python PyPI release on GitHub Release publish
          python scaffold_github_action.py --category release --platform python --triggers release
        """),
    )
    parser.add_argument("--category", required=True, choices=CATEGORIES, help="Workflow type")
    parser.add_argument("--platform", default="generic", choices=PLATFORMS, help="Tech stack")
    parser.add_argument(
        "--triggers",
        nargs="*",
        choices=TRIGGER_CHOICES,
        default=["pull_request"],
        metavar="TRIGGER",
        help=f"GitHub events (choices: {', '.join(TRIGGER_CHOICES)})",
    )
    parser.add_argument("--name", default="", help="Human-readable workflow name")
    parser.add_argument("--branch", default="main", help="Branch for push triggers")

    args = parser.parse_args()

    display_name = args.name or f"{args.category.title()} ({args.platform.title()})"
    workflows_dir = Path.cwd() / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    output = generate_github_action(
        category=args.category,
        platform=args.platform,
        triggers=args.triggers or ["pull_request"],
        name=display_name,
        branch=args.branch,
        workflows_dir=workflows_dir,
    )

    print(f"\n✅ Generated GitHub Action: {output}")
    print(f"   Category: {args.category} | Platform: {args.platform}")
    print(f"   Triggers: {', '.join(args.triggers or ['pull_request'])}")
    print(f"\nNext: Review {output.name}, add required secrets, then commit.")
