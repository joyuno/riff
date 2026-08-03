#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HOOK="$ROOT/hooks/riff-progress.sh"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

assert_json() {
  local output="$1"
  local filter="$2"
  if ! jq -e "$filter" <<<"$output" >/dev/null; then
    echo "FAIL: jq assertion failed: $filter" >&2
    echo "$output" >&2
    exit 1
  fi
}

run_hook() {
  local project="$1"
  local input="${2:-}"
  [[ -n "$input" ]] || input='{}'
  mkdir -p "$project/src/nested"
  (cd "$project/src/nested" && printf '%s' "$input" | bash "$HOOK")
}

# Valid v1 state is reported without writing legacy files.
project="$TMP_ROOT/valid"
mkdir -p "$project/.riff"
printf '%s\n' '{"cycle":2,"last_anchor":"abc123"}' > "$project/.riff/state.json"
output="$(run_hook "$project" '{"agent_name":"builder","total_tokens":120,"duration_ms":45}')"
assert_json "$output" '.continue == true'
assert_json "$output" '.additionalContext | contains("Cycle 2")'
assert_json "$output" '.additionalContext | contains("abc123")'
assert_json "$output" '.additionalContext | contains("builder")'
assert_json "$output" '.additionalContext | contains("120")'
assert_json "$output" '.additionalContext | contains("45")'
test ! -e "$project/.riff/riff-log.json"

# Invalid JSON degrades gracefully and does not overwrite state.
project="$TMP_ROOT/invalid"
mkdir -p "$project/.riff"
printf '%s\n' '{broken' > "$project/.riff/state.json"
before="$(cat "$project/.riff/state.json")"
output="$(run_hook "$project")"
assert_json "$output" '.continue == true'
assert_json "$output" '.additionalContext | contains("state.json")'
test "$(cat "$project/.riff/state.json")" = "$before"

# Missing required fields are rejected without creating files.
project="$TMP_ROOT/missing-fields"
mkdir -p "$project/.riff"
printf '%s\n' '{"cycle":1}' > "$project/.riff/state.json"
output="$(run_hook "$project")"
assert_json "$output" '.continue == true'
assert_json "$output" '.additionalContext | contains("필수 필드")'
test ! -e "$project/.riff/riff-log.json"

# A Riff directory without state is inactive.
project="$TMP_ROOT/no-state"
mkdir -p "$project/.riff"
output="$(run_hook "$project")"
assert_json "$output" '. == {"continue":true}'
test ! -e "$project/.riff/state.json"

# A non-Riff project is inactive.
project="$TMP_ROOT/no-riff"
mkdir -p "$project"
output="$(run_hook "$project")"
assert_json "$output" '. == {"continue":true}'

echo "PASS: riff-progress v1 state handling"
