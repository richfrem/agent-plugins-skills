#!/usr/bin/env python3
"""
Tests for kv_cache_orchestrator.py — TDD first pass.

Architectural pattern inspired by antirez/ds4 ds4_kvstore.c:
SHA-keyed disk-persistent cache with hit-frequency decay and budget eviction.
"""

import hashlib
import json
import os
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.dirname(__file__))
from kv_cache_orchestrator import KVCacheOrchestrator, HALF_LIFE_SECONDS


def _make_cache(tmpdir, budget_bytes=4 * 1024 * 1024 * 1024, quant_config=None):
    return KVCacheOrchestrator(
        cache_dir=tmpdir,
        llama_base_url="http://localhost:8089",
        budget_bytes=budget_bytes,
        quant_config=quant_config,
    )


def _mock_urlopen_ok():
    resp = MagicMock()
    resp.status = 200
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


class TestCacheKeyGeneration(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cache = _make_cache(self.tmpdir)

    def test_same_system_prompt_same_key(self):
        msgs = [{"role": "system", "content": "You are a helpful assistant."}]
        self.assertEqual(self.cache.cache_key(msgs), self.cache.cache_key(msgs))

    def test_key_is_sha256_hex(self):
        msgs = [{"role": "system", "content": "test prompt"}]
        key = self.cache.cache_key(msgs)
        self.assertEqual(len(key), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in key))

    def test_user_messages_excluded_from_key(self):
        # Only system messages form the cache key — user turn is variable
        base = [{"role": "system", "content": "sys prompt"}]
        with_user_a = base + [{"role": "user", "content": "question A"}]
        with_user_b = base + [{"role": "user", "content": "question B entirely different"}]
        self.assertEqual(self.cache.cache_key(with_user_a), self.cache.cache_key(with_user_b))

    def test_empty_system_prompt_is_stable(self):
        msgs = [{"role": "user", "content": "hello"}]
        self.assertEqual(self.cache.cache_key(msgs), self.cache.cache_key(msgs))

    def test_key_matches_manual_sha256(self):
        content = "exact system content"
        msgs = [{"role": "system", "content": content}]
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        self.assertEqual(self.cache.cache_key(msgs), expected)

    def test_multiple_system_messages_joined(self):
        msgs = [
            {"role": "system", "content": "part one"},
            {"role": "user", "content": "ignored"},
            {"role": "system", "content": "part two"},
        ]
        expected = hashlib.sha256("part one\npart two".encode("utf-8")).hexdigest()
        self.assertEqual(self.cache.cache_key(msgs), expected)

    def test_content_as_parts_array_produces_stable_key(self):
        msgs = [{"role": "system", "content": [{"type": "text", "text": "You are helpful."}]}]
        key1 = self.cache.cache_key(msgs)
        key2 = self.cache.cache_key(msgs)
        self.assertEqual(key1, key2)
        self.assertEqual(len(key1), 64)

    def test_content_as_parts_and_string_same_text_same_key(self):
        text = "You are a helpful assistant."
        string_msgs = [{"role": "system", "content": text}]
        parts_msgs = [{"role": "system", "content": [{"type": "text", "text": text}]}]
        self.assertEqual(self.cache.cache_key(string_msgs), self.cache.cache_key(parts_msgs))

    def test_content_as_parts_array_no_text_type_gives_empty_string(self):
        # Parts with no "text" type (e.g. image-only) → treated as empty system content
        msgs = [{"role": "system", "content": [{"type": "image_url", "image_url": "..."}]}]
        no_system_msgs = [{"role": "user", "content": "hello"}]
        self.assertEqual(self.cache.cache_key(msgs), self.cache.cache_key(no_system_msgs))


class TestCacheHitSkipsPrefill(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cache = _make_cache(self.tmpdir)

    def _plant_bin(self, key):
        path = os.path.join(self.tmpdir, f"{key}.bin")
        with open(path, "wb") as f:
            f.write(b"fake kv state data")
        return path

    def test_check_cache_true_when_bin_exists(self):
        key = self.cache.cache_key([{"role": "system", "content": "existing prompt"}])
        self._plant_bin(key)
        self.assertTrue(self.cache.check_cache(key))

    def test_check_cache_false_when_no_bin(self):
        key = self.cache.cache_key([{"role": "system", "content": "unknown prompt"}])
        self.assertFalse(self.cache.check_cache(key))

    def test_restore_calls_llama_server_restore_endpoint(self):
        key = self.cache.cache_key([{"role": "system", "content": "known prompt"}])
        self._plant_bin(key)

        with patch("urllib.request.urlopen", return_value=_mock_urlopen_ok()) as mock_open:
            result = self.cache.restore_slot(key)

        self.assertTrue(result)
        req = mock_open.call_args[0][0]
        self.assertIn("/slots/0/restore", req.full_url)
        body = json.loads(req.data)
        self.assertIn(key, body["filename"])
        self.assertTrue(body["filename"].endswith(".bin"))

    def test_restore_increments_hit_count(self):
        key = self.cache.cache_key([{"role": "system", "content": "hits test"}])
        self._plant_bin(key)
        meta_path = os.path.join(self.tmpdir, f"{key}.json")
        with open(meta_path, "w") as f:
            json.dump({"key": key, "hits": 3, "created_at": 0, "last_used": 0,
                       "file_size": 18, "reason": "cold"}, f)

        with patch("urllib.request.urlopen", return_value=_mock_urlopen_ok()):
            self.cache.restore_slot(key)

        meta = json.loads(open(meta_path).read())
        self.assertEqual(meta["hits"], 4)

    def test_restore_returns_false_on_server_error(self):
        key = self.cache.cache_key([{"role": "system", "content": "error case"}])
        self._plant_bin(key)

        with patch("urllib.request.urlopen", side_effect=Exception("connection refused")):
            result = self.cache.restore_slot(key)

        self.assertFalse(result)


class TestCacheMissSavesAfterResponse(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cache = _make_cache(self.tmpdir)

    def test_save_calls_llama_server_save_endpoint(self):
        key = self.cache.cache_key([{"role": "system", "content": "brand new prompt"}])
        self.assertFalse(self.cache.check_cache(key))

        def fake_urlopen(req, timeout=None):
            # Simulate server writing the .bin file
            with open(os.path.join(self.tmpdir, f"{key}.bin"), "wb") as f:
                f.write(b"saved kv state")
            return _mock_urlopen_ok()

        with patch("urllib.request.urlopen", side_effect=fake_urlopen) as mock_open:
            result = self.cache.save_slot(key)

        self.assertTrue(result)
        req = mock_open.call_args[0][0]
        self.assertIn("/slots/0/save", req.full_url)
        body = json.loads(req.data)
        self.assertIn(key, body["filename"])

    def test_save_writes_metadata_sidecar(self):
        key = self.cache.cache_key([{"role": "system", "content": "meta test"}])

        def fake_urlopen(req, timeout=None):
            with open(os.path.join(self.tmpdir, f"{key}.bin"), "wb") as f:
                f.write(b"x" * 100)
            return _mock_urlopen_ok()

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            self.cache.save_slot(key)

        meta_path = os.path.join(self.tmpdir, f"{key}.json")
        self.assertTrue(os.path.isfile(meta_path))
        meta = json.loads(open(meta_path).read())
        self.assertEqual(meta["key"], key)
        self.assertEqual(meta["reason"], "cold")
        self.assertEqual(meta["hits"], 0)
        self.assertIn("created_at", meta)
        self.assertIn("file_size", meta)
        self.assertIn("tokens", meta)

    def test_save_returns_false_on_server_error(self):
        key = self.cache.cache_key([{"role": "system", "content": "fail case"}])

        with patch("urllib.request.urlopen", side_effect=Exception("timeout")):
            result = self.cache.save_slot(key)

        self.assertFalse(result)
        self.assertFalse(self.cache.check_cache(key))


class TestDiskBudgetEviction(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # 1 MiB budget — three 500 KiB entries will exceed it
        self.cache = _make_cache(self.tmpdir, budget_bytes=1024 * 1024)

    def _plant_entry(self, label, hits, age_hours, tokens=1000):
        key = hashlib.sha256(label.encode()).hexdigest()
        bin_path = os.path.join(self.tmpdir, f"{key}.bin")
        with open(bin_path, "wb") as f:
            f.write(b"x" * 512 * 1024)  # 500 KiB
        meta = {
            "key": key,
            "reason": "cold",
            "hits": hits,
            "created_at": int(time.time()) - int(age_hours * 3600),
            "last_used": int(time.time()) - int(age_hours * 3600),
            "file_size": 512 * 1024,
            "tokens": tokens,
        }
        with open(os.path.join(self.tmpdir, f"{key}.json"), "w") as f:
            json.dump(meta, f)
        return key

    def test_oldest_least_hit_entry_evicted_first(self):
        # Three 500 KiB entries, budget 1 MiB → must evict at least one
        k0 = self._plant_entry("prompt_zero_hits_old", hits=0, age_hours=24)
        k1 = self._plant_entry("prompt_one_hit_medium", hits=1, age_hours=12)
        k2 = self._plant_entry("prompt_five_hits_recent", hits=5, age_hours=1)

        self.cache._maybe_evict()

        # k0 should be evicted (lowest effective_hits * score)
        self.assertFalse(os.path.isfile(os.path.join(self.tmpdir, f"{k0}.bin")),
                         "Zero-hit old entry should have been evicted")
        # k2 (most hits, most recent) should survive
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, f"{k2}.bin")),
                        "High-hit recent entry should survive eviction")

    def test_no_eviction_within_budget(self):
        # Only one 500 KiB entry — comfortably under 1 MiB budget
        k0 = self._plant_entry("single_entry", hits=0, age_hours=1)

        self.cache._maybe_evict()

        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, f"{k0}.bin")),
                        "Entry within budget should not be evicted")

    def test_both_bin_and_json_removed_on_eviction(self):
        k0 = self._plant_entry("evict_both_files", hits=0, age_hours=48)
        k1 = self._plant_entry("keep_this_one", hits=10, age_hours=1)
        self._plant_entry("third_entry", hits=0, age_hours=48)

        self.cache._maybe_evict()

        if not os.path.isfile(os.path.join(self.tmpdir, f"{k0}.bin")):
            self.assertFalse(os.path.isfile(os.path.join(self.tmpdir, f"{k0}.json")),
                             "JSON sidecar must be removed alongside .bin on eviction")

    def test_high_token_entry_outscores_low_token_entry(self):
        # Same hits, same file_size, same age — more tokens = higher eviction score = kept longer
        def _meta(tokens):
            return {
                "reason": "cold",
                "hits": 1,
                "created_at": int(time.time()),
                "last_used": int(time.time()),
                "file_size": 512 * 1024,
                "tokens": tokens,
            }
        score_low = self.cache._eviction_score(_meta(tokens=100))
        score_high = self.cache._eviction_score(_meta(tokens=5000))
        self.assertGreater(score_high, score_low,
            "Entry that saved more tokens should have higher eviction score (kept longer)")


class TestDifferentPromptsDifferentKeys(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cache = _make_cache(self.tmpdir)

    def test_claude_copilot_delegation_get_separate_keys(self):
        claude_msgs = [{"role": "system", "content":
            "You are Claude Code, Anthropic's AI for software engineering tasks. "
            "Tool definitions follow..."}]
        copilot_msgs = [{"role": "system", "content":
            "You are GitHub Copilot, an AI programming assistant. "
            "You can edit files, run shell commands, search your codebase..."}]
        delegation_msgs = [{"role": "system", "content":
            "You are a lightweight delegation agent. Answer concisely."}]

        keys = {
            "claude": self.cache.cache_key(claude_msgs),
            "copilot": self.cache.cache_key(copilot_msgs),
            "delegation": self.cache.cache_key(delegation_msgs),
        }

        self.assertEqual(len(set(keys.values())), 3,
                         "Each CLI's system prompt must produce a unique cache key")

    def test_whitespace_difference_produces_different_key(self):
        msgs_a = [{"role": "system", "content": "You are a helpful assistant."}]
        msgs_b = [{"role": "system", "content": "You are a helpful assistant. "}]
        self.assertNotEqual(self.cache.cache_key(msgs_a), self.cache.cache_key(msgs_b))

    def test_slot_parameter_respected(self):
        cache0 = KVCacheOrchestrator(self.tmpdir, slot=0)
        cache1 = KVCacheOrchestrator(self.tmpdir, slot=1)
        key = cache0.cache_key([{"role": "system", "content": "test"}])

        with patch("urllib.request.urlopen", return_value=_mock_urlopen_ok()) as m:
            # Plant a bin so restore proceeds
            with open(os.path.join(self.tmpdir, f"{key}.bin"), "wb") as f:
                f.write(b"data")
            cache0.restore_slot(key)
            url0 = m.call_args[0][0].full_url
            cache1.restore_slot(key)
            url1 = m.call_args[0][0].full_url

        self.assertIn("/slots/0/restore", url0)
        self.assertIn("/slots/1/restore", url1)


class TestQuantValidation(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def _plant_bin(self, key):
        path = os.path.join(self.tmpdir, f"{key}.bin")
        with open(path, "wb") as f:
            f.write(b"fake kv state")

    def _plant_meta(self, key, quant_config, tokens=500):
        meta = {
            "key": key,
            "reason": "cold",
            "hits": 2,
            "created_at": int(time.time()),
            "last_used": int(time.time()),
            "file_size": 13,
            "tokens": tokens,
            "quant_config": quant_config,
        }
        with open(os.path.join(self.tmpdir, f"{key}.json"), "w") as f:
            json.dump(meta, f)

    def test_restore_rejects_mismatched_quant(self):
        cache = _make_cache(self.tmpdir, quant_config={"ctk": "q4_0", "ctv": "q4_0"})
        key = cache.cache_key([{"role": "system", "content": "test prompt"}])
        self._plant_bin(key)
        self._plant_meta(key, quant_config={"ctk": "q8_0", "ctv": "q8_0"})

        with patch("urllib.request.urlopen") as mock_open:
            result = cache.restore_slot(key)

        self.assertFalse(result, "Should reject without API call when quant config differs")
        mock_open.assert_not_called()

    def test_restore_accepts_matching_quant(self):
        quant = {"ctk": "q8_0", "ctv": "q8_0"}
        cache = _make_cache(self.tmpdir, quant_config=quant)
        key = cache.cache_key([{"role": "system", "content": "test prompt"}])
        self._plant_bin(key)
        self._plant_meta(key, quant_config=quant)

        with patch("urllib.request.urlopen", return_value=_mock_urlopen_ok()):
            result = cache.restore_slot(key)

        self.assertTrue(result, "Should proceed to API call when quant config matches")

    def test_restore_accepts_entry_with_no_quant_recorded(self):
        # Entries saved before the quant fix have no quant_config in sidecar — don't reject them
        cache = _make_cache(self.tmpdir, quant_config={"ctk": "q8_0", "ctv": "q8_0"})
        key = cache.cache_key([{"role": "system", "content": "legacy entry"}])
        self._plant_bin(key)
        # Plant meta without quant_config field
        meta = {"key": key, "reason": "cold", "hits": 0, "created_at": 0,
                "last_used": 0, "file_size": 13, "tokens": 0}
        with open(os.path.join(self.tmpdir, f"{key}.json"), "w") as f:
            json.dump(meta, f)

        with patch("urllib.request.urlopen", return_value=_mock_urlopen_ok()):
            result = cache.restore_slot(key)

        self.assertTrue(result, "Legacy entries without quant_config should not be rejected")

    def test_save_records_quant_config_in_sidecar(self):
        quant = {"ctk": "q8_0", "ctv": "q8_0"}
        cache = _make_cache(self.tmpdir, quant_config=quant)
        key = cache.cache_key([{"role": "system", "content": "quant save test"}])

        def fake_urlopen(req, timeout=None):
            with open(os.path.join(self.tmpdir, f"{key}.bin"), "wb") as f:
                f.write(b"saved state")
            return _mock_urlopen_ok()

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            cache.save_slot(key, tokens=750)

        meta = json.loads(open(os.path.join(self.tmpdir, f"{key}.json")).read())
        self.assertEqual(meta["quant_config"], quant)
        self.assertEqual(meta["tokens"], 750)


class TestSlotLock(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cache = _make_cache(self.tmpdir)

    def _plant_bin(self, key):
        path = os.path.join(self.tmpdir, f"{key}.bin")
        with open(path, "wb") as f:
            f.write(b"fake kv state")

    def test_slot_lock_serializes_concurrent_slot_operations(self):
        key = self.cache.cache_key([{"role": "system", "content": "lock test"}])
        self._plant_bin(key)

        order = []
        save_in_urlopen = threading.Event()
        save_may_finish = threading.Event()

        def recording_urlopen(req, timeout=None):
            if "save" in req.full_url:
                order.append("save-start")
                save_in_urlopen.set()
                save_may_finish.wait(timeout=3)
                order.append("save-end")
            else:
                order.append("restore")
            return _mock_urlopen_ok()

        def fake_save_urlopen(req, timeout=None):
            with open(os.path.join(self.tmpdir, f"{key}.bin"), "wb") as f:
                f.write(b"saved")
            return recording_urlopen(req, timeout)

        with patch("urllib.request.urlopen", side_effect=recording_urlopen):
            save_thread = threading.Thread(
                target=lambda: self.cache.save_slot(key, tokens=100)
            )
            save_thread.start()
            save_in_urlopen.wait(timeout=3)  # wait until save holds _slot_lock

            restore_thread = threading.Thread(
                target=lambda: self.cache.restore_slot(key)
            )
            restore_thread.start()
            time.sleep(0.03)  # give restore time to block on _slot_lock
            save_may_finish.set()

            save_thread.join(timeout=3)
            restore_thread.join(timeout=3)

        restore_idx = order.index("restore")
        save_end_idx = order.index("save-end")
        self.assertGreater(restore_idx, save_end_idx,
            "restore must wait for save to release _slot_lock before calling llama-server")


class TestMaxTokensGuard(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_save_skips_oversized_entry(self):
        cache = KVCacheOrchestrator(
            cache_dir=self.tmpdir,
            llama_base_url="http://localhost:8089",
            max_tokens_per_entry=4000,
        )
        key = cache.cache_key([{"role": "system", "content": "oversized prompt"}])

        with patch("urllib.request.urlopen") as mock_open:
            result = cache.save_slot(key, tokens=5000)

        self.assertFalse(result, "save_slot should return False when tokens exceeds limit")
        mock_open.assert_not_called()

    def test_save_proceeds_within_limit(self):
        cache = KVCacheOrchestrator(
            cache_dir=self.tmpdir,
            llama_base_url="http://localhost:8089",
            max_tokens_per_entry=4000,
        )
        key = cache.cache_key([{"role": "system", "content": "within limit prompt"}])

        def fake_urlopen(req, timeout=None):
            with open(os.path.join(self.tmpdir, f"{key}.bin"), "wb") as f:
                f.write(b"saved state")
            return _mock_urlopen_ok()

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = cache.save_slot(key, tokens=3999)

        self.assertTrue(result, "save_slot should proceed when tokens is within limit")


if __name__ == "__main__":
    unittest.main()
