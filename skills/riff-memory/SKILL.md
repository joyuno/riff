---
name: riff-memory
description: "프로젝트의 학습 메모리. 버그 패턴(항체)과 사용자 프로파일을 함께 관리하여 다음 Riff·다음 세션에 자동 적용. Riff의 LEARN 단계에서 호출. 버그 발생 시 항체 자동 생성·강화, 계약서 작성 실수도 별도 항체로 추적, 사용자 선호도는 단일 프로파일에 누적. '버그 기억', '같은 실수 방지', '내 스타일 기억', '학습' 시 사용."
---

# riff-memory: 항체 + 프로파일 통합 메모리

## 무엇이고 왜 하나로 묶나

Riff가 다음 세션·다음 Riff에서 같은 실수를 반복하지 않도록 두 가지를 누적한다:

1. **항체** — 한번 겪은 버그·계약서 실수의 예방 체크리스트
2. **프로파일** — 사용자의 작업 방식·선호도

둘 다 LEARN 단계에서 같은 입력(이번 세션의 실패와 수정 요청)을 보고 다른 출력을 만드는 것뿐이다. 모듈을 분리하면 호출 순서·세션 분리 직전 저장 등 동기화 비용이 늘어나기에 단일 모듈로 통합한다.

> **단일 호출 보장**: LEARN 단계에서 riff-memory가 한번 실행되면 항체와 프로파일이 모두 갱신되고 저장된다.

---

## 저장 위치

```
.riff/memory/
├── antibodies/
│   ├── boundary-{name}.md
│   ├── logic-{name}.md
│   ├── ui-{name}.md
│   ├── performance-{name}.md
│   ├── security-{name}.md
│   ├── contract-{name}.md      ← 계약서 작성 실수
│   └── secret-{name}.md        ← 시크릿/PII 외부 유출 차단 (신규)
└── profile.md                   ← 사용자 프로파일 단일 파일
```

`.gitignore` 정책:
- `.riff/memory/antibodies/` — git 추적 (팀 공유)
- `.riff/memory/profile.md` — git 미추적 (개인)

---

## 항체 (antibodies)

상세 스키마: `references/antibody-schema.md`

### 7가지 type

| type | 적용 영역 | 예시 |
|------|----------|------|
| `boundary` | 에이전트/모듈 간 경계면 | API 응답 shape 불일치 |
| `logic` | 비즈니스 로직 | 상태 전이 가드 누락 |
| `ui` | UI/UX | empty/error 상태 누락 |
| `performance` | 성능 | N+1 쿼리, 큰 번들 |
| `security` | 보안 | 권한 체크 누락, 토큰 만료 |
| `contract` | **계약서 작성 실수** | 단위 누락, 종단 상태 가드 누락 |
| `secret` | **시크릿/PII 외부 유출** | API 키·토큰·PEM·PII가 코드/PR 본문에 노출 |

`contract` 타입 시드 카탈로그: `riff-contracts/references/contract-mistakes.md`의 CM-001 ~ CM-020.
`secret` 타입은 외부 전송 직전(PR/이슈 본문·커밋·codex 디스패치) **차단 게이트**로 작동한다 —
탐지 패턴과 처리는 `references/antibody-schema.md`의 secret 섹션 참조.

### 생명주기

```
[없음] ──버그 발견──→ [active]
[active] ──재발──→ [active] (recurrence +1, 체크리스트 강화)
[active] ──90일 무재발──→ [weakened] (BUILD 주입 제외, 파일 보존)
[weakened] ──재발──→ [active]
[weakened] ──180일 무재발──→ [dormant]
```

### LEARN 단계에서의 처리 순서

1. VERIFY 결과에서 실패 목록 수집
2. 각 실패에 대해 `.riff/memory/antibodies/`에서 유사 항체 검색
3. 있으면 강화(`recurrence +1`, `last_seen` 갱신, 체크리스트 보강), 없으면 신규 생성
4. `last_seen`이 90일 지난 항체는 `weakened`로 전이

### BUILD 단계 자동 주입

오케스트레이터는 BUILD 시작 시:

1. 작업 대상의 파일 경로/모듈/키워드 수집
2. `status: active` 항체 중 관련성 매칭(파일/타입/키워드/severity)
3. 매칭된 항체의 예방 체크리스트를 에이전트 프롬프트에 삽입
4. `severity: critical | high` 항체는 타입만 일치해도 항상 주입

`contract` 타입 항체는 BUILD-CONTRACT 단계에서 우선 주입된다 (계약서 작성 직전).

---

## 프로파일 (profile)

상세 스키마: `references/profile-schema.md`

### 단일 파일 구조

```markdown
# 사용자 프로파일

> 마지막 업데이트: YYYY-MM-DD | 관찰 세션 수: N

## 커뮤니케이션
- 코드 설명 상세도: minimal | moderate | detailed
- 질문 선호 형식: choices | open-ended | minimal | none
- 보고 형식: bullet | prose | table | mixed
- 이모지 사용: yes | no

## 기술 성향
- 주력 언어: [...]
- 선호 프레임워크: [...]
- 테스트 스타일: tdd | 후작성 | 없음
- 코딩 스타일: 간결 | 명시적

## 의사결정 패턴
- 속도 vs 품질: speed | quality | balanced
- 자동화 수준: maximum | selective | manual

## Pain Points
- [원하지 않는 패턴 / 반복 불만]

## 관찰 이력
| 날짜 | 관찰 | 추론 | 확인 여부 |
```

> 4개 파일에서 1개로 압축한 이유: 매번 4파일을 다 읽어야 의미가 있어, 분리는 컨텍스트 비용만 증가시킴.

### 학습 메커니즘

| 트리거 | 처리 |
|--------|------|
| 사용자 수정 요청 | 패턴 분석 → 처음 발생이면 확인 요청, 2회 반복이면 자동 학습 |
| 우회 행동(직접 지시) | 자동화 수준 / 질문 형식 조정 검토 |
| 명시적 피드백 ("이렇게 해줘") | 즉시 프로파일 업데이트 |

### 적용 메커니즘

| 단계 | 적용 방식 |
|------|----------|
| ASK | 질문 선호 형식에 따라 인터뷰 톤 조정 |
| BUILD | 주력 언어 / 프레임워크 / 코딩 스타일 반영 |
| 보고 | bullet/prose/table 형식 + 이모지 정책 적용 |

---

## LEARN 단계 실행 절차

세션 종료 또는 Riff 종료 시:

```
1. 항체 처리
   1-1. VERIFY 실패 목록 수집
   1-2. 각 실패 → 유사 항체 검색 → 강화 또는 신규 생성
   1-3. weakened 후보(90일 무재발) 표시

2. 프로파일 처리
   2-1. 이번 세션의 수정 요청·우회 행동·명시적 피드백 수집
   2-2. 각 관찰 → 프로파일 카테고리 매핑
   2-3. 신규 관찰은 confirmed: false로 추가, 2회 반복은 자동 confirm

3. 저장
   3-1. .riff/memory/antibodies/ 갱신
   3-2. .riff/memory/profile.md 갱신
   3-3. _workspace/riff-status.md의 자동화 체크리스트에 "DNA 저장 완료" 체크

4. 학습 요약 보고
   - 신규 항체 N개 / 강화 M개 / 약화 K개
   - 프로파일 업데이트 항목 또는 확인 요청 목록
```

> **세션 분리 전 반드시 LEARN 단계에서 riff-memory가 완료돼야 한다.** 분리 직전 저장 여부 미확인 시 이번 세션 관찰이 소실된다.

---

## 항체 자동 주입 형식

BUILD 단계에서 에이전트 프롬프트에 삽입되는 블록 예시:

```
## 면역 체크리스트 (이전 실수 패턴 기반)

작업 완료 전 반드시 확인하세요.

### [boundary] api-response-wrapping (high, 재발 3회)
- [ ] 응답이 type 계약서의 Response Body와 일치?
- [ ] 빈 배열과 null을 구분?
- [ ] 에러 응답이 { error: { code, message } } 형태?

### [contract] CM-013 상수 단위 모호 (medium, 재발 2회)
- [ ] 모든 수치 상수에 단위가 명시?
- [ ] 변수명에 단위 포함?
```

---

## 운영 원칙

1. **단일 호출**: LEARN에서 riff-memory를 한번 부르면 항체+프로파일 모두 처리.
2. **삭제 금지**: 항체 파일은 status 변경만, 삭제 안 함.
3. **구체성**: 체크리스트는 "확인할 것"이 아닌 "무엇을 어떻게 확인"인지.
4. **최소 주입**: 관련성 없는 항체는 주입 안 함 (노이즈 방지).
5. **프로파일 분리**: `profile.md`는 개인 단위, `.gitignore` 필수.
6. **세션 분리 전 저장**: LEARN 완료 확인 후 세션 종료.

---

## 참조 파일

| 파일 | 역할 |
|------|------|
| `references/antibody-schema.md` | 항체 YAML/섹션 스키마 + type별 예시 |
| `references/profile-schema.md` | 프로파일 단일 파일 스키마 + 학습/적용 상세 |
| `riff-contracts/references/contract-mistakes.md` | `contract` 타입 항체 시드 카탈로그 |
