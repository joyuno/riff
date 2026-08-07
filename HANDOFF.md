# riff v1.0.0 개발 세션 핸드오프 (2026-08-03)

> Claude Code 세션에서 Codex로 이어가기 위한 요약. 이 문서만 읽으면 전체 맥락 복원 가능.

## 1. 프로젝트 현재 상태 (가장 중요)

- **riff v1.0.0 전면 개편이 main에 병합 완료** — merge 커밋 `d1b563f` (merge --no-ff, feat/v1-revamp 34커밋, 74파일 +895/-1883)
- **origin에 미푸시 커밋 39개** — push는 사용자 확인 후에만 (원웨이도어 정책). 태그 `v1.0.0`·GitHub Release도 push와 함께 대기 중
- 워킹트리 클린, feat/v1-revamp 브랜치·워크트리는 병합 후 삭제됨
- 사용자가 로컬 마켓플레이스로 설치 완료(`/plugin marketplace add <로컬경로>` + install), **로컬 실사용 테스트 시작 단계 — 아직 피드백 없음**

## 2. 무엇을 만들었나 — riff v1.0 "질문이 캔버스를 채운다"

v0.3.1(Question-Driven, ASK→EXPLORE→BUILD→VERIFY→LEARN, 5스킬 분리)을 전면 개편:

| 축 | v1.0 결정 |
|---|---|
| 정체성 | Question-Driven 유지 + **Living CANVAS.md 단일 SSOT** ("이 문서만으로 재시작 가능") |
| 사이클 | **FRAME → SHAPE → BUILD → PROVE → LEARN** (재명명) |
| 깊이 | **adaptive depth**: 8신호 체크 → 단순/보통/복잡 3프로파일, 실패 시 에스컬레이션(건너뛴 스테이지 소급) |
| 구조 | 5스킬 → **단일 스킬**(SKILL.md 75줄 + references/ 12종, progressive disclosure) |
| 모델 | 티어 별칭만(opus/sonnet/haiku), **인라인 우선** — 스폰은 잼·병렬≥2·컨텍스트 압박 시만 |
| 이벤트 스테이지 | **DROP**(랜딩: 잼 랜딩·4택 메뉴·보안 딥스캔·카나리) · **TUNE**(조율: 스톡테이크·가드닝·항체 정리) — 사이클 핫패스 밖 |
| 용어 | 분신술→**잼(Jam)**, Riff N→Cycle N |
| 컴패니언 | ralph-loop·codex·**ecc plan-canvas**(verdict 게이트 브라우저 리뷰) — 전부 폴백 있음(없어도 전 기능 동작) |

핵심 메커니즘: 사이클 커밋 앵커(`cycle-N:` 커밋 = 되감기·diff·lint의 기준), canvas-lint(기계적 술어 5종), diff-review(사이클당 1회, Critical/Minor), red-green 항체 검증, verdict 게이트(approve/request-changes), 가정 선언(FRAME 스킵 가드), 보안 트리거 술어, 원웨이도어 게이트.

## 3. 여정 요약 (이 세션에서 한 일 순서대로)

1. **경쟁 리서치** (Exa, 232소스): superpowers v6·OMC v4.15·revfactory/harness·spec-driven 툴(Spec Kit/BMAD/OpenSpec/GSD)·컨텍스트 엔지니어링 2026 컨센서스 → `exa-results/riff-revamp-research-2026-07-30.md`
2. **브레인스토밍** (superpowers:brainstorming, 사용자가 결정 11건 선택) → 스펙 v1.0
3. **적대적 감사** (32 에이전트 워크플로): 25공격 → 11검증 → real 6건(행위검증 부재·diff-review 부재·canvas-lint 무정의·depth 자가판정 맹점·스폰 강제 속도 역전·계약 술어 오류) 전부 보완 → 스펙 v1.1
4. **ECC 벤치마킹** (github.com/affaan-m/ECC 클론 분석): plan-canvas 컴패니언·CANVAS 내 UPDATE RULE 자기기술·mermaid 규칙·verdict 형식화 채택
5. **루프 엔지니어링 갭 스캔** (3소스: Ralph 정론·플러그인 캐시·ECC): DROP·TUNE 이벤트 스테이지 + 보강 8건(커밋 앵커·시크릿 grep·보안 트리거·스펙 준수 리뷰·acceptance 동결·red-green·컨텍스트 체크·원웨이도어) → 스펙 v1.2
6. **구현** (superpowers:subagent-driven-development, 17태스크 × 구현자+스펙 리뷰어+품질 리뷰어): 13/17 태스크에서 리뷰가 실결함 검출·수정. 최종 통합 리뷰 NOT READY(B1: convergence.md 반쪽 마이그레이션) → 수정 → **READY** → main 병합

## 4. 저장소 구조 (병합 후)

```
skills/riff/
├─ SKILL.md                  # 진입점(75줄): 원칙·부트스트랩·depth 표·사이클 표·이벤트·가드·라우팅 포인터
└─ references/
    ├─ canvas-schema.md      # CANVAS 템플릿(UPDATE RULE·STATUS·[1]~[5])·운영규칙 4·마이그레이션
    ├─ frame.md + frame/     # 스킵 가드·가정 선언·acceptance 동결 + 구 인터뷰 자산(layers·domains·experts)
    ├─ shape-jam.md          # 잼: worktree 격리·opus·codex 폴백
    ├─ build.md              # 태스크 보드(등급·모델·병렬·플래그·도메인 태그)·계약 병렬 술어·인라인 우선·행위 체크
    ├─ contracts/            # 8종 템플릿 + contract-lint(병렬 시만 발동)
    ├─ prove/                # tier1~3 + canvas-lint(술어5) + diff-review + tier2 확장(behavior·acceptance·시크릿 grep -i)
    ├─ learn.md + learn/     # 9단계(항체 dedup→red-green→…→verdict 게이트→커밋 앵커→TUNE 판단), state.json SSOT {cycle,last_anchor}
    ├─ model-routing.md      # 라우팅 표 13행 + 컨텍스트 압박 승격 규칙
    ├─ companions.md         # 부트스트랩(ralph·codex·ecc plan-canvas)·폴백 매트릭스 4행·verdict 터미널 폴백 상세
    ├─ drop.md · tune.md     # 이벤트 스테이지
    ├─ rewind-protocol.md    # 0단계 git 앵커(증거 선캡처: git diff <anchor> 백업 → reset)·원거리 앵커 git log --grep
    └─ convergence.md · ui-stack-guide.md
hooks/  session-start-canvas.sh(STATUS 자동 주입, 상향 탐색) · riff-progress.sh(구 스키마 — 후속) · install.sh
benchmarks/  신규 픽스처: depth 모호 브리프 2종·canvas dirty-exit 재시작·rewind-anchor (+ground-truth JSON)
.claude-plugin/  v1.0.0 매니페스트 (키워드 10종)
README.md  전면 재작성(mermaid, 단일 설치, PNG 제거)
```

## 5. 핵심 문서 경로

- 스펙(v1.2, 최종): `docs/superpowers/specs/2026-07-31-riff-revamp-design.md`
- 적대적 감사: `docs/superpowers/specs/2026-07-31-riff-revamp-audit.md`
- 구현 계획(17태스크): `docs/superpowers/plans/2026-07-31-riff-v1-revamp.md`
- 경쟁 리서치: `exa-results/riff-revamp-research-2026-07-30.md`

## 6. 남은 작업 (후속 범위 — 문서에 명시됨)

1. **speed-tax 벤치마크 측정 스크립트** — medium 사이클 오버헤드 wall-clock ≤15% 검증 (benchmarks/README에 "계획됨" 표기만 존재)
2. **depth-reproducibility 자동 채점** — 픽스처는 있으나 반복 실행 일관성 측정 스크립트 없음 (현재 수동 채점)
3. **riff-progress.sh 훅 v1.0 스키마 연동** — 현재 구 `.riff/riff-log.json`을 읽음(v1.0은 `.riff/state.json`). v1.0 프로젝트에선 조용히 스킵됨. hooks/README에 호환 노트 있음
4. **English README** (배지에 "English coming soon")
5. **push + v1.0.0 태그 + GitHub Release** — 사용자 확인 대기
6. 사용자 로컬 테스트 피드백 반영 (테스트 관전 포인트: 모호 브리프에서 가정 선언 노출 여부, 세션 재시작 시 캔버스 복원)

## 7. 작업 규칙 (이 리포에서 지킬 것)

- 커밋은 conventional(feat/fix/docs/test/chore) + 한국어 요약. main 직접 커밋이 관례(단 대형 작업은 브랜치→merge --no-ff)
- **push·publish·배포는 사용자 확인 후에만**
- Codex 호출 시 `--model`/`--effort` 플래그 미지정(최신 기본값 사용) — 리포 자체 정책이기도 함
- `docs/superpowers/`·`exa-results/`는 역사 기록 — 용어 sweep 대상 제외
- 스펙 수정 시 반드시 관련 references 파일과 교차 정합 확인 (이번 세션 결함 대부분이 문서 간 불일치였음)

---

# 2026-08-07 추가 세션 (Claude Code)

## 완료

1. **Codex 세션 미커밋 산출물 정리** — 도메인 인텔리전스 전체(Router·Domain Model·Knowledge Ledger·K→A 게이트), MVP Bench 하네스, 프로젝트 지침 문서를 3커밋으로 분리 커밋. 테스트 3종 PASS.
2. **graphify 갱신** — Codex sandbox 권한 오류였던 것이 로컬에서는 정상. 1258 노드/1278 엣지.
3. **Playwright grader 차단 해제** — `grader/riff_preflight_playwright.py`가 로컬에서 실행되고 결과 JSON이 커밋본과 byte-identical 재현. `BROWSER-BLOCKER.md`에 재검증 기록 추가.
   - baseline(도메인 인텔리전스 이전): a-salon 4/8, b-reviews 6/8, c-quotes 5/9. **critical 실패 8건 전부 실무 요구사항 누락**(합계·상태 전이·지속성·인쇄)이지 코드 버그가 아님.
4. **FRAME 질문 체계 개편 (방향 2)** — 커밋 `958201e`. 아래 참조.

## FRAME 개편 내용

근거: 외부 2레포(addyosmani/agent-skills, mattpocock/skills) + riff 자체 감사 + 로컬 경쟁 스킬(OMC deep-interview·GSD·superpowers) + 실무 질문법 웹조사, 5방향 병렬 리서치.

진단한 근본 원인 4개:
- 질문이 방법론(JTBD·Mom Test)에서 연역돼 도메인 중립 → `domains/*.md`의 🔴 리스크가 참고표로만 존재
- 위험 Router가 인터뷰 **뒤에** 돌아 질문에 반영되지 않음
- 충분성 태그 14개에 돈·데이터 거처·되돌림·기존 절차가 없음 → 안 물어도 100%
- 되묻기 규칙이 Layer 2에만 존재 → 첫 답을 그대로 수용

적용:
- 게이트 태그 4종 신설, 미수집 시 충분성 60% 상한 (종료 조건 70%)
- Router 2패스 분리 — 1차(계열·overlay 판정)는 Layer 1~2 직후, 2차(Exa 조사)는 종전대로 인터뷰 뒤
- 질문 12개 교체, 순증 턴 **net −1** (Q7 폐지가 신규 2턴 상쇄)
- 프레임워크 이름 사용자 출력 전면 제거 (내부 설계 근거 블록은 유지)

검증 2라운드에서 blocking 2건(게이트 태그 선언만 하고 수집 질문 부재 → 60% 상한 때문에 종료 조건 도달 불가) 포함 9건 수정.

## 다음

- **human pilot** — K-ID → A-ID → 구현 → Playwright 전체 trace 검증. 브라우저 어댑터는 이제 실행 가능하나 성공/실패 fixture 대조는 미완(`plans/2026-08-06-human-pilot-harness.md` 미체크 4건).
- 개편된 질문으로 preflight 재실행 → baseline 대비 critical 실패 감소 측정 (개편 효과의 유일한 객관 증거)
- push + v1.x 태그 (사용자 확인 대기, 미푸시 9커밋)
