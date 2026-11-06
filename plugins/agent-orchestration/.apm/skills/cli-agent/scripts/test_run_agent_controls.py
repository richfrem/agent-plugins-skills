"""Launch controls enforced in run_agent.py's own path (real child processes, fixture backend; no model is called)."""
import json, os, subprocess, sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("run_agent.py")


def fake(tmp_path, name="claude", body=""):
    p = tmp_path / name
    p.write_text(f'#!{sys.executable}\nimport sys,json,os\nif "--version" in sys.argv:\n print("fixture 1.0");sys.exit(0)\n{body}\nprint(json.dumps({{"argv":sys.argv[1:],"cwd":os.getcwd()}}))\n')
    p.chmod(0o755)
    return p


def run(tmp_path, *extra, path_dirs=None):
    src = tmp_path / "src.md"; src.write_text("x")
    out = tmp_path / "out.md"
    pd = path_dirs if path_dirs is not None else [str(tmp_path)]
    env = {**os.environ, "PATH": os.pathsep.join(pd + [os.environ["PATH"]])}
    r = subprocess.run([sys.executable, str(SCRIPT), "/dev/null", str(src), str(out), "do it", "--cli", "claude",
                        "--model", "m", "--require-input", *extra], env=env, capture_output=True, text=True)
    return r, out


def result_of(tmp_path):
    return json.loads((tmp_path / "res.json").read_text())


def test_result_json_records_execution_and_usage_unknown(tmp_path):
    fake(tmp_path)
    r, _ = run(tmp_path, "--result-json", str(tmp_path / "res.json"), "--isolated")
    assert r.returncode == 0, r.stdout + r.stderr
    res = result_of(tmp_path)
    assert res["status"] == "ok" and res["backend"] == "claude" and res["version"] == "fixture 1.0"
    assert res["usage"]["total_tokens"] is None          # unknown, never zero
    assert "instructed_only" in res and res["enforced_by_code"] == []


def test_cwd_boundary_refuses_before_launch(tmp_path):
    marker = tmp_path / "launched"
    fake(tmp_path, body=f'open({str(marker)!r},"w").write("1")')
    root = tmp_path / "root"; root.mkdir()
    r, _ = run(tmp_path, "--cwd", str(tmp_path), "--allowed-root", str(root), "--result-json", str(tmp_path / "res.json"))
    assert r.returncode == 2 and not marker.exists()
    res = result_of(tmp_path)
    assert res["status"] == "refused" and "cwd_boundary" in res["enforced_by_code"]


def test_cwd_inside_root_runs_there(tmp_path):
    fake(tmp_path)
    wt = tmp_path / "wt"; wt.mkdir()
    r, out = run(tmp_path, "--cwd", str(wt), "--allowed-root", str(tmp_path), "--isolated")
    assert r.returncode == 0, r.stdout + r.stderr
    assert json.loads(out.read_text().splitlines()[-1])["cwd"] == str(wt.resolve())


def test_duplicate_unit_refused_and_claim_released(tmp_path):
    marker = tmp_path / "launched"
    fake(tmp_path, body=f'open({str(marker)!r},"w").write("1")')
    claims = tmp_path / "claims"
    from importlib import import_module
    sys.path.insert(0, str(SCRIPT.parent)); g = import_module("dispatch_guard")
    assert g.claim(claims, "u1", "other-worker")["ok"]
    r, _ = run(tmp_path, "--claim-dir", str(claims), "--unit", "u1", "--owner", "me", "--result-json", str(tmp_path / "res.json"))
    assert r.returncode == 2 and not marker.exists()
    g.release(claims, "u1", "other-worker")
    r, _ = run(tmp_path, "--claim-dir", str(claims), "--unit", "u1", "--owner", "me", "--isolated")
    assert r.returncode == 0
    assert g.claim(claims, "u1", "third")["ok"]            # released after the run


def test_missing_executable_fails_with_structured_result(tmp_path):
    r, _ = run(tmp_path, "--result-json", str(tmp_path / "res.json"), path_dirs=[str(tmp_path / "empty")])
    res = result_of(tmp_path)
    assert r.returncode != 0 and res["status"] in ("failed", "refused")


def test_clean_context_adds_flags_and_neutral_cwd(tmp_path):
    fake(tmp_path)
    r, out = run(tmp_path, "--clean-context", "--result-json", str(tmp_path / "res.json"))
    assert r.returncode == 0, r.stdout + r.stderr
    j = json.loads(out.read_text().splitlines()[-1])
    assert "--setting-sources" in j["argv"] and "--disable-slash-commands" in j["argv"] and "--dangerously-skip-permissions" not in j["argv"]
    assert Path(j["cwd"]).name.startswith("clean-ctx-")
    assert any("not probed" in x for x in result_of(tmp_path)["limitations"])


def test_clean_context_refused_for_other_backends(tmp_path):
    src = tmp_path / "s"; src.write_text("x")
    r = subprocess.run([sys.executable, str(SCRIPT), "/dev/null", str(src), str(tmp_path / "o"), "i", "--cli", "codex", "--clean-context"],
                       capture_output=True, text=True)
    assert r.returncode == 2


def test_timeout_kills_streaming_backend(tmp_path):
    fake(tmp_path, name="agy", body="import time; time.sleep(30)")
    src = tmp_path / "s"; src.write_text("x")
    env = {**os.environ, "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"]}
    r = subprocess.run([sys.executable, str(SCRIPT), "/dev/null", str(src), str(tmp_path / "o"), "i", "--cli", "agy", "--model", "m",
                        "--timeout", "1", "--result-json", str(tmp_path / "res.json"), "--isolated"], env=env, capture_output=True, text=True, timeout=20)
    assert r.returncode != 0
