# Riff Hooks

Riff 플러그인의 Claude Code 훅 모음입니다.
서브에이전트 완료 시 진행률을 자동 추적하고 수렴 지표를 갱신합니다.

---

## 목차

1. [riff-progress 훅 개요](#1-riff-progress-훅-개요)
2. [설치 방법](#2-설치-방법)
3. [.riff/ 디렉토리 구조](#3-riff-디렉토리-구조)
4. [riff-log.json 스키마](#4-riff-logjson-스키마)
5. [수렴 지표 설명](#5-수렴-지표-설명)
6. [트러블슈팅](#6-트러블슈팅)
7. [향후 추가 예정 훅](#7-향후-추가-예정-훅)

---

## 1. riff-progress 훅 개요

**이벤트**: `SubagentStop` — 서브에이전트가 완료될 때마다 트리거됩니다.

**동작 순서**:

1. `SubagentStop` 이벤트 발생 시 Claude Code가 stdin으로 JSON 전달
2. 훅이 `agent_name`, `total_tokens`, `duration_ms` 추출
3. `.riff/riff-log.json`의 `agents` 배열에 완료 기록 추가
4. 수렴 지표(`journeys_done`, `qa_pass_rate`, `bugs_last_3`) 기반으로 다음 Riff 우선순위 제안 생성
5. `additionalContext` 필드로 진행 상황을 Claude에게 주입

**수렴 조건 충족 시**: "MVP 완성 여부를 사용자에게 확인하세요" 메시지 출력.

---

## 2. 설치 방법

### 자동 설치 (권장)

```bash
bash /path/to/riff/hooks/install.sh
```

옵션:

| 플래그 | 설명 |
|--------|------|
| `--dry-run` | 실제 변경 없이 예상 결과만 출력 |
| `--help` | 도움말 출력 |

### 수동 설치

`~/.claude/settings.json`을 열어 아래 내용을 추가합니다.

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "",
        "command": "bash /절대경로/riff/hooks/riff-progress.sh"
      }
    ]
  }
}
```

`hooks` 섹션이 이미 있다면 `SubagentStop` 배열에 항목을 추가하면 됩니다.
설정 후 Claude Code를 재시작해야 훅이 활성화됩니다.

### 프로젝트별 활성화

훅은 `.riff/` 디렉토리가 존재하는 프로젝트에서만 동작합니다.
Riff를 사용할 프로젝트 루트에서 다음 명령을 실행하세요.

```bash
mkdir -p .riff
```

---

## 3. `.riff/` 디렉토리 구조

```
<프로젝트 루트>/
└── .riff/
    └── riff-log.json      # 에이전트 완료 기록 및 수렴 지표
```

`.riff/` 디렉토리가 없는 프로젝트에서는 훅이 자동으로 비활성화됩니다(`continue: true` 반환 후 종료).

---

## 4. `riff-log.json` 스키마

```json
{
  "schema_version": "1.0",
  "riffs": [],
  "agents": [
    {
      "name": "executor",
      "timestamp": "2026-04-11T12:00:00Z",
      "tokens": 3200,
      "duration_ms": 45000
    }
  ],
  "convergence": {
    "journeys_done": 2,
    "journeys_total": 5,
    "qa_pass_rate": 0.75,
    "bugs_last_3": 1
  }
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `schema_version` | string | 스키마 버전 |
| `riffs` | array | Riff 단위 실행 기록 (향후 사용) |
| `agents` | array | 완료된 서브에이전트 목록 |
| `agents[].name` | string | 에이전트 이름 |
| `agents[].timestamp` | string | 완료 시각 (ISO 8601 UTC) |
| `agents[].tokens` | number | 해당 에이전트가 사용한 토큰 수 |
| `agents[].duration_ms` | number | 실행 시간 (밀리초) |
| `convergence` | object | 수렴 지표 (외부에서 업데이트) |

`convergence` 필드는 Riff 오케스트레이터가 직접 갱신합니다.
훅은 이 값을 읽어 우선순위 제안 및 수렴 판별에만 사용합니다.

---

## 5. 수렴 지표 설명

| 지표 | 필드명 | 설명 | 수렴 조건 |
|------|--------|------|-----------|
| 유저 저니 완료 수 | `journeys_done` | 완료된 유저 시나리오 수 | `journeys_done == journeys_total` |
| 전체 유저 저니 수 | `journeys_total` | 목표 유저 시나리오 수 | — |
| QA 통과율 | `qa_pass_rate` | 0.0 ~ 1.0 (1.0 = 100%) | `>= 0.9` |
| 최근 3 Riff 버그 수 | `bugs_last_3` | 최근 3회 Riff에서 발생한 버그 수 | 제안 트리거: `>= 3` |

**수렴 조건**: `journeys_done == journeys_total` AND `qa_pass_rate >= 0.9`
두 조건이 모두 충족되면 훅이 "MVP 완성 여부 확인" 메시지를 출력합니다.

**우선순위 자동 제안 규칙**:

- `qa_pass_rate < 0.8` → 테스트 보강 우선 제안
- `bugs_last_3 >= 3` → 버그 수정 우선 제안
- 미완료 저니 존재 → 저니 완료 우선 제안

---

## 6. 트러블슈팅

### jq 가 설치되지 않은 경우

훅이 graceful하게 실패하며 아래 메시지를 출력합니다.

```
[Riff Progress] 경고: jq가 설치되지 않아 진행률 추적을 건너뜁니다.
```

설치 방법:

```bash
# macOS
brew install jq

# Ubuntu / Debian
sudo apt install jq

# Alpine Linux
apk add jq
```

### 훅이 실행되지 않는 경우

1. `~/.claude/settings.json`에 `SubagentStop` 훅이 등록되어 있는지 확인
2. 스크립트에 실행 권한이 있는지 확인: `chmod +x riff-progress.sh`
3. Claude Code 재시작 여부 확인
4. 절대 경로를 사용했는지 확인 (상대 경로 불가)

### 훅이 등록되어 있으나 `.riff/` 감지 실패

훅은 현재 작업 디렉토리(`pwd`)에서 상위 방향으로 `.riff/`를 탐색합니다.
Claude Code 세션의 작업 디렉토리가 프로젝트 루트 하위인지 확인하세요.

### `riff-log.json` 이 손상된 경우

훅이 자동으로 손상된 파일을 `.riff/riff-log.json.bak.<timestamp>` 로 백업하고 재초기화합니다.

### 권한 오류 (Permission denied)

```bash
chmod +x /path/to/riff/hooks/riff-progress.sh
chmod +x /path/to/riff/hooks/install.sh
```

---

## 7. 향후 추가 예정 훅

| 훅 이름 | 이벤트 | 역할 |
|---------|--------|------|
| `riff-boot` | `SessionStart` | Claude Code 세션 시작 시 Riff 상태 로드 및 컨텍스트 주입 |
| `riff-learn` | `SubagentStop` | 완료된 에이전트의 아웃풋에서 패턴 학습, `.riff/learnings.json` 갱신 |
| `riff-antibody-inject` | `PreToolUse` | 과거 실패 패턴을 기반으로 위험 도구 호출 전 경고 주입 |

각 훅은 이 디렉토리에 추가되며 `install.sh`가 자동으로 일괄 등록을 지원할 예정입니다.
