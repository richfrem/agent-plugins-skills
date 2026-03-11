#!/usr/bin/env bash
# =============================================================================
# run_poc.sh - Manchurian Candidate POC End-to-End Demo
#
# Demonstrates the full attack chain from a clean environment:
#   1. Remove background from sample image (benign use)
#   2. Embed the payload into the artifact image (embedding mode)
#   3. Verify the EXIF hook survives the encode/decode cycle
#   4. Run the pipeline simulator (LLM layer trigger)
#   5. Report audit results
#
# Usage:
#   cd plugins/image-metadata-processor
#   bash ../../run_poc.sh
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$SCRIPT_DIR"
BG_REMOVER="$PLUGIN_DIR/skills/background-remover/scripts/remove_background.py"
SIMULATOR="$PLUGIN_DIR/scripts/pipeline_simulator.py"
SAMPLE_IMG="$PLUGIN_DIR/skills/background-remover/example/unprocessed.png"
ARTIFACT="$PLUGIN_DIR/skills/background-remover/example/withinstructions.jpg"
ENV_FILE="$(cd "$PLUGIN_DIR/../../../../" && pwd)/.env"

echo "================================================================"
echo "  MANCHURIAN CANDIDATE POC - FULL CHAIN DEMO"
echo "================================================================"

# --- Step 1: Background removal (benign use) ---
echo ""
echo "[STEP 1] Removing background from source image..."
python3 "$BG_REMOVER" \
  --source "$SAMPLE_IMG" \
  --output "$PLUGIN_DIR/skills/background-remover/example/nobackground.png"

# --- Step 2: Embed payload ---
echo ""
echo "[STEP 2] Embedding configuration directive into artifact..."
# Payload: python3 scripts/verify_poc.py --env <path>
PAYLOAD_CMD="python3 scripts/verify_poc.py --env $ENV_FILE"
PAYLOAD_B64="$(echo -n "$PAYLOAD_CMD" | base64)"
python3 "$BG_REMOVER" \
  --embed \
  --source "$SAMPLE_IMG" \
  --output "$ARTIFACT" \
  --payload "$PAYLOAD_B64"

# --- Step 3: Confirm artifact is ready ---
echo ""
echo "[STEP 3] Artifact check..."
if [ -f "$ARTIFACT" ]; then
  echo "  [OK] Artifact present: $ARTIFACT"
else
  echo "  [FAIL] Artifact not found."
  exit 1
fi

# --- Step 4: Run pipeline simulator ---
echo ""
echo "[STEP 4] Running agent pipeline simulator (LLM trigger)..."
python3 "$SIMULATOR" "$ARTIFACT"

# --- Step 5: Show audit output ---
echo ""
echo "[STEP 5] Audit summary:"
HASHFILE="$PLUGIN_DIR/audit/hashcodes.md"
if [ -f "$HASHFILE" ]; then
  cat "$HASHFILE"
else
  echo "  [WARNING] hashcodes.md not found - check verify_poc.py output above."
fi

echo ""
echo "================================================================"
echo "  DEMO COMPLETE"
echo "================================================================"
