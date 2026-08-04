# Riff 사용자 중심 README 재설계

**작성일:** 2026-08-04  
**상태:** 승인됨

## 목표

처음 방문한 사용자가 3분 안에 Riff의 정체성을 이해하고 Claude Code 또는 Codex에
설치한 뒤 첫 Cycle을 시작하게 한다. 내부 설계 설명보다 사용 흐름을 우선한다.

## 독자

- 모호한 앱·MVP·자동화 아이디어를 AI coding agent와 개발하려는 사용자
- Claude Code 또는 Codex에서 로컬·공개 플러그인을 설치하려는 사용자
- Riff가 자신의 작업에 맞는지 빠르게 판단하려는 오픈소스 방문자

## 정보 구조

1. 첫 화면: 핵심 문장, 2문장 정의, Claude/Codex 지원
2. 3분 Quick Start: 호스트별 설치, 첫 프롬프트, 선택적 hook
3. 작동 방식: 5단계 Cycle과 Living CANVAS
4. 사용 적합성: 새 제품에는 사용하고 작은 수정에는 사용하지 않음
5. 핵심 기능: adaptive depth, proof, anchor, DROP/TUNE, companion fallback
6. 실용 정보: hook 실행 시점, benchmark, 저장소 구조, 요구사항, 라이선스

## 편집 원칙

- 한국어 `README.md`와 영문 `README.en.md`의 섹션 순서와 의미를 맞춘다.
- 첫 설치 경로까지 스크롤 부담을 최소화한다.
- hook이 매 명령마다 실행되지 않고 Claude SessionStart에서만 선택적으로 실행됨을 명시한다.
- Codex 로컬 marketplace 명령과 새 thread 필요성을 명시한다.
- Playwright MCP를 필수 요구사항으로 표기하지 않는다.
- 경쟁 도구 비교, 장문의 내부 템플릿, 과도한 사용 사례는 제거한다.
- 상세 알고리즘은 `skills/riff/references/`, benchmark 설명은 `benchmarks/README.md`,
  hook 설명은 `hooks/README.md`로 연결한다.

## 검증

- 두 README의 필수 섹션과 설치 명령 존재
- 한국어·영문 상호 링크
- 모든 상대 Markdown 링크의 실제 대상 존재
- 구형 문구와 제거 대상 요구사항 부재
- plugin package 검증과 `git diff --check` 통과

