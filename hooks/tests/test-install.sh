#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INSTALLER="$ROOT/hooks/install.sh"
TMP_HOME="$(mktemp -d)"
trap 'rm -rf "$TMP_HOME"' EXIT

mkdir -p "$TMP_HOME/.claude"
cat > "$TMP_HOME/.claude/settings.json" <<'JSON'
{
  "theme": "dark",
  "hooks": {
    "SubagentStop": [
      {"matcher":"","command":"bash /old/riff-progress.sh"},
      {"matcher":"","command":"bash /other/subagent-hook.sh"}
    ],
    "SessionStart": [
      {"matcher":"","command":"bash /other/session-hook.sh"}
    ]
  }
}
JSON

HOME="$TMP_HOME" bash "$INSTALLER" >/dev/null
HOME="$TMP_HOME" bash "$INSTALLER" >/dev/null

settings="$TMP_HOME/.claude/settings.json"
jq -e '.theme == "dark"' "$settings" >/dev/null
jq -e '[.hooks.SubagentStop[] | select(.command | contains("riff-progress.sh"))] | length == 0' "$settings" >/dev/null
jq -e '[.hooks.SubagentStop[] | select(.command == "bash /other/subagent-hook.sh")] | length == 1' "$settings" >/dev/null
jq -e '[.hooks.SessionStart[] | select(.command | contains("session-start-canvas.sh"))] | length == 1' "$settings" >/dev/null
jq -e '[.hooks.SessionStart[] | select(.command == "bash /other/session-hook.sh")] | length == 1' "$settings" >/dev/null

echo "PASS: installer keeps only the Riff SessionStart hook"
