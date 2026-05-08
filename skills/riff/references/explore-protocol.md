# EXPLORE 단계 프로토콜

이 파일은 EXPLORE 단계 실행 시에만 읽는다. SKILL.md에 포함하지 않는다.

---

## 발동 조건

다음 중 하나 충족 시 EXPLORE 단계 실행:
- 구현 방법이 2개 이상이고 트레이드오프가 불명확
- 같은 문제를 PoC 없이 판단하면 되감기 위험이 높을 때
- 새로운 기술 스택/라이브러리 도입 여부 결정이 필요할 때

명확한 방법이 이미 있으면 건너뜀.
**EXPLORE 에이전트도 BUILD와 합산 병렬 3개 제한에 포함된다.**

---

## 탐색 결과 파일 형식

저장 위치: `_workspace/pulse-N/explore-{방향명}-result.md`

예시: `explore-rest-result.md`, `explore-graphql-result.md`

```markdown
---
direction: [방향명 — 예: rest, graphql, websocket]
pulse: N
explored_at: [날짜]
recommendation: proceed | reject | needs_more
confidence: [0-100%]
---

## 한 줄 요약
[이 방향의 핵심 가치를 한 문장으로]

## 핵심 발견

[이 방향으로 구현했을 때 실제로 어떻게 동작하는지]

## 트레이드오프

| 장점 | 단점 |
|------|------|
| [구체적 장점] | [구체적 단점] |

## 구현 복잡도 예측

- 예상 파일 수: N개
- 주요 의존성: [라이브러리명@버전]
- 위험 요소: [가장 불확실한 부분]

## 샘플 코드 / PoC 결과

[핵심 로직 10~30줄 또는 "PoC 생략 (개념 검증으로 충분)"]

## 추천 결정

`proceed` / `reject` / `needs_more`

이유: [2~3줄]
```

---

## 종합 보고서 형식

모든 방향 탐색이 끝나면 오케스트레이터가 종합 보고서를 작성한다.

저장 위치: `_workspace/pulse-N/explore-synthesis.md`

```markdown
## EXPLORE 종합 — Pulse N

### 탐색한 방향
| 방향 | 추천 | 확신도 | 요약 |
|------|------|--------|------|
| [A] | proceed | 85% | [한 줄] |
| [B] | reject | 20% | [한 줄] |

### 선택 결정

**선택: [방향명]**

이유:
- [결정 근거 1]
- [결정 근거 2]

트레이드오프 수용:
- [포기하는 것]
- [얻는 것]

### BUILD로 전달하는 제약 조건

다음을 Architecture Contract / Type Contract에 반영한다:
- [제약 1 — 예: "GraphQL 스키마는 backend-agent가 단독 소유"]
- [제약 2 — 예: "실시간 기능은 WebSocket, REST 혼용 금지"]

확신도: [0-100%]
질문 예산 임계값 이하면 사용자에게 판단 요청.
```

---

## 탐색 방법별 가이드

### 분신술 패턴 (방향이 2~3개)

```
1. 각 방향마다 에이전트 1개 스폰 (병렬 3개 제한)
2. 각 에이전트: 해당 방향으로 최소 PoC 구현 또는 개념 검증
3. 결과를 explore-{방향명}-result.md에 저장
4. 오케스트레이터: explore-synthesis.md 작성 후 BUILD 진행
```

### 대립 토론 패턴 (중요 아키텍처 결정)

```
1. 찬성 에이전트: 특정 방향의 장점을 최대한 옹호
2. 반대 에이전트: 해당 방향의 약점과 리스크 파고들기
3. 오케스트레이터: 두 관점을 읽고 explore-synthesis.md에 최종 결정 기록
```

### 점진적 확신 패턴 (확신도가 임계값 미달)

```
1차 탐색 → 확신도 측정 → 임계값 미달이면 2차 탐색
최대 3회 탐색 후에도 확신도 미달 → 사용자에게 판단 요청
```

---

## BUILD로의 핸드오프

`explore-synthesis.md`가 존재하면 BUILD 단계에서:

1. PLAN 시 `explore-synthesis.md`의 **"BUILD로 전달하는 제약 조건"** 섹션을 먼저 읽는다.
2. 제약 조건을 Architecture Contract / Dependency Contract에 반영한다.
3. 선택된 방향의 `explore-{방향명}-result.md`를 에이전트 프롬프트에 포함한다.

```
에이전트 프롬프트에 추가:
"탐색 결과: _workspace/pulse-N/explore-{방향명}-result.md 참조.
 이 방향의 트레이드오프를 이미 수용한 상태로 구현하라."
```

`pulse-status.md` 갱신: 현재 위치를 `BUILD > PLAN`으로 이동. explore-synthesis.md 경로를 기록.
