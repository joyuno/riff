---
name: riff
description: "신규 프로젝트·앱·MVP를 처음부터 만드는 AI-Native 루프. ASK → EXPLORE → BUILD → VERIFY → LEARN을 빠르게 반복하며 매 사이클마다 작동하는 결과물을 만든다. 'riff로 시작', '프로젝트 시작', '새 프로젝트', '앱 만들어줘', 'MVP', '프로토타입', '이거 만들어줘' 시 사용. 단순 버그 수정·작은 기능 추가에는 사용하지 않는다."
---

# Riff — AI-Native Project Loop

## Bootstrap (첫 호출 시 1회)

이 프로젝트에서 `riff`를 처음 호출할 때 다음 의존성을 점검하고, 누락된 것을 사용자에게 한 번 물어 자동 설치한다. 부트스트랩 재실행 가드: `_workspace/.riff-bootstrap-done` **또는** `_workspace/.riff-bootstrap-skip-all` 둘 중 하나라도 존재하면 스킵.

### 점검 항목 (각 항목마다 on/off 선택 가능)

| 의존성 | 점검 방법 | 누락 시 자동 동작 | 효과 |
|--------|-----------|------------------|------|
| `ralph-loop` 플러그인 | `~/.claude/plugins/cache/claude-plugins-official/ralph-loop` 존재 | `/plugin install ralph-loop@anthropic` | VERIFY-FIX 자동 루프 |
| `codex` 플러그인 | `~/.claude/plugins/cache/openai-codex/codex` 존재 | `/plugin marketplace add openai/codex-plugin-cc` + `/plugin install codex@openai-codex` | EXPLORE 분신, VERIFY cross-check |
| Codex CLI | `command -v codex` | `npm install -g @openai/codex` | 위 두 기능의 런타임 |
| Codex 로그인 | `node ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs setup --json` 의 `loggedIn: true` (codex 플러그인 캐시의 절대 경로 사용 — `${CLAUDE_PLUGIN_ROOT}`는 riff 컨텍스트라 부적합) | 사용자에게 `!codex login` 안내 (OAuth는 브라우저 필요) | Codex 호출 권한 |
| Codex sandbox 설정 | `~/.codex/config.toml`에 `sandbox_mode`/`approval_policy` 키 + 현재 프로젝트 `[projects."<cwd>"]` 섹션의 `trust_level = "trusted"` 존재 여부 | 누락된 키만 append (기존 설정 보존, 변경 전 `~/.codex/config.toml.bak`로 백업) — 아래 "Codex sandbox 권장 설정" 참조 | `/codex:review`·`/codex:adversarial-review` 호출 시 sandbox 권한 거부·trust 프롬프트 0건 |

### 사용자 응답 처리

- **Install (Recommended)**: 자동 설치 후 다음 항목 점검
- **Skip**: 해당 항목 비활성화하고 다음 항목으로 — Riff는 보강 기능 없이 기본 흐름만 사용
- **Skip all**: 일괄 비활성화, 더 이상 묻지 않음 (`_workspace/.riff-bootstrap-skip-all` 마킹 — 위 가드가 이 파일도 체크함)

설치 후 `_workspace/.riff-bootstrap-done`에 timestamps + 활성화된 의존성 목록 기록.

### Codex sandbox 권장 설정 (자동 적용 상세)

목적: 첫 다운로드한 사용자가 수동 설정 없이도 `/codex:review`·`/codex:adversarial-review`가 sandbox 권한 거부·trust 프롬프트 없이 즉시 실행되도록 한다.

**점검 순서:**
1. `~/.codex/config.toml` 존재 여부 — 없으면 생성
2. 다음 3개 키 누락 여부를 grep으로 점검:
   - `^sandbox_mode\s*=`
   - `^approval_policy\s*=`
   - 현재 프로젝트 trust 등록: `[projects."<cwd>"]` 섹션 안에 `trust_level\s*=\s*"trusted"`
3. 누락된 항목만 사용자에게 보여주고 동의받기 — 이미 설정된 항목은 그대로 둔다 (사용자 선택 존중)

**자동 추가할 내용:**

```toml
# riff bootstrap이 추가 — 작업 디렉토리 외부 쓰기 차단, 권한 거부 시만 사용자 확인
sandbox_mode = "workspace-write"
approval_policy = "on-failure"

# riff bootstrap이 추가 — <cwd> 프로젝트 trust 등록 (매번 trust 묻지 않음)
[projects."<현재 프로젝트 절대 경로>"]
trust_level = "trusted"
```

**안전 장치:**
- 변경 전 `cp ~/.codex/config.toml ~/.codex/config.toml.bak.$(date +%s)` 으로 timestamp 백업 — 사용자가 원복 가능
- `append`만, 기존 값 `replace` 금지. 이미 다른 값이 설정되어 있으면 (예: `sandbox_mode = "read-only"`) 사용자 의도이므로 그대로 둠
- 추가하는 라인 앞에 `# riff bootstrap (YYYY-MM-DD)` 주석 — 어디서 왔는지 추적 가능
- 사용자 응답 처리는 위 "사용자 응답 처리" 정책과 동일 (Install / Skip / Skip all)

**왜 이 값들인가:**
- `workspace-write`: Codex CLI의 3가지 모드(`read-only`/`workspace-write`/`danger-full-access`) 중 작업 디렉토리만 쓰기 허용. `read-only`로는 `/codex:rescue` 등 수정 도구가 동작 못 함, `danger-full-access`는 위험.
- `on-failure`: 매번 확인 묻는 `untrusted`/`on-request`는 자동화 흐름 끊김. `never`는 실패 가시성 없음.
- 프로젝트별 `trust_level = "trusted"`: 전역 trust가 아니라 현재 프로젝트만 — 다른 프로젝트는 영향 없음.

---

## 보강 통합 (의존성이 활성화돼 있을 때만 적용)

### EXPLORE — Codex 분신
대립 토론 패턴에서 트레이드오프가 명확하지 않을 때, 분신 중 하나로 Codex 투입:
`/codex:adversarial-review --wait <focus>` — 결정 1회만, 자동 호출 X.

### VERIFY tier 0~3 — Codex cross-check
각 tier 통과 후 변경 규모/위험도가 임계 이상(대형 리팩토링·아키텍처·보안·DB 마이그레이션)이면:
`/codex:review --wait --scope working-tree` — Codex 의견을 LEARN 입력으로 흘림.

### VERIFY 실패 — ralph-loop 자동 루프
VERIFY 실패 시 즉시 다음 호출:
`/ralph-loop:ralph-loop "<failure context + 수정 지시>" --max-iterations 3 --completion-promise 'VERIFY_PASSED'`
통과 시 `<promise>VERIFY_PASSED</promise>` 출력 후 LEARN 단계 진입. 3회 초과 시 되감기 패턴.

### Codex/GPT 모델 정책
**모든 Codex 호출에 `--model` 플래그를 명시하지 않는다.** Codex CLI 기본값이 그 시점의 최신 모델이며 자동 업데이트된다. 사용자가 명시 요청하면 그때만 `--model <name>` 사용.

---

## 핵심 원칙

- 한 번에 잘 만들지 않는다. 빠르게 많이 시도한다.
- 매 Riff마다 작동하는 결과물이 존재한다.
- 질문은 트레이드오프가 있을 때만.
- 실패는 비용이 아니라 학습이다.
- AI 시간으로 사고한다.

---

## 디렉토리 정책

```
프로젝트루트/
├── _workspace/                  ← git 추적, 이번 프로젝트 산출물
│   ├── riff-status.md
│   ├── riff-log.md
│   ├── contracts/               ← 8종 계약서 + ui-stack
│   │   ├── README.md
│   │   └── *.md
│   └── riff-N/                 ← Riff별 결과물
│       └── {agent}-result.md
└── .riff/                      ← 학습 메모리 + 세션 상태
    ├── memory/
    │   ├── antibodies/          ← git 추적 (팀 공유)
    │   └── profile.md           ← git 미추적 (개인)
    ├── riff-log.json           ← 훅 출력
    └── state.json               ← 세션 상태 (미추적)
```

`.gitignore` 필수: `.riff/memory/profile.md`, `.riff/state.json`

---

## Riff 0: 프로젝트 부팅

1. `riff-interview` 있으면 5-Layer 인터뷰. 없으면 핵심 질문 2개:
   - "이 프로젝트가 해결하는 문제는?"
   - "성공하면 어떤 모습인가?"
2. 산출물 생성. UI 있으면 `_workspace/contracts/ui-stack.md` 확정 (`references/ui-stack-guide.md`).
3. `_workspace/` 초기화, `riff-log.md` + `riff-status.md` 생성 (`references/riff-status-schema.md`).

산출물:
```
_workspace/
  riff-log.md
  riff-0/
    problem.md / personas.md / journeys.md / success-criteria.md / question-budget.md
  contracts/
    README.md / ui-stack.md
```

---

## 세션 재개 프로토콜

새 세션 시작 시:
1. `_workspace/riff-status.md` 존재 확인.
2. 있으면 "현재 위치"에서 즉시 재개. 자동화 체크리스트 미체크 항목 실행.
3. `.riff/memory/profile.md` 있으면 로드.
4. 없으면 Riff 0부터.

---

## Riff 사이클: ASK → EXPLORE → BUILD → VERIFY → LEARN

### 1. ASK

`riff-interview` 있으면 호출. 없으면 트레이드오프가 있는 결정만 질문.
질문 예산 임계값 이상의 확신도면 건너뜀.

**질문 예산 레벨**

| 레벨 | 임계값 |
|------|------|
| A | 신호 8개 중 8개 |
| B | 신호 8개 중 6개 이상 |
| C | 신호 8개 중 4개 이상 |
| D | 질문 안 함 |

**확신도 신호 (8개 체크)**

상향:
- [ ] 같은 패턴이 이전 Riff에서 검증됨
- [ ] 요구사항이 명시적으로 기술됨 (문서 또는 사용자 발화)
- [ ] 유사 도메인 경험 또는 표준 패턴 존재
- [ ] 성공 기준이 측정 가능한 형태

하향(체크 = 신호 부족):
- [ ] 요구사항 모호하지 않음
- [ ] 같은 영역에서 이전 되감기 없음
- [ ] 외부 시스템 의존도 낮음
- [ ] 트레이드오프 분석 완료

체크된 항목 수가 임계값 이상이면 ASK 건너뜀.

> 점수 합산 방식에서 체크리스트로 변경한 이유: LLM이 가중치 합산을 일관되게 수행하지 못해 재현성 ↓.

---

### 2. EXPLORE

세부: `references/explore-protocol.md`

- 방법 2개 이상 + 트레이드오프 불명확 시 분신술. 명확하면 건너뜀.
- EXPLORE 에이전트도 병렬 3개 제한 포함. BUILD와 합산 최대 3.
- 결과 저장: `_workspace/riff-N/explore-{방향}-result.md`
- 종합본: `explore-synthesis.md` — BUILD가 이 파일을 읽고 시작.
- 최대 3회 후에도 미결 시 사용자 판단 요청.

---

### 3. BUILD

세부: `references/build-protocol.md`

1. **PLAN** — 에이전트 스폰 전, 기존 `_workspace/contracts/README.md` 확인 후 공유 타입(A)·상수(B)·의존성(C)·병렬분업(D) 목록화.
2. **CONTRACT** — A/B/C/D 항목 있으면 계약서 먼저 작성. **계약서 lint 통과 필수** (`riff-contracts/references/contract-lint.md`). 계약서 없이 에이전트 스폰 금지.
3. **EXECUTE** — 계약서 확정 후 에이전트 스폰. 프롬프트에 계약서 경로 + 관련 항체 체크리스트 포함.

> 계약서는 Riff 번호 무관 `_workspace/contracts/` 단일 경로.
>
> CONTRACT → EXECUTE → CONTRACT 복귀 루프 3회 시 사용자 개입 요청.

---

### 4. VERIFY

`riff-qa` 있으면 Tier 0~3 순서로 실행. 없으면 빌드 통과 + 회귀 없음만 확인.

| Tier | 이름 | 내용 |
|------|------|------|
| 0 | 계약 커버리지 + lint | 계약서 lint frontmatter 확인, 공유 타입 누락 탐지 |
| 1 | 정적 경계면 | API shape, 깨진 링크, 상태 전이 |
| 2 | 빌드/타입 | tsc / dart analyze / build |
| 3 | Live Browser | Playwright 유저 저니 |

실패 시 즉시 수정 후 재실행. 3회 실패 시 되감기 (`references/convergence.md`).

---

### 5. LEARN

`riff-memory` 있으면 호출 — 항체 + 프로파일 한번에 처리.
없으면 `_workspace/riff-log.md`에 수동 기록:

```markdown
## Riff N — [날짜]
### 발견한 것 / 결정한 것 / 남은 것 / 확신도 [0-100%]
```

`riff-status.md`의 성공 기준 진행도 갱신. **세션 분리 전 riff-memory 저장 완료 확인 의무**.

---

## 토큰 절약 규칙 (필수)

1. **파일 통신**: 에이전트 결과는 `_workspace/riff-N/{agent}-result.md` 저장. 대화 반환 금지.
2. **세션 분리**: 3~5 Riff마다 `.riff/state.json` 저장 후 분리. memory 저장 후.
3. **병렬 제한**: EXPLORE + BUILD 합산 최대 3개 동시 스폰.
4. **컨텍스트 경고**: 도구 호출 20회 초과 또는 같은 파일 3회 반복 시 분리 제안.

---

## 모듈 연동

| 모듈 | 단계 | 효과 |
|------|------|------|
| `riff-interview` | ASK | 5-Layer 인터뷰 |
| `riff-contracts` | BUILD-CONTRACT | 8종 계약서 + lint |
| `riff-qa` | VERIFY | Tier 0~3 |
| `riff-memory` | LEARN | 항체(7종) + 프로파일 |

---

## AI-Native 패턴

| 패턴 | 적용 시점 | 프로토콜 |
|------|----------|---------|
| 분신술 | EXPLORE 방향 2개 이상 | `references/explore-protocol.md` |
| 되감기 | VERIFY 3회 실패 | `references/rewind-protocol.md` |
| 점진적 확신 | EXPLORE 후 확신도 낮을 때 | `references/convergence.md` |
| 루프 엔지니어링 | 매 VERIFY·되감기·자동화 등급 결정 | `references/loop-engineering.md` |

대립 토론·시간 여행·미래 시뮬레이션은 README 비전이며 별도 프로토콜 미정의 — 필요 시 분신술/되감기로 대체.

## 루프 엔지니어링 (자율 루프 안전장치)

Riff를 감독 없이도 안전하게 도는 자율 루프로 만든다. 핵심만(상세 `references/loop-engineering.md`):

- **상태는 디스크, 컨텍스트는 작게.** 각 Riff는 신선한 컨텍스트로 시작, 필요한 파일만 읽는다.
- **완료는 결정적으로.** "됐다"는 모델이 아니라 기계가 확정한다 — VERIFY는 종료 코드, 프로젝트는 수렴식+사용자 승인.
- **다차원 예산.** 수정 3회·도구 20회·같은 명령 3회·같은 파일 4회 중 하나라도 소진되면 멈춘다(정체/폭주 방어).
- **불가침 기준.** 테스트·계약서·success-criteria를 고쳐서 통과시키지 않는다(reward hacking 방어). 매 Riff에 재주입.
- **자동화 등급은 사용자가 고른다.** L2 반자동(기본) ↔ L3 AFK(결정적 acceptance가 있을 때만).

---

## 웹앱 fast-path

이번 Riff가 신규 웹앱이고 `riff-interview` 미설치 시:
1. 도메인 기본값 = `web-development`
2. 핵심 12문항만 진행 (Layer 1~5에서 도메인 미분기 질문만)
3. 인터뷰 완료 후 `_workspace/contracts/ui-stack.md` 확정
4. Riff 1부터 표준 사이클

---

## OMC 공존

OMC 활성 시 Riff 사이클 중 OMC 모드·에이전트·스킬을 호출하지 않는다.
