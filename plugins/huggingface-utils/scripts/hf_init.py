"""
hf_init.py
=====================================

Purpose:
    Validates environment, tests API connectivity, and ensures dataset structure on HF.

Layer: Execution / Initialization

Usage Examples:
    pythonhf_init.py
    pythonhf_init.py --validate-only

Supported Object Types:
    None

CLI Arguments:
    --validate-only: Validate without making changes.

Input Files:
    - .env file for credentials

Output:
    - JSON string printed containing initialization status report.

Key Functions:
    full_init(): Run full HF initialization sequence.

Script Dependencies:
    sys, json, asyncio, argparse, pathlib, hf_config

Consumed by:
    - hf-init skill
"""
import sys
import json
import asyncio
import argparse
from pathlib import Path

# Resolve imports (locally symlinked)
sys.path.insert(0, str(Path(__file__).parent))
try:
    from hf_config import get_hf_config, validate_config
except ImportError as e:
    print(f"Failed to import local hf_config: {e}")
    sys.exit(1)


async def full_init(validate_only: bool = False) -> dict:
    """Run full HF initialization sequence."""

    # Step 1: Validate config
    result = validate_config()
    if result["status"] != "valid":
        return result

    if validate_only:
        result["mode"] = "validate_only"
        return result

    # Step 2: Ensure dataset structure
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hf-upload" / "scripts"))
        from hf_upload import ensure_dataset_structure, ensure_dataset_card

        config = get_hf_config()

        structure_ok = await ensure_dataset_structure(config)
        result["dataset_structure"] = "created" if structure_ok else "failed"

        card_ok = await ensure_dataset_card(config)
        result["dataset_card"] = "created" if card_ok else "failed"

        result["next_steps"] = [
            f"Visit: https://huggingface.co/datasets/{config.dataset_repo_id}",
            "Verify lineage/, data/, metadata/ folders exist",
            "Configure your project's persistence plugin to use hf-upload primitives"
        ]
    except ImportError as e:
        result["warning"] = f"Could not import upload module: {e}. Install: pip install huggingface_hub"

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="HuggingFace Init")
    parser.add_argument("--validate-only", action="store_true", help="Validate without making changes")
    args = parser.parse_args()

    result = asyncio.run(full_init(args.validate_only))
    print(json.dumps(result, indent=2))

    if result.get("status") != "valid":
        sys.exit(1)


if __name__ == "__main__":
    main()
