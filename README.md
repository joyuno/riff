<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/⚡_PULSE-Right_Questions,_Right_Products-blueviolet?style=for-the-badge&labelColor=1a1a2e&color=7B2FF7&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiPjxwYXRoIGQ9Ik0yMiAxMmgtNGwtMyA5TDkgM2wtMyA5SDIiLz48L3N2Zz4=" />
    <img alt="Pulse Banner" src="https://img.shields.io/badge/⚡_PULSE-Right_Questions,_Right_Products-blueviolet?style=for-the-badge&labelColor=1a1a2e&color=7B2FF7&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiPjxwYXRoIGQ9Ik0yMiAxMmgtNGwtMyA5TDkgM2wtMyA5SDIiLz48L3N2Zz4=" />
  </picture>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-0.1.0-brightgreen.svg" alt="Version">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/Claude_Code-Plugin-purple.svg" alt="Claude Code Plugin">
  <img src="https://img.shields.io/badge/Modules-6_Skills-orange.svg" alt="6 Modules">
  <img src="https://img.shields.io/badge/Domains-5_Experts-green.svg" alt="5 Domains">
  <img src="https://img.shields.io/badge/QA-3_Tier_+_Playwright-red.svg" alt="3-Tier QA">
  <a href="https://github.com/joyuno/pulse/stargazers"><img src="https://img.shields.io/github/stars/joyuno/pulse?style=social" alt="GitHub Stars"></a>
</p>

<p align="center">
  <b>올바른 질문이 올바른 제품을 만든다.</b><br>
  <sub>Right questions, right products.</sub>
</p>

---

# Pulse

**Question-Driven Development** — A Claude Code Plugin

**한국어** | [English (coming soon)]()

코드를 잘 짜는 건 AI가 합니다. 하지만 **"무엇을 만들어야 하는가"는 여전히 사람의 머릿속에 있습니다.**

Pulse는 처음 기획 단계에서 **올바른 질문을 던져서**, 개발 경험이 없는 사람도 자신의 아이디어를 완성도 높은 서비스로 만들 수 있게 해주는 질문 프레임워크입니다.

## Why Pulse?

AI가 아무리 뛰어나도, **질문이 잘못되면 결과도 잘못됩니다.**

```
질문 없이:  "쇼핑몰 만들어줘"
            → AI가 알아서 만듦 → 내가 원하던 게 아님 → 처음부터 다시

질문과 함께: "누가 쓰나? 핵심 문제가 뭔가? 성공 기준은?"
            → 내가 진짜 원하는 게 명확해짐 → AI가 정확히 만듦 → 완성
```

> 문제는 AI의 능력이 아닙니다. **당신의 머릿속에 있는 것을 꺼내는 과정**이 빠져 있었을 뿐입니다.

Pulse는 JTBD(Jobs-to-Be-Done), Mom Test, Pre-mortem, 소크라테스 대화법을 결합한 **5-Layer 질문 프레임워크**로, 기획 단계에서 올바른 의사결정을 유도합니다. 질문이 끝나면, AI가 빠른 반복 루프로 실제 서비스를 만듭니다.

```
Pulse = 올바른 질문(ASK) + 빠른 반복(EXPLORE → BUILD → VERIFY → LEARN)

           ┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃→ 완성
           각 ┃ = 하나의 Pulse (수분~수십분)
           매 Pulse마다 "질문 → 시도 → 검증 → 학습"
```

> 9주짜리 기존 프로젝트 = **15~25 Pulse** = **3~8시간**

---

## Quick Start

### Installation

```shell
# 1. 마켓플레이스 등록
/plugin marketplace add joyuno/pulse

# 2. 핵심 엔진 설치 (이것만으로 동작)
/plugin install pulse@pulse

# 3. 모듈 추가 (선택 — 있으면 더 강력)
/plugin install pulse@pulse-interview    # 소크라테스 인터뷰
/plugin install pulse@pulse-qa           # 3-Tier QA + Playwright
/plugin install pulse@pulse-contracts    # 인터페이스 계약
/plugin install pulse@pulse-immunity     # 실패 면역 시스템
/plugin install pulse@pulse-dna          # 사용자 프로파일 학습
```

### Direct Installation

```shell
# 글로벌 스킬로 직접 복사
cp -r skills/* ~/.claude/skills/
```

### Usage

Claude Code에서 바로 사용:

```
"프로젝트 시작해줘"
"쇼핑몰 MVP 만들어줘"
"pulse로 시작"
"앱 만들어줘"
```

---

## Architecture

### Pulse Cycle

매 Pulse는 5단계를 반복합니다. 각 사이클 후 **작동하는 결과물**이 존재합니다.

<p align="center">
  <img src="docs/pulse_cycle.png" alt="Pulse Cycle" width="700">
</p>

### Module System

**핵심 원칙: 없어도 돌아가는 모듈 시스템.**

```
pulse만 설치:           pulse + interview:        pulse + 전체:
┌─────────────┐        ┌─────────────┐           ┌─────────────┐
│ ASK: 기본 2개│        │ ASK: 5-Layer│           │ ASK: 전문가  │
│ EXPLORE: Agent│       │    전문가질문 │           │ EXPLORE: 분신│
│ BUILD: 직접  │        │ EXPLORE: 동일│           │ BUILD: 계약  │
│ VERIFY: build│        │ BUILD: 동일  │           │ VERIFY: Live │
│ LEARN: 로그  │        │ VERIFY: 동일 │           │ LEARN: 항체  │
└─────────────┘        └─────────────┘           │       + DNA │
     기본 동작              ASK 강화               └─────────────┘
                                                    최대 성능
```

### Modular Architecture

<p align="center">
  <img src="docs/architecture.png" alt="Modular Architecture" width="700">
</p>

---

## Features

### 1. Question Engine — 멀티 프레임워크 질문 엔진

> 검증된 4가지 질문법을 결합해서, **비개발자도 AI와 함께 상세 기획을 완성**할 수 있습니다.

```
일반 AI:  "쇼핑몰 만들어줘" → AI가 알아서 만듦 → 내가 원하던 게 아님

Pulse:    "이 제품이 없으면 그 일을 지금 어떻게 하고 있나요?"  ← JTBD
          → "매주 엑셀로 3시간씩 주문 정리해요"
          "지난주에 가장 짜증났던 순간은?"                     ← Mom Test
          → "복붙하다 주문 2건을 빠뜨렸어요"
          "딱 하나의 버튼만 있다면?"                           ← Constraint
          → "주문 자동 확인 버튼이요"
          "3개월 후 실패했다면, 왜?"                           ← Pre-mortem
          → "주문량이 늘면 느려질 것 같아요"
          → 기획 완성 → AI가 정확히 구현
```

**5-Layer 기획 프레임 — 각 Layer에 최적의 질문법:**

| Layer | 프레임워크 | 핵심 질문 | 결정하는 것 |
|-------|-----------|----------|-----------|
| **WHY** | JTBD | 이 제품이 해결할 "일"은? | 핵심 Job, 리스크 태깅 |
| **WHO** | Mom Test | 실제로 지금 어떻게 하고 있나? | 실제 행동 기반 페르소나 |
| **WHAT** | Constraint Forcing | 딱 하나만 만든다면? | MVP 핵심, 우선순위 |
| **HOW** | 소크라테스 | A와 B 중 비용은? | 트레이드오프, 기술 결정 |
| **MEASURE** | Pre-mortem | 실패한다면 이유는? | 리스크 제거, 성공 기준 |

**5개 전문 도메인:**

| 도메인 | 전문가 질문 예시 |
|--------|----------------|
| **웹개발** | SSR vs CSR? 인증 방식? 실시간 필요? |
| **스마트스토어** | 소싱 방식? 자동화 범위? 마진 구조? |
| **영상 제작** | 숏폼/롱폼? AI 활용 범위? 다국어? |
| **퀀트 투자** | 전략 유형? 실행 주기? 리스크 관리? |
| **AI 엔지니어링** | RAG vs 파인튜닝? 가드레일? 비용 최적화? |

---

### 2. 3-Tier QA — Live Browser Testing

> 정적 분석으로 잡을 수 있는 건 앞에서 잡고, **런타임 버그만 Playwright로 검증**합니다.

```
Tier 1: 정적 경계면 QA          비용: 낮음 | 속도: 빠름
        API 응답 shape ↔ 프론트 훅 타입 교차 비교
        파일 경로 ↔ href 링크 매핑 검증
        ──────────────────────────────────────
Tier 2: 빌드/타입 QA            비용: 중간 | 속도: 중간
        tsc --noEmit, eslint, npm run build
        ──────────────────────────────────────
Tier 3: Live Browser QA         비용: 높음 | 속도: 느림
        Playwright로 실제 브라우저에서 유저 시나리오 실행
        스크린샷 증거 수집, 콘솔 에러/네트워크 확인
```

**Tier 3 QA 변형:**

| 변형 | 설명 |
|------|------|
| **유령 사용자** | AI가 스크린샷을 보고 자유 탐색 — 예상 못한 버그 발견 |
| **파괴자** | SQL 인젝션, XSS, 버튼 연타, 초장문 입력 등 비정상 테스트 |
| **시간축** | 상태 변화 흐름 추적 — 새로고침/탭 전환 후에도 일관성 검증 |
| **다중 인격** | 급한 운영자 / 신규 사용자 / 모바일 사용자 등 다양한 관점 |

---

### 3. Interface Contracts — 인터페이스 계약

> 에이전트 간 **500줄 대신 30줄 계약서만 교환**하여 컨텍스트를 94% 절약합니다.

```
기존:  에이전트A ──500줄 전체 코드──→ 에이전트B (낭비)
Pulse: 에이전트A ──30줄 계약서────→ 에이전트B (효율)
```

**5종 계약서:**

| 계약 유형 | 내용 | QA Tier |
|----------|------|---------|
| **type** | API 응답 shape, 타입 시그니처 | Tier 1 |
| **behavior** | 상태 전이 규칙, 유저 저니 순서 | Tier 3 |
| **visual** | 컴포넌트 상태, 반응형 브레이크포인트 | Tier 3 |
| **performance** | 응답 시간 SLA, 번들 크기 제한 | Tier 3 |
| **security** | 인증 규칙, 입력 검증, CORS | Tier 3 (파괴자) |

---

### 4. Failure Immunity — 실패 면역 시스템

> 한번 겪은 버그에 **항체**를 만들어 같은 실수를 자동 방지합니다.

```
버그 발생 → 항체 생성 → 다음 BUILD에서 자동 주입
                ↓
           재발 시 → 항체 강화 (체크리스트 확장)
                ↓
      5회 미발생 → 항체 약화 (체크리스트 제거, 기록 보존)
```

---

### 5. User DNA — 사용자 프로파일

> 세션별로 사용자의 성향을 학습하여, **다음 세션에서 자동 적응**합니다.

추적 항목: 커뮤니케이션 스타일 / 기술 선호 / 의사결정 패턴 / 코딩 컨벤션

---

## AI-Native Patterns

인간이 할 수 없지만 **AI라서 가능한** 7가지 협업 방식:

| 패턴 | 인간 | AI |
|------|------|-----|
| **분신술** | 한 명이 한 관점 | 같은 에이전트를 3개 관점으로 동시 스폰 |
| **시간여행** | 설계→구현→테스트 1회 | 빠른 사이클을 5회 반복, 5번째가 최고 품질 |
| **대립토론** | 회의 정치, 감정 개입 | 순수 논리로 찬성/반대 동시 수행 |
| **되감기** | 3주 진행 후 되돌리면 3주 낭비 | git reset 후 항체/DNA는 보존 |
| **탐색 폭발** | 방법 A를 2주 시도 → 실패 → 방법 B | A, B, C를 동시에 5분간 시도 |
| **미래 시뮬레이션** | "6개월 후 괜찮을까?" 알 수 없음 | 데이터 100만건, 신기능 추가 시나리오 검증 |
| **점진적 확신** | 확신 없어도 일정 때문에 진행 | 확신 낮으면 자동 추가 탐색 |

---

## Use Cases — Try These Prompts

Pulse 설치 후 Claude Code에서 바로 사용:

**E-Commerce MVP**
```
쿠팡 스타일의 주문 관리 대시보드를 만들어줘.
판매자가 주문 확인, 배송 처리, 환불 관리를 할 수 있어야 해.
```

**Smart Store Automation**
```
네이버 스마트스토어 상품 등록을 자동화하는 도구를 만들어줘.
엑셀에서 상품 정보를 읽어서 API로 등록하고 가격을 자동 조정하는 시스템.
```

**Video Content Pipeline**
```
유튜브 숏폼 자동 생성 파이프라인을 만들어줘.
트렌드 주제 수집 → 대본 생성 → TTS → 자막 → 업로드까지.
```

**Quant Trading Bot**
```
바이낸스에서 BTC/USDT 모멘텀 전략으로 자동매매하는 봇을 만들어줘.
백테스트 → 시뮬레이션 → 실거래 순서로 진행하고 리스크 관리 포함.
```

**AI Agent System**
```
RAG 기반 고객 상담 챗봇을 만들어줘.
회사 문서를 벡터 DB에 넣고, 질문에 답변하되 할루시네이션 방지 가드레일 포함.
```

---

## Plugin Structure

```
pulse/
├── .claude-plugin/
│   └── plugin.json                          # Plugin manifest
│
├── skills/
│   ├── pulse/                               # Core loop engine
│   │   ├── SKILL.md                         #   ASK→EXPLORE→BUILD→VERIFY→LEARN
│   │   └── references/
│   │       └── convergence.md               #   Convergence detection criteria
│   │
│   ├── pulse-interview/                     # Socratic interview
│   │   ├── SKILL.md                         #   5-Layer interview framework
│   │   └── references/
│   │       ├── layers.md                    #   Question trees per layer
│   │       ├── scorecard.md                 #   Interview quality evaluation
│   │       ├── answer-to-arch.md            #   Answer → architecture mapping
│   │       └── domains/
│   │           ├── web-development.md       #   Web dev expert questions
│   │           ├── smart-store.md           #   Dropshipping/smart store
│   │           ├── video-creation.md        #   Video production
│   │           ├── quant-trading.md         #   Quant/auto-trading
│   │           └── ai-engineering.md        #   AI/ML engineering
│   │
│   ├── pulse-qa/                            # 3-Tier QA system
│   │   ├── SKILL.md                         #   QA orchestration
│   │   └── references/
│   │       ├── tier1-boundary.md            #   Static boundary analysis
│   │       ├── tier2-build.md               #   Build/type verification
│   │       ├── tier3-live.md                #   Playwright live browser QA
│   │       ├── ghost-user.md                #   AI free-exploration testing
│   │       └── destroyer.md                 #   Destructive/security testing
│   │
│   ├── pulse-contracts/                     # Interface contracts
│   │   ├── SKILL.md                         #   Contract system overview
│   │   └── references/
│   │       ├── type.template.md             #   API shape contracts
│   │       ├── behavior.template.md         #   State transition contracts
│   │       ├── visual.template.md           #   UI state contracts
│   │       ├── performance.template.md      #   SLA contracts
│   │       └── security.template.md         #   Auth/security contracts
│   │
│   ├── pulse-immunity/                      # Failure immunity
│   │   ├── SKILL.md                         #   Antibody lifecycle
│   │   └── references/
│   │       └── antibody-schema.md           #   Antibody file schema
│   │
│   └── pulse-dna/                           # User profiling
│       ├── SKILL.md                         #   Learning mechanism
│       └── references/
│           └── profile-schema.md            #   Profile schema
│
├── LICENSE
└── README.md
```

## Comparison

|  | Harness | OMC | **Pulse** |
|---|---------|-----|-----------|
| **본질** | 팀을 만든다 | 팀을 굴린다 | **올바른 질문으로 제품을 만든다** |
| **관점** | 인간 팀 모방 | 인간 워크플로우 | **Question-Driven** |
| **시간 단위** | Phase (시간~일) | Task (분~시간) | **Pulse (분)** |
| **설계** | 사전 전체 설계 | 계획→실행 | **점진적 발견** |
| **QA 시점** | 완성 후 | 완성 후 | **매 Pulse** |
| **실패 비용** | 높음 | 중간 | **없음 (되감기)** |
| **학습** | 수동 피드백 | 메모리 수동 | **자동 (항체/DNA)** |
| **조합** | — | — | **Harness/OMC와 함께 사용 가능** |

## Inspired By

- [revfactory/harness](https://github.com/revfactory/harness) — Agent Team & Skill Architect. Pulse의 Progressive Disclosure 패턴과 에이전트 팀 설계는 Harness에서 영감을 받았습니다.

## Requirements

- Claude Code CLI
- [Agent Teams enabled](https://code.claude.com/docs/en/agent-teams): `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Playwright MCP (Tier 3 Live QA 사용 시)

## License

MIT