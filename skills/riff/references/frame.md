# FRAME — 조사와 질문으로 문제·성공 기준 확정

구 ASK + Riff 0(프로젝트 부팅) 통합. 세부 질문 자산은 `frame/` 하위(레이어·도메인·전문가) 사용.

## depth별 동작

| 프로파일 | 동작 |
|---|---|
| 단순 (신호 6+/8) | **스킵 가드 확인 후** 가정 선언 1줄 |
| 보통 (4~5/8) | 핵심 질문 2개: "이 프로젝트가 해결하는 문제는?" / "성공하면 어떤 모습인가?" |
| 복잡 (<4/8) | 5-Layer 인터뷰(`frame/layers.md`, `frame/enriched-layers.md`) + 도메인 분기(`frame/domains/`) |

## 근거 기반 요구사항 발굴 (Cycle 0)

인터뷰 답변을 받은 뒤 verdict 전에 `frame/domain-intelligence.md`의 Router로 조사법을
선택하고 `frame/discovery-research.md`를 실행한다. Exa로
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

## 웹앱 fast-path

신규 웹앱 + 보통 depth: 도메인 기본값 `web-development`, 핵심 12문항만 — Layer 1~5의 도메인 미분기 질문(`frame/layers.md`) + 도메인 결정(`frame/domains/web-development.md`),
완료 후 `_workspace/contracts/ui-stack.md` 확정(`ui-stack-guide.md`).

## 산출

CANVAS [1] 갱신(상한 30줄, 전문은 `detail/frame-*.md`와
`detail/domain-profile.md`, `detail/domain-model.md`, `detail/knowledge-ledger.md`,
`detail/discovery-research-cycle-N.md`) → verdict 게이트(`companions.md`) → SHAPE 또는 BUILD.
