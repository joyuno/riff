---
name: pulse
description: "신규 프로젝트·앱·MVP를 처음부터 만드는 AI-Native 루프. ASK → EXPLORE → BUILD → VERIFY → LEARN을 빠르게 반복하며 매 사이클마다 작동하는 결과물을 만든다. 'pulse로 시작', '프로젝트 시작', '새 프로젝트', '앱 만들어줘', 'MVP', '프로토타입', '이거 만들어줘' 시 사용. 단순 버그 수정·작은 기능 추가에는 사용하지 않는다."
---

# Pulse — AI-Native Project Loop

## 핵심 원칙

- 한 번에 잘 만들지 않는다. 빠르게 많이 시도한다.
- 매 Pulse마다 작동하는 결과물이 존재한다.
- 질문은 트레이드오프가 있을 때만.
- 실패는 비용이 아니라 학습이다.
- AI 시간으로 사고한다.

---

## 디렉토리 정책

```
프로젝트루트/
├── _workspace/                  ← git 추적, 이번 프로젝트 산출물
│   ├── pulse-status.md
│   ├── pulse-log.md
│   ├── contracts/               ← 8종 계약서 + ui-stack
│   │   ├── README.md
│   │   └── *.md
│   └── pulse-N/                 ← Pulse별 결과물
│       └── {agent}-result.md
└── .pulse/                      ← 학습 메모리 + 세션 상태
    ├── memory/
    │   ├── antibodies/          ← git 추적 (팀 공유)
    │   └── profile.md           ← git 미추적 (개인)
    ├── pulse-log.json           ← 훅 출력
    └── state.json               ← 세션 상태 (미추적)
```

`.gitignore` 필수: `.pulse/memory/profile.md`, `.pulse/state.json`

---

## Pulse 0: 프로젝트 부팅

1. `pulse-interview` 있으면 5-Layer 인터뷰. 없으면 핵심 질문 2개:
   - "이 프로젝트가 해결하는 문제는?"
   - "성공하면 어떤 모습인가?"
2. 산출물 생성. UI 있으면 `_workspace/contracts/ui-stack.md` 확정 (`references/ui-stack-guide.md`).
3. `_workspace/` 초기화, `pulse-log.md` + `pulse-status.md` 생성 (`references/pulse-status-schema.md`).

산출물:
```
_workspace/
  pulse-log.md
  pulse-0/
    problem.md / personas.md / journeys.md / success-criteria.md / question-budget.md
  contracts/
    README.md / ui-stack.md
```

---

## 세션 재개 프로토콜

새 세션 시작 시:
1. `_workspace/pulse-status.md` 존재 확인.
2. 있으면 "현재 위치"에서 즉시 재개. 자동화 체크리스트 미체크 항목 실행.
3. `.pulse/memory/profile.md` 있으면 로드.
4. 없으면 Pulse 0부터.

---

## Pulse 사이클: ASK → EXPLORE → BUILD → VERIFY → LEARN

### 1. ASK

`pulse-interview` 있으면 호출. 없으면 트레이드오프가 있는 결정만 질문.
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
- [ ] 같은 패턴이 이전 Pulse에서 검증됨
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
- 결과 저장: `_workspace/pulse-N/explore-{방향}-result.md`
- 종합본: `explore-synthesis.md` — BUILD가 이 파일을 읽고 시작.
- 최대 3회 후에도 미결 시 사용자 판단 요청.

---

### 3. BUILD

세부: `references/build-protocol.md`

1. **PLAN** — 에이전트 스폰 전, 기존 `_workspace/contracts/README.md` 확인 후 공유 타입(A)·상수(B)·의존성(C)·병렬분업(D) 목록화.
2. **CONTRACT** — A/B/C/D 항목 있으면 계약서 먼저 작성. **계약서 lint 통과 필수** (`pulse-contracts/references/contract-lint.md`). 계약서 없이 에이전트 스폰 금지.
3. **EXECUTE** — 계약서 확정 후 에이전트 스폰. 프롬프트에 계약서 경로 + 관련 항체 체크리스트 포함.

> 계약서는 Pulse 번호 무관 `_workspace/contracts/` 단일 경로.
>
> CONTRACT → EXECUTE → CONTRACT 복귀 루프 3회 시 사용자 개입 요청.

---

### 4. VERIFY

`pulse-qa` 있으면 Tier 0~3 순서로 실행. 없으면 빌드 통과 + 회귀 없음만 확인.

| Tier | 이름 | 내용 |
|------|------|------|
| 0 | 계약 커버리지 + lint | 계약서 lint frontmatter 확인, 공유 타입 누락 탐지 |
| 1 | 정적 경계면 | API shape, 깨진 링크, 상태 전이 |
| 2 | 빌드/타입 | tsc / dart analyze / build |
| 3 | Live Browser | Playwright 유저 저니 |

실패 시 즉시 수정 후 재실행. 3회 실패 시 되감기 (`references/convergence.md`).

---

### 5. LEARN

`pulse-memory` 있으면 호출 — 항체 + 프로파일 한번에 처리.
없으면 `_workspace/pulse-log.md`에 수동 기록:

```markdown
## Pulse N — [날짜]
### 발견한 것 / 결정한 것 / 남은 것 / 확신도 [0-100%]
```

`pulse-status.md`의 성공 기준 진행도 갱신. **세션 분리 전 pulse-memory 저장 완료 확인 의무**.

---

## 토큰 절약 규칙 (필수)

1. **파일 통신**: 에이전트 결과는 `_workspace/pulse-N/{agent}-result.md` 저장. 대화 반환 금지.
2. **세션 분리**: 3~5 Pulse마다 `.pulse/state.json` 저장 후 분리. memory 저장 후.
3. **병렬 제한**: EXPLORE + BUILD 합산 최대 3개 동시 스폰.
4. **컨텍스트 경고**: 도구 호출 20회 초과 또는 같은 파일 3회 반복 시 분리 제안.

---

## 모듈 연동

| 모듈 | 단계 | 효과 |
|------|------|------|
| `pulse-interview` | ASK | 5-Layer 인터뷰 |
| `pulse-contracts` | BUILD-CONTRACT | 8종 계약서 + lint |
| `pulse-qa` | VERIFY | Tier 0~3 |
| `pulse-memory` | LEARN | 항체(6종) + 프로파일 |

---

## AI-Native 패턴

| 패턴 | 적용 시점 | 프로토콜 |
|------|----------|---------|
| 분신술 | EXPLORE 방향 2개 이상 | `references/explore-protocol.md` |
| 되감기 | VERIFY 3회 실패 | `references/rewind-protocol.md` |
| 점진적 확신 | EXPLORE 후 확신도 낮을 때 | `references/convergence.md` |

대립 토론·시간 여행·미래 시뮬레이션은 README 비전이며 별도 프로토콜 미정의 — 필요 시 분신술/되감기로 대체.

---

## 웹앱 fast-path

이번 Pulse가 신규 웹앱이고 `pulse-interview` 미설치 시:
1. 도메인 기본값 = `web-development`
2. 핵심 12문항만 진행 (Layer 1~5에서 도메인 미분기 질문만)
3. 인터뷰 완료 후 `_workspace/contracts/ui-stack.md` 확정
4. Pulse 1부터 표준 사이클

---

## OMC 공존

OMC 활성 시 Pulse 사이클 중 OMC 모드·에이전트·스킬을 호출하지 않는다.
