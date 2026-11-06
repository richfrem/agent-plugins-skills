"""Two related tasks in a non-Sanctuary repo through the real loop: work_loop -> run_agent (real subprocess) -> outcome_eval -> lessons.
MOCKED: the worker backend is a fixture executable, not a model. Asserts over the action trace and file state, not stated intent."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

S = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(S / "orchestrating-agent-work/scripts"))
sys.path.insert(0, str(S / "evaluating-agent-outcomes/scripts"))
import work_loop as wl, lessons as L, eval_core as core


def make_worker(d):
    p = Path(d) / "claude"
    p.write_text(f'#!{sys.executable}\nimport sys,re\nif "--version" in sys.argv:\n print("fixture 1");sys.exit(0)\n'
                 'm=re.search(r"CREATE:(\\S+)", " ".join(sys.argv))\nif m: open(m.group(1),"w").write("print(\'hello\')\\n")\nprint("done")\n')
    p.chmod(0o755)
    return p


def contract(wid, fname, goal):
    return {"id": wid, "type": "task", "goal": goal, "scope": {"paths": [fname]},
            "acceptance": [{"id": "A1", "text": "script prints hello", "check": {"kind": "command", "argv": [sys.executable, fname], "expect_stdout_contains": ["hello"]}}],
            "failure_conditions": [{"id": "F1", "text": "error marker", "check": {"kind": "file_exists", "path": "ERROR.txt"}}],
            "budget": {"max_attempts": 3}, "authorization": {"may_merge": False}}


class E2E(unittest.TestCase):
    def test_two_related_tasks_learning_loop(self):
        repo = Path(tempfile.mkdtemp()); subprocess.run(["git", "init", "-q", str(repo)])
        tools = Path(tempfile.mkdtemp()); worker = make_worker(tools)
        good_path = str(tools) + os.pathsep + os.environ["PATH"]
        bad_path = str(Path(tempfile.mkdtemp()))                     # injected failure: worker env lacks the executable
        env_py = os.path.dirname(sys.executable)

        # ---- task 1
        c1 = repo / "c1.json"; c1.write_text(json.dumps(contract("t1", "hello.py", "create hello script with the claude worker")))
        self.assertTrue(wl.start(c1, repo)["ok"])
        r = wl.dispatch("t1", "u1", "orch", "claude", bad_path, "CREATE:hello.py", repo, repo)
        self.assertEqual(r["status"], "refused")                       # detected by the executor path, before any launch
        f = wl.evaluate("t1", repo)
        self.assertEqual(f["recommended"], "repair"); self.assertEqual(f["incomplete"], ["A1"])   # worker exit is not completion
        r = wl.dispatch("t1", "u1", "orch", "claude", good_path, "CREATE:hello.py", repo, repo, executable=str(worker))
        self.assertTrue(r["ok"], r)
        f = wl.evaluate("t1", repo)
        self.assertTrue(f["complete"]); self.assertEqual(f["recommended"], "accept"); self.assertFalse(f["integration_allowed"])
        self.assertIsNone(f["usage"]["total_tokens"])                  # fixture reports none: unknown, not zero
        lesson = L.add("worker PATH lacks the claude executable at launch", "dispatch refused: executable unavailable in worker environment",
                       "trace t1: exec_check ok=false", "run exec-check on the worker PATH first; pass the explicit executable path",
                       "e2e test task 2", "applies to CLI backends launched with a restricted PATH", cause_status="known", tags=["claude", "path", "executable"], root=repo)
        core.record_repair("worker_env_executable", "trace t1", "explicit executable", "e2e", "test", root=repo)

        # ---- task 2 (related): lesson retrieved BEFORE dispatch and applied
        c2 = repo / "c2.json"; c2.write_text(json.dumps(contract("t2", "greet.py", "create greet script, launching the claude worker from a restricted PATH")))
        plan = wl.start(c2, repo)["plan"]
        self.assertEqual([l["id"] for l in plan["lessons"]], [lesson["id"]])
        r = wl.dispatch("t2", "u2", "orch", "claude", bad_path, "CREATE:greet.py", repo, repo, executable=str(worker))   # lesson applied
        self.assertTrue(r["ok"], r)
        f = wl.evaluate("t2", repo); self.assertEqual(f["recommended"], "accept")
        L.use(lesson["id"], "t2", "helped", root=repo); core.record_application("worker_env_executable", "prevented", "t2", root=repo)
        tr = [t["action"] for t in wl.read_trace(repo, "t2")]
        self.assertLess(tr.index("lessons_retrieved"), tr.index("dispatch"))
        self.assertNotIn("dispatch_refused", tr)
        self.assertEqual(L.stats(repo)[lesson["id"]]["helped"], 1)
        self.assertEqual(core.repair_report(repo)["worker_env_executable"]["recurrence_rate"], 0.0)
        # records stayed inside the repo root
        for p in (repo / ".agent-work").rglob("*"):
            self.assertTrue(str(p.resolve()).startswith(str(repo.resolve())))

    def test_duplicate_unit_not_launched(self):
        repo = Path(tempfile.mkdtemp()); tools = Path(tempfile.mkdtemp()); worker = make_worker(tools)
        c = repo / "c.json"; c.write_text(json.dumps(contract("t3", "hello.py", "x"))); wl.start(c, repo)
        guard = wl._import("cli-agent", "dispatch_guard")
        self.assertTrue(guard.claim(repo / ".agent-work/t3/claims", "u9", "someone-else")["ok"])
        r = wl.dispatch("t3", "u9", "orch", "claude", str(tools), "CREATE:hello.py", repo, repo, executable=str(worker))
        self.assertEqual(r["status"], "refused"); self.assertFalse((repo / "hello.py").exists())


if __name__ == "__main__":
    unittest.main()
