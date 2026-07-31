# riff 개편 리서치 — 경쟁 툴 분석 + 컨텍스트 엔지니어링 동향 (2026-07-30)

> Exa 서브에이전트 5개 × 총 232 소스 리뷰. 수치(스타 수 등)는 서브에이전트 보고 기준이며 과장 가능성이 있어 정확 수치는 인용 전 재검증 권장. 정성적 구조 분석이 본 문서의 핵심.

## 1. superpowers (obra/superpowers) — v6.1.1, 2026-07

- **구조**: 14개 조합형 스킬. Testing/Debugging(TDD, systematic-debugging, verification-before-completion), Collaboration(brainstorming, writing-plans, executing-plans, subagent-driven-development, worktrees, code-review, branch finishing), Meta(using-superpowers, writing-skills).
- **7단계 파이프라인**: Brainstorming(소크라테스 질문 → 200-300단어 섹션별 승인 설계문서) → Worktree 격리 → Writing Plans(태스크당 2-5분 스코프, 정확한 파일 경로+검증 단계) → Subagent-Driven Development(태스크당 fresh 서브에이전트 + 2단계 리뷰) → TDD(RED-GREEN-REFACTOR 강제) → Code Review(심각도 등급) → Branch Finishing.
- **2026 변화**: v5(3월) 인라인 self-review로 서브에이전트 리뷰 대체(~3배 빠름). v5.1(5월) 레거시 슬래시 커맨드 제거. v6(6월) "Massively Parallel Procrastination" — wall-clock 50%↓, 토큰 60%↓, 리뷰 패킷 사전 구성, 태스크별 모델 선택 가이드. 평가 스위트(superpowers-evals)로 하네스 횡단 검증.
- **평판**: 설계 강제·엣지케이스 발굴·다중파일 일관성 호평. 불만: trivial 작업 토큰 과다, 멀티 서브에이전트 인지 부담, 최신 모델(Fable 5)에선 풀 하네스가 과하다는 의견 — "Fable에선 brainstorm+review만 얇게, Opus/Sonnet에선 풀 플러그인" 컨센서스 형성 중.
- **핵심 시사점**: 탐색적 프로토타이핑에는 부적합하다고 스스로 인정되는 포지션 — riff가 노릴 공백.

## 2. oh-my-claudecode (OMC) — v4.15.7, 2026-07-23

- **구조**: Hooks + Skills(31종) + Agents(19종, Haiku/Sonnet/Opus 티어 라우팅) + State(.omc/) 4축. 실행 모드 6종: Team(plan→PRD→exec→verify→fix 5단계, 네이티브 Agent Teams), Autopilot, Ralph(완료까지 지속 루프), Ultrawork(최대 병렬), UltraQA(품질 게이트까지 진단/수정 반복), omc team(tmux로 Codex/Gemini/Antigravity/Grok 워커).
- **컨텍스트 엔지니어링**: .omc/ 상태 디렉토리(세션 로그·PRD·체크포인트·학습 패턴), HUD 상태줄(토큰 사용률 ±5%), 스킬 학습(세션에서 패턴 추출), 프로젝트 메모리, 매직 키워드.
- **평판**: 제로컨피그·비용 절감·HUD 정확도·멀티모델 워커 호평. 불만: 단일 메인테이너 리스크(5개월 232 릴리스), 잦은 breaking change, 데이터 손실 버그 이력, 컨텍스트 고갈 데드락 이력, 영어권 커뮤니티 얇음.
- **핵심 시사점**: "팀을 굴린다" 포지션 유지 중. 기획 질문 엔진은 없음(Deep Interview가 흡수됐지만 보조적).

## 3. revfactory/harness + Claude Code 플랫폼 (2026)

- **harness**: 2026-03 생성. L3 메타 팩토리 — 팀 아키텍처를 "생성"하는 플러그인. 6개 아키텍처 패턴(Pipeline, Fan-out/Fan-in, Expert Pool, Producer-Reviewer, Supervisor, Hierarchical Delegation) × 6단계 워크플로(도메인 분석→팀 설계→에이전트 정의→스킬 생성→통합→검증). 산출물은 .claude/agents/ + .claude/skills/.
- **Agent Teams**: 여전히 experimental(기본 off). 팀메이트당 격리 1M 컨텍스트, P2P 메일박스, git 기반 태스크 클레임. 3-5명 권장. 한계: /resume 미지원, 토큰 3-7배, 데드락 가능.
- **공식 플러그인 생태계**: ralph-loop(19만+ 설치, Stop hook 기반 루프, --completion-promise), 내장 /loop·/goal·/batch와 보완 관계. 마켓플레이스는 SKILL.md 루트만으로 스킬번들 플러그인 지원.
- **플랫폼 신기능(플러그인 저자용)**: Progressive Disclosure 스킬, 라이프사이클 훅(SessionStart/PreToolUse/PostToolUse/Stop/TeammateIdle — 훅은 "강제", 스킬은 "권고"), TaskCreate 공유 작업 목록, worktree 격리 서브에이전트, /plugin details 토큰 영향 표시, 네임스페이스 스킬.

## 4. spec-driven / 단계형 프레임워크 경쟁 지형

| 프레임워크 | 스테이지 모델 | 산출물 | 게이트 | 무게 |
|---|---|---|---|---|
| GitHub Spec Kit | Constitution→Specify→Plan→Tasks→Implement | spec.md, plan.md, tasks.md, 체크리스트 | 리뷰 게이트+constitution 검증 | 중 |
| BMAD-METHOD | Analysis→Planning→Solutioning→Implementation | PRD, 아키텍처, 에픽, 스토리 | 프로세스 게이트 핸드오프 | 무거움 |
| Amazon Kiro | Requirements→Design→Tasks | requirements.md(EARS), design.md, tasks.md | 리뷰 게이트+SMT 검증 | 중 |
| OpenSpec | Propose→Apply→Archive | delta 스펙(변경분만) | 최소 세리머니 상태머신 | 가벼움 |
| GSD | PLANNING→BUILDING 루프 | 우선순위 TODO, 테스트 결과 | 태스크당 fresh context, 테스트 주도 | 가벼움 |
| Cursor Plan Mode | 단일 계획 단계 | 구현 계획+질문 | 리뷰 게이트 | 가벼움 |
| Tessl | Spec→Generate (spec-as-source) | 스펙이 소스, 코드는 생성물 | 실험적 | 가벼움 |
| Agent OS | 컨벤션 발견→주입 | 코드베이스 표준 | 게이트 없음(권고) | 가벼움 |

**실무자 컨센서스**:
- 동일 CRM 대시보드 벤치마크: BMAD 5.5시간 vs Spec Kit 90분 vs OpenSpec 12분 — 작은 작업에 무거운 프레임워크는 자멸.
- 스펙은 수 시간 내 구현과 drift — 정적 스펙 툴의 최대 약점. GSD는 태스크당 fresh 200K 컨텍스트로 context rot 자체를 설계로 제거 (5개월 만에 급성장).
- 솔로 개발자에게 풀 역할 시뮬레이션(BMAD 12 에이전트)은 "연극" — 채택 실패 1순위.
- 프레임워크 오버헤드가 컨텍스트 창의 15-20% 차지하면 사용자가 직접 쳐냄.
- 빠른 프로토타이핑 스위트스팟: 가볍게 시작(OpenSpec/Plan Mode급) → 필요할 때만 격상.

**2026 신규 흐름**:
- **Claude Code Dynamic Workflows**(6월): JS 오케스트레이션으로 "이 작업 전용 하네스를 그때그때 생성" — 고정 프레임워크 패러다임의 전환.
- **AI-DLC(AWS)**: adaptive depth — 단순 변경은 단순 처리, 복잡 변경만 풀 단계 발동. 파일 기반 승인.
- **cc-wf-studio**(5월): 비주얼 드래그앤드롭 워크플로 에디터 → .claude/agents/ 내보내기.
- **Augment Cosmos**(3월): "living specs" 자동 갱신 (대규모 조직용).
- Spec Kit: 통합 플러그인 아키텍처 + lean preset으로 세리머니 비판 대응.

## 5. 컨텍스트 엔지니어링 컨버전스 (2026 중반)

**수렴된 진실**:
1. **컨텍스트 = 유한한 attention budget** (Anthropic, 2025-09) — 매 턴 큐레이션. 프롬프트 엔지니어링의 후계.
2. **Living document(ExecPlan) = 에이전트 상태 머신** (OpenAI Codex) — "ExecPlan만으로 재시작 가능해야 한다". 7시간+ 세션의 비결.
3. **Interview-first** (Anthropic Tariq + 실무자) — 스펙 확정 전 40+ 심층 질문. 원샷 프롬프팅에 암묵적으로 묻힌 아키텍처 결정이 최대 재작업 원인.
4. **Progressive Disclosure** — 필요할 때만 컨텍스트 주입 (토큰 98% 절감 사례).

**2026 신흥 패턴 (워크플로 플러그인 저자용)**:
- Spec-Execution 분리: 발견(인터뷰)과 구현(스펙 소비)을 다른 세션/에이전트로.
- 스펙 내 결정 로그("왜 바꿨나") — 컨텍스트 리셋 후 복원력.
- 검증을 마일스톤 게이트로: 테스트가 스펙 정의의 일부.
- 멀티에이전트엔 코드 대신 계약+결정로그 전달.
- Question-driven bootstrap: 코딩 전 인터뷰 루프 자동 발동 → 구조화 스펙 산출.
- **Canvas as Source of Truth**: 세션 경계를 넘는 살아있는 작업 문서.

**폐기된 안티패턴**: 원샷 프롬프팅 / 서브에이전트에 풀 코드 전달 / 채팅 히스토리 = 메모리 / 사후 QA.

## 6. riff 현재 위치와 갭 분석

**riff가 이미 맞춘 것** (2026 컨센서스 선취):
- Question-Driven(ASK) = interview-first ✓
- 계약서 30줄 교환 = contracts-over-code ✓
- 매 Riff 검증 = verification gate ✓
- 항체/프로파일 = 세션 횡단 학습 ✓

**riff가 뒤처진 것**:
1. **Living canvas 부재** — riff-status.md는 상태 추적이지 "이것만으로 재시작 가능한" ExecPlan급 SSOT가 아님. _workspace/ 산출물이 파편화(problem.md, personas.md, journeys.md...).
2. **Adaptive depth 부재** — 질문 예산은 있으나 스테이지 자체가 고정 5단계. AI-DLC/GSD식 "단순하면 얇게" 없음.
3. **플랫폼 신기능 미활용** — TaskCreate 공유 작업목록, Stop/TeammateIdle 훅, worktree 격리 서브에이전트, Dynamic Workflows, /plugin details 토큰 가시성.
4. **모델 진화 미반영** — Fable 5급 모델에선 강제 파이프라인보다 얇은 게이트가 우세하다는 superpowers발 교훈.
5. **드리프트 관리 부재** — 계약서·스펙이 구현과 어긋날 때 탐지 메커니즘 없음.

## 소스 집계

- superpowers: 46 / OMC: 40 / harness·플랫폼: 40 / spec-driven: 54 / context-eng: 52 → **총 232 소스, 5 서브에이전트**

### 주요 URL
- https://github.com/obra/superpowers · https://blog.fsck.com
- https://github.com/Yeachan-Heo/oh-my-claudecode
- https://github.com/revfactory/harness · https://code.claude.com/docs/en/agent-teams
- https://github.com/github/spec-kit · https://github.com/fission-ai/openspec · https://github.com/context-studios/gsd · https://github.com/bmad-code-org/BMAD-METHOD · https://kiro.dev
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- https://github.com/openai/openai-cookbook/blob/main/articles/codex_exec_plans.md
