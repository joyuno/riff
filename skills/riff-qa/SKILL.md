---
name: riff-qa
description: "4단계 QA 시스템(Tier 0~3): 계약서 lint → 정적 경계면 → 빌드/타입 → Live Browser. Riff의 VERIFY 단계에서 호출. 유령 사용자·파괴자·시간축·다중 인격 변형 포함. '테스트', 'QA', '검증', '확인해줘', '동작하는지', '버그 찾아', '품질 검사' 시 사용."
---

# riff-qa — 4단계 QA 시스템 (Tier 0~3)

## 개요

비용 효율 최우선 원칙. 앞 Tier에서 잡을 수 있는 버그는 반드시 앞에서 잡고, 브라우저(riff-browse, 외부 MCP 불필요)는 정적 분석·빌드로 잡을 수 없는 런타임 버그에만 투입.

```
Tier 0 (계약서 lint + 커버리지)
    ↓ 통과
Tier 1 (정적 경계면 분석)
    ↓ 통과
Tier 2 (빌드/타입 검증)
    ↓ 통과
Tier 3 (Live Browser)
```

> README와 본문 모두 `Tier 0~3` 4단계로 통일. 이전 "3-Tier QA" 표현은 deprecated.

---

## Tier 요약

| Tier | 이름 | 비용 | 발견 가능 버그 |
|------|------|------|------------|
| 0 | 계약서 lint + 커버리지 | 최소 (Grep/parse) | linted 누락, 공유 타입 계약 누락, 상수/버전 불일치 |
| 1 | 정적 경계면 | 매우 낮음 (Grep/AST) | API shape, 깨진 링크, 상태 전이, DB↔API↔UI 체인 |
| 2 | 빌드/타입 | 낮음 (tsc/lint/build) | 타입 에러, 린트 위반, 번들 실패 |
| 3 | Live Browser | 높음 (riff-browse) | 렌더링, 비동기 타이밍, UX, 보안, 접근성 |

앞 Tier 통과 없이 다음 Tier로 진행 금지.

---

## Tier 0: 계약서 lint + 커버리지 스캔

> BUILD-CONTRACT 직후, VERIFY 시작 시 두 번 실행.

### 실행

1. **lint frontmatter 검증**: `_workspace/contracts/*.md` 모두에 `linted: YYYY-MM-DD` 존재 확인. 없으면 차단.
2. **mtime > linted 검증**: 계약서 파일이 수정됐는데 재린트 안 됐으면 차단.
3. **공유 타입 커버리지**: 이번 Riff의 import/생성자 파라미터 ↔ 계약서 README.md 비교. 누락 시 BUILD-CONTRACT 복귀.
4. **상수 정합성**: Constants Contract 값 ↔ 코드 하드코딩 비교. 불일치 시 코드 수정.
5. **의존성 정합성**: Dependency Contract 핀 ↔ 잠금 파일 비교.

스택별 탐지 명령: `riff-contracts/references/stack-patterns.md`

### 통과 조건

- 모든 계약서에 유효한 `linted` frontmatter
- 공유 타입 전부에 계약서 존재
- Constants/Dependency Contract와 코드/잠금 파일 일치

### 복귀 루프 가드 (3회)

Tier 0 실패 → BUILD-CONTRACT 복귀 → Tier 0 재실행 사이클이 같은 항목에 대해 3회 반복되면:
1. 사용자 보고 ("계약서 또는 코드 변경이 반복 충돌 — 어느 쪽이 맞나요?")
2. 사용자 결정 후 계속 또는 보류

---

## Tier 1: 정적 경계면 QA

> 상세: `references/tier1-boundary.md`

### 핵심 원칙

경계면의 양쪽을 동시에 읽어 shape 일치 비교. 한쪽만 읽으면 불일치 못 잡음.

### 검증 대상

1. **API 응답 shape ↔ 프론트 훅 타입** — snake/camelCase, 옵셔널 처리
2. **파일 경로 ↔ href / router.push** — 깨진 링크, 404
3. **상태 전이 ↔ 실제 status 업데이트 코드** — Behavior Contract 위반
4. **DB 스키마 ↔ API 응답 ↔ 프론트 타입 체인** — 이름·타입 단절 지점

계약서 기반 검증: riff-contracts가 생성한 계약을 기준점으로 사용.

---

## Tier 2: 빌드/타입 QA

> 상세: `references/tier2-build.md`

### 실행 순서

```bash
npx tsc --noEmit          # 타입 에러
npx eslint src/           # 린트 위반
npm run build             # 번들 빌드
```

Flutter:
```bash
dart analyze
flutter build web
```

### 주요 확인

- TypeScript strict 모드 (strictNullChecks 포함)
- `as any`, `as unknown` 우회 검출
- 빌드 경고를 에러로 처리 (`--strict`)
- unused imports, 미사용 변수

> 빌드 통과 ≠ 정상 동작. 타입이 맞아도 런타임 로직 틀릴 수 있음.

---

## Tier 3: Live Browser QA

> 상세: `references/tier3-live.md`

### 흐름 (gstack `/qa` 모방 — 외부 MCP 없이 경량 러너 `riff-browse.mjs` 사용)

```
개발 서버 시작 (백그라운드)
   → health check (curl)
   → riff-browse 데몬 기동 ($R start)
   → 유저 저니 시나리오 실행 ($R goto/snapshot/click/fill/wait)
   → 스크린샷 / 콘솔 / 네트워크 수집
   → 데몬·서버 종료 ($R stop)
   → QA 보고서 생성 (Health Score 포함)
```

### 유저 저니 → riff-browse 시나리오 변환

`riff-interview`의 `journeys.md` 또는 `master-plan.md`를 변환 (`R="node _workspace/.riff/riff-browse.mjs"`):

| 저니 문장 | riff-browse |
|----------|-----------|
| "사용자가 [페이지]에 접근" | `$R goto <URL>` |
| "요소 탐색" | `$R snapshot -i -o shot.png` → `@eN` 라벨 |
| "[필드]에 [값] 입력" | `$R fill @eN "[값]"` |
| "[버튼] 클릭" | `$R click @eN` |
| "[텍스트] 보임" | `$R wait "[텍스트]"` |
| "API 직접 검증" | `$R js "await fetch('/api/...').then(r=>r.status)"` |

라벨/selector 우선순위: `data-testid` > role+name > text. 상세·러너 설치는 `references/tier3-live.md`.

시나리오 저장: `_workspace/riff-N/scenario.sh`

### 변형

| 변형 | 목적 | 참조 |
|------|------|------|
| 유령 사용자 | AI가 스크린샷 보고 자유 탐색 | `references/ghost-user.md` |
| 파괴자 | 비정상 입력, 보안 취약점 | `references/destroyer.md` |
| 시간축 | 상태 변화 흐름 (시간순 스크린샷) | `references/tier3-live.md` |
| 다중 인격 | 사용자 유형별 시뮬레이션 | `references/tier3-live.md` |

---

## Tier 자동 선택

| 변경 유형 | 실행 Tier | 추가 변형 |
|----------|----------|----------|
| UI 컴포넌트 | 0 + 1 + 2 + 3 | 유령 사용자 |
| API 엔드포인트만 | 0 + 1 + 2 | — |
| 인증/권한 | 0 + 1 + 2 + 3 | 파괴자 |
| DB 스키마 | 0 + 1 + 2 + 3 | 시간축 |
| 전체 | 0 + 1 + 2 + 3 | 다중 인격 |

계약서 변경만 있으면 Tier 0만으로 종결될 수 있음.

---

## VERIFY-FIX 루프 (gstack `/qa` 모방 — 보고로 끝내지 않는다)

riff-qa는 **버그를 보고만 하지 않는다.** gstack `/qa`처럼 발견 → 수정 → 재검증을 닫힌 루프로 돌린다.

```
발견 → 원자적 수정(한 버그=한 커밋) → 회귀 시나리오 첨부 → 재검증 → Health Score before/after
```

### 루프 절차

1. **발견**: Tier에서 버그 1건 확정 (증거: 콘솔/네트워크/스크린샷).
2. **수정**: 해당 버그만 고친다. 한 버그 = 한 커밋. 무관한 코드 건드리지 않는다.
3. **회귀 첨부**: 그 버그를 재현하는 `scenario.sh`의 Step(또는 Tier1/2 검사)을 **회귀 시나리오로 고정**.
   LEARN에서 `riff-memory` 항체에 이 재현 절차를 첨부한다.
4. **재검증**: 같은 Tier를 다시 실행해 PASS 확인. 동시에 앞 Tier 회귀 없음 확인.
5. **점수 갱신**: Health Score를 before → after로 기록.

### 루프 제어 (loop-engineering 준수 — `riff/references/loop-engineering.md`)

VERIFY-FIX는 무한히 돌면 안 된다. 다음 **다차원 예산** 중 하나라도 소진되면 즉시 멈추고 사용자에게 보고:

| 한계 | 임계 | 초과 시 |
|------|------|--------|
| 같은 버그 수정 시도 | 3회 | 되감기(`rewind-protocol.md`) |
| 같은 명령/파일 반복 | 명령 3회·파일 4회 | 정체(stall) 판정 → 접근 전환 |
| 도구 호출 | 누적 20회 | 세션 분리 제안 |
| 콘솔 에러 진동 | 같은 에러 메시지 3회 재출현 | 근본 원인 미해결 → 보고 |

> **수정이 테스트를 통과시키되 요구를 충족 못 하는 "reward hacking" 방지:** 테스트/계약서
> 파일을 수정해서 통과시키지 않는다. 통과 기준(계약서·success-criteria)은 **불가침**이다.
> 검증자는 모델의 "됐다" 주장이 아니라 **종료 코드/스크린샷/콘솔 같은 결정적 증거**만 신뢰한다.

---

## Health Score 루브릭 (gstack 모방)

QA 보고서는 `before X/10 → after Y/10`을 항상 포함한다. 가중 합산:

| 차원 | 가중 | 10점 기준 |
|------|------|----------|
| Console | 15% | 콘솔 에러 0, 경고 최소 |
| Links | 10% | 깨진 링크/404 0 |
| Visual | 15% | 레이아웃 깨짐·반응형 오류 없음 |
| Functional | 25% | 핵심 저니 전부 PASS |
| UX | 10% | 로딩/빈/에러 상태 처리, 피드백 명확 |
| Content | 5% | 오타·깨진 텍스트·플레이스홀더 없음 |
| Performance | 10% | 느린 응답·과대 번들 없음 |
| Accessibility | 10% | 키보드·라벨·대비 기본 충족 |

점수 = Σ(차원 점수 × 가중). **수정 후 재검증에서 점수가 오르지 않으면 그 수정은 무효**로 보고
원인을 다시 추적한다 (점수 정체 = 정체 신호).

---

## QA 보고서 형식

### Step별 결과

| Step | 행동 | 예상 | 실제 | 결과 | 증거 |
|------|------|------|------|------|------|
| 1 | 로그인 페이지 접속 | 폼 표시 | 표시됨 | PASS | screenshot-01.png |
| 2 | 이메일+로그인 | 대시보드 이동 | 500 에러 | FAIL | screenshot-02.png |

### 실패 분석

```
콘솔 에러: [전문]
네트워크: [URL, 상태, body]
원인 추정: [어느 Tier 1 경계면인지]
경계면 유형: [API↔훅 / 경로↔링크 / 상태전이 / DB↔API↔UI]
```

### 전체 요약

```
총 N / 통과 X / 실패 Y / 건너뜀 Z
발견 버그: [...]
권장 수정 우선순위: [...]
```

실패 항목은 LEARN 단계에서 `riff-memory`의 항체로 기록된다.

---

## 실행 체크리스트

```
[ ] Tier 0: 모든 계약서 linted frontmatter 확인
[ ] Tier 0: 공유 타입 커버리지 통과
[ ] Tier 0: Constants/Dependency 정합성 통과
[ ] Tier 1: API shape, 경로/링크, 상태 전이, DB체인 4종 모두 검증
[ ] Tier 2: tsc / dart analyze / build 통과
[ ] Tier 3: 개발 서버 기동, 유저 저니 시나리오 실행
[ ] Tier 3: 스크린샷 증거 수집
[ ] 보고서 작성, LEARN으로 인계
```

---

## 참조 파일

| 파일 | 역할 |
|------|------|
| `riff-contracts/references/stack-patterns.md` | 스택별 Tier 0 탐지/검증 명령 |
| `references/tier1-boundary.md` | 4종 경계면 검증 상세 |
| `references/tier2-build.md` | 빌드/타입 검증 상세 |
| `references/tier3-live.md` | Live Browser 흐름 + 시간축 + 다중 인격 |
| `references/ghost-user.md` | 유령 사용자 변형 |
| `references/destroyer.md` | 파괴자 변형 |
