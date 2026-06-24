# Antibody Schema: 항체 파일 스키마 상세

이 파일은 LEARN 단계 또는 BUILD 자동 주입 시에만 읽는다. SKILL.md에 포함하지 않는다.

---

## YAML Frontmatter

```yaml
---
name: {항체명}
type: boundary | logic | ui | performance | security | contract | secret
severity: critical | high | medium | low
discovered: YYYY-MM-DD
recurrence: {정수, 최초 0}
last_seen: YYYY-MM-DD
status: active | weakened | dormant
---
```

### 필드 설명

| 필드 | 필수 | 설명 |
|------|------|------|
| `name` | 필수 | 파일명과 일치, 영문 소문자 + 하이픈 |
| `type` | 필수 | 7종 중 하나 (`contract`, `secret` 신규) |
| `severity` | 필수 | critical / high / medium / low |
| `discovered` | 필수 | 최초 발견일 |
| `recurrence` | 필수 | 누적 재발 횟수 (최초 생성 시 0) |
| `last_seen` | 필수 | 마지막 발견일 |
| `status` | 필수 | active / weakened / dormant |

### type 값 정의

| type | 적용 영역 | 예시 |
|------|----------|------|
| `boundary` | 에이전트/모듈 경계면 | API 응답 shape 불일치 |
| `logic` | 비즈니스 로직 | 상태 전이 가드 누락, 계산 실수 |
| `ui` | UI/UX | empty/error 상태 누락, 로딩 미처리 |
| `performance` | 성능 | N+1 쿼리, 큰 번들 |
| `security` | 보안 | 권한 체크 누락, 토큰 정책 |
| `contract` | **계약서 작성 실수** | 단위 누락, 종단 상태 가드 누락 |
| `secret` | **시크릿/PII 외부 유출** | API 키·토큰·PEM·PII가 코드/계약서/PR 본문에 노출 |

`contract` 타입은 **BUILD-CONTRACT 단계에서 우선 주입**된다 (코드 작성 전 계약서 단계).
`secret` 타입은 **외부 전송 직전(PR/이슈 본문, 커밋, codex 디스패치) 게이트**로 주입된다 —
gstack의 redaction guard를 Riff 항체로 흡수한 것. ML 분류기까지 가지 않고 정규식 차단으로 충분하다
(Riff는 "가볍게"가 정체성). 매칭 시 BUILD/SHIP을 **차단**하고 사용자에게 보고한다.

#### secret 탐지 패턴 (HIGH = 차단, MEDIUM = 확인 후 진행)

| 티어 | 패턴(정규식) | 처리 |
|------|------------|------|
| HIGH | `AKIA[0-9A-Z]{16}` (AWS 액세스 키) | 차단 |
| HIGH | `-----BEGIN [A-Z ]*PRIVATE KEY-----` (PEM) | 차단 |
| HIGH | `gh[pousr]_[A-Za-z0-9]{36,}` (GitHub 토큰) | 차단 |
| HIGH | `xox[baprs]-[A-Za-z0-9-]{10,}` (Slack 토큰) | 차단 |
| MEDIUM | `eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.` (JWT) | 확인 |
| MEDIUM | `(sk|pk)_(live\|test)_[A-Za-z0-9]{20,}` (Stripe) | 확인 |
| MEDIUM | `[A-Z0-9_]*(KEY\|SECRET\|TOKEN\|PASSWORD)\s*=\s*['"][^'"]{8,}` (env 대입) | 확인 |
| MEDIUM | 이메일·주민번호·카드번호 형태 PII | 확인 |

> 스캔은 **보낼 바이트 그대로**(PR 본문 파일·커밋 메시지 파일)에 적용한다. 문자열을 스캔한 뒤
> 다시 렌더링하면 스캔-전송 간극이 생긴다(gstack 규칙). `riff-contracts`의 security 계약서가
> 예시로 든 시크릿은 ` ```example ` 펜스로 감싸 오탐(WARN)으로 강등한다.

### severity 정의

| severity | 기준 |
|----------|------|
| `critical` | 데이터 손실, 보안 취약점, 서비스 중단 |
| `high` | 주요 기능 오작동, 데이터 불일치 |
| `medium` | 부분 기능 오류, 엣지 케이스 |
| `low` | UI 불일치, 경고 누락 |

### status 정의

| status | BUILD 주입 | 설명 |
|--------|----------|------|
| `active` | 예 | 현재 유효 |
| `weakened` | 아니오 | 90일 무재발, 기록만 보존 |
| `dormant` | 아니오 | 180일 무재발, 완전 비활성 |

---

## 섹션 구조

```markdown
---
[YAML frontmatter]
---

## 버그 설명
[증상 위주]

## 근본 원인
[왜 발생했는지, 어떤 가정이 틀렸는지]

## 예방 체크리스트
- [ ] [확인 항목 1]
- [ ] [확인 항목 2]

## 관련 파일
- [파일 경로]

## 재발 이력
| 날짜 | 상황 | 강화 내용 |
```

---

## 파일명 규칙

`{type}-{summary}.md` — 파일명만 봐도 type 추론 가능.

예시:
- `boundary-api-response-wrapping.md`
- `logic-state-transition-guard.md`
- `ui-async-state-incomplete.md`
- `performance-n-plus-one.md`
- `security-missing-authz.md`
- `contract-cm-013-unit-missing.md`
- `secret-aws-key-in-pr-body.md`

`contract` 타입 항체는 `contract-{cm-id}-{slug}.md` 형식 권장 (CM 카탈로그와 cross-reference).

---

## 예시 1: boundary 타입

```markdown
---
name: boundary-api-response-wrapping
type: boundary
severity: high
discovered: 2024-03-15
recurrence: 3
last_seen: 2024-05-02
status: active
---

## 버그 설명
백엔드가 배열을 직접 반환했고 프론트엔드가 `{ data: [...] }` 래핑을 기대해 런타임 에러 발생.

## 근본 원인
계약서 없이 "data로 감싸겠지" 가정. type 계약서에 래핑 규칙 누락.

## 예방 체크리스트
- [ ] 응답이 type 계약서의 Response Body와 일치?
- [ ] 배열 반환 시 { data: [...] } 래핑인지 직접 반환인지 계약서 확인
- [ ] 에러 응답 { error: { code, message } } 형태?
- [ ] null과 빈 배열 구분 처리?

## 관련 파일
- src/api/routes/
- src/services/

## 재발 이력
| 날짜 | 상황 | 강화 내용 |
|------|------|-----------|
| 2024-04-01 | 결제 API 재발 | "null vs 빈 배열" 추가 |
| 2024-05-02 | 알림 API 재발 | "계약서 확인" 강조 |
```

---

## 예시 2: contract 타입 (신규)

```markdown
---
name: contract-cm-013-unit-missing
type: contract
severity: medium
discovered: 2026-04-10
recurrence: 2
last_seen: 2026-05-01
status: active
---

## 버그 설명
Constants Contract에 `EXPIRE: 30` 적힘. 프론트는 분으로 해석, 백엔드는 초로 해석 → 토큰 만료 시점 불일치.

## 근본 원인
계약서 작성 시 단위 명시 빠뜨림. lint도 통과되어 BUILD에 들어감.

## 예방 체크리스트
- [ ] 모든 수치 상수에 단위 표기? (`30 (분)` 또는 `EXPIRE_MINUTES: 30`)
- [ ] 변수명에 단위 포함됐는가?
- [ ] contract-lint.md의 Constants 체크리스트 통과?

## 관련 파일
- _workspace/contracts/auth-constants.md

## 재발 이력
| 날짜 | 상황 | 강화 내용 |
|------|------|-----------|
| 2026-05-01 | rate limit 상수에 단위 누락 | "변수명 단위 포함 강제" 추가 |
```

---

## 예시 3: ui 타입

```markdown
---
name: ui-async-state-incomplete
type: ui
severity: medium
discovered: 2024-03-20
recurrence: 5
last_seen: 2024-05-10
status: active
---

## 버그 설명
비동기 컴포넌트에서 loading/error 상태 미구현 → 빈 화면 표시.

## 근본 원인
성공 케이스만 구현, loading/error 후순위로 미루다 누락.

## 예방 체크리스트
- [ ] 로딩 중 스켈레톤/스피너?
- [ ] API 오류 시 메시지 + 재시도 버튼?
- [ ] empty state 화면?
- [ ] visual 계약서 7가지 상태(default/hover/active/disabled/loading/success/error) 모두 처리?

## 관련 파일
- src/components/
- src/hooks/useAsync.ts
```

---

## 예시 4: secret 타입 (신규)

```markdown
---
name: secret-aws-key-in-pr-body
type: secret
severity: critical
discovered: 2026-06-24
recurrence: 0
last_seen: 2026-06-24
status: active
---

## 버그 설명
SHIP 단계에서 PR 본문에 디버그용 AWS 액세스 키(AKIA...)가 그대로 포함되어 외부로 나갈 뻔함.

## 근본 원인
로그에서 복붙한 에러 메시지에 키가 섞여 있었고, 외부 전송 직전 스캔이 없었음.

## 예방 체크리스트
- [ ] PR/이슈 본문, 커밋 메시지를 **보낼 파일 그대로** secret 패턴 스캔했는가?
- [ ] HIGH 매칭(AWS/PEM/GitHub/Slack) 시 차단했는가?
- [ ] 예시 시크릿은 ```example 펜스로 감쌌는가?
- [ ] .riff/, _workspace/ 산출물에 실 키가 남지 않았는가?

## 관련 파일
- (SHIP 직전 외부 전송 경로 전체)

## 재발 이력
| 날짜 | 상황 | 강화 내용 |
```

`secret` 항체는 매칭 시 보고로 끝내지 않고 **해당 단계를 차단**한다는 점에서 다른 타입과 다르다.

---

## 관련성 매칭 기준 (BUILD 자동 주입)

| 기준 | 설명 |
|------|------|
| 파일 경로 일치 | 항체의 관련 파일이 현재 작업 파일과 겹침 |
| type 일치 | 항체의 type이 현재 단계와 일치 (boundary↔BUILD, contract↔BUILD-CONTRACT 등) |
| 키워드 일치 | 항체 설명 내 키워드가 작업 설명에 포함 |
| severity | critical / high는 type만 일치해도 항상 주입 |

---

## 항체 강화 규칙

같은 유형의 버그 재발 시:

1. `recurrence` +1
2. `last_seen` 갱신
3. 재발 이력 표에 행 추가
4. 기존 체크리스트 검토 → 더 구체적인 항목 추가
5. 필요 시 `severity` 상향

3회 이상 재발 시 사용자에게 보고: "이 항체가 반복 재발 — 계약서 또는 템플릿 자체 갱신 필요?"

---

## 약화 / 휴면 규칙

- `last_seen + 90일 < 오늘` AND 그 기간 무재발 → `weakened`
- `last_seen + 180일 < 오늘` AND 그 기간 무재발 → `dormant`
- 재발 시 즉시 `active`로 복귀

파일 자체는 절대 삭제하지 않는다 (기록 보존).
