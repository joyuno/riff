---
type: regex
# 진행 중 프로젝트를 이어갈 때도 일상어 가드가 적용돼야 한다 — 스킬이 안 켜지면 내부 용어가 그대로 나온다.
pattern: '(SHAPE|FRAME|A-0\d\d|K-0\d\d)'
match: not_contains
target: last_message
---
