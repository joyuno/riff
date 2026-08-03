#!/usr/bin/env bash
# Measure the median wall-clock overhead of a Riff medium-cycle command.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCORER="$SCRIPT_DIR/scoring/speed_tax.py"
RESULTS_DIR="${SPEED_TAX_RESULTS_DIR:-$SCRIPT_DIR/results}"

BASELINE_MS=""
RIFF_MS=""
BUDGET_PERCENT="15"
REPETITIONS="${REPETITIONS:-3}"
FIXTURE="${SPEED_TAX_FIXTURE:-$SCRIPT_DIR/fixtures/depth/ambiguous-brief-notes.md}"

usage() {
  cat <<'USAGE'
Usage:
  run-speed-tax.sh --baseline-ms 100,105,110 --riff-ms 110,115,120 [--budget-percent 15]
  BASELINE_COMMAND='...' RIFF_COMMAND='...' run-speed-tax.sh [--repetitions 3] [--fixture path]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --baseline-ms) BASELINE_MS="$2"; shift 2 ;;
    --riff-ms) RIFF_MS="$2"; shift 2 ;;
    --budget-percent) BUDGET_PERCENT="$2"; shift 2 ;;
    --repetitions) REPETITIONS="$2"; shift 2 ;;
    --fixture) FIXTURE="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ ! "$REPETITIONS" =~ ^[1-9][0-9]*$ ]]; then
  echo "REPETITIONS must be a positive integer" >&2
  exit 2
fi

measure_command() {
  local command="$1"
  python3 - "$command" "$FIXTURE" <<'PY'
import subprocess
import sys
import time
from pathlib import Path

command, fixture_path = sys.argv[1:]
fixture = Path(fixture_path).read_bytes()
started = time.monotonic_ns()
completed = subprocess.run(
    command,
    shell=True,
    input=fixture,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
elapsed_ms = max(1, round((time.monotonic_ns() - started) / 1_000_000))
if completed.returncode != 0:
    raise SystemExit(completed.returncode)
print(elapsed_ms)
PY
}

append_sample() {
  local current="$1"
  local value="$2"
  if [[ -z "$current" ]]; then
    printf '%s' "$value"
  else
    printf '%s,%s' "$current" "$value"
  fi
}

if [[ -z "$BASELINE_MS" || -z "$RIFF_MS" ]]; then
  if [[ -z "${BASELINE_COMMAND:-}" || -z "${RIFF_COMMAND:-}" ]]; then
    echo "Provide both timing lists or BASELINE_COMMAND and RIFF_COMMAND" >&2
    exit 2
  fi
  if [[ ! -f "$FIXTURE" ]]; then
    echo "Fixture not found: $FIXTURE" >&2
    exit 2
  fi

  BASELINE_MS=""
  RIFF_MS=""
  index=1
  while [[ "$index" -le "$REPETITIONS" ]]; do
    baseline_value="$(measure_command "$BASELINE_COMMAND")"
    riff_value="$(measure_command "$RIFF_COMMAND")"
    BASELINE_MS="$(append_sample "$BASELINE_MS" "$baseline_value")"
    RIFF_MS="$(append_sample "$RIFF_MS" "$riff_value")"
    index=$((index + 1))
  done
fi

mkdir -p "$RESULTS_DIR"
timestamp="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
report="$RESULTS_DIR/speed-tax-$timestamp.json"

set +e
python3 "$SCORER" \
  --baseline-ms "$BASELINE_MS" \
  --riff-ms "$RIFF_MS" \
  --budget-percent "$BUDGET_PERCENT" \
  --output "$report" >/dev/null
status=$?
set -e

if [[ "$status" -eq 2 ]]; then
  exit 2
fi

baseline_median="$(jq -r '.baseline_median_ms' "$report")"
riff_median="$(jq -r '.riff_median_ms' "$report")"
overhead="$(jq -r '.overhead_percent' "$report")"

if [[ "$status" -eq 0 ]]; then
  verdict="PASS"
else
  verdict="FAIL"
fi

printf '%s: baseline=%sms riff=%sms overhead=%s%% budget=%s%%\n' \
  "$verdict" "$baseline_median" "$riff_median" "$overhead" "$BUDGET_PERCENT"
printf 'Report: %s\n' "$report"
exit "$status"
