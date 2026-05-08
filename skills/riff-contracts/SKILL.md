---
name: riff-contracts
description: "에이전트 간 경계면 계약 시스템. 전체 코드가 아닌 계약서만 교환해 컨텍스트 ~94% 절약. 8종 계약서(type/behavior/visual/performance/security/constants/dependency/architecture) 생성·lint·cross-validation. Riff의 BUILD-CONTRACT 단계에서 호출. '계약', 'contract', '인터페이스', 'API 정의', '경계면' 시 사용."
---

# riff-contracts: 인터페이스 계약 시스템

## 핵심 가치

에이전트 A가 백엔드 API를 구현했고 에이전트 B가 그것에 맞춰 프론트엔드를 만든다.
- 나쁜 방법: A의 500줄 코드 전체를 B의 컨텍스트에 넣는다.
- 좋은 방법: A가 30줄 계약서를 내보내고 B는 계약서만 읽는다.

계약서는 "무엇이 오가는지"만 명시한다. "어떻게 만들었는지"는 담지 않는다.

평균 절약: 코드 500줄 → 계약서 30줄 (~94%).

---

## 8종 계약서

| # | 유형 | 용도 | 템플릿 | 주된 QA Tier |
|---|------|------|--------|------------|
| 1 | `type` | API/데이터 shape | `references/type.template.md` | Tier 1 |
| 2 | `behavior` | 상태 전이·플로우 | `references/behavior.template.md` | Tier 3 |
| 3 | `visual` | UI 상태·디자인 토큰 | `references/visual.template.md` | Tier 3 |
| 4 | `performance` | SLA·예산 | `references/performance.template.md` | Tier 3 |
| 5 | `security` | 인증/인가/입력 | `references/security.template.md` | Tier 3 |
| 6 | `constants` | 공유 상수 SSOT | `references/constants.template.md` | Tier 0 |
| 7 | `dependency` | 라이브러리 버전 핀 | `references/dependency.template.md` | Tier 0 |
| 8 | `architecture` | 병렬 에이전트 소유권 | `references/architecture.template.md` | Tier 0 + 1 |

각 유형 작성 시점·자동 감지 신호·예시는 해당 템플릿 파일 참조.

---

## 계약서 작성 → lint → 사용 흐름

```
BUILD-PLAN (공유 대상 식별)
   ↓
BUILD-CONTRACT
   ├─ 1. 계약서 작성 (해당 템플릿 사용)
   ├─ 2. self-lint (references/contract-lint.md)
   │    └─ 실패 시 다시 작성 (3회 가드 → 사용자 보고)
   ├─ 3. cross-contract 검증 (8종 다 작성한 뒤 1회)
   └─ 4. linted: YYYY-MM-DD frontmatter 추가
   ↓
BUILD-EXECUTE (에이전트 스폰)
   ↓
VERIFY Tier 0 (계약서 frontmatter + 코드 정합성 재확인)
```

> linted 없는 계약서는 Tier 0이 자동 차단.
> mtime > linted 날짜면 재린트 필요.

---

## Lint (self-check)

상세 체크리스트: `references/contract-lint.md`

작성 직후 에이전트가 직접 실행. 8종 각각의 체크리스트를 100% 통과해야 lint 메타 추가 허용.

자주 빠뜨리는 실수 카탈로그(시드 항체): `references/contract-mistakes.md` (CM-001 ~ CM-020)

이 두 파일은 `riff-memory`의 `contract` 타입 항체와 cross-reference된다 — 같은 실수가 2회 이상 발생하면 항체로 누적되어 다음 BUILD-CONTRACT 시 자동 주입.

### 복귀 루프 가드

CONTRACT → lint 실패 → 재작성 사이클이 같은 계약서에 대해 3회 반복되면:
1. 사용자에게 "이 계약서가 반복 실패 — 템플릿 자체 문제일 수 있음" 보고
2. 사용자 개입 또는 계약서 보류 후 다음 단계로

---

## Cross-Contract 검증

8종을 모두 작성한 뒤 마지막에 1회. 상세: `references/contract-lint.md` 마지막 섹션.

핵심 매트릭스:
- Constants ↔ Security: 입력 검증이 같은 키 가리키는가
- Type ↔ Architecture: 모든 엔드포인트가 소유권 표에 있는가
- Type ↔ Behavior: 상태 전이를 트리거하는 API가 정의됐는가
- Visual ↔ Behavior: 상태(loading/error)가 컴포넌트에 매핑되는가
- Performance ↔ Type: SLA가 모든 엔드포인트 커버하는가
- Security ↔ Type: 모든 엔드포인트가 인증 요구 표에 있는가

cross 위반은 단일 위반보다 위험도 높음 (누락이 명백하지 않음).

---

## 내보내기 / 가져오기 프로토콜

### 내보내기 (생산자 에이전트 A)

```
1. 구현한 경계면 유형 파악
2. 해당 템플릿 선택
3. 최소 필수 항목만 작성
4. self-lint → linted frontmatter 추가
5. _workspace/contracts/{이름}-{유형}.md 저장
6. _workspace/contracts/README.md 갱신
7. 계약서 경로를 다음 에이전트에 전달
```

### 가져오기 (소비자 에이전트 B)

```
1. _workspace/contracts/README.md에서 관련 계약서 식별
2. 필요한 계약서만 읽기 (전체 코드 아님)
3. 계약서 기반 구현
4. 계약서와 충돌 발견 시 → 오케스트레이터 보고 (임의 변경 금지)
```

### 충돌 처리

에이전트가 계약서와 다른 결과를 발견하면:
- 임의로 계약서 수정 ❌
- 구현을 계약서에 맞게 조정 ✅
- 계약서 자체가 잘못이면 오케스트레이터 보고

---

## 디렉토리 구조

```
_workspace/contracts/
├── README.md                    ← 전체 목록 (Riff 통합)
├── ui-stack.md                  ← UI 스택 (Riff 0)
├── {이름}-type.md
├── {이름}-behavior.md
├── {이름}-visual.md
├── {이름}-performance.md
├── {이름}-security.md
├── {이름}-constants.md
├── {이름}-dependency.md
└── architecture.md              ← 병렬 에이전트 소유권 맵
```

> 계약서는 Riff 번호 무관, 단일 경로. 생성 Riff는 README.md에만 기록.

### README 형식

```markdown
| 계약서 | 유형 | 생성 Riff | 소비자 | linted | 상태 |
|--------|------|----------|--------|--------|------|
| auth-type.md | type | 1 | frontend, backend | 2026-05-04 | 활성 |
| auth-constants.md | constants | 1 | frontend, backend | 2026-05-04 | 활성 |
```

---

## pre-BUILD 공유 타입 스캔

BUILD-CONTRACT 진입 전 오케스트레이터 실행:

**기존 코드베이스가 있을 때**
1. 이번 Riff 수정·생성 파일 목록 확정
2. import 문과 생성자 파라미터 읽기
3. "다른 파일에서 정의되고 이 파일에서 소비되는 타입" 추출
4. 추출된 타입마다 계약서 1개

**신규 파일을 여러 개 만들 때**
1. 파일별 역할 정의 (화면 A, 위젯 B, 서비스 C)
2. 역할 간 데이터 흐름 화살표로 정리
3. 화살표 위 데이터 구조마다 계약서 1개

스택별 탐지 명령: `references/stack-patterns.md`

---

## 자동 감지 신호 (요약)

각 유형 상세 신호 + 예시 코드는 해당 템플릿 파일 참조.

| 유형 | 감지 신호 핵심 |
|------|--------------|
| `type` | `fetch/axios/prisma`, `interface/type` 정의, REST 엔드포인트 |
| `behavior` | `status/state/phase` 변수, 다단계 폼/위저드 |
| `visual` | UI 컴포넌트, `disabled/loading/error` 상태 |
| `performance` | 복잡한 DB 쿼리, 대용량, 번들 사이즈 |
| `security` | 인증 미들웨어, role/permission, 민감 데이터 |
| `constants` | 같은 수치가 2개 이상 파일에 등장, `MAX_/MIN_/EXPIRE_` 패턴 |
| `dependency` | `requirements.txt`/`package.json`/`pubspec.yaml` 중 2+ 동시 작성 |
| `architecture` | 병렬 에이전트 2개 이상 스폰 시 항상 |

---

## 운영 원칙

1. **최소성**: 경계면 정보만. 구현 힌트 ❌
2. **불변성**: 합의된 계약서는 임의 변경 ❌
3. **명시성**: 모든 규칙은 계약서에 명문화
4. **단방향성**: 생산자 → 소비자
5. **버전 없음**: 변경 시 기존 파일 update (히스토리는 git)
6. **lint 의무**: linted frontmatter 없으면 BUILD ❌
7. **3회 가드**: 같은 계약서 lint 3회 실패 시 사용자 개입

---

## 참조 파일

| 파일 | 역할 |
|------|------|
| `references/contract-lint.md` | 8종 self-check + cross-contract 검증 |
| `references/contract-mistakes.md` | CM-001~020 실수 카탈로그(항체 시드) |
| `references/stack-patterns.md` | 스택별 탐지/검증 명령 |
| `references/{유형}.template.md` | 8종 각 템플릿 |
