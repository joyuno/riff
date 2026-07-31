# Companions — 부트스트랩·폴백

이 문서는 riff의 세 가지 선택적 컴패니언(`ralph-loop`, `codex`, `ecc-plan-canvas`)의 부트스트랩 설치와, 컴패니언 부재 시 네이티브 폴백을 정의한다. 모든 컴패니언은 있으면 강화, 없어도 riff는 전 기능 동작한다.

## Bootstrap (첫 호출 시 1회)

이 프로젝트에서 `riff`를 처음 호출할 때 다음 의존성을 점검하고, 누락된 것을 사용자에게 한 번 물어 자동 설치한다. 부트스트랩 재실행 가드: `_workspace/.riff-bootstrap-done` **또는** `_workspace/.riff-bootstrap-skip-all` 둘 중 하나라도 존재하면 스킵.

### 점검 항목 (각 항목마다 on/off 선택 가능)

| 의존성 | 점검 방법 | 누락 시 자동 동작 | 효과 |
|--------|-----------|------------------|------|
| `ralph-loop` 플러그인 | `~/.claude/plugins/cache/claude-plugins-official/ralph-loop` 존재 | `/plugin install ralph-loop@anthropic` | PROVE 실패 루프 |
| `codex` 플러그인 | `~/.claude/plugins/cache/openai-codex/codex` 존재 | `/plugin marketplace add openai/codex-plugin-cc` + `/plugin install codex@openai-codex` | SHAPE 대립 검토, diff-review cross-check |
| Codex CLI | `command -v codex` | `npm install -g @openai/codex` | 위 두 기능의 런타임 |
| Codex 로그인 | `node ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs setup --json` 의 `loggedIn: true` (codex 플러그인 캐시의 절대 경로 사용 — `${CLAUDE_PLUGIN_ROOT}`는 riff 컨텍스트라 부적합) | 사용자에게 `!codex login` 안내 (OAuth는 브라우저 필요) | Codex 호출 권한 |
| Codex sandbox 설정 | `~/.codex/config.toml`에 `sandbox_mode`/`approval_policy` 키 + 현재 프로젝트 `[projects."<cwd>"]` 섹션의 `trust_level = "trusted"` 존재 여부 | 누락된 키만 append (기존 설정 보존, 변경 전 `~/.codex/config.toml.bak`로 백업) — 아래 "Codex sandbox 권장 설정" 참조 | `/codex:review`·`/codex:adversarial-review` 호출 시 sandbox 권한 거부·trust 프롬프트 0건 |
| ecc plan-canvas | `command -v ecc-plan-canvas` | `npm install -g ecc-universal` | verdict 게이트 브라우저 리뷰 |

### 사용자 응답 처리

- **Install (Recommended)**: 자동 설치 후 다음 항목 점검
- **Skip**: 해당 항목 비활성화하고 다음 항목으로 — Riff는 보강 기능 없이 기본 흐름만 사용
- **Skip all**: 일괄 비활성화, 더 이상 묻지 않음 (`_workspace/.riff-bootstrap-skip-all` 마킹 — 위 가드가 이 파일도 체크함)

설치 후 `_workspace/.riff-bootstrap-done`에 timestamps + 활성화된 의존성 목록 기록.

### Codex sandbox 권장 설정 (자동 적용 상세)

목적: 첫 다운로드한 사용자가 수동 설정 없이도 `/codex:review`·`/codex:adversarial-review`가 sandbox 권한 거부·trust 프롬프트 없이 즉시 실행되도록 한다.

**점검 순서:**
1. `~/.codex/config.toml` 존재 여부 — 없으면 생성
2. 다음 3개 키 누락 여부를 grep으로 점검:
   - `^sandbox_mode\s*=`
   - `^approval_policy\s*=`
   - 현재 프로젝트 trust 등록: `[projects."<cwd>"]` 섹션 안에 `trust_level\s*=\s*"trusted"`
3. 누락된 항목만 사용자에게 보여주고 동의받기 — 이미 설정된 항목은 그대로 둔다 (사용자 선택 존중)

**자동 추가할 내용:**

```toml
# riff bootstrap이 추가 — 작업 디렉토리 외부 쓰기 차단, 권한 거부 시만 사용자 확인
sandbox_mode = "workspace-write"
approval_policy = "on-failure"

# riff bootstrap이 추가 — <cwd> 프로젝트 trust 등록 (매번 trust 묻지 않음)
[projects."<현재 프로젝트 절대 경로>"]
trust_level = "trusted"
```

**안전 장치:**
- 변경 전 `cp ~/.codex/config.toml ~/.codex/config.toml.bak.$(date +%s)` 으로 timestamp 백업 — 사용자가 원복 가능
- `append`만, 기존 값 `replace` 금지. 이미 다른 값이 설정되어 있으면 (예: `sandbox_mode = "read-only"`) 사용자 의도이므로 그대로 둠
- 추가하는 라인 앞에 `# riff bootstrap (YYYY-MM-DD)` 주석 — 어디서 왔는지 추적 가능
- 사용자 응답 처리는 위 "사용자 응답 처리" 정책과 동일 (Install / Skip / Skip all)

**왜 이 값들인가:**
- `workspace-write`: Codex CLI의 3가지 모드(`read-only`/`workspace-write`/`danger-full-access`) 중 작업 디렉토리만 쓰기 허용. `read-only`로는 `/codex:rescue` 등 수정 도구가 동작 못 함, `danger-full-access`는 위험.
- `on-failure`: 매번 확인 묻는 `untrusted`/`on-request`는 자동화 흐름 끊김. `never`는 실패 가시성 없음.
- 프로젝트별 `trust_level = "trusted"`: 전역 trust가 아니라 현재 프로젝트만 — 다른 프로젝트는 영향 없음.

### Codex/GPT 모델 정책

**모든 Codex 호출에 `--model` 플래그를 명시하지 않는다.** Codex CLI 기본값이 그 시점의 최신 모델이며 자동 업데이트된다. 사용자가 명시 요청하면 그때만 `--model <name>` 사용.

---

## 폴백 매트릭스 (있으면 강화, 없으면 네이티브 — 컴패니언 없이도 전 기능 동작)

| 기능 | 컴패니언 있으면 | 없으면 |
|---|---|---|
| PROVE 실패 루프 | `/ralph-loop:ralph-loop "<failure>" --max-iterations 3 --completion-promise 'VERIFY_PASSED'` | 자체 재시도 2회 → 실패 유형 진단 → 에스컬레이션 |
| SHAPE 대립 검토 | `/codex:adversarial-review --wait <focus>` 1회 | 잼에 반대 관점 에이전트 1개 추가 |
| diff-review (복잡 depth) | `/codex:review --wait --scope working-tree` | 인라인 self-review / `sonnet` 독립 리뷰 |
| verdict 게이트 | `ecc-plan-canvas open _workspace/CANVAS.md` → `await` — 요소 앵커 주석 + approve/request-changes, 수정 시 라이브 리로드, 끝나면 `end` | 터미널 구조화 질문 |

**codex 리뷰 단일 트리거 규칙**: `/codex:review`는 diff-review의 복잡 depth 슬롯에서만 호출한다.
(구 버전의 "대형 변경 시 별도 cross-check" 트리거는 이 슬롯에 통합 — 동일 사이클 이중 호출 금지.)
