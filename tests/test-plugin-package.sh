#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
codex_manifest="$ROOT/.codex-plugin/plugin.json"
claude_manifest="$ROOT/.claude-plugin/plugin.json"
marketplace="$ROOT/.agents/plugins/marketplace.json"
mcp="$ROOT/.mcp.json"

test -f "$codex_manifest"
test -f "$marketplace"
jq -e '.name == "riff" and .version == "1.0.0" and .skills == "./skills/" and .mcpServers == "./.mcp.json"' "$codex_manifest" >/dev/null
jq -e --slurpfile claude "$claude_manifest" '.name == $claude[0].name and .version == $claude[0].version' "$codex_manifest" >/dev/null
jq -e '.name == "joyuno-riff-local" and (.plugins | length) == 1' "$marketplace" >/dev/null
jq -e '.plugins[0] | .name == "riff" and .source.source == "local" and .source.path == "./" and .policy.installation == "AVAILABLE" and .policy.authentication == "ON_INSTALL" and .category == "Developer Tools"' "$marketplace" >/dev/null
test -f "$ROOT/skills/riff/SKILL.md"
test -f "$mcp"
jq -e '.mcpServers.exa.type == "http" and .mcpServers.exa.url == "https://mcp.exa.ai/mcp"' "$mcp" >/dev/null
grep -q 'Codex 호스트에서는 Codex 자체 기능' "$ROOT/skills/riff/SKILL.md"
grep -q 'references/companions.md.*읽지 않는다' "$ROOT/skills/riff/SKILL.md"
grep -q '외부 전송 가드' "$ROOT/skills/riff/SKILL.md"
grep -q 'domain-intelligence.md' "$ROOT/skills/riff/SKILL.md"
# 등급별 builder 3개는 model만 다르고 본문(가드)은 같아야 한다
body() { awk 'f>=2{print} /^---$/{f++}' "$1"; }
for tier in support trivial; do
  diff <(body "$ROOT/agents/riff-builder.md") <(body "$ROOT/agents/riff-builder-$tier.md") >/dev/null
done
echo "PASS: Claude and Codex plugin package metadata"
