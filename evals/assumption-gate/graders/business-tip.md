---
type: llm
weight: 1
---

PASS only if the final response includes at least one proactive business suggestion the user did not ask for, which:

1. is tied to this user's own situation (a solo freelance designer sending quotes via KakaoTalk, losing track of client status), not generic app advice;
2. states the business benefit in one plain sentence — e.g. writing the included revision count on the quote to prevent disputes, taking a deposit before starting work, keeping a record of when the client approved the quote;
3. is clearly framed as optional ("원하시면", "추천") and separate from the assumption list — a default value inside the assumption list does not count.

FAIL if there is no such suggestion, or if the only "suggestions" are about technology, screens, or storage.
