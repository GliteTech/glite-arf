# Glite Autonomous Research Framework (Glite ARF)

> Run autonomous AI research projects without chaos: every task is isolated, every artifact is
> verified, every step is logged, and completed work is frozen so later runs can build on it without
> breaking it.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/GliteTech/glite-arf/actions/workflows/ci.yml/badge.svg)](https://github.com/GliteTech/glite-arf/actions/workflows/ci.yml)

Glite ARF is a file-based system for running AI-driven research projects with hard structural
guardrails. Every task runs in isolation. Every artifact has a specification. Every step is logged.
Every output is checked by a verificator before it can be committed — guardrails that catch the
mistakes AI agents reliably make.

Fork this repo to bootstrap a new Glite ARF project.

## ⚠️ Read this before you run it

Glite ARF runs AI agents (Claude Code, Codex CLI) **autonomously** with high permissions on your
machine and GitHub account: shell execution, file writes, `git push`, paid LLM API calls, and —
optionally — provisioning remote GPU machines on vast.ai that cost real money.

ARF's verificators, task isolation, and PR-gated workflow contain mistakes — they do not eliminate
them. Before you fork, read [Autonomy and Safety](arf/docs/explanation/safety.md) to understand what
you are consenting to.

## Who made this

Glite ARF is built and maintained by [Glite](https://glite.ai), an AI tutoring company based in
London. We use Glite ARF internally to run research on adaptive assessment and learner modeling.

We also used Glite ARF to run our submission to the British Council
[BEA 2026 Shared Task](https://sig-edu.org/sharedtask/2026), where we placed **first in the closed
track**. Glite ARF ran every stage of the submission: literature review, dataset preparation,
baseline replication, experiment tracking, and the final reporting pass.

If you find Glite ARF useful, we would love to hear about it. If you want to work on problems like
this full-time, [we are hiring](https://jobs.glite.ai).

## Is Glite ARF right for me?

**Yes, if you:**

* Run AI-driven research projects where an autonomous agent executes most of the work
* Need reproducibility across many experiments, not just one run
* Want every artifact to match a known format before it lands on `main`
* Have multiple tasks that can run in parallel in isolated worktrees
* Want aggregated views across tasks that honor a corrections overlay

**No, if you:**

* Want a generic task runner — use Make, Just, or a workflow orchestrator instead
* Are building a production application — Glite ARF is a research harness, not a deployment tool
* Want to keep LLM spend low — ARF runs dozens of autonomous agents per task and burns tokens
  heavily; plan on a top-tier Claude (Max) or Codex (ChatGPT Pro) subscription, or a generous API
  budget
* Do not want to commit to rigid structural rules — the point of the framework is the rules

## What Glite ARF gives you

* **Task isolation.** One task = one folder under `tasks/<task_id>/` = one branch = one PR.
  Subagents run each stage with a bounded context.
* **Mandatory task lifecycle.** Creation → preflight → research → planning → implementation →
  analysis → reporting. Each phase produces specified artifacts in a specified folder.
* **Specifications for every artifact.** `arf/specifications/` and
  `meta/asset_types/*/specification.md` are the source of truth. Every file an agent writes conforms
  to a versioned spec.
* **Verificators enforce structure.** Python scripts in `arf/scripts/verificators/` check task
  folders, logs, results, plans, assets, corrections, metrics, and git rules. Errors block commits.
* **Aggregators collect data across tasks.** `arf/scripts/aggregators/` read all task folders, apply
  the corrections overlay, and emit filtered views by category or task ID. Skills must read through
  aggregators — never by walking task folders directly.
* **Immutability with corrections overlay.** Completed task folders are frozen. Downstream tasks fix
  earlier results by writing correction files into their own folder; aggregators apply them at read
  time.
* **Materialized overview.** `arf/scripts/overview/materialize.py` regenerates `overview/` — a
  committed human-readable dashboard of all aggregator output, reviewable on GitHub.
* **Skills for every operation.** `arf/skills/` holds reusable agent workflows (create-task,
  execute-task, planning, research-papers, implementation, generate-suggestions, compare-literature,
  …), exposed via symlinks in `.claude/skills/` and `.codex/skills/`.
* **Logs for everything.** Every CLI call is wrapped in `arf/scripts/utils/run_with_logs.py`; every
  step writes a log folder; a verificator enforces that logs exist.

Why this exists: autonomous AI agents create mess, write unread prose, and lose debugging state.
Glite ARF imposes hard structure that is checked by scripts, not by trust.

## Top-level layout

```text
arf/            Framework code: scripts, skills, specifications, styleguide, docs, tests
meta/           Project metadata: asset_types/, categories/, metrics/, task_types/
tasks/          One folder per research task (created by the create-task skill)
overview/       Materialized aggregator dashboard (regenerated, committed)
project/        Project-level files: description.md, budget.json (created during setup)
.claude/        Claude Code config (settings.json, rules/, skills/ symlinks)
.codex/         Codex CLI config (agents/, skills/ symlinks)
CLAUDE.md       Project overview loaded at Claude Code session start
pyproject.toml  Python deps and tooling config
doctor.py       Environment validation script
ruff.toml       Lint config
LICENSE         Apache License 2.0
NOTICE          Copyright notice
CITATION.cff    Academic citation metadata
```

## Bootstrap a new project

1. **Fork** this repo on GitHub, clone locally.
2. **Run `/setup-project`** in Claude Code, or `$setup-project` in Codex. The skill shows the safety
   acknowledgement, installs everything it needs (`uv`, Python dependencies, pre-commit hooks, git
   LFS) with explicit consent for each installer, validates the environment with `doctor.py`, guides
   you through `project/description.md` and `project/budget.json`, provisions the paid services the
   project declares, populates `meta/`, replaces this template README with a project-specific
   README, and runs `/human-brainstorm` to plan first tasks.

When setup finishes, execute one of the planned tasks with `/execute-task <task_id>`. Use
`/human-brainstorm` after each completed task to turn its `suggestions.json` into new task folders,
and open `overview/README.md` to inspect aggregated results.

Follow the full walkthrough at [`arf/docs/tutorial/`](arf/docs/tutorial/).

## Key rules (enforced by verificators)

* **Every CLI call** is wrapped in `uv run python -m arf.scripts.utils.run_with_logs <cmd>` so logs
  are captured.
* **Tasks only modify files inside their own folder.** The only top-level files a task may touch are
  `pyproject.toml`, `uv.lock`, `ruff.toml`, and `.gitignore`.
* **Every task stage and every action is a separate, well-described commit.**
* **Completed task folders are immutable.** Fix mistakes via correction files in a new task, never
  by editing past folders.
* **Read through aggregators, never walk task folders directly.** Raw globs miss the corrections
  overlay. This is the single hardest rule to follow.
* **Metrics must be registered in `meta/metrics/` before a task reports them.** Unregistered metrics
  fail verification.
* **No human intervention for anything a script can resolve** (merge conflicts, log generation,
  etc.). Genuine blockers produce a file in the task's `intervention/` folder.

## Security warning: permissive AI agent permissions

Glite ARF ships a `.claude/settings.json` (and an equivalent `.codex` configuration) with a broad
allow-list so autonomous agents can drive the whole task lifecycle without repeated permission
prompts:

```json
"allow": [
  "Read(*)", "Edit(*)", "Write(*)",
  "Glob(*)", "Grep(*)", "Bash(*)",
  "WebFetch(*)", "WebSearch(*)"
]
```

This allow-list gives the AI agent unrestricted shell and filesystem access inside the repo and its
worktrees. **Review and adjust it before running Glite ARF on machines with sensitive data, access
to production credentials, or unattended long-running sessions.** Consider:

* Running agents inside a sandboxed VM, container, or dedicated user account
* Narrowing `Bash(*)` to a concrete allow-list if you have specific security requirements
* Disabling `WebFetch(*)` and `WebSearch(*)` if you need reproducible, offline-only runs
* Using Git worktrees so a rogue agent cannot touch unrelated projects in your home directory

Glite ARF assumes the operator trusts the AI agent to operate within the repo. It is not a sandbox.
The mitigation is the verificator layer, which blocks any commit that violates structural rules —
but it does not prevent arbitrary side effects during a session.

## Where to read next

* [`arf/docs/explanation/concepts.md`](arf/docs/explanation/concepts.md) — the fundamental
  principles and the problem Glite ARF solves
* [`arf/docs/explanation/architecture.md`](arf/docs/explanation/architecture.md) — how skills,
  specifications, verificators, aggregators, and meta fit together
* [`arf/docs/explanation/task_lifecycle.md`](arf/docs/explanation/task_lifecycle.md) — every phase
  from creation to merge
* [`arf/docs/explanation/corrections.md`](arf/docs/explanation/corrections.md) — immutability and
  the corrections overlay
* [`arf/docs/tutorial/`](arf/docs/tutorial/) — five-page walkthrough from empty fork to first
  results
* [`arf/docs/howto/`](arf/docs/howto/) — daily operations (run a task, brainstorm, apply a
  correction, debug verificators, add a category)
* [`arf/docs/reference/`](arf/docs/reference/) — glossary, task folder structure, specifications,
  verificators, aggregators, skills, utilities

## Source of truth

Specs in [`arf/specifications/`](arf/specifications/) and [`meta/asset_types/`](meta/asset_types/)
are authoritative. The prose in `arf/docs/` synthesizes and links to them; it never replaces them.
Specs and skills carry plain-integer version numbers (`**Version**: N`); files produced under a spec
carry a matching `spec_version` field.

Everything under `arf/` and most of `meta/` is framework-generic. Project-specific content lives in
`project/` and `tasks/`.

## Contributing

Contributions are welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md) for scope, development setup,
quality checks, and the process for proposing a new specification, verificator, aggregator, or
skill.

## Citing Glite ARF

If you use Glite ARF in your research, please cite it using the metadata in
[`CITATION.cff`](CITATION.cff). GitHub renders a "Cite this repository" button from that file for
both BibTeX and APA output.

```bibtex
@software{glite_arf_2026,
  author = {{Glite Tech Ltd} and Philippov, Vassili},
  title = {{Glite Autonomous Research Framework (Glite ARF)}},
  year = {2026},
  url = {https://github.com/GliteTech/glite-arf},
  license = {Apache-2.0}
}
```

## License

Glite ARF is released under the [Apache License 2.0](LICENSE). Copyright 2024-2026 Glite Tech Ltd.
See [`NOTICE`](NOTICE) for attribution details.
