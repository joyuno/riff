# BUILD 단계 상세 프로토콜

이 파일은 BUILD 단계 실행 시에만 읽는다. SKILL.md에 포함하지 않는다.

---

## 단계 1: PLAN — 경계면 설계 (에이전트 스폰 전)

오케스트레이터가 직접 수행:

1. 이번 Pulse에서 만들 파일 목록 작성
2. **기존 `_workspace/contracts/README.md` 먼저 확인** → 이미 존재하는 계약서 파악, 중복 생성 방지
3. 파일 간 import/의존 관계 파악
4. 아래 3가지 공유 대상 목록화:

**A. 공유 타입/인터페이스** → Type/Visual Contract 대상
- 파일 A가 파일 B의 클래스·타입을 import하거나 파라미터로 받을 때
- 위젯·컴포넌트가 외부에서 데이터 객체를 props/생성자로 전달받을 때

**B. 공유 상수/검증 규칙** → Constants Contract 대상
- 프론트엔드 validation과 백엔드 validator가 동시에 구현될 때 (반드시 발행)
- 같은 수치(최소 길이, Rate Limit, 만료 시간)가 2개 이상 레이어에서 사용될 때

**C. 라이브러리·설정 공유** → Dependency Contract 대상
- `requirements.txt`, `package.json`, `docker-compose.yml` 중 2개 이상 동시 작성 시 (반드시 발행)
- 암호화 라이브러리(`bcrypt`, `passlib`, `jwt`) 포함 시
- config 파일과 docker-compose가 동일한 DB 자격증명 참조 시

A/B/C 목록이 모두 비어있으면 단계 2를 건너뛴다.

---

## 단계 2: CONTRACT — 계약서 선(先) 작성

**A/B/C 중 하나라도 있으면 계약서를 먼저 작성한다. 계약서 없이 에이전트 스폰 금지.**

- `pulse-contracts` 모듈 있으면 해당 스킬 호출
- 없으면 오케스트레이터가 직접 최소 형식으로 작성

**계약서 저장 경로: `_workspace/contracts/{계약명}.md` (Pulse 번호 무관, 단일 경로)**

완료 후 `_workspace/contracts/README.md` 목록 갱신:
```markdown
| 계약서 | 유형 | 생성 Pulse | 소비자 | 상태 |
|--------|------|-----------|--------|------|
| auth-constants.md | constants | 1 | frontend, backend | 활성 |
```

최소 계약서 형식:
```
# [계약명]

## 정의
[타입·상수·버전 정의]

## 소유 관계
- 정의: [파일 경로]
- 사용: [파일 경로 목록]

## 불변 규칙
- 에이전트가 계약서와 다른 값을 발명하는 것 금지
- 변경 필요 시 계약서 먼저 업데이트 후 코드 수정
```

---

## 단계 3: EXECUTE — 에이전트 스폰 및 구현

계약서 확정 후 에이전트 스폰. 각 에이전트 프롬프트에 반드시 포함:

```
다음 계약서를 먼저 읽고 구현을 시작하라:
- _workspace/contracts/ui-stack.md (UI 있는 경우)
- _workspace/contracts/README.md (전체 목록 확인)
- _workspace/contracts/{관련 계약서명}.md

규칙:
- 계약서에 정의된 타입·상수·버전을 그대로 사용할 것
- 새로운 공유 값을 발명하지 말 것
- 계약서에 없는 공유 타입이 필요하면 구현 중단 후 보고할 것
- 결과를 _workspace/pulse-N/{agent-name}-result.md에 저장할 것
- 대화로 결과를 반환하지 말고 파일 경로만 알릴 것
```
