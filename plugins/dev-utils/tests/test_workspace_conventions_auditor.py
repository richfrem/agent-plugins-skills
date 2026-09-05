"""
test_workspace_conventions_auditor.py
=====================================

Purpose:
    Verifies the two-tier length + McCabe complexity model in
    workspace_conventions_auditor.py (coding-conventions.md SS5, revised
    2026-09-05, DEBT-20260905-08): length soft/hard ceilings, complexity
    soft/hard ceilings, and structural exemptions (argparse, dict/mapping
    literals, match/case, string templates) from the length ceiling only.

Key Input Dependencies:
    - ../scripts/workspace_conventions_auditor.py (module under test)
"""

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import workspace_conventions_auditor as wca  # noqa: E402


def _parse_func(src: str) -> ast.FunctionDef:
    """Parse src and return its single top-level FunctionDef node."""
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            return node
    raise AssertionError("No top-level function found in source")


def test_short_simple_function_is_clean():
    """A short function with no branching must produce no findings."""
    src = "def f(x):\n" + "\n".join(f"    y{i} = {i}" for i in range(10)) + "\n    return x\n"
    node = _parse_func(src)
    assert wca._check_function_length_and_complexity(node) == []


def test_length_soft_threshold_warns_not_errors():
    """A function between 50 and 100 lines with low complexity must WARN, not ERROR."""
    src = "def f(x):\n" + "\n".join(f"    y{i} = {i}" for i in range(60)) + "\n    return x\n"
    node = _parse_func(src)
    findings = wca._check_function_length_and_complexity(node)
    assert any("[WARNING]" in f and "50-line" in f for f in findings)
    assert not any("[ERROR]" in f for f in findings)


def test_length_hard_ceiling_errors():
    """A function over 100 lines must ERROR regardless of complexity."""
    src = "def f(x):\n" + "\n".join(f"    y{i} = {i}" for i in range(110)) + "\n    return x\n"
    node = _parse_func(src)
    findings = wca._check_function_length_and_complexity(node)
    assert any("[ERROR]" in f and "100-line" in f for f in findings)


def test_high_mccabe_errors_even_when_short():
    """A short function with McCabe >= 15 must ERROR on complexity."""
    conditions = "\n".join(f"    if x == {i}:\n        return {i}" for i in range(15))
    src = f"def f(x):\n{conditions}\n    return -1\n"
    node = _parse_func(src)
    findings = wca._check_function_length_and_complexity(node)
    assert any("[ERROR]" in f and "McCabe" in f for f in findings)


def test_argparse_block_exempt_from_length_ceiling():
    """A function dominated by argparse add_argument calls must be exempt from length, not complexity."""
    lines = "\n".join(f'    parser.add_argument("--opt{i}")' for i in range(60))
    src = f"def main():\n    parser = argparse.ArgumentParser()\n{lines}\n    return parser\n"
    node = _parse_func(src)
    findings = wca._check_function_length_and_complexity(node)
    assert findings == []


def test_dict_literal_dominant_function_exempt_from_length_ceiling():
    """A function whose body is a single large dict return must be exempt from length."""
    entries = ",\n".join(f'        "key{i}": {i}' for i in range(60))
    src = f"def get_config():\n    return {{\n{entries}\n    }}\n"
    node = _parse_func(src)
    findings = wca._check_function_length_and_complexity(node)
    assert findings == []


def test_transactional_high_complexity_not_exempt_by_subject_matter():
    """A long, branchy function must ERROR even if it looks like transactional state-machine code."""
    branches = "\n".join(
        f'    if state == "S{i}":\n        state = "S{i+1}"\n    elif state == "T{i}":\n        raise ValueError(state)'
        for i in range(20)
    )
    src = f"def transition(state):\n{branches}\n    return state\n"
    node = _parse_func(src)
    findings = wca._check_function_length_and_complexity(node)
    assert any("[ERROR]" in f and "McCabe" in f for f in findings)


def test_pass_fail_ignores_warning_only_findings():
    """_audit_file must not count a file toward failed stats when only WARNINGs are present."""
    import tempfile
    src = '"""\nPurpose:\n    x\nKey Input Dependencies:\n    x\n"""\n'
    src += "def f(x):\n"
    src += '    """A trivial docstring."""\n'
    src += "\n".join(f"    y{i} = {i}" for i in range(60))
    src += "\n    return x\n"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "plugins").mkdir()
        f = tmp_path / "plugins" / "sample.py"
        f.write_text(src, encoding="utf-8")
        orig_root = wca.WORKSPACE_ROOT
        wca.WORKSPACE_ROOT = tmp_path
        try:
            results = {"py": [], "ts": [], "tsx": [], "js": []}
            scanned, failed, uniq_scan, uniq_fail = set(), set(), set(), set()
            _, hard_failed = wca._audit_file(f, results, scanned, failed, uniq_scan, uniq_fail)
            assert hard_failed == 0
            assert len(uniq_fail) == 0
            assert len(results["py"]) == 1  # still visible in the report
        finally:
            wca.WORKSPACE_ROOT = orig_root
