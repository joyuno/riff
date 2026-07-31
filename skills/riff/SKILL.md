---
name: riff
description: "신규 프로젝트·앱·MVP를 처음부터 만드는 AI-Native 루프. 질문이 캔버스를 채운다 — FRAME → SHAPE → BUILD → PROVE → LEARN을 빠르게 반복하며 매 사이클마다 작동하는 결과물과 살아있는 CANVAS.md를 남긴다. 'riff로 시작', '프로젝트 시작', '새 프로젝트', '앱 만들어줘', 'MVP', '프로토타입', '이거 만들어줘' 시 사용. 단순 버그 수정·작은 기능 추가에는 사용하지 않는다."
---

# Riff — 질문이 캔버스를 채운다

## 핵심 원칙

- 한 번에 잘 만들지 않는다. 빠르게 많이 시도한다.
- **CANVAS.md만으로 재시작 가능해야 한다** — 캔버스는 지도, detail/·contracts/는 영토.
- 질문은 트레이드오프가 있을 때만. 실패는 비용이 아니라 학습이다.
- 사이클 핫패스에 세리머니를 더하지 않는다(오버헤드 ≤15% — `benchmarks/` speed-tax로 측정). 무거운 일은 이벤트 스테이지(DROP·TUNE)로.

## Bootstrap (첫 호출 1회)

`references/companions.md` — ralph-loop·codex·ecc plan-canvas 점검, Install/Skip/Skip all.
가드: `_workspace/.riff-bootstrap-done` 또는 `.riff-bootstrap-skip-all` 존재 시 스킵.

## 캔버스

`references/canvas-schema.md`의 템플릿으로 `_workspace/CANVAS.md` 생성·유지.
v0.3.1 잔재(`riff-status.md` 등) 감지 시 1회 변환 제안. 쓰기는 메인 루프 단독.

## 세션 재개

SessionStart 훅이 CANVAS.md 감지 → STATUS 자동 로드. 어긋남 감지 시 canvas-lint(`references/prove/canvas-lint.md`) 먼저.
훅 미설치 폴백: CANVAS.md 존재 확인 → STATUS부터 재개. 없으면 v0.3.1 잔재(`riff-status.md` 등) 확인 → 있으면 변환 제안(`references/canvas-schema.md` 마이그레이션 절), 없으면 Cycle 0.

## Cycle 0 (프로젝트 부팅)

FRAME 복잡 프로파일로 시작(`references/frame.md`) → CANVAS 생성 → UI 있으면 `contracts/ui-stack.md` 확정(`references/ui-stack-guide.md`).

## depth 판정 (사이클 시작 시 1회)

8신호 체크(가중치 없이 개수만):
상향 — 같은 패턴이 이전 사이클에서 검증 / 요구사항 명시적 / 유사 도메인·표준 패턴 존재 / 성공 기준 측정 가능
하향 — 요구 모호하지 않음 / 같은 영역 되감기 없음 / 외부 의존 낮음 / 트레이드오프 분석 완료

| 체크 수 | 프로파일 | 동작 |
|---|---|---|
| 6+/8 | 단순 | FRAME 스킵 가드 → 가정 선언, SHAPE 스킵, PROVE-lite(Tier 0+2) |
| 4~5/8 | 보통 | FRAME 2문항, PROVE Tier 0~2 + 인라인 diff-review |
| <4/8 | 복잡 | 풀 스테이지 + 잼 + Tier 0~3 + 독립 diff-review |

오버라이드: 사용자가 "가볍게"/"꼼꼼하게"로 강제 지정 가능.

## 사이클: FRAME → SHAPE → BUILD → PROVE → LEARN

| 스테이지 | 요약 | 세부 |
|---|---|---|
| FRAME | 질문·가정 선언으로 문제/성공 기준 확정, verdict 게이트 | `references/frame.md` |
| SHAPE | 결정 로그. 트레이드오프 불명확 시 잼(worktree 격리) | `references/shape-jam.md` |
| BUILD | 태스크 보드(등급·병렬·보안 플래그·도메인 태그) → 병렬 시만 계약 → 구현 | `references/build.md` |
| PROVE | Tier 0~3 + canvas-lint + diff-review | `references/prove/` |
| LEARN | 항체(red-green)·프로파일·도메인 brief·verdict 게이트·**사이클 커밋 앵커** | `references/learn.md` |

## 이벤트 스테이지 (사이클 밖)

- **DROP** — 잼 병합·성공 기준 달성(판정: `references/convergence.md`)·사용자 요청 시: 잼 랜딩·랜딩 메뉴·worktree 정리·보안 딥스캔·카나리 (`references/drop.md`)
- **TUNE** — 3~5사이클·rewind 후·no-progress 시: 스톡테이크·가드닝·항체 정리·컨텍스트 감사 (`references/tune.md`)

## 가드 (전 스테이지 공통)

- **에스컬레이션**: PROVE 2회 실패 → 실패 유형 진단(기계적→재시도 / 설계→SHAPE 소급). 모호 발견 → FRAME 재진입. 3회 연속 실패 → 되감기(`references/rewind-protocol.md`).
- **원웨이도어**: push·publish·파괴적 마이그레이션·배포 전 사용자 확인 (depth 무관).
- **컨텍스트 압박**: 스테이지 경계마다 확인 — 임계 초과 시 태스크 마무리·캔버스 갱신 후 세션 분리 권고.

## 모델 라우팅

`references/model-routing.md` — 스폰은 잼·병렬 태스크 ≥2·컨텍스트 압박일 때만. 그 외 인라인.

## OMC 공존

OMC 활성 시 Riff 사이클 중 OMC 모드·에이전트·스킬을 호출하지 않는다.
