#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/outputs" "$TMP/results"

for scenario in depth-ambiguous-notes depth-ambiguous-tracker; do
  for run in 1 2 3; do
    cat > "$TMP/outputs/$scenario-$run.txt" <<'OUT'
depth 프로파일: 복잡 (신호 4/8)
FRAME 질문: 사용자는 누구이고 성공 기준은 무엇인가?
## STATUS
- 활성 가정: 첫 버전은 개인용이다.
OUT
  done
done

DEPTH_RESULTS_DIR="$TMP/results" bash "$ROOT/benchmarks/run-depth-reproducibility.sh" \
  --outputs-dir "$TMP/outputs" --repetitions 3 >/dev/null

report="$(find "$TMP/results" -name 'depth-reproducibility-*.json' -print -quit)"
jq -e '.passed == true and (.fixtures | length) == 2' "$report" >/dev/null
echo "PASS: depth reproducibility stored-output runner"
