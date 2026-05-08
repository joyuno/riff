---
name: riff-qa
description: "4단계 QA 시스템(Tier 0~3): 계약서 lint → 정적 경계면 → 빌드/타입 → Live Browser. Riff의 VERIFY 단계에서 호출. 유령 사용자·파괴자·시간축·다중 인격 변형 포함. '테스트', 'QA', '검증', '확인해줘', '동작하는지', '버그 찾아', '품질 검사' 시 사용."
---

# riff-qa — 4단계 QA 시스템 (Tier 0~3)

## 개요

비용 효율 최우선 원칙. 앞 Tier에서 잡을 수 있는 버그는 반드시 앞에서 잡고, Playwright는 정적 분석·빌드로 잡을 수 없는 런타임 버그에만 투입.

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
| 3 | Live Browser | 높음 (Playwright) | 렌더링, 비동기 타이밍, UX, 보안, 접근성 |

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

### 흐름

```
개발 서버 시작 (백그라운드)
   → health check
   → Playwright 브라우저 열기
   → 유저 저니 시나리오 실행
   → 스크린샷 / 콘솔 / 네트워크 수집
   → 서버 종료
   → QA 보고서 생성
```

### 유저 저니 → Playwright 시나리오 변환

`riff-interview`의 `journeys.md` 또는 `master-plan.md`를 변환:

| 저니 문장 | Playwright |
|----------|-----------|
| "사용자가 [페이지]에 접근" | `await page.goto('[URL]')` |
| "[필드]에 [값] 입력" | `await page.fill('[selector]', '[값]')` |
| "[버튼] 클릭" | `await page.click('[selector]')` |
| "[텍스트] 보임" | `await expect(page.locator('text=[텍스트]')).toBeVisible()` |
| "[페이지]로 이동" | `await expect(page).toHaveURL('[URL]')` |

selector 우선순위: `data-testid` > `getByRole(role, name)` > `getByText`.

시나리오 저장: `_workspace/riff-N/playwright-scenarios.md`

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
