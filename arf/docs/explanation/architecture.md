# Architecture

## Component Map

ARF is a handful of cooperating components sharing one repository layout. None of them is clever on
its own. The power comes from how they interact.

```text
                        +-----------------+
                        |     Skills      |  (what agents do)
                        +--------+--------+
                           ^     |
                           |     v
         +-----------+     |  +-----------------+
         |   Meta    |<-+  |  |  Specifications |  (what outputs must look like)
         +-----+-----+  |  |  +--------+--------+
               |        |  |           |
               |        |  |           v
               |        |  |  +-----------------+
               |        |  |  |   Verificators  |  (are the outputs valid?)
               |        |  |  +--------+--------+
               |        |  |           |
               v        |  v           v
         +-----------+  |  +-----------------+
         | Aggregators|-+  |     Tasks       |  (folders on disk)
         +-----+-----+     +--------+--------+
               |                    ^
               |  read              |
               +--------------------+
                                    |
                           +--------+--------+
                           |    Utilities    |  (run_with_logs, doi_to_slug, ...)
                           +-----------------+
```

Skills tell agents what to do. Specifications define the shape of the outputs. Verificators check
the shape. Utilities provide the plumbing that connects steps to logs. Meta holds the type
definitions and categories everyone agrees on.

**Aggregators read across tasks to produce combined views — and skills read back through the
aggregators.** This is the non-obvious loop: a task running `/create-task` or `/human-brainstorm`
does not grep `tasks/` by hand; it calls aggregators to see the current effective state (with
corrections applied) and decides what to do next. Tasks generate data, aggregators fold it into
views, skills consume the views, new tasks get created. That is the cycle the whole framework turns
on.

## Skills

[Skills](../reference/skills.md) live under [`arf/skills/`](../../skills/). Agents invoke them
either as slash commands or pick them up automatically when their description matches the situation.
Each skill is one markdown file that tells a subagent how to do one thing: conduct internet
research, write a plan, download a paper, execute an entire task.

Why are skills a separate component? Because the **procedure** for doing something should be
independent of the **format** of what it produces and the **rules** that check correctness. A skill
can be rewritten to try a new approach without changing its target specs. New specs can land without
rewriting every skill. Skills are also the natural unit of subagent isolation — running a skill
spins up a focused subagent with only the context it needs.

## Specifications

[Specifications](../reference/specifications.md) live under
[`arf/specifications/`](../../specifications/). Each one defines the exact format of one kind of
file or folder: what fields must be present, what types they must have, what sections must appear in
what order. They are versioned. Every spec carries a `Version: N` field so files produced under
older specs stay identifiable after the format evolves.

Specs are deliberately boring. They are reference documents, not essays. Their job is to give
skills, verificators, and human reviewers a single source of truth for what a correct X looks like.
When a skill and a verificator disagree, the spec is the arbiter.

## Verificators

[Verificators](../reference/verificators.md) are small Python scripts under
[`arf/scripts/verificators/`](../../scripts/verificators/). Each one checks one thing. Does the task
folder have the required subdirectories? Does the results file have the required sections? Does the
paper asset's metadata match its folder name? Were any files outside the current task touched on the
current branch?

They exist because, as the [concepts](concepts.md) doc puts it, structure is only real if something
checks it. Verificators are designed to be runnable by agents themselves as part of a step, so an
agent can self-correct before committing broken work. They produce two kinds of diagnostics: errors
(genuine structural violations, almost always block) and warnings (quality concerns, do not block).

Verificators are allowed to be noisy and duplicated. Two verificators checking the same thing from
different angles is a feature, not a bug. It catches cases one of them misses.

## Aggregators

[Aggregators](../reference/aggregators.md) are Python scripts that walk the `tasks/` tree and
produce combined views: every suggestion across every task, every paper across every completed task,
every metric filtered by category. They support filtering by category and task ID so consumers can
ask focused questions.

Aggregators are the other half of the no-duplication principle. Data lives in exactly one place, so
any view that spans tasks must be computed on demand. Aggregators are where that computation lives.
They are also where the corrections overlay is applied: when an aggregator reads a completed task's
suggestions, it also reads correction files targeting those suggestions and returns the effective
view. Full model: see [corrections](corrections.md).

Aggregators can be expensive. ARF stores snapshot outputs under [`overview/`](../../../overview/) so
humans can review combined views on GitHub without rerunning the scripts. These snapshots are
regenerated by [`arf/scripts/overview/materialize.py`](../../scripts/overview/materialize.py).

## Utilities

[Utilities](../reference/utilities.md) live under [`arf/scripts/utils/`](../../scripts/utils/). They
are the small, sharp tools everything else depends on.
[`run_with_logs.py`](../../scripts/utils/run_with_logs.py) wraps every command-line invocation in
structured logging. [`doi_to_slug.py`](../../scripts/utils/doi_to_slug.py) converts a DOI to a safe
folder name. [Worktree helpers](../../scripts/utils/worktree.py) create isolated task branches.
Utilities are a separate layer so skills, verificators, and aggregators can share behavior without
duplicating code.

The most important utility is [`run_with_logs.py`](../../scripts/utils/run_with_logs.py). It is the
hinge between doing the work and proving the work happened. Every command that affects the
repository goes through it. Its output becomes part of the audit trail.

## Meta

The `meta/` directory holds the framework's data about itself:
[asset type](../reference/asset_types.md) specs under
[`meta/asset_types/`](../../../meta/asset_types/), category folders under
[`meta/categories/`](../../../meta/categories/), and the global registries for metrics. Meta is
distinct from `project/`, which holds the current project's actual goals and budget, and from
`tasks/`, which holds the work.

The separation matters because meta is generic. A category is a tag. An asset type is a schema.
Neither knows anything about the research domain of the current project. That is what makes ARF
reusable.

## How a Task Runs

Before zooming into a step, a quick picture of the thing that contains steps.

A **task** is the unit of work. It owns a folder under `tasks/t<NNNN>_<slug>/`, a git branch
`task/<task_id>`, and a sequence of stages: preflight, research, planning, implementation, analysis,
reporting. Each stage is made of one or more **steps**. Steps exist inside tasks; a step without a
task does not mean anything.

The orchestrator is the [`execute-task`](../../skills/execute-task/SKILL.md) skill. It reads
`task.json`, decides which optional stages apply based on the `task_type`, and runs the steps in
order. Every step commits to the task branch. When the last step finishes, the task opens a pull
request; merging the PR is how a task becomes part of `main`.

Full stage breakdown: see [task lifecycle](task_lifecycle.md).

## How a Step Runs

A single step is the smallest unit of execution **inside a task**. Walking through one shows how the
components collaborate. Every step has the same shape: **prestep**, **step work**, **format**,
**commit**, **poststep**.

In the [prestep](../../scripts/utils/prestep.py) phase, the agent confirms it is on the correct task
branch, loads [`step_tracker.json`](../../specifications/step_tracker_specification.md), marks the
step as in-progress, and runs verificators that check prerequisites — that earlier required steps
completed and the task folder is in a valid state.

In the step work phase, the agent executes the skill associated with the step. This is where the
actual research, planning, or implementation happens. Every command goes through `run_with_logs.py`,
which records the command, its stdout and stderr, its exit code, and its duration to a log file
under `logs/commands/`. If the agent spawns a subagent, that subagent's work is logged as a step
under `logs/steps/NNN_<step_id>/`.

In the format phase, the agent runs the project's formatting and linting tools on any files it
touched — flowmark on markdown, ruff and mypy on Python. This happens before the commit so the
committed state is always clean.

In the commit phase, the agent creates a single git commit with all the step's changes. The message
references both the task ID and the step ID, giving every step a precise marker in git history.

In the [poststep](../../scripts/utils/poststep.py) phase, the agent updates `step_tracker.json` to
mark the step completed, runs verificators that check the step's output (results files, logs, asset
structure), and hands control back to the orchestrating skill, which decides what comes next.

This cycle repeats for every step. The same scaffolding — verificators, logging, commit per step —
applies whether the step is a thirty-second folder init or a multi-hour training run.

## See Also

* [Task lifecycle](task_lifecycle.md) — how steps are grouped into phases
* [Corrections](corrections.md) — how aggregators reconcile old and new
* [Reference documentation](../reference/) — component-by-component details
* [How-to guides](../howto/) — practical procedures for common operations
