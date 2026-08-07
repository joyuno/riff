# MVP Bench Human Pilot Protocol

## 공개 조건

- 참가자: 익명의 비개발 창업자 1명
- 실행: Riff, GSD, gstack 각 3회, 총 9회
- 환경: 같은 Codex 모델과 starter, 각 harness 설치 상태의 검색 도구, 새 thread와 새 run 디렉터리
- 제한: 인위적 시간 제한 없음, 참가자의 코드·명령·원인 분석 개입 금지
- 공개: AI preflight와 human pilot 분리, 유지보수자 운영·비독립 연구 명시

## 사전 준비

1. `tasks/`와 grader 기준을 커밋하고 해시를 기록한다.
2. 공식 runner 환경에서 브라우저 adapter의 성공·실패 fixture를 통과시킨다.
3. 다음 명령으로 익명 9회 배정을 한 번만 만든다.

```bash
python3 benchmarks/mvp-bench/bench.py init --seed '<sealed-random-seed>'
```

`pilot/assignments.json`은 채점 완료 전 비공개로 둔다. 각 run의 공개 `metadata.json`에는
harness가 들어가지 않는다.

## 실행

1. 운영자는 배정된 harness 하나만 설치한 새 thread를 연다.
2. 해당 task의 `첫 요청`만 입력한다.
3. 참가자는 질문받은 내용만 `참가자 답변 카드`에서 답한다.
4. 시작·종료 시각, 검색 도구·검색 횟수, 추가 요구 질문·답변, 기술 개입, 중단 사유를 기록한다.
5. 완료 선언 후 운영자는 코드 수정 없이 hidden browser adapter를 실행한다.
6. adapter는 `checks.json`만 만든다. 각 항목은 `id`, `critical`, `passed`, `evidence`를 가진다.
7. Riff run은 Domain Profile·Model·Knowledge Ledger와 core acceptance의 K/A 추적을 함께
   봉인한다. 이 파일이 없거나 blocked 지식으로 구현했으면 discovery 실패로 기록한다.

## 채점과 봉인

```bash
python3 benchmarks/mvp-bench/bench.py grade benchmarks/mvp-bench/runs/<run-id>
python3 benchmarks/mvp-bench/bench.py seal benchmarks/mvp-bench/runs/<run-id>
python3 benchmarks/mvp-bench/bench.py verify benchmarks/mvp-bench/runs/<run-id>
```

성공은 critical 실패 0개, 전체 90% 이상, `persistence`와 `research-evidence` 통과를 모두
요구한다. 도구의 완료 선언이나 자체 테스트 통과만으로 성공 처리하지 않는다.

9회 종료 후에만 배정을 결합해 결과를 계산한다.

```bash
python3 benchmarks/mvp-bench/bench.py report
```

원자료, 실패, 중앙값을 공개한다. 단일 가중 종합점수는 만들지 않는다.

## 검색 비대칭 공개

이 파일럿은 검색 능력을 제거한 harness-only 실험이 아니라 설치 직후 제품 전체를
비교한다. Riff는 플러그인에 번들된 Exa를 사용하며, GSD와 gstack에는 Exa를 별도
설치하지 않는다. 각 run은 실제 사용한 검색 도구와 출처를 공개한다. 검색으로 발견한
후보는 사용자가 확인해야만 acceptance로 인정하며, 무승인 기능 추가는 별도 실패로
기록한다.

## 아직 실행하면 안 되는 조건

`grader/adapters/`의 세 browser adapter와 성공·실패 fixture가 없거나 390px·새로고침 검증이
통과하지 않으면 human pilot을 시작하지 않는다.
