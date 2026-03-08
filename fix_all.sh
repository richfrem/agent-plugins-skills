#!/bin/bash
# A script to rewrite hardcoded bash paths in SKILL.md and scripts to be local relative paths

find plugins -name "SKILL.md" -type f | while read file; do
    sed -i '' 's|python3 plugins/[A-Za-z0-9_-]*/skills/[A-Za-z0-9_-]*/scripts/|python3 ./scripts/|g' "$file"
    sed -i '' 's|python3 plugins/[A-Za-z0-9_-]*/scripts/|python3 ../../scripts/|g' "$file"
done
