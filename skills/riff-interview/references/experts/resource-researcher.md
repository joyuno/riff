# 전문가: 자료 리서처

**기여 Layer**: Layer 4 HOW-B
**상세 질문 흐름**: references/enriched-layers.md 참조
**이 파일**: Layer 4 HOW-B 질문의 전체 선택지와 GitHub 리서치 로직 상세

**역할**: 필요한 스킬/도구를 GitHub에서 리서치하고 설치 안내
**질문 수**: 4개
**의존**: UI 디자이너 결정사항 수신 후 실행

---

## 도입 멘트

"저는 자료 리서처입니다. 이 프로젝트에 필요한 Claude Code 스킬과 도구를 찾아드리겠습니다."

---

## Q1: 현재 설치된 스킬 파악

"현재 Claude Code에 설치된 스킬을 확인합니다."

실행: `claude plugin list` (또는 `ls ~/.claude/plugins/` 확인)
결과에서 설치된 스킬 목록 파악.

질문: "다음 중 추가로 필요할 것 같은 카테고리가 있으면 선택해주세요."
- [ ] UI/디자인 스킬 (taste-skill, frontend-design 등)
- [ ] 테스트/QA 스킬
- [ ] Git/배포 스킬
- [ ] 도메인 특화 스킬 (쇼핑몰, AI 서비스 등)
- [ ] 코드 품질 스킬

---

## Q2: GitHub 트렌드 리서치

UI 디자이너가 전달한 스킬 목록 + Q1 선택 항목을 기반으로 GitHub에서 리서치.

**리서치 도구: mcp-omnisearch**

mcp-omnisearch는 Tavily·Brave·Exa·Kagi·GitHub 검색을 하나의 인터페이스로 통합한 MCP 서버다.
GitHub 검색 기능으로 claude code 스킬, 트렌딩 플러그인을 실시간으로 탐색할 수 있다.

**mcp-omnisearch 설치 (최초 1회)**:

```bash
claude mcp add mcp-omnisearch -- npx -y mcp-omnisearch
```

환경변수 설정 (`~/.claude/settings.json` 또는 프로젝트 `.mcp.json`에 추가):
```json
{
  "mcpServers": {
    "mcp-omnisearch": {
      "command": "npx",
      "args": ["-y", "mcp-omnisearch"],
      "env": {
        "GITHUB_TOKEN": "YOUR_GITHUB_TOKEN"
      }
    }
  }
}
```

> ⚠️ **보안 규칙**: GITHUB_TOKEN은 `.mcp.json` 또는 `settings.local.json`에만 저장한다.
> `settings.json`이 git에 커밋되는 경우 반드시 `.gitignore`에 추가하거나 환경변수로 분리한다.
> 토큰을 SKILL.md나 마크다운 파일에 직접 기록하는 것을 금지한다.

**리서치 실행** (mcp-omnisearch `github_search` 도구 사용):

```
검색어 예시:
  github_search("claude code skill {기술스택} {키워드}")
  github_search("claude plugin {프레임워크} stars:>100")
  github_search("topic:claude-code-plugin language:{언어}")
```

리서치 후 발견된 스킬 목록을 제시:

```
발견된 스킬:
1. [스킬명] — [설명] — [GitHub URL] ⭐[stars]
   설치 명령: claude plugin install [URL]

2. [스킬명] — [설명] — [GitHub URL] ⭐[stars]
   설치 명령: claude plugin install [URL]
```

질문: "설치할 스킬을 선택해주세요. (번호로 선택, '전부'도 가능)"

---

## Q3: 설치 실행

선택된 스킬에 대해:
```
설치 명령 생성:
claude plugin install https://github.com/{owner}/{repo}
```

설치 완료 확인 후:
- 성공: "✅ {스킬명} 설치 완료. 이 프로젝트에서 사용 가능합니다."
- 실패: "⚠️ {스킬명} 설치 실패. 수동 설치 방법: [안내]"

---

## Q4: 스킬 사용 계획 확정

"설치된 스킬이 각 단계에서 어떻게 사용될지 매핑합니다."

출력:
```markdown
## 스킬 사용 계획

| 단계 | 스킬 | 용도 |
|------|------|------|
| ASK | riff-interview | 5-Layer 기획 |
| BUILD | [설치된 UI 스킬] | UI 컴포넌트 생성 |
| VERIFY | riff-qa | Tier 0~3 검증 |
| LEARN | riff-memory | 버그 패턴 기록 |
```

---

## 스킬 카탈로그 (사전 조사된 주요 스킬)

빠른 추천을 위한 참조 목록. 상세 최신 목록은 리서치 시 갱신.

| 스킬 | 용도 | GitHub |
|------|------|--------|
| taste-skill | 디자인 취향 분석 | 리서치 필요 |
| frontend-design | UI 컴포넌트 생성 | 내장 |
| oh-my-claudecode | 멀티 에이전트 | 내장 |
| riff | 프로젝트 루프 | joyuno/riff |
| mcp-omnisearch | GitHub·웹 통합 검색 MCP | spences10/mcp-omnisearch |

---

## 출력 형식

```markdown
## 자료 리서처 결정사항

- 설치된 스킬: [목록]
- 신규 설치: [목록 + 명령]
- 설치 실패: [목록 + 대안]
- 스킬 사용 계획: [단계별 매핑]
```
