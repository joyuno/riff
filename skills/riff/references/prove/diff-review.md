# diff-review — 사이클당 1회 코드 정독

BUILD 완료 후 PROVE 내 서브스텝. 입력은 사이클 diff(`git diff <이전 사이클 커밋 앵커>..HEAD`)만.

## depth별 실행

| 프로파일 | 방식 |
|---|---|
| 단순 | 스킵 |
| 보통 | 메인 루프 인라인 self-review |
| 복잡 또는 core 태스크 포함 | `sonnet` 서브에이전트 독립 리뷰 (fresh-context) — codex 있으면 `/codex:review --wait --scope working-tree`가 대체 |

## 체크리스트

1. 삼켜진 에러·미실행 분기·검증 누락 엔드포인트·중복 로직
2. **스펙 준수 2문항**: FRAME이 요구하지 않은 것을 만들었나(스코프 크립)? FRAME이 요구한 것이 diff에 빠졌나?

## 산출

발견은 **Critical / Minor** 2단계만.
- Critical → 즉시 수정(기존 PROVE 실패 루프, ralph-loop 폴백 포함)
- Minor → 수정 없이 CANVAS [5]에 이연 기록(항체 머신 재사용)
결과를 CANVAS [4] 행에 기록.
