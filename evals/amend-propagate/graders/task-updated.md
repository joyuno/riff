---
type: regex
pattern: '\| *예약금 결제·몰수 처리 *\| *A-004 *\| *core *\| *todo *\|'
match: not_contains
target: { source: file, path: _workspace/CANVAS.md }
---
