# Task Steps Specification

**Version**: 4

* * *

## Purpose

This specification defines the canonical step IDs for task execution. These IDs are used everywhere:
`step_tracker.json`, log file names, commit messages, and branch history.

**Consumers**:

* **Task agents** — populate `step_tracker.json` with these IDs
* **Commit messages** — reference step IDs for traceability
* **Log files** — use step IDs in file names and frontmatter
* **Verificator scripts** — validate step IDs against this list

* * *

## Step ID Format

Step IDs are short lowercase slugs: 1-3 words separated by hyphens. The canonical table below shows
the default phase order. Each step has an ID (the slug) and a display name.

## Step Numbering

The `step` field in `step_tracker.json` is a **sequential task-local number** starting from 1. It
does NOT use the canonical order numbers from the table below. When a task skips optional steps, the
remaining steps are numbered consecutively (1, 2, 3, ...) with no gaps.

The canonical "Order" column below shows the recommended sequence within each phase — it is not a
numbering scheme for `step_tracker.json`.

* * *

## Canonical Steps

### Preflight Phase

| Order | Step ID | Name | Required | Description |
| --- | --- | --- | --- | --- |
| 1 | `create-branch` | Create branch | yes | Create `task/<task_id>` branch from `main` |
| 2 | `check-deps` | Check dependencies | yes | Run verify_task_dependencies.py, confirm all deps completed |
| 3 | `init-folders` | Initialize folders | yes | Create task folder structure, step_tracker.json, logs/ |

### Research Phase

| Order | Step ID | Name | Required | Description |
| --- | --- | --- | --- | --- |
| 4 | `research-papers` | Research existing papers | no | Review papers already in the corpus |
| 5 | `research-internet` | Internet research | no | Search for new papers and resources online |
| 6 | `research-code` | Research previous tasks | no | Review code, datasets, and findings from prior tasks |

### Planning Phase

| Order | Step ID | Name | Required | Description |
| --- | --- | --- | --- | --- |
| 7 | `planning` | Planning | no | Design approach, estimate costs, list assets |

### Implementation Phase

| Order | Step ID | Name | Required | Description |
| --- | --- | --- | --- | --- |
| 8 | `setup-machines` | Set up machines | no | Create remote machines if needed |
| 9 | `implementation` | Implementation | yes | Run the main task work |
| 10 | `teardown` | Tear down machines | no | Destroy remote machines after implementation |

### Analysis Phase

| Order | Step ID | Name | Required | Description |
| --- | --- | --- | --- | --- |
| 11 | `creative-thinking` | Creative thinking | no | Out-of-the-box analysis and alternative approaches |
| 12 | `results` | Results summarization | yes | Write results_summary.md, results_detailed.md, metrics.json |
| 13 | `compare-literature` | Compare to literature | no | Compare results against published baselines |

### Reporting Phase

| Order | Step ID | Name | Required | Description |
| --- | --- | --- | --- | --- |
| 14 | `suggestions` | Formulate suggestions | yes | Write suggestions.json for future tasks |
| 15 | `reporting` | Post-task reporting | yes | Final reporting, W&B upload, verification pass |

* * *

## Usage in step_tracker.json

Use the `step` field for the order number and `name` for the step ID:

```json
{
  "task_id": "t0003_download_training_corpus",
  "steps": [
    {
      "step": 1,
      "name": "create-branch",
      "description": "Create task/t0003_download_training_corpus branch from main.",
      "status": "completed",
      "started_at": "2026-03-30T08:50:00Z",
      "completed_at": "2026-03-30T08:50:01Z",
      "log_file": "logs/steps/001_create-branch/"
    },
    {
      "step": 2,
      "name": "check-deps",
      "description": "Verify all dependencies are completed.",
      "status": "completed",
      "started_at": "2026-03-30T08:50:02Z",
      "completed_at": "2026-03-30T08:50:03Z",
      "log_file": "logs/steps/002_check-deps/"
    },
    {
      "step": 3,
      "name": "init-folders",
      "description": "Create task folder structure and initial files.",
      "status": "completed",
      "started_at": "2026-03-30T08:50:04Z",
      "completed_at": "2026-03-30T08:51:00Z",
      "log_file": "logs/steps/003_init-folders/"
    },
    {
      "step": 4,
      "name": "research-papers",
      "description": "Review existing dataset papers in the corpus.",
      "status": "completed",
      "started_at": "2026-03-30T09:00:00Z",
      "completed_at": "2026-03-30T09:30:00Z",
      "log_file": "logs/steps/004_research-papers/"
    },
    {
      "step": 5,
      "name": "research-internet",
      "description": "Search for corpus download sources and documentation.",
      "status": "completed",
      "started_at": "2026-03-30T10:00:00Z",
      "completed_at": "2026-03-30T10:45:00Z",
      "log_file": "logs/steps/005_research-internet/"
    },
    {
      "step": 6,
      "name": "planning",
      "description": "Design the experiment plan.",
      "status": "in_progress",
      "started_at": "2026-03-30T11:00:00Z",
      "completed_at": null,
      "log_file": null
    },
    {
      "step": 7,
      "name": "implementation",
      "description": "Download corpus and create dataset asset.",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "log_file": null
    }
  ]
}
```

* * *

## Usage in Commit Messages

Commit messages must include both the task ID and step ID:

```text
<task_id> [<step_id>]: <description>
```

Examples:

```text
t0003_download_training_corpus [create-branch]: Create task branch from main
```

```text
t0003_download_training_corpus [check-deps]: Verify all dependencies completed
```

```text
t0003_download_training_corpus [implementation]: Download and verify training corpus
```

* * *

## Usage in Log File Names

Step logs use the step order and step ID:

```text
logs/steps/<NNN>_<step_id>.md
```

Examples:

* `logs/steps/001_create-branch/`
* `logs/steps/002_check-deps/`
* `logs/steps/003_init-folders/`
* `logs/steps/004_research-papers/`
* `logs/steps/006_planning/`
* `logs/steps/007_implementation/`

* * *

## Skipping Optional Steps

Not every task needs all steps. Optional steps (marked `no` in the Required column) can be skipped.
When a step is skipped:

* It must still appear in `step_tracker.json` with status `"skipped"`
* A step log must be created with status `"skipped"` and a brief explanation in the Summary section
* No commit is required for skipped steps

* * *

## Custom Steps

Some tasks may need steps not in the canonical list (e.g., a multi-phase execution). Custom steps
are allowed with these rules:

* Use the same slug format (1-3 lowercase words, hyphens)
* Insert at the appropriate position in the order
* Use order numbers that don't conflict (e.g., `6a` is not allowed; use `6`, `7`, `8` and shift
  subsequent steps)
* Document the custom step in the task's `plan/plan.md`

* * *

## Verification Rules

### Errors

| Code | Description |
| --- | --- |
| `TS-E001` | Step ID in `step_tracker.json` is not a valid slug format |
| `TS-E002` | A required step is missing from `step_tracker.json` |
| `TS-E003` | Step order numbers are not sequential |

### Warnings

| Code | Description |
| --- | --- |
| `TS-W001` | Step ID is not in the canonical list (custom step) |
| `TS-W002` | Steps are out of canonical order |
