import json, subprocess, sys, tempfile, unittest
from pathlib import Path
S = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(S / "scripts"))
import eval_core as c, outcome_eval as oe, lessons as L


def contract(root, rubric=None, **over):
    d = {"id": "w1", "type": "task", "goal": "add hello", "scope": {"paths": ["hello.py"]},
         "acceptance": [{"id": "A1", "check": {"kind": "command", "argv": [sys.executable, "hello.py"], "expect_stdout_contains": ["hello"]}},
                        {"id": "A2", "check": {"kind": "file_exists", "path": "hello.py"}}],
         "failure_conditions": [{"id": "F1", "text": "error marker", "check": {"kind": "file_exists", "path": "ERROR.txt"}}],
         "budget": {"max_attempts": 3, "max_tokens": 1000}, "authorization": {"may_merge": False}}
    if rubric:
        d["rubric"] = json.loads((S / "assets" / "rubrics" / "pr-review.json").read_text())
    d.update(over)
    return d


class Assess(unittest.TestCase):
    def setUp(self):
        self.r = Path(tempfile.mkdtemp())
    def test_plain_task_no_scores(self):
        (self.r / "hello.py").write_text("print('hello')")
        f = oe.assess(contract(self.r), self.r)
        self.assertTrue(f["complete"]); self.assertEqual(f["recommended"], "accept"); self.assertNotIn("scores", f)
        self.assertFalse(f["integration_allowed"])               # authorization not expanded by success
    def test_incomplete_returns_repair(self):
        f = oe.assess(contract(self.r), self.r)
        self.assertEqual(f["recommended"], "repair"); self.assertEqual(set(f["incomplete"]), {"A1", "A2"})
    def test_attempt_cap_escalates(self):
        self.assertEqual(oe.assess(contract(self.r), self.r, attempts_used=3)["recommended"], "escalate")
    def test_high_score_cannot_conceal_unmet_criterion(self):
        ev = {"scores": {"correctness": 3, "tests": 3, "scope_discipline": 3, "economy": 3}}
        f = oe.assess(contract(self.r, rubric=True), self.r, ev)
        self.assertEqual(f["scores"]["normalized"], 1.0); self.assertFalse(f["complete"]); self.assertEqual(f["recommended"], "repair")
    def test_pr_rubric_validated(self):
        (self.r / "hello.py").write_text("print('hello')")
        f = oe.assess(contract(self.r, rubric=True), self.r, {"scores": {"correctness": 9}})
        self.assertTrue(f["scores"]["problems"]); self.assertIsNone(f["scores"]["normalized"]); self.assertTrue(f["complete"])
    def test_failure_condition_blocks_completion(self):
        (self.r / "hello.py").write_text("print('hello')"); (self.r / "ERROR.txt").write_text("x")
        f = oe.assess(contract(self.r), self.r)
        self.assertFalse(f["complete"]); self.assertEqual(f["failure_hits"][0]["id"], "F1")
    def test_missing_usage_is_unknown_not_zero(self):
        (self.r / "hello.py").write_text("print('hello')")
        f = oe.assess(contract(self.r), self.r)
        self.assertIsNone(f["usage"]["total_tokens"]); self.assertTrue(any("unmeasured" in x for x in f["limitations"]))
    def test_budget_exceeded_blocks_and_still_not_authorized(self):
        (self.r / "hello.py").write_text("print('hello')")
        f = oe.assess(contract(self.r), self.r, {"usage": {"total_tokens": 5000}})
        self.assertEqual(f["recommended"], "blocked")
    def test_manual_criterion_unverified_without_confirmation(self):
        c1 = contract(self.r, acceptance=[{"id": "M", "check": {"kind": "manual"}}])
        self.assertEqual(oe.assess(c1, self.r)["criteria"][0]["result"], "unverified")
        self.assertTrue(oe.assess(c1, self.r, {"manual_confirmations": {"M": "reviewer note 12"}})["complete"])
    def test_contract_needs_observable_acceptance_and_failure(self):
        self.assertTrue(oe.validate_contract({"id": "x", "type": "t", "goal": "g"}))
    def test_command_cwd_cannot_escape_root(self):
        c1 = contract(self.r, acceptance=[{"id": "A", "check": {"kind": "command", "argv": ["true"], "cwd": ".."}}])
        f = oe.assess(c1, self.r); self.assertEqual(f["criteria"][0]["result"], "error"); self.assertFalse(f["complete"])


class Store(unittest.TestCase):
    def test_store_confined_to_root(self):
        r = tempfile.mkdtemp()
        with self.assertRaises(ValueError): c.resolve_store(r, "/tmp/elsewhere.jsonl")
        with self.assertRaises(ValueError): c.resolve_store(r, "../up.jsonl")
        self.assertTrue(str(c.resolve_store(r)).startswith(str(Path(r).resolve())))
    def test_default_store_is_repo_local(self):
        r = tempfile.mkdtemp(); c.record_intervention("scope_change", "why", "user msg", root=r)
        self.assertTrue((Path(r) / ".agent-work/records.jsonl").exists())
    def test_legacy_event_type_read_and_written(self):
        r = tempfile.mkdtemp(); c.record_repair("cat", "ev", "fix", "t", "o", root=r, store="e.jsonl", compat_event_type=True)
        raw = json.loads((Path(r) / "e.jsonl").read_text())
        self.assertEqual(raw["event_type"], "FAILURE_REPAIR"); self.assertEqual(c.repair_report(r, "e.jsonl")["cat"]["failures"], 1)


class Gates(unittest.TestCase):
    def test_qwen_and_haiku_regressions(self):
        self.assertEqual(c.validity(60, 2, {"q": {"k": 2, "n": 60}})["max_claim"], "MECHANICS_ONLY")
        self.assertEqual(c.validity(60, 60, {"h": {"k": 0, "n": 60}})["max_claim"], "UNSCORABLE")
        self.assertEqual(c.validity(60, 60, {})["max_claim"], "UNSCORABLE")
    def test_invest_unknown_and_correction_classes(self):
        r = c.investment([{"id": "a", "execution": 10}, {"id": "b"}])
        self.assertTrue(r["telemetry_gap"]); self.assertIsNone(r["totals"]["verification"])
        d = tempfile.mkdtemp()
        c.record_intervention("required_authorization", "merge", "user said go", root=d); c.record_intervention("execution_failure_correction", "r", "msg", root=d)
        s = c.intervention_summary(d); self.assertEqual(s["corrections"], 1); self.assertEqual(s["records"], 2)
        self.assertIn("unknown", c.intervention_summary(tempfile.mkdtemp())["coverage"])
    def test_select_never_shrinks(self):
        self.assertEqual(c.select_method(True, True, True, True)["method"], "checkpoint")


class Lessons(unittest.TestCase):
    def test_add_find_use_stats(self):
        r = tempfile.mkdtemp()
        l = L.add("worker PATH lacks the claude executable", "launch failed", "run 12", "pass explicit --executable after exec-check", "test", "claude backend only", tags=["executable", "path"], root=r)
        L.add("unrelated database migration", "lock", "ev", "retry", "t", "x", root=r)
        hits = L.find("run the claude worker with a restricted PATH", root=r)
        self.assertEqual(hits[0]["id"], l["id"]); self.assertEqual(len(hits), 1)       # compact: only relevant lesson
        L.use(l["id"], "task2", "helped", root=r)
        self.assertEqual(L.stats(r)[l["id"]]["helped"], 1)
    def test_lesson_requires_evidence(self):
        with self.assertRaises(ValueError): L.add("t", "f", "", "a", "v", "l", root=tempfile.mkdtemp())


if __name__ == "__main__":
    unittest.main()


class ReviewFixes(unittest.TestCase):
    def setUp(self):
        self.r = Path(tempfile.mkdtemp()); (self.r / "hello.py").write_text("print('hello')")
    def test_unevaluable_failure_condition_blocks_completion(self):
        c1 = contract(self.r, failure_conditions=[{"id": "f", "check": {"kind": "command", "argv": ["true"], "cwd": "../.."}}])
        f = oe.assess(c1, self.r); self.assertFalse(f["complete"]); self.assertEqual(f["unevaluated_failure_conditions"][0]["id"], "f")
    def test_may_merge_must_be_bool(self):
        self.assertTrue(oe.validate_contract(contract(self.r, authorization={"may_merge": "false"})))
        f = oe.assess(contract(self.r, authorization={"may_merge": True}), self.r); self.assertTrue(f["integration_allowed"])
    def test_all_optional_acceptance_rejected(self):
        acc = [{"id": "A", "required": False, "check": {"kind": "file_exists", "path": "nope"}}]
        self.assertTrue(oe.validate_contract(contract(self.r, acceptance=acc)))
    def test_failure_condition_without_check_rejected(self):
        self.assertTrue(oe.validate_contract(contract(self.r, failure_conditions=[{"id": "f", "text": "t"}])))
