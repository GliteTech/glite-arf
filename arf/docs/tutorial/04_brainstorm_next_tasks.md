# 4. Brainstorm Next Tasks

In [part 3](03_run_your_first_task.md) the literature survey landed, and its
`results/suggestions.json` holds a handful of follow-up ideas the agent generated. Now decide which
of those to actually run.

That decision is interactive. It belongs to you, not an agent. Use the
[`human-brainstorm`](../../skills/human-brainstorm/SKILL.md) skill: it pulls together every open
suggestion, every in-flight task, and every recent finding, then walks you through choosing what to
do next.

## Step 1: Run human-brainstorm

From your project root:

```text
/human-brainstorm   # Claude Code
$human-brainstorm   # Codex
```

The skill aggregates project state automatically (no arguments). It runs the task aggregator, the
suggestion aggregator, and the cost aggregator, then summarizes:

* What just completed and what it found
* Open suggestions, grouped by priority and kind
* Tasks that are queued, blocked, or in progress
* How much budget is left

It then presents the suggestions one at a time and asks you to **accept**, **reject**, **adjust**,
or **defer** each one.

## Step 2: Make Decisions

For this tutorial, two augmentation suggestions are worth picking up:

* `S-0001-01` Train ResNet-18 baseline on CIFAR-10 — accept (you need a baseline before any
  augmentation work pays off)
* `S-0001-02` Sweep mixup vs cutout on the 5,000-image subset — accept (the survey identified this
  as the most promising near-term experiment)

Reject anything that duplicates work already in flight. Defer anything you cannot afford this week.
The skill records every decision as a [correction](../explanation/corrections.md) on the original
suggestion, so the next aggregator run reflects the new state.

## Step 3: Create the Tasks

For each accepted suggestion the brainstorm skill calls
[`create-task`](../../skills/create-task/SKILL.md) automatically. Each new task gets a name, a short
description, the right `task_type`, and a `source_suggestion` field linking back to the suggestion
it came from. When the skill finishes you should see two new task folders:

```bash
ls tasks/
```

```text
tasks/
├── t0001_survey_image_augmentation_papers/
├── t0002_baseline_resnet18_cifar10/
└── t0003_sweep_mixup_cutout_subset/
```

Both new tasks are on status `not_started`, ready for `execute-task` to pick up.

## Step 4: Run the Next Task

Pick one and run it the same way as part 3:

```text
/execute-task t0002_baseline_resnet18_cifar10   # Claude Code
$execute-task t0002_baseline_resnet18_cifar10   # Codex
```

This task is a
[`baseline-evaluation`](../../../meta/task_types/baseline-evaluation/description.json) type, so it
goes through every stage: research papers (reading the survey from t0001!), planning,
implementation, results. The papers added by the literature survey now feed the next task's research
stage. That is the whole point of papers-as-assets.

## Why brainstorm before executing?

Because the suggestions chooser is the only place where strategic decisions happen. Tasks are
expensive — compute, API spend, your attention. Running every suggestion that gets generated wastes
all three. The brainstorm session is a five-minute ritual that prevents months of drift.

Two rules that fall out of this:

* **Never create tasks by hand** — always through `/human-brainstorm` or `/create-task` invoked from
  inside a brainstorm session. Hand-rolled tasks bypass the suggestion link, the cost check, and the
  priority review.
* **Never add paper assets outside a task** — every paper enters the project as part of a real task
  (a literature survey, an experiment that needs the paper, a comparative analysis). There is no
  standalone "add a paper" workflow because there is no standalone reason to do it.

## Next

Continue to [5. Inspect Results](05_inspect_results.md) to read what your tasks produced.
