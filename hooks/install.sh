#!/usr/bin/env bash
# Install the single optional Riff SessionStart hook for Claude Code.

set -euo pipefail

DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --help|-h)
      echo "사용법: bash install.sh [--dry-run]"
      echo "  --dry-run  설정을 쓰지 않고 결과만 출력"
      exit 0
      ;;
    *) echo "알 수 없는 옵션: $arg" >&2; exit 1 ;;
  esac
done

HOOKS_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_SCRIPT="$HOOKS_DIR/session-start-canvas.sh"
SETTINGS_FILE="$HOME/.claude/settings.json"
SETTINGS_DIR="$(dirname "$SETTINGS_FILE")"

if [[ ! -f "$HOOK_SCRIPT" ]]; then
  echo "session-start-canvas.sh를 찾을 수 없습니다: $HOOK_SCRIPT" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "설치에는 jq가 필요합니다: brew install jq 또는 apt install jq" >&2
  exit 1
fi

if [[ ! -x "$HOOK_SCRIPT" ]]; then
  if $DRY_RUN; then
    echo "[DRY-RUN] chmod +x $HOOK_SCRIPT"
  else
    chmod +x "$HOOK_SCRIPT"
  fi
fi

NEW_HOOK="$(jq -n --arg cmd "bash $HOOK_SCRIPT" '{matcher:"", command:$cmd}')"

JQ_FILTER='
  .hooks = (.hooks // {})
  | .hooks.SubagentStop = (
      (.hooks.SubagentStop // [])
      | if type == "array" then . else [] end
      | map(select(((.command // "") | endswith("/riff-progress.sh")) | not))
    )
  | .hooks.SessionStart = (
      (.hooks.SessionStart // [])
      | if type == "array" then . else [] end
      | map(select(((.command // "") | endswith("/session-start-canvas.sh")) | not))
      | . + [$canvas]
    )
'

render_settings() {
  local source="$1"
  jq --argjson canvas "$NEW_HOOK" "$JQ_FILTER" "$source"
}

if [[ ! -f "$SETTINGS_FILE" ]]; then
  if $DRY_RUN; then
    jq -n --argjson canvas "$NEW_HOOK" '{hooks:{SessionStart:[$canvas]}}'
    exit 0
  fi
  mkdir -p "$SETTINGS_DIR"
  jq -n --argjson canvas "$NEW_HOOK" '{hooks:{SessionStart:[$canvas]}}' > "$SETTINGS_FILE"
else
  if ! jq empty "$SETTINGS_FILE" >/dev/null 2>&1; then
    echo "settings.json이 올바른 JSON이 아닙니다: $SETTINGS_FILE" >&2
    exit 1
  fi

  if $DRY_RUN; then
    render_settings "$SETTINGS_FILE"
    exit 0
  fi

  TMP_FILE="$SETTINGS_FILE.tmp.$$"
  render_settings "$SETTINGS_FILE" > "$TMP_FILE"
  mv "$TMP_FILE" "$SETTINGS_FILE"
fi

echo "Riff SessionStart hook 설치 완료"
echo "  hook: $HOOK_SCRIPT"
echo "  settings: $SETTINGS_FILE"
echo "  실행 시점: Claude Code 세션 시작/재개 시 1회"
echo "  참고: 기존 Riff riff-progress SubagentStop 등록은 제거했습니다."
