import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import dispatch_guard as g


class Ownership(unittest.TestCase):
    def test_second_claim_fails_before_launch(self):
        d = tempfile.mkdtemp()
        self.assertTrue(g.claim(d, "haiku-arm", "codex-c")["ok"])
        r = g.claim(d, "haiku-arm", "claude-code")
        self.assertFalse(r["ok"]); self.assertEqual(r["owner"], "codex-c")
    def test_only_owner_releases(self):
        d = tempfile.mkdtemp(); g.claim(d, "u", "a")
        self.assertFalse(g.release(d, "u", "b")["ok"])
        self.assertTrue(g.release(d, "u", "a")["released"]); self.assertTrue(g.claim(d, "u", "b")["ok"])


class Exec(unittest.TestCase):
    def test_missing_on_worker_path(self):
        # The orchestrator can see python; a worker whose PATH is empty cannot.
        self.assertTrue(g.exec_check([Path(sys.executable).name], path=str(Path(sys.executable).parent))["ok"])
        with self.assertRaises(ValueError): g.exec_check(["python3"], path=None)
        r = g.exec_check(["claude"], path=tempfile.mkdtemp())
        self.assertFalse(r["ok"]); self.assertIn("not found", r["results"][0]["detail"])


class Context(unittest.TestCase):
    CLEAN = {"cwd": "/tmp/neutral-x", "model": "m", "tools": [], "slash_commands": [], "skills": [], "mcp_servers": []}
    def test_clean(self):
        self.assertEqual(g.context_problems(self.CLEAN, 0), [])
    def test_mission_052_contamination_detected(self):
        # 480 Haiku calls ran with hooks, skills, tools and memory loaded from the repo folder.
        init = dict(self.CLEAN, skills=["a"], tools=["Bash"], slash_commands=["x"])
        p = g.context_problems(init, hook_events=3)
        self.assertTrue(any("hook" in s for s in p) and any("skills" in s for s in p) and any("tools" in s for s in p))
    def test_instruction_file_in_cwd(self):
        d = Path(tempfile.mkdtemp()); (d / "CLAUDE.md").write_text("x")
        self.assertTrue(any("CLAUDE.md" in s for s in g.context_problems(dict(self.CLEAN, cwd=str(d)))))
    def test_missing_init_refuses(self):
        f = Path(tempfile.mkdtemp()) / "s.jsonl"; f.write_text('{"type":"result"}\n')
        self.assertFalse(g.context_check(f)["ok"])


class Edges(unittest.TestCase):
    def test_all_malformed_is_not_all_valid(self):
        r = g.reconcile(["a", "b"], [{"id": "a", "valid": False}, {"id": "b", "valid": False}])
        self.assertFalse(r["all_valid"]); self.assertEqual(r["malformed"], 2)
    def test_string_false_is_invalid_and_valid_retry_supersedes(self):
        self.assertEqual(g.reconcile(["a"], [{"id": "a", "valid": "false"}])["malformed"], 1)
        self.assertEqual(g.reconcile(["a"], [{"id": "a", "valid": False}, {"id": "a"}])["completed"], 1)
    def test_missing_id_does_not_crash(self):
        g.reconcile(["a"], [{"x": 1}, {"id": "z"}])
    def test_second_init_event_checked(self):
        f = Path(tempfile.mkdtemp()) / "s.jsonl"
        ok = {"type": "system", "subtype": "init", "cwd": "/tmp", "model": "m"}
        f.write_text(json.dumps(ok) + "\n" + json.dumps(dict(ok, skills=["s"])) + "\n")
        self.assertFalse(g.context_check(f)["ok"])
    def test_absent_cwd_is_unobservable(self):
        self.assertTrue(g.context_problems({"model": "m"}))
    def test_slash_collision_free(self):
        d = tempfile.mkdtemp(); g.claim(d, "a/b", "x"); self.assertTrue(g.claim(d, "a_b", "y")["ok"])


class Cwd(unittest.TestCase):
    def test_inside_and_escape(self):
        root = Path(tempfile.mkdtemp()); (root / "wt").mkdir()
        self.assertTrue(g.check_cwd(root / "wt", root)["ok"])
        self.assertFalse(g.check_cwd(root.parent, root)["ok"])
        self.assertFalse(g.check_cwd(root / "nope", root)["ok"])
    def test_symlink_escape(self):
        root = Path(tempfile.mkdtemp()); out = Path(tempfile.mkdtemp()); (root / "l").symlink_to(out)
        self.assertFalse(g.check_cwd(root / "l", root)["ok"])


class Reconcile(unittest.TestCase):
    def test_unique_units_not_log_rows(self):
        rows = [{"id": "a"}, {"id": "a"}, {"id": "b", "valid": False}, {"id": "z"}]
        r = g.reconcile(["a", "b", "c"], rows)
        self.assertEqual((r["planned"], r["completed"], r["malformed"], r["missing"], r["log_rows"]), (3, 1, 1, 1, 4))
        self.assertEqual(r["duplicates"], {"a": 2}); self.assertEqual(r["unexpected"], ["z"]); self.assertFalse(r["done"])


if __name__ == "__main__":
    unittest.main()
