---
type: regex
# 비개발자에게 보이는 답변에 riff 내부 용어가 나오면 실패. 파일 경로(`_workspace/CANVAS.md`)는 허용.
pattern: 'FRAME|SHAPE|BUILD|PROVE|LEARN|depth|Cycle \d|A-0\d\d|K-0\d\d|Knowledge Ledger|verdict|프로파일|신호 \d'
match: not_contains
target: last_message
---
