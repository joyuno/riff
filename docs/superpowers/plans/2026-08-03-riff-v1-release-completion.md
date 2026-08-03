# riff v1.0 Release Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the v1-only progress hook, two automated benchmark gates, bilingual documentation, Codex local installation, field validation, and the `v1.0.0` release.

**Architecture:** Keep runtime pieces independent: the progress hook reads only `.riff/state.json`, Python modules perform deterministic benchmark scoring, and thin shell runners orchestrate external commands. Package the existing root skill for both Claude and Codex without copying its source, then validate it through a repo-local marketplace before releasing.

**Tech Stack:** Bash 3.2+, Python 3.9+ standard library, jq, Codex CLI, GitHub CLI, Markdown/JSON.

## Global Constraints

- v1.0 only; do not retain or migrate `.riff/riff-log.json` behavior.
- Do not hard-code a Claude or OpenAI model ID in new benchmark code.
- Default benchmark repetitions are 3 and the speed-tax budget is 15%.
- Preserve `.claude-plugin/` compatibility while adding Codex packaging.
- Do not add the Shorts automation product code to this repository.
- Do not download or republish media without explicit rights evidence.
- Do not stage `.serena/` or `HANDOFF.md`.
- Push, tag, and GitHub Release happen only after all verification gates pass.

---

### Task 0: Restore the portable benchmark baseline

**Files:**
- Create: `benchmarks/tests/test-run-benchmark-bash32.sh`
- Modify: `benchmarks/run-benchmark.sh:437-441`

**Interfaces:**
- `./benchmarks/run-benchmark.sh --dry-run` must run on macOS Bash 3.2 without Bash 4-only builtins.

- [ ] **Step 1: Add a failing regression test**

Invoke the runner through the system `bash`, assert exit 0, six original fixtures, and the completion marker; reject `mapfile: command not found` and `unbound variable`.

- [ ] **Step 2: Verify RED**

Run: `bash benchmarks/tests/test-run-benchmark-bash32.sh`
Expected: FAIL at `mapfile` on Bash 3.2.

- [ ] **Step 3: Replace `mapfile` with a portable read loop**

Populate the local array using `while IFS= read -r entry; do fixture_list+=("$entry"); done` and process substitution. Map the six historical fixture basenames to their ground-truth filenames explicitly so collection is not empty.

- [ ] **Step 4: Verify GREEN and commit**

Run: `bash benchmarks/tests/test-run-benchmark-bash32.sh && bash -n benchmarks/run-benchmark.sh`
Expected: PASS and exit 0.

```bash
git add benchmarks/run-benchmark.sh benchmarks/tests/test-run-benchmark-bash32.sh docs/superpowers/plans/2026-08-03-riff-v1-release-completion.md
git commit -m "fix(bench): Bash 3.2 dry-run 호환 복구"
```

### Task 1: Minimal optional SessionStart hook

**Files:**
- Create: `hooks/tests/test-install.sh`
- Delete: `hooks/riff-progress.sh`
- Delete: `hooks/tests/test-riff-progress.sh`
- Modify: `hooks/install.sh`
- Modify: `hooks/README.md`
- Modify: `README.md`

**Interfaces:**
- Installs only `session-start-canvas.sh` under Claude Code `SessionStart`.
- Removes obsolete Riff `riff-progress.sh` registrations while preserving unrelated hooks and settings.

- [ ] **Step 1: Write failing shell tests**

Seed a temporary settings file with an old Riff progress hook, an unrelated SubagentStop hook, and an unrelated SessionStart hook. Run the installer twice and assert:

```bash
jq -e '[.hooks.SubagentStop[] | select(.command | contains("riff-progress.sh"))] | length == 0' "$settings"
jq -e '[.hooks.SubagentStop[] | select(.command == "bash /other/subagent-hook.sh")] | length == 1' "$settings"
jq -e '[.hooks.SessionStart[] | select(.command | contains("session-start-canvas.sh"))] | length == 1' "$settings"
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `bash hooks/tests/test-install.sh`
Expected: FAIL because the existing installer retains and installs the progress hook.

- [ ] **Step 3: Reduce installer and hook set**

Delete the progress hook. Make the installer remove only Riff progress registrations, preserve unrelated entries, normalize and deduplicate the Riff SessionStart command, and require no per-command hook.

- [ ] **Step 4: Run the hook tests and syntax check**

Run: `bash hooks/tests/test-install.sh && bash -n hooks/*.sh`
Expected: all cases PASS and syntax check exits 0.

- [ ] **Step 5: Rewrite the hooks documentation for v1**

Document that SessionStart runs only at session start/resume, is optional, reads CANVAS STATUS without mutation, is not wired into Codex, and that no per-command or SubagentStop Riff hook remains.

- [ ] **Step 6: Commit**

```bash
git add hooks/ README.md docs/superpowers/specs/2026-08-03-riff-v1-release-completion-design.md docs/superpowers/plans/2026-08-03-riff-v1-release-completion.md
git commit -m "refactor(hooks): SessionStart 안전망만 유지"
```

### Task 2: deterministic speed-tax gate

**Files:**
- Create: `benchmarks/scoring/speed_tax.py`
- Create: `benchmarks/tests/test_speed_tax.py`
- Create: `benchmarks/run-speed-tax.sh`
- Modify: `benchmarks/README.md`

**Interfaces:**
- `calculate_report(baseline_ms: list[int], riff_ms: list[int], budget_percent: float = 15.0) -> dict`
- CLI consumes `--baseline-ms 100,110,105 --riff-ms 110,120,115 --budget-percent 15` and emits JSON.
- Shell runner consumes `BASELINE_COMMAND`, `RIFF_COMMAND`, `REPETITIONS`, and optional `SPEED_TAX_FIXTURE`.

- [ ] **Step 1: Write failing Python tests**

Cover median calculation for odd/even samples, pass at exactly 15%, fail above 15%, zero baseline rejection, non-positive timing rejection, and mismatched/empty sample rejection. Core assertion:

```python
report = calculate_report([100, 110, 105], [110, 120, 115])
assert report["baseline_median_ms"] == 105
assert report["riff_median_ms"] == 115
assert report["overhead_percent"] == 9.5238
assert report["passed"] is True
```

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m unittest benchmarks/tests/test_speed_tax.py -v`  
Expected: import failure because `benchmarks.scoring.speed_tax` does not exist.

- [ ] **Step 3: Implement the calculator and CLI**

Use only `argparse`, `json`, `statistics`, and standard typing. Round overhead to four decimals. Exit 0 for pass, 1 for budget failure, and 2 for invalid input.

- [ ] **Step 4: Run calculator tests and verify GREEN**

Run: `python3 -m unittest benchmarks/tests/test_speed_tax.py -v`  
Expected: all tests PASS.

- [ ] **Step 5: Write a failing runner smoke test**

Add a test that invokes the runner with deterministic sleep-free commands writing prerecorded durations through `--baseline-ms`/`--riff-ms`; assert JSON creation and the process exit code for pass/fail.

- [ ] **Step 6: Run the runner test and verify RED**

Run: `bash benchmarks/tests/test-speed-tax-runner.sh`  
Expected: FAIL because `run-speed-tax.sh` is absent.

- [ ] **Step 7: Implement the shell runner**

Support two modes: prerecorded timings passed to the Python CLI, or actual repeated commands timed in milliseconds. Store the report at `benchmarks/results/speed-tax-<timestamp>.json`. Do not append model flags.

- [ ] **Step 8: Verify runner and document usage**

Run: `bash benchmarks/tests/test-speed-tax-runner.sh && bash -n benchmarks/run-speed-tax.sh`  
Expected: PASS. Replace the README “planned” note with exact prerecorded and live command examples.

- [ ] **Step 9: Commit**

```bash
git add benchmarks/scoring/speed_tax.py benchmarks/tests/test_speed_tax.py benchmarks/tests/test-speed-tax-runner.sh benchmarks/run-speed-tax.sh benchmarks/README.md
git commit -m "feat(bench): speed-tax 15퍼센트 게이트 추가"
```

### Task 3: depth reproducibility scorer and runner

**Files:**
- Create: `benchmarks/scoring/depth_reproducibility.py`
- Create: `benchmarks/tests/test_depth_reproducibility.py`
- Create: `benchmarks/run-depth-reproducibility.sh`
- Modify: `benchmarks/README.md`

**Interfaces:**
- `score_run(output: str, ground_truth: dict) -> dict`
- `score_fixture(outputs: list[str], ground_truth: dict) -> dict`
- CLI consumes one ground-truth JSON plus repeated `--output` paths and emits a fixture report.
- Runner consumes `DEPTH_COMMAND`, `REPETITIONS` (default 3), and optional fixture filter.

- [ ] **Step 1: Write failing scorer tests**

Use Korean sample outputs for: expected `복잡`, allowed `보통+가정선언`, missing STATUS assumption, explicit FRAME skip, build without success criteria, mixed profiles across repeats, and three consistent passes. Assert both per-run validity and `decision_consistent`.

- [ ] **Step 2: Run and verify RED**

Run: `python3 -m unittest benchmarks/tests/test_depth_reproducibility.py -v`  
Expected: import failure because the scorer does not exist.

- [ ] **Step 3: Implement deterministic output parsing and scoring**

Normalize Unicode with NFKC. Recognize explicit depth/profile labels. Map each human ground-truth phrase to concrete evidence predicates rather than generic keyword counts. A forbidden predicate overrides all positive evidence.

- [ ] **Step 4: Run scorer tests and verify GREEN**

Run: `python3 -m unittest benchmarks/tests/test_depth_reproducibility.py -v`  
Expected: all tests PASS.

- [ ] **Step 5: Write a failing runner dry-run test**

Prepare temporary stored outputs for both existing depth fixtures, run the wrapper with `--outputs-dir`, and assert both scenarios appear in the aggregate JSON.

- [ ] **Step 6: Run runner test and verify RED**

Run: `bash benchmarks/tests/test-depth-runner.sh`  
Expected: FAIL because the wrapper is absent.

- [ ] **Step 7: Implement the execution wrapper**

In live mode, pipe each fixture to `DEPTH_COMMAND` exactly three times by default. In stored-output mode, score files without external calls. Store aggregate JSON under `benchmarks/results/` and fail if any fixture has a failed run or inconsistent decision.

- [ ] **Step 8: Verify and document**

Run: `bash benchmarks/tests/test-depth-runner.sh && bash -n benchmarks/run-depth-reproducibility.sh`  
Expected: PASS. Add exact Codex/Claude-neutral command injection examples to the benchmark README.

- [ ] **Step 9: Commit**

```bash
git add benchmarks/scoring/depth_reproducibility.py benchmarks/tests/test_depth_reproducibility.py benchmarks/tests/test-depth-runner.sh benchmarks/run-depth-reproducibility.sh benchmarks/README.md
git commit -m "feat(bench): depth 반복 일관성 자동 채점 추가"
```

### Task 4: Codex package and bilingual documentation

**Files:**
- Create: `.codex-plugin/plugin.json`
- Create: `.agents/plugins/marketplace.json`
- Create: `tests/test-plugin-package.sh`
- Create: `README.en.md`
- Modify: `README.md`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Codex manifest declares `name: riff`, strict-semver `version: 1.0.0`, and `skills: ./skills/`.
- Marketplace name is `joyuno-riff-local`; its local source resolves to the repository root.

- [ ] **Step 1: Write failing package validation**

The shell test must assert manifest presence, matching name/version across both manifests and marketplace entries, an existing skills path, required marketplace policy/category, and no unresolved local source path.

- [ ] **Step 2: Run and verify RED**

Run: `bash tests/test-plugin-package.sh`  
Expected: FAIL because `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json` do not exist.

- [ ] **Step 3: Add Codex manifest and repo marketplace**

Copy shared metadata from the Claude manifest, add `skills: "./skills/"`, and include validated interface fields without nonexistent asset paths. Add marketplace policy `AVAILABLE`/`ON_INSTALL` and category `Developer Tools`.

- [ ] **Step 4: Validate package and manifests**

Run:

```bash
bash tests/test-plugin-package.sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py" .
```

Expected: both exit 0. The absolute validator path is an execution-time tool path and must not be written into repository documentation.

- [ ] **Step 5: Write the English README and language links**

Translate the current README faithfully into `README.en.md`, including identity, lifecycle, adaptive depth, CANVAS, companions/fallbacks, hooks, benchmark commands, Claude install, and Codex local install. Add `[한국어](README.md) | [English](README.en.md)` near the top of both files and remove “English coming soon”.

- [ ] **Step 6: Check documentation references**

Run a local Markdown link checker or a Python standard-library script that validates relative file links. Expected: no missing local targets.

- [ ] **Step 7: Commit**

```bash
git add .codex-plugin/plugin.json .agents/plugins/marketplace.json tests/test-plugin-package.sh README.md README.en.md .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat(plugin): Codex 패키지와 영문 문서 추가"
```

### Task 5: Local Codex install and field smoke test

**Files:**
- Modify only if a verified riff defect is found in Tasks 1-4 files.
- Create outside this repository: a separate Shorts automation project with `_workspace/CANVAS.md`.

**Interfaces:**
- Marketplace selector: `riff@joyuno-riff-local`.
- Field prompt: build an automation that uses open-source models to transform rights-cleared popular-video inputs into reviewed Shorts and distribute them through supported platform APIs.

- [ ] **Step 1: Register the local marketplace**

Run: `codex plugin marketplace add . --json`  
Expected: JSON identifies `joyuno-riff-local`. If already registered, inspect the existing local entry instead of creating a duplicate.

- [ ] **Step 2: Install and inspect riff**

Run:

```bash
codex plugin add riff@joyuno-riff-local --json
codex plugin list
```

Expected: riff is installed from the local marketplace and its cached package contains `skills/riff/SKILL.md` plus references.

- [ ] **Step 3: Run activation smoke tests in fresh Codex executions**

Run direct, indirect, and unrelated prompts without `--model` or `--effort`. Record whether riff activates, whether unrelated work avoids activation, and whether installed references resolve.

- [ ] **Step 4: Start the real Shorts automation FRAME in a separate project**

Create a sibling project directory, invoke riff in a fresh Codex thread, and stop at FRAME approval. The resulting CANVAS must expose active assumptions and unresolved questions about rights, YouTube/platform APIs, data acquisition, human review, attribution, model/runtime, cost, and latency.

- [ ] **Step 5: Test restart restoration**

Start another Codex execution in the Shorts project and verify that CANVAS STATUS is loaded and the next action matches the saved FRAME state.

- [ ] **Step 6: Apply only confirmed riff defects with regression tests**

For each defect, add a failing repository test, verify RED, make the smallest riff change, and verify GREEN. Do not implement the Shorts product inside riff.

- [ ] **Step 7: Reinstall after any plugin change**

Use the plugin-creator cachebuster helper, reinstall from `joyuno-riff-local`, and repeat only the affected smoke tests. Before release, restore all manifests to strict `1.0.0` and perform one final clean install.

- [ ] **Step 8: Commit confirmed field-test fixes**

Use `fix:` plus a Korean summary naming the observed behavior. Skip this commit when no defect is found.

### Task 6: Final verification and v1.0.0 release

**Files:**
- Create: `docs/releases/v1.0.0.md`

**Interfaces:**
- Git tag: annotated `v1.0.0` at verified `main` HEAD.
- GitHub release: `v1.0.0` using `docs/releases/v1.0.0.md` as notes.

- [ ] **Step 1: Write release notes**

Include the FRAME→SHAPE→BUILD→PROVE→LEARN redesign, Living CANVAS, adaptive depth, DROP/TUNE, proof gates, companions/fallbacks, v1 hook, automated benchmarks, Claude/Codex installation, and known boundary that Shorts automation is a separate project.

- [ ] **Step 2: Run the complete verification suite fresh**

```bash
bash hooks/tests/test-install.sh
python3 -m unittest discover -s benchmarks/tests -p 'test*.py' -v
bash benchmarks/tests/test-speed-tax-runner.sh
bash benchmarks/tests/test-depth-runner.sh
bash tests/test-plugin-package.sh
./benchmarks/run-benchmark.sh --dry-run
bash -n hooks/*.sh benchmarks/*.sh
git diff --check
```

Expected: every command exits 0 with no failing tests.

- [ ] **Step 3: Audit release state**

Confirm manifests are exactly `1.0.0`, no tag or release exists, remote is the intended `joyuno/riff`, and staged/untracked files exclude `.serena/` and `HANDOFF.md`. Confirm only `session-start-canvas.sh` remains as a Riff lifecycle hook.

- [ ] **Step 4: Commit release notes**

```bash
git add docs/releases/v1.0.0.md
git commit -m "docs: v1.0.0 릴리스 노트 추가"
```

- [ ] **Step 5: Re-run verification at final HEAD**

Repeat Step 2 and require all exit codes to be 0 before any push or tag.

- [ ] **Step 6: Push main**

Run: `git push origin main`  
Expected: origin/main advances to the verified final HEAD.

- [ ] **Step 7: Create and push the tag**

```bash
git tag -a v1.0.0 -m "riff v1.0.0"
git push origin v1.0.0
```

Expected: remote annotated tag points to the same verified commit.

- [ ] **Step 8: Create and verify the GitHub Release**

```bash
gh release create v1.0.0 --repo joyuno/riff --title "riff v1.0.0 — 질문이 캔버스를 채운다" --notes-file docs/releases/v1.0.0.md
gh release view v1.0.0 --repo joyuno/riff
```

Expected: published release URL, correct tag, title, and notes.
