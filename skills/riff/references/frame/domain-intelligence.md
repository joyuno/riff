# Domain Intelligence — 도메인별 지식 발굴·검증·실행 계약

목적은 많은 문서를 모으는 것이 아니라 **이 도메인에서 무엇을 근거로 믿을지 정하고,
확인된 지식만 acceptance와 구현으로 연결하는 것**이다. Exa는 검색 수단이며 판단
주체가 아니다.

## 1. Domain Research Router

Cycle 0 인터뷰 직후 다음 프로파일을 `_workspace/detail/domain-profile.md`에 기록한다.

```markdown
# Domain Profile
- 업무 도메인:
- 지식 계열: regulated | operational | market | creative | technical | ai-data
- 위험 overlay: money | safety | privacy | rights | none
- 관할·언어·기준일:
- 사용자·현장 전문가:
- 우선 조사법:
- 우선 출처:
- 개발 전 막아야 할 unknown:
```

혼합 도메인은 주 계열 하나와 위험 overlay를 함께 쓴다. 이름만 보고 선택하지 말고,
잘못된 지식이 어떤 피해를 만드는지로 판정한다.

| 지식 계열 | 우선 발굴법 | 출처 우선순위 | 사용자 확인의 역할 |
|---|---|---|---|
| regulated | 관할·시행일·적용대상 확인 | 법령·규제기관·공식 기준 → 전문가 | 적용 상황 확인. 공식 규칙 자체를 취향으로 변경하지 않음 |
| operational | 실제 업무의 앞·중간·뒤 관찰, 기록물·예외 수집 | 사용자 행동·현장 담당자·운영 데이터 → 제품 도움말 | 실제 흐름·예외·우선순위 확정 |
| market | 현재 대안·구매 행동·지원 문의·이탈 증거 | 행동 데이터·인터뷰·지원 기록 → 경쟁 제품 도움말 | 문제 강도와 지불/사용 의사 검증 |
| creative | 성공/실패 사례 비교, 권리·플랫폼 제약 확인 | 플랫폼 정책·라이선스·성과 데이터 → 사례 | 품질 기준·브랜드·허용 타협 확정 |
| technical | 호환성·경계·실패 조건 재현 | 공식 문서·표준·소스·실행 실험 | 운영 제약과 허용 비용 확정 |
| ai-data | 실제 표본·오류 분류·사람 검토 지점 평가 | 데이터셋·평가 결과·모델 문서·공식 정책 | 허용 오류·검토 책임·중단 조건 확정 |

위험 overlay가 있으면 다음을 추가한다.

- `money`: 계산 불변식, 승인권자, 감사·되돌리기
- `safety`: 금기, 실패 안전, 사람 개입, 중단 조건
- `privacy`: 수집 최소화, 접근, 보존·삭제, 외부 전송
- `rights`: 소유권, 라이선스, 동의, 플랫폼 정책

## 2. Domain Model

조사 내용을 `_workspace/detail/domain-model.md`의 고정 7절로 합성한다.

```markdown
# Domain Model
## Actors       누가 수행·승인·지원하는가
## Jobs         어떤 결과를 끝내려 하는가
## Artifacts    무엇을 만들고 읽고 전달하는가
## Lifecycle    생성→변경→완료·취소 상태
## Rules        계산·정책·불변식
## Exceptions   중복·누락·실패·복구
## Unknowns     아직 확인되지 않은 결정
```

검색 결과의 기능 목록을 그대로 복사하지 않는다. 각 항목은 실제 행위·규칙·예외 중
하나로 번역한다. core-closure matrix(`discovery-research.md`)는 이 모델의 누락 검사다.

## 3. Knowledge Ledger

모든 구현 근거는 `_workspace/detail/knowledge-ledger.md`에 한 행으로 남긴다.

```markdown
| ID | Model | Claim | Evidence state | Evidence | Scope/date | User verdict | Acceptance | Status |
|---|---|---|---|---|---|---|---|---|
| K-001 | Rules | VAT 10%를 별도 표시 | official | URL | KR/2026-08-07 | 필요 | A-003 | confirmed |
```

### Evidence state

- `observed`: 실제 사용자 행동·운영 데이터에서 관찰
- `user-confirmed`: 사용자가 자기 업무에 필요하다고 확인
- `official`: 적용 가능한 법령·표준·공식 정책
- `industry`: 복수 사례나 제품 문서에서 발견한 관행
- `assumption`: 아직 검증되지 않은 해석
- `excluded`: 사용자가 이번 범위에서 제외

`industry`와 `assumption`만으로 core acceptance를 만들지 않는다. 공식 규칙은 사용자에게
진위를 묻지 않고 **그 규칙이 적용되는 상황인지** 확인한다. 출처가 바뀔 수 있으면
관할과 기준일을 반드시 기록한다.

### Status

- `candidate`: 질문 후보
- `confirmed`: 구현 가능
- `blocked`: 중요하지만 미확인
- `excluded`: 이번 범위 밖
- `invalidated`: PROVE에서 틀린 것으로 확인

## 4. Knowledge → Acceptance trace gate

FRAME verdict 전에 다음을 모두 만족해야 한다.

1. Domain Profile의 계열·overlay·관할·기준일이 정해졌다.
2. Domain Model 7절이 채워졌거나 해당 없음의 이유가 있다.
3. 관련 있는 core-closure 행에 `blocked`가 없다.
4. 모든 core acceptance에 `A-NNN` ID와 근거 `K-NNN`이 연결됐다.
5. `candidate`·`assumption`은 BUILD 태스크에 들어가지 않았다.
6. `excluded` 항목과 제외 비용이 기록됐다.

추적 형식:

```markdown
### A-003 견적 합계
- Knowledge: K-001, K-004
- Given: 수량 2, 단가 50,000원
- When: 견적을 저장한다
- Then: 공급가 100,000원, VAT 10,000원, 총액 110,000원이 보인다
```

## 5. PROVE와 LEARN

PROVE 실패는 코드 버그와 지식 실패를 분리한다.

- acceptance 구현이 틀림 → BUILD로
- Claim이 실제 업무와 다름 → Ledger를 `invalidated`, FRAME으로
- 중요한 예외가 새로 발견됨 → Domain Model·Ledger 갱신 후 사용자 재질문
- 출처 적용 범위가 틀림 → Router의 관할·overlay 재판정

LEARN에서는 프로젝트 사실을 전역 진리로 승격하지 않는다. 같은 계열에서 3회 이상
독립적으로 확인된 **발굴법**만 도메인 brief에 남기고, 고객별 값·정책·민감정보는
재사용하지 않는다.
