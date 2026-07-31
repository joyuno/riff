#!/bin/bash
# Riff Hooks Installer
# Claude Code settings.json에 riff-progress, session-start-canvas 훅을 자동 등록합니다.
#
# 사용법:
#   bash install.sh
#   bash install.sh --dry-run   # 변경 없이 결과만 미리 확인

set -euo pipefail

# ── 색상 출력 헬퍼 ─────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; RESET='\033[0m'
info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }

# ── 옵션 파싱 ─────────────────────────────────────────────────────────────────
DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --help|-h)
      echo "사용법: bash install.sh [--dry-run]"
      echo "  --dry-run  변경 없이 예상 결과만 출력"
      exit 0
      ;;
    *) error "알 수 없는 옵션: $arg"; exit 1 ;;
  esac
done

# ── 경로 설정 ─────────────────────────────────────────────────────────────────
HOOKS_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_SCRIPT="$HOOKS_DIR/riff-progress.sh"
HOOK_SCRIPT_CANVAS="$HOOKS_DIR/session-start-canvas.sh"
SETTINGS_FILE="$HOME/.claude/settings.json"
SETTINGS_DIR="$(dirname "$SETTINGS_FILE")"

# ── 요약 출력 함수 (앞에 정의해야 호출 가능) ──────────────────────────────────
show_summary() {
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo " Riff 훅 설치 완료"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo " riff-progress 훅        (SubagentStop) : $HOOK_SCRIPT"
  echo " session-start-canvas 훅 (SessionStart) : $HOOK_SCRIPT_CANVAS"
  echo " 설정 파일                              : $SETTINGS_FILE"
  echo ""
  echo " 다음 단계:"
  echo "   1. 프로젝트 루트에 .riff/ 디렉토리를 생성하세요."
  echo "      mkdir -p <프로젝트루트>/.riff"
  echo "   2. Claude Code 를 재시작하면 훅이 활성화됩니다."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

info "Riff Hooks Installer 시작"
info "riff-progress 스크립트 경로:        $HOOK_SCRIPT"
info "session-start-canvas 스크립트 경로: $HOOK_SCRIPT_CANVAS"
info "설정 파일 경로:                     $SETTINGS_FILE"
$DRY_RUN && warn "DRY-RUN 모드 — 실제 파일은 변경되지 않습니다."
echo ""

# ── 사전 확인 ─────────────────────────────────────────────────────────────────

# 1) 훅 스크립트 존재 확인
if [ ! -f "$HOOK_SCRIPT" ]; then
  error "riff-progress.sh 를 찾을 수 없습니다: $HOOK_SCRIPT"
  error "install.sh 와 riff-progress.sh 가 같은 디렉토리에 있어야 합니다."
  exit 1
fi
success "riff-progress.sh 확인됨"

if [ ! -f "$HOOK_SCRIPT_CANVAS" ]; then
  error "session-start-canvas.sh 를 찾을 수 없습니다: $HOOK_SCRIPT_CANVAS"
  error "install.sh 와 session-start-canvas.sh 가 같은 디렉토리에 있어야 합니다."
  exit 1
fi
success "session-start-canvas.sh 확인됨"

# 2) 실행 권한 부여
for script in "$HOOK_SCRIPT" "$HOOK_SCRIPT_CANVAS"; do
  if [ ! -x "$script" ]; then
    if $DRY_RUN; then
      info "[DRY-RUN] chmod +x $script"
    else
      chmod +x "$script"
      success "실행 권한 부여: $script"
    fi
  else
    success "실행 권한 이미 설정됨: $script"
  fi
done

# 3) jq 설치 확인
if ! command -v jq &>/dev/null; then
  warn "jq 가 설치되지 않았습니다. 훅이 graceful하게 실패하지만 진행률 추적은 비활성화됩니다."
  warn "설치 방법: macOS → brew install jq | Ubuntu → sudo apt install jq"
fi

# 4) ~/.claude/ 디렉토리 생성
if [ ! -d "$SETTINGS_DIR" ]; then
  if $DRY_RUN; then
    info "[DRY-RUN] mkdir -p $SETTINGS_DIR"
  else
    mkdir -p "$SETTINGS_DIR"
    success "디렉토리 생성: $SETTINGS_DIR"
  fi
fi

# ── settings.json 처리 ────────────────────────────────────────────────────────

# 새 훅 엔트리 정의
NEW_HOOK=$(jq -n \
  --arg cmd "bash $HOOK_SCRIPT" \
  '{"matcher": "", "command": $cmd}')
NEW_HOOK_CANVAS=$(jq -n \
  --arg cmd "bash $HOOK_SCRIPT_CANVAS" \
  '{"matcher": "", "command": $cmd}')

# settings.json 이 없으면 최소 구조로 생성
if [ ! -f "$SETTINGS_FILE" ]; then
  if $DRY_RUN; then
    info "[DRY-RUN] settings.json 새로 생성:"
    jq -n --argjson progress "$NEW_HOOK" --argjson canvas "$NEW_HOOK_CANVAS" \
      '{hooks: {SubagentStop: [$progress], SessionStart: [$canvas]}}'
  else
    jq -n --argjson progress "$NEW_HOOK" --argjson canvas "$NEW_HOOK_CANVAS" \
      '{hooks: {SubagentStop: [$progress], SessionStart: [$canvas]}}' > "$SETTINGS_FILE"
    success "settings.json 생성 및 훅 등록 완료"
  fi
  echo ""
  show_summary
  exit 0
fi

# settings.json 유효성 검사
if ! jq empty "$SETTINGS_FILE" 2>/dev/null; then
  error "settings.json 이 유효한 JSON이 아닙니다: $SETTINGS_FILE"
  error "파일을 수동으로 확인하거나 백업 후 삭제하세요."
  exit 1
fi

# 중복 등록 확인 (동일한 command 가 이미 있는지, 훅별로 독립 판단)
EXISTING_PROGRESS=$(jq \
  --arg cmd "bash $HOOK_SCRIPT" \
  '[.hooks.SubagentStop // [] | .[] | select(.command == $cmd)] | length' \
  "$SETTINGS_FILE" 2>/dev/null || echo "0")
EXISTING_CANVAS=$(jq \
  --arg cmd "bash $HOOK_SCRIPT_CANVAS" \
  '[.hooks.SessionStart // [] | .[] | select(.command == $cmd)] | length' \
  "$SETTINGS_FILE" 2>/dev/null || echo "0")

[ "$EXISTING_PROGRESS" -gt 0 ] && warn "riff-progress 훅이 이미 등록되어 있습니다. 중복 등록을 건너뜁니다."
[ "$EXISTING_CANVAS" -gt 0 ] && warn "session-start-canvas 훅이 이미 등록되어 있습니다. 중복 등록을 건너뜁니다."

if [ "$EXISTING_PROGRESS" -gt 0 ] && [ "$EXISTING_CANVAS" -gt 0 ]; then
  echo ""
  show_summary
  exit 0
fi

SKIP_PROGRESS=$([ "$EXISTING_PROGRESS" -gt 0 ] && echo true || echo false)
SKIP_CANVAS=$([ "$EXISTING_CANVAS" -gt 0 ] && echo true || echo false)

# settings.json 업데이트
# - hooks / SubagentStop / SessionStart 키 없음 → 배열로 추가
# - 이미 있음                                    → 배열에 append
# - 이미 등록된 훅(skip 플래그)                  → 건드리지 않음
JQ_FILTER='
  .hooks = (.hooks // {})
  | if ($skip_progress | not) then .hooks.SubagentStop = ((.hooks.SubagentStop // []) + [$progress]) else . end
  | if ($skip_canvas | not) then .hooks.SessionStart = ((.hooks.SessionStart // []) + [$canvas]) else . end
'

if $DRY_RUN; then
  info "[DRY-RUN] settings.json 에 추가될 내용:"
  jq --argjson progress "$NEW_HOOK" --argjson canvas "$NEW_HOOK_CANVAS" \
    --argjson skip_progress "$SKIP_PROGRESS" --argjson skip_canvas "$SKIP_CANVAS" \
    "$JQ_FILTER" "$SETTINGS_FILE"
else
  TMP="$SETTINGS_FILE.tmp.$$"
  jq --argjson progress "$NEW_HOOK" --argjson canvas "$NEW_HOOK_CANVAS" \
    --argjson skip_progress "$SKIP_PROGRESS" --argjson skip_canvas "$SKIP_CANVAS" \
    "$JQ_FILTER" "$SETTINGS_FILE" > "$TMP" && mv "$TMP" "$SETTINGS_FILE"
  success "settings.json 에 훅 등록 완료"
fi

show_summary
