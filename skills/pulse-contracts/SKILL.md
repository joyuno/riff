---
name: pulse-contracts
description: "인터페이스 계약 시스템. 에이전트 간 경계면에서 전체 코드가 아닌 최소 계약서만 교환하여 컨텍스트를 절약. 8종 계약서(type/behavior/visual/performance/security/constants/dependency/architecture) 생성 및 검증. Pulse의 BUILD 단계에서 호출. '계약', 'contract', '인터페이스', '경계면', 'API 정의' 시 사용."
---

# pulse-contracts: 인터페이스 계약 시스템

## 핵심 가치

에이전트 A가 백엔드 API를 구현했다. 에이전트 B는 그 결과물을 받아 프론트엔드를 붙여야 한다.
나쁜 방법: 에이전트 A의 500줄 코드 전체를 에이전트 B의 컨텍스트에 넣는다.
좋은 방법: 에이전트 A가 30줄짜리 계약서를 내보내고, 에이전트 B는 그것만 읽는다.

계약서는 "무엇이 오가는지"만 명시한다. "어떻게 만들었는지"는 담지 않는다.
이것이 에이전트 간 컨텍스트 폭발을 막는 핵심 메커니즘이다.

### 컨텍스트 절약 효과

- 평균 절약: 코드 500줄 → 계약서 30줄 (약 94% 감소)
- 에이전트 B가 알아야 할 것: API shape, 상태 규칙, UI 상태, 성능 제한, 보안 규칙
- 에이전트 B가 알 필요 없는 것: 구현 세부사항, 내부 로직, 최적화 방법

---

## 7종 계약서 유형

### 1. Type Contract (타입 계약)

**용도**: API 경계면에서 오가는 데이터의 shape 정의

**언제 생성**:
- REST API 엔드포인트를 새로 만들 때
- 기존 API의 응답 구조가 바뀔 때
- 프론트엔드-백엔드 경계를 넘는 데이터가 있을 때

**담는 내용**:
- HTTP 메서드, 경로, 요청/응답 body
- 공유 타입 정의 (TypeScript interface 또는 JSON Schema)
- 옵셔널 필드, null/undefined 처리 규칙
- 네이밍 컨벤션 (camelCase vs snake_case)

**템플릿**: `references/type.template.md`

---

### 2. Behavior Contract (행동 계약)

**용도**: 상태 전이 규칙과 비즈니스 로직의 순서 정의

**언제 생성**:
- 사용자 플로우(회원가입, 결제, 온보딩)를 구현할 때
- 상태 머신이 필요한 기능 (주문 상태, 예약 상태)
- 두 에이전트가 같은 플로우의 다른 부분을 맡을 때

**담는 내용**:
- 상태 목록과 허용/금지된 전이
- 각 전이의 조건 (가드)
- 유저 저니 단계 순서
- 에러 상태 처리 규칙

**템플릿**: `references/behavior.template.md`

---

### 3. Visual Contract (시각 계약)

**용도**: UI 컴포넌트 상태와 디자인 시스템 토큰 정의

**언제 생성**:
- 디자이너-개발자 경계를 넘는 컴포넌트 구현 시
- 동일 컴포넌트를 여러 에이전트가 서로 다른 페이지에서 사용할 때
- 반응형 브레이크포인트 규칙이 필요할 때

**담는 내용**:
- 컴포넌트별 상태 (default, hover, active, disabled)
- 반응형 브레이크포인트 (mobile/tablet/desktop)
- 색상, 타이포그래피, 간격 토큰
- 애니메이션 duration/easing

**템플릿**: `references/visual.template.md`

---

### 4. Performance Contract (성능 계약)

**용도**: 응답 시간, 번들 크기, 쿼리 제한 등 성능 SLA 정의

**언제 생성**:
- 성능 요구사항이 명시된 기능
- DB 쿼리가 많은 API 엔드포인트
- 번들 크기 예산이 있는 페이지

**담는 내용**:
- API 응답 시간 제한 (P50, P95, P99)
- 페이지 로드 시간 목표
- 번들 크기 예산
- DB 쿼리 최대 횟수, 캐시 TTL

**템플릿**: `references/performance.template.md`

---

### 5. Security Contract (보안 계약)

**용도**: 인증/인가 규칙, 입력 검증, 데이터 보호 정책 정의

**언제 생성**:
- 인증이 필요한 엔드포인트
- 사용자 권한이 다른 리소스 접근
- 민감한 데이터를 다루는 기능

**담는 내용**:
- 엔드포인트별 인증 요구사항
- 역할별 권한 매트릭스
- 입력 검증 규칙 (최대 길이, 허용 형식)
- CORS 정책, 토큰 만료 시간
- 비밀 정보 처리 규칙 (로그 금지 필드 등)

**템플릿**: `references/security.template.md`

---

### 6. Constants Contract (상수 계약)

**용도**: 검증 규칙·비즈니스 상수처럼 **여러 레이어에서 동일한 값**을 써야 하는 것의 단일 진실 공급원(SSOT)

**언제 생성**:
- 프론트엔드와 백엔드가 같은 검증 규칙을 공유할 때 (최소 길이, 최대 횟수 등)
- 같은 상수가 2개 이상의 파일에 등장할 때
- 환경변수 키 이름이 여러 파일에서 참조될 때

**담는 내용**:
- 입력 검증 상수 (최소/최대 길이, 허용 형식, 정규표현식)
- Rate Limit 수치 (IP당 분당 N회 등)
- 비즈니스 규칙 상수 (만료 시간, 페이지 크기 등)
- 에러 코드/메시지 매핑

**핵심 규칙**: 이 계약서에 정의된 값을 에이전트가 코드 안에서 다시 하드코딩하는 것을 금지한다. 반드시 이 계약서에서 읽어서 사용한다.

**예시**:
```
# auth-constants.md

## 검증 상수
PASSWORD_MIN_LENGTH: 8
PASSWORD_MAX_LENGTH: 128
EMAIL_MAX_LENGTH: 254

## Rate Limit
SIGNUP_RATE_LIMIT: 5회 / IP / 분
LOGIN_RATE_LIMIT: 10회 / IP / 분
RATE_LIMIT_STATUS: 429

## 토큰
ACCESS_TOKEN_EXPIRE_MINUTES: 30
REFRESH_TOKEN_EXPIRE_DAYS: 7
```

**감지 신호**:
- 숫자 리터럴이 2개 이상 파일에서 같은 의미로 반복될 때
- `MAX_`, `MIN_`, `LIMIT_`, `EXPIRE_`, `TIMEOUT_` 패턴의 변수
- 프론트엔드 validation과 백엔드 validator가 동시에 구현될 때

스택별 에러 패턴과 탐지 명령은 `references/stack-patterns.md` 참조.

**템플릿**: `references/constants.template.md`

---

### 7. Dependency Contract (의존성 계약)

**용도**: 에이전트 스폰 전에 사용할 라이브러리와 버전을 확정하여 버전 충돌 방지

**언제 생성**:
- 여러 에이전트가 동일 언어/런타임을 공유할 때 (항상)
- 라이브러리 간 호환성이 중요한 조합이 있을 때 (ORM + DB 드라이버, 암호화 라이브러리 등)
- docker-compose, requirements.txt, package.json이 동시에 존재할 때

**담는 내용**:
- 핵심 라이브러리와 **고정 버전** (범위 지정 금지, 정확한 버전 핀)
- 알려진 호환성 주의사항
- 설정 파일 간 공유되는 환경변수 키와 값의 출처

**핵심 규칙**: 에이전트는 이 계약서에 없는 라이브러리를 임의로 추가할 수 없다. 새 라이브러리가 필요하면 오케스트레이터에게 보고 후 계약서를 먼저 업데이트한다.

**예시**:
```
# dependency-contract.md

## Python 런타임
python: "3.11"

## 핵심 의존성 (버전 고정)
fastapi: "0.111.0"
sqlalchemy: "2.0.30"
passlib[bcrypt]: "1.7.4"       ← bcrypt 직접 설치 금지, passlib 통해서만
bcrypt: "4.0.1"                 ← passlib 1.7.4와 호환되는 버전
psycopg2-binary: "2.9.9"
pydantic: "2.7.1"

## 호환성 주의
# bcrypt 4.1+ 은 passlib 1.7.4와 비호환.
# bcrypt는 반드시 4.0.x 이하를 사용한다.

## 설정값 출처 (SSOT)
# DB 자격증명의 진실 공급원: docker-compose.yml의 environment 섹션
# config.py는 os.getenv()로만 읽고, 값을 직접 정의하지 않는다.
DB_HOST: ${POSTGRES_HOST}
DB_PORT: ${POSTGRES_PORT}
DB_NAME: ${POSTGRES_DB}
DB_USER: ${POSTGRES_USER}
DB_PASSWORD: ${POSTGRES_PASSWORD}
```

**감지 신호**:
- `requirements.txt`, `package.json`, `pubspec.yaml`, `go.mod` 중 2개 이상이 동시 수정될 때
- 암호화 관련 라이브러리 (`bcrypt`, `passlib`, `cryptography`, `jwt`)
- `docker-compose.yml`과 `config.py`(또는 `.env`)가 동시에 등장할 때
- ORM + DB 드라이버 조합

스택별 충돌 에러 패턴과 사전 검증 명령은 `references/stack-patterns.md` 참조.

**템플릿**: `references/dependency.template.md`

### 8. Architecture Contract (아키텍처 계약)

**용도**: 병렬 에이전트 간 API 명세·모듈 소유권·파일 소유권을 사전 확정하여 구현 방식 충돌 방지

**언제 생성**:
- 병렬로 2개 이상의 에이전트가 동시에 스폰될 때 (항상)
- 프론트엔드·백엔드·공통 모듈을 서로 다른 에이전트가 담당할 때
- API 엔드포인트를 한쪽은 만들고 다른 쪽은 소비할 때

**담는 내용**:
- API 엔드포인트 목록 (URL, 메서드, 소유 에이전트)
- 모듈·서비스 소유권 (에이전트별 담당 디렉토리/파일)
- 기술 결정 (선택한 접근법, 금지된 대안)
- 에이전트 간 협의된 인터페이스 요약

**핵심 규칙**:
- 계약서에 명시된 엔드포인트는 에이전트가 임의로 URL이나 메서드를 바꿀 수 없다.
- 모듈 소유권 밖의 파일을 수정하려면 오케스트레이터에게 먼저 보고한다.
- 기술 결정 사항은 계약서에 "확정"으로 표시된 이후 번복 불가.

**예시**:
```
# architecture-contract.md

## API 엔드포인트 소유권
| 엔드포인트 | 메서드 | 소유 에이전트 | 상태 |
|-----------|--------|-------------|------|
| /api/auth/login | POST | backend-agent | 확정 |
| /api/users/{id} | GET | backend-agent | 확정 |
| /api/products | GET | backend-agent | 확정 |

## 모듈 소유권
| 디렉토리 | 소유 에이전트 | 다른 에이전트 접근 |
|---------|-------------|-----------------|
| src/frontend/ | frontend-agent | 읽기 가능, 쓰기 금지 |
| src/backend/ | backend-agent | 읽기 가능, 쓰기 금지 |
| src/shared/ | orchestrator 승인 필요 | 협의 후 수정 |

## 기술 결정 (확정)
- 인증: JWT, Bearer 토큰 방식 (세션 방식 금지)
- API 응답: { data: ..., error: ... } 래핑 통일 (에러 시 null data)
- 상태 관리: Zustand (Redux 금지)
```

**감지 신호**:
- BUILD에서 `에이전트 2개 이상 병렬 스폰` 시 자동 트리거
- 동일 API를 여러 에이전트가 각자 정의할 가능성이 있을 때
- "프론트/백 분리", "기능별 분리" 같은 분업 구조

**템플릿**: `references/architecture.template.md`

---

## 계약서와 QA Tier 매핑

계약서 유형은 Pulse QA 시스템의 검증 강도를 결정한다.

| 계약서 유형 | QA Tier | 이유 |
|------------|---------|------|
| type | Tier 1 (스냅샷) | API shape 변경은 런타임에 즉시 감지됨 |
| behavior | Tier 3 (파괴자) | 상태 전이 오류는 사용자 데이터 손실로 이어짐 |
| visual | Tier 3 (파괴자) | UI 회귀는 사용자 경험 전체에 영향 |
| performance | Tier 3 (파괴자) | 성능 저하는 전체 서비스 품질 하락 |
| security | Tier 3 (파괴자) | 보안 계약 위반은 데이터 유출로 직결 |
| constants | Tier 0 (커버리지 스캔) | 하드코딩 값이 계약서와 다르면 즉시 불일치 |
| dependency | Tier 0 (커버리지 스캔) | 버전 핀이 잠금 파일과 다르면 즉시 충돌 가능성 |
| architecture | Tier 0 (커버리지 스캔) + Tier 1 (정적 분석) | URL·소유권 불일치는 런타임 전에 탐지 가능 |

---

## 내보내기/가져오기 프로토콜

### 내보내기 (에이전트 A → 계약서)

BUILD 단계 완료 후 에이전트는 다음을 수행한다:

```
1. 구현한 경계면 유형 파악 (API? UI? 상태 머신?)
2. 해당 계약서 템플릿 선택
3. 최소 필수 항목만 채워 _workspace/contracts/{모듈명}-{유형}.md 저장
4. 계약서 경로를 다음 에이전트에게 전달
```

### 가져오기 (에이전트 B ← 계약서)

에이전트 B는 전체 코드 대신 계약서만 읽는다:

```
1. _workspace/contracts/ 디렉토리에서 관련 계약서 목록 확인
2. 필요한 계약서 파일만 읽기
3. 계약서 기반으로 구현 시작
4. 계약서와 충돌 발생 시 → 오케스트레이터에게 보고 (임의 변경 금지)
```

### 계약서 충돌 처리

에이전트가 계약서와 다른 결과물을 발견하면:
- 임의로 계약서를 수정하지 않는다
- 구현을 계약서에 맞게 조정한다
- 계약서 자체가 잘못됐다면 오케스트레이터에게 보고한다

---

## pre-BUILD 공유 타입 스캔 프로토콜

BUILD 단계가 시작되기 전에 오케스트레이터는 아래 스캔을 실행한다.
스캔 결과로 공유 타입이 발견되면 계약서를 먼저 작성한다.

### 스캔 방법

**기존 코드베이스가 있을 때:**
```
1. 이번 Pulse에서 수정·생성할 파일 목록을 확정한다.
2. 각 파일의 import 문과 생성자 파라미터를 읽는다.
3. "다른 파일에서 정의되고 이 파일에서 소비되는 타입"을 추출한다.
4. 해당 타입마다 계약서 1개를 작성한다.
```

**신규 파일을 여러 개 만들 때:**
```
1. 파일별 역할을 먼저 정의한다 (화면 A, 위젯 B, 서비스 C...).
2. 역할 간 데이터 흐름을 화살표로 정리한다 (A → B: 어떤 데이터?).
3. 화살표를 건너는 데이터 구조마다 계약서 1개를 작성한다.
```

---

## 자동 감지 가이드라인

코드를 보고 어떤 계약서가 필요한지 추론하는 규칙:

### Type Contract이 필요한 신호

**웹/Node.js:**
- `fetch()`, `axios`, `prisma`, `mongoose` 사용
- `interface`, `type`, `schema` 정의
- REST 엔드포인트 (`router.get`, `app.post`, `@Get`, `@Post`)

**Flutter/Dart:**
- `class ${PascalCase}` 패턴이면서 다른 `.dart` 파일에서 import됨
- 생성자에 `required this.`, `required` 파라미터가 있는 데이터 클래스
- `fromJson`, `toJson`, `copyWith` 메서드가 있는 모델 클래스
- `List<${PascalCase}>`, `Map<String, ${PascalCase}>` 타입 사용

### Behavior Contract이 필요한 신호
- 상태 변수 (`status`, `state`, `phase`, `step`)
- 조건부 전이 (`if status === 'pending' then ...`)
- 다단계 폼, 위저드, 온보딩 플로우
- **Flutter:** `StatefulWidget` + `setState`, `Provider`, `Riverpod`, `Bloc` 상태 전이

### Visual Contract이 필요한 신호

**웹/React:**
- UI 컴포넌트 (`Button`, `Modal`, `Card`, `Form`)
- CSS 변수, 디자인 토큰
- `disabled`, `loading`, `error`, `success` 상태

**Flutter/Dart:**
- `Widget`을 반환하는 커스텀 클래스 (특히 `StatelessWidget`, `StatefulWidget`)
- 생성자에 외부에서 전달받는 데이터 파라미터가 있을 때
- `final` 필드가 2개 이상인 데이터 표시용 위젯
- 예: `class PersonalityToggle extends StatelessWidget { final PersonalityTraitData data; }`

### Performance Contract이 필요한 신호
- 복잡한 DB 쿼리 (JOIN, 집계)
- 대용량 데이터 처리
- 번들 크기에 영향을 주는 라이브러리 추가

### Security Contract이 필요한 신호
- 인증 미들웨어 (`authenticate`, `requireAuth`, `@UseGuards`)
- 사용자 권한 체크 (`role`, `permission`, `canAccess`)
- 민감한 데이터 (비밀번호, 토큰, 개인정보)

---

## _workspace/contracts/ 디렉토리 구조

```
_workspace/
└── contracts/
    ├── README.md               ← 전체 계약서 목록 (Pulse 통합, 단일 경로)
    ├── ui-stack.md             ← UI 스택 계약 (Pulse 0에서 생성)
    ├── {계약명}-type.md        ← Type Contract
    ├── {계약명}-behavior.md    ← Behavior Contract
    ├── {계약명}-visual.md      ← Visual Contract
    ├── {계약명}-performance.md ← Performance Contract
    ├── {계약명}-security.md    ← Security Contract
    ├── {계약명}-constants.md    ← Constants Contract
    ├── {계약명}-dependency.md  ← Dependency Contract
    └── architecture.md         ← Architecture Contract (병렬 에이전트 소유권 맵)
```

> **계약서는 Pulse 번호 무관하게 `_workspace/contracts/` 단일 경로에 저장한다.**
> Pulse N에서 생성한 계약서도 `_workspace/contracts/`에 저장하며, `README.md`에 생성 Pulse를 기록한다.

### README.md 형식

```markdown
# 계약서 목록

| 계약서 | 유형 | 생성 Pulse | 소비자 | 상태 |
|--------|------|-----------|--------|------|
| auth-type.md | type | 1 | frontend, backend | 활성 |
| auth-constants.md | constants | 1 | frontend, backend | 활성 |
| checkout-behavior.md | behavior | 2 | backend | 활성 |
```

---

## 운영 원칙

1. **최소성**: 계약서는 경계면 정보만 담는다. 구현 힌트는 담지 않는다.
2. **불변성**: 한번 합의된 계약서는 에이전트가 임의 변경하지 않는다.
3. **명시성**: 암묵적 약속은 없다. 모든 규칙은 계약서에 적힌다.
4. **단방향성**: 계약서는 생산자 → 소비자 방향으로만 흐른다.
5. **버전 없음**: 계약서 변경 시 새 파일 생성이 아닌 기존 파일 업데이트 (히스토리는 git이 관리).
