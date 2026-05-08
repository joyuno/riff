#!/bin/bash
# Riff Progress Hook — SubagentStop
# 서브에이전트 완료 시 Riff 진행률 자동 업데이트
#
# Claude Code 훅 설정 (settings.json):
# {
#   "hooks": {
#     "SubagentStop": [{
#       "matcher": "",
#       "command": "bash /path/to/riff-progress.sh"
#     }]
#   }
# }

set -euo pipefail

# ── jq 설치 여부 확인 ───────────────────────────────────────────────────────────
if ! command -v jq &>/dev/null; then
  # jq 없이는 JSON 파싱 불가 → graceful 실패
  echo '{"continue":true,"additionalContext":"[Riff Progress] 경고: jq가 설치되지 않아 진행률 추적을 건너뜁니다. brew install jq 또는 apt install jq 로 설치하세요."}'
  exit 0
fi

# ── stdin에서 훅 입력 읽기 ──────────────────────────────────────────────────────
INPUT=$(cat)

# ── 프로젝트 루트 감지 (.riff/ 디렉토리가 있는 곳) ───────────────────────────
RIFF_DIR=""
CHECK_DIR="$(pwd)"
while [ "$CHECK_DIR" != "/" ]; do
  if [ -d "$CHECK_DIR/.riff" ]; then
    RIFF_DIR="$CHECK_DIR/.riff"
    break
  fi
  CHECK_DIR="$(dirname "$CHECK_DIR")"
done

# .riff/ 없으면 Riff 비활성 → 종료
if [ -z "$RIFF_DIR" ]; then
  echo '{"continue":true}'
  exit 0
fi

# ── 토큰/시간/에이전트명 추출 ──────────────────────────────────────────────────
# 각 필드가 없으면 기본값 사용
TOTAL_TOKENS=$(echo "$INPUT" | jq -r '.total_tokens // 0' 2>/dev/null || echo "0")
DURATION_MS=$(echo "$INPUT"  | jq -r '.duration_ms   // 0' 2>/dev/null || echo "0")
AGENT_NAME=$(echo "$INPUT"   | jq -r '.agent_name    // "unknown"' 2>/dev/null || echo "unknown")
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 숫자 유효성 검사 (비정상 값 보호)
[[ "$TOTAL_TOKENS" =~ ^[0-9]+$ ]] || TOTAL_TOKENS=0
[[ "$DURATION_MS"  =~ ^[0-9]+$ ]] || DURATION_MS=0

# ── riff-log.json 초기화 ──────────────────────────────────────────────────────
LOG_FILE="$RIFF_DIR/riff-log.json"

if [ ! -f "$LOG_FILE" ]; then
  cat > "$LOG_FILE" <<'INIT_JSON'
{
  "schema_version": "1.0",
  "riffs": [],
  "agents": [],
  "convergence": {
    "journeys_done": 0,
    "journeys_total": 0,
    "qa_pass_rate": 0,
    "bugs_last_3": 0
  }
}
INIT_JSON
fi

# JSON 유효성 검사 — 파일이 손상된 경우 재초기화
if ! jq empty "$LOG_FILE" 2>/dev/null; then
  mv "$LOG_FILE" "$LOG_FILE.bak.$(date +%s)"
  cat > "$LOG_FILE" <<'INIT_JSON'
{
  "schema_version": "1.0",
  "riffs": [],
  "agents": [],
  "convergence": {
    "journeys_done": 0,
    "journeys_total": 0,
    "qa_pass_rate": 0,
    "bugs_last_3": 0
  }
}
INIT_JSON
fi

# ── 에이전트 기록 추가 ─────────────────────────────────────────────────────────
AGENT_ENTRY=$(jq -n \
  --arg  name     "$AGENT_NAME" \
  --arg  ts       "$TIMESTAMP" \
  --argjson tokens "$TOTAL_TOKENS" \
  --argjson dur    "$DURATION_MS" \
  '{name:$name, timestamp:$ts, tokens:$tokens, duration_ms:$dur}')

# 원자적 쓰기: .tmp → rename
TMP_FILE="$LOG_FILE.tmp.$$"
jq --argjson entry "$AGENT_ENTRY" '.agents += [$entry]' "$LOG_FILE" > "$TMP_FILE" \
  && mv "$TMP_FILE" "$LOG_FILE"

# ── 수렴 지표 계산 ────────────────────────────────────────────────────────────
TOTAL_AGENTS=$(   jq '.agents | length'          "$LOG_FILE")
TOTAL_TOKENS_SUM=$(jq '[.agents[].tokens] | add // 0' "$LOG_FILE")

JOURNEYS_DONE=$(  jq '.convergence.journeys_done'  "$LOG_FILE")
JOURNEYS_TOTAL=$( jq '.convergence.journeys_total' "$LOG_FILE")
QA_PASS=$(        jq '.convergence.qa_pass_rate'   "$LOG_FILE")
BUGS=$(           jq '.convergence.bugs_last_3'    "$LOG_FILE")

# ── 다음 Riff 우선순위 제안 생성 ─────────────────────────────────────────────
PRIORITY_HINT=""

# QA 통과율이 낮으면 QA 우선
QA_LOW=$(echo "$QA_PASS < 0.8" | bc -l 2>/dev/null || echo "0")
if [ "$QA_LOW" = "1" ]; then
  PRIORITY_HINT="[우선순위 제안] QA 통과율(${QA_PASS})이 낮습니다 — 다음 Riff는 테스트 보강을 우선하세요."
fi

# 버그 3개 이상이면 버그 수정 우선
if [ "$BUGS" -ge 3 ] 2>/dev/null; then
  PRIORITY_HINT="${PRIORITY_HINT:+$PRIORITY_HINT } [우선순위 제안] 최근 버그 ${BUGS}건 — 다음 Riff는 버그 수정을 우선하세요."
fi

# 저니 미완성이면 저니 완료 우선
if [ "$JOURNEYS_TOTAL" -gt 0 ] 2>/dev/null; then
  REMAINING=$((JOURNEYS_TOTAL - JOURNEYS_DONE))
  if [ "$REMAINING" -gt 0 ]; then
    PRIORITY_HINT="${PRIORITY_HINT:+$PRIORITY_HINT } [우선순위 제안] 유저 저니 ${REMAINING}개 미완성 — 다음 Riff에서 완료를 목표로 하세요."
  fi
fi

# ── 수렴 조건 판별 ─────────────────────────────────────────────────────────────
# 조건: 모든 유저 저니 완료 + QA 통과율 >= 0.9
CONVERGED="false"
if [ "$JOURNEYS_TOTAL" -gt 0 ] 2>/dev/null \
   && [ "$JOURNEYS_DONE" -eq "$JOURNEYS_TOTAL" ] 2>/dev/null \
   && [ "$(echo "$QA_PASS >= 0.9" | bc -l 2>/dev/null || echo 0)" = "1" ]; then
  CONVERGED="true"
fi

# ── 출력 메시지 구성 ──────────────────────────────────────────────────────────
BASE_MSG="[Riff Progress] 서브에이전트 '${AGENT_NAME}' 완료 (${TOTAL_TOKENS}토큰, ${DURATION_MS}ms). 총 에이전트: ${TOTAL_AGENTS}개, 누적 토큰: ${TOTAL_TOKENS_SUM}. 수렴 상태: 유저 저니 ${JOURNEYS_DONE}/${JOURNEYS_TOTAL}, QA ${QA_PASS}, 버그 ${BUGS}건."

if [ -n "$PRIORITY_HINT" ]; then
  BASE_MSG="${BASE_MSG} ${PRIORITY_HINT}"
fi

if [ "$CONVERGED" = "true" ]; then
  MSG="${BASE_MSG} ⚡ 수렴 조건 충족 — MVP 완성 여부를 사용자에게 확인하세요."
else
  MSG="$BASE_MSG"
fi

# JSON 안전하게 인코딩 (특수문자 이스케이프)
ENCODED_MSG=$(printf '%s' "$MSG" | jq -Rs '.')

printf '{"continue":true,"additionalContext":%s}\n' "$ENCODED_MSG"
