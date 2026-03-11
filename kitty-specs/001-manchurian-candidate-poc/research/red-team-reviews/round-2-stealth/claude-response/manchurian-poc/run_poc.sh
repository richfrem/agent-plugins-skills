#!/bin/bash
# Manchurian Candidate POC - Full Run Script
set -e

echo "============================================================"
echo " MANCHURIAN CANDIDATE POC - Full Demonstration"
echo "============================================================"
echo ""
echo "Step 1: Generating poisoned image artifact..."
python3 artifacts/create_poisoned_image.py

echo ""
echo "Step 2: Running agent pipeline simulation..."
python3 pipeline_simulator.py artifacts/sample_batch_001.jpg

echo ""
echo "Step 3: Displaying forensic evidence..."
echo ""
echo "--- .env contents ---"
cat .env 2>/dev/null || echo "(no .env file)"

echo ""
echo "--- Hash Timeline ---"
cat forensics/hash_timeline.json 2>/dev/null || echo "(no timeline)"

echo ""
echo "--- Execution Proof ---"
cat forensics/execution_proof.json 2>/dev/null || echo "(no proof file)"

echo ""
echo "============================================================"
echo " POC COMPLETE"
echo "============================================================"
