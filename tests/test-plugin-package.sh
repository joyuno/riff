#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
codex_manifest="$ROOT/.codex-plugin/plugin.json"
claude_manifest="$ROOT/.claude-plugin/plugin.json"
marketplace="$ROOT/.agents/plugins/marketplace.json"

test -f "$codex_manifest"
test -f "$marketplace"
jq -e '.name == "riff" and .version == "1.0.0" and .skills == "./skills/"' "$codex_manifest" >/dev/null
jq -e --slurpfile claude "$claude_manifest" '.name == $claude[0].name and .version == $claude[0].version' "$codex_manifest" >/dev/null
jq -e '.name == "joyuno-riff-local" and (.plugins | length) == 1' "$marketplace" >/dev/null
jq -e '.plugins[0] | .name == "riff" and .source.source == "local" and .source.path == "./" and .policy.installation == "AVAILABLE" and .policy.authentication == "ON_INSTALL" and .category == "Developer Tools"' "$marketplace" >/dev/null
test -f "$ROOT/skills/riff/SKILL.md"
echo "PASS: Claude and Codex plugin package metadata"
