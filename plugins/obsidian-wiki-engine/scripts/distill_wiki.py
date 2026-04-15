#!/usr/bin/env python3
"""
distill_wiki.py
=====================================

Purpose:
    Cheap-model RLM distillation orchestrator for the Obsidian Wiki Engine.
    Iterates over all wiki nodes needing RLM summaries, auto-detects the
    cheapest available LLM CLI, and generates three summary layers per concept:
    summary.md, bullets.md, deep.md.

    Fallback chain (strict — Ollama is fully deprecated):
        1. copilot  -> gpt-5-mini
        2. claude   -> claude-haiku-4-5
        3. gemini   -> gemini-3-flash-preview

Layer: Distill / Wiki

Usage:
    python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root
    python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root --source arch-docs
    python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root --engine claude
    python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root --dry-run

Related:
    - raw_manifest.py  (WikiSourceConfig + agent-memory.json)
    - wiki_builder.py  (consumes the rlm/ summaries it produces)
    - audit.py         (reports missing summaries)
"""
import sys
import os
import shutil
import shlex
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_manifest import WikiSourceConfig, now_iso

# ─── ENGINE REGISTRY (strict cheap-model only) ────────────────────────────────
# Ollama is fully deprecated for distillation tasks.
ENGINE_PRIORITY: List[Tuple[str, str]] = [
    ("copilot", "gpt-5-mini"),
    ("claude",  "claude-haiku-4-5"),
    ("gemini",  "gemini-3-flash-preview"),
]

# ─── PATH AUGMENTATION (stripped PATH in some environments) ──────────────────
_EXTRA_PATHS = [
    "/opt/homebrew/bin",
    "/usr/local/bin",
    os.path.expanduser("~/.local/bin"),
    os.path.expanduser("~/.npm-global/bin"),
    os.path.expanduser("~/n/bin"),
]
for _p in _EXTRA_PATHS:
    if _p not in os.environ.get("PATH", "") and Path(_p).exists():
        os.environ["PATH"] = _p + os.pathsep + os.environ.get("PATH", "")


def detect_engine(override: Optional[str] = None) -> Tuple[str, str]:
    """
    Detect the cheapest available LLM CLI on PATH.

    Args:
        override: Force a specific engine name (e.g. 'claude').

    Returns:
        (engine_name, model_name) tuple.

    Raises:
        SystemExit: If override is unknown or no engine is found.
    """
    if override:
        for engine, model in ENGINE_PRIORITY:
            if engine == override.lower():
                if shutil.which(engine):
                    return (engine, model)
                print(f"[ERROR] Engine '{override}' not found on PATH.")
                print(f"   Install: https://github.com/cli/{override}")
                sys.exit(1)
        print(f"[ERROR] Unknown engine '{override}'. Choose from: {[e for e, _ in ENGINE_PRIORITY]}")
        sys.exit(1)

    for engine, model in ENGINE_PRIORITY:
        if shutil.which(engine):
            print(f"[ENGINE] Using: {engine} ({model})")
            return (engine, model)

    print("[ERROR] No LLM CLI found on PATH.")
    print("   Install one of:")
    for engine, model in ENGINE_PRIORITY:
        print(f"     {engine} (model: {model})")
    sys.exit(1)


def build_prompt(layer: str, concept: str, content: str) -> str:
    """
    Build the distillation prompt for the given layer.

    Args:
        layer:   One of 'summary', 'bullets', 'deep'.
        concept: The concept slug being distilled.
        content: The raw wiki node content excerpt.

    Returns:
        Prompt string ready to send to the LLM.
    """
    base = f"Concept: {concept}\n\n{content}\n\n"
    if layer == "summary":
        return base + (
            "Write a concise 1-5 sentence summary of this concept. "
            "Focus on the most important idea. Plain prose, no headings, no bullets."
        )
    elif layer == "bullets":
        return base + (
            "List 6-10 key ideas from this concept as concise bullet points. "
            "Use '- ' prefix. No headings, no preamble."
        )
    elif layer == "deep":
        return base + (
            "Write a thorough multi-paragraph distillation of this concept. "
            "Cover the main ideas, important details, and relationships to related concepts. "
            "Use markdown headings where helpful."
        )
    return base + "Summarize this content."


def call_llm(
    engine: str,
    model: str,
    prompt: str,
    timeout: int = 120,
) -> Optional[str]:
    """
    Call the specified LLM CLI with the given prompt.

    Args:
        engine:  CLI name ('copilot', 'claude', 'gemini').
        model:   Model identifier string.
        prompt:  Full prompt payload.
        timeout: Subprocess timeout in seconds.

    Returns:
        Stripped LLM response string, or None on error.
    """
    if engine == "claude":
        cmd = ["claude", "--model", model, "-p", prompt, "--no-session-persistence"]
        stdin_text = ""
    elif engine == "gemini":
        cmd = ["gemini", "--model", model, "-p", prompt]
        stdin_text = ""
    elif engine == "copilot":
        cmd = ["copilot", "--model", model]
        stdin_text = prompt
    else:
        return None

    try:
        proc = subprocess.run(
            cmd,
            input=stdin_text or None,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=(sys.platform == "win32"),
        )
    except FileNotFoundError:
        print(f"[ERROR] CLI '{engine}' not found on PATH.")
        return None
    except subprocess.TimeoutExpired:
        print(f"[ERROR] {engine} timed out after {timeout}s.")
        return None

    if proc.returncode != 0 or not proc.stdout.strip():
        print(f"[ERROR] {engine} returned exit code {proc.returncode}")
        if proc.stderr:
            print(proc.stderr[:300])
        return None

    return proc.stdout.strip()


def write_rlm_layer(
    wiki_root: Path,
    concept: str,
    layer: str,
    content: str,
) -> None:
    """
    Write one RLM summary layer file to {wiki_root}/rlm/{concept}/{layer}.md.

    Args:
        wiki_root: Root of the wiki output directory.
        concept:   Concept slug.
        layer:     Layer name ('summary', 'bullets', 'deep').
        content:   Distilled text to write.
    """
    rlm_dir = wiki_root / "rlm" / concept
    rlm_dir.mkdir(parents=True, exist_ok=True)
    layer_path = rlm_dir / f"{layer}.md"

    layer_content = "\n".join([
        "---",
        f'concept: "{concept}"',
        f'layer: "{layer}"',
        f'generated_at: "{now_iso()}"',
        "---",
        "",
        f"# {layer.title()}",
        "",
        content,
        "",
    ])
    layer_path.write_text(layer_content, encoding="utf-8")


def distill_concept(
    concept: str,
    wiki_root: Path,
    engine: str,
    model: str,
    layers: List[str],
    dry_run: bool = False,
) -> bool:
    """
    Distill all requested layers for one concept.

    Reads the wiki node file as source content, calls the LLM for each layer,
    and writes the result to {wiki_root}/rlm/{concept}/

    Args:
        concept:   Concept slug (matches wiki/{concept}.md filename).
        wiki_root: Root of the wiki output directory.
        engine:    LLM CLI to use.
        model:     Model identifier.
        layers:    List of layer names to generate.
        dry_run:   If True, build prompts but do not call LLM.

    Returns:
        True on success, False if the wiki node file is missing.
    """
    wiki_node = wiki_root / "wiki" / f"{concept}.md"
    if not wiki_node.exists():
        print(f"  [SKIP] Wiki node not found: {wiki_node.name}")
        return False

    content = wiki_node.read_text(encoding="utf-8")

    for layer in layers:
        prompt = build_prompt(layer, concept, content[:3000])

        if dry_run:
            print(f"  [DRY] Would distill {concept}/{layer}.md via {engine}")
            continue

        print(f"  [RUN] {concept}/{layer}.md via {engine}...", end=" ", flush=True)
        result = call_llm(engine, model, prompt)
        if result:
            write_rlm_layer(wiki_root, concept, layer, result)
            print(f"OK ({len(result)} chars)")
        else:
            print("FAILED")

    return True


def get_concepts_needing_distillation(
    wiki_root: Path,
    layers: List[str],
    source_name: Optional[str] = None,
) -> List[str]:
    """
    Find all wiki node concepts that are missing one or more RLM layers.

    Args:
        wiki_root:   Root of the wiki output directory.
        layers:      Layer names to check for.
        source_name: Optional source filter (not yet implemented at this level).

    Returns:
        Sorted list of concept slugs needing distillation.
    """
    wiki_dir = wiki_root / "wiki"
    if not wiki_dir.exists():
        return []

    needs_distill = []
    for node_file in sorted(wiki_dir.glob("*.md")):
        if node_file.name.startswith("_"):
            continue
        concept = node_file.stem
        rlm_dir = wiki_root / "rlm" / concept
        missing = any(not (rlm_dir / f"{layer}.md").exists() for layer in layers)
        if missing:
            needs_distill.append(concept)

    return needs_distill


def main() -> None:
    """Parse CLI arguments and run the distillation pipeline."""
    parser = argparse.ArgumentParser(
        description="Distill wiki nodes into RLM summary layers using cheap cloud LLMs"
    )
    parser.add_argument("--wiki-root", required=True, help="Path to the wiki root directory")
    parser.add_argument("--source", default=None, help="Distill one named source only (filter by source label)")
    parser.add_argument("--engine", default=None, choices=["copilot", "claude", "gemini"],
                        help="Force a specific LLM CLI engine")
    parser.add_argument("--layers", default="summary,bullets,deep",
                        help="Comma-separated layers to generate (default: summary,bullets,deep)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be distilled without calling the LLM")
    args = parser.parse_args()

    wiki_root = Path(args.wiki_root).resolve()
    layers = [l.strip() for l in args.layers.split(",")]
    engine, model = detect_engine(args.engine)

    concepts = get_concepts_needing_distillation(wiki_root, layers)
    if not concepts:
        print("[OK] All wiki nodes already have RLM summaries.")
        return

    print(f"\n[DISTILL] {len(concepts)} concepts need distillation")
    print(f"          Engine: {engine} ({model})")
    print(f"          Layers: {layers}")
    print(f"          Wiki  : {wiki_root}\n")

    success = 0
    for concept in concepts:
        ok = distill_concept(concept, wiki_root, engine, model, layers, dry_run=args.dry_run)
        if ok:
            success += 1

    action = "planned" if args.dry_run else "completed"
    print(f"\n[DONE] Distillation {action}: {success}/{len(concepts)} concepts.")


if __name__ == "__main__":
    main()
