"""
control_plane/simulation_identity.py
====================================

Purpose:
    The agent's simulation identity, kept apart from the human's production identity. Real work
    is approved only with the human's key, enrolled in <repo>/context/identity/allowed_signers
    (set up by the human with setup_ciba_identity.py). Simulations run in
    <repo>/context/simulation/simulation_control_plane.db and are approved only with the agent's
    simulation key, which lives in its own folder and trust file:
        <repo>/context/simulation/identity/simulation_key(.pub)
        <repo>/context/simulation/identity/allowed_signers(_selftest)
    The agent may create and use this identity (it is the agent's own key, passphrase-less by
    design). Creating it never writes the human's production trust file; reruns reuse the key and
    only ever add enrollment lines. A key registered here is refused on real work even if someone
    relabels it as a human in the production trust file (approver_policy).

    Also reports readiness for the three parts of the setup separately (human approval,
    simulation, isolation of the agent from the human's trust files), on macOS, Linux and Windows.

Key Input Dependencies:
    - ssh-keygen (OpenSSH 8.1+) to generate the simulation key
    - control_plane.identity_layout, identity_setup (human status, per-OS account commands), isolation_check
    - control_plane.gate1_approval (show_challenge / approve_transition, used by SimulationSigner)

Key Functions:
    - simulation_root() / simulation_db_path() / simulation_layout() -- where simulations and their identity live
    - ensure_identity_at() / ensure_simulation_identity() -- create or reuse the simulation key and enroll it additively
    - simulation_key_fingerprints() -- fingerprints registered as simulation keys for a repository
    - dual_identity_status() -- human / simulation / isolation readiness, reported separately
    - SimulationSigner -- signs a simulation database's gates with the simulation key

Usage:
    from control_plane.simulation_identity import ensure_simulation_identity, simulation_db_path
    PipelineSimulator(simulation_db_path(repo)).run_standard_happy_path(task)  # signs with the simulation key
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Set

from control_plane.approver_policy import AGENT_SIMULATION_PRINCIPAL, SIMULATION_DB_NAME, enrolled_keys, key_fingerprint
from control_plane.identity_layout import IdentityLayout, default_layout
from control_plane.ssh_signing import SELFTEST_NAMESPACE, SIGN_NAMESPACE

SIMULATION_KEY_NAME = "simulation_key"


# <repo>/context/simulation: simulations never share a file with real work
def simulation_root(repo_root: Any) -> Path:
    """Return <repo>/context/simulation."""
    return Path(repo_root) / "context" / "simulation"


def simulation_db_path(repo_root: Any) -> Path:
    """Return <repo>/context/simulation/simulation_control_plane.db."""
    return simulation_root(repo_root) / SIMULATION_DB_NAME


def simulation_layout(repo_root: Any) -> IdentityLayout:
    """Return the simulation identity layout: <repo>/context/simulation/identity."""
    return IdentityLayout(root=simulation_root(repo_root) / "identity")


def _append_line(path: Path, line: str) -> None:
    """Append `line` to a trust file unless already present (additive, never rewrites), owner-only on POSIX."""
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if line not in existing.splitlines():
        with open(path, "a", encoding="utf-8") as f:
            f.write(("" if not existing or existing.endswith("\n") else "\n") + line + "\n")
    if os.name == "posix":
        os.chmod(path, 0o600)


# Create or reuse a simulation key in an identity folder; enroll it additively there only
def ensure_identity_at(identity_root: Any) -> Dict[str, Any]:
    """Return {'key', 'fingerprint', 'created', 'layout'} for the simulation identity in identity_root."""
    layout = IdentityLayout(root=Path(identity_root))
    for directory in (layout.root, layout.challenge_dir):
        directory.mkdir(parents=True, exist_ok=True)
        if os.name == "posix":
            os.chmod(directory, 0o700)
    key = layout.root / SIMULATION_KEY_NAME
    created = False
    if not key.exists():
        subprocess.run(
            ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "agentic-os-simulation", "-f", str(key)],
            check=True, capture_output=True,
        )
        created = True
    key_type, key_b64 = Path(str(key) + ".pub").read_text(encoding="utf-8").split()[:2]
    for path, namespace in ((layout.allowed_signers, SIGN_NAMESPACE), (layout.allowed_signers_selftest, SELFTEST_NAMESPACE)):
        _append_line(path, f'{AGENT_SIMULATION_PRINCIPAL} namespaces="{namespace}" {key_type} {key_b64}')
    return {"key": key, "fingerprint": key_fingerprint(key_b64), "created": created, "layout": layout}


# The repository's simulation identity: <repo>/context/simulation/identity
def ensure_simulation_identity(repo_root: Any) -> Dict[str, Any]:
    """Create or reuse the repository's simulation key; never writes the production trust file."""
    return ensure_identity_at(simulation_layout(repo_root).root)


# Keys registered as simulation keys for the repository that owns a database
def simulation_key_fingerprints(repo_root: Any) -> Set[str]:
    """Return the fingerprints enrolled in <repo>/context/simulation/identity/allowed_signers."""
    anchor = simulation_layout(repo_root).allowed_signers
    if not anchor.exists():
        return set()
    return {k.fingerprint for k in enrolled_keys(anchor)}


def _isolation_status() -> Dict[str, Any]:
    """Report whether the agent runs as its own OS account (per platform), with the human's setup commands."""
    from control_plane.identity_setup import privileged_account_commands
    from control_plane.isolation_check import DEFAULT_AGENT_NAME, _resolve_agent_identity

    if sys.platform.startswith("win"):
        return {
            "ready": False,
            "detail": "Windows: account and folder-permission isolation is not auto-detected. Run the agent as a separate "
                      "account and deny it write access to context/identity (see references/isolation-setup.md).",
            "commands": privileged_account_commands(),
        }
    uid, _ = _resolve_agent_identity(DEFAULT_AGENT_NAME, None, None)
    if uid is None:
        return {
            "ready": False,
            "detail": f"No '{DEFAULT_AGENT_NAME}' account: the agent runs as you and could edit your trust files. "
                      "Separation of approvals is enforced for normal use, not against a hostile agent, until you create it.",
            "commands": privileged_account_commands(),
        }
    if uid == os.geteuid():
        return {"ready": False, "detail": f"This process runs as the agent account '{DEFAULT_AGENT_NAME}'; run the status as yourself.", "commands": []}
    return {
        "ready": False,
        "account_present": True,
        "detail": f"Agent account '{DEFAULT_AGENT_NAME}' exists (uid {uid}), but account existence does not "
                  "verify the agent runtime or protected-file permissions. Confirm the agent actually runs under "
                  "that account and run the human signing isolation preflight before claiming isolation.",
        "commands": [],
    }


# Human approval / simulation / isolation readiness, never collapsed into one "ready"
def dual_identity_status(repo_root: Any) -> Dict[str, Dict[str, Any]]:
    """Return {'human', 'simulation', 'isolation'} readiness for a repository. Never writes."""
    production = default_layout(repo_root).allowed_signers
    human_keys = [k for k in enrolled_keys(production) if AGENT_SIMULATION_PRINCIPAL not in k.principals] if production.exists() else []
    sim_prints = simulation_key_fingerprints(repo_root)
    relabelled = sorted(k.fingerprint for k in human_keys if k.fingerprint in sim_prints)
    human = {
        "ready": bool(human_keys) and not relabelled,
        "keys": [k.fingerprint for k in human_keys],
        "detail": ("Relabelled simulation key(s) found in the production trust file: " + ", ".join(relabelled)) if relabelled
        else ("Human key(s) enrolled." if human_keys else "No human key enrolled: the human runs setup_ciba_identity.py."),
    }
    sim_key = simulation_layout(repo_root).root / SIMULATION_KEY_NAME
    simulation = {
        "ready": sim_key.exists() and bool(sim_prints),
        "keys": sorted(sim_prints),
        "database": str(simulation_db_path(repo_root)),
        "detail": "Simulation identity ready." if sim_key.exists() and sim_prints else "No simulation identity yet (os-init creates it).",
    }
    return {"human": human, "simulation": simulation, "isolation": _isolation_status()}


class SimulationSigner:
    """Signs a simulation database's cryptographic gates with the simulation key kept next to it
    (<db dir>/identity; for <repo>/context/simulation/simulation_control_plane.db that is the
    repository's simulation identity). That trust file is the agent's own by design, so the
    human-anchor isolation preflight does not apply to it; it never touches the human's identity."""

    def __init__(self, identity_root: Path) -> None:
        """Use the simulation identity kept in `identity_root` (created on first use)."""
        self.identity_root = Path(identity_root)

    def __call__(self, cp: Any, request_id: int) -> Any:
        """Sign and commit one pending gate request with the simulation key; return the TransitionRecord."""
        import io

        from control_plane.gate1_approval import approve_transition, show_challenge
        from control_plane.ssh_signing import sign_command

        identity = ensure_identity_at(self.identity_root)
        layout = identity["layout"]
        uid = os.geteuid() if hasattr(os, "geteuid") else 0
        not_this_process = {"agent_name": "agentic-os-simulation-none", "agent_uid": uid + 4242, "agent_gids": set()}
        challenge = show_challenge(cp, request_id, layout=layout, key_hint=str(identity["key"]), agent_identity=not_this_process, out=io.StringIO())
        sig = Path(str(challenge) + ".sig")
        if sig.exists():
            sig.unlink()
        subprocess.run(sign_command(str(identity["key"]), challenge), check=True, capture_output=True)
        return approve_transition(cp, request_id, layout=layout, principal=AGENT_SIMULATION_PRINCIPAL, agent_identity=not_this_process, out=io.StringIO())
