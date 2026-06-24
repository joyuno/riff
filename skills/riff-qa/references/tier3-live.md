# Tier 3: Live Browser QA — 상세 가이드

gstack `/qa`의 브라우저 구동 방식을 모방한다: **외부 Playwright MCP를 쓰지 않고**, 경량
러너 `riff-browse.mjs`(데몬)를 Bash로 호출한다. 한 명령 = 한 동작, 데몬이 페이지·요소맵·콘솔을
메모리에 유지하므로 두 번째 명령부터 ~100ms. Tier 1·2 통과 후에만 실행한다. 정적 분석으로
잡을 수 없는 런타임 버그·UX 문제·비동기 타이밍 버그를 발견한다.

> 왜 MCP를 버렸나: MCP는 명령마다 왕복(round-trip)이 있어 느리고 비결정적이다. gstack은
> 자체 브라우저 CLI를 "소유"해서 빠르고 재현 가능하게 만든다. Riff는 같은 철학을 58MB
> 바이너리·데몬 의존 없이, 프로젝트의 playwright만으로 재현한다.

---

## 0. 러너 설치 (첫 Tier 3 실행 시 1회)

```bash
mkdir -p _workspace/.riff
# 이 스킬의 references/riff-browse.mjs를 프로젝트 작업공간으로 복사
cp "$CLAUDE_PLUGIN_ROOT/skills/riff-qa/references/riff-browse.mjs" _workspace/.riff/riff-browse.mjs 2>/dev/null \
  || cp ~/.claude/plugins/*/joyuno-riff/skills/riff-qa/references/riff-browse.mjs _workspace/.riff/riff-browse.mjs
# playwright 확인 (프로젝트 dep 없으면)
node -e "require.resolve('playwright')" 2>/dev/null || npx playwright install chromium
```

이후 매 명령은 `R="node _workspace/.riff/riff-browse.mjs"` 별칭으로 호출한다.

---

## 1. 환경 준비

### 개발 서버 백그라운드 기동 + health check

```bash
npm run dev &
DEV_PID=$!
for i in $(seq 1 30); do
  curl -s http://localhost:3000 > /dev/null && echo "서버 준비 완료" && break
  echo "대기 중... ${i}초"; sleep 1
done
```

### 브라우저 데몬 기동

```bash
R="node _workspace/.riff/riff-browse.mjs"
$R start            # 헤드리스. 사람이 보면서 디버그하려면: $R start --headed
```

### 테스트 종료 후 정리

```bash
$R stop             # storageState 저장 후 브라우저 종료
kill $DEV_PID
```

---

## 2. riff-browse 명령 어휘 (gstack `$B` 모방)

| 명령 | 용도 | gstack 대응 |
|------|------|------------|
| `$R goto <url>` | 페이지 이동 | `$B goto` |
| `$R snapshot -i [-o shot.png]` | 클릭/입력 가능 요소에 `@e1..` 라벨 부여(+스크린샷) | `$B snapshot -i -o` |
| `$R click @e5` | 요소 클릭 | `$B click @e5` |
| `$R fill @e3 "값"` | 폼 입력 | `$B fill @e3` |
| `$R text [selector]` | 보이는 텍스트 확인 | `$B text` |
| `$R console --errors` | 콘솔 에러 수집 | `$B console --errors` |
| `$R network --errors` | 4xx/5xx 응답 | `$B console` |
| `$R js "<expr>"` | API 직접 타격/평가 | `$B js` |
| `$R links` | 페이지 링크 맵 | `$B links` |
| `$R wait "<텍스트>" [ms]` | 비동기 완료 대기 | `$B snapshot -D` |
| `$R screenshot <path>` | 증거 스크린샷 | `$B screenshot` |
| `$R cookie-import <file>` | storageState 주입 | `$B cookie-import` |

**핵심 흐름: snapshot으로 `@eN` 라벨을 얻은 뒤 그 라벨로 click/fill 한다.** 라벨은 DOM에
`data-riff-ref` 속성으로 고정되므로 같은 페이지 내 후속 명령에서 안정적으로 재사용된다.

---

## 3. 유저 저니 → riff-browse 시나리오 변환

`riff-interview`가 수집한 `journeys.md`(또는 `master-plan.md`)의 각 Step을 명령 시퀀스로 변환한다.

**유저 저니 원문:**
```
사용자가 로그인한다 → 대시보드에서 새 주문을 생성한다 → 주문 완료를 확인한다
```

**riff-browse 시나리오:**
```bash
R="node _workspace/.riff/riff-browse.mjs"
SHOT=_workspace/riff-N/screenshots; mkdir -p "$SHOT"

# Step 1: 로그인 페이지 접속
$R goto http://localhost:3000/login
$R snapshot -i -o "$SHOT/step-01-login.png"   # @e1 email, @e2 password, @e3 submit ...

# Step 2: 로그인
$R fill @e1 "user@test.com"
$R fill @e2 "[REDACTED]"                       # 실제 비밀번호는 보고서에 절대 기록 금지
$R click @e3
$R wait "대시보드"
$R console --errors                            # 에러 없는지
$R screenshot "$SHOT/step-02-dashboard.png"

# Step 3: 새 주문 생성
$R snapshot -i -o "$SHOT/step-03-orders.png"   # "새 주문" 버튼 @eN 확인
$R click @e7
$R fill @e9 "상품A"
$R click @e12                                  # 제출
$R network --errors                            # API 호출 상태(4xx/5xx) 확인

# Step 4: 완료 확인
$R wait "주문이 완료되었습니다" 5000
$R screenshot "$SHOT/step-04-complete.png"
```

selector/라벨 우선순위는 gstack과 동일: **`data-testid` > role+name > text**. `snapshot -i`가
부여한 `@eN`은 role+name 기반이므로 안정적이다. 시나리오는 `_workspace/riff-N/scenario.sh`에 저장.

### 매 Step에서 반드시 수행
1. **screenshot** — 현재 상태 증거 캡처
2. **console --errors** — 에러 발생 여부
3. 중요 비동기 작업 후 **network --errors** — API 상태

---

## 4. API 직접 타격 (gstack 패턴)

UI 없이 엔드포인트만 검증할 땐 브라우저 컨텍스트에서 직접 fetch:

```bash
$R js "await fetch('/api/orders', {method:'POST', body: JSON.stringify({item:'A'})}).then(r => r.status)"
$R js "await fetch('/api/orders').then(r => r.json()).then(d => d.length)"
```

세션 쿠키가 데몬 컨텍스트에 살아있으므로 인증된 요청이 그대로 나간다.

---

## 5. 검증 실패 시 대응

### 실패 감지 기준
- `$R wait` timeout
- `$R console --errors`에 error 레벨 메시지
- `$R network --errors`에 4xx/5xx
- `$R snapshot -i`에 예상 요소(@eN)가 없음

### 실패 시 수집 절차
```bash
$R screenshot "$SHOT/FAIL-$(date +%s).png"   # 실패 시점
$R console --errors                           # 콘솔 에러 전문
$R network --errors                           # 실패 API 요청/응답
$R snapshot -i                                # 현재 DOM 상태
```

### Tier 1 경계면으로 역추적

| 실패 증상 | 경계면 유형 | 역추적 방향 |
|----------|-----------|-----------|
| API 응답 후 화면 업데이트 없음 | API↔훅 shape 불일치 | 응답 body vs 훅 타입 재비교 |
| 클릭 후 404 이동 | 경로↔링크 불일치 | href 값 vs 실제 파일 재확인 |
| 상태가 변하지 않음 | 상태전이 누락 | status 업데이트 코드 재확인 |
| 데이터가 undefined | DB↔API↔UI 체인 단절 | 체인 전체 재추적 |
| 콘솔에 타입 에러 | Tier 2 미탐지 타입 버그 | `as any` 우회 코드 검사 |

**실패 발견 후에는 보고로 끝내지 말고 `riff-qa/SKILL.md`의 "VERIFY-FIX 루프"로 진입한다.**

---

## 6. 시나리오 우선순위

1. **핵심 전환 경로** (가입 → 핵심 기능 → 결제 등)
2. **가장 많이 쓰이는 경로** (riff-interview 사용 빈도 기준)
3. **에러가 예상되는 경계면** (Tier 1 위험 신호 영역)
4. **선택적 변형**: 유령 사용자(`ghost-user.md`), 파괴자(`destroyer.md`)

변형도 같은 `$R` 어휘를 쓴다 — 유령 사용자는 `$R snapshot -i` 결과를 보고 자유 클릭,
파괴자는 `$R fill @eN`에 SQL/XSS/초장문 페이로드를 주입한다.

---

## 7. Tier 3 보고서 형식

### Step별 결과
| Step | 행동 | 예상 | 실제 | 결과 | 증거 |
|------|------|------|------|------|------|
| 1 | 로그인 페이지 접속 | 폼 표시 | 표시됨 | PASS | step-01-login.png |
| 2 | 이메일+로그인 | 대시보드 이동 | 500 에러 | FAIL | step-02-dashboard.png |

### 실패 상세
```
Step 2 실패:
  콘솔: TypeError: Cannot read property 'userId' of undefined (Dashboard.tsx:42)
  네트워크: POST /api/auth/login → 500  body: {"error":"user_id column not found"}
  원인 추정: DB 컬럼명 user_id → API 응답 userId 변환 누락
  경계면 유형: DB↔API↔UI 체인 (Tier 1 검증 대상 4)
```

### 전체 요약 (Health Score 포함 — `riff-qa/SKILL.md` 루브릭)
```
시나리오: 로그인 → 주문 생성 → 완료
총 Step 6 / 통과 1 (17%) / 실패 1 / 건너뜀 4
Health Score: before 4/10 → (수정 후 재검증) after ?/10
발견 버그: [CRITICAL] 로그인 API 500 — DB 컬럼명 불일치 (src/pages/api/auth/login.ts:28)
```

실패 항목은 VERIFY-FIX 루프에서 수정 후, LEARN 단계에서 `riff-memory` 항체로 기록된다
(재현 시나리오 `scenario.sh`의 해당 Step을 항체에 첨부 → 회귀 방지).
