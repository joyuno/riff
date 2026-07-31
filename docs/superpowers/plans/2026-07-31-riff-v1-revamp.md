# riff v1.0.0 전면 개편 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 스펙 `docs/superpowers/specs/2026-07-31-riff-revamp-design.md`(v1.2)대로 riff를 5스킬 구조에서 단일 스킬 + Living Canvas + adaptive depth + DROP/TUNE 이벤트 스테이지 구조(v1.0.0)로 재구축한다.

**Architecture:** 단일 플러그인 안의 `skills/riff/` 하나로 통합 — SKILL.md(얇은 코어 루프)가 `references/`(구 4모듈 흡수, progressive disclosure)를 가리킨다. 기존 참조 파일은 최대한 `git mv`로 보존·이관하고, 신규 파일(canvas-schema, drop, tune, model-routing, companions, canvas-lint, diff-review)만 새로 작성한다. 모든 태스크는 독립 커밋으로 닫고, 커밋마다 검증 커맨드(grep 구조 체크·`python3 -m json.tool`·`bash -n`)를 실행한다.

**Tech Stack:** Claude Code 플러그인(SKILL.md + references + hooks), bash 훅, 마크다운 벤치마크 픽스처 + JSON ground-truth.

**참고 — 마크다운 산출물의 "테스트":** 이 리포의 산출물은 스킬 문서이므로 TDD의 red/green을 "검증 커맨드가 기대 출력을 내는가"로 치환한다. 각 태스크의 Verify 스텝은 실패 조건(기대 grep 카운트·파싱 성공)을 명시한다.

**용어 규칙(전 태스크 공통):** "분신술"→"잼(Jam)", "Riff N/riff-N"→"Cycle N/cycle-N", "ASK/EXPLORE/VERIFY"→"FRAME/SHAPE/PROVE"(BUILD·LEARN 유지). `docs/superpowers/`(스펙·감사·계획 문서)는 역사 기록이므로 치환 대상에서 제외.

---

## File Structure (최종 목표 트리)

```
skills/riff/
├─ SKILL.md                        ← 전면 재작성 (Task 11)
└─ references/
    ├─ canvas-schema.md            ← 신규 (Task 1)
    ├─ frame.md                    ← 신규 (Task 2)
    ├─ frame/                      ← 구 riff-interview/references/* 이관 (Task 2)
    ├─ shape-jam.md                ← explore-protocol.md 이관+개정 (Task 3)
    ├─ build.md                    ← build-protocol.md 이관+개정 (Task 4)
    ├─ contracts/                  ← 구 riff-contracts/references/* 이관 (Task 5)
    ├─ prove/                      ← 구 riff-qa/references/* 이관 + canvas-lint.md·diff-review.md 신규 (Task 6)
    ├─ learn.md                    ← 신규 (Task 7)
    ├─ learn/                      ← antibody-schema.md·profile-schema.md 이관 (Task 7)
    ├─ model-routing.md            ← 신규 (Task 8)
    ├─ companions.md               ← 신규, 구 SKILL.md Bootstrap 이관 (Task 9)
    ├─ drop.md · tune.md           ← 신규 (Task 10)
    ├─ rewind-protocol.md          ← 유지 + 커밋 앵커 개정 (Task 10)
    ├─ convergence.md              ← 유지 (용어 sweep만)
    └─ ui-stack-guide.md           ← 유지 (용어 sweep만)
삭제: skills/riff-interview·riff-qa·riff-contracts·riff-memory (Task 12),
      skills/riff/references/riff-status-schema.md (canvas-schema로 대체, Task 1),
      skills/.omc/ (잡파일, Task 12), docs/riff_cycle.png·architecture.png (mermaid 대체, Task 16)
hooks/session-start-canvas.sh      ← 신규 (Task 13)
benchmarks/fixtures/depth/·canvas/ ← 신규 픽스처 (Task 15)
```

---

### Task 1: canvas-schema.md 신규 + riff-status-schema.md 제거

**Files:**
- Create: `skills/riff/references/canvas-schema.md`
- Delete: `skills/riff/references/riff-status-schema.md`

- [ ] **Step 1: canvas-schema.md 작성** — 아래 내용 그대로 생성:

````markdown
# CANVAS.md 스키마 — 유일 SSOT

원칙: **이 문서만으로 재시작 가능해야 한다.** 캔버스는 지도, `detail/`·`contracts/`는 영토.

## 템플릿 (Cycle 0에서 이 골격 그대로 생성)

```markdown
# CANVAS — <프로젝트명>
> 마지막 갱신: Cycle N · <스테이지> · <YYYY-MM-DD>

## UPDATE RULE
현재 사이클만 상세히. 스테이지 종료 시 해당 섹션 갱신. 섹션 상한 초과 시
오래된 내용은 detail/로 내리고 링크만 남긴다. 완료 사이클은 1줄 요약으로 접는다.
아키텍처·플로우·상태머신은 mermaid 블록으로 그린다.
이 문서의 쓰기는 메인 루프 단독(single-writer) — 서브에이전트는 detail/·contracts/·태스크 보드에만 기록.

## STATUS                                  <!-- 10줄 이내 -->
- 현재: Cycle N · <스테이지>
- 성공 기준 진행도: n/m
- depth 프로파일: 단순|보통|복잡 (신호 n/8)
- 활성 가정: <가정 선언 요약 or 없음>
- 다음 액션: <1줄>

## [1] FRAME — 문제와 성공 기준             <!-- 상한 30줄 -->
질문→답 요약 · 핵심 Job · 페르소나 1줄씩 · 측정 가능한 성공 기준
(FRAME 스킵 시 가정 선언 기록 / 상세 → detail/frame-*.md)

## [2] SHAPE — 결정 로그                    <!-- 상한 20행 -->
| # | 결정 | 기각된 대안 | 근거 | cycle |
(잼 결과 = 요약 1줄 + detail/ 링크, 구조 결정은 mermaid 병기)

## [3] BUILD — 계약 + 태스크 보드           <!-- 상한 30줄 -->
활성 계약 링크 + 1줄 요약
| 태스크 | 등급 | 모델 | 병렬 | 상태 |

## [4] PROVE — 검증 게이트 기록             <!-- 최근 5개 -->
| cycle | tier | 결과 | diff-review | 에스컬레이션 |

## [5] LEARN — 항체 & 다음 사이클           <!-- 상한 15줄 -->
새 항체 포인터 · 확신도 · 다음 사이클 후보 · 도메인 brief 포인터
```

## 운영 규칙

1. **갱신(권고)**: 각 스테이지 종료 시 해당 섹션 갱신. 훅 강제 없음 — 미갱신은 canvas-lint(`prove/canvas-lint.md`)가 탐지.
2. **압축**: UPDATE RULE이 자기 기술 — 스킬 컨텍스트가 없는 세션에서도 규칙이 문서와 함께 이동.
3. **single-writer**: CANVAS.md 쓰기는 메인 루프 단독.
4. **verdict 게이트**: FRAME 산출(또는 가정 선언)과 사이클 종료는 approve/request-changes로 닫는다 — `ecc-plan-canvas` 있으면 브라우저(요소 앵커 주석+판정), 없으면 터미널 구조화 질문(`companions.md`).

## 디렉토리

```
_workspace/
├─ CANVAS.md      ← 유일 SSOT
├─ contracts/     ← 계약서 (병렬 빌드 시에만 생성)
└─ detail/        ← 인터뷰 전문·잼 결과·검증 상세·domains/<domain>.md
.riff/            ← 항체·프로파일·세션 상태 (기존 유지, .gitignore: profile.md·state.json)
```

## v0.3.1 마이그레이션

첫 실행 시 `_workspace/riff-status.md` 또는 `riff-log.md` 감지 → CANVAS.md 1회 변환 제안:
status의 "현재 위치"→STATUS, riff-0 산출물 요약→[1], riff-log 학습→[5], 기존 riff-N/→detail/로 이동.
````

- [ ] **Step 2: 구 스키마 삭제**

```bash
git rm skills/riff/references/riff-status-schema.md
```

- [ ] **Step 3: Verify**

```bash
grep -c '^## ' skills/riff/references/canvas-schema.md   # 기대: 4 (템플릿/운영 규칙/디렉토리/마이그레이션)
grep -c 'UPDATE RULE' skills/riff/references/canvas-schema.md  # 기대: >=2
```

- [ ] **Step 4: Commit** — `feat(canvas): CANVAS.md 스키마 신설, riff-status-schema 대체`

---

### Task 2: FRAME — riff-interview 흡수 + frame.md 신규

**Files:**
- Move: `skills/riff-interview/references/*` → `skills/riff/references/frame/`
- Create: `skills/riff/references/frame.md`

- [ ] **Step 1: 참조 이관**

```bash
mkdir -p skills/riff/references/frame
git mv skills/riff-interview/references/* skills/riff/references/frame/
```

- [ ] **Step 2: frame.md 작성** — 아래 내용 그대로:

````markdown
# FRAME — 질문으로 문제·성공 기준 확정

구 ASK + Riff 0(프로젝트 부팅) 통합. 세부 질문 자산은 `frame/` 하위(레이어·도메인·전문가) 사용.

## depth별 동작

| 프로파일 | 동작 |
|---|---|
| 단순 (신호 6+/8) | **스킵 가드 확인 후** 가정 선언 1줄 |
| 보통 (4~5/8) | 핵심 질문 2개: "이 프로젝트가 해결하는 문제는?" / "성공하면 어떤 모습인가?" |
| 복잡 (<4/8) | 5-Layer 인터뷰(`frame/layers.md`, `frame/enriched-layers.md`) + 도메인 분기(`frame/domains/`) |

## 스킵 가드 (필수)

FRAME 완전 스킵은 **CANVAS [1]에 성공 기준이 이미 존재할 때만** 허용.
없으면 스킵 대신 **가정 선언**: 채택한 해석 1줄 + 성공 기준 1줄을 [1]에 기록하고
STATUS에 `활성 가정: X — 아니면 지금 말해주세요`로 노출. verdict 게이트 대상.

## 수용 기준 규칙

1. **testability 가드**: 성공 기준·가정 선언은 "Tier 2 체크가 실행할 수 있는 관찰 가능한 행동"을 명시
   (예: "주문 생성 API가 201과 주문 id를 반환" O / "구현이 완료된다" X — PRD theater 금지).
2. **acceptance 동결**: verdict 승인 시점에 core급 작업의 수용 기준에서 실행 가능 체크 1~3개를 유도해
   `detail/acceptance/` 에 동결. Tier 2가 매 PROVE마다 실행. 단순 depth는 스킵.

## 웹앱 fast-path

신규 웹앱 + 보통 depth: 도메인 기본값 `web-development`, 핵심 12문항만(`frame/domains/web-development.md`),
완료 후 `_workspace/contracts/ui-stack.md` 확정(`ui-stack-guide.md`).

## 산출

CANVAS [1] 갱신(상한 30줄, 전문은 `detail/frame-*.md`) → verdict 게이트(`companions.md`) → SHAPE 또는 BUILD.
````

- [ ] **Step 3: Verify**

```bash
ls skills/riff/references/frame/layers.md skills/riff/references/frame/domains/web-development.md  # 존재
ls skills/riff-interview/references 2>&1 | grep -c 'No such'  # 기대: 1
grep -c '스킵 가드' skills/riff/references/frame.md  # 기대: >=2
```

- [ ] **Step 4: Commit** — `feat(frame): riff-interview 흡수 + 스킵 가드·가정 선언·acceptance 동결`

---

### Task 3: SHAPE — explore-protocol → shape-jam.md

**Files:**
- Move+Modify: `skills/riff/references/explore-protocol.md` → `skills/riff/references/shape-jam.md`

- [ ] **Step 1: 이관**

```bash
git mv skills/riff/references/explore-protocol.md skills/riff/references/shape-jam.md
```

- [ ] **Step 2: 개정** — Edit(replace_all)로 파일 내: `분신술`→`잼(Jam)` 첫 등장, 이후 `잼`; `EXPLORE`→`SHAPE`; `explore-`→`shape-`; `riff-N`→`cycle-N`. 파일 끝에 아래 섹션 추가:

```markdown
## 잼 실행 방식 (v1.0)

- 각 대안은 **격리 worktree**에서 동시 시도(Agent isolation: 'worktree'). 미채택 방향은 워크트리째 폐기(DROP의 정리 목록에 등록).
- 잼 에이전트 모델: `opus` 강제 지정(`model-routing.md`).
- 결과는 CANVAS [2]에 결정 1행(기각 대안·근거 포함) + `detail/shape-*.md` 링크로 기록. 구조 결정은 mermaid 병기.
- codex 컴패니언 있으면 트레이드오프 불명확 시 `/codex:adversarial-review --wait <focus>` 1회. 없으면 잼에 반대 관점 에이전트 1개 추가.
```

- [ ] **Step 3: Verify**

```bash
grep -c '분신술' skills/riff/references/shape-jam.md  # 기대: 0
grep -c 'worktree' skills/riff/references/shape-jam.md  # 기대: >=2
```

- [ ] **Step 4: Commit** — `feat(shape): 잼 프로토콜 — worktree 격리·opus 라우팅·codex 폴백`

---

### Task 4: BUILD — build-protocol → build.md

**Files:**
- Move+Modify: `skills/riff/references/build-protocol.md` → `skills/riff/references/build.md`

- [ ] **Step 1: 이관** — `git mv skills/riff/references/build-protocol.md skills/riff/references/build.md`

- [ ] **Step 2: 개정** — 용어 규칙 적용 후, PLAN/CONTRACT/EXECUTE 절을 아래 규칙으로 대체·추가:

```markdown
## BUILD-PLAN 산출 (태스크 보드)

TaskCreate로 태스크 생성 + CANVAS [3]에 요약 행. 태스크마다:
- **등급**: core(성공 기준 직결) / support(접점이나 대체 가능) / trivial(실패해도 즉시 재시도). 애매하면 상위 등급.
- **병렬 여부**: 동시 실행 예정인지 (이 값이 계약·스폰 조건의 술어)
- **보안 플래그**: auth·결제·시크릿·유저 데이터 접촉 또는 >20파일 → DROP 전 sonnet 보안 패스 예약

## 계약 조건 (v1.0 — 병렬 시에만)

계약 작성은 **태스크 보드에 잼 또는 병렬 스폰(동시 태스크 ≥2)이 계획된 경우에만**.
순차 빌드는 코드의 타입 선언이 계약이고 tsc가 lint — 계약서 생략.
병렬 시: 8종 계약(`contracts/`) + lint 통과 후 스폰(기존 규칙 유지). CONTRACT→EXECUTE 복귀 3회 시 사용자 개입.

## 실행 위치 (라우팅 조건)

- 순차 태스크: **메인 루프 인라인** — 스폰 금지, 결과만 CANVAS [3] 상태 갱신.
- 병렬 태스크(≥2): 등급→모델 지정 스폰(`model-routing.md`). 동시 슬롯 3(웨이브 배리어 대신 완료 즉시 충원, trivial은 상한 미포함).
- 스폰된 에이전트 결과는 `_workspace/detail/` 파일 통신(대화 반환 금지) — 인라인 실행에는 미적용.

## 행위 체크 (core 필수)

core 태스크 산출물에 행위 계약 기반 **실행 가능 체크 ≥1개**(테스트 or assertion 스크립트) 포함.
작성 순서는 자유. 체크는 PROVE Tier 2가 누적 실행.
```

- [ ] **Step 3: Verify**

```bash
grep -c '병렬 스폰이 계획된 경우에만\|병렬 시에만' skills/riff/references/build.md  # 기대: >=1
grep -c 'EXPLORE\|분신술' skills/riff/references/build.md  # 기대: 0
```

- [ ] **Step 4: Commit** — `feat(build): 태스크 등급표·계약 병렬 술어·인라인 우선 실행`

---

### Task 5: contracts/ 이관

**Files:**
- Move: `skills/riff-contracts/references/*` → `skills/riff/references/contracts/`

- [ ] **Step 1:**

```bash
mkdir -p skills/riff/references/contracts
git mv skills/riff-contracts/references/* skills/riff/references/contracts/
```

- [ ] **Step 2: contract-lint.md 머리에 조건 명시** — 파일 최상단 제목 아래 1줄 추가:

```markdown
> v1.0: 계약·lint는 **병렬 빌드(잼 또는 동시 태스크 ≥2)일 때만** 발동한다(`build.md`). Tier 0 계약 검사도 contracts/에 계약이 존재할 때만 실행.
```

- [ ] **Step 3: Verify** — `ls skills/riff/references/contracts/contract-lint.md skills/riff/references/contracts/type.template.md` 존재, `ls skills/riff-contracts/references 2>&1 | grep -c 'No such'` = 1

- [ ] **Step 4: Commit** — `refactor(contracts): riff-contracts 참조 이관 + 병렬 조건 명시`

---

### Task 6: PROVE — riff-qa 흡수 + canvas-lint.md·diff-review.md 신규

**Files:**
- Move: `skills/riff-qa/references/*` → `skills/riff/references/prove/`
- Create: `skills/riff/references/prove/canvas-lint.md`, `skills/riff/references/prove/diff-review.md`
- Modify: `skills/riff/references/prove/tier2-build.md`

- [ ] **Step 1: 이관**

```bash
mkdir -p skills/riff/references/prove
git mv skills/riff-qa/references/* skills/riff/references/prove/
```

- [ ] **Step 2: canvas-lint.md 작성** — 아래 내용 그대로:

````markdown
# canvas-lint — Tier 0 기계적 술어 5종

캔버스↔실상태 일치 검사. 전 depth 프로파일의 PROVE에 포함. 실행 위치: 메인 루프 인라인(grep/parse 수준).

| # | 술어 | 검사 방법 | 실패 시 조치 |
|---|---|---|---|
| 1 | 헤더 신선도 | CANVAS 헤더 `Cycle N` == `.riff/state.json`의 cycle && 최근 사이클 커밋 앵커 존재 | 헤더 갱신 지시 |
| 2 | 태스크 보드 동기 | CANVAS [3] 행 상태 == TaskCreate 태스크 상태 (done↔completed, active↔in_progress) | 어긋난 행 갱신 |
| 3 | 링크 해소 | CANVAS 안 `detail/`·`contracts/` 링크가 실존 파일 | 죽은 링크 제거·복원 |
| 4 | 섹션 상한 | STATUS≤10줄, [1]≤30, [2]≤20행, [3]≤30, [4]≤5개, [5]≤15 | "압축 규칙 적용" — 초과분 detail/ 오프로드 |
| 5 | PROVE 기록 최신성 | [4] 최신 행의 cycle == 현재 cycle | [4] 갱신 지시 |

SessionStart 훅이 재개 시 어긋남을 감지하면 이 lint를 먼저 실행한 후 작업 재개.
````

- [ ] **Step 3: diff-review.md 작성** — 아래 내용 그대로:

````markdown
# diff-review — 사이클당 1회 코드 정독

BUILD 완료 후 PROVE 내 서브스텝. 입력은 사이클 diff(`git diff <이전 사이클 커밋 앵커>..HEAD`)만.

## depth별 실행

| 프로파일 | 방식 |
|---|---|
| 단순 | 스킵 |
| 보통 | 메인 루프 인라인 self-review |
| 복잡 또는 core 태스크 포함 | `sonnet` 서브에이전트 독립 리뷰 (fresh-context) — codex 있으면 `/codex:review --wait --scope working-tree`가 대체 |

## 체크리스트

1. 삼켜진 에러·미실행 분기·검증 누락 엔드포인트·중복 로직
2. **스펙 준수 2문항**: FRAME이 요구하지 않은 것을 만들었나(스코프 크립)? FRAME이 요구한 것이 diff에 빠졌나?

## 산출

발견은 **Critical / Minor** 2단계만.
- Critical → 즉시 수정(기존 PROVE 실패 루프, ralph-loop 폴백 포함)
- Minor → 수정 없이 CANVAS [5]에 이연 기록(항체 머신 재사용)
결과를 CANVAS [4] 행에 기록.
````

- [ ] **Step 4: tier2-build.md 확장** — 기존 빌드/타입 검사 절 뒤에 추가:

```markdown
## v1.0 확장 — behavior + acceptance + 시크릿

1. **누적 behavior 검증**: `detail/acceptance/` 동결 체크 + core 태스크 행위 체크 전부 실행 (PROVE-lite에도 포함)
2. **시크릿 grep 1회**: 하드코딩 키·토큰 패턴 — `grep -rEn '(api[_-]?key|secret|token|password)\s*[:=]\s*["'"'"'][A-Za-z0-9_\-]{16,}' src/ app/ lib/ 2>/dev/null` 매치 시 FAIL
3. 실행 위치: 메인 루프 인라인(bash 직접 호출) — 서브에이전트 스폰 금지
```

- [ ] **Step 5: Verify**

```bash
ls skills/riff/references/prove/tier1-boundary.md skills/riff/references/prove/canvas-lint.md skills/riff/references/prove/diff-review.md
grep -c '술어' skills/riff/references/prove/canvas-lint.md  # 기대: >=2
grep -c 'Critical' skills/riff/references/prove/diff-review.md  # 기대: >=2
```

- [ ] **Step 6: Commit** — `feat(prove): riff-qa 흡수 + canvas-lint 술어 5종 + diff-review + Tier2 확장`

---

### Task 7: LEARN — riff-memory 흡수 + learn.md 신규

**Files:**
- Move: `skills/riff-memory/references/*` → `skills/riff/references/learn/`
- Create: `skills/riff/references/learn.md`

- [ ] **Step 1:** `mkdir -p skills/riff/references/learn && git mv skills/riff-memory/references/* skills/riff/references/learn/`

- [ ] **Step 2: learn.md 작성** — 아래 내용 그대로:

````markdown
# LEARN — 항체·프로파일·커밋 앵커

실행 위치: 메인 루프 인라인. 스키마는 `learn/antibody-schema.md`·`learn/profile-schema.md`.

## 순서

1. **항체**: 이번 사이클 버그 → 항체 생성/강화. 저장 전 dedup grep(`grep -rl <핵심 패턴> .riff/memory/antibodies/`) — 기존 항체 강화가 우선, 신규는 중복 없을 때만.
2. **red-green 검증** (신규 항체 + repro 테스트 생성 시에만): fix를 임시 되돌려 repro 실패(red) 확인 → 복원 후 통과(green) 확인. 실패 재현 안 되는 repro는 폐기(거짓 면역 방지).
3. **프로파일**: 2회 반복 관찰 → 학습, 명시 피드백 → 즉시 반영 (기존 규칙 유지).
4. **도메인 brief**: 같은 도메인 태스크 ≥3 누적 시 `detail/domains/<domain>.md` ≤20줄 생성·갱신 — 이후 해당 도메인 스폰 프롬프트에 주입. 3개 도메인 초과 시 STATUS에 팀 툴 졸업 안내 1줄.
5. **CANVAS [5] + STATUS 갱신** → 확신도 기록.
6. **사이클 커밋 앵커**: clean-tree 확인(`git status --porcelain` 비어야 함 — 미추적 잔재는 정리 후) → `git add -A && git commit -m "cycle-N: <1줄 요약>"`. 이 커밋이 되감기·diff-review·canvas-lint 술어 1의 앵커다.
7. **TUNE 발동 판단**: 마지막 TUNE 후 3~5사이클 경과 or rewind 직후 or no-progress 상한 → TUNE 제안(`tune.md`).
8. **세션 분리 판단**: 컨텍스트 압박 시 캔버스 갱신 완료 후 분리 권고.
````

- [ ] **Step 3: Verify** — `ls skills/riff/references/learn/antibody-schema.md` 존재, `grep -c 'red-green' skills/riff/references/learn.md` >= 1, `grep -c '커밋 앵커' skills/riff/references/learn.md` >= 2

- [ ] **Step 4: Commit** — `feat(learn): riff-memory 흡수 + red-green 항체·커밋 앵커·도메인 brief`

---

### Task 8: model-routing.md 신규

**Files:**
- Create: `skills/riff/references/model-routing.md`

- [ ] **Step 1: 작성** — 아래 내용 그대로:

````markdown
# 모델 라우팅

원칙: ① 티어 별칭(`opus`/`sonnet`/`haiku`)만 — 특정 버전 고정 금지(항상 최신 자동).
② **스폰 조건**: 서브에이전트 스폰은 정당화된 경우만 — 잼 · 동시 BUILD 태스크 ≥2 · 컨텍스트 압박.
그 외 순차 태스크·기계적 검증(Tier 0~2)·LEARN 기록은 메인 루프 인라인. 게이트 기준은 실행 위치와 무관하게 동일.

| 위치 | 모델 | 방식 |
|---|---|---|
| FRAME·SHAPE (기획) | Fable/Opus 권장 | 메인 루프 — 다른 모델이면 STATUS에 권장 안내 1줄 |
| SHAPE 잼 | `opus` | 스폰 |
| BUILD core (병렬) | `opus` | 스폰 |
| BUILD support (병렬) | `sonnet` | 스폰 |
| BUILD trivial (병렬) | `haiku` | 스폰 (동시 슬롯 상한 미포함) |
| BUILD (순차) | — | 메인 루프 인라인 |
| PROVE Tier 0~2 | — | 메인 루프 인라인 |
| PROVE Tier 3 (유령·파괴자) | `sonnet` | 스폰 (격리 가치) |
| PROVE diff-review (복잡/core) | `sonnet` | 스폰 (fresh-context 가치) |
| DROP 보안 딥스캔 | `sonnet` | 스폰 (보안 플래그 시 1회) |
| TUNE 스톡테이크 | `sonnet` | 스폰 (fresh-context 가치) |
| LEARN | — | 메인 루프 인라인 |

등급은 BUILD-PLAN에서 태스크 보드에 명시 → 사용자가 스폰 전 오버라이드 가능(`build.md`).
````

- [ ] **Step 2: Verify** — `grep -c '메인 루프 인라인' skills/riff/references/model-routing.md` >= 4

- [ ] **Step 3: Commit** — `feat(routing): 티어 별칭 라우팅 + 스폰 조건`

---

### Task 9: companions.md 신규 (부트스트랩 이관)

**Files:**
- Create: `skills/riff/references/companions.md`

- [ ] **Step 1: 작성** — 구 `skills/riff/SKILL.md`의 Bootstrap 절(점검 항목 표·사용자 응답 처리·Codex sandbox 권장 설정 전체)을 이 파일로 **그대로 복사**한 뒤, 점검 항목 표에 아래 행 추가 + 폴백 매트릭스 절 신설:

점검 항목 표에 추가할 행:

```markdown
| ecc plan-canvas | `command -v ecc-plan-canvas` | `npm install -g ecc-universal` | verdict 게이트 브라우저 리뷰 |
```

파일 끝에 추가:

````markdown
## 폴백 매트릭스 (있으면 강화, 없으면 네이티브 — 컴패니언 없이도 전 기능 동작)

| 기능 | 컴패니언 있으면 | 없으면 |
|---|---|---|
| PROVE 실패 루프 | `/ralph-loop:ralph-loop "<failure>" --max-iterations 3 --completion-promise 'VERIFY_PASSED'` | 자체 재시도 2회 → 실패 유형 진단 → 에스컬레이션 |
| SHAPE 대립 검토 | `/codex:adversarial-review --wait <focus>` 1회 | 잼에 반대 관점 에이전트 1개 추가 |
| diff-review (복잡 depth) | `/codex:review --wait --scope working-tree` | 인라인 self-review / `sonnet` 독립 리뷰 |
| verdict 게이트 | `ecc-plan-canvas open _workspace/CANVAS.md` → `await` — 요소 앵커 주석 + approve/request-changes, 수정 시 라이브 리로드, 끝나면 `end` | 터미널 구조화 질문 |

## Codex/GPT 모델 정책

모든 Codex 호출에 `--model` 미지정(기본값 = 최신, 자동 업데이트). 사용자 명시 요청 시만 지정. `--effort`도 동일.
````

- [ ] **Step 2: Verify** — `grep -c 'ecc-plan-canvas' skills/riff/references/companions.md` >= 3, `grep -c 'sandbox_mode' skills/riff/references/companions.md` >= 1

- [ ] **Step 3: Commit** — `feat(companions): 부트스트랩 이관 + ecc plan-canvas + 폴백 매트릭스`

---

### Task 10: drop.md·tune.md 신규 + rewind-protocol 개정

**Files:**
- Create: `skills/riff/references/drop.md`, `skills/riff/references/tune.md`
- Modify: `skills/riff/references/rewind-protocol.md`

- [ ] **Step 1: drop.md 작성** — 아래 내용 그대로:

````markdown
# DROP — 랜딩·발매 (이벤트 스테이지)

발동: 잼 병합 시 · 성공 기준 달성 시 · 사용자 요청 시. 사이클 핫패스 아님.

1. **검증 확인**: 마지막 PROVE 통과 + clean tree. 아니면 PROVE부터.
2. **랜딩 메뉴** (4택, 사용자 선택): merge / PR / keep(브랜치 유지) / discard
3. **worktree 정리**: 미채택 잼 워크트리 `git worktree remove` + `git worktree prune`
4. **보안 딥스캔**: BUILD 보안 플래그가 하나라도 있으면 `sonnet` 보안 패스 1회 필수(auth·인가·입력 검증·시크릿·CORS)
5. **원웨이도어**: push·publish·배포는 실행 전 사용자 확인(depth 무관)
6. **카나리 체크** (배포한 경우): 배포 URL 1패스 — HTTP 상태·콘솔 에러·핵심 요소 렌더·주요 API 응답. 실패 시 롤백 안내 + 원인을 다음 사이클 후보로.
7. **기록**: CANVAS STATUS·[5]에 DROP 기록, README quickstart 갱신.
````

- [ ] **Step 2: tune.md 작성** — 아래 내용 그대로:

````markdown
# TUNE — 조율 (이벤트 스테이지)

발동: 3~5사이클마다 · rewind 직후 · no-progress 상한(검증된 진행 없이 소비만 증가한 2사이클 연속) 도달 시. 사이클 핫패스 아님.

1. **스톡테이크** (`sonnet` 서브에이전트 1개, fresh-context): 코드 현실 ↔ CANVAS 재대조 —
   `TODO(prod)`·placeholder·스킵된 테스트(`.skip`)·미구현 스텁 사냥 → [3] 태스크 보드 재유도, 발견은 다음 사이클 후보로.
2. **가드닝** (메인 루프): 데드 코드·미사용 의존성·중복 제거 — **제거 1건마다 빌드+테스트 green 확인** 후 다음 제거.
3. **항체 라이프사이클**: dedup·90일 무재발 weakened 정리(`learn/antibody-schema.md`)·프로파일 정합 — 주입 페이로드 비대화 방지.
4. **컨텍스트·토큰 감사**: 캔버스 섹션 상한 점검, 오래된 detail/ `detail/archive/`로 이동.
5. **기록**: CANVAS [5]에 TUNE 요약 1줄 + 커밋 `tune: <요약>`.
````

- [ ] **Step 3: rewind-protocol.md 개정** — 용어 규칙 적용 + 복원 절차 첫 항목으로 추가:

```markdown
0. **git 앵커 복원**: 되감기 목표 사이클의 커밋 앵커(`cycle-N`)로 `git reset --hard <anchor>` (항체·`.riff/`는 보존 — 별도 디렉토리라 영향 없음). 앵커가 없으면(pre-v1.0 프로젝트) 기존 수동 절차 사용.
```

- [ ] **Step 4: Verify** — `grep -c '카나리' skills/riff/references/drop.md` >= 1, `grep -c 'green 확인' skills/riff/references/tune.md` >= 1, `grep -c 'git reset --hard' skills/riff/references/rewind-protocol.md` >= 1

- [ ] **Step 5: Commit** — `feat(stages): DROP·TUNE 이벤트 스테이지 + rewind git 앵커`

---

### Task 11: SKILL.md 전면 재작성

**Files:**
- Rewrite: `skills/riff/SKILL.md`

- [ ] **Step 1: 재작성** — 아래 내용 그대로 (frontmatter 트리거 문구는 기존 유지):

````markdown
---
name: riff
description: "신규 프로젝트·앱·MVP를 처음부터 만드는 AI-Native 루프. 질문이 캔버스를 채운다 — FRAME → SHAPE → BUILD → PROVE → LEARN을 빠르게 반복하며 매 사이클마다 작동하는 결과물과 살아있는 CANVAS.md를 남긴다. 'riff로 시작', '프로젝트 시작', '새 프로젝트', '앱 만들어줘', 'MVP', '프로토타입', '이거 만들어줘' 시 사용. 단순 버그 수정·작은 기능 추가에는 사용하지 않는다."
---

# Riff — 질문이 캔버스를 채운다

## 핵심 원칙

- 한 번에 잘 만들지 않는다. 빠르게 많이 시도한다.
- **CANVAS.md만으로 재시작 가능해야 한다** — 캔버스는 지도, detail/·contracts/는 영토.
- 질문은 트레이드오프가 있을 때만. 실패는 비용이 아니라 학습이다.
- 사이클 핫패스에 세리머니를 더하지 않는다(오버헤드 ≤15%). 무거운 일은 이벤트 스테이지(DROP·TUNE)로.

## Bootstrap (첫 호출 1회)

`references/companions.md` — ralph-loop·codex·ecc plan-canvas 점검, Install/Skip/Skip all.
가드: `_workspace/.riff-bootstrap-done` 또는 `.riff-bootstrap-skip-all` 존재 시 스킵.

## 캔버스

`references/canvas-schema.md`의 템플릿으로 `_workspace/CANVAS.md` 생성·유지.
v0.3.1 잔재(`riff-status.md` 등) 감지 시 1회 변환 제안. 쓰기는 메인 루프 단독.

## 세션 재개

SessionStart 훅이 CANVAS.md 감지 → STATUS 자동 로드. 어긋남 감지 시 canvas-lint 먼저.
훅 미설치 폴백: CANVAS.md 존재 확인 → STATUS부터 재개, 없으면 Cycle 0.

## Cycle 0 (프로젝트 부팅)

FRAME 복잡 프로파일로 시작(`references/frame.md`) → CANVAS 생성 → UI 있으면 `contracts/ui-stack.md` 확정.

## depth 판정 (사이클 시작 시 1회)

8신호 체크(가중치 없이 개수만):
상향 — 같은 패턴이 이전 사이클에서 검증 / 요구사항 명시적 / 유사 도메인·표준 패턴 존재 / 성공 기준 측정 가능
하향 — 요구 모호하지 않음 / 같은 영역 되감기 없음 / 외부 의존 낮음 / 트레이드오프 분석 완료

| 체크 수 | 프로파일 | 동작 |
|---|---|---|
| 6+/8 | 단순 | FRAME 스킵 가드 → 가정 선언, SHAPE 스킵, PROVE-lite(Tier 0+2) |
| 4~5/8 | 보통 | FRAME 2문항, PROVE Tier 0~2 + 인라인 diff-review |
| <4/8 | 복잡 | 풀 스테이지 + 잼 + Tier 0~3 + 독립 diff-review |

오버라이드: 사용자가 "가볍게"/"꼼꼼하게"로 강제 지정 가능.

## 사이클: FRAME → SHAPE → BUILD → PROVE → LEARN

| 스테이지 | 요약 | 세부 |
|---|---|---|
| FRAME | 질문·가정 선언으로 문제/성공 기준 확정, verdict 게이트 | `references/frame.md` |
| SHAPE | 결정 로그. 트레이드오프 불명확 시 잼(worktree 격리) | `references/shape-jam.md` |
| BUILD | 태스크 보드(등급·병렬·보안 플래그) → 병렬 시만 계약 → 구현 | `references/build.md` |
| PROVE | Tier 0~3 + canvas-lint + diff-review | `references/prove/` |
| LEARN | 항체(red-green)·프로파일·도메인 brief·**사이클 커밋 앵커** | `references/learn.md` |

## 이벤트 스테이지 (사이클 밖)

- **DROP** — 잼 병합·성공 기준 달성·사용자 요청 시: 랜딩 메뉴·worktree 정리·보안 딥스캔·카나리 (`references/drop.md`)
- **TUNE** — 3~5사이클·rewind 후·no-progress 시: 스톡테이크·가드닝·항체 정리·컨텍스트 감사 (`references/tune.md`)

## 가드 (전 스테이지 공통)

- **에스컬레이션**: PROVE 2회 실패 → 실패 유형 진단(기계적→재시도 / 설계→SHAPE 소급). 모호 발견 → FRAME 재진입. 3회 초과 → 되감기(`references/rewind-protocol.md`).
- **원웨이도어**: push·publish·파괴적 마이그레이션·배포 전 사용자 확인 (depth 무관).
- **컨텍스트 압박**: 스테이지 경계마다 확인 — 임계 초과 시 태스크 마무리·캔버스 갱신 후 세션 분리 권고.

## 모델 라우팅

`references/model-routing.md` — 스폰은 잼·병렬 태스크 ≥2·컨텍스트 압박일 때만. 그 외 인라인.

## OMC 공존

OMC 활성 시 Riff 사이클 중 OMC 모드·에이전트·스킬을 호출하지 않는다.
````

- [ ] **Step 2: Verify**

```bash
grep -c 'FRAME\|SHAPE\|PROVE' skills/riff/SKILL.md   # 기대: >=10
grep -c '분신술\|EXPLORE\|VERIFY\b' skills/riff/SKILL.md  # 기대: 0
grep -c 'references/' skills/riff/SKILL.md  # 기대: >=10 (progressive disclosure 포인터)
wc -l skills/riff/SKILL.md  # 기대: 120 이하 (얇은 코어)
```

- [ ] **Step 3: Commit** — `feat(core): SKILL.md 전면 재작성 — 캔버스·depth·이벤트 스테이지·가드`

---

### Task 12: 구 모듈 제거 + 잡파일 정리

**Files:**
- Delete: `skills/riff-interview/`, `skills/riff-qa/`, `skills/riff-contracts/`, `skills/riff-memory/` (남은 SKILL.md들)
- Delete(추적 시): `skills/.omc/`

- [ ] **Step 1:**

```bash
git rm -r skills/riff-interview skills/riff-qa skills/riff-contracts skills/riff-memory
git ls-files skills/.omc | head -1  # 출력 있으면: git rm -r skills/.omc / 없으면: rm -rf skills/.omc + .gitignore에 'skills/.omc/' 추가
```

- [ ] **Step 2: 잔존 참조 확인**

```bash
grep -rn 'riff-interview\|riff-qa\|riff-contracts\|riff-memory' skills/ hooks/ benchmarks/ .claude-plugin/  # 기대: 0건 (있으면 해당 참조를 새 경로로 수정)
```

- [ ] **Step 3: Commit** — `refactor: 구 4모듈 스킬 제거 — 단일 스킬 통합 완료`

---

### Task 13: hooks — session-start-canvas.sh 신규

**Files:**
- Create: `hooks/session-start-canvas.sh`
- Modify: `hooks/install.sh` (SessionStart 등록 추가), `hooks/README.md` (설명 1절 추가)

- [ ] **Step 1: 스크립트 작성** — 아래 내용 그대로:

```bash
#!/usr/bin/env bash
# SessionStart: _workspace/CANVAS.md 존재 시 STATUS 섹션을 컨텍스트로 주입
set -euo pipefail
CANVAS="_workspace/CANVAS.md"
[ -f "$CANVAS" ] || exit 0
STATUS=$(awk '/^## STATUS/{f=1;next}/^## /{f=0}f' "$CANVAS" | head -12)
[ -n "$STATUS" ] || exit 0
cat <<EOF
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"[riff] CANVAS.md 감지 — 현재 STATUS:\n${STATUS//\"/\\\"}\n재개 전 canvas-lint(references/prove/canvas-lint.md)로 어긋남 확인 후 STATUS의 '다음 액션'부터."}}
EOF
```

- [ ] **Step 2: install.sh에 SessionStart 훅 등록 추가** — 기존 SubagentStop 등록 패턴과 동일한 방식으로 `session-start-canvas.sh`를 SessionStart 이벤트에 append(기존 settings 보존, 중복 등록 가드 포함 — install.sh의 기존 jq/merge 패턴 재사용).

- [ ] **Step 3: Verify**

```bash
bash -n hooks/session-start-canvas.sh && bash -n hooks/install.sh  # 문법 OK
cd /tmp && mkdir -p riff-hook-test/_workspace && cd riff-hook-test && printf '# CANVAS — t\n\n## STATUS\n- 현재: Cycle 1 · BUILD\n\n## [1] FRAME\nx\n' > _workspace/CANVAS.md && bash <riff리포절대경로>/hooks/session-start-canvas.sh | python3 -m json.tool > /dev/null && echo HOOK_OK  # 기대: HOOK_OK
```

- [ ] **Step 4: Commit** — `feat(hooks): SessionStart 캔버스 STATUS 자동 로드`

---

### Task 14: 플러그인 매니페스트 v1.0.0

**Files:**
- Modify: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

- [ ] **Step 1: plugin.json** — `version` → `"1.0.0"`, `description` → `"질문이 캔버스를 채운다 — FRAME→SHAPE→BUILD→PROVE→LEARN 사이클과 Living CANVAS.md로 신규 웹앱·MVP를 빠르게 만드는 Question-Driven 루프. adaptive depth·모델 라우팅·잼(worktree 병렬 탐색)·Tier 0~3 QA·항체 메모리·DROP/TUNE 이벤트 스테이지 포함."`, `keywords`에 `"canvas"`, `"adaptive-depth"` 추가.

- [ ] **Step 2: marketplace.json** — plugins[0].version `"1.0.0"`, description 동일 갱신.

- [ ] **Step 3: Verify** — `python3 -m json.tool .claude-plugin/plugin.json > /dev/null && python3 -m json.tool .claude-plugin/marketplace.json > /dev/null && grep -c '1.0.0' .claude-plugin/plugin.json .claude-plugin/marketplace.json` (각 1 이상)

- [ ] **Step 4: Commit** — `feat(plugin): v1.0.0 매니페스트`

---

### Task 15: 벤치마크 신규 픽스처

**Files:**
- Create: `benchmarks/fixtures/depth/ambiguous-brief-notes.md`, `benchmarks/fixtures/depth/ambiguous-brief-tracker.md`, `benchmarks/fixtures/canvas/mid-build-restart.md`, `benchmarks/ground-truth/depth-ambiguous-notes.json`, `benchmarks/ground-truth/depth-ambiguous-tracker.json`, `benchmarks/ground-truth/canvas-restart.json`
- Modify: `benchmarks/README.md` (신규 시나리오 3종 표 추가)

- [ ] **Step 1: 모호 브리프 픽스처 2종 작성** — 정답이 '복잡'인 케이스:

`ambiguous-brief-notes.md`:
```markdown
# 시나리오: 모호 브리프 — 메모 앱
사용자 발화: "메모 앱 만들어줘"
숨은 모호성: 대상(개인/팀)? 동기화 필요? 마크다운? 오프라인? — 해석에 따라 아키텍처가 갈린다.
기대 동작: depth 판정 '복잡'(신호 <4/8) 또는 최소한 FRAME 스킵 금지 + 가정 선언 노출.
실패 판정: FRAME 완전 스킵 후 임의 해석으로 BUILD 진입.
```

`ambiguous-brief-tracker.md`:
```markdown
# 시나리오: 모호 브리프 — 트래커
사용자 발화: "운동 기록 트래커 하나 뚝딱 만들어줘"
숨은 모호성: 기록 항목? 시각화? 모바일? 데이터 보존? "뚝딱"이 단순 신호로 오독되기 쉬움.
기대 동작: '뚝딱'이라는 어휘에도 불구하고 성공 기준 부재 → 가정 선언 필수.
실패 판정: 신호 6+/8로 자가판정하고 가정 노출 없이 진행.
```

`depth-ambiguous-notes.json` / `depth-ambiguous-tracker.json` (동일 구조):
```json
{
  "scenario": "depth-ambiguous-notes",
  "expected_profile": "복잡",
  "allow_alternative": "보통+가정선언",
  "must_have": ["가정 선언 또는 FRAME 질문", "STATUS 활성 가정 노출"],
  "must_not": ["FRAME 완전 스킵", "성공 기준 없이 BUILD 진입"]
}
```

- [ ] **Step 2: canvas 재시작 픽스처 작성**

`mid-build-restart.md`:
```markdown
# 시나리오: BUILD 도중 강제 종료 후 재시작 (dirty exit)
설정: Cycle 3 BUILD에서 태스크 2/4 완료 상태의 CANVAS.md + TaskCreate 보드 + 커밋 앵커 cycle-2까지 존재.
세션 강제 종료 후 새 세션 시작.
기대 동작: STATUS 로드 → canvas-lint 술어 1·2 어긋남 감지 → 재조정 후 태스크 3부터 재개.
실패 판정: 완료된 태스크 재작업, 또는 Cycle 헤더/보드 불일치 방치.
```

`canvas-restart.json`:
```json
{
  "scenario": "canvas-mid-build-restart",
  "must_have": ["canvas-lint 선실행", "태스크 3부터 재개", "cycle-2 앵커 기준 diff 인지"],
  "must_not": ["태스크 1-2 재작업", "CANVAS 헤더 불일치 방치"]
}
```

- [ ] **Step 3: benchmarks/README.md에 시나리오 표 추가** (depth 2종·canvas 1종, 위 파일 경로와 판정 기준 1줄씩).

- [ ] **Step 4: Verify** — `for f in benchmarks/ground-truth/depth-ambiguous-notes.json benchmarks/ground-truth/depth-ambiguous-tracker.json benchmarks/ground-truth/canvas-restart.json; do python3 -m json.tool "$f" > /dev/null || echo "FAIL $f"; done` (출력 없음 기대)

- [ ] **Step 5: Commit** — `test(bench): depth 모호 브리프 2종 + canvas dirty-exit 재시작 픽스처`

---

### Task 16: README 전면 재작성 + PNG 제거

**Files:**
- Rewrite: `README.md`
- Delete: `docs/riff_cycle.png`, `docs/architecture.png`

- [ ] **Step 1: README.md 재작성** — 상단 배지 블록(1~29행)은 유지하되 버전 배지 `0.3.1`→`1.0.0`, `Modules-4_Skills` 배지 → `Canvas-Single_SSOT`, `QA-Tier_0~3` 유지. 본문은 아래 구성으로 재작성(각 절 실제 내용 포함, 총 250줄 이내):
  1. **한 줄 정의**: "질문이 캔버스를 채운다" + Riff = FRAME→SHAPE→BUILD→PROVE→LEARN (+DROP·TUNE)
  2. **Why**: 기존 "질문 없이 vs 질문과 함께" 예시 유지 + CANVAS.md 재시작 스니펫
  3. **사이클 다이어그램**: mermaid `flowchart LR` — `F[FRAME] --> S[SHAPE] --> B[BUILD] --> P[PROVE] --> L[LEARN] -.->|3~5사이클| T[TUNE]` + `L -->|마일스톤| D[DROP]` (PNG 대체)
  4. **Quick Start**: `/plugin marketplace add joyuno/riff` + `/plugin install riff@joyuno-riff` 단일 설치(모듈 설치 절 삭제)
  5. **핵심 기능 4절**: Living Canvas(UPDATE RULE 스니펫) / adaptive depth(신호 표) / 모델 라우팅(등급표) / 잼·이벤트 스테이지
  6. **Companions**: ralph-loop·codex·ecc plan-canvas 표 + 폴백 요약
  7. **Comparison 표**: 기존 표 갱신 — Riff 열에 "질문이 캔버스를 채운다 / Cycle(분) / 매 사이클 QA+커밋 앵커 / 자동 학습+red-green"
  8. **Use Cases**: 기존 5개 프롬프트 유지
  9. **Plugin Structure**: Task File Structure의 최종 트리
  10. Requirements(Agent Teams 항목 삭제 — 스펙 v1.2에서 미사용)·License

- [ ] **Step 2:** `git rm docs/riff_cycle.png docs/architecture.png`

- [ ] **Step 3: Verify**

```bash
grep -c 'mermaid' README.md          # 기대: >=1
grep -c '분신술\|EXPLORE\|ASK →\|VERIFY' README.md  # 기대: 0
grep -c 'riff-interview\|riff-qa@\|install riff@riff-' README.md  # 기대: 0
grep -c '1.0.0' README.md            # 기대: >=1
```

- [ ] **Step 4: Commit** — `docs: README v1.0 전면 재작성 — mermaid 다이어그램·단일 설치·잼 용어`

---

### Task 17: 최종 sweep + 전체 검증

**Files:** 전체 (수정 발생 시에만)

- [ ] **Step 1: 용어 sweep**

```bash
grep -rn '분신술' --include='*.md' --include='*.sh' --include='*.json' . | grep -v 'docs/superpowers\|exa-results\|.git/'  # 기대: 0건
grep -rn 'riff-status.md' skills/ hooks/ README.md | grep -v 'canvas-schema.md\|마이그레이션'  # 기대: 0건 (마이그레이션 안내 제외)
grep -rn 'EXPLORE\|VERIFY' skills/riff/SKILL.md README.md  # 기대: 0건
```

- [ ] **Step 2: 구조 검증**

```bash
ls skills/riff/references/{canvas-schema,frame,shape-jam,build,learn,model-routing,companions,drop,tune}.md skills/riff/references/{contracts,prove,frame,learn} > /dev/null && echo TREE_OK
python3 -m json.tool .claude-plugin/plugin.json > /dev/null && bash -n hooks/*.sh && echo VALID_OK
ls skills/ | grep -vc '^riff$'  # 기대: 0 (riff 하나만)
```

- [ ] **Step 3: 스펙 대조** — 스펙 §3~§8의 각 규칙이 참조 파일 어디에 있는지 1:1로 짚고, 누락 발견 시 해당 태스크 파일에 즉시 추가.

- [ ] **Step 4: Commit** (수정 있을 시) — `chore: v1.0 최종 sweep`

---

## Self-Review 결과

- **Spec coverage**: §3 캔버스→Task 1 / §4 FRAME 가드·acceptance→Task 2, 잼→Task 3, BUILD 규칙→Task 4·5, PROVE(canvas-lint·diff-review·Tier2)→Task 6, LEARN(red-green·앵커·brief)→Task 7, 에스컬레이션·가드→Task 11, DROP·TUNE→Task 10 / §5 라우팅→Task 8 / §6 컴패니언·훅·슬롯→Task 9·13·4 / §7 구조·마이그레이션→Task 12·14·16, 캔버스 변환→Task 1 / §8 벤치마크→Task 15 (speed-tax·rewind-anchor 시나리오는 실행 하네스 필요 — 픽스처만 v1.0 범위, 측정 스크립트는 후속. benchmarks/README에 명시).
- **Placeholder scan**: 통과 — 모든 신규 파일 전문 수록, 이관 태스크는 정확한 명령+치환 규칙.
- **Type consistency**: 참조 경로(`references/prove/canvas-lint.md` 등)와 SKILL.md 포인터 일치 확인. 태스크 등급 어휘(core/support/trivial), 프로파일 어휘(단순/보통/복잡) 전 태스크 통일.
