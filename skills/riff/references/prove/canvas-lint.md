# canvas-lint — Tier 0 기계적 술어 5종

캔버스↔실상태 일치 검사. 전 depth 프로파일의 PROVE에 포함. 실행 위치: 메인 루프 인라인(grep/parse 수준).

| # | 술어 | 검사 방법 | 실패 시 조치 |
|---|---|---|---|
| 1 | 헤더 신선도 | CANVAS 헤더 `Cycle N` == `.riff/state.json`의 cycle && 최근 사이클 커밋 앵커 존재 (앵커 정의: `../learn.md`의 사이클 커밋 규칙) | 헤더 갱신 지시 |
| 2 | 태스크 보드 동기 | CANVAS [3] 행 상태 == TaskCreate 태스크 상태 (done↔completed, active↔in_progress) | 어긋난 행 갱신 |
| 3 | 링크 해소 | CANVAS 안 `detail/`·`contracts/` 링크가 실존 파일 | 죽은 링크 제거·복원 |
| 4 | 섹션 상한 | STATUS≤10줄, [1]≤30, [2]≤20행, [3]≤30, [4]≤5개, [5]≤15 | "압축 규칙 적용" — 초과분 detail/ 오프로드 |
| 5 | PROVE 기록 최신성 | [4] 최신 행의 cycle == 현재 cycle | [4] 갱신 지시 |

SessionStart 훅이 재개 시 어긋남을 감지하면 이 lint를 먼저 실행한 후 작업 재개.
