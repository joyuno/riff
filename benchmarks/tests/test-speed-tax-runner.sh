#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNNER="$ROOT/benchmarks/run-speed-tax.sh"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

SPEED_TAX_RESULTS_DIR="$TMP_ROOT/pass" bash "$RUNNER" \
  --baseline-ms 100,110,105 \
  --riff-ms 110,120,115 \
  --budget-percent 15 > "$TMP_ROOT/pass.out"

pass_report="$(find "$TMP_ROOT/pass" -name 'speed-tax-*.json' -print -quit)"
jq -e '.passed == true and .overhead_percent == 9.5238' "$pass_report" >/dev/null
grep -q 'PASS' "$TMP_ROOT/pass.out"

set +e
SPEED_TAX_RESULTS_DIR="$TMP_ROOT/fail" bash "$RUNNER" \
  --baseline-ms 100,100,100 \
  --riff-ms 120,120,120 \
  --budget-percent 15 > "$TMP_ROOT/fail.out"
status=$?
set -e

test "$status" -eq 1
fail_report="$(find "$TMP_ROOT/fail" -name 'speed-tax-*.json' -print -quit)"
jq -e '.passed == false and .overhead_percent == 20' "$fail_report" >/dev/null
grep -q 'FAIL' "$TMP_ROOT/fail.out"

echo "PASS: speed-tax runner prerecorded timing mode"
