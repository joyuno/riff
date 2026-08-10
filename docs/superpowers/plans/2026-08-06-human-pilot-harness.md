# MVP Bench Human Pilot Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create, seal, grade and summarize nine anonymous Riff/GSD/gstack human-pilot runs with one reproducible command-line tool.

**Architecture:** A dependency-free Python CLI owns run IDs, randomized assignments, immutable metadata hashes and aggregate results. Hidden task adapters emit a small JSON check-result contract; the CLI validates that contract and computes success without knowing the harness identity. Browser-driving adapters remain separate so the scoring core can be tested without a browser dependency.

**Tech Stack:** Python 3.10 standard library, `unittest`, JSON, SHA-256.

## Global Constraints

- Three tasks × three harnesses produce exactly nine runs.
- Public run IDs do not contain task, harness or participant identity.
- AI preflight and human pilot results never share a result table.
- Success requires zero critical failures, at least 90% scored checks, persistence and research evidence.
- Raw check results remain available; no weighted composite score is invented.
- Browser adapters must be validated before the first official run and are not simulated by the scoring core.

---

### Task 1: Anonymous Run Initialization

**Files:**
- Create: `benchmarks/mvp-bench/bench.py`
- Create: `benchmarks/mvp-bench/tests/test_bench.py`

**Interfaces:**
- Produces: `init_pilot(root: Path, seed: str) -> dict`
- Produces: nine `runs/run-*/metadata.json` files and private `pilot/assignments.json`

- [x] Write a failing test that asserts nine opaque, unique run IDs and a balanced 3×3 assignment.
- [x] Run `python3 -m unittest benchmarks/mvp-bench/tests/test_bench.py` and confirm the missing module failure.
- [x] Implement only deterministic initialization, collision protection and SHA-256 protocol hashing.
- [x] Run the test and confirm it passes.

### Task 2: Blind Result Grading

**Files:**
- Modify: `benchmarks/mvp-bench/bench.py`
- Modify: `benchmarks/mvp-bench/tests/test_bench.py`
- Create: `benchmarks/mvp-bench/grader/check-result.schema.json`

**Interfaces:**
- Consumes: run-local `checks.json` containing `id`, `critical`, `passed`, `evidence`
- Produces: `grade_checks(checks: list[dict]) -> dict`

- [x] Write failing tests for 90% pass, critical failure, missing persistence and missing research evidence.
- [x] Confirm the tests fail because grading is absent.
- [x] Implement strict input validation and the success rule without harness access.
- [x] Confirm all tests pass.

### Task 3: Seal and Aggregate

**Files:**
- Modify: `benchmarks/mvp-bench/bench.py`
- Modify: `benchmarks/mvp-bench/tests/test_bench.py`
- Create: `benchmarks/mvp-bench/protocol.md`

**Interfaces:**
- Produces CLI commands: `init`, `grade`, `report`, `verify`
- Produces `pilot/results.json` and a Markdown result table grouped by harness only after grading

- [x] Write failing tests for tamper detection and median/result aggregation.
- [x] Implement SHA-256 sealing and deterministic report output.
- [x] Document the exact operator workflow and disclosure language.
- [x] Run all harness tests and existing preflight checks.

### Task 4: Browser Task Adapters

**Files:**
- `benchmarks/mvp-bench/grader/riff_preflight_playwright.py`
- `benchmarks/mvp-bench/grader/fixtures/{pass,fail}/{a-salon,b-reviews,c-quotes}/`
- `benchmarks/mvp-bench/grader/test_grader.py`

**Interfaces:**
- Consumes: a running app URL and hidden task criteria
- Produces: schema-valid `checks.json`

- [x] Select one browser runtime only after it is installable in the official runner environment.
- [x] Build success and failure fixtures for each of the three tasks.
- [x] Prove each adapter accepts the success fixture and rejects the failure fixture.
- [x] Run desktop, reload and 390px checks before any official human run.

Browser runtime is Playwright Chromium: it is the only runtime that completed localhost bind, click, `page.reload()` and the 390px viewport end to end in the official runner environment (`benchmarks/mvp-bench/grader/BROWSER-BLOCKER.md`, 2026-08-07 local rerun).

Discrimination proof: `cd benchmarks/mvp-bench/grader && python3 -m unittest test_grader -v` grades both fixture sets with the same `grade_*` functions. `pass` returns zero critical failures on all three tasks; `fail` fails exactly the one check each fixture removed (`booking-conflict`, `persistence`, `vat-total`). Desktop 1280×900, `page.reload()` and the 390px viewport all run inside those graded passes.

Task 4 is a hard gate for the human pilot. Tasks 1–3 may ship first; no official run may start before Task 4 passes.
