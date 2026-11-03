"""Tests for the hf_upload.py command line (managing-huggingface-assets).

Purpose: verify the documented CLI (--file/--folder/--remote-path/--dry-run) without network access or credentials.
Key Input Dependencies: pytest; the hf_upload module under .apm/skills/managing-huggingface-assets/scripts.
Key Functions: test_requires_file_or_folder, test_dry_run_needs_no_credentials, test_rejects_parent_segments,
    test_missing_file_fails, test_upload_failure_exit_code, test_default_remote_path_is_file_name, test_folder_upload_routes
Usage: python3 -m pytest plugins/dev-utils/tests/test_hf_upload_cli.py
"""
import asyncio
import importlib
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / ".apm" / "skills" / "managing-huggingface-assets" / "scripts"
sys.path.insert(0, str(SCRIPTS))
hf_upload = importlib.import_module("hf_upload")
HFUploadResult = hf_upload.HFUploadResult


@pytest.fixture(autouse=True)
def no_credentials(monkeypatch):
    for key in ("HUGGING_FACE_USERNAME", "HUGGING_FACE_TOKEN", "HUGGING_FACE_REPO", "HUGGING_FACE_DATASET_PATH"):
        monkeypatch.delenv(key, raising=False)


def _fake(calls, ok=True):
    async def fake(path, remote, config=None, commit_msg=None):
        calls.append((Path(path), remote, commit_msg))
        return HFUploadResult(ok, "https://huggingface.co/datasets/x/y" if ok else "", remote if ok else "", None if ok else "boom")
    return fake


def test_requires_file_or_folder():
    with pytest.raises(SystemExit) as exc:
        hf_upload.main([])
    assert exc.value.code == 2


def test_file_and_folder_are_mutually_exclusive(tmp_path):
    with pytest.raises(SystemExit) as exc:
        hf_upload.main(["--file", str(tmp_path / "a"), "--folder", str(tmp_path)])
    assert exc.value.code == 2


def test_dry_run_needs_no_credentials(tmp_path, capsys, monkeypatch):
    f = tmp_path / "x.md"
    f.write_text("hi")
    monkeypatch.setattr(hf_upload, "upload_file", lambda *a, **k: pytest.fail("dry-run must not upload"))
    assert hf_upload.main(["--file", str(f), "--remote-path", "lineage/x.md", "--dry-run"]) == 0
    assert "lineage/x.md" in capsys.readouterr().out


def test_rejects_parent_segments(tmp_path, capsys):
    f = tmp_path / "x.md"
    f.write_text("hi")
    assert hf_upload.main(["--file", str(f), "--remote-path", "../escape.md", "--dry-run"]) == 1
    assert ".." in capsys.readouterr().err


def test_missing_file_fails(tmp_path, capsys):
    assert hf_upload.main(["--file", str(tmp_path / "nope.md")]) == 1
    assert "not a file" in capsys.readouterr().err


def test_default_remote_path_is_file_name(tmp_path, monkeypatch):
    f = tmp_path / "report.md"
    f.write_text("hi")
    calls = []
    monkeypatch.setattr(hf_upload, "upload_file", _fake(calls))
    assert hf_upload.main(["--file", str(f), "--commit-message", "msg"]) == 0
    assert calls == [(f, "report.md", "msg")]


def test_upload_failure_exit_code(tmp_path, monkeypatch, capsys):
    f = tmp_path / "x.md"
    f.write_text("hi")
    monkeypatch.setattr(hf_upload, "upload_file", _fake([], ok=False))
    assert hf_upload.main(["--file", str(f)]) == 1
    assert "boom" in capsys.readouterr().err


def test_folder_upload_routes(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(hf_upload, "upload_folder", _fake(calls))
    assert hf_upload.main(["--folder", str(tmp_path), "--remote-path", "/data/"]) == 0
    assert calls == [(tmp_path, "data/", None)]
