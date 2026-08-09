# FRAME — 조사와 질문으로 문제·성공 기준 확정

구 ASK + Riff 0(프로젝트 부팅) 통합. 세부 질문 자산은 `frame/` 하위(레이어·도메인·전문가) 사용.

## depth별 동작

| 프로파일 | 동작 |
|---|---|
| 단순 (신호 6+/8) | **스킵 가드 확인 후** 가정 선언 1줄 |
| 보통 (4~5/8) | 핵심 질문 2개: "이 프로젝트가 해결하는 문제는?" / "성공하면 어떤 모습인가?" |
| 복잡 (<4/8) | 5-Layer 인터뷰(`frame/layers.md`, `frame/enriched-layers.md`) + 도메인 분기(`frame/domains/`) |

## 근거 기반 요구사항 발굴 (Cycle 0)

Router는 두 번 돈다. Layer 1~2 답변 직후(기술 질문 시작 전)
`frame/domain-intelligence.md`의 Router를 **1차 실행**해 지식 계열과 위험 overlay만
판정하고, overlay가 있으면 해당 항목을 Layer 3~5의 기존 턴에 꼬리로 삽입한다(별도 턴 신설 금지).
**2차**는 종전대로 인터뷰 답변을 받은 뒤 verdict 전에 조사법을 선택하고
`frame/discovery-research.md`를 실행한다. Exa로
표준 업무 흐름·필드·상태·계산·예외를 조사하고, 현재 답변에 없는 항목은 기능으로
자동 추가하지 않고 사용자에게 재질문한다. 미확인 후보가 남아 있으면 acceptance를
동결하거나 FRAME을 승인하지 않는다.

## 스킵 가드 (필수)

FRAME 완전 스킵은 **CANVAS [1]에 성공 기준이 이미 존재할 때만** 허용.
없으면 스킵 대신 **가정 선언**: 채택한 해석 1줄 + 성공 기준 1줄을 [1]에 기록하고
STATUS에 `활성 가정: X — 아니면 지금 말해주세요`로 노출. verdict 게이트 대상.

## 수용 기준 규칙

1. **testability 가드**: 성공 기준·가정 선언은 "Tier 2 체크가 실행할 수 있는 관찰 가능한 행동"을 명시
   (예: "주문 생성 API가 201과 주문 id를 반환" O / "구현이 완료된다" X — PRD theater 금지).
2. **acceptance 동결**: verdict 승인 시점에 core급 작업의 수용 기준에서 실행 가능 체크 1~3개를 유도해
   `detail/acceptance/` 에 동결. 각 체크는 `A-NNN` ID와 Knowledge Ledger의 `K-NNN`을
   연결한다. Tier 2가 매 PROVE마다 실행. 단순 depth는 스킵.
3. **실물·기존 자산 우선**: 다루는 데이터나 코드가 이미 존재하면 설명 대신 실물을 본다.
   기존 프로젝트면 `_workspace/detail/*`와 소스를 먼저 읽고 거기서 확인된 사실은 묻지 않는다.
   사용자 업무 데이터면 실제 3줄을 요청한다. 실물을 받으면 필드·상태·계산 질문은 확인만 한다.
4. **닫힘 검사**: verdict 요청 전에 core-closure 7행이 전부 처분(`frozen`/`excluded`/`n/a`)됐는지
   확인한다(`frame/discovery-research.md` 처분 강제). **사용자가 요구한 것만 동결하면 반드시 빠진다** —
   새로고침 후 데이터 유지·건수가 늘었을 때 찾기·진행 중과 끝난 것의 구분은 아무도 먼저 말하지 않는다.
   미처분 행이 있으면 verdict을 요청하지 않는다.

## 웹앱 fast-path

신규 웹앱 + 보통 depth: 도메인 기본값 `web-development`, 핵심 11문항만 — Layer 1~5의 도메인 미분기 질문(`frame/layers.md`) + 도메인 결정(`frame/domains/web-development.md`),
완료 후 `_workspace/contracts/ui-stack.md` 확정(`ui-stack-guide.md`).

## 산출

CANVAS [1] 갱신(상한 30줄, 전문은 `detail/frame-*.md`와
`detail/domain-profile.md`, `detail/domain-model.md`, `detail/knowledge-ledger.md`,
`detail/discovery-research-cycle-N.md`) → verdict 게이트(`companions.md`) → SHAPE 또는 BUILD.
게이트 태그(`frame/termination-engine.md`)가 미수집이면 스킵 가드와 같은 방식으로
STATUS에 `미확인 위험: X`로 노출한다.
