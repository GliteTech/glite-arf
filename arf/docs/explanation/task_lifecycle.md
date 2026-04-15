# Task Lifecycle

## Overview

An ARF task is not free-form. It moves through a fixed sequence of phases. Each phase has a defined
purpose and a defined set of outputs. Some phases are mandatory, some optional. The order never
changes.

```text
   creation  -->  preflight  -->  research  -->  planning
                                  (optional)    (optional)
                                                     |
                                                     v
   reporting  <--  analysis  <--  implementation  <--+
                  (optional)
```

Creation sets up a new task folder with status `not_started`. Preflight makes the task runnable.
Research gathers what is already known. Planning turns that into an executable plan. Implementation
does the work. Analysis interprets the results. Reporting writes them up and proposes what comes
next.

This is not a bureaucratic checklist. Each phase exists because skipping it produces a specific,
recurring failure. The phases are the failure modes made explicit.

## Phase 0: Creation

Tasks are created through [brainstorming](../../skills/human-brainstorm/SKILL.md) sessions. The
`/human-brainstorm` skill reviews the current project state — open suggestions, in-flight tasks,
budget, recent findings — and walks the researcher through accepting, rejecting, or deferring each
candidate. Accepted suggestions are turned into new task folders by the
[`create-task`](../../skills/create-task/SKILL.md) skill (which the brainstorm session calls for
you; `/create-task` can also be invoked directly when you know exactly what you want). Creation is
gated on purpose. Arbitrary agents are not allowed to spawn new tasks. Uncontrolled task creation is
the fastest way to turn a research project into a mess.

After creation, the task folder contains
[`task.json`](../../specifications/task_file_specification.md) (status `not_started`, name,
description, dependency list, expected assets) and an optional longer description file. Nothing
else. The branch does not exist. The step tracker does not exist. The task is a declaration of
intent waiting for an agent to pick it up.

## Phase 1: Preflight

Preflight is bootstrapping. Its three steps — `create-branch`, `check-deps`, and `init-folders` —
guarantee that the task starts real work from a known clean state.

The `create-branch` step creates a new git branch named `task/<task_id>` from `main` and moves the
agent's working tree to it, usually via a worktree. From this point on, every change lives on a
branch that will eventually become a pull request.

The `check-deps` step runs a [verificator](../../scripts/verificators/verify_task_dependencies.py)
that loads the task's dependency list from `task.json` and confirms every dependency exists and has
status `completed`. If a dependency was corrected by a later task, a warning fires so planning can
account for it. This is what stops tasks from running against stale inputs.

The `init-folders` step creates the
[mandatory folder structure](../../specifications/task_folder_specification.md) via
[`init_task_folders.py`](../../scripts/utils/init_task_folders.py):

```text
tasks/t<NNNN>_<slug>/
├── task.json
├── task_description.md
├── step_tracker.json
├── plan/
├── research/
├── assets/
├── results/
├── corrections/
├── intervention/
└── logs/
```

The `step_tracker.json` is written during the `create-branch` step with every step the task intends
to run.

After preflight, the task has a folder, a branch, a step tracker, and an empty logs directory. Its
status in `task.json` becomes `in_progress`.

## Phase 2: Research (Optional)

Research is where the task figures out what is already known before committing to an approach. The
goal is bigger than "read a few papers": **every task should be implemented with the full body of
knowledge the world has on the topic plus everything this project has already discovered in earlier
tasks**. No blind spots, no reinventing the wheel, no repeating a failed experiment from three
months ago. Three independent subagent-driven steps achieve this:
[`research-papers`](../../skills/research-papers/SKILL.md) (papers already in the project's corpus),
[`research-internet`](../../skills/research-internet/SKILL.md) (search for new material on the web
and in published literature), and [`research-code`](../../skills/research-code/SKILL.md) (relevant
code and findings from prior tasks in this project). Each produces a focused markdown document in
`research/`.

Why split it three ways? Because mixing "what papers say" with "what our previous code does"
produces muddled conclusions. Separating them forces each stream to stand on its own. A simple task
may skip this phase. But every time a task skips research and then fails because "we didn't know
there was already a library for that," the skip was a mistake.

**Research produces assets, not just notes.** When `research-internet` finds a paper worth keeping,
the step invokes [`add-paper`](../../skills/add-paper/SKILL.md) to download it, write its summary,
and register it as a [paper asset](../../../meta/asset_types/paper/) under `assets/paper/`. Those
papers stay in the project forever. The next task's `research-papers` step will see them through the
[papers aggregator](../reference/aggregators.md). This is how the project's literature corpus grows
— one task at a time, always attached to the task that brought each paper in.

The three research documents are not free-form notes. Each has a structured format with mandatory
sections, enforced by its verificator:
[`research_papers.md`](../../specifications/research_papers_specification.md),
[`research_internet.md`](../../specifications/research_internet_specification.md),
[`research_code.md`](../../specifications/research_code_specification.md). The structure is
deliberate. A free-form "summary" is easy to half-finish; a spec with required sections forces the
agent to actually cover every angle — methodology, results, gaps, recommendations — and surfaces the
gaps the agent would otherwise skip.

After research, `research/` contains the subset of `research_papers.md`, `research_internet.md`, and
`research_code.md` the task chose to produce, plus new paper assets under `assets/paper/`.

## Phase 3: Planning (Optional)

[Planning](../../skills/planning/SKILL.md) turns research into a concrete plan in
[`plan/plan.md`](../../specifications/plan_specification.md). The plan specifies the objective, the
approach, a cost estimate, the step-by-step sequence, any remote machines needed, the input assets,
the expected output assets, a time estimate, the risks and fallbacks, and the verification criteria
that decide whether the task succeeded.

Why is this its own phase? Research produces breadth. Implementation demands depth. The transition
between them is where most wasted effort comes from. Forcing the task to commit to a plan before
implementing means the cost estimate and success criteria are written while the team still has
perspective — not after a week sunk into the wrong approach.

## Phase 4: Implementation

Implementation does the work. Three steps: optional
[`setup-machines`](../../skills/setup-remote-machine/SKILL.md), the mandatory
[`implementation`](../../skills/implementation/SKILL.md), and optional `teardown`. Remote setup and
teardown only matter when the task needs compute beyond the local machine.

**The task's job is to produce the assets the plan committed to.** A training task writes a
[model asset](../../../meta/asset_types/model/). A benchmark writes a
[predictions asset](../../../meta/asset_types/predictions/). A data-prep task writes a
[dataset asset](../../../meta/asset_types/dataset/). A library task writes a
[library asset](../../../meta/asset_types/library/). Each lands under `assets/<type>/<asset_id>/`
inside the task folder, validated against its asset type spec.

The shape of the work depends on the **task type**. Every task declares `task_types` in `task.json`
— a list of slugs from [`meta/task_types/`](../../../meta/task_types/). Each task type ships with
its own `instruction.md` — planning guidelines, implementation guidelines, common pitfalls,
verification additions — that the planning and implementation skills read on top of their generic
instructions. A `baseline-evaluation` task gets baseline-specific guardrails. A `write-library` task
gets library-specific ones. Task types are **project-specific**. Start from the defaults, customize
them, add new ones when a new kind of work appears. See
[How to add a task type](../howto/add_a_task_type.md).

Every command goes through [`run_with_logs.py`](../../scripts/utils/run_with_logs.py). If the task
needs human intervention — a credential, an approval, a manual download — the agent writes a file
under `intervention/` and pauses. Full execution model: the [architecture](architecture.md) doc.

After implementation, the assets are the task's permanent contribution to the project. Every later
task that consumes them reads them through the [aggregators](../reference/aggregators.md), with any
corrections applied.

## Phase 5: Analysis (Optional)

Analysis turns raw outputs into meaning. Up to three steps: `creative-thinking`, `results`, and
[`compare-literature`](../../skills/compare-literature/SKILL.md). The results step is mandatory. It
produces the required files in [`results/`](../../specifications/task_results_specification.md):
`results_summary.md`, `results_detailed.md`, `metrics.json`, `costs.json`, and
`remote_machines_used.json`.

Why split analysis from implementation? Interpreting results well requires stepping back from the
code. An agent that just spent two hours debugging a training script is in exactly the wrong frame
of mind to do that. Running analysis as a separate subagent gives it a clean context and forces the
task to articulate what actually happened — in prose and in numbers — before moving on.

## Phase 6: Reporting

Reporting closes the loop. Two mandatory steps:
[`suggestions`](../../skills/generate-suggestions/SKILL.md) and `reporting`. The first writes
[`suggestions.json`](../../specifications/suggestions_specification.md) (proposals fed back into the
suggestions chooser for future task creation). The second handles final reporting duties — uploading
artifacts to external trackers, running the full verificator pass, and marking the task completed in
`task.json`. The final action is opening the pull request and merging it.

Reporting exists so every task ends with the same question: **what did we learn, and what should be
done next?** Without an explicit suggestion step, useful follow-up ideas stay trapped inside the
implementation agent's context and disappear when that agent exits.

## Step Tracker Mechanics

The `step_tracker.json` file is the single source of truth for what steps a task intends to run and
where each one stands. It is populated during `create-branch` with every planned step, including
skipped ones. Each step has a status that moves from `pending` to `in_progress` to `completed` or
`skipped`. Each step records its started and completed timestamps and the path to its log folder.

Step numbering is sequential and task-local. The first step is 1, the second is 2, and so on,
regardless of which canonical steps were skipped. Skipped steps still appear in the tracker so the
audit trail is complete. No gaps. The full step ID catalog and naming rules live in the task steps
reference.

## Git Workflow

One task = one folder = one branch = one pull request. Every step produces a single, well-described
commit whose message references both the task ID and the step ID. `git log` reads as a summary of
the task's history. The branch is created from `main` during preflight, lives in its own worktree
for the duration of the task, and is merged back into `main` via pull request as part of reporting.

The commit-per-step rule is not cosmetic. It is what lets a human reviewer browse a task after the
fact and understand what happened stage by stage. It is also what lets the corrections mechanism
target specific earlier state.

## What Files Exist When

| Phase | Files present at end of phase |
| --- | --- |
| Creation | `task.json`, `task_description.md` |
| Preflight | `task.json`, `step_tracker.json`, empty `logs/`, empty `plan/` `research/` `results/` `assets/` `corrections/` `intervention/` |
| Research | Above, plus the produced `research/*.md` files |
| Planning | Above, plus `plan/plan.md` |
| Implementation | Above, plus populated `assets/` subfolders and `logs/` entries |
| Analysis | Above, plus `results/results_summary.md`, `results/results_detailed.md`, `results/metrics.json`, `results/costs.json`, `results/remote_machines_used.json` |
| Reporting | Above, plus `results/suggestions.json` and a completed-status `task.json` |

## See Also

* [Concepts](concepts.md) — the principles behind this lifecycle
* [Architecture](architecture.md) — the components that implement it
* [Corrections](corrections.md) — how completed tasks can still be fixed
* [Reference documentation](../reference/) — exact field and step definitions
* [Tutorial](../tutorial/) — walk through creating and running a task
