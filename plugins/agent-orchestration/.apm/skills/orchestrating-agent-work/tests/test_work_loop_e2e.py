"""Two related tasks in a non-Sanctuary repo through the real loop. MOCKED: the worker (a fixture executable). REAL: run_agent.py subprocesses,
claims, ledger, assessment, lessons. Asserts over action traces and state, not stated intent."""
import json, os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _loop_fixtures import *  # noqa
import lessons as L, eval_core as core


class E2E(unittest.TestCase):
    def test_two_related_tasks_learning_loop(self):
        repo, tools, worker = make_repo()
        bad_path = tempfile.mkdtemp()                         # injected failure: the worker environment lacks the executable
        # task 1: first dispatch refused by the worker-environment preflight, repaired by supplying the explicit executable
        p1 = put(repo, contract("t1", goal="create hello script with the claude worker"), "c1.json")
        self.assertTrue(wl.start(p1, repo)["ok"])
        r = wl.dispatch("t1", "u1", "orch", "claude", bad_path, "CREATE:hello.py", repo, repo)
        self.assertEqual(r["status"], "refused")
        f = wl.evaluate("t1", repo)
        self.assertEqual((f["recommended"], f["incomplete"]), ("repair", ["A1"]))          # worker refusal is not completion
        r = wl.dispatch("t1", "u1", "orch", "claude", bad_path, "CREATE:hello.py", repo, repo, executable=str(worker))
        self.assertTrue(r["ok"], r)
        f = wl.evaluate("t1", repo)
        self.assertEqual((f["complete"], f["recommended"], f["integration_allowed"]), (True, "accept", False))
        self.assertEqual(f["accounting"]["preflight_refusals"], 1)                           # refusal kept apart from executions
        self.assertEqual(f["accounting"]["execution_attempts"], 1)
        self.assertIsNone(f["usage"]["total_tokens"])                                        # fixture reports none: unknown, not zero
        lesson = L.add("worker PATH lacks the claude executable at launch", "dispatch refused: executable unavailable in worker environment",
                       "trace t1: exec_check ok=false", "pass the explicit executable path", "e2e", "restricted PATH launches", cause_status="known",
                       tags=["claude", "path", "executable"], root=repo)
        core.record_repair("worker_env_executable", "trace t1", "explicit executable", "e2e", "test", root=repo)
        # task 2: lesson is retrieved AND placed in the worker brief; usefulness is recorded only from observed evidence
        p2 = put(repo, contract("t2", "greet.py", "create greet script, launching the claude worker from a restricted PATH"), "c2.json")
        plan = wl.start(p2, repo)["plan"]
        self.assertEqual([l["id"] for l in plan["lessons"]], [lesson["id"]])
        r = wl.dispatch("t2", "u2", "orch", "claude", bad_path, "CREATE:greet.py", repo, repo, executable=str(worker), lessons_supplied=plan["lessons"])
        self.assertTrue(r["ok"], r)
        brief = (repo / ".agent-work/t2/attempts" / r["attempt_id"] / "input.md").read_text()
        self.assertIn(lesson["id"], brief); self.assertIn("fallible guidance", brief); self.assertIn("NEVER override", brief)
        self.assertEqual(L.stats(repo)[lesson["id"]]["helped"], 0)                           # retrieval/supply alone is not "helped"
        wl.evaluate("t2", repo)
        wl.observe_lessons("t2", {lesson["id"]: "helped"}, [r["attempt_id"]], repo)
        self.assertEqual(L.stats(repo)[lesson["id"]]["helped"], 1)
        tr = [t["action"] for t in wl.read_trace(repo, "t2")]
        self.assertLess(tr.index("lessons_retrieved"), tr.index("attempt_reserved")); self.assertNotIn("dispatch_refused", tr)
        for p in (repo / ".agent-work").rglob("*"):
            self.assertTrue(str(p.resolve()).startswith(str(repo.resolve())))


if __name__ == "__main__":
    unittest.main()
