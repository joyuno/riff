<p align="center">
  <img src="https://img.shields.io/badge/RIFF-Right_Questions,_Right_Products-7B2FF7?style=for-the-badge" alt="Riff">
</p>

<p align="center">
  <a href="https://github.com/joyuno/riff/releases/tag/v1.0.0"><img src="https://img.shields.io/badge/version-1.0.0-brightgreen" alt="v1.0.0"></a>
  <img src="https://img.shields.io/badge/Claude_Code-supported-purple" alt="Claude Code">
  <img src="https://img.shields.io/badge/Codex-supported-black" alt="Codex">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT"></a>
</p>

<p align="center"><strong>질문이 캔버스를 채운다.</strong><br>Right questions, right products.</p>

**한국어** | [English](README.en.md)

# Riff

Riff는 모호한 앱·MVP·자동화 아이디어를 질문으로 구체화하고, 실제로 작동하는
결과물까지 반복해서 만드는 개발 workflow입니다. Claude Code와 Codex에서 사용할 수
있으며, 모든 결정과 진행 상태를 Living `CANVAS.md` 한 장에 남깁니다.

```text
FRAME → SHAPE → BUILD → PROVE → LEARN
```

대화 기록이 길어지거나 세션을 다시 시작해도 CANVAS를 읽으면 현재 상태와 다음 행동을
바로 알 수 있습니다.

## 3분 Quick Start

### Claude Code

```text
/plugin marketplace add joyuno/riff
/plugin install riff@joyuno-riff
```

설치 후 새 대화에서:

```text
riff를 사용해서 이 아이디어를 제품으로 만들어줘.
```

### Codex

저장소를 로컬 marketplace로 등록하고 설치합니다.

```bash
codex plugin marketplace add .
codex plugin add riff@joyuno-riff-local
```

설치 후에는 새 Codex thread를 열어주세요. 예:

```text
Riff로 새 프로젝트를 시작해. 아이디어는 영상 편집 자동화야.
```

### 선택적 Claude Code hook

```bash
bash hooks/install.sh
```

설치되는 것은 `session-start-canvas.sh` 하나입니다. Claude Code 세션을 시작하거나
재개할 때 CANVAS의 STATUS를 한 번 복원하며, **명령이나 파일 수정마다 실행되지
않습니다.** Codex에는 이 Claude 전용 hook을 자동 등록하지 않습니다.

자세한 내용: [hooks/README.md](hooks/README.md)

## 어떻게 작동하나요?

| 단계 | 하는 일 | 남는 결과 |
|---|---|---|
| **FRAME** | Exa 조사와 재질문으로 사용자·문제·빠진 요구·성공 기준을 확정 | 근거, 가정과 acceptance |
| **SHAPE** | 가능한 방향과 트레이드오프를 비교 | 선택한 접근과 결정 로그 |
| **BUILD** | 작은 작업 단위로 구현 | 실행 가능한 결과물 |
| **PROVE** | 테스트·행동 검증·diff review | 통과/실패 증거 |
| **LEARN** | 교훈과 재발 방지 규칙을 기록 | 다음 Cycle과 commit anchor |

한 번에 완벽하게 만드는 대신 짧은 Cycle을 반복합니다. 실패하면 무작정 재시도하지
않고 FRAME 또는 SHAPE로 돌아가 잘못된 가정부터 수정합니다.

### Living CANVAS.md

Riff 프로젝트의 재시작 지점은 `_workspace/CANVAS.md`입니다.

```text
STATUS       현재 Cycle·단계·활성 가정·다음 행동
[1] FRAME    문제와 성공 기준
[2] SHAPE    선택한 방향과 결정
[3] BUILD    작업 보드와 계약 상태
[4] PROVE    검증 결과와 증거
[5] LEARN    교훈과 다음 Cycle
```

긴 조사와 계약은 `_workspace/detail/`, `_workspace/contracts/`로 분리해 CANVAS는
항상 짧고 최신 상태로 유지합니다.

## 언제 사용하나요?

**잘 맞는 작업**

- 새 웹앱·모바일 앱·MVP
- 업무 자동화와 AI pipeline
- 요구사항이 아직 모호한 신규 제품
- 여러 외부 API와 데이터 흐름을 연결하는 프로젝트
- 구현뿐 아니라 검증과 학습까지 반복해야 하는 작업

**굳이 사용하지 않아도 되는 작업**

- 오타 수정
- 원인이 명확한 작은 버그
- 범위가 확정된 단일 함수 변경
- 설명이나 코드 리뷰만 필요한 요청

이런 작은 작업에서는 일반적인 Claude Code/Codex workflow가 더 빠릅니다.

## 핵심 기능

### Domain Intelligence

Riff는 의료·법률·현장 운영·SaaS·콘텐츠·AI처럼 서로 다른 도메인에 같은 검색법을
적용하지 않습니다. Domain Research Router가 도메인의 지식 계열·위험·관할을 판정하고,
그에 맞는 출처와 발굴법을 선택합니다.

Exa로 찾은 내용은 역할·업무·데이터·상태·규칙·예외의 Domain Model로 바꾸고 Knowledge
Ledger에 근거 상태를 기록합니다. 검색 결과를 기능으로 몰래 추가하지 않으며, 사용자가
확인한 지식만 `Knowledge → acceptance → 구현 → PROVE`로 추적됩니다.

번들 Exa MCP는 API 키 없는 무료 경로를 기본으로 사용합니다. 무료 한도에 걸리거나 연결할
수 없으면 Claude Code/Codex의 웹 검색으로 폴백하며, 가입 때문에 작업을 멈추지 않습니다.

### Adaptive depth

요구 명확성·외부 의존·보안·실패 비용 등 8개 신호로 작업을 단순/보통/복잡으로
분류합니다. “빠르게”, “간단히” 같은 표현만으로 검증 단계를 줄이지 않습니다.

### 증거가 남는 PROVE

작업 깊이에 맞춰 정적 검사, 테스트, acceptance, secret scan, diff review, live QA를
선택합니다. 모델의 “완료했습니다”가 아니라 실행 결과로 완료를 판단합니다.

### Cycle commit anchor

각 Cycle의 검증된 상태를 `cycle-N:` commit으로 남깁니다. 실패가 누적되면 변경 증거를
보존한 뒤 이전 anchor로 안전하게 되돌아갈 수 있습니다.

### DROP과 TUNE

- **DROP:** 실험 결과를 merge/keep/discard하고 안전하게 착륙
- **TUNE:** 여러 Cycle 뒤 쌓인 결정·규칙·컨텍스트를 정리

둘 다 매 Cycle의 필수 절차가 아니라 필요할 때만 실행됩니다.

### 선택적 companion

Riff는 외부 companion이 없어도 동작합니다. 사용할 수 있으면 대립 검토나 반복 검증을
강화하고, 없으면 인라인 fallback으로 계속 진행합니다. Codex 안에서는 Claude 전용
companion 설치를 다시 묻지 않습니다.

## 벤치마크

```bash
cd benchmarks

# API 호출 없이 기존 pipeline 점검
./run-benchmark.sh --dry-run

# Riff 적용 전후 wall-clock 오버헤드 판정 (기본 예산 15%)
./run-speed-tax.sh --baseline-ms 1000,1050,1100 --riff-ms 1100,1150,1200

# 저장된 결과로 depth 반복 일관성 채점
./run-depth-reproducibility.sh --outputs-dir ./saved-depth-outputs --repetitions 3
```

실제 모델 명령 연결과 결과 형식은 [benchmarks/README.md](benchmarks/README.md)를
참고하세요.

## 저장소 구조

```text
riff/
├── .claude-plugin/              Claude Code plugin metadata
├── .codex-plugin/plugin.json    Codex plugin manifest
├── .mcp.json                    bundled Exa search
├── .agents/plugins/             local Codex marketplace
├── skills/riff/
│   ├── SKILL.md                 workflow 진입점
│   └── references/              단계별 상세 규칙
├── hooks/                       선택적 SessionStart hook
├── benchmarks/                  fixture·scorer·runner
└── README.md / README.en.md
```

세부 동작은 [`skills/riff/SKILL.md`](skills/riff/SKILL.md)와
[`skills/riff/references/`](skills/riff/references/)에서 확인할 수 있습니다.

## 요구사항

- Claude Code 또는 Codex
- 요구사항 발굴을 위한 인터넷 연결(Exa 실패 시 호스트 검색으로 폴백)
- benchmark 실행 시 Python 3.9+와 jq
- 프로젝트가 실제로 사용하는 build/test/browser 도구

## 라이선스

[MIT](LICENSE)
