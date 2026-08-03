#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCORER="$SCRIPT_DIR/scoring/depth_reproducibility.py"
RESULTS_DIR="${DEPTH_RESULTS_DIR:-$SCRIPT_DIR/results}"
OUTPUTS_DIR=""
REPETITIONS="${REPETITIONS:-3}"
FIXTURE_FILTER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --outputs-dir) OUTPUTS_DIR="$2"; shift 2 ;;
    --repetitions) REPETITIONS="$2"; shift 2 ;;
    --fixture) FIXTURE_FILTER="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: run-depth-reproducibility.sh [--outputs-dir DIR] [--repetitions 3] [--fixture SCENARIO]"
      exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

[[ "$REPETITIONS" =~ ^[1-9][0-9]*$ ]] || { echo "repetitions must be positive" >&2; exit 2; }
if [[ -z "$OUTPUTS_DIR" && -z "${DEPTH_COMMAND:-}" ]]; then
  echo "Provide --outputs-dir or DEPTH_COMMAND" >&2
  exit 2
fi

mkdir -p "$RESULTS_DIR"
timestamp="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
raw_dir="$RESULTS_DIR/depth-outputs-$timestamp"
mkdir -p "$raw_dir"
fixture_reports=()
failed=0

for ground_truth in "$SCRIPT_DIR"/ground-truth/depth-*.json; do
  scenario="$(jq -r '.scenario' "$ground_truth")"
  [[ -z "$FIXTURE_FILTER" || "$scenario" == "$FIXTURE_FILTER" ]] || continue
  fixture_name="${scenario#depth-}"
  fixture_path="$SCRIPT_DIR/fixtures/depth/${fixture_name/ambiguous-/ambiguous-brief-}.md"
  output_args=()

  run=1
  while [[ "$run" -le "$REPETITIONS" ]]; do
    if [[ -n "$OUTPUTS_DIR" ]]; then
      output_path="$OUTPUTS_DIR/$scenario-$run.txt"
    else
      output_path="$raw_dir/$scenario-$run.txt"
      if ! sh -c "$DEPTH_COMMAND" < "$fixture_path" > "$output_path"; then
        echo "Depth command failed: $scenario run $run" >&2
        exit 2
      fi
    fi
    [[ -f "$output_path" ]] || { echo "Missing output: $output_path" >&2; exit 2; }
    output_args+=(--output "$output_path")
    run=$((run + 1))
  done

  fixture_report="$raw_dir/$scenario.json"
  if ! python3 "$SCORER" --ground-truth "$ground_truth" "${output_args[@]}" --report "$fixture_report" >/dev/null; then
    failed=1
  fi
  fixture_reports+=("$fixture_report")
done

[[ ${#fixture_reports[@]} -gt 0 ]] || { echo "No matching fixtures" >&2; exit 2; }
report="$RESULTS_DIR/depth-reproducibility-$timestamp.json"
python3 - "$report" "${fixture_reports[@]}" <<'PY'
import json
import sys
from pathlib import Path

destination = Path(sys.argv[1])
fixtures = [json.loads(Path(path).read_text(encoding="utf-8")) for path in sys.argv[2:]]
report = {"fixtures": fixtures, "passed": all(item["passed"] for item in fixtures)}
destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

if [[ "$failed" -eq 0 ]]; then verdict="PASS"; else verdict="FAIL"; fi
echo "$verdict: depth reproducibility report: $report"
exit "$failed"
