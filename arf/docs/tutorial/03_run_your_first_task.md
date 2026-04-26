# 3. Run Your First Task

In [part 2](02_customize_meta.md) you reviewed the `meta/` entries that `/setup-project` created.
The right first task in many new ARF projects is a **literature survey**: find and download the
relevant papers before committing to any experiments. This part walks one through end to end.

## Step 1: Create a Literature Survey Task

Tasks are never created by hand. `/setup-project` already ran
[`human-brainstorm`](../../skills/human-brainstorm/SKILL.md), so first check whether it created a
literature-survey task:

```bash
uv run python -m arf.scripts.aggregators.aggregate_tasks --status not_started --format ids
```

If a suitable literature-survey task already exists, use that task ID in the rest of this tutorial.
If setup explicitly deferred task creation, invoke
[`create-task`](../../skills/create-task/SKILL.md) to build the folder, write
[`task.json`](../../specifications/task_file_specification.md), and draft `task_description.md`:

```text
/create-task   # Claude Code
$create-task   # Codex
```

When prompted, use:

* **Name**: Survey image augmentation papers
* **Task type**: `literature-survey`
* **Description**: Find, download, and summarize the key papers on image augmentation for
  small-dataset image classification. Cover the standard techniques (flip, crop, mixup, cutout,
  randaugment) and recent work on CIFAR-10 and similar benchmarks.

The task folder starts with just two files: `task.json` and `task_description.md`. No branch, no
worktree, no subdirectories — that all happens later when you execute the task.

Why a literature survey first? Two reasons. You learn what the field already tried before spending
compute on it. And the paper assets the survey produces become the input for every later task's
research stage — papers added once, read many times.

## Step 2: Inspect the Task Folder

```bash
ls tasks/t0001_survey_image_augmentation_papers/
```

Right now the folder is minimal:

```text
tasks/t0001_survey_image_augmentation_papers/
├── task.json
└── task_description.md
```

Open `task.json`:

```bash
cat tasks/t0001_survey_image_augmentation_papers/task.json
```

Fields include `name`, `short_description`, `status` (currently `"not_started"`), `dependencies`,
and `expected_assets`. Never edit it by hand — skills own it.

## Step 3: Execute the Task with execute-task

The [`execute-task`](../../skills/execute-task/SKILL.md) skill handles everything: branch creation,
worktree setup, the full folder structure (`assets/`, `research/`, `results/`, `logs/`, etc.), and
every mandatory stage in order. Each stage runs as its own sub-agent so contexts stay clean.

Invoke it:

```text
/execute-task t0001_survey_image_augmentation_papers   # Claude Code
$execute-task t0001_survey_image_augmentation_papers   # Codex
```

The skill will:

1. Create branch `task/t0001_survey_image_augmentation_papers` in a git worktree and build the full
   task folder structure (`assets/`, `corrections/`, `intervention/`, `logs/`, `plan/`, `research/`,
   `results/`, `step_tracker.json`). Flip `task.json` status to `in_progress`.
2. Run `research-internet` — find relevant papers, download them, and create one paper asset per
   paper under `assets/paper/`.
3. Skip planning (the `literature-survey` task type marks it optional).
4. Run implementation: write `research/research_papers.md` synthesizing the downloaded papers
   grouped by topic.
5. Run analysis and reporting into `results/results_summary.md` and friends.
6. Commit each step as a separate, well-described commit.
7. Open a PR, merge it, and refresh the `overview/` dashboard on `main`.

Every step runs under [`arf/scripts/utils/run_with_logs.py`](../../scripts/utils/run_with_logs.py),
which captures stdout, stderr, and exit codes into `logs/`. When something breaks, start there.

## Step 4: Watch the Step Tracker

In a second terminal, follow progress:

```bash
watch -n 2 cat tasks/t0001_survey_image_augmentation_papers/step_tracker.json
```

A snapshot mid-run:

```json
{
  "task_id": "t0001_survey_image_augmentation_papers",
  "steps": [
    {
      "step": 1,
      "name": "create-branch",
      "description": "Create task branch and worktree.",
      "status": "completed",
      "started_at": "2026-04-08T08:59:00Z",
      "completed_at": "2026-04-08T08:59:30Z",
      "log_file": "logs/steps/001_create-branch/"
    },
    {
      "step": 2,
      "name": "research-internet",
      "description": "Search the web for relevant image-augmentation papers.",
      "status": "completed",
      "started_at": "2026-04-08T09:00:00Z",
      "completed_at": "2026-04-08T09:40:00Z",
      "log_file": "logs/steps/002_research-internet/"
    },
    {
      "step": 3,
      "name": "implementation",
      "description": "Download papers and write the synthesis document.",
      "status": "in_progress",
      "started_at": "2026-04-08T09:40:05Z",
      "completed_at": null,
      "log_file": "logs/steps/003_implementation/"
    },
    {
      "step": 4,
      "name": "results",
      "description": "Write results files.",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "log_file": null
    }
  ]
}
```

The tracker is the single source of truth for task state. Verificators read it to decide whether a
stage's prerequisites are ready.

## Step 5: Inspect the PR

The `execute-task` skill automatically merges the PR and refreshes the `overview/` dashboard on
`main`. When it finishes, it prints the PR URL. Open it to review what was merged. You should see:

* One commit per step with a descriptive message
* A diff that touches only files inside `tasks/t0001_survey_image_augmentation_papers/` (plus
  `pyproject.toml` and `uv.lock` if dependencies changed)
* New paper assets under `tasks/t0001_survey_image_augmentation_papers/assets/paper/`
* Final `task.json` with `status` set to `"completed"`

Your first task is in the project history, and the project now has its first batch of paper assets.

## What Just Happened

Two skills split the work. `human-brainstorm` or `create-task` wrote the task folder and metadata.
`execute-task` handled the branch, worktree, stages, logging, verification, and the PR. For the
mental model behind stages, sub-agents, and verificators, read the
[task lifecycle](../explanation/task_lifecycle.md) doc.

## Next

The literature survey produced a batch of paper assets and a `suggestions.json` of follow-up ideas.
Continue to [4. Brainstorm Next Tasks](04_brainstorm_next_tasks.md) to decide which suggestions to
turn into real tasks.
