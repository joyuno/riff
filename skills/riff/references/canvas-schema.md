# CANVAS.md 스키마 — 유일 SSOT

원칙: **이 문서만으로 재시작 가능해야 한다.** 캔버스는 지도, `detail/`·`contracts/`는 영토.

## 템플릿 (Cycle 0에서 이 골격 그대로 생성)

```markdown
# CANVAS — <프로젝트명>
> 마지막 갱신: Cycle N · <스테이지> · <YYYY-MM-DD>

## UPDATE RULE
현재 사이클만 상세히. 스테이지 종료 시 해당 섹션 갱신. 섹션 상한 초과 시
오래된 내용은 detail/로 내리고 링크만 남긴다. 완료 사이클은 1줄 요약으로 접는다.
아키텍처·플로우·상태머신은 mermaid 블록으로 그린다.
이 문서의 쓰기는 메인 루프 단독(single-writer) — 서브에이전트는 detail/·contracts/·태스크 보드에만 기록.

## STATUS                                  <!-- 10줄 이내 -->
- 현재: Cycle N · <스테이지>
- 성공 기준 진행도: n/m
- depth 프로파일: 단순|보통|복잡 (신호 n/8)
- 도메인 프로파일: <계열 + 위험 overlay> · 지식 blocked n개
- 활성 가정: <가정 선언 요약 or 없음>
- 다음 액션: <1줄>

## [1] FRAME — 문제와 성공 기준             <!-- 상한 30줄 -->
질문→답 요약 · 핵심 Job · 페르소나 · 측정 가능한 성공 기준
Domain Profile·Model·Knowledge Ledger 링크와 confirmed/blocked/excluded 개수
(FRAME 스킵 시 가정 선언 기록 / 상세 → detail/frame-*.md)

## [2] SHAPE — 결정 로그                    <!-- 상한 20행 -->
| # | 결정 | 기각된 대안 | 근거 | cycle |
(잼 결과 = 요약 1줄 + detail/ 링크, 구조 결정은 mermaid 병기)

## [3] BUILD — 계약 + 태스크 보드           <!-- 상한 30줄 -->
활성 계약 링크 + 1줄 요약
| 태스크 | 근거 A/K ID | 등급 | 모델 | 병렬 | 플래그 | 상태 |

## [4] PROVE — 검증 게이트 기록             <!-- 최근 5개 -->
| cycle | tier | 결과 | diff-review | 에스컬레이션 |

## [5] LEARN — 항체 & 다음 사이클           <!-- 상한 15줄 -->
새 항체 포인터 · 확신도 · 다음 사이클 후보 · 도메인 brief 포인터
```

## 운영 규칙

1. **갱신(권고)**: 각 스테이지 종료 시 해당 섹션 갱신. 훅 강제 없음 — 미갱신은 canvas-lint(`prove/canvas-lint.md`)가 탐지.
2. **압축**: UPDATE RULE이 자기 기술 — 스킬 컨텍스트가 없는 세션에서도 규칙이 문서와 함께 이동.
3. **single-writer**: CANVAS.md 쓰기는 메인 루프 단독.
4. **verdict 게이트**: FRAME 산출(또는 가정 선언)과 사이클 종료는 approve/request-changes로 닫는다 — `ecc-plan-canvas` 있으면 브라우저(요소 앵커 주석+판정), 없으면 터미널 구조화 질문(`companions.md`).
5. **승인 후 수정 (in-place amend)**: 이미 approve된 항목이라도 사용자가 선택을 바꾸거나
   모순이 발견되면 **그 자리에서 고치고 계속한다.** 절차는 셋뿐이다 —
   ① 바뀐 선택을 해당 CANVAS 섹션에 반영, ② 그 선택에 연결된 `K-NNN`·`A-NNN`만 갱신
   (연결 없는 항목은 건드리지 않는다), ③ 영향 범위를 1줄로 알리고 재승인.
   **세션 분리·핸드오프·되감기는 이 경우의 답이 아니다** — 각각의 발동 조건은
   컨텍스트 압박, 그리고 PROVE 3회 연속 실패뿐이다(`../SKILL.md` 가드).
   기획 수정은 정상 흐름이지 사고가 아니다.

## 디렉토리

```
_workspace/
├─ CANVAS.md      ← 유일 SSOT
├─ contracts/     ← 계약서 (병렬 빌드 시에만 생성)
└─ detail/        ← domain-profile/model·knowledge-ledger·acceptance·검증 상세
.riff/            ← 항체·프로파일·세션 상태 (기존 유지, .gitignore: profile.md·state.json)
```

## v0.3.1 마이그레이션

첫 실행 시 `_workspace/riff-status.md` 또는 `riff-log.md` 감지 → CANVAS.md 1회 변환 제안:
status의 "현재 위치"→STATUS, riff-0 산출물 요약→[1], riff-log 학습→[5], 기존 riff-N/→detail/로 이동.
