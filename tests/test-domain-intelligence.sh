#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOMAIN="$ROOT/skills/riff/references/frame/domain-intelligence.md"

test -f "$DOMAIN"
for heading in \
  'Domain Research Router' \
  'Domain Model' \
  'Knowledge Ledger' \
  'Knowledge → Acceptance trace gate' \
  'PROVE와 LEARN'; do
  grep -q "$heading" "$DOMAIN"
done

for state in observed user-confirmed official industry assumption excluded; do
  grep -q "\`$state\`" "$DOMAIN"
done

grep -q 'domain-intelligence.md' "$ROOT/skills/riff/SKILL.md"
grep -q 'K-NNN' "$ROOT/skills/riff/references/build.md"
grep -q 'Knowledge trace 검증' "$ROOT/skills/riff/references/prove/tier2-build.md"
grep -q '지식 추적' "$ROOT/skills/riff/references/prove/canvas-lint.md"
grep -q '검색 예산과 확장 조건' "$ROOT/skills/riff/references/frame/discovery-research.md"

echo "PASS: domain intelligence trace contract"
