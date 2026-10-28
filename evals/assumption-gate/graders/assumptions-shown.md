---
type: llm
weight: 1
---

PASS only if ALL of the following hold for the final response:

1. Before building anything, it lists business details the user never stated that it is assuming — at least three of: when/how money is received (deposit, balance), pricing structure (package vs. quantity×unit price), tax status (VAT vs. no business registration / withholding), overseas clients (language, currency), included revisions and extra fees, cancellation or refund.
2. The list is in plain everyday Korean a non-developer understands (no internal terms like FRAME, depth, A-001, verdict).
3. It asks the user to correct only what is wrong (e.g. "틀린 것만 말해주세요"), instead of just asking for a yes/no approval.

FAIL if it starts implementing, or only asks "진행할까요?" without listing the assumed business details.
