"""
HuggingFace Init Script

Purpose: Validates environment, tests API connectivity, ensures dataset structure
and card exist on HuggingFace Hub. Run this once per project onboarding.

Token setup:
    macOS:  Add to ~/.zshrc   → export HUGGING_FACE_TOKEN=hf_xxxxx
    WSL:    Add to Windows env → WSLENV=HUGGING_FACE_TOKEN/u
    Linux:  Add to ~/.bashrc  → export HUGGING_FACE_TOKEN=hf_xxxxx

    The token should NEVER go in .env (which is committed).

Project-level vars go in .env:
    HUGGING_FACE_USERNAME=<your-username>
    HUGGING_FACE_REPO=<your-model-repo>
    HUGGING_FACE_DATASET_PATH=<your-dataset-repo>
"""
import sys
import json
import asyncio
import argparse
from pathlib import Path

# Resolve imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
try:
    from hf_config import get_hf_config, validate_config
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "huggingface-utils" / "scripts"))
    from hf_config import get_hf_config, validate_config


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


def main():
    parser = argparse.ArgumentParser(description="HuggingFace Init")
    parser.add_argument("--validate-only", action="store_true", help="Validate without making changes")
    args = parser.parse_args()

    result = asyncio.run(full_init(args.validate_only))
    print(json.dumps(result, indent=2))

    if result.get("status") != "valid":
        sys.exit(1)


if __name__ == "__main__":
    main()
