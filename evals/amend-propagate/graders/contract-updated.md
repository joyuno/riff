---
type: regex
pattern: 'DEPOSIT_KRW\s*=\s*10000|forfeitDeposit'
match: not_contains
target: { source: file, path: _workspace/contracts/booking.md }
---
