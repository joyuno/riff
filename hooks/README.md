# Riff Hook

Riff는 Claude Code에서 **선택적인 SessionStart hook 하나만** 제공합니다.
플랫폼의 일반 세션 메모리를 대체하지 않으며, Riff 프로젝트에 명시적으로 작성된
Living `CANVAS.md`의 STATUS만 세션 시작 시 한 번 복원합니다.

## 실행 시점

| Hook | 이벤트 | 실행 빈도 |
|---|---|---|
| `session-start-canvas.sh` | `SessionStart` | Claude Code 세션 시작 또는 재개 시 1회 |

명령 실행이나 파일 편집마다 동작하는 `PreToolUse`/`PostToolUse` hook은 없습니다.
서브에이전트 종료마다 동작하던 `riff-progress.sh`도 v1.0에서 제거했습니다.

Codex 로컬 플러그인 설치는 이 Claude Code hook을 자동 등록하지 않습니다. Codex는
자체 세션 컨텍스트를 사용하고, Riff skill이 필요할 때 CANVAS를 직접 읽습니다.

## 설치

```bash
bash /path/to/riff/hooks/install.sh
```

설치기는 기존 `~/.claude/settings.json`을 보존하면서 다음 항목만 등록합니다.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "command": "bash /절대경로/riff/hooks/session-start-canvas.sh"
      }
    ]
  }
}
```

이전 버전의 Riff `riff-progress.sh` 등록이 있으면 제거하며, 다른 프로젝트의
`SubagentStop` hook은 그대로 보존합니다. 같은 설치기를 다시 실행해도 Riff
SessionStart 항목은 하나만 유지됩니다.

설정을 쓰지 않고 결과만 확인하려면:

```bash
bash hooks/install.sh --dry-run
```

## 동작

`session-start-canvas.sh`는 현재 디렉터리에서 상위로 `_workspace/CANVAS.md`를 찾고,
`## STATUS`부터 다음 H2 직전까지 최대 12줄을 `additionalContext`로 반환합니다.

- CANVAS 또는 STATUS가 없으면 아무 상태도 주입하지 않습니다.
- CANVAS를 생성하거나 수정하지 않습니다.
- `jq`가 없으면 조용히 종료합니다.
- 주입 후에는 STATUS와 실제 working tree가 맞는지만 확인합니다.

따라서 일반적인 Claude/Codex 메모리와 경쟁하지 않고, 사용자가 Riff Cycle을 시작해
CANVAS가 존재하는 경우에만 결정론적인 재개 지점을 제공합니다.

## 테스트

```bash
bash hooks/tests/test-install.sh
bash -n hooks/*.sh
```

## 제거

`~/.claude/settings.json`의 `hooks.SessionStart` 배열에서 command가
`session-start-canvas.sh`로 끝나는 Riff 항목만 삭제합니다. 다른 SessionStart
hook은 보존합니다.
