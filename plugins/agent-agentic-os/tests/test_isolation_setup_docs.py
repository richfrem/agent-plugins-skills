"""
tests/test_isolation_setup_docs.py
==================================

Purpose:
    Failing-first acceptance tests for T8 (auth-ciba-increment-b, issue #639, spec case 12): the
    isolation setup documentation `references/isolation-setup.md` exists at the path the Gate 1
    remediation error names, is reachable from the os-signing-setup skill, states the ranked setups
    and the honest residual risks (D4), and describes the strict/legacy modes and the human-side flow.
    Real files only.

Key Input Dependencies:
    - plugins/agent-agentic-os/references/isolation-setup.md
    - plugins/agent-agentic-os/skills/os-signing-setup/ (SKILL.md, references/ symlink)
    - control_plane/coordinator.py (the `setup_docs` path in the remediation error)

Key Functions (test cases):
    - test_doc_exists_at_the_path_the_remediation_error_names
    - test_doc_states_setups_modes_and_honest_limits
    - test_doc_is_reachable_from_the_skill
"""

import re
import sys
from pathlib import Path

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

PLUGIN = Path(__file__).resolve().parent.parent
REPO = PLUGIN.parent.parent
DOC = PLUGIN / "references" / "isolation-setup.md"


def test_doc_exists_at_the_path_the_remediation_error_names():
    source = (PLUGIN / "scripts" / "control_plane" / "coordinator.py").read_text()
    named = re.search(r'"setup_docs": "([^"]+)"', source).group(1)
    assert (REPO / named).resolve() == DOC.resolve()
    assert DOC.is_file()


def test_doc_states_setups_modes_and_honest_limits():
    text = DOC.read_text().lower()
    for required in (
        "container", "dedicated", "agentic-os-local-agent",       # the ranked setups
        "same-account", "strict",                                   # the single mode and the weakest posture
        "allowed_signers", "0600", "0700", "challenge",             # what is protected and how
        "show-challenge", "approve-transition", "test-signing-mechanics", "setup_ciba_identity.py",
        "residual", "direct", "database",                          # D4: a same-account DB writer is not stopped
        "touch id", "certificate",                                 # explicitly not supported
        "trusted display",                                         # FIDO caveat
        "macos", "windows",
    ):
        assert required in text, required
    assert "input_unhardened" not in text and "off by default" not in text  # the removed fallback is not documented as an option


def test_doc_is_reachable_from_the_skill():
    skill = PLUGIN / "skills" / "os-signing-setup"
    assert "references/isolation-setup.md" in (skill / "SKILL.md").read_text()
    link = skill / "references" / "isolation-setup.md"
    assert link.is_file() and link.resolve() == DOC.resolve()
