# Contract Mistakes: 자주 발생하는 계약서 작성 실수 카탈로그

이 파일은 `riff-memory`의 `contract` 타입 항체 시드 카탈로그다.
새 계약서 작성 직전 또는 lint 실패 시 참조한다.

각 실수는 항체 형식과 1:1 대응되도록 작성됐다 — 재발 시 `riff-memory`가 동일 ID로 항체 강화한다.

---

## CM-001: 에러 응답 shape 누락 (Type)

**증상**
프론트엔드가 API를 호출하다 에러를 만나면 `error.code`나 `error.message`를 읽으려다 런타임 에러 (`undefined`).

**원인**
Type Contract에 성공 응답만 정의하고 에러 응답 형태를 빠뜨림. 에이전트가 "에러는 status code로 충분하지" 가정.

**예방**
- 모든 Type Contract에 `ErrorResponse` 인터페이스 별도 정의 필수.
- 에러 코드 목록 표 누락 시 lint 차단.

---

## CM-002: 빈 배열과 null의 불일치 (Type)

**증상**
백엔드는 결과 없을 때 `null`을 반환하는데, 프론트엔드는 빈 배열 `[]`을 기대 → `.map is not a function`.

**원인**
계약서에 부재 시 표현(`null` vs `[]`)을 명시하지 않아 양쪽 에이전트가 다르게 해석.

**예방**
- 목록 응답의 부재 표현을 계약서에 명시 ("결과 없을 때 빈 배열").
- 옵셔널 필드 처리 규칙(키 생략 vs `null`)도 동일하게 명시.

---

## CM-003: snake_case ↔ camelCase 혼용 (Type)

**증상**
백엔드는 `created_at`을 반환하는데 프론트는 `createdAt`을 읽으려다 `undefined`.

**원인**
계약서에 네이밍 컨벤션이 명시되지 않거나, 한 계약서 안에서 두 스타일이 섞여 있음.

**예방**
- 계약서 상단에 컨벤션 한 줄 명시 ("응답 body: camelCase, DB 필드는 노출하지 않음").
- DB 직렬화 책임(어느 레이어가 변환하는지) 명시.

---

## CM-004: 종단 상태 가드 누락 (Behavior)

**증상**
주문이 `COMPLETED` 상태에서 `CANCELLED`로 전이되어 데이터 정합성 깨짐.

**원인**
계약서에 "허용된 전이"만 적고 "금지된 전이" 또는 "종단 상태"를 표시하지 않음.

**예방**
- Behavior Contract에 종단 상태 명시 + 종단에서의 전이 시도 처리(차단/무시/에러) 규칙 필수.
- lint 차단 항목.

---

## CM-005: 동시 요청 정책 누락 (Behavior)

**증상**
두 사용자가 동시에 같은 리소스를 수정 → race condition으로 last-write-wins 의도치 않은 동작.

**원인**
상태 전이를 단일 사용자 관점으로만 작성. 동시성 정책(낙관적 락 / 비관적 락 / 무시) 미명시.

**예방**
- Behavior Contract 작성 시 "동시 요청 충돌 처리" 섹션 필수.
- 충돌 시 반환할 status code(409 등)도 함께 명시.

---

## CM-006: empty/error 상태 누락 (Visual)

**증상**
사용자가 데이터 없는 페이지에서 빈 화면을 봄. 에러 발생 시 깜빡거리고 끝.

**원인**
Visual Contract에 default/hover/active만 적고 loading/empty/error 상태를 빠뜨림.

**예방**
- Visual Contract 7가지 상태 모두 다루는 것이 lint 통과 조건.
- empty와 error는 별도 상태로 구분 (메시지/CTA가 다름).

---

## CM-007: 반응형 단위 혼용 (Visual)

**증상**
브라우저 글꼴 크기 변경 시 일부 영역만 깨짐.

**원인**
계약서에 px와 rem이 섞여 있어 에이전트별로 다른 단위로 구현.

**예방**
- 디자인 토큰 단위를 계약서 상단에 한 번만 선언 ("모든 spacing은 rem, breakpoint는 px").

---

## CM-008: 응답시간 단위 누락 (Performance)

**증상**
"응답시간 200" → 200ms로 구현했는데 200초가 SLA였음 (또는 그 반대).

**원인**
Performance Contract에 단위가 없음.

**예방**
- 모든 시간 값에 명시적 단위 필수 (`200ms`, `30s`).
- lint 차단 항목.

---

## CM-009: 측정 조건 누락 (Performance)

**증상**
로컬에서는 P95 100ms 달성했는데 프로덕션에서 800ms.

**원인**
"P95 100ms"라는 목표만 적고 측정 환경(데이터 규모, 캐시 상태, 동시 요청 수)을 안 적음.

**예방**
- 모든 SLA 옆에 측정 조건 명시 ("데이터 1만 건, 캐시 cold, 단일 요청").

---

## CM-010: 인증 vs 인가 혼용 (Security)

**증상**
로그인한 사용자가 다른 사용자의 데이터를 ID만 알면 조회/수정 가능.

**원인**
Security Contract에 "로그인 필요"만 적고 "리소스 소유권 검증"을 별도로 적지 않음.

**예방**
- 인증(AuthN)과 인가(AuthZ)를 별도 섹션으로 분리.
- 권한 매트릭스(역할 × 리소스 × 액션) 표 필수.

---

## CM-011: refresh token 정책 불완전 (Security)

**증상**
사용자가 30분마다 강제 로그아웃되거나 refresh token이 영구 유효해 보안 문제.

**원인**
access token 만료만 적고 refresh token 만료/회전(rotation) 정책을 빠뜨림.

**예방**
- access + refresh 양쪽 만료 시간 명시.
- refresh 회전(rotation) 여부 명시.
- 로그아웃 시 토큰 무효화 정책 명시.

---

## CM-012: 404 vs 403 노출 정책 부재 (Security)

**증상**
공격자가 "404가 오면 리소스 없음, 403이 오면 리소스 있음 + 권한 없음" 추론으로 데이터 존재 여부 enum.

**원인**
계약서에 권한 없는 사용자에게 어떤 응답을 줄지 통일 정책이 없음.

**예방**
- "권한 없는 리소스는 항상 404로 응답" 같은 명시적 정책.

---

## CM-013: 상수 단위 모호 (Constants)

**증상**
프론트는 `EXPIRE: 30`을 분으로 해석, 백엔드는 초로 해석 → 토큰 만료 시점 불일치.

**원인**
숫자만 적고 단위를 빠뜨림.

**예방**
- 모든 수치 상수에 단위 필수 (`30 (분)`, `30000 (ms)`).
- 변수명에 단위 포함 권장 (`EXPIRE_MINUTES`).

---

## CM-014: 같은 상수 두 번 정의 (Constants)

**증상**
한 계약서에 `MAX_LENGTH: 100`, 다른 계약서에 `NAME_MAX: 80` — 어느 게 맞는지 모름.

**원인**
SSOT(single source of truth) 원칙 미준수.

**예방**
- Constants Contract는 정확히 1개. 다른 계약서는 참조만 (`Constants Contract의 NAME_MAX 사용`).
- cross-contract lint 항목.

---

## CM-015: 버전 범위 표기 (Dependency)

**증상**
한 에이전트는 `lodash@4.17.21`, 다른 에이전트는 `lodash@4.17.30`으로 설치 → 미묘한 동작 차이.

**원인**
계약서에 `^4.17.0`처럼 범위로 적어 에이전트마다 다른 버전 선택.

**예방**
- 버전은 항상 정확한 핀(`4.17.21`).
- `^`, `~`, `>=` 발견 시 lint 차단.

---

## CM-016: 잠금 파일 미반영 (Dependency)

**증상**
계약서는 `bcrypt: 4.0.1`인데 `package-lock.json`은 `4.1.2`. 에이전트가 잠금 파일대로 설치.

**원인**
계약서 변경 시 잠금 파일 재생성을 잊음.

**예방**
- Tier 0에서 계약서 ↔ 잠금 파일 자동 비교.
- 잠금 파일 위치를 계약서에 명시.

---

## CM-017: 같은 path 중복 할당 (Architecture)

**증상**
`POST /api/users`를 두 에이전트가 각자 구현 → 라우터 충돌 또는 무작위 우선순위.

**원인**
Architecture Contract의 엔드포인트 표에서 같은 (path + method)가 두 에이전트에 할당됨.

**예방**
- 작성 직후 cross-row 검사 (같은 row 반복 검출).
- lint 차단 항목.

---

## CM-018: 공유 디렉토리 정책 부재 (Architecture)

**증상**
`src/shared/`를 두 에이전트가 동시 수정해 git 충돌.

**원인**
Architecture Contract에 공유 영역의 수정 정책(orchestrator 승인 / 락 / 사전 협의)이 없음.

**예방**
- 공유 디렉토리는 별도 행에 "수정 정책" 컬럼으로 명시.
- 기본은 "orchestrator 승인 필요".

---

## CM-019: 금지된 대안 미명시 (Architecture)

**증상**
"인증을 JWT로 한다"고 적었지만, 한 에이전트가 세션 방식으로 우회 구현.

**원인**
"확정"만 적고 "금지된 대안"을 빠뜨림.

**예방**
- Architecture Contract에 `금지` 섹션 별도 (예: "세션 방식 금지", "Redux 금지").

---

## CM-020: linted frontmatter 누락 (Meta)

**증상**
계약서가 lint 안 거치고 BUILD에 사용됨 → 위 실수들 중 하나 재발.

**원인**
작성 후 lint 단계 건너뜀.

**예방**
- Tier 0이 `linted: YYYY-MM-DD` frontmatter 없는 계약서를 자동 차단.
- 파일 mtime이 `linted` 날짜보다 늦으면 재린트 필요.

---

## 항체 강화 정책

같은 ID의 실수가 2회 이상 발생하면 `riff-memory`가 다음을 수행:

1. `.riff/memory/antibodies/contract-{ID}.md`의 `recurrence` +1
2. 해당 항체의 예방 체크리스트를 lint 파일에 자동 반영(우선순위 ↑)
3. 다음 BUILD-CONTRACT 단계에서 해당 항체를 강제 주입

3회 이상 재발 시 사용자에게 "이 실수가 반복되고 있다 — 계약서 템플릿 자체를 갱신할까요?" 보고.
