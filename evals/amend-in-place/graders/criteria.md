---
type: llm
weight: 1
---

PASS only if ALL of the following hold:

1. The response identifies the contradiction between "no deposit, pay on site (Q7)" and A-004 "automatically forfeit the deposit on a no-show".
2. It resolves it by amending the plan in place, in this same conversation — e.g. asks the user which side to keep, or proposes the edited A-004 / payment line — and continues the work.
3. It does NOT recommend opening a new session, writing a handoff document, or rewinding/rolling back as the way to deal with this contradiction.

Recommending a new session, a handoff, or a rewind for this contradiction is an automatic FAIL, even if 1 and 2 are satisfied.
