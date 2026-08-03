# Riff

[한국어](README.md) | **English**

> **Right questions, right products.**

Riff is a question-driven product-development skill for Claude Code and Codex. It turns an
ambiguous product brief into a maintained `CANVAS.md`, then moves through a repeating cycle:

```text
FRAME → SHAPE → BUILD → PROVE → LEARN
```

Event stages sit outside the hot path: **DROP** lands a jam safely, while **TUNE** reduces
accumulated complexity. Riff v1.0 uses adaptive depth, explicit proof gates, cycle commit anchors,
and progressive disclosure from one skill into focused references.

## Quick start

### Claude Code

```text
/plugin marketplace add joyuno/riff
/plugin install riff@joyuno-riff
```

Optional CANVAS restoration hook:

```bash
bash hooks/install.sh
```

The hook runs once when a Claude Code session starts or resumes. Riff has no per-command hook.

### Codex local development

```bash
codex plugin marketplace add .
codex plugin add riff@joyuno-riff-local
```

Start a new Codex thread after installation so the installed skill is loaded. The Codex package
does not install the Claude-specific SessionStart hook.

Try:

```text
Use Riff to shape and build this product idea.
Resume this project from its Living CANVAS.
Run a Riff proof cycle on the current implementation.
```

## Why Riff?

Coding agents can produce code quickly, but speed amplifies a weak problem definition. Riff makes
the agent expose assumptions, define observable success, and preserve decisions before committing
to implementation. The project remains restartable from one document instead of relying only on
chat history.

## Living CANVAS.md

`_workspace/CANVAS.md` is the single source of truth:

```text
STATUS       current Cycle, stage, progress, active assumptions, next action
[1] FRAME    problem, users, constraints, success criteria
[2] SHAPE    explored directions and selected approach
[3] BUILD    task board and contract status
[4] PROVE    verification evidence and diff review
[5] LEARN    decisions, antibodies, and the next-cycle brief
```

Large details go into `_workspace/detail/`; contracts go into `_workspace/contracts/`. CANVAS
remains compact, current, and single-writer.

## Adaptive depth

Riff evaluates eight signals: brief clarity, integration uncertainty, reversibility, security,
data migration, UX ambiguity, failure cost, and cross-domain impact.

| Signals | Profile | Typical path |
|---|---|---|
| 0–3 | Simple | Declare assumptions, skip safely, PROVE-lite |
| 4–5 | Medium | Two FRAME questions, Tier 0–2 proof, one diff review |
| 6–8 | Complex | Full FRAME, jam when useful, Tier 0–3 proof |

Words such as “quick” or “simple” never lower depth by themselves. If a skipped concern later
fails, Riff escalates and retroactively performs the omitted stage.

## The cycle

### FRAME

Clarify the job, users, constraints, risks, and measurable acceptance criteria. A skipped FRAME
requires an explicit assumption declaration in STATUS.

### SHAPE

Compare viable directions. A **Jam** uses isolated worktrees only when alternatives genuinely
benefit from parallel exploration. Results collapse into one recommendation plus supporting detail.

### BUILD

Execute a graded task board. Work stays inline by default; spawning is reserved for jams, two or
more independent tasks, or context pressure. Parallel work requires explicit contracts.

### PROVE

Run the proof tier selected by depth:

- Tier 0: canvas lint and mechanical consistency
- Tier 1: syntax, static checks, and focused tests
- Tier 2: behavior, acceptance, secret scan, and diff review
- Tier 3: live application and browser-based QA when applicable

Each cycle gets one Critical/Minor diff review. A Critical result blocks LEARN.

### LEARN

Deduplicate lessons, verify bug antibodies red-to-green, update CANVAS, obtain an
approve/request-changes verdict, and create a `cycle-N:` commit anchor. `.riff/state.json` stores
the current cycle and last anchor.

## Event stages

- **DROP:** choose merge, PR, keep, or discard; clean worktrees; run security checks and canaries.
- **TUNE:** review every three to five cycles, after rewinds, or after no-progress signals; prune
  stale decisions and consolidate antibodies.

## Companions and fallbacks

Riff can use `ralph-loop`, Codex cross-checks, or ECC plan-canvas, but none is required. Every
companion has a built-in fallback: manual retry, inline review, or a terminal verdict prompt.

## Hooks

Riff ships one optional Claude Code hook:

| File | Event | Purpose |
|---|---|---|
| `hooks/session-start-canvas.sh` | SessionStart | Inject at most 12 STATUS lines when CANVAS exists |

It does not run for every command, does not modify CANVAS, and is not automatically wired into
Codex. See [hooks/README.md](hooks/README.md).

## Benchmarks

```bash
cd benchmarks

# Existing quality fixtures, no model call
./run-benchmark.sh --dry-run

# Deterministic speed-tax calculation
./run-speed-tax.sh --baseline-ms 1000,1050,1100 --riff-ms 1100,1150,1200

# Repeated depth decisions from stored outputs
./run-depth-reproducibility.sh --outputs-dir ./saved-depth-outputs --repetitions 3
```

The speed budget is a median wall-clock overhead of at most 15%. Depth reproducibility requires
every run to satisfy the ground truth and all repeated runs to choose the same profile. See
[benchmarks/README.md](benchmarks/README.md).

## Project structure

```text
riff/
├── .claude-plugin/              Claude marketplace metadata
├── .codex-plugin/plugin.json    Codex plugin manifest
├── .agents/plugins/             local Codex marketplace
├── skills/riff/
│   ├── SKILL.md                 workflow entry point
│   └── references/              FRAME through LEARN, events, proof, contracts
├── hooks/                       optional SessionStart hook and installer
├── benchmarks/                  fixtures, scorers, and runners
└── README.md / README.en.md
```

## Requirements

- Claude Code or Codex
- Python 3.9+ and jq for benchmark tooling
- Playwright MCP only when Tier 3 live QA requires it

## License

MIT
