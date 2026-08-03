#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP_ROOT="$(mktemp -d)"
OUTPUT="$(mktemp)"
trap 'rm -rf "$TMP_ROOT"; rm -f "$OUTPUT"' EXIT
cp -R "$ROOT/benchmarks" "$TMP_ROOT/benchmarks"

if ! bash "$TMP_ROOT/benchmarks/run-benchmark.sh" --dry-run >"$OUTPUT" 2>&1; then
  cat "$OUTPUT" >&2
  echo "FAIL: dry-run must work on Bash 3.2 without mapfile" >&2
  exit 1
fi

if grep -q 'mapfile: command not found' "$OUTPUT"; then
  cat "$OUTPUT" >&2
  echo "FAIL: Bash 4-only mapfile was used" >&2
  exit 1
fi

if grep -q 'unbound variable' "$OUTPUT"; then
  cat "$OUTPUT" >&2
  echo "FAIL: dry-run accessed an empty array under set -u" >&2
  exit 1
fi

grep -q '결과 디렉토리:' "$OUTPUT"
score_file="$(find "$TMP_ROOT/benchmarks/results" -name 'scores-with-riff-*.json' ! -name '*-latest.json' -print -quit)"
jq -e '.total_fixtures == 6' "$score_file" >/dev/null

filtered_root="$(mktemp -d)"
cp -R "$ROOT/benchmarks" "$filtered_root/benchmarks"
if ! bash "$filtered_root/benchmarks/run-benchmark.sh" --dry-run --fixture interview-ecommerce >"$filtered_root/out" 2>&1; then
  cat "$filtered_root/out" >&2
  echo "FAIL: documented ground-truth fixture id must be runnable" >&2
  rm -rf "$filtered_root"
  exit 1
fi
filtered_score="$(find "$filtered_root/benchmarks/results" -name 'scores-with-riff-*.json' ! -name '*-latest.json' -print -quit)"
jq -e '.total_fixtures == 1 and .fixture_results[0].fixture_id == "interview-ecommerce"' "$filtered_score" >/dev/null
rm -rf "$filtered_root"
echo "PASS: run-benchmark dry-run is Bash 3.2 compatible"
