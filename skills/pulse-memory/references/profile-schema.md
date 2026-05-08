# Profile Schema: 사용자 프로파일 단일 파일 스키마

이 파일은 LEARN 단계에서 프로파일 갱신 또는 ASK/BUILD에서 적용 시에만 읽는다. SKILL.md에 포함하지 않는다.

---

## 저장 위치

```
.pulse/memory/profile.md   (단일 파일)
```

`.gitignore`에 `.pulse/memory/profile.md` 필수 (개인 단위).

> 4개 파일(preferences/domain-knowledge/pain-points/decision-history)에서 1개로 압축한 이유: 매번 4파일 다 읽어야 의미 있어 분리는 컨텍스트 비용만 증가.

---

## 파일 형식

```markdown
# 사용자 프로파일

> 마지막 업데이트: YYYY-MM-DD
> 관찰 세션 수: N

## 커뮤니케이션

- 코드 설명 상세도: minimal | moderate | detailed
  - confirmed: yes | no
  - 마지막 관찰: YYYY-MM-DD
- 질문 선호 형식: choices | open-ended | minimal | none
  - confirmed: yes | no
- 보고 형식: bullet | prose | table | mixed
  - confirmed: yes | no
- 이모지 사용: yes | no
  - confirmed: yes | no

## 기술 성향

- 주력 언어: [TypeScript, Python]
- 선호 프레임워크: [Next.js, FastAPI]
- 테스트 스타일: tdd | 후작성 | 없음
- 코딩 스타일: 간결 | 명시적 | 혼합

## 의사결정 패턴

- 속도 vs 품질: speed | quality | balanced
- 새 기술 vs 검증된 기술: bleeding-edge | stable | pragmatic
- 자동화 수준: maximum | selective | manual

## 도메인 지식

- 잘 아는 영역: [...]
- 학습 중인 영역: [...]
- 약한 영역(설명 보강 필요): [...]

## Pain Points (원하지 않는 패턴)

- [짧은 한 줄 설명]
- [짧은 한 줄 설명]

## 의사결정 이력

| 날짜 | 결정 | 이유 |
|------|------|------|

## 관찰 이력

| 날짜 | 관찰 | 추론 | 확인 여부 |
```

---

## 값 정의

### 코드 설명 상세도

| 값 | 의미 |
|---|---|
| `minimal` | 코드만, 설명 최소 |
| `moderate` | 핵심 결정만 설명 |
| `detailed` | 배경/이유/대안까지 |

### 질문 선호 형식

| 값 | 의미 |
|---|---|
| `choices` | A vs B 선택지 |
| `open-ended` | "어떻게 하면 좋을까요?" |
| `minimal` | 꼭 필요한 것만 |
| `none` | 질문 없이 최선 진행 후 보고 |

### 보고 형식

| 값 | 의미 |
|---|---|
| `bullet` | 짧은 글머리 |
| `prose` | 서술형 |
| `table` | 표 정리 |
| `mixed` | 상황별 |

### 자동화 수준

| 값 | 의미 |
|---|---|
| `maximum` | 알아서 결정 |
| `selective` | 중요한 것만 확인 |
| `manual` | 매 단계 직접 확인 |

---

## 학습 메커니즘

### 자동 학습: 수정 요청

```
관찰: 사용자가 "설명이 너무 길어"
추론:
  - 현재 값이 detailed → minimal로 1단계 조정 검토
  - 처음 발생: confirmed=no로 추가 + 확인 요청
  - 2회 반복: 자동 confirm
```

### 자동 학습: 우회 행동

```
관찰: 오케스트레이터의 선택지 질문에 "그냥 알아서 해줘"
추론: 질문 선호 = none / 자동화 수준 = maximum 방향
```

### 명시적 학습

| 트리거 문구 | 처리 |
|----------|------|
| "이렇게 하지 마" | Pain Points에 추가 |
| "이게 좋아" | 해당 항목 confirm |
| "앞으로도 이렇게" | 즉시 update + 확인 |
| "내 스타일 기억해줘" | 현재 세션 관찰 즉시 저장 |

### 확인 요청 프로토콜

새 추론을 처음 했을 때:

```
"코드 설명을 짧게 원하시는 것 같은데, 앞으로도 이렇게 할까요?
(예 / 아니오 / 이번만)"

예 → profile 업데이트 (confirmed: yes)
아니오 → 학습 안 함
이번만 → 이번 세션만 적용, 미저장
```

같은 추론이 2회 이상 반복되면 확인 없이 자동 update.

---

## 적용 메커니즘

### ASK 단계

질문 선호 형식에 따라 인터뷰 톤 조정:
- `choices` → "A vs B 중?"
- `open-ended` → "어떻게 하면 좋을까요?"
- `minimal` → 핵심만 묻기
- `none` → 질문 생략, 최선 선택 후 보고

### BUILD 단계

- 주력 언어 / 선호 프레임워크 우선 추천
- 코딩 스타일에 따라:
  - `간결` → 짧은 변수명, 인라인, 추상화 최소
  - `명시적` → 긴 변수명, 타입 명시, 단계 분리
- 테스트 스타일 적용:
  - `tdd` → 테스트 먼저 작성

### 보고 단계

- 보고 형식 (`bullet` / `prose` / `table`) 적용
- 이모지 정책 적용 (no면 출력에서 완전 제거)

---

## 운영 원칙

1. **관찰 기반**: 추정이 아닌 실제 행동에서. "아마 이걸 좋아할 것"은 기록 안 함.
2. **확인 우선**: 신규 추론은 한번 확인 (2회 반복 전).
3. **명시성**: 사용자가 읽을 수 있는 형태로 기록.
4. **삭제 가능**: 사용자가 언제든 항목 또는 전체 초기화.
5. **세션 분리 전 저장**: LEARN 완료 확인 후 분리 (미확인 시 관찰 소실).

---

## 초기화

전체 프로파일 초기화:

```bash
rm .pulse/memory/profile.md
```

특정 카테고리만: 사용자가 직접 `profile.md`에서 해당 섹션 삭제. 다음 LEARN에서 새 관찰부터 다시 누적.
