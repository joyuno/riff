# riff v1.0 전면 개편 설계 — "질문이 캔버스를 채운다"

- 날짜: 2026-07-31
- 상태: 사용자 승인 완료 (브레인스토밍 7개 결정 + 설계 6개 섹션)
- 근거 리서치: `exa-results/riff-revamp-research-2026-07-30.md` (232 소스, 5개 리서치 에이전트)

## 1. 배경과 목표

riff v0.3.1은 Question-Driven Development 플러그인으로 interview-first·계약 교환·매 사이클 검증을 선취했으나, 2026년 중반 기준 다음 갭이 확인됐다:

1. **Living Canvas 부재** — 산출물이 `riff-status.md`/`riff-log.md`/`riff-N/`으로 파편화되어 "이 문서만으로 재시작"(ExecPlan 패턴)이 불가능.
2. **Adaptive depth 부재** — 질문 예산은 있으나 스테이지 자체가 고정 5단계. 작은 작업에도 동일한 세리머니.
3. **플랫폼 신기능 미활용** — TaskCreate 공유 작업목록, worktree 격리 서브에이전트, SessionStart 훅.
4. **모델 라우팅 부재** — 모든 작업을 메인 모델이 수행, 비용·속도 비효율.
5. **드리프트 관리 부재** — 문서와 구현이 어긋나도 탐지 장치 없음.

**목표**: "완성도 높지만 빠른 프로토타이핑" — superpowers(무거운 규율)와 GSD류 경량 툴(기획 없음) 사이의 중간 지점을 현대적 구조로 재구축한다.

## 2. 확정 결정 요약

| # | 결정 사항 | 선택 |
|---|---|---|
| 1 | 정체성 | **질문이 캔버스를 채운다** — Question-Driven 유지 + Living Canvas SSOT |
| 2 | 캔버스 구조 | **단일 CANVAS.md = 지도**, 상세는 `detail/` 오프로드 + 링크 |
| 3 | 깊이 조절 | **자동 감지 + 실패 에스컬레이션** (신호 체크리스트 기반) |
| 4 | 모듈 구조 | **단일 플러그인 통합** — 4개 모듈을 references/로 흡수 |
| 5 | 스테이지 | **FRAME → SHAPE → BUILD → PROVE → LEARN** (5단계 재명명) |
| 6 | 모델 라우팅 | **태스크 등급표 + 티어 별칭 + 사용자 오버라이드** |
| 7 | 플랫폼 통합 | **네이티브 우선 + 컴패니언 폴백** (훅 강제 게이트는 제외 — 권고만) |
| 8 | 용어 | **"분신술" → "잼(Jam)"** 전면 교체 (음악 은유로 브랜드 통일) |

## 3. CANVAS.md 스키마

원칙: **이 문서만으로 재시작 가능해야 한다.**

```markdown
# CANVAS — <프로젝트명>
> 마지막 갱신: Cycle N · <스테이지> · <날짜>

## STATUS                                  (항상 최상단, 10줄 이내)
현재 위치 · 성공 기준 진행도 · depth 프로파일(신호 n/8) · 다음 액션 1줄

## [1] FRAME — 문제와 성공 기준             (상한 30줄)
질문→답 요약, 핵심 Job, 페르소나 1줄씩, 측정 가능한 성공 기준
상세 인터뷰 전문 → detail/frame-*.md 링크

## [2] SHAPE — 결정 로그                    (상한 20행 테이블)
| # | 결정 | 기각된 대안 | 근거 | cycle |
잼(Jam) 결과는 요약 1줄 + detail/ 링크

## [3] BUILD — 계약 + 태스크 보드           (상한 30줄)
활성 계약 링크 + 1줄 요약 / 태스크: 등급(core·support·trivial)과 담당 모델 명시

## [4] PROVE — 검증 게이트 기록             (최근 5개만)
tier · 통과/실패 · 에스컬레이션 발동 여부

## [5] LEARN — 항체 & 다음 사이클           (상한 15줄)
새 항체 포인터 · 확신도 · 다음 사이클 후보
```

**운영 규칙**
1. **갱신 규칙(권고)**: 각 스테이지 종료 시 해당 섹션 갱신. 훅으로 강제하지 않는다(사용자 결정). 미갱신은 PROVE의 canvas-lint가 탐지.
2. **압축 규칙**: 섹션 상한 초과 시 오래된 내용을 `detail/`로 내리고 링크만 남김. 완료 사이클은 1줄 요약으로 접음.
3. **디렉토리 재편**: `riff-status.md` + `riff-log.md` + `riff-N/` → `CANVAS.md` + `detail/`. `contracts/`와 `.riff/`(memory)는 유지.

```
프로젝트루트/
├── _workspace/
│   ├── CANVAS.md            ← 유일 SSOT (지도)
│   ├── contracts/           ← 8종 계약서 (영토)
│   └── detail/              ← 인터뷰 전문·잼 결과·검증 상세 (영토)
└── .riff/                   ← 항체·프로파일·세션 상태 (기존 유지)
```

## 4. 스테이지 설계 + Adaptive Depth

| 스테이지 | 역할 | 얕을 때 | 깊을 때 |
|---|---|---|---|
| **FRAME** | 질문으로 문제·성공 기준 확정 (구 ASK + Riff 0 통합) | 스킵 또는 핵심 2문항 | 5-Layer 인터뷰 + 도메인 분기 |
| **SHAPE** | 트레이드오프 결정, 결정 로그 기록 (구 EXPLORE 재편) | 스킵 (결정 로그 1행만) | 잼 2-3방향 동시 탐색 + codex 대립 검토 |
| **BUILD** | 계약 작성 → 태스크 보드 → 구현 | 계약 생략(공유 경계 없을 때) | 8종 계약 + lint 게이트 |
| **PROVE** | 검증 게이트 (구 VERIFY) | Tier 0+2만 (lint+빌드) | Tier 0~3 풀 + Live Browser |
| **LEARN** | 항체·프로파일·캔버스 갱신 | 캔버스 [5]만 갱신 | 항체 생성 + 세션 분리 판단 |

**깊이 결정**: 사이클 시작 시 1회, 기존 8신호 체크리스트(가중치 없는 체크 개수 방식 — LLM 재현성)로 판정.
- 신호 6+/8 → 단순: FRAME·SHAPE 스킵, PROVE-lite
- 신호 4~5/8 → 보통: FRAME 2문항, PROVE Tier 0~2
- 신호 <4/8 → 복잡: 풀 스테이지 + 잼

**에스컬레이션 트리거** (건너뛴 스테이지 소급 발동):
- PROVE 2회 실패 → SHAPE 소급 (잼 발동)
- 구현 중 요구 모호 발견 → FRAME 재진입 (질문 1~3개만)
- 같은 계약 3회 수정 → 계약 재설계 + 사용자 개입 요청
- 3회 초과 → 되감기(rewind) — 기존 프로토콜 유지

**오버라이드 키워드**: 사용자가 "가볍게"/"꼼꼼하게" 등으로 depth 판정을 무시하고 강제 지정 가능.

**canvas-lint (Tier 0 신설)**: 캔버스 STATUS·태스크 보드와 실제 구현 상태의 불일치를 매 PROVE마다 검사. 스펙 드리프트(경쟁 툴 공통 약점)를 게이트로 차단.

## 5. 모델 라우팅

원칙: ① 티어 별칭(`opus`/`sonnet`/`haiku`)만 사용 — 버전 고정 금지, 자동 최신화. ② 메인 루프는 권장 안내, 서브에이전트는 강제 지정.

| 위치 | 작업 | 모델 | 방식 |
|---|---|---|---|
| FRAME·SHAPE | 질문 설계·트레이드오프 판단 | Fable 5/Opus 5 권장 | 메인 루프 — 다른 모델이면 STATUS에 권장 안내 |
| SHAPE 잼 | 대안 동시 탐색 | `opus` | 서브에이전트 지정 |
| BUILD core | 핵심 비즈니스 로직·아키텍처 | `opus` | 태스크 등급 → 스폰 시 지정 |
| BUILD support | 보조 기능·UI·CRUD | `sonnet` | 〃 |
| BUILD trivial | 설정·보일러플레이트·단순 수정 | `haiku` | 〃 |
| PROVE Tier 0~2 | 기계적 검증 | `haiku` | 서브에이전트 지정 |
| PROVE Tier 3 | 유령 사용자·파괴자 (판단형) | `sonnet` | 〃 |
| PROVE 실패 분석 | 원인 진단·에스컬레이션 판단 | 메인 루프 | — |
| LEARN | 항체·프로파일 기록 | `haiku` | 서브에이전트 지정 |

**등급 판정**: BUILD-PLAN에서 태스크 보드 생성 시 태스크마다 등급 명시 → 캔버스 [3]에 노출 → 스폰 전 사용자 오버라이드 가능. 기준: 성공 기준 직결(core) / 사용자 접점이나 대체 가능(support) / 실패해도 즉시 재시도 가능(trivial). 애매하면 상위 등급.

## 6. 플랫폼 통합

**네이티브 편입 3종:**
1. **TaskCreate 공유 작업목록** = BUILD 태스크 보드의 실체. 등급·모델을 태스크 메타데이터로 저장, 캔버스 [3]은 요약 뷰.
2. **worktree 격리 서브에이전트** = 잼의 실행 방식. 대안별 격리 워크트리에서 동시 시도, 미채택 방향은 워크트리째 폐기(되감기 단순화).
3. **SessionStart 훅**: CANVAS.md 감지 시 STATUS 자동 로드 (세션 재개 자동화). 기존 SubagentStop 진행률 훅 유지. **Stop 훅 강제 게이트는 도입하지 않는다** (사용자 결정 — 부담).

**컴패니언 폴백 매트릭스** (있으면 강화, 없으면 네이티브 폴백 — 컴패니언 없이도 전 기능 동작):

| 기능 | ralph-loop/codex 있으면 | 없으면 (네이티브 폴백) |
|---|---|---|
| PROVE 실패 루프 | `ralph-loop --completion-promise` | 자체 재시도 2회 → 에스컬레이션 |
| SHAPE 대립 검토 | `codex adversarial-review` 1회 | 잼에 반대 관점 에이전트 1개 추가 |
| 대형 변경 교차 검증 | `codex review` | 메인 모델 self-review 체크리스트 |

부트스트랩: 유지하되 간소화 — 첫 호출 시 1회 제안, Skip해도 기능 손실 없음. Codex 모델 정책(`--model` 미지정) 유지.

## 7. 플러그인 구조 & 마이그레이션

```
riff/  (v1.0.0)
├─ .claude-plugin/           ← 단일 플러그인으로 정리
├─ skills/riff/
│   ├─ SKILL.md              ← 코어 루프 + depth 신호 + 라우팅 요약만 (얇게)
│   └─ references/           ← 구 4모듈 흡수 (progressive disclosure)
│       ├─ canvas-schema.md
│       ├─ frame.md          ← 구 riff-interview (layers·domains·experts)
│       ├─ shape-jam.md      ← 구 explore-protocol + 잼 프로토콜
│       ├─ build.md          ← 구 build-protocol + 태스크 등급
│       ├─ contracts/        ← 구 riff-contracts (8종 템플릿 + lint)
│       ├─ prove/            ← 구 riff-qa (tier0~3 + canvas-lint 신설)
│       ├─ learn.md          ← 구 riff-memory (항체·프로파일 스키마)
│       ├─ model-routing.md
│       ├─ companions.md     ← 폴백 매트릭스 + 부트스트랩
│       └─ rewind.md · convergence.md
├─ hooks/                    ← session-start-canvas 추가, riff-progress 유지
├─ benchmarks/               ← 기존 픽스처 유지 + 신규 2종
└─ README.md                 ← 전면 재작성
```

**마이그레이션:**
- v0.3.1 → **v1.0.0** (breaking: 모듈 4종 플러그인 제거, `_workspace/` 구조 변경)
- 기존 프로젝트: 첫 실행 시 `riff-status.md`/`riff-log.md` 감지 → `CANVAS.md` 변환 1회 제안
- 구 모듈 4종: 마켓플레이스에서 deprecated 표시
- 용어 교체: "분신술" → "잼(Jam)" — README·SKILL.md·references·다이어그램 전체
- README·다이어그램(`docs/riff_cycle.png`, `docs/architecture.png`) 재생성

## 8. 검증 계획

1. **기존 벤치마크 픽스처 유지** (interview·boundary·immunity·live-app) — 개편 전후 회귀 없음 확인
2. **canvas-restart (신설)**: 세션을 끊고 CANVAS.md만으로 재개했을 때 프로젝트 상태 복원 정확도
3. **depth-reproducibility (신설)**: 동일 픽스처에 대한 depth 판정(스킵 여부)의 재현 일관성

## 9. 용어집

| 용어 | 의미 |
|---|---|
| **캔버스(Canvas)** | 프로젝트의 유일 SSOT 문서 (`_workspace/CANVAS.md`) |
| **잼(Jam)** | 여러 에이전트가 격리 워크트리에서 대안을 동시 탐색 (구 "분신술") |
| **사이클(Cycle)** | FRAME→SHAPE→BUILD→PROVE→LEARN 1회전 (구 "Riff N") |
| **depth 프로파일** | 신호 체크 결과에 따른 스테이지별 깊이 (단순/보통/복잡) |
| **에스컬레이션** | 실패·모호 신호 시 건너뛴 스테이지를 소급 발동 |
| **항체(Antibody)** | 한번 겪은 실수의 재발 방지 체크리스트 (기존 유지) |
