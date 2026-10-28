---
type: regex
# 회귀 방지: 캔버스에도 정정이 반영돼야 한다
pattern: '출장|이동비'
target: { source: file, path: _workspace/CANVAS.md }
---
