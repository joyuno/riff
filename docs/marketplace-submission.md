# Community Marketplace 제출 자료

Claude Code 커뮤니티 마켓플레이스(`claude-community`) 제출 폼에 붙여넣을 원고.

> 공식 마켓플레이스(`claude-plugins-official`)는 Anthropic 큐레이션이라 신청 창구가 없다.
> 제출 경로는 개인 개발자 [platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit),
> Team/Enterprise 조직 [claude.ai/admin-settings/directory/submissions/plugins/new](https://claude.ai/admin-settings/directory/submissions/plugins/new).

## 기본 정보

```
Plugin name : riff
Repository  : https://github.com/joyuno/riff
License     : MIT
Version     : 1.0.0
Validation  : claude plugin validate . --strict → ✔ Validation passed
```

---

## Short description

**EN**

```
Question-driven development loop for non-developers — riff asks the right questions, freezes them as testable acceptance criteria, and keeps everything in one restartable CANVAS.md.
```

**KO**

```
질문이 캔버스를 채운다 — 비개발자도 자기 도메인 지식만으로 완성도 있는 MVP를 만들도록, 올바른 질문을 던지고 그 답을 검증 가능한 수용 기준으로 굳히는 루프.
```

---

## Full description

```
Riff turns "I know my business but not code" into a working prototype.

Most AI coding tools accept a one-line brief and start building. What gets missed isn't code
quality — it's the requirements nobody articulates. A quote-management app ships without a VAT
line. A booking app loses everything on refresh. Users never say "data must survive a reload,"
but every app needs it.

Riff runs a five-stage cycle — FRAME → SHAPE → BUILD → PROVE → LEARN — where every stage writes
into a single living document (CANVAS.md) designed so a session can restart from that file alone.

What makes it different

- Domain intelligence, not generic interviews. A router classifies the work (regulated /
  operational / market / creative / technical / ai-data) plus a risk overlay (money / safety /
  privacy / rights), then asks the questions that domain actually breaks on. Findings land in a
  Knowledge Ledger where every claim carries its evidence state, and no acceptance criterion can
  be frozen without a traceable source.

- Closure checking. Seven operational gaps — records, state, calculation, retrieval, persistence,
  mistakes, delivery — must each end in frozen, excluded with reason, or not applicable before
  planning is approved. This is what catches the requirements users never mention.

- Adaptive depth. An eight-signal check sets ceremony level per cycle. Simple work skips the
  interview; ambiguous work gets the full treatment. Overhead is measured, not asserted
  (benchmarks/context-tax.py).

- Verification that runs. Tier 0-3 checks from contract lint through build/behavior tests to
  live-browser Playwright journeys, with frozen acceptance criteria executed every cycle.

- Learning that compounds. Bugs become "antibodies" — reproducible regression checks injected
  into later cycles.

Korean-language interface with English documentation. Works standalone; optionally integrates
with ralph-loop, codex, and ecc-plan-canvas, with native fallbacks so nothing is required.
```

---

## Target users

```
Solo founders, domain experts, and rapid prototypers who understand their own workflow but don't
write code — plus experienced developers who want requirements pinned down before implementation
rather than after.
```

---

## Use cases

```
1. Quote & client tracker for a freelancer
   "Build an app where a freelancer creates quotes and tracks client status."
   Riff surfaces what the brief omits: line items with quantity x unit price, VAT handling,
   draft->sent->approved transitions, search by client, and print view — then freezes each as a
   testable check before writing code.

2. Salon booking with no-show tracking
   "Build a booking manager for a hair salon, including no-shows."
   Beyond the obvious calendar, riff asks who notices a wrong entry and whether it can be undone,
   whether the existing paper log must keep working during rollout, and whether data survives a
   refresh.

3. Customer review insights for a store owner
   "Analyze my shop's customer reviews and show me what to fix first."
   Riff separates what the owner says they want (a dashboard) from the job to be done (deciding
   this week's fix), and pins a processing-status workflow so reviews don't get re-read forever.

4. Internal tool replacing a spreadsheet
   "We manage inventory in Excel and it keeps breaking. Make us a proper tool."
   Riff asks for three real rows of the spreadsheet instead of a description, derives fields from
   the artifact, and records which existing procedures must not break during migration.

5. Regulated or money-touching MVP
   "Build a simple invoicing app for a small studio."
   The risk router flags money handling, forcing questions about calculation invariants, who
   approves, and whether a wrong number can be reversed — before any of it becomes code.

6. Resuming after a break
   "continue"
   A new session reads CANVAS.md alone, reconciles it against the working tree, and resumes at the
   next action — no re-explaining the project.
```

### 짧은 버전 (입력 칸이 좁을 때)

```
- Freelancer quote tracker — catches VAT, line items, and status flow the brief never mentions
- Salon booking — asks who catches a wrong entry and whether the paper log must keep working
- Review insights — separates the dashboard the user asks for from the decision they need
- Excel replacement — reads three real rows instead of trusting a description
- Invoicing MVP — money router forces calculation, approval, and reversibility questions
- Resume anytime — a fresh session restarts from CANVAS.md alone
```

---

## Permissions & safety notes

리뷰에 자동 안전성 스크리닝이 포함되므로, 해당 항목이 있으면 이 내용을 적는다.

```
- Git commits: at the end of each cycle riff commits with a "cycle-N:" message in the user's own
  repository. This commit is the anchor for its rewind protocol. It never pushes.

- One-way-door gate: push, publish, destructive migration, and deploy always require explicit user
  confirmation before execution, regardless of automation depth.

- Optional dependencies: bootstrap offers to install companion plugins (ralph-loop, codex,
  ecc-universal) once per project, with Install / Skip / Skip-all. Every companion has a native
  fallback; declining costs no functionality.

- Network: no network access of its own. Web research uses the bundled Exa MCP only when the user
  permits it, and skips silently if unavailable.

- Writes: confined to _workspace/ and .riff/ in the user's project.
```

---

## 한국어 소개 (README·블로그용)

```
- 프리랜서 견적 관리 — "견적서 만들고 고객 진행 상태 관리하는 앱 만들어줘"
  → 항목별 수량·단가, 부가세, 초안→발송→승인 전환, 고객 검색, 인쇄 뷰까지 끌어내
    검증 가능한 체크로 동결
- 미용실 예약·노쇼 — 달력 너머로, 잘못된 값을 누가 언제 알아채는지·되돌릴 수 있는지·
  기존 장부는 계속 돌아야 하는지를 묻는다
- 리뷰 인사이트 — 사장님이 말한 것(대시보드)과 실제로 끝내려는 일(이번 주에 뭘 고칠지)을 분리
- 엑셀 대체 내부 도구 — 설명 대신 실제 3줄을 요청하고, 이관 중에도 깨지면 안 되는 절차를 기록
- 돈을 다루는 MVP — 위험 라우터가 계산 불변식·승인권자·되돌리기를 코드 전에 묻는다
- 이어서 하기 — 새 세션이 CANVAS.md만 읽고 다음 액션부터 재개
```

---

## 작성 의도 (제출 시 참고)

- 첫 문단이 리뷰어가 읽는 전부일 수 있어 "VAT 없는 견적서 / 새로고침하면 사라지는 예약"이라는
  구체적 실패 예시를 앞에 뒀다. 추상적인 "질문 프레임워크" 설명보다 전달이 빠르다.
- use case 6개 모두 **riff가 추가로 묻는 것**을 한 줄씩 붙였다. "질문해주는 도구"는 흔한 주장이라
  무엇을 묻는지 구체적으로 보여주는 것이 차별점이 된다.
- 오버헤드를 "측정한다(`benchmarks/context-tax.py`)"고 적은 것은 사실이다. 측정값은
  단순 4.81% / 보통 6.98% / 복잡 17.94%(BORDER)이며, 복잡 프로파일은 15% 예산을 넘길 수 있다.
  질문받으면 그대로 답한다.
