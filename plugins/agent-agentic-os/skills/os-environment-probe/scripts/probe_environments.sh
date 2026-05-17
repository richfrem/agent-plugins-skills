#!/usr/bin/env bash
# Non-interactive probe script for commonly used AI CLIs. Safe: uses --version or explain "test" where available.
set -euo pipefail

report_file="environment_probe_report.txt"
> "$report_file"

echo "Probing AI CLIs at $(date --iso-8601=seconds)" | tee -a "$report_file"

check_cmd() {
  local name="$1" cmd="$2"
  echo "Checking $name..." | tee -a "$report_file"
  if command -v $(echo "$cmd" | awk '{print $1}') >/dev/null 2>&1; then
    echo "  Command present; running probe" | tee -a "$report_file"
    if out=$($cmd 2>&1 | head -n 3); then
      echo "  ✓ $name: $out" | tee -a "$report_file"
    else
      echo "  ✗ $name: probe failed" | tee -a "$report_file"
    fi
  else
    echo "  ✗ $name: not installed" | tee -a "$report_file"
  fi
}

check_cmd "Gemini CLI" "gemini --version"
check_cmd "Copilot CLI" "gh copilot explain \"test\" 2>&1 | head -n 3"
check_cmd "Cursor CLI" "cursor --version"


echo "Probe complete. Report written to $report_file" | tee -a "$report_file"
