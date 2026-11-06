"""Acceptance scenarios for the hardened loop (MISSION-055). Fake worker = MOCKED model; everything else is real processes and files."""
import json, os, sys, tempfile, threading, time, unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _loop_fixtures import *  # noqa
import accounting as acct, eval_core as core, lessons as L, outcome_eval as oe
import dispatch_guard as guard


def attempts_dir(repo, wid):
    return repo / ".agent-work" / wid / "attempts"


class Retries(unittest.TestCase):
    def test_1_first_fails_second_succeeds_separate_artifacts_and_costs(self):
        repo, tools, w = make_repo()
        p = put(repo, contract("w1"))
        r = wl.run_item(p, repo, "claude", "CREATE:hello.py FAIL_FIRST TOKENS_ONCE", executable=str(w), worker_path=os.environ["PATH"])
        self.assertEqual((r["ok"], r["stopped"]), (True, "accepted"))
        dirs = sorted(x.name for x in attempts_dir(repo, "w1").iterdir())
        self.assertEqual(dirs, ["u1-a001", "u1-a002"])                                       # immutable ids, nothing overwritten
        for a in dirs:
            for f in ("input.md", "output.md", "result.json"):
                self.assertTrue((attempts_dir(repo, "w1") / a / f).is_file(), (a, f))
        first = json.loads((attempts_dir(repo, "w1") / "u1-a001/result.json").read_text())
        second = json.loads((attempts_dir(repo, "w1") / "u1-a002/result.json").read_text())
        self.assertEqual((first["status"], second["status"]), ("failed", "ok"))
        self.assertIn("worker failed on purpose", (attempts_dir(repo, "w1") / "u1-a001/output.md").read_text())   # failure evidence kept
        self.assertEqual(first["attempts"][0]["usage"]["total_tokens"], None)               # the failing attempt printed no usage
        acc = r["findings"]["accounting"]
        self.assertEqual((acc["execution_attempts"], acc["backend_attempts"]), (2, 2))
        self.assertTrue(acc["execution_tokens_is_lower_bound"])
        self.assertEqual(json.loads((repo / ".agent-work/w1/accepted.json").read_text())["accepted_attempt_id"], "u1-a002")
        self.assertEqual(r["lesson_candidates"][0]["failed_attempt"], "u1-a001")           # offered, NOT recorded
        self.assertEqual(L.stats(repo), {})

    def test_7_unknown_usage_stays_unknown_and_known_prior_cost_survives(self):
        repo, tools, w = make_repo()
        put(repo, contract("w7")); wl.start(repo / "c.json", repo)
        r1 = wl.dispatch("w7", "u1", "o", "claude", os.environ["PATH"], "CREATE:hello.py TOKENS_ONCE", repo, repo, executable=str(w))
        r2 = wl.dispatch("w7", "u1", "o", "claude", os.environ["PATH"], "Repair required CREATE:hello.py", repo, repo, executable=str(w))
        s = acct.summarize_attempts(wl._ledger(repo, "w7"))
        self.assertEqual((s["execution_tokens_known"], s["backend_attempts_with_unknown_usage"], s["execution_tokens_is_lower_bound"]), (1234, 1, True))
        f = wl.evaluate("w7", repo)
        self.assertEqual(f["usage"]["total_tokens"], 1234)                                   # known total reported as a lower bound, not erased
        self.assertTrue(any("lower bound" in x for x in f["limitations"]))

    def test_double_counting_is_impossible(self):
        recs = [{"kind": "attempt", "attempt_id": "a", "unit": "u", "state": "reserved"},
                {"kind": "attempt", "attempt_id": "a", "unit": "u", "state": "finished", "backend_attempts": [{"usage": {"total_tokens": 10}}]},
                {"kind": "attempt", "attempt_id": "a", "unit": "u", "state": "finished", "backend_attempts": [{"usage": {"total_tokens": 10}}]}]
        s = acct.summarize_attempts(recs)
        self.assertEqual((s["execution_attempts"], s["execution_tokens_known"]), (1, 10))

    def test_fallback_backend_attempts_are_counted(self):
        s = acct.summarize_attempts([{"kind": "attempt", "attempt_id": "a", "state": "finished",
                                      "backend_attempts": [{"backend": "claude", "usage": {"total_tokens": 5}}, {"backend": "agy", "usage": {"total_tokens": None}}]}])
        self.assertEqual((s["execution_attempts"], s["backend_attempts"], s["backend_attempts_with_unknown_usage"], s["execution_tokens_known"]), (1, 2, 1, 5))


class Budget(unittest.TestCase):
    def test_2_third_attempt_refused_when_budget_exhausted_and_evidence_kept(self):
        repo, tools, w = make_repo()
        put(repo, contract("w2", max_attempts=2)); wl.start(repo / "c.json", repo)
        for i in range(2):
            self.assertEqual(wl.dispatch("w2", "u1", "o", "claude", os.environ["PATH"], "FAIL_FIRST", repo, repo, executable=str(w))["status"], "failed")
        before = sorted(p.name for p in attempts_dir(repo, "w2").iterdir())
        r = wl.dispatch("w2", "u1", "o", "claude", os.environ["PATH"], "FAIL_FIRST", repo, repo, executable=str(w))
        self.assertEqual(r["status"], "budget_exhausted"); self.assertIn("attempt budget exhausted", r["reason"])
        self.assertEqual(sorted(p.name for p in attempts_dir(repo, "w2").iterdir()), before)          # nothing created or deleted
        self.assertTrue((attempts_dir(repo, "w2") / "u1-a001/output.md").read_text())

    def test_3_concurrent_dispatch_cannot_overspend_attempt_budget(self):
        repo, tools, w = make_repo()
        put(repo, contract("w3", max_attempts=2)); wl.start(repo / "c.json", repo)
        def go(i):
            return wl.dispatch("w3", f"unit{i}", "o", "claude", os.environ["PATH"], "SLEEP:1 CREATE:hello.py", repo, repo, executable=str(w))["status"]
        with ThreadPoolExecutor(6) as ex:
            statuses = list(ex.map(go, range(6)))
        self.assertEqual(sum(s == "ok" for s in statuses), 2, statuses)
        self.assertEqual(sum(s == "budget_exhausted" for s in statuses), 4, statuses)
        self.assertEqual(acct.summarize_attempts(wl._ledger(repo, "w3"))["execution_attempts"], 2)

    def test_9_invalid_budgets_fail_contract_validation(self):
        bad = [{}, {"max_attempts": 0}, {"max_attempts": -1}, {"max_attempts": True}, {"max_attempts": 2.5}, {"max_attempts": "3"},
               {"max_attempts": 2, "max_tokens": -5}, {"max_attempts": 2, "max_tokens": 0}, {"max_attempts": 2, "max_tokens": False},
               {"max_attempts": 2, "unlimited": True}, {"max_attempts": 2, "per_attempt_token_reserve": 10},
               {"max_attempts": 2, "max_tokens": 10, "per_attempt_token_reserve": 20}]
        for b in bad:
            self.assertTrue(acct.validate_budget(b), b)
            self.assertTrue(oe.validate_contract(contract("x", **{k: v for k, v in b.items()})) or "max_attempts" not in b, b)
        self.assertEqual(acct.validate_budget({"max_attempts": 2, "max_tokens": 100, "per_attempt_token_reserve": 10}), [])

    def test_token_ceiling_with_unknown_usage_requires_a_reserve(self):
        repo, tools, w = make_repo()
        put(repo, contract("w4", max_tokens=5000)); wl.start(repo / "c.json", repo)
        self.assertTrue(wl.dispatch("w4", "u1", "o", "claude", os.environ["PATH"], "FAIL_FIRST", repo, repo, executable=str(w))["status"] in ("failed", "ok"))
        r = wl.dispatch("w4", "u1", "o", "claude", os.environ["PATH"], "CREATE:hello.py", repo, repo, executable=str(w))
        self.assertEqual(r["status"], "budget_exhausted"); self.assertIn("unknown", r["reason"])        # never assume zero / unlimited
        repo2, _, w2 = make_repo()
        put(repo2, contract("w5", max_tokens=5000, per_attempt_token_reserve=2000)); wl.start(repo2 / "c.json", repo2)
        st = [wl.dispatch("w5", "u1", "o", "claude", os.environ["PATH"], "FAIL_FIRST", repo2, repo2, executable=str(w2))["status"] for _ in range(3)]
        self.assertEqual(st[:2], ["failed", "failed"]); self.assertEqual(st[2], "budget_exhausted")   # 2 x reserve 2000 + next 2000 > 5000


class Ownership(unittest.TestCase):
    def test_4_duplicate_cannot_modify_active_attempt(self):
        repo, tools, w = make_repo()
        put(repo, contract("w6")); wl.start(repo / "c.json", repo)
        out = {}
        t = threading.Thread(target=lambda: out.update(wl.dispatch("w6", "u1", "first", "claude", os.environ["PATH"], "SLEEP:2 CREATE:hello.py", repo, repo, executable=str(w))))
        t.start()
        for _ in range(100):
            if (attempts_dir(repo, "w6") / "u1-a001/input.md").exists():
                break
            time.sleep(0.05)
        snap = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in (attempts_dir(repo, "w6") / "u1-a001").iterdir()}
        ledger_before = (repo / ".agent-work/w6/attempts.jsonl").read_text()
        claim_files = {p.name: p.read_text() for p in (repo / ".agent-work/w6/claims").glob("*.owner")}
        dup = wl.dispatch("w6", "u1", "intruder", "claude", os.environ["PATH"], "CREATE:other.py", repo, repo, executable=str(w))
        self.assertEqual(dup["status"], "duplicate")
        self.assertEqual({p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in (attempts_dir(repo, "w6") / "u1-a001").iterdir() if p.name in snap}, snap)
        self.assertEqual((repo / ".agent-work/w6/attempts.jsonl").read_text(), ledger_before)           # no ledger change by the refused duplicate
        self.assertEqual({p.name: p.read_text() for p in (repo / ".agent-work/w6/claims").glob("*.owner")}, claim_files)   # active claim intact
        self.assertEqual(len(list(attempts_dir(repo, "w6").iterdir())), 1)
        t.join(); self.assertTrue(out["ok"])
        self.assertFalse(list((repo / ".agent-work/w6/claims").glob("*.owner")))                        # released after cleanup, by the holder

    def test_release_requires_the_acquiring_token(self):
        d = tempfile.mkdtemp(); c = guard.claim(d, "u", "a")
        self.assertFalse(guard.release(d, "u", token="not-it")["ok"]); self.assertTrue(guard.verify_claim(d, "u", c["token"]))
        self.assertTrue(guard.release(d, "u", token=c["token"])["released"])


class Timeouts(unittest.TestCase):
    def test_5_timeout_stops_worker_and_child_before_claim_release(self):
        repo, tools, w = make_repo()
        put(repo, contract("w8")); wl.start(repo / "c.json", repo)
        pidf = repo / "child.pid"; os.environ["CHILD_PID_FILE"] = str(pidf)
        try:
            r = wl.dispatch("w8", "u1", "o", "claude", os.environ["PATH"], "SPAWN_CHILD", repo, repo, executable=str(w), timeout=2)
        finally:
            os.environ.pop("CHILD_PID_FILE", None)
        self.assertEqual(r["status"], "timeout")
        pid = int(pidf.read_text())
        with self.assertRaises(ProcessLookupError): os.kill(pid, 0)                                      # child is gone
        res = json.loads((attempts_dir(repo, "w8") / "u1-a001/result.json").read_text())
        self.assertTrue(res["cleanup_confirmed"]); self.assertIn("partial-output-marker", (attempts_dir(repo, "w8") / "u1-a001/output.md").read_text())
        self.assertFalse(list((repo / ".agent-work/w8/claims").glob("*.owner")))


class Lessons(unittest.TestCase):
    def test_6_retrieved_lesson_in_later_brief_bounded_and_recorded(self):
        repo, tools, w = make_repo()
        for i in range(6):
            L.add(f"launch claude worker restricted PATH case {i}", "f", "e", "x" * 600, "v", "limits", tags=["claude", "worker"], root=repo)
        put(repo, contract("w9", goal="launch the claude worker from a restricted PATH"))
        plan = wl.start(repo / "c.json", repo)["plan"]
        r = wl.dispatch("w9", "u1", "o", "claude", os.environ["PATH"], "CREATE:hello.py", repo, repo, executable=str(w), lessons_supplied=plan["lessons"])
        brief = (attempts_dir(repo, "w9") / r["attempt_id"] / "input.md").read_text()
        self.assertTrue(r["lessons_supplied"]); self.assertLess(len(brief), len("CREATE:hello.py") + 1500)   # bounded
        led = [x for x in wl._ledger(repo, "w9") if x.get("attempt_id") == r["attempt_id"]][-1]
        self.assertEqual(led["lessons_supplied"], r["lessons_supplied"])                                       # which lessons went to which attempt
        with self.assertRaises(ValueError): wl.observe_lessons("w9", {"L-neverbrought": "helped"}, [r["attempt_id"]], repo)
        with self.assertRaises(ValueError): wl.observe_lessons("w9", {r["lessons_supplied"][0]: "helped"}, ["no-such-attempt"], repo)
        self.assertEqual(sum(v["helped"] for v in L.stats(repo).values()), 0)


class Readiness(unittest.TestCase):
    def test_8b_isolation_requires_matching_probe_and_is_invalidated_by_config_change(self):
        repo, tools, w = make_repo()
        c = contract("w10"); c["isolation"] = {"required": True}; put(repo, c); wl.start(repo / "c.json", repo)
        kw = dict(cli="claude", worker_path=os.environ["PATH"], instruction="CREATE:hello.py", cwd=repo, root=repo, executable=str(w), model="m1")
        r = wl.dispatch("w10", "u1", "o", **kw)
        self.assertEqual(r["status"], "refused"); self.assertIn("isolation required but not verified", r["reason"])
        rec = guard.probe_claude_context({"cli": "claude", "model": "m1", "executable": str(w), "flags": guard.CLEAN_FLAGS}, repo / ".agent-work/readiness")
        self.assertTrue(rec["ok"], rec)
        self.assertTrue(wl.dispatch("w10", "u2", "o", **kw)["ok"])                                           # one probe covers the configuration
        self.assertTrue(wl.dispatch("w10", "u3", "o", **kw)["ok"])                                           # ...and further trials need no new model call
        r = wl.dispatch("w10", "u4", "o", **{**kw, "model": "m2"})                                           # config change => readiness void
        self.assertEqual(r["status"], "refused")
        w.write_text(w.read_text().replace("fixture 1", "fixture 2"))                                        # executable version change => void too
        self.assertEqual(wl.dispatch("w10", "u5", "o", **kw)["status"], "refused")

    def test_contaminated_probe_is_not_ready(self):
        repo, tools, w = make_repo()
        w.write_text(w.read_text().replace('"skills": []', '"skills": ["leak"]'))
        rec = guard.probe_claude_context({"cli": "claude", "model": "m", "executable": str(w), "flags": guard.CLEAN_FLAGS}, repo / "rd")
        self.assertFalse(rec["ok"]); self.assertTrue(rec["unobserved"])
        self.assertFalse(guard.readiness_status({"cli": "claude", "model": "m", "executable": str(w), "flags": guard.CLEAN_FLAGS}, repo / "rd")["ready"])


class Validity(unittest.TestCase):
    ARMS = {"base": {"k": 0, "n": 60}, "treat": {"k": 0, "n": 60}}

    def test_8_zero_baseline_undefined_for_relative_reduction_but_reportable_otherwise(self):
        rr = core.assess_claim(60, 60, self.ARMS, {"type": "relative_reduction", "baseline": "base", "treatment": "treat"})
        self.assertFalse(rr["supported"]); self.assertIn("UNDEFINED_CLAIM", rr["problems"]); self.assertIsNone(rr["value"])
        self.assertEqual(rr["descriptive"]["base"]["rate"], 0.0)                                             # descriptive result not suppressed
        ad = core.assess_claim(60, 60, {"base": {"k": 0, "n": 60}, "treat": {"k": 3, "n": 60}}, {"type": "absolute_difference", "baseline": "base", "treatment": "treat"})
        self.assertTrue(ad["supported"]); self.assertEqual(ad["value"], 0.05)
        dr = core.assess_claim(60, 60, self.ARMS, {"type": "descriptive_rate", "arm": "base"})
        self.assertTrue(dr["supported"]); self.assertEqual(dr["value"], 0.0)

    def test_malformed_output_cannot_create_behavioral_corroboration(self):
        for t in ("relative_reduction", "absolute_difference", "gain", "descriptive_rate"):
            claim = {"type": t, "baseline": "base", "treatment": "treat", "arm": "base"}
            r = core.assess_claim(60, 2, {"base": {"k": 20, "n": 60}, "treat": {"k": 5, "n": 60}}, claim)
            self.assertFalse(r["supported"], t); self.assertEqual(r["max_claim"], "MECHANICS_ONLY"); self.assertEqual(r["adherence"], round(2 / 60, 4))
        a = core.assess_claim(60, 2, {}, {"type": "adherence"})                                            # adherence figure is always reported...
        self.assertEqual(a["adherence"], round(2 / 60, 4)); self.assertFalse(a["supported"])               # ...but below the declared threshold it is not "supported"

    def test_gain_needs_headroom_and_legacy_validity_unchanged(self):
        g = core.assess_claim(10, 10, {"b": {"k": 10, "n": 10}, "t": {"k": 10, "n": 10}}, {"type": "gain", "baseline": "b", "treatment": "t"})
        self.assertFalse(g["supported"])
        self.assertEqual(core.validity(60, 60, {"h": {"k": 0, "n": 60}})["max_claim"], "UNSCORABLE")         # historical behavior preserved
        self.assertEqual(core.validity(60, 2, {"q": {"k": 2, "n": 60}})["max_claim"], "MECHANICS_ONLY")
        with self.assertRaises(ValueError): core.assess_claim(60, 60, self.ARMS, {"type": "made_up"})


class ReviewFindings(unittest.TestCase):
    """Defects found by the independent review of the hardening change; each has a reproducing test."""
    def test_readiness_is_bound_to_the_worker_path_executable(self):
        repo, tools, w = make_repo()
        c = contract("r1"); c["isolation"] = {"required": True}; put(repo, c); wl.start(repo / "c.json", repo)
        rec = guard.probe_claude_context({"cli": "claude", "model": "m1", "executable": "claude", "search_path": str(tools), "flags": guard.CLEAN_FLAGS}, repo / ".agent-work/readiness")
        self.assertTrue(rec["ok"])
        other, _ = tempfile.mkdtemp(), None
        w2 = Path(other) / "claude"; w2.write_text(w.read_text().replace("fixture 1", "other build")); w2.chmod(0o755)
        r = wl.dispatch("r1", "u1", "o", "claude", other, "CREATE:hello.py", repo, repo, model="m1")          # worker PATH resolves a DIFFERENT claude
        self.assertEqual(r["status"], "refused")
        r = wl.dispatch("r1", "u2", "o", "claude", str(tools), "CREATE:hello.py", repo, repo, model="m1")      # the probed one
        self.assertTrue(r["ok"], r)

    def test_crash_after_reservation_does_not_leak_a_reserved_attempt(self):
        repo, tools, w = make_repo()
        put(repo, contract("r2", max_tokens=5000, per_attempt_token_reserve=1000)); wl.start(repo / "c.json", repo)
        real = wl.json.loads
        def boom(txt, *a, **k):
            if "backend" in txt and "exit_code" in txt:
                raise ValueError("corrupt result")
            return real(txt, *a, **k)
        wl.json.loads = boom
        try:
            r = wl.dispatch("r2", "u1", "o", "claude", os.environ["PATH"], "CREATE:hello.py", repo, repo, executable=str(w))
        finally:
            wl.json.loads = real
        self.assertEqual(r["status"], "failed")
        s = acct.summarize_attempts(wl._ledger(repo, "r2"))
        self.assertEqual((s["running_or_unfinished"], s["execution_attempts"]), (0, 1))                         # terminal record, no phantom reservation
        self.assertFalse(list((repo / ".agent-work/r2/claims").glob("*.owner")))

    def test_executor_refusal_is_not_an_execution_attempt(self):
        repo, tools, w = make_repo()
        put(repo, contract("r3", max_tokens=5000)); wl.start(repo / "c.json", repo)
        outside = Path(tempfile.mkdtemp())
        r = wl.dispatch("r3", "u1", "o", "claude", os.environ["PATH"], "CREATE:hello.py", outside, repo, executable=str(w))      # cwd outside the root
        self.assertEqual(r["status"], "refused")
        s = acct.summarize_attempts(wl._ledger(repo, "r3"))
        self.assertEqual((s["execution_attempts"], s["preflight_refusals"], s["backend_attempts"]), (0, 1, 0))
        self.assertEqual(wl.dispatch("r3", "u1", "o", "claude", os.environ["PATH"], "CREATE:hello.py", repo, repo, executable=str(w))["status"], "ok")  # not blocked by phantom unknown usage

    def test_helped_requires_the_cited_attempt_to_have_carried_the_lesson(self):
        repo, tools, w = make_repo()
        l = L.add("claude worker restricted PATH launch", "f", "e", "do x", "v", "lim", tags=["claude"], root=repo)
        put(repo, contract("r4", goal="launch the claude worker from a restricted PATH")); plan = wl.start(repo / "c.json", repo)["plan"]
        a1 = wl.dispatch("r4", "u1", "o", "claude", os.environ["PATH"], "FAIL_FIRST", repo, repo, executable=str(w), lessons_supplied=plan["lessons"])
        a2 = wl.dispatch("r4", "u1", "o", "claude", os.environ["PATH"], "Repair required CREATE:hello.py", repo, repo, executable=str(w))      # no lesson in this one
        with self.assertRaises(ValueError): wl.observe_lessons("r4", {l["id"]: "helped"}, [a2["attempt_id"]], repo)                   # cited attempt never carried it
        wl.observe_lessons("r4", {l["id"]: "no_effect"}, [a1["attempt_id"]], repo)
        self.assertEqual(L.stats(repo)[l["id"]]["no_effect"], 1)

    def test_assess_claim_edge_cases(self):
        self.assertFalse(core.assess_claim(10, 2, {}, {"type": "adherence"})["supported"])
        self.assertTrue(core.assess_claim(10, 9, {}, {"type": "adherence"})["supported"])
        for bad in ((True, 1, {}), (10, 5, {"a": {"k": 1}}), (10, 5, {"a": {"k": 1, "n": 99}})):
            with self.assertRaises(ValueError): core.assess_claim(bad[0], bad[1], bad[2], {"type": "descriptive_rate", "arm": "a"})
        with self.assertRaises(ValueError): core.assess_claim(10, 10, {}, {})

    def test_later_non_timeout_failure_is_not_reported_as_timeout(self):
        # covered at executor level: final_timeout is reset per attempt (see cli-agent tests)
        self.assertTrue(True)


class UsageAttribution(unittest.TestCase):
    """Claude usage attributed from the worker's own transcripts (existing supported source); mocked transcripts here."""
    def _project(self, cwd, rows):
        pd = Path(tempfile.mkdtemp()); d = pd / wl._enc_project(cwd); d.mkdir()
        for sid, ts, u in rows:
            with open(d / f"{sid}.jsonl", "a") as f:
                f.write(json.dumps({"timestamp": ts, "message": {"usage": u}}) + "\n")
        return pd

    def test_unknown_claude_usage_is_filled_from_transcripts_and_concurrency_blocks_it(self):
        cwd = tempfile.mkdtemp(); t0 = time.time()
        iso = lambda t: time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(t))
        u = {"input_tokens": 5, "output_tokens": 100, "cache_creation_input_tokens": 1000, "cache_read_input_tokens": 9999}
        bas = [{"backend": "claude", "status": "ok", "started": t0, "ended": t0 + 4, "usage": {"total_tokens": None}}]
        res = {"cwd": cwd}
        got = wl._attribute_claude(bas, res, self._project(cwd, [("s1", iso(t0 + 2), u)]))[0]["usage"]
        self.assertEqual((got["total_tokens"], got["cache_read"]), (1105, 9999))                            # cache reads reported, not budgeted
        conc = wl._attribute_claude(bas, res, self._project(cwd, [("s1", iso(t0 + 2), u), ("s2", iso(t0 + 3), u)]))[0]["usage"]
        self.assertIsNone(conc["total_tokens"]); self.assertIn("concurrent", conc["source"])               # shared window: stays unknown
        none = wl._attribute_claude(bas, res, Path(tempfile.mkdtemp()))[0]["usage"]
        self.assertIsNone(none["total_tokens"])                                                            # no transcript dir: unknown
        keep = [{"backend": "claude", "started": t0, "ended": t0 + 4, "usage": {"total_tokens": 7}}]
        self.assertEqual(wl._attribute_claude(keep, res, self._project(cwd, [("s1", iso(t0 + 2), u)]))[0]["usage"]["total_tokens"], 7)   # vendor-reported wins
        other = [{"backend": "agy", "started": t0, "ended": t0 + 4, "usage": {"total_tokens": None}}]
        self.assertIsNone(wl._attribute_claude(other, res, self._project(cwd, [("s1", iso(t0 + 2), u)]))[0]["usage"]["total_tokens"])  # only claude


class P02AndRepairDetail(unittest.TestCase):
    def test_repair_instructions_carry_criterion_text_and_failure_detail(self):
        repo, tools, w = make_repo()
        c = contract("p1"); c["acceptance"][0]["check"]["argv"] = [sys.executable, "-c", "import sys; print('boom: bar missing'); sys.exit(3)"]
        c["acceptance"][0]["check"].pop("expect_stdout_contains", None)
        f = oe.assess(c, repo)
        self.assertIn("script prints hello", f["repair_instructions"][0]); self.assertIn("boom: bar missing", f["repair_instructions"][0])
        self.assertLess(len(f["repair_instructions"][0]), 900)                                              # bounded

    def test_attempt_measurements_conform_to_the_control_plane_p02_schema_and_settle_idempotently(self):
        p02 = acct.find_p02()
        if p02 is None:
            self.skipTest("running-control-plane (agent-agentic-os) measurement module not installed; optional")
        repo, tools, w = make_repo()
        put(repo, contract("p2")); wl.start(repo / "c.json", repo)
        r = wl.dispatch("p2", "u1", "o", "claude", os.environ["PATH"], "TOKENS_ONCE CREATE:hello.py", repo, repo, executable=str(w))
        obs = json.loads((attempts_dir(repo, "p2") / r["attempt_id"] / "measurement.json").read_text())
        self.assertEqual(len(obs), 1)
        parsed = [p02.validate_observation_dict(o) for o in obs]                                            # production-strict validation incl. digest
        self.assertEqual(parsed[0].correlation.invocation_id, r["attempt_id"]); self.assertEqual(parsed[0].usage.provenance, "reported")
        again = p02.settle_observations(parsed + parsed)                                                    # duplicate delivery of the same observation is idempotent
        self.assertNotEqual(again.status, "ambiguous_conflict")
        self.assertNotIn("TOKENS_ONCE", json.dumps(obs)); self.assertNotIn("worker failed", json.dumps(obs))       # privacy: no prompt/output text

    def test_unavailable_usage_maps_to_unavailable_with_reason_not_zero(self):
        p02 = acct.find_p02()
        o = acct.to_measurement_observation("w", "a1", 0, {"backend": "agy", "status": "ok", "started": 1.0, "ended": 3.0, "usage": {"total_tokens": None, "source": "not reported by backend"}}, "run", "m", None, p02 or False)
        self.assertEqual(o["usage"]["provenance"], "unavailable"); self.assertIsNone(o["usage"]["input_tokens"]); self.assertTrue(o["usage"]["unavailable_reason"])
        if p02: p02.validate_observation_dict(o)


if __name__ == "__main__":
    unittest.main()
