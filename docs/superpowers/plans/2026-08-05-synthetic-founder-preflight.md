# Synthetic Founder Preflight Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run three isolated Codex subagents as domain-expert, development-novice founders using `riff:riff`, then independently verify the resulting MVPs.

**Architecture:** Keep the preflight separate from official human benchmark results. Three persona prompt packs drive three isolated run directories; the root agent performs acceptance checks after builders finish and records synthetic provenance without personal identifiers.

**Tech Stack:** Markdown prompt packs, Codex `riff:riff`, each generated app's chosen local stack, browser-based acceptance checks.

## Global Constraints

- Synthetic and human results must remain visibly separate.
- Public artifacts disclose `AI founder personas`, `automated or maintainer-operated grading`, and `maintainer-operated, not independent`.
- Persona names, local paths, accounts, machine details, and private transcript content are not published.
- Agents may use Codex native web search without Exa signup or API keys.
- Agents must not read acceptance criteria, other runs, or the Riff source repository.
- A persona may describe domain facts and visible failures but may not supply code, commands, architecture, or debugging diagnoses.

---

### Task 1: Preflight Prompt Packs

**Files:**
- Create: `benchmarks/mvp-bench/preflight/README.md`
- Create: `benchmarks/mvp-bench/preflight/personas/a-salon.md`
- Create: `benchmarks/mvp-bench/preflight/personas/b-reviews.md`
- Create: `benchmarks/mvp-bench/preflight/personas/c-quotes.md`
- Create: `benchmarks/mvp-bench/preflight/acceptance/a-salon.md`
- Create: `benchmarks/mvp-bench/preflight/acceptance/b-reviews.md`
- Create: `benchmarks/mvp-bench/preflight/acceptance/c-quotes.md`

**Interfaces:**
- Consumes: `docs/superpowers/specs/2026-08-05-mvp-bench-design.md`
- Produces: three self-contained persona prompts and three root-only acceptance checklists

- [ ] **Step 1: Write the persona prompts**

Each prompt must include the domain brief, novice knowledge boundary, `riff:riff` invocation, web-research permission, isolation boundary, `FOUNDER_LOG.md` requirement, and exact output directory.

- [ ] **Step 2: Write root-only acceptance checklists**

Each checklist must define critical flows, persistence checks, calculation examples, validation cases, mobile viewport checks, and research-to-decision evidence without revealing implementation selectors.

- [ ] **Step 3: Verify prompt isolation**

Run:

```bash
grep -R "acceptance/\|hidden grader\|other runs" benchmarks/mvp-bench/preflight/personas
```

Expected: only explicit prohibitions, no acceptance details or paths beyond the prohibition.

- [ ] **Step 4: Commit**

```bash
git add benchmarks/mvp-bench/preflight
git commit -m "test: synthetic founder preflight 프롬프트 추가"
```

### Task 2: Three Isolated Synthetic Runs

**Files:**
- Create: `benchmarks/mvp-bench/preflight/runs/a-salon/`
- Create: `benchmarks/mvp-bench/preflight/runs/b-reviews/`
- Create: `benchmarks/mvp-bench/preflight/runs/c-quotes/`

**Interfaces:**
- Consumes: the persona prompt matching each run
- Produces: three runnable MVP repositories, `RESEARCH.md`, `_workspace/CANVAS.md`, and `FOUNDER_LOG.md`

- [ ] **Step 1: Create three empty isolated run directories**

Run:

```bash
mkdir -p benchmarks/mvp-bench/preflight/runs/{a-salon,b-reviews,c-quotes}
```

- [ ] **Step 2: Dispatch persona A, B, and C concurrently**

Each subagent receives only its persona prompt and output directory. It must invoke installed `riff:riff`, research as needed, implement until Riff's PROVE stage passes, and report exact start/run/test commands.

- [ ] **Step 3: Confirm required artifacts exist**

Run:

```bash
for run in a-salon b-reviews c-quotes; do
  test -f "benchmarks/mvp-bench/preflight/runs/$run/RESEARCH.md"
  test -f "benchmarks/mvp-bench/preflight/runs/$run/_workspace/CANVAS.md"
  test -f "benchmarks/mvp-bench/preflight/runs/$run/FOUNDER_LOG.md"
done
```

Expected: exit 0.

### Task 3: Independent Acceptance Verification

**Files:**
- Create: `benchmarks/mvp-bench/preflight/results/a-salon.md`
- Create: `benchmarks/mvp-bench/preflight/results/b-reviews.md`
- Create: `benchmarks/mvp-bench/preflight/results/c-quotes.md`
- Create: `benchmarks/mvp-bench/preflight/RESULTS.md`

**Interfaces:**
- Consumes: three completed run directories and root-only acceptance checklists
- Produces: reproducible commands, pass/fail evidence, screenshots, and a synthetic-only summary

- [ ] **Step 1: Run each app's own checks**

Use the exact install, test, build, and start commands reported by each subagent. Record command, exit status, and failures verbatim in the matching result file.

- [ ] **Step 2: Exercise every acceptance flow in a browser**

Test the checklist at desktop and mobile viewport. Capture screenshots of the primary dashboard and every critical failure.

- [ ] **Step 3: Compare research decisions with the UI**

For every claimed decision in `RESEARCH.md`, record whether it appears in the product, is contradicted, or has no observable effect.

- [ ] **Step 4: Write the synthetic-only summary**

`RESULTS.md` must show completion, critical failures, acceptance percentage, technical intervention count, research traceability, and the disclosure that no result is human evidence.

- [ ] **Step 5: Commit**

```bash
git add benchmarks/mvp-bench/preflight
git commit -m "test: synthetic founder preflight 결과 기록"
```

### Task 4: Convert Findings Into the Human Pilot Harness

**Files:**
- Modify: `docs/superpowers/specs/2026-08-05-mvp-bench-design.md`
- Create: `benchmarks/mvp-bench/README.md`

**Interfaces:**
- Consumes: synthetic failure patterns and brittle acceptance steps
- Produces: only evidence-backed grader requirements for the later nine-run human pilot

- [ ] **Step 1: List preflight defects without changing scores**

Classify each issue as persona leakage, task ambiguity, Riff workflow failure, app defect, or acceptance-check weakness.

- [ ] **Step 2: Update the human-pilot protocol only where evidence requires it**

Do not tune task requirements to make Riff pass. Clarify only ambiguous or non-reproducible requirements, with the preflight result link beside each change.

- [ ] **Step 3: Verify disclosure language**

Run:

```bash
grep -R "Synthetic\|AI founder\|not independent" benchmarks/mvp-bench/README.md benchmarks/mvp-bench/preflight/RESULTS.md
```

Expected: both public entry points clearly distinguish synthetic and human evidence.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-08-05-mvp-bench-design.md benchmarks/mvp-bench/README.md
git commit -m "docs: MVP Bench human pilot 기준 보완"
```
