# 비교 harness 설치 기준

## Riff

현재 Codex에 `riff:riff` 1.0.0이 설치돼 있다. Synthetic preflight 세 결과만 생성됐다.

## GSD

현재 미설치다. 기존 `gsd-build/get-shit-done` 저장소는 아카이브됐으므로 공식 후속
프로젝트인 `open-gsd/gsd-core`를 사용한다.

```bash
npx @opengsd/gsd-core@latest
```

설치기에서 Codex와 local 설치를 선택한 뒤 새 프로젝트에서는 `$gsd-new-project`를
사용한다.

## gstack

현재 미설치다. 공식 upstream의 Codex 설치 방법을 사용한다.

```bash
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/gstack
cd ~/gstack && ./setup --host codex
```

MVP 시작은 `$office-hours`로 문제를 정리한 뒤 계획·구현·QA 흐름을 따른다.

## 공정성 규칙

- 세 harness 모두 동일 Codex 모델과 검색 접근을 사용한다.
- 설치 버전 또는 Git commit을 첫 실행 전에 기록한다.
- GSD와 gstack 미설치 폴더는 결과로 채점하지 않는다.
- AI가 실행한 로컬 검수 결과와 실제 human pilot 결과를 합산하지 않는다.
