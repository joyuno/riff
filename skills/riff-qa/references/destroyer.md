# 파괴자 QA — 상세 가이드

파괴자(Destroyer)는 비정상 입력, 경계값, 보안 취약점을 의도적으로 테스트하는 QA 변형이다.
일반 사용자가 하지 않을 행동을 통해 방어 코드의 존재 여부를 확인한다.
인증/권한 로직 변경, 사용자 입력이 있는 폼, 결제/금융 기능이 있을 때 반드시 실행한다.

---

## 비정상 입력 패턴 목록

### 1. 빈 입력

```
테스트: 모든 필수 필드를 비워두고 폼 제출
예상 정상 동작:
  - 클라이언트 사이드 유효성 검사로 차단
  - "필수 항목입니다" 등 명확한 에러 메시지 표시
  - API 요청이 전송되지 않음 (또는 API가 400 반환)

riff-browse 실행 ($R = node _workspace/.riff/riff-browse.mjs):
  $R snapshot -i             → 폼 요소 @eN 확인
  $R click @eN               → 빈 상태로 제출
  $R console --errors
  $R network --errors        → API 호출/4xx 5xx 여부 확인
  $R screenshot dest-01.png

실패 판정:
  - 빈 값이 API로 전송되어 500 에러 발생
  - 에러 메시지 없이 페이지 새로고침
  - DB에 빈 레코드 삽입됨
```

### 2. 초장문 입력

```
테스트: 10,000자 문자열 입력 후 제출
입력값: "A".repeat(10000)

예상 정상 동작:
  - 입력 필드에 maxlength 제한
  - 또는 API에서 길이 초과 시 400/422 반환
  - 에러 메시지: "최대 XXX자까지 입력 가능합니다"

실패 판정:
  - 서버가 10,000자 그대로 DB에 저장
  - 저장 후 UI 레이아웃이 깨짐
  - 500 에러 또는 타임아웃 발생
```

### 3. 특수문자 및 이모지

```
테스트 입력값:
  특수문자: !@#$%^&*()[]{}|<>?,./\`~
  이모지: 🎉🔥💀👾🌈
  줄바꿈: "첫째줄\n둘째줄\n셋째줄"
  탭: "열1\t열2\t열3"
  null 바이트: "\x00"

예상 정상 동작:
  - 허용된 특수문자만 저장
  - 이모지 정상 저장 및 표시 (UTF-8 처리)
  - 줄바꿈이 의도한 방식으로 처리 (nl2br 또는 무시)

실패 판정:
  - 이모지 입력 시 인코딩 에러
  - 특수문자로 레이아웃 깨짐
  - null 바이트로 문자열 잘림
```

### 4. SQL 인젝션

```
테스트 입력값 (예시 패턴):
  '; DROP TABLE users; --
  ' OR '1'='1
  1; SELECT * FROM users WHERE 1=1; --

예상 정상 동작:
  - ORM 사용 시 자동으로 이스케이프 처리 (Prisma, Sequelize 등)
  - 원시 SQL 사용 시 파라미터 바인딩으로 처리
  - 입력값이 문자열 그대로 저장되거나 유효성 에러 반환

실패 판정 (심각도: CRITICAL):
  - SQL 에러가 클라이언트에 노출됨
  - 비정상적인 데이터 반환
  - DB 구조 정보 노출

심각도: CRITICAL — 발견 즉시 개발팀 에스컬레이션
```

### 5. XSS (크로스 사이트 스크립팅)

```
테스트 입력값 (예시 패턴):
  스크립트 태그 삽입 시도
  이미지 onerror 핸들러 삽입 시도
  SVG onload 이벤트 삽입 시도
  javascript: 프로토콜 링크 삽입 시도

예상 정상 동작:
  - HTML 이스케이프 처리 후 저장 및 표시
  - React의 경우 JSX 텍스트 렌더링 시 자동 이스케이프
  - 입력값이 화면에 텍스트로만 표시됨 (스크립트 미실행)
  - innerHTML 직접 조작 코드가 없어야 함

riff-browse 확인:
  $R fill @eN "스크립트 태그 패턴 입력"
  $R click @eN               → 제출
  $R console --errors        → 스크립트 실행 흔적 확인
  $R screenshot dest-05.png  → 화면에 텍스트로 표시되는지 확인

실패 판정 (심각도: CRITICAL):
  - 스크립트가 실행됨 (console.messages로 확인)
  - 다른 사용자에게 스크립트 전파 가능성

방어 방법:
  - JSX 텍스트 노드 사용 (innerHTML/innerText 대신)
  - HTML 삽입이 불가피한 경우 DOMPurify 등 sanitizer 라이브러리 사용
  - Content Security Policy(CSP) 헤더 설정

심각도: CRITICAL — 발견 즉시 개발팀 에스컬레이션
```

### 6. 버튼 연타 (중복 요청)

```
테스트: 제출 버튼을 빠르게 여러 번 클릭 (또는 Enter 키 연타)
시뮬레이션:
  $R click @eN
  $R click @eN               ← 즉시 연속 클릭
  $R click @eN
  $R network --errors        → 요청이 몇 번 전송됐는지 확인

예상 정상 동작:
  - 첫 클릭 후 버튼 비활성화 (disabled)
  - 또는 debounce/throttle로 중복 요청 차단
  - 결과적으로 DB에 레코드 1개만 생성

실패 판정 (심각도: HIGH):
  - 동일 주문/결제가 N개 생성됨
  - 이중 결제 발생 가능성
  - 네트워크 요청이 클릭 횟수만큼 전송됨
```

### 7. 뒤로가기 후 재제출

```
테스트:
  1. 폼 작성 후 제출
  2. 제출 완료 페이지에서 브라우저 뒤로가기
  3. 폼 페이지로 돌아온 후 다시 제출

riff-browse:
  $R click @eN
  $R wait "완료"
  $R js "history.back()"
  $R click @eN
  $R network --errors

예상 정상 동작:
  - 뒤로가기 시 "이 페이지를 재방문하면 제출이 반복됩니다" 경고
  - 또는 서버 사이드 멱등성 처리 (동일 요청 중복 방지)
  - 중복 레코드 생성 없음

실패 판정 (심각도: HIGH):
  - 중복 레코드 2개 생성
  - 결제가 두 번 청구됨
```

### 8. 네트워크 끊김 시뮬레이션

```
테스트: 폼 제출 직후 (API 응답 전) 네트워크 차단 시뮬레이션

riff-browse:
  $R click @eN
  $R js "window.dispatchEvent(new Event('offline'))"
  $R screenshot dest-08.png
  $R console --errors

예상 정상 동작:
  - "네트워크 연결이 끊겼습니다" 또는 "잠시 후 다시 시도해주세요" 메시지
  - 입력값이 유지됨 (재시도 가능)
  - 앱이 크래시되지 않음

실패 판정 (심각도: MEDIUM):
  - 앱 전체 크래시 (흰 화면)
  - 입력값이 사라짐
  - 에러 메시지 없이 무한 로딩
```

### 9. 권한 우회 시도

```
테스트 1: URL 직접 접근
  - 다른 사용자의 리소스 URL 직접 입력
  - 예: /orders/123 (내 주문이 아닌 다른 사람의 주문 ID)

riff-browse:
  $R goto http://localhost:3000/orders/타인_주문_ID
  $R screenshot dest-09.png
  $R network --errors        → API 응답 상태 코드(403/404 기대) 확인

예상 정상 동작:
  - 403 Forbidden 또는 404 반환
  - "접근 권한이 없습니다" 메시지
  - 타인의 데이터가 표시되지 않음

실패 판정 (심각도: CRITICAL):
  - 타인의 주문/개인정보가 표시됨
  - API가 200으로 응답하며 데이터 반환

테스트 2: 권한 없는 API 직접 호출
  - 관리자 전용 API를 일반 사용자 토큰으로 호출
  - 예: DELETE /api/admin/users/123

심각도: CRITICAL — 발견 즉시 개발팀 에스컬레이션
```

### 10. 만료된 토큰으로 요청

```
테스트:
  1. 로그인 후 토큰 저장
  2. 토큰 만료 시뮬레이션 (localStorage 직접 변조)
  3. API 요청 실행

riff-browse:
  $R js "localStorage.setItem('token', 'expired.invalid.token')"
  $R goto http://localhost:3000/dashboard
  $R screenshot dest-10.png
  $R network --errors

예상 정상 동작:
  - 401 Unauthorized 응답
  - 로그인 페이지로 자동 리다이렉트
  - "세션이 만료되었습니다. 다시 로그인해주세요" 메시지

실패 판정 (심각도: HIGH):
  - 만료된 토큰으로 API 접근 성공
  - 리다이렉트 없이 에러 화면 표시
  - 앱 크래시
```

---

## 심각도 분류

| 심각도 | 기준 | 대응 |
|--------|------|------|
| CRITICAL | 데이터 유출, 권한 우회, SQL 인젝션 성공, XSS 스크립트 실행 | 즉시 개발팀 에스컬레이션, 기능 릴리즈 차단 |
| HIGH | 중복 결제, 만료 토큰 접근, 앱 크래시 | 릴리즈 전 필수 수정 |
| MEDIUM | 네트워크 에러 시 UX 깨짐, 레이아웃 파괴 | 다음 스프린트 내 수정 |
| LOW | 에러 메시지 불명확, i18n 불일치 | 백로그 등록 후 수정 |

---

## 파괴자 보고서 형식

### 패턴별 결과

| 패턴 | 예상 동작 | 실제 동작 | 결과 | 심각도 | 증거 |
|------|----------|----------|------|--------|------|
| 빈 입력 | 유효성 에러 메시지 | 에러 메시지 표시됨 | PASS | - | dest-01.png |
| XSS 삽입 시도 | 텍스트로 표시 | 스크립트 실행됨 | FAIL | CRITICAL | dest-05.png |
| 버튼 연타 | 요청 1회만 전송 | 요청 3회 전송, 중복 주문 생성 | FAIL | HIGH | dest-06.png |
| 권한 우회 | 403 반환 | 200 + 타인 데이터 반환 | FAIL | CRITICAL | dest-09.png |

### 전체 요약

```
총 패턴: 10개
PASS: 7개
FAIL: 3개

CRITICAL 취약점:
  1. XSS — 사용자 입력이 HTML로 렌더링됨
             위치: src/components/CommentList.tsx:34
             원인: innerHTML 직접 조작 사용
             수정: JSX 텍스트 렌더링으로 교체 또는 DOMPurify 적용

  2. 권한 우회 — 타인의 주문 데이터 노출
                 위치: src/pages/api/orders/[id].ts
                 원인: session.userId 와 order.userId 검증 없음
                 수정: API에서 소유권 검증 로직 추가

HIGH 취약점:
  1. 중복 요청 — 버튼 연타 시 중복 주문 생성
                 위치: 제출 버튼 disabled 처리 누락
                 수정: 제출 버튼 클릭 후 즉시 disabled 처리

권장 조치 순서:
  1. [즉시] XSS: innerHTML 제거, 안전한 렌더링 방식으로 교체
  2. [즉시] 권한 우회: API 소유권 검증 추가
  3. [릴리즈 전] 중복 요청: 제출 버튼 disabled 처리
```
