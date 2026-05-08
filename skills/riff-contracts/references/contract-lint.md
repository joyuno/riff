# Contract Lint: 계약서 작성 직후 self-check

이 파일은 BUILD-CONTRACT 단계에서 계약서를 작성한 직후, 그리고 VERIFY Tier 0에서 재확인 시에만 읽는다.
SKILL.md에 포함하지 않는다.

---

## 사용 방법

각 계약서를 저장하기 전에 해당 유형의 체크리스트를 통과해야 한다.
체크리스트 중 단 하나라도 누락되면 계약서를 다시 작성한다.
3회 반복 실패 시 사용자에게 보고한다 (`riff-contracts` SKILL.md 복귀 루프 가드 참조).

체크 통과 후 `_workspace/contracts/{이름}.md` 상단에 다음 메타를 추가한다:

```yaml
---
type: type | behavior | visual | performance | security | constants | dependency | architecture
linted: YYYY-MM-DD
---
```

`linted` 필드 없는 계약서는 Tier 0에서 자동 차단된다.

---

## Type Contract — 체크리스트

- [ ] 모든 엔드포인트에 `Method`, `Path`, `Request Body`, `Response Body`, `Status Codes` 4컬럼이 채워져 있다.
- [ ] 성공 응답 shape에 `data` 래핑 규칙이 명시되어 있다 (단일/목록/204 케이스 구분).
- [ ] 에러 응답 shape이 정의되어 있다 (`{ error: { code, message } }` 또는 명시된 다른 형태).
- [ ] 에러 코드 목록이 별도 표로 존재하고, 적어도 400/401/404/500이 포함되어 있다.
- [ ] 네이밍 컨벤션이 한 줄로 명시되어 있다 (camelCase / snake_case 중 하나로 일관).
- [ ] 옵셔널 필드의 부재 시 처리(키 생략 vs `null`) 규칙이 명시되어 있다.
- [ ] 날짜/시간 필드가 있다면 형식(ISO 8601)과 타임존(UTC) 명시.
- [ ] 페이지네이션 필드가 있다면 기본 크기, 최대 크기, 시작 페이지 번호 명시.
- [ ] 이 계약서를 소비할 에이전트(프론트/모바일 등) 1개 이상 명시.

**자주 빠뜨리는 것**: 에러 응답 shape, 빈 배열 vs `null` 구분, 204 No Content의 응답 body 부재 명시.

---

## Behavior Contract — 체크리스트

- [ ] 모든 상태가 enum 형태로 나열되어 있다.
- [ ] 허용된 전이가 표(from → to)로 정의되어 있다.
- [ ] **금지된 전이**가 명시적으로 적혀 있다 (없으면 모든 전이가 허용된다고 잘못 해석됨).
- [ ] 종단(terminal) 상태가 무엇인지 표시되어 있다 (예: COMPLETED, CANCELLED).
- [ ] 종단 상태에서의 전이 시도 처리(차단 vs 무시 vs 에러)가 명시.
- [ ] 각 전이의 트리거(이벤트 이름 또는 API 호출)가 적혀 있다.
- [ ] 동시 요청 충돌 처리(낙관적 락 / 비관적 락 / 무시)가 명시.
- [ ] 에러 상태(FAILED, REJECTED 등)에서의 복구 경로 또는 데드엔드 명시.

**자주 빠뜨리는 것**: 종단 상태 가드, 동시성 정책, 실패 상태로의 전이.

---

## Visual Contract — 체크리스트

- [ ] 컴포넌트별 상태가 7가지 모두 다뤄졌다: `default`, `hover`, `active`, `disabled`, `loading`, `success`, `error`.
- [ ] empty state(데이터 없음)와 error state가 구분되어 정의되어 있다.
- [ ] 반응형 브레이크포인트의 단위(px/rem)와 경계값이 명시되어 있다.
- [ ] 색상 토큰이 hex 또는 토큰 이름으로 명시 (RGB 변환 규칙 명확).
- [ ] 타이포그래피 토큰 단위(rem/px)가 통일.
- [ ] 애니메이션이 있다면 `duration` + `easing` 함께 명시.
- [ ] 다크 모드 지원 여부 명시 (지원하면 토큰 매핑까지).

**자주 빠뜨리는 것**: empty state, error state, 반응형 단위 통일성.

---

## Performance Contract — 체크리스트

- [ ] 응답 시간 목표가 P50/P95/P99 중 최소 2개 명시되고 단위(ms)가 적혀 있다.
- [ ] 측정 조건이 명시되어 있다 (예: "DB 캐시 hit 상태", "데이터 1만 건 기준").
- [ ] DB 쿼리 횟수 상한이 엔드포인트별로 정의되어 있다.
- [ ] 번들 크기 예산이 페이지 단위로 명시되어 있다 (gzip 기준 명시).
- [ ] 캐시 TTL이 있다면 단위(초) 함께 명시.
- [ ] SLA 위반 시 동작(에러 / degrade / 그대로 통과)이 정의되어 있다.

**자주 빠뜨리는 것**: 단위 명시, 측정 조건, SLA 위반 시 정책.

---

## Security Contract — 체크리스트

- [ ] 인증(AuthN)과 인가(AuthZ)가 분리되어 정의되어 있다.
- [ ] 엔드포인트별 인증 요구사항 표가 있다 (public / authenticated / admin).
- [ ] 역할별 권한 매트릭스가 정의되어 있다 (역할 × 리소스 × 액션).
- [ ] 토큰 정책: access 만료 시간 + refresh 만료 시간 + 갱신 흐름 모두 명시.
- [ ] 입력 검증 규칙이 있다면 Constants Contract와 cross-reference (값을 여기서 다시 적지 않음).
- [ ] CORS 정책 (허용 origin, 메서드, credentials 포함 여부) 명시.
- [ ] 민감 필드 로그 금지 목록 명시 (비밀번호, 토큰, 주민번호 등).
- [ ] 에러 응답이 리소스 존재 여부를 노출하지 않는지 정책 명시 (404 vs 403 통일).

**자주 빠뜨리는 것**: refresh token 정책, 인증/인가 분리, 404/403 구분 정책.

---

## Constants Contract — 체크리스트

- [ ] 모든 수치 상수에 단위가 명시되어 있다 (초/분/시간/byte/문자 등).
- [ ] bound가 있는 값은 포함/미포함이 명시 (예: `MIN_LENGTH: 8 (포함)`).
- [ ] 같은 이름의 상수가 두 번 정의되지 않는다 (single source of truth).
- [ ] 환경변수 키 이름은 대문자 + 언더스코어 통일.
- [ ] 환경변수 값의 출처(SSOT)가 명시 (예: `docker-compose.yml`의 environment 섹션).
- [ ] 정규표현식이 있다면 테스트 가능한 예시 입력/출력 1쌍 이상 포함.
- [ ] 에러 코드/메시지 매핑이 있다면 코드와 문구가 1:1 대응.

**자주 빠뜨리는 것**: 단위 누락(분 vs 초 혼용), bound 포함/미포함 모호, 같은 상수 다른 값 정의.

---

## Dependency Contract — 체크리스트

- [ ] 모든 핵심 라이브러리가 **고정 버전**으로 적혀 있다 (`^`, `~`, `>=` 등 범위 지정 금지).
- [ ] 런타임 버전(node/python/dart 등)이 명시되어 있다.
- [ ] 알려진 호환성 주의사항(예: bcrypt 4.1+ 비호환)이 별도 섹션에 정리.
- [ ] 잠금 파일(`package-lock.json`/`requirements.txt`/`pubspec.lock`/`go.sum`)이 있는 위치 명시.
- [ ] peer dependency 충돌 가능성이 있는 조합은 명시적으로 검증되어 있다.
- [ ] 환경변수 키 + 출처가 표로 정리되어 있다 (Constants Contract와 중복되지 않게).

**자주 빠뜨리는 것**: 버전 범위 표기, 잠금 파일 위치, 호환성 메모.

---

## Architecture Contract — 체크리스트

- [ ] 모든 API 엔드포인트가 표(Path × Method × 소유 에이전트 × 상태)로 정리되어 있다.
- [ ] 같은 (Path + Method) 조합이 두 에이전트에 할당되어 있지 않다.
- [ ] 모듈/디렉토리 소유권이 표로 정리되어 있다 (디렉토리 × 소유 × 다른 에이전트 권한).
- [ ] `src/shared/` 같은 공유 영역의 수정 정책이 명시(orchestrator 승인 필요 등).
- [ ] 기술 결정이 "확정/검토 중" 상태로 표시되어 있다.
- [ ] 금지된 대안이 명시되어 있다 (예: "세션 방식 금지", "Redux 금지").
- [ ] 에이전트 간 협의 인터페이스 요약 1줄씩 (예: "frontend는 backend가 만든 OpenAPI 스키마를 소비").

**자주 빠뜨리는 것**: 같은 path 중복 할당, 공유 영역 수정 정책, 금지 대안 명시.

---

## Cross-Contract 검증 (8종을 모두 작성한 뒤 마지막에 1회 실행)

이 검증은 단일 계약서가 아닌 계약서들 사이의 일관성을 본다.

- [ ] **Constants ↔ Security**: 보안 입력 검증에서 참조하는 길이/형식이 Constants Contract와 동일한 키를 가리킨다.
- [ ] **Constants ↔ Dependency**: 환경변수 키가 두 계약에서 같은 출처를 가리킨다.
- [ ] **Type ↔ Architecture**: Type Contract의 엔드포인트 path가 Architecture Contract의 소유권 표에 모두 등장한다.
- [ ] **Type ↔ Behavior**: Behavior Contract의 상태 전이를 트리거하는 API가 Type Contract에 정의되어 있다.
- [ ] **Visual ↔ Behavior**: Behavior Contract의 상태(loading/error 등)가 Visual Contract의 컴포넌트 상태로 매핑된다.
- [ ] **Performance ↔ Type**: Performance Contract의 응답 시간 SLA가 Type Contract의 모든 엔드포인트를 커버한다.
- [ ] **Security ↔ Type**: Type Contract의 모든 엔드포인트가 Security Contract의 인증 요구사항 표에 등장한다.

cross-contract 위반은 단일 계약서 위반보다 위험도가 높다 (누락이 명백하지 않기 때문). 발견 시 즉시 BUILD-CONTRACT로 복귀.

---

## Lint 통과 의무

- 계약서 파일 상단에 `linted: YYYY-MM-DD` frontmatter 없으면 Tier 0이 차단한다.
- `linted` 날짜가 마지막 수정일보다 이전이면 재린트 필요(파일 변경 후 재검증 안 됐다는 신호).
