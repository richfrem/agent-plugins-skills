"""
control_plane package — hexagonal decomposition of agent_control.py's ControlPlane (issue-524)
================================================================================================

Purpose:
    Home for the ports/adapters/domain/application layers extracted from the original
    monolithic ControlPlane class. agent_control.py's ControlPlane remains the public,
    backward-compatible facade (per the human-approved decision in docs/plans/issue-524-spec.md,
    Section 3) and composes these layers internally; external callers (CLI, init_agentic_os.py,
    tests) are unaffected.

Layer:
    OS Kernel / Execution Control Plane Substrate (sub-package)

Key Input Dependencies:
    None directly — submodules declare their own.

Key Functions:
    (re-exported from submodules as they are added in subsequent steps)
"""
