#!/usr/bin/env python3
"""jev_router.py - Zero-Token Latent Decision-Tree Task Router (JEV Router).

Implements in-process non-generative Joint-Embedding Vector (JEV) task routing (<1ms latency, 0 tokens)
based on the Platonic Representation Hypothesis (arXiv:2610.39302, Balestriero & LeCun).

Shields frontier model quotas (Claude, Codex, Gemini Argon) by routing routine
engineering chores to OpenRouter micro-models (0.5B-3B, 30B MoE) or local inference.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class RoutingDecision:
    """Zero-token routing decision output by JEV Router."""

    task_id: Optional[str]
    description: str
    tier: str  # TIER_1_MICRO, TIER_2_LOCAL, TIER_3_FRONTIER
    recommended_runtime: str  # openrouter, llama, claude, codex, agy
    recommended_model: str
    complexity_class: str  # MECHANICAL_CHORE, CODING_SYNTAX, GENERAL_TRIAGE, EPISTEMIC_ARCHITECTURAL
    intent: str  # READ_ONLY, STATE_CHANGING
    confidence: float
    scores: Dict[str, float]
    tokens_consumed: int
    latency_ms: float
    offline_fallback: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JEVRouter:
    """In-process non-generative Latent Decision-Tree Router (Tier 0)."""

    DIM = 512
    TOKEN_RE = re.compile(r"[a-z0-9_\-\./]+")

    # Calibrated anchor seeds representing Platonic domain centroids
    ANCHORS: Dict[str, List[str]] = {
        "MECHANICAL_CHORE": [
            "format markdown table columns align pipe whitespace",
            "fix invalid trailing comma in json schema block sort keys",
            "update copyright year file headers comments",
            "reformat docstrings conform to google docstring args returns",
            "clean trailing whitespace single newline EOF markdown",
            "sort list tags alphabetical ascending order",
            "convert bullet list numbered list",
            "pretty print json 2-space indentation",
            "replace deprecated markdown image syntax html figure",
            "extract url links verify https",
            "fix typo variable name spelling rename identifier",
            "add type hint str int signature def",
            "sort import statements isort grouping",
            "format git commit message subject imperative mood 50 char",
            "remove unused imported module sys os",
            "normalize yaml frontmatter separators three dashes",
            "replace hardcoded path string tempfile",
            "format code fence language identifier python bash",
            "validate schema fields non-empty required",
            "rename key dictionary draft manifest"
        ],
        "CODING_SYNTAX": [
            "write pytest unit test function verifying sha256 hash",
            "implement helper function parse jsonl yield valid objects",
            "add optional command-line flag argparse pass runner",
            "implement exponential backoff retry decorator max_retries delay",
            "calculate cosine similarity float vectors sqrt sum",
            "read git commit log subprocess check_output commit hashes",
            "unit test pytest raises ValueError reject invalid input",
            "construct python dataclass fields agent mission expires",
            "scaffold bash script check port listening curl",
            "implement sliding window token counter character length",
            "create context manager record execution time milliseconds",
            "parse iso 8601 utc timestamp elapsed seconds",
            "scaffold ast visitor python find function def docstring",
            "dictionary merge preserve nested keys overwrite",
            "unit test mock http 500 response external api retry"
        ],
        "GENERAL_TRIAGE": [
            "read missions directory extract priority_score sorted markdown list",
            "scan commit messages main categorize feat fix docs refactor chore",
            "compare tags across manifests identify orphan tags single mission",
            "inspect cognitive backlog inbox jsonl candidate interest statements",
            "parse chronicle entries count entries logged by claude gemini codex qwen",
            "triage incoming issues classify priority P0 P1 P2",
            "summarize git diff status files modified insertions deletions"
        ],
        "EPISTEMIC_ARCHITECTURAL": [
            "derive mathematical proof non-generative jepa vicreg regularizer convergence platonic manifold sample complexity autoregressive llm",
            "design orthogonal procrustes alignment algorithm heterogeneous embedding spaces svd rotation metric preservation orthogonal group O(d)",
            "formulate popperian research mission anti-asch epistemic resistance adversarial consensus cascades multi-agent falsification criteria",
            "resolve constitutional doctrinal conflict protocol 128 autonomous lifecycle protocol 78 human verification gate",
            "deep cognitive root-cause analysis autoregressive linguistic sycophancy multi-agent jury deliberation axiomatic mathematical defense",
            "architect 4-tier macro-moe scheduling system balance apple silicon unified memory cloud micro-models frontier rate limits token economics",
            "derive information-theoretic bounds mutual information code execution traces autonomous agents",
            "develop formal specification zero-knowledge proof verification pipeline lora fine-tuning platonic traces",
            "evaluate asymptotic computational complexity memory safety bounds distributed graph planning sovereign memory",
            "formulate epistemic foundation axiomatic rules protocol 134 autonomous self-directed inquiry popperian falsification"
        ]
    }

    # Model catalog mapping for each tier
    MODEL_TIERS = {
        "MECHANICAL_CHORE": ("openrouter", "meta-llama/llama-3.2-3b-instruct"),
        "CODING_SYNTAX": ("openrouter", "qwen/qwen3-coder-30b-a3b-instruct"),
        "GENERAL_TRIAGE": ("openrouter", "meta-llama/llama-3.2-1b-instruct"),
        "EPISTEMIC_ARCHITECTURAL": ("claude", "claude-3-5-sonnet-20241022"),
        "OFFLINE": ("llama", "local-server")
    }

    def __init__(self) -> None:
        """Initialize JEV router and compute centroid normal vectors."""
        self.centroids: Dict[str, List[float]] = {}
        self._calibrate()

    @staticmethod
    def _hash_feature(s: str) -> int:
        """Fast 32-bit FNV-1a hash for deterministic token and n-gram projection."""
        h = 2166136261
        for ch in s:
            h = (h ^ ord(ch)) * 16777619 & 0xFFFFFFFF
        return h

    def text_to_latent(self, text: str) -> List[float]:
        """Project raw text to D-dimensional normalized latent vector (<0.1ms, 0 tokens)."""
        dim = self.DIM
        vec = [0.0] * dim
        tokens = self.TOKEN_RE.findall(text.lower())
        n = len(tokens)

        for i, t in enumerate(tokens):
            h = self._hash_feature(t)
            idx = h % dim
            sign = 1.0 if ((h >> 16) & 1) else -1.0
            vec[idx] += sign

            if i + 1 < n:
                bg = f"{t}_{tokens[i+1]}"
                hbg = self._hash_feature(bg)
                vec[hbg % dim] += 0.8 if ((hbg >> 16) & 1) else -0.8

        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 1e-9:
            vec = [v / norm for v in vec]
        return vec

    def _calibrate(self) -> None:
        """Compute centroid normal vectors for each domain from anchor sets."""
        for domain, anchors in self.ANCHORS.items():
            acc = [0.0] * self.DIM
            for text in anchors:
                z = self.text_to_latent(text)
                for i in range(self.DIM):
                    acc[i] += z[i]
            norm = math.sqrt(sum(v * v for v in acc))
            if norm > 1e-9:
                self.centroids[domain] = [v / norm for v in acc]
            else:
                self.centroids[domain] = acc

    @staticmethod
    def _dot(v1: List[float], v2: List[float]) -> float:
        """Compute inner product between two normalized vectors."""
        return sum(a * b for a, b in zip(v1, v2))

    def evaluate_intent(self, text: str) -> str:
        """Level 1 Constitutional Gate: Classify READ_ONLY vs STATE_CHANGING."""
        lower = text.lower()
        mutating_verbs = [
            "fix ", "update ", "modify ", "replace ", "rename ", "delete ",
            "write ", "create ", "format ", "convert ", "sort ", "clean ",
            "add ", "patch ", "implement ", "refactor ", "scaffold "
        ]
        is_mutating = any(v in lower for v in mutating_verbs)
        return "STATE_CHANGING" if is_mutating else "READ_ONLY"

    def route_task(
        self,
        description: str,
        task_id: Optional[str] = None,
        offline: bool = False,
    ) -> RoutingDecision:
        """Route task through hierarchical latent hyperplanes (<1ms, 0 tokens)."""
        t0 = time.perf_counter()

        # Step 1: Project task into latent manifold
        z = self.text_to_latent(description)

        # Step 2: Level 1 Constitutional intent
        intent = self.evaluate_intent(description)

        # Step 3: Compute inner-product similarity against domain centroids
        scores = {domain: self._dot(z, c) for domain, c in self.centroids.items()}

        s_arch = scores.get("EPISTEMIC_ARCHITECTURAL", 0.0)
        s_mech = scores.get("MECHANICAL_CHORE", 0.0)
        s_code = scores.get("CODING_SYNTAX", 0.0)
        s_triage = scores.get("GENERAL_TRIAGE", 0.0)

        # Architectural Firewall Split
        arch_boost = 0.0
        arch_markers = [
            "proof", "derive", "procrustes", "platonic", "vicreg",
            "epistemic", "sycophancy", "asch", "manifold", "constitutional",
            "doctrinal", "information-theoretic", "asymptotic", "axiomatic"
        ]
        lower = description.lower()
        if any(m in lower for m in arch_markers):
            arch_boost += 0.25

        effective_arch_score = s_arch + arch_boost

        if effective_arch_score > max(s_mech, s_code, s_triage) or effective_arch_score > 0.40:
            complexity = "EPISTEMIC_ARCHITECTURAL"
            tier = "TIER_3_FRONTIER"
            if any(m in lower for m in ["proof", "procrustes", "derive", "mathematical"]):
                runtime = "agy"
                model = "gemini-4-argon"
            else:
                runtime = "claude"
                model = "claude-3-5-sonnet-20241022"
            conf = min(0.99, max(0.65, effective_arch_score))
        else:
            routine_scores = {
                "MECHANICAL_CHORE": s_mech,
                "CODING_SYNTAX": s_code,
                "GENERAL_TRIAGE": s_triage,
            }
            complexity = max(routine_scores.keys(), key=lambda k: routine_scores[k])
            conf = routine_scores[complexity]

            if offline:
                tier = "TIER_2_LOCAL"
                runtime, model = self.MODEL_TIERS["OFFLINE"]
            else:
                tier = "TIER_1_MICRO"
                runtime, model = self.MODEL_TIERS[complexity]

        latency_ms = (time.perf_counter() - t0) * 1000.0

        return RoutingDecision(
            task_id=task_id,
            description=description,
            tier=tier,
            recommended_runtime=runtime,
            recommended_model=model,
            complexity_class=complexity,
            intent=intent,
            confidence=round(conf, 4),
            scores={k: round(v, 4) for k, v in scores.items()},
            tokens_consumed=0,
            latency_ms=round(latency_ms, 3),
            offline_fallback=offline,
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="JEV Router: Zero-Token Latent Task Router"
    )
    parser.add_argument("description", nargs="?", help="Task description string")
    parser.add_argument("--batch", help="Path to JSON batch file of tasks")
    parser.add_argument("--offline", action="store_true", help="Force local inference fallback")
    parser.add_argument("--format", choices=["text", "json", "cli-flags"], default="text")

    args = parser.parse_args()
    router = JEVRouter()

    if args.batch:
        with open(args.batch) as f:
            tasks = json.load(f)
        decisions = []
        for t in tasks:
            d = router.route_task(
                description=t.get("description", ""),
                task_id=t.get("id"),
                offline=args.offline,
            )
            decisions.append(d.to_dict())
        if args.format == "json":
            print(json.dumps(decisions, indent=2))
        else:
            print(f"Routed {len(decisions)} tasks:")
            for d in decisions:
                print(f"[{d['task_id'] or 'TASK'}] -> {d['tier']} | {d['recommended_runtime']}/{d['recommended_model']} ({d['complexity_class']}, {d['latency_ms']:.2f}ms)")
        return

    if not args.description:
        parser.print_help()
        sys.exit(1)

    decision = router.route_task(args.description, offline=args.offline)
    if args.format == "json":
        print(json.dumps(decision.to_dict(), indent=2))
    elif args.format == "cli-flags":
        print(f"--runtime {decision.recommended_runtime} --model {decision.recommended_model}")
    else:
        print("=== JEV Zero-Token Latent Routing Decision ===")
        print(f"Task:            {decision.description}")
        print(f"Tier:            {decision.tier}")
        print(f"Runtime:         {decision.recommended_runtime}")
        print(f"Model:           {decision.recommended_model}")
        print(f"Complexity:      {decision.complexity_class}")
        print(f"Intent:          {decision.intent}")
        print(f"Confidence:      {decision.confidence:.4f}")
        print(f"Tokens Consumed: {decision.tokens_consumed} tokens (Zero-Token Guarantee)")
        print(f"Latency:         {decision.latency_ms:.3f} ms")


if __name__ == "__main__":
    main()
