---
type: tool_used
tool: Write
# 구현 파일(_workspace/ 밖)을 쓰면 실패 — 가정 확인 전에 만들지 않는다
input_match: '"file_path"\s*:\s*"(?![^"]*_workspace)[^"]*"'
min: 0
max: 0
---
