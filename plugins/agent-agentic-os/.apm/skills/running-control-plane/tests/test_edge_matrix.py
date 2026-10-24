"""
test_edge_matrix.py
===================

Purpose:
    Contract tests for control_plane/edge_matrix.py: classify every transition edge
    in the live registry by WHO runs it (agent / soft: human approves in chat then
    agent runs / hard: agent cannot run), with a plain reason. Task T0b of
    start-here-cleanup; human's three-class taxonomy (requirements ledger item 19).

Key Input Dependencies:
    - control_plane/transition_templates.yaml (via TransitionRegistry, real file, no mocks)

Index:
    - test_one_row_per_registry_edge
    - test_crypto_rows_equal_registry_proof_edges
    - test_crypto_rows_only_target_the_three_signed_gates
    - test_class_rules_follow_registry_fields
    - test_markdown_lists_every_edge_with_plain_class_words
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.registry import TransitionRegistry
from control_plane.edge_matrix import build_edge_matrix, render_markdown, AGENT, SOFT, HARD

SIGNED_GATE_TARGETS = {"APPROVED", "VERIFY_EXIT", "DONE"}


def _rows():
    return build_edge_matrix(TransitionRegistry.load_default())


def test_one_row_per_registry_edge():
    registry = TransitionRegistry.load_default()
    rows = build_edge_matrix(registry)
    assert len(rows) == len(registry.get_all_templates())
    assert {r["transition_id"] for r in rows} == {t.transition_id for t in registry.get_all_templates()}


def test_crypto_rows_equal_registry_proof_edges():
    registry = TransitionRegistry.load_default()
    proof_edges = {(row[0], row[1]) for row in registry.get_all_edges_with_proof() if row[3]}
    crypto_rows = {(r["from_state"], r["to_state"]) for r in build_edge_matrix(registry) if r["basis"] == "crypto"}
    assert crypto_rows == proof_edges
    assert crypto_rows


def test_crypto_rows_only_target_the_three_signed_gates():
    for row in _rows():
        if row["basis"] == "crypto":
            assert row["run_by"] == HARD
            assert row["to_state"] in SIGNED_GATE_TARGETS


def test_class_rules_follow_registry_fields():
    registry = TransitionRegistry.load_default()
    by_id = {t.transition_id: t for t in registry.get_all_templates()}
    for row in build_edge_matrix(registry):
        template = by_id[row["transition_id"]]
        assert row["run_by"] in (AGENT, SOFT, HARD)
        if template.requires_cryptographic_proof:
            assert (row["run_by"], row["basis"]) == (HARD, "crypto")
        elif template.authorized_actor == "human_only":
            assert (row["run_by"], row["basis"]) == (HARD, "policy")
        elif template.human_questions:
            assert (row["run_by"], row["basis"]) == (SOFT, "none")
        else:
            assert (row["run_by"], row["basis"]) == (AGENT, "none")
        assert row["why"].strip()


def test_markdown_lists_every_edge_with_plain_class_words():
    rows = _rows()
    text = render_markdown(rows)
    for row in rows:
        assert row["transition_id"] in text
    assert "You (the agent) run this" in text
    assert "Ask the human in chat, then you run this" in text
    assert "Only the human can run this" in text
