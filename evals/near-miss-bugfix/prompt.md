---
max_turns: 4
allowed_tools: [Read, Glob, Grep, Skill]
---

이 함수 합계가 틀려요. 수량을 안 곱하는 것 같은데 고쳐주세요.

```js
function total(items) { return items.reduce((sum, item) => sum + item.price, 0); }
```
