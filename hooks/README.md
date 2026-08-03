# Riff Hooks

Riff v1.0의 Claude Code lifecycle hook입니다. 진행 훅은 `.riff/state.json`의
현재 Cycle을 읽고, 세션 시작 훅은 Living `CANVAS.md`의 STATUS를 복원합니다.
두 훅 모두 프로젝트 상태를 막지 않는 graceful fallback을 사용합니다.

## 설치

```bash
bash /path/to/riff/hooks/install.sh
```

옵션:

| 옵션 | 설명 |
|---|---|
| `--dry-run` | 설정을 쓰지 않고 변경 예정 내용만 출력 |
| `--help` | 사용법 출력 |

수동 등록 시 `~/.claude/settings.json`의 기존 `hooks`를 보존하면서 다음 항목을
추가합니다.

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "",
        "command": "bash /절대경로/riff/hooks/riff-progress.sh"
      }
    ],
    "SessionStart": [
      {
        "matcher": "",
        "command": "bash /절대경로/riff/hooks/session-start-canvas.sh"
      }
    ]
  }
}
```

## `.riff/state.json`

진행 훅이 읽는 v1 상태 SSOT입니다.

```json
{
  "cycle": 2,
  "last_anchor": "abc123def456"
}
```

| 필드 | 형식 | 조건 |
|---|---|---|
| `cycle` | number | 0 이상의 정수 |
| `last_anchor` | string | 비어 있지 않은 사이클 커밋 SHA |

`riff-progress.sh`는 이 파일을 **읽기만** 합니다. 에이전트 기록을 누적하거나
상태 파일을 생성·수정·복구하지 않습니다. v0.3.1의 `riff-log.json`, journey/QA
수렴 지표, Riff 번호 기반 로직은 v1.0에서 지원하지 않습니다.

## `riff-progress.sh`

**이벤트:** `SubagentStop`

1. 현재 디렉터리부터 상위로 `.riff/`를 찾습니다.
2. `state.json`의 `cycle`과 `last_anchor`를 검증합니다.
3. hook 입력에서 `agent_name`, `total_tokens`, `duration_ms`를 읽습니다.
4. 현재 Cycle과 마지막 앵커를 `additionalContext`로 반환합니다.

정상 출력 예:

```json
{
  "continue": true,
  "additionalContext": "[Riff Progress] builder 완료 (120토큰, 45ms). 현재 Cycle 2, 마지막 앵커 abc123. CANVAS STATUS와 실제 작업 상태를 맞춘 뒤 다음 작업을 진행하세요."
}
```

다음 경우에도 항상 `continue: true`로 종료합니다.

- `.riff/` 또는 `state.json`이 없음: 추가 컨텍스트 없이 비활성
- JSON 손상 또는 필수 필드 오류: 경고 컨텍스트만 반환
- `jq`가 없음: 설치 경고 후 상태 확인 생략
- hook 입력 필드가 잘못됨: 토큰·시간은 0, 에이전트명은 `unknown`

## `session-start-canvas.sh`

**이벤트:** `SessionStart`

현재 위치에서 상위로 `_workspace/CANVAS.md`를 찾고 `## STATUS`부터 다음 H2
직전까지 최대 12줄을 `additionalContext`로 주입합니다. CANVAS가 없거나 STATUS가
비어 있으면 조용히 종료합니다. 이 훅도 파일을 수정하지 않습니다.

세션 재시작 후에는 주입된 STATUS와 실제 working tree·태스크 상태가 일치하는지
확인하고, 어긋나면 `skills/riff/references/prove/canvas-lint.md`의 규칙으로 먼저
재조정합니다.

## 테스트

```bash
bash hooks/tests/test-riff-progress.sh
bash -n hooks/*.sh
```

## 트러블슈팅

### 훅이 실행되지 않음

1. `~/.claude/settings.json`에 이벤트가 등록됐는지 확인합니다.
2. 스크립트 실행 권한을 확인합니다: `chmod +x hooks/*.sh`.
3. 설정 변경 후 Claude Code를 재시작합니다.
4. 수동 등록 시 절대 경로를 사용했는지 확인합니다.

### `.riff/`를 찾지 못함

훅은 hook 프로세스의 `pwd`에서 상위 방향으로 탐색합니다. 세션 작업 디렉터리가
프로젝트 루트 또는 그 하위인지 확인합니다.

### `state.json` 경고

파일을 자동 수정하지 않습니다. JSON 문법과 `cycle`, `last_anchor`를 확인한 뒤
CANVAS와 최근 `cycle-N:` 커밋 앵커를 기준으로 수동 복구합니다.

### `jq`가 없음

```bash
# macOS
brew install jq

# Ubuntu / Debian
sudo apt install jq
```
