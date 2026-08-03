# riff v1.0 릴리스 완성 설계

**작성일:** 2026-08-03  
**상태:** 승인됨

## 목표

riff v1.0의 남은 후속 작업을 완료한다. v1 상태 훅, speed-tax 측정,
depth 재현성 채점, 영문 문서, Codex 로컬 플러그인 설치와 실사용 검증을
마친 뒤 현재 `main`을 `v1.0.0`으로 배포한다.

## 범위와 순서

1. lifecycle hook을 선택적 SessionStart CANVAS 복원 하나로 단순화한다.
2. medium 사이클 speed-tax를 반복 측정하고 15% 예산을 판정한다.
3. depth 모호 브리프의 반복 실행 일관성을 자동 채점한다.
4. `README.en.md`를 추가하고 한국어 README와 상호 연결한다.
5. Codex 로컬 marketplace에 riff를 등록·설치한 뒤 실제 프로젝트로 검증한다.
6. 검증된 `main`을 push하고 annotated `v1.0.0` 태그와 GitHub Release를 만든다.

쇼츠 자동화 제품 구현은 riff 저장소 변경과 분리된 후속 프로젝트다. 다만 Codex
설치 후 첫 실사용 시나리오로 해당 프로젝트를 FRAME부터 시작하며, 그 과정에서
발견한 riff 자체의 결함은 이 릴리스에 반영한다.

## 1. Hook 최소화

플랫폼의 세션 메모리와 중복되는 진행 추적을 제거한다.

- `riff-progress.sh`와 Riff의 `SubagentStop` 등록을 제거한다.
- `session-start-canvas.sh`만 선택적으로 유지한다.
- 이 hook은 Claude Code 세션 시작 또는 재개 시 한 번만 실행한다.
- CANVAS가 있을 때 STATUS 최대 12줄만 읽으며 파일을 생성·수정하지 않는다.
- Codex 플러그인에서는 hook을 자동 등록하지 않고 자체 세션 컨텍스트를 사용한다.
- 설치기는 과거 Riff progress 등록을 제거하되 다른 hook은 보존한다.

셸 회귀 테스트는 설치 중 기존 설정 보존, progress 등록 제거, SessionStart 중복 방지를
검증한다.

## 2. speed-tax 측정

독립 실행기 `benchmarks/run-speed-tax.sh`를 추가한다.

- 동일한 medium fixture에 대해 baseline과 with-riff 명령을 각각 기본 3회 실행한다.
- 실행 명령은 환경변수로 주입하며 특정 모델이나 공급자에 고정하지 않는다.
- 초 단위가 아닌 밀리초 단위 wall-clock을 기록한다.
- 각 집합의 중앙값과 `(riff-baseline)/baseline*100`을 계산한다.
- 오버헤드가 15% 이하이면 pass, 초과하면 fail을 반환한다.
- 결과는 JSON과 사람이 읽을 수 있는 요약으로 저장한다.
- dry-run 및 미리 기록된 timing 입력을 지원해 모델 호출 없이 판정 로직을 검증한다.

## 3. depth 재현성 채점

`benchmarks/scoring/depth_reproducibility.py`와 실행 래퍼를 추가한다.

- `depth-ambiguous-notes`, `depth-ambiguous-tracker`를 기본 3회씩 평가한다.
- 각 출력에서 선택 프로파일, 가정 선언 또는 FRAME 질문, STATUS 활성 가정,
  금지 동작을 구조화해 채점한다.
- ground truth의 `expected_profile`, `allow_alternative`, `must_have`, `must_not`을
  판정 기준으로 사용한다.
- fixture별 통과율과 모든 반복에서 동일한 결정을 내렸는지 보고한다.
- 단 한 번이라도 금지 동작이 나타나면 해당 반복은 실패한다.
- 모델 실행 명령은 주입 가능하며 저장된 샘플 출력만으로도 채점 테스트를 실행한다.

## 4. Codex/Claude 동시 패키징과 문서

- 기존 `.claude-plugin/`은 변경 호환성을 유지한다.
- Codex가 요구하는 `.codex-plugin/plugin.json`을 추가한다.
- repo-local `.agents/plugins/marketplace.json`은 riff 루트를 local source로 노출한다.
- manifest 버전은 모두 `1.0.0`으로 일치시킨다.
- Codex CLI에서 marketplace 등록, plugin 설치, 설치 목록 확인을 수행한다.
- 로컬 캐시가 소스 변경을 놓치지 않도록 cachebuster/reinstall 절차를 따른다.
- `README.en.md`는 한국어 README의 구조와 기능 설명을 보존한 영문판으로 작성한다.
- 두 README의 첫 부분에 언어 전환 링크를 둔다.
- hooks README와 benchmarks README에서 v1 훅, 신규 실행기, Codex 설치를 설명한다.

## 5. Codex 실사용 검증

설치 후 새 대화에서 다음을 확인한다.

1. 직접 요청에서 riff skill이 활성화된다.
2. 간접적인 신규 제품 요청에서도 FRAME/adaptive-depth가 작동한다.
3. 관계없는 요청에서는 riff가 활성화되지 않는다.
4. 참조 파일 경로가 설치 캐시에서도 해석된다.
5. 세션 재시작 시 CANVAS STATUS가 복원된다.

첫 실제 시나리오는 “오픈소스 모델을 활용해 허가된 YouTube 인기 영상 소재를
재편집하고 Shorts 배포를 자동화하는 시스템”이다. riff는 FRAME에서 최소한 다음을
확정해야 BUILD로 진행할 수 있다.

- 영상별 재사용·편집·배포 권한과 라이선스 증거
- YouTube API와 대상 배포 플랫폼의 현재 정책 및 인증 방식
- 인기 영상 선정 데이터의 합법적·지원되는 취득 경로
- 원본 출처 표시, 중복 콘텐츠 방지, 인간 승인 단계
- 생성 모델, 저장소, 큐, 실패 재시도, 비용·처리시간 성공 기준

이 FRAME 결과는 별도 프로젝트의 `CANVAS.md`에 기록한다. 릴리스 저장소에는
실사용 중 발견된 riff 동작 결함만 반영한다.

## 6. 검증과 릴리스

릴리스 전 다음을 새로 실행한다.

- 모든 셸 회귀 테스트
- Python 채점 테스트
- benchmark dry-run
- plugin manifest 검증
- Markdown 링크와 내부 참조 검사
- `git diff --check` 및 워킹트리 검토

검증 후 conventional commit을 만들고 `main`을 origin에 push한다. 최종 커밋에
annotated `v1.0.0` 태그를 만들고 push한 뒤, 변경 요약과 설치·검증 방법을 포함한
GitHub Release를 생성한다. 기존 태그나 릴리스가 발견되면 덮어쓰지 않고 중단한다.

## 비목표

- 기존 v0.3.1 진행률·수렴 hook 호환 또는 `riff-log.json` 자동 마이그레이션
- `state.json`에 장기 에이전트 통계 저장
- 특정 Claude/OpenAI 모델 ID를 벤치마크 코드에 고정
- 권한이 확인되지 않은 영상 다운로드 또는 재업로드
- riff 저장소 내부에 쇼츠 자동화 제품 코드를 혼합
