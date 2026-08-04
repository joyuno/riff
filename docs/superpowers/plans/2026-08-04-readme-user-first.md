# Riff User-First README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace both README files with concise, user-first Korean and English landing documentation and deploy the result to `main`.

**Architecture:** Keep both languages structurally equivalent. Put activation and installation first, summarize the product loop in plain language, and route implementation detail to existing focused documents.

**Tech Stack:** Markdown, Bash, Python 3 standard library, Git.

## Global Constraints

- Preserve version `1.0.0` and do not move or recreate the existing release tag.
- Document only one optional Riff hook: Claude Code SessionStart CANVAS restoration.
- Do not claim that Codex installs Claude hooks.
- Do not list Playwright MCP as a requirement.
- Do not stage `.serena/` or `HANDOFF.md`.

---

### Task 1: README contract test

**Files:**
- Create: `tests/test-readme.sh`

**Interfaces:**
- Validates both README files for language links, install commands, Cycle stages, CANVAS, hook timing, benchmark links, and absence of retired copy.

- [ ] Write a shell test that checks the required content and resolves relative Markdown links.
- [ ] Run `bash tests/test-readme.sh` and verify RED against the current long README.
- [ ] Commit together with the rewritten README in Task 2.

### Task 2: Rewrite Korean and English landing pages

**Files:**
- Modify: `README.md`
- Modify: `README.en.md`
- Test: `tests/test-readme.sh`

**Interfaces:**
- Produces matching user journeys: understand → install → invoke → learn the loop → find details.

- [ ] Rewrite `README.md` with the approved six-part structure.
- [ ] Rewrite `README.en.md` with the same order and meaning.
- [ ] Run `bash tests/test-readme.sh`, `bash tests/test-plugin-package.sh`, and `git diff --check`.
- [ ] Commit with `docs: README를 사용자 중심으로 전면 개편`.

### Task 3: Deploy documentation

**Files:** none.

- [ ] Fetch origin and confirm local `main` is not behind.
- [ ] Re-run README and plugin validation at final HEAD.
- [ ] Push `main` without changing `v1.0.0`.
- [ ] Verify `origin/main` equals local HEAD and the existing release remains published.

