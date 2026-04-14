---
name: pulse
description: "AI-Native 프로젝트 루프. 프로젝트를 시작하거나, 기능을 만들거나, 앱/서비스를 만들 때 사용. 'pulse로 시작', '프로젝트 시작', '앱 만들어줘', '이거 만들어줘', 'MVP', '프로토타입', '처음부터', '새 프로젝트', '만들어줘', '구현해줘', '개발해줘' 등의 요청에 반드시 이 스킬을 사용할 것. 기존 프로젝트의 기능 추가, 리팩토링, 버그 수정에도 사용."
---

# Pulse — AI-Native Project Loop

## 핵심 원칙

- 한 번에 잘 만들지 않는다. 빠르게 많이 시도한다.
- 매 Pulse마다 작동하는 결과물이 존재한다.
- 질문은 트레이드오프가 있을 때만 한다.
- 실패는 비용이 아니라 학습이다.
- AI 시간으로 사고한다 (인간 기준 일정 적용 안 함).

---

## Pulse 0: 프로젝트 부팅

1. `pulse-interview` 있으면 5-Layer 인터뷰 실행. 없으면 핵심 질문 2개:
   - "이 프로젝트가 해결하는 문제는?"
   - "성공하면 어떤 모습인가?"
2. 산출물 생성. UI 있으면 `_workspace/contracts/ui-stack.md` 확정 (`references/ui-stack-guide.md` 참조).
3. `_workspace/` 초기화, `pulse-log.md` 생성.

**산출물:**
```
_workspace/
  pulse-log.md
  pulse-0/
    problem.md / personas.md / journeys.md / success-criteria.md / question-budget.md
  contracts/
    README.md       ← 전체 계약서 목록 (Pulse 통합 관리)
    ui-stack.md     ← UI 있는 프로젝트만
```

---

## Pulse 사이클: ASK → EXPLORE → BUILD → VERIFY → LEARN

### 1. ASK

- `pulse-interview` 있으면 호출. 없으면 트레이드오프가 있는 결정만 질문.
- 확신도가 질문 예산 임계값 이상이면 건너뜀.

| 레벨 | 이름 | 질문 임계값 |
|------|------|------------|
| A | 매 단계 확인 | 확신 < 99% |
| B | 핵심만 | 확신 < 80% |
| C | 최소한 | 확신 < 60% |
| D | 전자동 | 질문 안 함 |

**확신도 계산 기준 (행동 기반):**

| 확신도 상향 조건 | +점수 |
|----------------|-------|
| 같은 패턴이 이전 Pulse에서 이미 검증됨 | +20 |
| 요구사항이 명시적으로 기술됨 (문서, 사용자 발화) | +20 |
| 유사 도메인 경험 또는 표준 패턴 존재 | +15 |
| 성공 기준이 측정 가능한 형태로 정의됨 | +15 |

| 확신도 하향 조건 | -점수 |
|----------------|-------|
| 요구사항이 모호하거나 상충됨 | -20 |
| 이전에 유사 Pulse에서 되감기가 발생한 이력 | -20 |
| 외부 시스템 의존도가 높음 (미확인 API 등) | -15 |
| 트레이드오프 분석 미완료 | -10 |

시작 확신도: 50%. 상향/하향 조건을 합산해 최종값 결정. 결과가 임계값 이상이면 ASK 건너뜀.

---

### 2. EXPLORE

- 방법이 2개 이상이고 트레이드오프 불명확 시 분신술 패턴 적용. 명확하면 건너뜀.
- **EXPLORE 에이전트도 병렬 3개 제한에 포함된다.** BUILD와 합산 최대 3개.
- 탐색 결과는 파일로 저장. 최대 3회 탐색 후에도 미결 시 사용자에게 판단 요청.

---

### 3. BUILD

세부 절차: `references/build-protocol.md` 참조. 요약:

1. **PLAN** — 에이전트 스폰 전, 기존 `_workspace/contracts/README.md` 확인 후 공유 타입(A)·상수(B)·의존성(C)·병렬분업(D) 목록화.
2. **CONTRACT** — A/B/C/D 항목 있으면 `_workspace/contracts/`에 계약서 먼저 작성. 계약서 없이 에이전트 스폰 금지. 병렬 에이전트 시 Architecture Contract 필수.
3. **EXECUTE** — 계약서 확정 후 에이전트 스폰. 각 에이전트 프롬프트에 계약서 경로 포함.

> **계약서는 Pulse 번호 무관하게 `_workspace/contracts/` 단일 경로에 저장한다.**

---

### 4. VERIFY

`pulse-qa` 있으면 아래 Tier 순서로 실행. 없으면 빌드 통과 + 회귀 없음만 확인.

| Tier | 이름 | 내용 |
|------|------|------|
| 0 | 계약 커버리지 스캔 | 공유 타입·상수·의존성 계약서 누락 탐지 |
| 1 | 정적 경계면 분석 | API shape 불일치, 깨진 링크, 상태 전이 오류 |
| 2 | 빌드/타입 검증 | tsc / dart analyze / build |
| 3 | Live Browser QA | Playwright 유저 저니 시나리오 실행 |

실패 시 즉시 수정 후 재실행. 3회 실패 시 되감기 패턴 적용 (`references/convergence.md` 참조).

---

### 5. LEARN

- `pulse-dna` 있으면 먼저 실행 후 세션 분리. (세션 분리 전에 반드시 DNA 저장)
- `pulse-immunity` 있으면 실패 패턴을 항체로 기록.
- 없으면 `_workspace/pulse-log.md`에 기록:

```markdown
## Pulse N — [날짜]
### 발견한 것 / 결정한 것 / 남은 것 / 확신도 [0-100%]
```

---

## 토큰 절약 규칙 (필수)

1. **파일 통신**: 에이전트 결과는 `_workspace/pulse-N/{agent}-result.md` 저장. 대화 반환 금지.
2. **세션 분리**: 3~5 Pulse마다 `.pulse/state.json` 저장 후 세션 종료. DNA 저장 후 분리.
3. **병렬 제한**: EXPLORE + BUILD 합산 최대 3개 동시 스폰.
4. **컨텍스트 경고**: 도구 호출 20회 초과 또는 같은 파일 3회 반복 시 세션 분리 제안.

---

## 모듈 연동

| 모듈 | 단계 | 효과 |
|------|------|------|
| `pulse-interview` | ASK | 5-Layer 인터뷰 |
| `pulse-contracts` | BUILD | 계약서 생성 강화 |
| `pulse-qa` | VERIFY | Tier 0~3 QA |
| `pulse-immunity` | LEARN | 항체 기록 |
| `pulse-dna` | LEARN | 사용자 프로파일 |

---

## AI-Native 패턴

| 패턴 | 적용 시점 |
|------|----------|
| 분신술 | EXPLORE, 방향 2개 이상 (3개 제한 내) |
| 대립 토론 | 중요 아키텍처 결정 시 |
| 되감기 | VERIFY 3회 실패 또는 방향 오류 감지 시 |
| 미래 시뮬레이션 | 설계 결정 전 |
| 점진적 확신 | EXPLORE 후 확신도 낮을 때 (최대 3회) |

---

## OMC 공존

OMC 활성 시 Pulse 사이클 중 OMC 모드·에이전트·스킬을 호출하지 않는다.
