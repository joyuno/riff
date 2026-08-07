# Browser grader 실행 차단 기록

> 2026-08-06: 제한 없는 로컬 터미널에서는 실행에 성공해 Riff 세 결과 JSON을 생성했다.
> 아래 내용은 Codex sandbox에만 해당한다.

## 확인된 환경

- Python Playwright 1.57.0 설치됨
- 시스템 Google Chrome 설치됨
- Playwright Chromium과 Chromium headless shell 설치됨
- gstack `browse` 실행 파일 설치됨

## 재현 결과

현재 Codex sandbox에서 다음 두 동작이 차단된다.

1. localhost server bind: `PermissionError: [Errno 1] Operation not permitted`
2. 시스템 Chrome headless 실행: `TargetClosedError`, Chrome `SIGABRT`, cleanup `kill EPERM`
3. Playwright headless shell 실행: Mach rendezvous `Permission denied (1100)`, `SIGTRAP`
4. gstack browse daemon: localhost bind `EPERM`

권한 밖 실행 승인도 완료되지 않아 실제 앱의 클릭, 새로고침, 390px viewport를 검증하지
못했다. Riff 세 앱용 grader는 `riff_preflight_playwright.py`에 작성했지만, 이 환경에서는
실행 결과를 검증하지 못했으므로 공식 증거로 취급하지 않는다.

## 해제 조건

- localhost socket bind 허용
- Chrome subprocess 실행 허용
- Riff 세 task grader 실행
- 결과가 schema-valid `*.playwright.json`을 생성하는지 확인

이 네 조건을 만족하기 전에는 공식 human pilot을 시작하지 않는다.
