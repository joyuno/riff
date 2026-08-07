<p align="center">
  <img src="https://img.shields.io/badge/RIFF-Right_Questions,_Right_Products-7B2FF7?style=for-the-badge" alt="Riff">
</p>

<p align="center">
  <a href="https://github.com/joyuno/riff/releases/tag/v1.0.0"><img src="https://img.shields.io/badge/version-1.0.0-brightgreen" alt="v1.0.0"></a>
  <img src="https://img.shields.io/badge/Claude_Code-supported-purple" alt="Claude Code">
  <img src="https://img.shields.io/badge/Codex-supported-black" alt="Codex">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT"></a>
</p>

<p align="center"><strong>Questions fill the canvas.</strong><br>Right questions, right products.</p>

[한국어](README.md) | **English**

# Riff

Riff is a development workflow that turns an ambiguous app, MVP, or automation idea into
clear decisions and working software. It runs in Claude Code and Codex and keeps the current
state in one Living `CANVAS.md`.

```text
FRAME → SHAPE → BUILD → PROVE → LEARN
```

Even when a conversation grows long or a session restarts, CANVAS shows where the project is and
what should happen next.

## 3-minute Quick Start

### Claude Code

```text
/plugin marketplace add joyuno/riff
/plugin install riff@joyuno-riff
```

Then start a new conversation:

```text
Use Riff to turn this idea into a product.
```

### Codex

Register this repository as a local marketplace and install the plugin:

```bash
codex plugin marketplace add .
codex plugin add riff@joyuno-riff-local
```

Open a new Codex thread after installation. For example:

```text
Start a new project with Riff. The idea is video-editing automation.
```

### Optional Claude Code hook

```bash
bash hooks/install.sh
```

This installs only `session-start-canvas.sh`. It restores CANVAS STATUS once when a Claude Code
session starts or resumes; it **does not run for every command or file edit**. Codex does not
automatically install this Claude-specific hook.

Details: [hooks/README.md](hooks/README.md)

## How it works

| Stage | What happens | What remains |
|---|---|---|
| **FRAME** | Use Exa research and follow-up questions to clarify users, missing needs, constraints, and success | Evidence, assumptions, and acceptance |
| **SHAPE** | Compare viable directions and trade-offs | Selected approach and decision log |
| **BUILD** | Implement in small, explicit tasks | Working software |
| **PROVE** | Run tests, behavior checks, and diff review | Pass/fail evidence |
| **LEARN** | Record lessons and recurrence guards | Next Cycle and commit anchor |

Riff repeats short Cycles instead of trying to be perfect in one pass. When evidence fails, it
returns to FRAME or SHAPE to correct the underlying assumption instead of blindly retrying.

### Living CANVAS.md

Every Riff project resumes from `_workspace/CANVAS.md`:

```text
STATUS       current Cycle, stage, active assumptions, next action
[1] FRAME    problem and success criteria
[2] SHAPE    selected direction and decisions
[3] BUILD    task board and contract status
[4] PROVE    verification results and evidence
[5] LEARN    lessons and next Cycle
```

Long research and contracts live under `_workspace/detail/` and `_workspace/contracts/`, keeping
CANVAS compact and current.

## When should you use it?

**Good fits**

- A new web app, mobile app, or MVP
- Business automation or an AI pipeline
- A new product with unclear requirements
- A project connecting several external APIs and data flows
- Work that needs repeated implementation, proof, and learning

**Usually unnecessary**

- Typo fixes
- Small bugs with a known cause
- A tightly scoped single-function change
- Explanation-only or code-review requests

For small tasks, the normal Claude Code or Codex workflow is faster.

## Core capabilities

### Domain Intelligence

Riff does not use one generic search method for clinical, legal, operational, SaaS, creative, and
AI work. Its Domain Research Router selects an evidence method from the domain's knowledge family,
risk, jurisdiction, and freshness needs.

Exa findings become a Domain Model of actors, jobs, artifacts, lifecycle, rules, and exceptions.
A Knowledge Ledger records evidence state and preserves the trace from confirmed knowledge to
acceptance, implementation, and PROVE. Search findings never become features automatically.

The bundled Exa MCP starts with its keyless free path. If it is unavailable or rate-limited, Riff
falls back to the host's web search instead of stopping the beginner flow for signup.

### Adaptive depth

Eight signals—including clarity, external dependencies, security, reversibility, and failure
cost—select a simple, medium, or complex profile. Words such as “quick” never lower proof depth
on their own.

### Evidence-driven PROVE

Riff selects static checks, tests, acceptance verification, secret scanning, diff review, and live
QA according to depth. Completion comes from executed evidence, not a model saying it is done.

### Cycle commit anchors

Each verified Cycle creates a `cycle-N:` commit. If repeated failures require a rewind, Riff first
preserves the evidence and then returns to a known anchor.

### DROP and TUNE

- **DROP:** land an experiment through merge, keep, or discard
- **TUNE:** prune accumulated decisions, rules, and context after several Cycles

They are event stages, not mandatory ceremony in every Cycle.

### Optional companions

Riff works without external companions. When available they strengthen adversarial review or retry
loops; otherwise the workflow uses inline fallbacks. Inside Codex, Riff does not re-run
Claude-specific companion installation.

## Benchmarks

```bash
cd benchmarks

# Check the existing pipeline without API calls
./run-benchmark.sh --dry-run

# Evaluate wall-clock overhead against the default 15% budget
./run-speed-tax.sh --baseline-ms 1000,1050,1100 --riff-ms 1100,1150,1200

# Score repeated depth decisions from stored outputs
./run-depth-reproducibility.sh --outputs-dir ./saved-depth-outputs --repetitions 3
```

See [benchmarks/README.md](benchmarks/README.md) for live command integration and result formats.

## Repository structure

```text
riff/
├── .claude-plugin/              Claude Code plugin metadata
├── .codex-plugin/plugin.json    Codex plugin manifest
├── .mcp.json                    bundled Exa search
├── .agents/plugins/             local Codex marketplace
├── skills/riff/
│   ├── SKILL.md                 workflow entry point
│   └── references/              stage-specific rules
├── hooks/                       optional SessionStart hook
├── benchmarks/                  fixtures, scorers, and runners
└── README.md / README.en.md
```

Read [`skills/riff/SKILL.md`](skills/riff/SKILL.md) and
[`skills/riff/references/`](skills/riff/references/) for implementation details.

## Requirements

- Claude Code or Codex
- Internet access for requirement discovery (host search is the Exa fallback)
- Python 3.9+ and jq for benchmarks
- Whatever build, test, or browser tools the target project actually uses

## License

[MIT](LICENSE)
