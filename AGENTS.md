## 작업 규칙

- riff에 규칙·게이트·감지 조건을 추가할 때는 **그 조건이 참일 때 실행할 구체적 행동·주체·시점**을 같은 커밋에서 문서화한다. 조건만 선언하고 행동을 비우면 모델이 가장 무거운 대안을 고른다(실측 3회). `tests/test-rule-closure.sh`가 이를 검사한다.
- riff 규칙(`skills/riff/SKILL.md`·`references/`)을 바꿀 때는 그 규칙이 막으려는 행동을 재현하는 케이스를 `evals/`에 같은 커밋으로 넣고, `claude plugin eval`로 **변경 전 실패 → 변경 후 통과**를 확인한다. 통과하지 못한 규칙 변경은 채택하지 않는다(문서 일관성 테스트는 행동을 보지 못한다).

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
