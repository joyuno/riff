# riff v1.0 전면 개편 설계 — "질문이 캔버스를 채운다" (spec v1.2)

- 날짜: 2026-07-31 (v1.2 — 루프 엔지니어링 갭 스캔 반영: 이벤트 스테이지 DROP·TUNE + 보강 8건)
- 상태: 브레인스토밍 결정 8건 승인 → 적대적 감사(16 에이전트, real 6/overstated 5) 보완 전부 반영 → ECC 캔버스 요소 4건 채택 → 루프 갭 스캔(Ralph 정론·superpowers/OMC 캐시·ECC 3소스) 채택
- 근거: `exa-results/riff-revamp-research-2026-07-30.md` (리서치 232 소스) · `2026-07-31-riff-revamp-audit.md` (감사 상세)

## 1. 배경과 목표

riff v0.3.1은 Question-Driven Development 플러그인으로 interview-first·계약 교환·매 사이클 검증을 선취했으나, 2026년 중반 기준 다음 갭이 확인됐다:

1. **Living Canvas 부재** — 산출물이 `riff-status.md`/`riff-log.md`/`riff-N/`으로 파편화되어 "이 문서만으로 재시작"(ExecPlan 패턴)이 불가능.
2. **Adaptive depth 부재** — 질문 예산은 있으나 스테이지 자체가 고정 5단계.
3. **플랫폼 신기능 미활용** — TaskCreate 공유 작업목록, worktree 격리 서브에이전트, SessionStart 훅.
4. **모델 라우팅 부재** — 단, 감사 결과(R5) "스폰 강제"는 속도 역전을 낳으므로 라우팅은 병렬 상황에만 적용.
5. **드리프트 관리 부재** — 문서와 구현이 어긋나도 탐지 장치 없음.

**목표**: "완성도 높지만 빠른 프로토타이핑" — superpowers(무거운 규율)와 GSD류 경량 툴(기획 없음) 사이의 중간 지점.

## 2. 확정 결정 요약

| # | 결정 사항 | 선택 |
|---|---|---|
| 1 | 정체성 | **질문이 캔버스를 채운다** — Question-Driven 유지 + Living Canvas SSOT |
| 2 | 캔버스 구조 | **단일 CANVAS.md = 지도**, 상세는 `detail/` 오프로드 + 링크 |
| 3 | 깊이 조절 | **자동 감지 + 실패 에스컬레이션** (신호 체크리스트 기반) |
| 4 | 모듈 구조 | **단일 플러그인 통합** — 4개 모듈을 references/로 흡수 |
| 5 | 스테이지 | **FRAME → SHAPE → BUILD → PROVE → LEARN** (5단계 재명명) |
| 6 | 모델 라우팅 | **태스크 등급표 + 티어 별칭 + 사용자 오버라이드** (병렬 시에만 스폰 — R5) |
| 7 | 플랫폼 통합 | **네이티브 우선 + 컴패니언 폴백** (훅 강제 게이트 없음 — 권고만) |
| 8 | 용어 | **"분신술" → "잼(Jam)"** 전면 교체 (음악 은유로 브랜드 통일) |
| 9 | 감사 보완 | **real 6건(R1~R6) + 명문화 4건 전부 반영** — 본문에 [R#] 표기 |
| 10 | ECC 벤치마킹 | **plan-canvas 컴패니언(E1)·Update Rule(E2)·mermaid(E3)·verdict(E4)** 채택 |
| 11 | 루프 갭 스캔 | **이벤트 스테이지 DROP·TUNE 추가 + 보강 8건** — 사이클 핫패스 불변, 본문 [루프 스캔] 표기 |

## 3. CANVAS.md 스키마

원칙: **이 문서만으로 재시작 가능해야 한다.**

```markdown
# CANVAS — <프로젝트명>
> 마지막 갱신: Cycle N · <스테이지> · <날짜>

## UPDATE RULE                              (고정 5줄 — 문서가 자기 유지 정책 기술) [E2]
현재 사이클만 상세히. 스테이지 종료 시 해당 섹션 갱신. 섹션 상한 초과 시
오래된 내용은 detail/로 내리고 링크만 남긴다. 완료 사이클은 1줄 요약으로 접는다.
아키텍처·플로우·상태머신은 mermaid 블록으로 그린다. [E3]

## STATUS                                   (10줄 이내)
현재 위치 · 성공 기준 진행도 · depth 프로파일(신호 n/8) · 활성 가정 [R4] · 다음 액션 1줄

## [1] FRAME — 문제와 성공 기준              (상한 30줄)
질문→답 요약, 핵심 Job, 페르소나 1줄씩, 측정 가능한 성공 기준
FRAME 스킵 시 가정 선언 기록 [R4] / 상세 인터뷰 전문 → detail/frame-*.md 링크

## [2] SHAPE — 결정 로그                     (상한 20행 테이블)
| # | 결정 | 기각된 대안 | 근거 | cycle |
잼(Jam) 결과는 요약 1줄 + detail/ 링크. 구조 결정은 mermaid로 병기 [E3]

## [3] BUILD — 계약 + 태스크 보드            (상한 30줄)
활성 계약 링크 + 1줄 요약 / 태스크: 등급(core·support·trivial)·모델·병렬 여부 명시

## [4] PROVE — 검증 게이트 기록              (최근 5개만)
tier · 통과/실패 · diff-review 결과(Critical/Minor) [R2] · 에스컬레이션 여부

## [5] LEARN — 항체 & 다음 사이클            (상한 15줄)
새 항체 포인터 · 확신도 · 다음 사이클 후보 · 도메인 brief 포인터
```

**운영 규칙**
1. **갱신 규칙(권고)**: 각 스테이지 종료 시 해당 섹션 갱신. 훅으로 강제하지 않는다. 미갱신은 canvas-lint(§4 PROVE)가 탐지.
2. **압축 규칙**: UPDATE RULE 섹션에 자기 기술 — 세션·스킬 컨텍스트가 없어도 규칙이 문서와 함께 이동한다. [E2]
3. **single-writer** [명문화]: CANVAS.md 쓰기는 메인 루프 단독. 서브에이전트는 `detail/`·`contracts/`·TaskCreate에만 기록한다.
4. **verdict 게이트** [E4]: FRAME 산출(또는 가정 선언)과 사이클 종료는 명시적 approve/request-changes로 닫는다 — plan-canvas 컴패니언이 있으면 브라우저에서 요소 단위 주석+판정, 없으면 터미널 질문.

```
프로젝트루트/
├── _workspace/
│   ├── CANVAS.md            ← 유일 SSOT (지도)
│   ├── contracts/           ← 계약서 (병렬 빌드 시에만 생성 — R6)
│   └── detail/              ← 인터뷰 전문·잼 결과·검증 상세 (영토)
└── .riff/                   ← 항체·프로파일·세션 상태 (기존 유지)
```

## 4. 스테이지 설계 + Adaptive Depth

| 스테이지 | 역할 | 얕을 때 | 깊을 때 |
|---|---|---|---|
| **FRAME** | 질문으로 문제·성공 기준 확정 | 가정 선언 1줄 [R4] 또는 핵심 2문항 | 5-Layer 인터뷰 + 도메인 분기 |
| **SHAPE** | 트레이드오프 결정, 결정 로그 | 스킵 (결정 로그 1행만) | 잼 2-3방향 + codex 대립 검토 |
| **BUILD** | (병렬 시 계약 →) 태스크 보드 → 구현 | 계약 없음, 순차 인라인 | 8종 계약 + lint + 병렬 스폰 |
| **PROVE** | 검증 게이트 + diff-review [R2] | Tier 0+2 + 인라인 self-review | Tier 0~3 풀 + sonnet 독립 리뷰 |
| **LEARN** | 항체·프로파일·캔버스 갱신 | 캔버스 [5]만 갱신 | 항체 생성 + 도메인 brief + 세션 분리 판단 |

**깊이 결정**: 사이클 시작 시 1회, 8신호 체크리스트(가중치 없는 체크 개수 — LLM 재현성)로 판정.
- 신호 6+/8 → 단순 / 4~5 → 보통 / <4 → 복잡(풀 스테이지 + 잼)

**FRAME 스킵 가드** [R4]: FRAME 완전 스킵은 CANVAS [1]에 성공 기준이 이미 존재할 때만 허용. 없으면 스킵 대신 **가정 선언** — 채택한 해석과 성공 기준 각 1줄을 [1]에 기록하고 STATUS에 "가정: X — 아니면 지금 말해주세요"로 노출(verdict 게이트 [E4] 대상). 조용한 해석이 외부에서 거부 가능한 커밋으로 바뀌고, canvas-lint의 앵커가 생겨 PROVE-lite로도 "잘못된 제품"이 탐지 가능해진다.

**FRAME 수용 기준 규칙** [루프 스캔]: ① 얕은 경로의 성공 기준·가정 선언은 "Tier 2 체크가 실행할 수 있는 관찰 가능한 행동"을 명시해야 한다(testability 가드 — 'PRD theater' 방지). ② verdict 승인 시점에 core급 작업의 수용 기준에서 실행 가능한 acceptance check 1~3개를 유도해 **동결**하고 Tier 2가 함께 실행한다 — 코드를 쓴 에이전트가 검증도 쓰는 자기채점 차단(단순 depth는 스킵).

**BUILD** [R1·R6]:
- **계약 조건** [R6]: 계약 작성은 태스크 보드에 잼 또는 병렬 스폰이 계획된 경우에만(BUILD-PLAN이 이미 아는 정보). 순차 빌드는 코드의 타입 선언이 계약이고 tsc가 lint — 계약서 생략. deep 프로파일(병렬)은 8종 계약 + lint 게이트 불변.
- **행위 체크** [R1]: core 등급 태스크의 산출물에는 해당 태스크의 행위 계약에서 유도한 **실행 가능한 체크 ≥1개**(테스트 또는 assertion 스크립트)를 포함한다. 작성 순서(테스트 우선 여부)는 강제하지 않는다.
- **보안 트리거 술어** [루프 스캔]: BUILD-PLAN에서 변경이 auth·결제·시크릿·유저 데이터를 만지거나 >20파일이면 플래그 → DROP 전 `sonnet` 보안 패스 1회 예약(사이클당 비용 0, 판정은 불리언 1개).

**PROVE**:
- Tier 0: 계약 검사(계약 존재 시만 [R6]) + **canvas-lint — 기계적 술어 5개** [R3]: ① 헤더 `Cycle N` = `.riff/` 세션 상태 일치 ② 캔버스 [3] ↔ TaskCreate 상태 diff 청결 ③ `detail/`·`contracts/` 링크 해소 ④ 섹션 상한 준수(위반 = "압축 규칙 적용" 지시) ⑤ [4] PROVE 기록 최신성
- Tier 2: **빌드/타입 + 누적 behavior 검증 + 동결 acceptance check 실행** [R1·루프 스캔] — PROVE-lite에도 포함되므로 얕은 사이클도 행위 검증을 유지. **시크릿 패턴 grep 1회** 포함(하드코딩 키·토큰, <1% 오버헤드)
- **diff-review 서브스텝 (사이클당 1회)** [R2]: 단순 = 스킵 / 보통 = 메인 루프 인라인 self-review / 복잡 또는 core 포함 = `sonnet` 독립 리뷰. 발견은 Critical/Minor 2단계만 — Critical은 기존 PROVE 실패 루프로 즉시 수정, Minor는 LEARN에 이연 기록. codex 있으면 codex review가 리뷰어(§6). 리뷰 체크리스트에 **스펙 준수 2문항** 포함 [루프 스캔]: "FRAME이 요구하지 않은 것을 만들었나(스코프 크립)? FRAME이 요구한 것이 diff에 빠졌나?"

**에스컬레이션 트리거**:
- PROVE 2회 실패 → **실패 유형 진단(메인 루프)** [명문화]: 기계적 실패(빌드·flaky)로 진단되면 같은 사이클에서 재시도 지속, 설계 실패면 SHAPE 소급(잼 발동)
- 구현 중 요구 모호 발견 → FRAME 재진입 (질문 1~3개만)
- 같은 계약 3회 수정 → 계약 재설계 + 사용자 개입 / 3회 초과 → 되감기(기존 프로토콜, 사이클 커밋 앵커 기반)
- **원웨이도어 게이트** [루프 스캔]: git push·패키지 publish·파괴적 마이그레이션·배포 등 비가역 행동 전에는 depth 무관 사용자 확인. **no-progress 상한**: 검증된 진행 없이 소비만 증가한 2사이클 연속 시 TUNE 발동 제안
- **컨텍스트 압박 체크** [루프 스캔]: 스테이지 경계마다 사용률 확인 — 임계 초과 시 진행 중 태스크만 마무리, 캔버스 갱신 후 세션 분리 권고 (미드-스테이지 자동 컴팩션의 in-flight 상태 소실 방지)

**LEARN**:
- 재현 가능한 버그의 항체에는 **repro 테스트 첨부** [R1] → Tier 2가 회귀로 실행
- **도메인 brief** [명문화]: 같은 도메인 태스크 ≥3 누적 시 ≤20줄 `detail/domains/<domain>.md` 생성, 이후 해당 도메인 스폰 프롬프트에 주입. 3개 도메인 초과 시 STATUS에 팀 아키텍처 툴(harness/Agent Teams) 졸업 안내 1줄.
- **사이클 커밋 앵커** [루프 스캔]: LEARN 종료 = clean-tree 확인 후 `git add -A && git commit`(메인 루프 인라인, 초 단위) — 되감기가 git ref 기반으로 결정적이 되고 canvas-lint 술어 ①의 앵커가 된다.
- **red-green 항체 검증** [루프 스캔]: 신규 항체의 repro 테스트는 fix를 임시 되돌려 실패(red) 확인 후 복원(green) — 항상 통과하는 가짜 repro의 거짓 면역 차단(신규 항체 생성 시에만, ~1분).

### 이벤트 스테이지 (사이클 밖 — 핫패스 세금 0) [루프 스캔]

**DROP — 랜딩·발매** (마일스톤 발동: 잼 병합·성공 기준 달성·사용자 요청)
1. 검증 통과 확인 → 4택 랜딩 메뉴: **merge / PR / keep / discard**
2. worktree 정리 (미채택 잼 워크트리 remove/prune)
3. 보안 딥스캔 (BUILD의 보안 트리거 플래그가 있으면 `sonnet` 패스 필수)
4. 배포 시 **카나리 체크**: 배포 URL의 HTTP 상태·콘솔 에러·핵심 요소·주요 API 1패스 — "로컬은 되는데 배포에서 죽는" 최빈 실패 차단
5. CANVAS에 DROP 기록 + README quickstart 갱신

**TUNE — 조율** (주기 발동: 3~5사이클마다 · rewind 직후 · no-progress 상한 도달 시)
1. **스톡테이크**: 코드 현실 ↔ CANVAS 재대조 — TODO(prod)·placeholder·스킵된 테스트·미구현 스텁 사냥, [3] 태스크 보드 재유도 (`sonnet` 서브에이전트 1개, fresh-context 가치)
2. **가드닝**: 데드 코드·미사용 의존성·중복 제거 — 제거마다 빌드+테스트 green 가드
3. **항체 라이프사이클**: dedup·90일 무재발 weakened 정리·프로파일 정합 — 주입 페이로드 비대화 방지
4. **컨텍스트·토큰 감사**: 캔버스 압축 상태 점검, detail/ 아카이빙

## 5. 모델 라우팅

원칙: ① 티어 별칭(`opus`/`sonnet`/`haiku`)만 — 버전 고정 금지. ② **라우팅 조건** [R5]: 서브에이전트 스폰(모델 강제 지정)은 스폰이 정당화된 경우에만 — 잼, 동시 실행 BUILD 태스크 ≥2, 컨텍스트 압박. 그 외 순차 태스크·기계적 검증·LEARN 기록은 **메인 루프가 인라인 실행**하고 결과만 캔버스에 기록한다. 게이트 기준(tier 판정·항체 기록 의무)은 실행 위치와 무관하게 동일.

| 위치 | 작업 | 모델 | 방식 |
|---|---|---|---|
| FRAME·SHAPE | 질문 설계·트레이드오프 판단 | Fable 5/Opus 5 권장 | 메인 루프 — 다른 모델이면 STATUS에 권장 안내 |
| SHAPE 잼 | 대안 동시 탐색 | `opus` | 서브에이전트 (스폰 정당) |
| BUILD core (병렬 시) | 핵심 로직·아키텍처 | `opus` | 태스크 등급 → 스폰 시 지정 |
| BUILD support (병렬 시) | 보조 기능·UI·CRUD | `sonnet` | 〃 |
| BUILD trivial (병렬 시) | 설정·보일러플레이트 | `haiku` | 〃 |
| BUILD (순차) | 위 전부 | 메인 루프 인라인 [R5] | — |
| PROVE Tier 0~2 | 기계적 검증 | 메인 루프 인라인 [R5] | — |
| PROVE Tier 3 | 유령 사용자·파괴자 | `sonnet` | 서브에이전트 (격리 가치) |
| PROVE diff-review | 복잡/core 사이클 독립 리뷰 [R2] | `sonnet` | 서브에이전트 (fresh-context 가치) |
| PROVE 실패 분석 | 원인 진단·에스컬레이션 판단 | 메인 루프 | — |
| LEARN | 항체·프로파일 기록·사이클 커밋 | 메인 루프 인라인 [R5] | — |
| DROP 보안 딥스캔 | 트리거 플래그 시 1회 | `sonnet` | 서브에이전트 |
| TUNE 스톡테이크 | 코드↔캔버스 재대조 감사 | `sonnet` | 서브에이전트 (fresh-context 가치) |

**등급 판정**: BUILD-PLAN에서 태스크마다 등급+병렬 여부 명시 → 캔버스 [3] 노출 → 스폰 전 사용자 오버라이드 가능. 기준: 성공 기준 직결(core) / 접점이나 대체 가능(support) / 실패해도 즉시 재시도(trivial). 애매하면 상위 등급.

## 6. 플랫폼 통합

**네이티브 편입 3종:**
1. **TaskCreate 공유 작업목록** = BUILD 태스크 보드의 실체(등급·모델·병렬 여부 메타데이터). 캔버스 [3]은 요약 뷰.
2. **worktree 격리 서브에이전트** = 잼의 실행 방식. 미채택 방향은 워크트리째 폐기.
   - **병렬 슬롯** [명문화]: 동시 슬롯 3 유지하되 웨이브 배리어 대신 태스크 완료 즉시 보드에서 다음 태스크 충원. trivial(haiku)은 상한 미포함. 사용자 오버라이드 가능.
3. **SessionStart 훅**: CANVAS.md 감지 시 STATUS 자동 로드. 로드 시 마지막 갱신 스테이지와 실제 상태(working tree·TaskCreate)가 어긋나면 canvas-lint 재조정을 먼저 실행 [명문화]. 기존 SubagentStop 진행률 훅 유지. Stop 훅 강제 게이트 없음.

**컴패니언 폴백 매트릭스** (있으면 강화, 없으면 네이티브 폴백 — 컴패니언 없이도 전 기능 동작):

| 기능 | 컴패니언 있으면 | 없으면 (네이티브 폴백) |
|---|---|---|
| PROVE 실패 루프 | `ralph-loop --completion-promise` | 자체 재시도 2회 → 실패 유형 진단 → 에스컬레이션 |
| SHAPE 대립 검토 | `codex adversarial-review` 1회 | 잼에 반대 관점 에이전트 1개 추가 |
| diff-review (복잡 depth) [R2] | `codex review` | §4 폴백 사다리 (인라인 self-review / sonnet) |
| **verdict 게이트** [E1·E4] | `ecc-plan-canvas open/await CANVAS.md` — 브라우저에서 요소 앵커 주석 + approve/request-changes, 파일 수정 시 라이브 리로드 | 터미널 구조화 질문 |

부트스트랩: 첫 호출 시 1회 제안(ralph-loop · codex · **ecc plan-canvas** — `command -v ecc-plan-canvas`, 누락 시 `npm i -g ecc-universal` 제안), Skip해도 기능 손실 없음. Codex 모델 정책(`--model` 미지정) 유지.

## 7. 플러그인 구조 & 마이그레이션

```
riff/  (v1.0.0)
├─ .claude-plugin/           ← 단일 플러그인으로 정리
├─ skills/riff/
│   ├─ SKILL.md              ← 코어 루프 + depth 신호 + 라우팅 조건 요약만 (얇게)
│   └─ references/           ← 구 4모듈 흡수 (progressive disclosure)
│       ├─ canvas-schema.md  ←   UPDATE RULE·mermaid·verdict 규칙 포함 [E2~E4]
│       ├─ frame.md          ←   구 riff-interview + 가정 선언 [R4]
│       ├─ shape-jam.md      ←   구 explore-protocol + 잼 프로토콜
│       ├─ build.md          ←   태스크 등급 + 계약 조건(병렬 시만) [R6] + 행위 체크 [R1]
│       ├─ contracts/        ←   구 riff-contracts (8종 템플릿 + lint)
│       ├─ prove/            ←   구 riff-qa + canvas-lint 술어 [R3] + diff-review [R2]
│       ├─ learn.md          ←   구 riff-memory + repro 항체 [R1] + 도메인 brief
│       ├─ model-routing.md  ←   라우팅 조건 [R5] + 등급표
│       ├─ companions.md     ←   폴백 매트릭스(4행) + 부트스트랩 [E1]
│       ├─ drop.md · tune.md ←   이벤트 스테이지 [루프 스캔]
│       └─ rewind.md · convergence.md
├─ hooks/                    ← session-start-canvas 추가, riff-progress 유지
├─ benchmarks/               ← 기존 픽스처 + 신규 (§8)
└─ README.md                 ← 전면 재작성 (잼 용어, 새 다이어그램)
```

**마이그레이션:**
- v0.3.1 → **v1.0.0** (breaking: 모듈 4종 플러그인 제거, `_workspace/` 구조 변경)
- 기존 프로젝트: 첫 실행 시 `riff-status.md`/`riff-log.md` 감지 → `CANVAS.md` 변환 1회 제안
- 구 모듈 4종: 마켓플레이스 deprecated 표시 / 용어 "분신술" → "잼" 전면 교체 / README·다이어그램 재생성

## 8. 검증 계획

1. **기존 벤치마크 픽스처 유지** (interview·boundary·immunity·live-app) — 회귀 없음 확인
2. **canvas-restart**: 세션 종료 후 CANVAS.md만으로 재개 정확도. **스테이지 중간 강제 종료(dirty exit) 후 재개 케이스 포함** [명문화]
3. **depth-reproducibility**: 동일 픽스처의 depth 판정 일관성 + **정답이 '복잡'인 모호 브리프 픽스처 2~3개** [R4] — 일관성만이 아니라 정답률 측정
4. **speed-tax**: medium 프로파일 표준 사이클의 오버헤드 연산 수 측정 — bare 대비 wall-clock 세금이 목표선(≤15%) 이내인지 [R5·R6 회귀 방지]. 이벤트 스테이지(DROP·TUNE)는 사이클 밖이므로 측정 제외
5. **rewind-anchor**: 사이클 커밋 앵커 기반 되감기가 워킹트리·캔버스·계약 상태를 일관되게 복원하는지 [루프 스캔]

## 9. 용어집

| 용어 | 의미 |
|---|---|
| **캔버스(Canvas)** | 프로젝트의 유일 SSOT 문서 (`_workspace/CANVAS.md`) |
| **잼(Jam)** | 여러 에이전트가 격리 워크트리에서 대안을 동시 탐색 (구 "분신술") |
| **사이클(Cycle)** | FRAME→SHAPE→BUILD→PROVE→LEARN 1회전 (구 "Riff N") |
| **depth 프로파일** | 신호 체크 결과에 따른 스테이지별 깊이 (단순/보통/복잡) |
| **가정 선언** | FRAME 스킵 대신 채택한 해석+성공 기준을 명시·노출하는 1줄 커밋 [R4] |
| **verdict 게이트** | FRAME 산출·사이클 종료의 approve/request-changes 명시 판정 [E4] |
| **diff-review** | 사이클당 1회 코드 정독 서브스텝, Critical/Minor 2단계 [R2] |
| **canvas-lint** | 캔버스↔실상태 일치를 검사하는 기계적 술어 5종 [R3] |
| **도메인 brief** | 도메인별 ≤20줄 관례 요약, 스폰 프롬프트 주입물 |
| **에스컬레이션** | 실패·모호 신호 시 건너뛴 스테이지를 소급 발동 |
| **항체(Antibody)** | 실수 재발 방지 체크리스트 + 재현 시 repro 테스트 [R1] — red-green 검증 필수 |
| **DROP** | 마일스톤 랜딩·발매 이벤트 스테이지: 랜딩 메뉴·worktree 정리·보안 딥스캔·카나리 |
| **TUNE** | 주기 조율 이벤트 스테이지: 스톡테이크·가드닝·항체 라이프사이클·컨텍스트 감사 |
| **원웨이도어 게이트** | 비가역 행동(push·publish·마이그레이션·배포) 전 사용자 확인 |
| **acceptance 동결** | FRAME verdict 시 수용 기준에서 유도한 실행 가능 체크 1~3개를 고정, Tier 2가 실행 |
