#!/usr/bin/env bash
# 규칙 닫힘 계약: 조건을 선언한 문서가 그 조건이 참일 때의 행동까지 정의하는지 검사한다.
# 실측 3회 재발한 결함(게이트 태그 데드락 / core-closure 미처분 통과 / 승인 후 수정 경로 부재)이
# 되돌아오면 이 테스트가 깨진다.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRAME="$ROOT/skills/riff/references/frame"
TERMINATION="$FRAME/termination-engine.md"
LAYERS="$FRAME/layers.md"
ENRICHED="$FRAME/enriched-layers.md"
DISCOVERY="$FRAME/discovery-research.md"
DOMAIN="$FRAME/domain-intelligence.md"
CANVAS="$ROOT/skills/riff/references/canvas-schema.md"
SKILL="$ROOT/skills/riff/SKILL.md"

fail() {
  echo "FAIL: $1" >&2
  echo "  깨진 이유: $2" >&2
  echo "  고칠 파일: ${3#"$ROOT/"}" >&2
  exit 1
}

for file in "$TERMINATION" "$LAYERS" "$ENRICHED" "$DISCOVERY" "$DOMAIN" "$CANVAS" "$SKILL"; do
  test -f "$file" || fail "문서 없음: ${file#"$ROOT/"}" "규칙 닫힘 계약이 이 파일에 걸려 있다" "$file"
done

# 1. 게이트 태그 닫힘 — 선언된 태그마다 수집 경로가 양쪽 인터뷰 파일에 존재한다.
#    웹앱 fast-path는 layers.md 단독으로 돌기 때문에 enriched-layers.md만으로는 부족하다.
gate_tags="$(awk '/^\*\*게이트 태그/,/^$/' "$TERMINATION" | sed -n 's/^- `\([a-z_]*\)`.*/\1/p')"
test -n "$gate_tags" || fail "게이트 태그 선언 블록을 찾지 못함" \
  "'**게이트 태그' 절이 사라졌거나 '- \`tag\`:' 형식이 바뀌었다 — 이 검사가 무력해진다" "$TERMINATION"

for tag in $gate_tags; do
  grep -q "^- \`$tag\`.*수집:" "$TERMINATION" || fail "게이트 태그 \`$tag\`에 수집 경로 표기 없음" \
    "태그를 선언만 하고 어느 질문이 채우는지 적지 않았다 — 모델이 수집 질문을 만들지 못한다" "$TERMINATION"
  grep -q "$tag" "$LAYERS" || fail "게이트 태그 \`$tag\`를 layers.md가 수집하지 않음" \
    "미수집 게이트 태그는 충분성 60% 상한을 걸고 종료 조건은 70%다 — 인터뷰가 끝나지 않는다 (fast-path는 layers.md 단독)" "$LAYERS"
  grep -q "$tag" "$ENRICHED" || fail "게이트 태그 \`$tag\`를 enriched-layers.md가 수집하지 않음" \
    "enriched 경로에서 이 태그가 영원히 비어 60% 상한에 걸린다" "$ENRICHED"
done

# 4. 도달 가능성 — 상한(60%)과 종료 임계값(70%)이 같은 파일에 있고, 상한을 푸는 수집 경로가 위에서 확인된다.
grep -q '종합 충분성 ≥ 70%' "$TERMINATION" || fail "종료 임계값 70% 표기 없음" \
  "임계값이 바뀌었거나 사라졌다 — 게이트 상한과의 도달 가능성을 검증할 수 없다" "$TERMINATION"
grep -q '60%를 넘을 수 없다' "$TERMINATION" || fail "게이트 미수집 상한 60% 표기 없음" \
  "상한 규칙이 사라졌거나 문구가 바뀌었다 — 데드락 회귀를 감지할 수 없다" "$TERMINATION"

# 2. core-closure 처분 강제 — 표의 행 수와 처분 규칙·trace gate가 요구하는 행 수가 일치한다.
matrix_rows="$(awk '/^### Core-closure matrix/,/^#### /' "$DISCOVERY" | grep -c '^| ' || true)"
matrix_rows=$((matrix_rows - 1)) # 헤더 제외
test "$matrix_rows" -gt 0 || fail "core-closure matrix 표를 찾지 못함" \
  "'### Core-closure matrix' 절이 사라졌거나 표 형식이 바뀌었다" "$DISCOVERY"

grep -q "처분 강제 (${matrix_rows}행 전부" "$DISCOVERY" || fail "처분 강제 절이 ${matrix_rows}행을 요구하지 않음" \
  "matrix 행 수(${matrix_rows})와 처분 강제 절의 행 수 주장이 어긋난다 — 늘어난 행이 처분 없이 통과한다" "$DISCOVERY"
for disposition in frozen excluded 'n/a'; do
  grep -q "\`$disposition\`" "$DISCOVERY" || fail "처분값 \`$disposition\` 없음" \
    "처분 3종 중 하나가 사라지면 행이 blocked도 부재도 아닌 상태로 통과한다" "$DISCOVERY"
done

grep -q "${matrix_rows}행 전부" "$DOMAIN" || fail "trace gate가 ${matrix_rows}행 전부를 요구하지 않음" \
  "verdict 게이트가 전 행 처분을 요구하지 않으면 미처분 행이 조용히 통과한다" "$DOMAIN"
grep -q '`blocked`가 남은 행이 없다' "$DOMAIN" || fail "trace gate에 blocked 잔여 금지 조건 없음" \
  "blocked인 채로 verdict을 요청할 수 있게 된다" "$DOMAIN"

# 3. 승인 후 수정 경로 — in-place amend가 존재하고, 세션 분리는 컨텍스트 압박으로만 한정된다.
grep -q 'in-place amend' "$CANVAS" || fail "승인 후 수정(in-place amend) 규칙 없음" \
  "모순 감지 후 행동이 비면 모델이 가장 무거운 카드(핸드오프+새 세션)를 뽑는다" "$CANVAS"
grep -q '세션 분리·핸드오프·되감기는 이 경우의 답이 아니다' "$CANVAS" || fail "amend에서 무거운 대안 배제 문구 없음" \
  "수정 경로가 있어도 더 무거운 대안이 열려 있으면 그쪽이 선택된다" "$CANVAS"
grep -q '세션 분리·핸드오프는 컨텍스트 압박에서만 나온다' "$SKILL" || fail "세션 분리 발동 조건 한정 문구 없음" \
  "SKILL.md가 세션 분리를 한정하지 않으면 기획 수정에도 세션이 갈린다 (실사용 실패 사례)" "$SKILL"

echo "PASS: 규칙 닫힘 계약 (게이트 태그 ${gate_tags//$'\n'/ } / core-closure ${matrix_rows}행 / 승인 후 수정)"
