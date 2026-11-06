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


def test_crash_before_launch_records_failed_not_ok(tmp_path):
    src = tmp_path / "s"; src.write_text("")
    r = subprocess.run([sys.executable, str(SCRIPT), "/dev/null", str(src), str(tmp_path / "o"), "i", "--cli", "claude", "--require-input",
                        "--result-json", str(tmp_path / "res.json")], capture_output=True, text=True)
    assert r.returncode != 0 and json.loads((tmp_path / "res.json").read_text())["status"] == "failed"


def test_nonpositive_timeout_rejected(tmp_path):
    fake(tmp_path)
    r, _ = run(tmp_path, "--timeout", "0", "--isolated")
    assert r.returncode != 0


def test_clean_context_refused_with_non_claude_fallback(tmp_path):
    fake(tmp_path)
    r, _ = run(tmp_path, "--clean-context", "--fallback-chain", "codex")
    assert r.returncode == 2


def test_claim_released_on_sigterm(tmp_path):
    import signal, time
    fake(tmp_path, name="agy", body="import time; time.sleep(30)")
    src = tmp_path / "s"; src.write_text("x"); claims = tmp_path / "claims"
    env = {**os.environ, "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"]}
    p = subprocess.Popen([sys.executable, str(SCRIPT), "/dev/null", str(src), str(tmp_path / "o"), "i", "--cli", "agy", "--model", "m", "--isolated",
                          "--claim-dir", str(claims), "--unit", "u", "--owner", "me", "--result-json", str(tmp_path / "res.json")], env=env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        if list(claims.glob("*.owner")): break
        time.sleep(0.1)
    p.send_signal(signal.SIGTERM); p.wait(timeout=20)
    assert not list(claims.glob("*.owner")) and (tmp_path / "res.json").exists()


# ---------------------------------------------------------------- MISSION-055 hardening: process-group cleanup, attempts, claim ownership
CHILD_BODY = ("import subprocess, time, sys\n"
              "c = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
              "open(os.environ.get('CHILD_PID_FILE', '/dev/null'), 'w').write(str(c.pid))\n"
              "print('partial-output-marker', flush=True)\n"
              "time.sleep(60)")


def _alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def _timeout_case(tmp_path, backend_name):
    import time
    fake(tmp_path, name=backend_name, body=CHILD_BODY)
    src = tmp_path / "s"; src.write_text("x"); claims = tmp_path / "claims"
    pidf = tmp_path / "child.pid"
    env = {**os.environ, "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"], "CHILD_PID_FILE": str(pidf)}
    t0 = time.time()
    r = subprocess.run([sys.executable, str(SCRIPT), "/dev/null", str(src), str(tmp_path / "out"), "i", "--cli", backend_name, "--model", "m",
                        "--isolated", "--timeout", "2", "--claim-dir", str(claims), "--unit", "u", "--owner", "me",
                        "--result-json", str(tmp_path / "res.json")], env=env, capture_output=True, text=True, timeout=60)
    return r, time.time() - t0, pidf, claims


def test_timeout_kills_worker_and_child_non_streaming_before_release(tmp_path):
    r, took, pidf, claims = _timeout_case(tmp_path, "claude")             # claude uses communicate()
    res = result_of(tmp_path)
    assert r.returncode != 0 and res["status"] == "timeout" and res["cleanup_confirmed"] is True
    assert not _alive(int(pidf.read_text()))                              # grandchild is gone by the time the run returns
    assert not list(claims.glob("*.owner"))                               # claim released only after cleanup
    assert "partial-output-marker" in (tmp_path / "out").read_text()      # partial output preserved
    assert res["attempts"][0]["status"] == "timeout" and res["attempts"][0]["cleanup"]["confirmed"] is True
    assert took < 30


def test_timeout_kills_worker_and_child_streaming(tmp_path):
    r, took, pidf, claims = _timeout_case(tmp_path, "agy")
    res = result_of(tmp_path)
    assert res["status"] == "timeout" and not _alive(int(pidf.read_text())) and not list(claims.glob("*.owner"))
    assert "partial-output-marker" in (tmp_path / "out").read_text()


def test_attempt_records_each_fallback_backend(tmp_path):
    fake(tmp_path, name="claude", body="print('quota exceeded: rate limit'); sys.exit(1)")
    fake(tmp_path, name="agy")
    src = tmp_path / "s"; src.write_text("x")
    env = {**os.environ, "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"]}
    r = subprocess.run([sys.executable, str(SCRIPT), "/dev/null", str(src), str(tmp_path / "o"), "i", "--cli", "claude", "--model", "m", "--isolated",
                        "--fallback-chain", "agy", "--result-json", str(tmp_path / "res.json")], env=env, capture_output=True, text=True)
    res = result_of(tmp_path)
    assert [a["backend"] for a in res["attempts"]] == ["claude", "agy"] and [a["status"] for a in res["attempts"]] == ["failed", "ok"]
    assert all(a["usage"]["total_tokens"] is None for a in res["attempts"])      # unknown stays unknown


def test_caller_held_claim_is_verified_not_released_and_wrong_token_refused(tmp_path):
    fake(tmp_path)
    sys.path.insert(0, str(SCRIPT.parent)); import dispatch_guard as g
    claims = tmp_path / "claims"; c = g.claim(claims, "u", "loop")
    r, _ = run(tmp_path, "--claim-dir", str(claims), "--unit", "u", "--owner", "loop", "--claim-token", c["token"], "--isolated",
               "--result-json", str(tmp_path / "res.json"))
    assert r.returncode == 0 and result_of(tmp_path)["claim_mode"] == "caller-held (verified)"
    assert g.verify_claim(claims, "u", c["token"])                         # executor did not release the caller's claim
    r, _ = run(tmp_path, "--claim-dir", str(claims), "--unit", "u", "--owner", "loop", "--claim-token", "forged", "--isolated",
               "--result-json", str(tmp_path / "res2.json"))
    assert r.returncode == 2
    assert g.verify_claim(claims, "u", c["token"])                         # refused run left the active claim untouched
    assert not g.release(claims, "u", token="forged")["ok"] and g.release(claims, "u", token=c["token"])["released"]


def test_failed_fallback_after_timeout_reports_failed_not_timeout(tmp_path):
    fake(tmp_path, name="claude", body="import time; time.sleep(60)")
    fake(tmp_path, name="agy", body="sys.exit(3)")
    src = tmp_path / "s"; src.write_text("x")
    env = {**os.environ, "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"]}
    subprocess.run([sys.executable, str(SCRIPT), "/dev/null", str(src), str(tmp_path / "o"), "i", "--cli", "claude", "--model", "m", "--isolated", "--timeout", "1",
                    "--fallback-chain", "agy", "--result-json", str(tmp_path / "res.json")], env=env, capture_output=True, text=True, timeout=60)
    res = result_of(tmp_path)
    assert [a["status"] for a in res["attempts"]] == ["timeout", "failed"] and res["status"] == "failed"
