#!/usr/bin/env bash
# Riff v1 Progress Hook — SubagentStop
# Reads .riff/state.json and injects the current Cycle context. Read-only.

set -euo pipefail

json_response() {
  local message="${1:-}"
  if [[ -z "$message" ]]; then
    printf '%s\n' '{"continue":true}'
    return
  fi

  local encoded
  encoded="$(printf '%s' "$message" | jq -Rs '.')"
  printf '{"continue":true,"additionalContext":%s}\n' "$encoded"
}

if ! command -v jq >/dev/null 2>&1; then
  printf '%s\n' '{"continue":true,"additionalContext":"[Riff Progress] 경고: jq가 없어 v1 상태 확인을 건너뜁니다."}'
  exit 0
fi

INPUT="$(cat)"

RIFF_DIR=""
CHECK_DIR="$(pwd)"
while [[ "$CHECK_DIR" != "/" ]]; do
  if [[ -d "$CHECK_DIR/.riff" ]]; then
    RIFF_DIR="$CHECK_DIR/.riff"
    break
  fi
  CHECK_DIR="$(dirname "$CHECK_DIR")"
done

if [[ -z "$RIFF_DIR" ]]; then
  json_response
  exit 0
fi

STATE_FILE="$RIFF_DIR/state.json"
if [[ ! -f "$STATE_FILE" ]]; then
  json_response
  exit 0
fi

if ! jq empty "$STATE_FILE" >/dev/null 2>&1; then
  json_response "[Riff Progress] 경고: .riff/state.json이 올바른 JSON이 아니어서 상태 주입을 건너뜁니다."
  exit 0
fi

if ! jq -e '
  (.cycle | type == "number" and floor == . and . >= 0) and
  (.last_anchor | type == "string" and length > 0)
' "$STATE_FILE" >/dev/null 2>&1; then
  json_response "[Riff Progress] 경고: .riff/state.json 필수 필드(cycle, last_anchor)가 유효하지 않아 상태 주입을 건너뜁니다."
  exit 0
fi

CYCLE="$(jq -r '.cycle' "$STATE_FILE")"
LAST_ANCHOR="$(jq -r '.last_anchor' "$STATE_FILE")"

TOTAL_TOKENS="$(printf '%s' "$INPUT" | jq -r '.total_tokens // 0' 2>/dev/null || printf '0')"
DURATION_MS="$(printf '%s' "$INPUT" | jq -r '.duration_ms // 0' 2>/dev/null || printf '0')"
AGENT_NAME="$(printf '%s' "$INPUT" | jq -r '.agent_name // "unknown"' 2>/dev/null || printf 'unknown')"

[[ "$TOTAL_TOKENS" =~ ^[0-9]+$ ]] || TOTAL_TOKENS=0
[[ "$DURATION_MS" =~ ^[0-9]+$ ]] || DURATION_MS=0
[[ -n "$AGENT_NAME" ]] || AGENT_NAME="unknown"

json_response "[Riff Progress] ${AGENT_NAME} 완료 (${TOTAL_TOKENS}토큰, ${DURATION_MS}ms). 현재 Cycle ${CYCLE}, 마지막 앵커 ${LAST_ANCHOR}. CANVAS STATUS와 실제 작업 상태를 맞춘 뒤 다음 작업을 진행하세요."
