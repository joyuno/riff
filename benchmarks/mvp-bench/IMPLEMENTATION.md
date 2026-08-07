# 구현 파일 안내

| 확인할 기능 | 파일 |
|---|---|
| 익명 9회 배정, 폴더 준비, 채점, 봉인, 결과 집계 CLI | `bench.py` |
| CLI 단위 테스트 | `tests/test_bench.py` |
| browser adapter 출력 JSON 규격 | `grader/check-result.schema.json` |
| 실제 human pilot 운영 절차 | `protocol.md` |
| 예약 시스템 첫 요청·답변 카드 | `tasks/a-salon.md` |
| 리뷰 인사이트 첫 요청·답변 카드 | `tasks/b-reviews.md` |
| 견적 관리 첫 요청·답변 카드 | `tasks/c-quotes.md` |
| Synthetic preflight 전체 결과 | `preflight/RESULTS.md` |
| 과제별 세부 판정 | `preflight/results/*.md` |
| AI 페르소나가 만든 실제 Riff 앱 | `preflight/runs/*` |
| 전체 설계 | `../../docs/superpowers/specs/2026-08-05-mvp-bench-design.md` |
| 구현 계획·남은 browser gate | `../../docs/superpowers/plans/2026-08-06-human-pilot-harness.md` |

## 직접 검수

```bash
python3 -m unittest benchmarks/mvp-bench/tests/test_bench.py -v
python3 benchmarks/mvp-bench/bench.py --help
```

## 보기 쉬운 로컬 결과 폴더

`local-results/` 아래에 다음 9개 폴더가 생성된다.

```text
예약시스템_riff       예약시스템_gsd       예약시스템_gstack
리뷰인사이트_riff     리뷰인사이트_gsd     리뷰인사이트_gstack
견적관리_riff         견적관리_gsd         견적관리_gstack
```

현재 세 Riff 폴더에는 AI 페르소나 preflight 결과물이 복사돼 있다. 나머지 여섯 폴더는
`RUN.json`과 `README.md`로 `not-run` 상태를 명시한다. 빈 폴더를 결과처럼 표시하지 않는다.

다시 만들 때:

```bash
python3 benchmarks/mvp-bench/bench.py prepare --with-preflight-riff
```
