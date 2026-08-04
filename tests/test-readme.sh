#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KO="$ROOT/README.md"
EN="$ROOT/README.en.md"

grep -q '\[English\](README.en.md)' "$KO"
grep -q '\[한국어\](README.md)' "$EN"

for file in "$KO" "$EN"; do
  grep -q 'FRAME.*SHAPE.*BUILD.*PROVE.*LEARN' "$file"
  grep -q 'CANVAS.md' "$file"
  grep -q 'codex plugin marketplace add \.' "$file"
  grep -q 'codex plugin add riff@joyuno-riff-local' "$file"
  grep -q 'session-start-canvas.sh' "$file"
  grep -q 'run-speed-tax.sh' "$file"
  grep -q 'benchmarks/README.md' "$file"
  if grep -qi 'Playwright MCP\|English (coming soon)' "$file"; then
    echo "retired README copy found: $file" >&2
    exit 1
  fi
done

if grep -q '^## Comparison' "$EN" || grep -q '^## 비교' "$KO"; then
  echo "competitive comparison should not be in the user-first README" >&2
  exit 1
fi

python3 - "$KO" "$EN" <<'PY'
import re
import sys
from pathlib import Path

for raw in sys.argv[1:]:
    file = Path(raw)
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
        if not target or target.startswith("#") or "://" in target:
            continue
        path = file.parent / target.split("#", 1)[0]
        if not path.exists():
            raise SystemExit(f"missing relative link: {file.name}: {target}")
print("PASS: README relative links")
PY

echo "PASS: user-first bilingual README contract"
