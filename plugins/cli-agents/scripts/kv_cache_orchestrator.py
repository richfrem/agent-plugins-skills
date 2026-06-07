#!/usr/bin/env python3
"""
KV Cache Orchestrator for llama-server slot save/restore.

Architectural pattern adapted from antirez/ds4 ds4_kvstore.c:
  - SHA-256 keyed disk-persistent cache (ds4 uses SHA-1)
  - Hit-frequency exponential decay with 6-hour half-life
  - Budget-based eviction by ascending score (lowest effective value evicted first)
  - Eviction score: (effective_hits + base) * tokens / file_size  (ds4 post-PR #177)
    base = 4.0 for anchor reasons (cold/evict/shutdown), 1.0 otherwise
  - Quant compatibility: saves record ctk/ctv; restore rejects if server config changed

Integration path: routing_proxy.py calls check_cache() → restore_slot() before
forwarding, then save_slot() in a background thread after the stream completes.
"""

import hashlib
import json
import math
import os
import threading
import time
import urllib.request
from typing import Optional

HALF_LIFE_SECONDS: int = 6 * 60 * 60  # 6-hour half-life (matches ds4)
_ANCHOR_REASONS = ("cold", "evict", "shutdown")
_MIN_EFFECTIVE_HITS = 0.01
_DEFAULT_BUDGET_BYTES = 4 * 1024 * 1024 * 1024  # 4 GiB


class KVCacheOrchestrator:
    """
    Proxy middleware for llama-server KV slot save/restore.

    One instance lives in routing_proxy at module level.  Thread-safe:
    all metadata reads/writes are protected by self._lock.
    """

    def __init__(
        self,
        cache_dir: str,
        llama_base_url: str = "http://localhost:8089",
        budget_bytes: int = _DEFAULT_BUDGET_BYTES,
        slot: int = 0,
        quant_config: Optional[dict] = None,
        max_tokens_per_entry: Optional[int] = None,
    ) -> None:
        self.cache_dir = cache_dir
        self.llama_base_url = llama_base_url.rstrip("/")
        self.budget_bytes = budget_bytes
        self.slot = slot
        self.quant_config = quant_config  # e.g. {"ctk": "q8_0", "ctv": "q8_0"}
        self.max_tokens_per_entry = max_tokens_per_entry
        self._lock = threading.Lock()
        self._slot_lock = threading.Lock()  # serializes save/restore API calls on single slot
        os.makedirs(cache_dir, exist_ok=True)

    # ------------------------------------------------------------------ #
    #  Cache key                                                           #
    # ------------------------------------------------------------------ #

    def cache_key(self, messages: list) -> str:
        """SHA-256 of system message content, handling string and parts-array formats."""
        parts = []
        for m in messages:
            if not isinstance(m, dict) or m.get("role") != "system":
                continue
            content = m.get("content", "")
            if isinstance(content, str):
                parts.append(content)
            elif isinstance(content, list):
                # OpenAI multimodal format: [{"type": "text", "text": "..."}]
                parts.append(" ".join(
                    p.get("text", "") for p in content
                    if isinstance(p, dict) and p.get("type") == "text"
                ))
        return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------ #
    #  File paths                                                          #
    # ------------------------------------------------------------------ #

    def _bin_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.bin")

    def _meta_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.json")

    # ------------------------------------------------------------------ #
    #  Cache presence check                                               #
    # ------------------------------------------------------------------ #

    def check_cache(self, key: str) -> bool:
        """True if a slot-state .bin file exists for this key."""
        return os.path.isfile(self._bin_path(key))

    # ------------------------------------------------------------------ #
    #  Restore (cache hit path)                                           #
    # ------------------------------------------------------------------ #

    def restore_slot(self, key: str) -> bool:
        """
        POST /slots/{slot}/restore to llama-server.

        Returns True on HTTP 2xx, False on any error (caller treats as miss).
        Rejects with False (no API call) if the saved quant config differs from
        the current server config — prevents silent garbage output on param changes.
        """
        if self.quant_config:
            meta = self._read_meta(key)
            if meta and meta.get("quant_config") and meta["quant_config"] != self.quant_config:
                print(f"[kv-cache] REJECT {key[:8]}... quant mismatch: "
                      f"saved={meta['quant_config']} current={self.quant_config}")
                return False

        path = self._bin_path(key)
        payload = json.dumps({"filename": path}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.llama_base_url}/slots/{self.slot}/restore",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self._slot_lock:
                with urllib.request.urlopen(req, timeout=5) as resp:
                    ok = resp.status < 400
            if ok:
                self._record_hit(key)
            return ok
        except Exception:
            return False

    # ------------------------------------------------------------------ #
    #  Save (cache miss path, call after stream completes)                #
    # ------------------------------------------------------------------ #

    def save_slot(self, key: str, tokens: int = 0) -> bool:
        """
        POST /slots/{slot}/save to llama-server.

        Writes metadata sidecar and runs budget eviction on success.
        tokens: estimated prompt token count — used in eviction scoring.
        Returns True on HTTP 2xx.
        """
        if self.max_tokens_per_entry and tokens > self.max_tokens_per_entry:
            print(f"[kv-cache] SKIP {key[:8]}... {tokens} tokens > limit "
                  f"({self.max_tokens_per_entry}), skipping save")
            return False
        path = self._bin_path(key)
        payload = json.dumps({"filename": path}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.llama_base_url}/slots/{self.slot}/save",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self._slot_lock:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    ok = resp.status < 400
            if ok:
                self._write_meta(key, "cold", tokens=tokens)
                self._maybe_evict()
            return ok
        except Exception:
            return False

    # ------------------------------------------------------------------ #
    #  Metadata helpers                                                    #
    # ------------------------------------------------------------------ #

    def _record_hit(self, key: str) -> None:
        meta_path = self._meta_path(key)
        with self._lock:
            meta = self._read_meta(key) or {}
            meta["hits"] = meta.get("hits", 0) + 1
            meta["last_used"] = int(time.time())
            with open(meta_path, "w") as f:
                json.dump(meta, f)

    def _write_meta(self, key: str, reason: str, tokens: int = 0) -> None:
        meta_path = self._meta_path(key)
        bin_path = self._bin_path(key)
        now = int(time.time())
        file_size = 0
        try:
            file_size = os.path.getsize(bin_path)
        except OSError:
            pass
        with self._lock:
            existing = self._read_meta(key) or {}
            meta = {
                "key": key,
                "reason": reason,
                "hits": existing.get("hits", 0),
                "created_at": existing.get("created_at", now),
                "last_used": now,
                "file_size": file_size,
                "tokens": tokens,
            }
            if self.quant_config:
                meta["quant_config"] = self.quant_config
            with open(meta_path, "w") as f:
                json.dump(meta, f)

    def _read_meta(self, key: str) -> Optional[dict]:
        meta_path = self._meta_path(key)
        try:
            with open(meta_path, "r") as f:
                return json.load(f)
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    #  Eviction                                                            #
    # ------------------------------------------------------------------ #

    def _eviction_score(self, meta: dict) -> float:
        """
        Higher score = higher value = keep.  Lower score = evict first.

        Matches ds4 post-PR #177:
          effective_hits = hits * exp2(-elapsed / HALF_LIFE_SECONDS)
          base = 4.0 for anchor reasons (cold/evict/shutdown), 1.0 otherwise
          score = (effective_hits + base) * tokens / file_size
        tokens falls back to 1 if not recorded (entries saved before this fix).
        """
        hits = float(meta.get("hits", 0))
        last_used = meta.get("last_used") or meta.get("created_at", 0)
        now = int(time.time())
        if last_used and now > last_used:
            elapsed = now - last_used
            hits = hits * math.pow(2.0, -elapsed / HALF_LIFE_SECONDS)
            if hits < _MIN_EFFECTIVE_HITS:
                hits = 0.0
        file_size = max(meta.get("file_size", 1), 1)
        base = 4.0 if meta.get("reason") in _ANCHOR_REASONS else 1.0
        tokens = max(meta.get("tokens", 0), 1)
        return (hits + base) * tokens / file_size

    def _maybe_evict(self) -> None:
        """Remove lowest-score entries until total disk usage is within budget."""
        with self._lock:
            entries: list[tuple[str, dict]] = []
            try:
                for fname in os.listdir(self.cache_dir):
                    if not fname.endswith(".json"):
                        continue
                    key = fname[:-5]
                    meta = self._read_meta(key)
                    if meta and os.path.isfile(self._bin_path(key)):
                        entries.append((key, meta))
            except OSError:
                return

            total = sum(m.get("file_size", 0) for _, m in entries)
            if total <= self.budget_bytes:
                return

            entries.sort(key=lambda x: self._eviction_score(x[1]))

            for key, meta in entries:
                if total <= self.budget_bytes:
                    break
                size = meta.get("file_size", 0)
                try:
                    os.remove(self._bin_path(key))
                    os.remove(self._meta_path(key))
                    total -= size
                    short = key[:8]
                    mib = size / (1024 * 1024)
                    print(f"[kv-cache] evicted {short}… ({mib:.1f} MiB)")
                except OSError:
                    pass
