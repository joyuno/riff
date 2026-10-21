---
type: regex
pattern: '예약금을 몰수하고 매출에 반영한다'
match: not_contains
target: { source: file, path: _workspace/CANVAS.md }
---
