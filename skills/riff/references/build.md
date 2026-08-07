# BUILD 단계 상세 프로토콜

이 파일은 BUILD 단계 실행 시에만 읽는다. SKILL.md에 포함하지 않는다.

---

## BUILD-PLAN 산출 (태스크 보드)

TaskCreate로 태스크 생성 + CANVAS [3]에 요약 행. 태스크마다:
- **지식 근거**: core 태스크는 `A-NNN` acceptance와 연결된 `K-NNN`을 기록한다.
  Knowledge Ledger가 `candidate`·`blocked`·`assumption`인 항목은 태스크로 만들지 않고
  FRAME으로 돌아간다.
- **등급**: core(성공 기준 직결) / support(접점이나 대체 가능) / trivial(실패해도 즉시 재시도). 애매하면 상위 등급.
- **모델**: 등급 판정에 따라 `model-routing.md` 표대로 함께 기입. 순차 태스크는 `-`(= 메인 루프 인라인).
- **병렬 여부**: 동시 실행 예정인지 (이 값이 계약·스폰 조건의 술어). 아니면 기본값인 메인 루프 인라인 실행(아래 "실행 위치" 참고).
- **보안 플래그**: auth·결제·시크릿·유저 데이터 접촉 또는 >20파일 → DROP 전 sonnet 보안 패스 예약. CANVAS [3] 플래그 컬럼에 기록 — 세션 재시작에도 유지되는 SSOT.
- **도메인 태그**: 태스크명 앞에 도메인(FE/BE/ML/infra/기타) 태그 병기(예: `[BE] 주문 API 구현`) — LEARN 도메인 brief(같은 도메인 ≥3 누적)와 스폰 프롬프트 주입의 집계 근거.

SHAPE에서 `shape-synthesis.md`가 나왔다면 그 "BUILD로 전달하는 제약 조건"을 태스크 분해에 먼저 반영한다.

병렬 태스크가 하나라도 있으면, 아래 4가지 공유 대상으로 계약 필요 여부·유형을 판단한다(발행 여부는 "계약 조건" 참조):

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

**D. 병렬 에이전트 분업** → Architecture Contract 대상 (반드시 발행)
- 2개 이상의 에이전트를 동시에 스폰할 때 항상 발행
- 담는 내용: API 엔드포인트 소유권, 모듈 소유권, 확정된 기술 결정
- 에이전트 프롬프트에 "내 소유 영역 밖 파일은 수정 금지" 명시 필수

A/B/C/D 모두 비어있으면 계약 작성을 건너뛴다.

---

## 계약 조건 (v1.0 — 병렬 시에만)

계약 작성은 **태스크 보드에 잼 또는 병렬 스폰(동시 태스크 ≥2)이 계획된 경우에만**.
순차 빌드는 코드의 타입 선언이 계약이고 tsc가 lint — 계약서 생략.
병렬 시: 8종 계약(`contracts/`) + lint 통과 후 스폰(기존 규칙 유지). 계약 작성→lint 실패→재작성이 같은 계약서에 3회 반복되면 사용자에게 보고하고 해당 계약서를 보류한다. 계약→실행 복귀 3회 시 사용자 개입.

**기존 `_workspace/contracts/README.md` 먼저 확인** → 이미 존재하는 계약서 파악, 중복 생성 방지.

- 계약 형식·8종 템플릿(`type`/`behavior`/`visual`/`performance`/`security`/`constants`/`dependency`/`architecture`)과 lint 규칙: `contracts/contract-lint.md`. 없으면 오케스트레이터가 아래 최소 형식으로 직접 작성.

**계약서 저장 경로: `_workspace/contracts/{계약명}.md` (Cycle 번호 무관, 단일 경로)**

완료 후 `_workspace/contracts/README.md` 목록 갱신:
```markdown
| 계약서 | 유형 | 생성 Cycle | 소비자 | 상태 |
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

## 실행 위치 (라우팅 조건)

- 순차 태스크: **메인 루프 인라인** — 스폰 금지, 결과만 CANVAS [3] 상태 갱신.
- 병렬 태스크(≥2): 등급→모델 지정 스폰(`model-routing.md`). 동시 슬롯 3(웨이브 배리어 대신 완료 즉시 충원, trivial은 상한 미포함).
- 스폰된 에이전트 결과는 `_workspace/detail/` 파일 통신(대화 반환 금지) — 인라인 실행에는 미적용.

병렬 스폰 시 각 에이전트 프롬프트에 반드시 포함:

```
다음 계약서를 먼저 읽고 구현을 시작하라:
- _workspace/contracts/ui-stack.md (UI 있는 경우)
- _workspace/contracts/README.md (전체 목록 확인)
- _workspace/contracts/{관련 계약서명}.md

규칙:
- 계약서에 정의된 타입·상수·버전을 그대로 사용할 것
- 새로운 공유 값을 발명하지 말 것
- 계약서에 없는 공유 타입이 필요하면 구현 중단 후 보고할 것
- 결과를 _workspace/detail/{agent-name}-result.md에 저장할 것
- 대화로 결과를 반환하지 말고 파일 경로만 알릴 것
```

에이전트 완료 감지: 각 에이전트가 `_workspace/detail/{agent-name}-result.md`를 저장하면 CANVAS [3] 태스크 보드의 해당 행 상태를 ✅로 갱신. 모든 에이전트가 ✅이면 PROVE로 진행.

---

## 행위 체크 (core 필수)

core 태스크 산출물에 행위 계약 기반 **실행 가능 체크 ≥1개**(테스트 or assertion 스크립트) 포함.
작성 순서는 자유. 체크는 PROVE Tier 2가 누적 실행.
FRAME에서 동결된 acceptance check(`detail/acceptance/`)가 이 태스크의 행위를 이미 커버하면 그것으로 갈음하고 중복 작성하지 않는다. 커버되지 않는 행위만 추가 체크 작성 — 두 세트 모두 PROVE Tier 2가 누적 실행.
구현과 체크 이름에 같은 `A-NNN`을 기록해 Knowledge Ledger까지 역추적할 수 있게 한다.
