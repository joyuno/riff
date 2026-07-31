#!/usr/bin/env bash
# SessionStart: _workspace/CANVAS.md 존재 시 STATUS 섹션을 컨텍스트로 주입
#
# Claude Code 훅 설정 (settings.json):
# {
#   "hooks": {
#     "SessionStart": [{
#       "matcher": "",
#       "command": "bash /path/to/session-start-canvas.sh"
#     }]
#   }
# }

set -euo pipefail

# ── 프로젝트 루트 감지 (_workspace/CANVAS.md 가 있는 곳, riff-progress.sh 와 동일 패턴) ──
CANVAS=""
CHECK_DIR="$(pwd)"
while [ "$CHECK_DIR" != "/" ]; do
  if [ -f "$CHECK_DIR/_workspace/CANVAS.md" ]; then
    CANVAS="$CHECK_DIR/_workspace/CANVAS.md"
    break
  fi
  CHECK_DIR="$(dirname "$CHECK_DIR")"
done

[ -n "$CANVAS" ] || exit 0

STATUS=$(awk '/^## STATUS/{f=1;next}/^## /{f=0}f' "$CANVAS" | head -12)
[ -n "$STATUS" ] || exit 0

# jq 없이는 안전한 JSON 이스케이프(따옴표·개행)를 보장할 수 없음 → graceful 스킵
command -v jq &>/dev/null || exit 0

MSG="[riff] CANVAS.md 감지 — 현재 STATUS:
${STATUS}
재개 전 canvas-lint(references/prove/canvas-lint.md)로 어긋남 확인 후 STATUS의 '다음 액션'부터."

# jq -Rs 로 특수문자(따옴표·개행 등)를 안전하게 JSON 문자열로 인코딩
ENCODED_MSG=$(printf '%s' "$MSG" | jq -Rs '.')

printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}\n' "$ENCODED_MSG"
