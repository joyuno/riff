# Tier 3: Live Browser QA — 상세 가이드

Playwright MCP 도구를 사용한 실제 브라우저 테스트.
Tier 1, 2를 통과한 뒤에만 실행한다.
정적 분석으로 잡을 수 없는 런타임 버그, UX 문제, 비동기 타이밍 버그를 발견한다.

---

## 환경 준비

### 1. 의존성 설치

```bash
npm install
```

패키지 설치 실패 시 Tier 3 진행 불가. 에러 로그 수집 후 보고.

### 2. 개발 서버 시작 (백그라운드)

```bash
npm run dev &
DEV_PID=$!
echo "개발 서버 PID: $DEV_PID"
```

### 3. 서버 Ready 확인 (health check)

서버가 준비되기 전에 테스트를 시작하면 모든 테스트가 실패한다.
반드시 준비 완료를 확인한 뒤 진행한다.

```bash
# 최대 30초 대기
for i in $(seq 1 30); do
  curl -s http://localhost:3000 > /dev/null && echo "서버 준비 완료" && break
  echo "대기 중... ${i}초"
  sleep 1
done
```

또는 Playwright `browser_wait_for`로 특정 텍스트 출현 대기.

### 4. 테스트 완료 후 서버 종료

```bash
kill $DEV_PID
```

---

## Playwright MCP 도구 사용법

### browser_navigate — URL 접속

```
도구: browser_navigate
입력: { url: "http://localhost:3000/dashboard" }
용도: 페이지 이동, 첫 진입
```

### browser_snapshot — 접근성 스냅샷 (요소 탐색의 시작점)

```
도구: browser_snapshot
용도: 현재 페이지의 모든 상호작용 가능한 요소와 ref 값 확인
출력: 각 요소의 ref, role, name, 텍스트
```

스냅샷을 먼저 찍어 `ref` 값을 확인한 뒤, 해당 ref로 클릭/입력한다.

### browser_click — 요소 클릭

```
도구: browser_click
입력: { ref: "e12" }  ← snapshot에서 얻은 ref 값
용도: 버튼, 링크, 탭 클릭
```

### browser_fill_form — 폼 입력

```
도구: browser_fill_form
입력: {
  ref: "e5",
  value: "test@example.com"
}
용도: input, textarea, select 값 입력
```

### browser_take_screenshot — 증거 스크린샷

```
도구: browser_take_screenshot
용도: 각 Step 완료 후 현재 상태 캡처
파일명 규칙: step-01-login-form.png, step-02-after-submit.png
```

### browser_console_messages — 콘솔 에러 수집

```
도구: browser_console_messages
용도: JavaScript 에러, 경고, 로그 수집
확인: error 레벨 메시지 필터링
```

### browser_network_requests — 네트워크 요청 확인

```
도구: browser_network_requests
용도: API 호출 상태 코드, 응답 body 확인
확인: 4xx, 5xx 응답 필터링
```

### browser_wait_for — 대기

```
도구: browser_wait_for
입력: {
  text: "주문이 완료되었습니다",  ← 출현 대기
  timeout: 5000
}
용도: 비동기 처리 완료 대기, 로딩 스피너 사라짐 대기
```

---

## 유저 저니 → Playwright 시나리오 변환

### 변환 원칙

`pulse-interview`가 수집한 유저 저니의 각 Step을 Playwright 행동 시퀀스로 변환한다.

**유저 저니 원문:**
```
사용자가 로그인한다 → 대시보드에서 새 주문을 생성한다 → 주문 완료를 확인한다
```

**Playwright 시나리오:**
```
Step 1: 로그인 페이지 접속
  browser_navigate({ url: "http://localhost:3000/login" })
  browser_snapshot()  → ref 확인
  browser_take_screenshot()  → 증거: step-01-login-page.png

Step 2: 로그인 정보 입력
  browser_fill_form({ ref: "e2", value: "user@test.com" })  → 이메일
  browser_fill_form({ ref: "e3", value: "password123" })   → 비밀번호
  browser_click({ ref: "e4" })  → 로그인 버튼
  browser_take_screenshot()  → 증거: step-02-login-submit.png

Step 3: 로그인 완료 확인
  browser_wait_for({ text: "대시보드" })
  browser_console_messages()  → 에러 없는지 확인
  browser_take_screenshot()  → 증거: step-03-dashboard.png

Step 4: 새 주문 생성
  browser_snapshot()  → "새 주문" 버튼 ref 확인
  browser_click({ ref: "e15" })
  browser_take_screenshot()  → 증거: step-04-new-order.png

Step 5: 주문 폼 작성 및 제출
  browser_fill_form({ ref: "e20", value: "상품A" })
  browser_click({ ref: "e25" })  → 제출 버튼
  browser_network_requests()   → API 호출 상태 확인

Step 6: 주문 완료 확인
  browser_wait_for({ text: "주문이 완료되었습니다", timeout: 5000 })
  browser_take_screenshot()  → 증거: step-06-order-complete.png
  browser_console_messages()  → 에러 없는지 확인
```

### 매 Step에서 반드시 수행

1. **browser_take_screenshot** — 현재 상태 증거 캡처
2. **browser_console_messages** — 에러 발생 여부 확인
3. 중요 비동기 작업 후 **browser_network_requests** — API 상태 확인

---

## 검증 실패 시 대응

### 실패 감지 기준

- `browser_wait_for` timeout 발생
- `browser_console_messages`에서 error 레벨 메시지
- `browser_network_requests`에서 4xx/5xx 응답
- 스냅샷에서 예상 요소가 없음
- 스크린샷에서 에러 화면 확인

### 실패 시 수집 절차

```
1. browser_take_screenshot()  → 실패 시점 상태 캡처
2. browser_console_messages() → 전체 콘솔 에러 전문 캡처
3. browser_network_requests() → 실패한 API 요청/응답 body 캡처
4. browser_snapshot()         → 현재 DOM 상태 확인
```

### Tier 1 경계면으로 역추적

실패 원인을 Tier 1 경계면 유형으로 분류한다:

| 실패 증상 | 경계면 유형 | 역추적 방향 |
|----------|-----------|-----------|
| API 응답 후 화면 업데이트 없음 | API↔훅 shape 불일치 | 응답 body vs 훅 타입 재비교 |
| 클릭 후 404 이동 | 경로↔링크 불일치 | href 값 vs 실제 파일 재확인 |
| 상태가 변하지 않음 | 상태전이 누락 | status 업데이트 코드 재확인 |
| 데이터가 undefined | DB↔API↔UI 체인 단절 | 체인 전체 재추적 |
| 콘솔에 타입 에러 | Tier 2 미탐지 타입 버그 | as any 우회 코드 검사 |

---

## 시나리오 우선순위

유저 저니가 여러 개인 경우 다음 순서로 실행한다:

1. **핵심 전환 경로** (가입 → 핵심 기능 → 결제 등)
2. **가장 많이 쓰이는 경로** (pulse-interview의 사용 빈도 기준)
3. **에러가 예상되는 경계면** (Tier 1에서 위험 신호가 나온 영역)
4. **선택적**: 유령 사용자, 파괴자 변형

---

## Tier 3 보고서 형식

### Step별 결과

| Step | 행동 | 예상 결과 | 실제 결과 | 결과 | 증거 |
|------|------|----------|----------|------|------|
| 1 | 로그인 페이지 접속 | 로그인 폼 표시 | 로그인 폼 표시됨 | PASS | step-01.png |
| 2 | 이메일/비밀번호 입력 후 로그인 | 대시보드 이동 | 500 에러 응답 | FAIL | step-02.png |

### 실패 상세

```
Step 2 실패 상세:
  콘솔 에러: TypeError: Cannot read property 'userId' of undefined
             at Dashboard.tsx:42
  네트워크:  POST /api/auth/login → 500
             응답 body: { "error": "user_id column not found" }
  원인 추정: DB 컬럼명 'user_id' → API 응답 'userId' 변환 누락
  경계면 유형: DB↔API↔UI 체인 (Tier 1 검증 대상 4)
```

### 전체 요약

```
시나리오: 로그인 → 주문 생성 → 완료 확인
총 Step: 6개
통과: 1개 (17%)
실패: 1개 (Step 2)
건너뜀: 4개 (실패로 인한 중단)

발견된 버그:
  [CRITICAL] 로그인 API 500 에러 — DB 컬럼명 불일치
              파일: src/pages/api/auth/login.ts:28

권장 수정 순서:
  1. [CRITICAL] API 응답 직렬화에서 user_id → userId 변환 추가
```
