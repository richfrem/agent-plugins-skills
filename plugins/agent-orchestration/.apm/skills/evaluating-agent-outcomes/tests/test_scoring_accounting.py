import json, sys, unittest
from pathlib import Path
S = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(S / "scripts"))
import scoring, accounting, usage_measure as um
FIX = Path(__file__).resolve().parent / "fixtures"


def prof(name):
    return scoring.load_profile((S / "tests" / "fixtures" if name.startswith("sanctuary") else S / "assets" / "rubrics") / name)


class OneMechanismTwoProfiles(unittest.TestCase):
    def test_sanctuary_profile_reproduces_historical_arithmetic(self):
        p = prof("sanctuary-contribution-v1.json")
        r = {"useful_outcome": 1, "learning_depth": 2, "verification_rigor": 3, "token_economy": 0, "anti_asch_integrity": 1}
        s = scoring.score(p, r)
        self.assertEqual((s["raw_score"], s["max_score"], s["fitness"]), (7, 15, round(7 / 15.0, 3)))
        self.assertEqual(scoring.cost_adjusted(s["fitness"], 4.0), round(s["fitness"] / 4.0, 3))
        self.assertIn("Expensive model 'opus'", scoring.bloat_warning(p, r, "opus", 4.0))
        self.assertIsNone(scoring.bloat_warning(p, r, "haiku", 0.2))             # cheap model: no bloat rule
        self.assertIsNone(scoring.bloat_warning(p, dict(r, token_economy=3, useful_outcome=3), "opus", 4.0))

    def test_pr_review_profile_weighted_headline_differs_by_design(self):
        p = prof("pr-review.json")
        r = {"correctness": 3, "tests": 0, "scope_discipline": 3, "economy": 3}
        s = scoring.score(p, r)
        # semantics differ: weights 3/2/1/1 -> (3*1 + 2*0 + 1 + 1)/7
        self.assertEqual(s["fitness"], round(5 / 7, 4)); self.assertEqual(s["raw_score"], 9)
        self.assertNotEqual(s["fitness"], round(9 / 12, 3))                       # unweighted fraction would give a different number

    def test_invalid_ratings_rejected_not_clamped(self):
        p = prof("sanctuary-contribution-v1.json")
        for bad in ({}, {"useful_outcome": 4}, {"useful_outcome": True}):
            with self.assertRaises(ValueError): scoring.score(p, bad)

    def test_projection_fold_is_order_independent_and_profile_sized(self):
        p = prof("sanctuary-contribution-v1.json")
        def a(i, agent, vals):
            d = dict(zip(p["dimensions"], vals)); return {"assessment_id": f"i{i}", "timestamp": f"2026-01-0{i}T00:00:00+00:00", "task_id": f"t{i}",
                    "agent_id": agent, "raw_score": sum(vals), "dimensions": d, "cognitive_fitness": round(sum(vals) / 15, 3), "notes": ""}
        evs = [a(1, "x", (3, 3, 3, 3, 3)), a(2, "y", (0, 1, 2, 3, 0)), a(3, "x", (1, 1, 1, 1, 1))]
        self.assertEqual(scoring.rebuild_projection(p, evs), scoring.rebuild_projection(p, list(reversed(evs))))
        pr = scoring.rebuild_projection(p, evs)
        self.assertEqual(pr["agents"]["x"]["assessments"], 2); self.assertEqual(pr["average_fitness"], round((15 + 6 + 5) / 45, 3))
        p2 = prof("pr-review.json"); self.assertEqual(scoring.empty_projection(p2)["dimension_totals"].keys(), p2["dimensions"].keys())


class Accounting(unittest.TestCase):
    def test_lookup_rule_and_default(self):
        self.assertEqual(accounting.get_model_cost_weight("claude-opus-5-5"), 4.0)
        self.assertEqual(accounting.get_model_cost_weight("totally-unknown"), 1.0)
        self.assertEqual(accounting.get_model_tier("Qwen2.5-Coder")["tier"], "free")

    def test_ledger_fold_preserves_extras_and_trims(self):
        led = accounting.new_ledger()
        for i in range(35):
            accounting.fold_usage(led, {"task_id": "t", "backend": "b", "model": "m", "tokens_est": 10, "turns": 1, "summary": "", "source": "measured"})
        self.assertEqual((led["total_tokens_consumed"], led["total_turns"], len(led["recent_records"])), (350, 35, 30))
        self.assertEqual(led["recent_records"][0]["source"], "measured")

    def test_turn_check_policy_is_caller_data(self):
        profs = {"default": {"description": "d", "soft_turn_limit_per_task": 5}, "tiny": {"description": "t", "soft_turn_limit_per_task": 1}}
        self.assertEqual(accounting.check_turns(profs, "tiny", 2)["status"], "WARNING")
        self.assertEqual(accounting.check_turns(profs, "missing", 5)["status"], "APPROVED")


class UsageMeasure(unittest.TestCase):
    def test_parsers_on_real_captured_output(self):
        r = um.parse_claude_usage((FIX / "claude_usage.txt").read_text())
        self.assertIsInstance(r["session_pct_used"], int)
        self.assertIsNone(um.parse_claude_usage("garbage")["week_pct_used"])
        rows = um.parse_agy_usage(json.loads((FIX / "agy_usage.json").read_text()))
        self.assertTrue(rows and all(0 <= x["remaining_pct"] <= 100 for x in rows))

    def test_resetless_session_is_parsed_as_displayed_not_unparsed(self):
        # Observed 2026-11-07: "Current session: 0% used" has no "· resets" suffix. The displayed value
        # is parsed; the missing reset stays None, and absent text stays None (never imputed as zero).
        r = um.parse_claude_usage((FIX / "claude_usage_resetless.txt").read_text())
        self.assertEqual(r["session_pct_used"], 0)
        self.assertIsNone(r["session_resets"])
        self.assertEqual(r["week_pct_used"], 65)
        self.assertEqual(r["week_resets"], "Nov 9 at 9pm (America/Vancouver)")
        empty = um.parse_claude_usage("Current week (all models): 65% used")
        self.assertIsNone(empty["session_pct_used"])
        self.assertEqual(empty["week_pct_used"], 65)

    def test_secrets_rejected_and_unknown_price_is_none_not_zero(self):
        with self.assertRaises(ValueError): um.assert_no_secrets({"k": "sk-" + "a" * 20})
        self.assertIsNone(um.cost_usd("absent", 1000, 1000, prices={}))
        self.assertEqual(um.cost_usd("m", 1_000_000, 0, prices={"m": {"input_per_mtok": 3.0, "output_per_mtok": 15.0}}), 3.0)


if __name__ == "__main__":
    unittest.main()
