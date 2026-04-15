# Step Tracker Specification

**Version**: 1

---

## Purpose

This specification defines the format and requirements for the `step_tracker.json` file
that tracks task execution progress.

**Producer**: Task agents (create and update during execution).

**Consumers**:

* **Task subagents** — read to determine which steps are complete
* **Verificator scripts** — validate step completion and log coverage
* **Human reviewers** — monitor task progress at checkpoints
* **Aggregator scripts** — collect execution metrics across tasks

---

## File Location

```text
tasks/<task_id>/step_tracker.json
```

One file per task. Created when the task starts; updated as each step progresses.

---

## Top-Level Fields

| Field     | Type        | Required | Description                     |
|-----------|-------------|----------|---------------------------------|
| `task_id` | string      | yes      | Must match the task folder name |
| `steps`   | list[Step]  | yes      | Ordered list of task steps      |

---

## Step Object

| Field          | Type          | Required | Description                                       |
|----------------|---------------|----------|---------------------------------------------------|
| `step`         | int           | yes      | Step number (1-indexed, sequential)                |
| `name`         | string        | yes      | Short human-readable name                          |
| `description`  | string        | yes      | What this step accomplishes                        |
| `status`       | string        | yes      | One of: `"pending"`, `"in_progress"`, `"completed"`, `"failed"`, `"skipped"` |
| `started_at`   | string / null | yes      | ISO 8601 UTC timestamp, `null` when pending        |
| `completed_at` | string / null | yes      | ISO 8601 UTC timestamp, `null` when not finished   |
| `log_file`     | string / null | no       | Relative path to step log folder in `logs/steps/`  |

### Status Values

* `"pending"` — step has not started yet
* `"in_progress"` — step is currently executing
* `"completed"` — step finished successfully
* `"failed"` — step failed (see step log for details)
* `"skipped"` — step was intentionally skipped (see step log for reason)

### The `log_file` Field

When a step reaches `"completed"`, `"failed"`, or `"skipped"` status, the agent must
set `log_file` to the relative path of the corresponding step log folder (e.g.,
`"logs/steps/005_research-internet/"`). This creates a verifiable link between the
tracker and the actual log folder.

---

## Example

```json
{
  "task_id": "0008-baseline-sentiment-classifier",
  "steps": [
    {
      "step": 1,
      "name": "create-branch",
      "description": "Create task branch from main.",
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
      "name": "research-papers",
      "description": "Review papers in the corpus relevant to baseline approaches.",
      "status": "completed",
      "started_at": "2026-03-30T09:00:00Z",
      "completed_at": "2026-03-30T09:30:00Z",
      "log_file": "logs/steps/003_research-papers/"
    },
    {
      "step": 4,
      "name": "planning",
      "description": "Design the experiment plan including model selection and evaluation.",
      "status": "in_progress",
      "started_at": "2026-03-30T11:00:00Z",
      "completed_at": null,
      "log_file": null
    },
    {
      "step": 5,
      "name": "implementation",
      "description": "Run the baseline classification experiment.",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "log_file": null
    }
  ]
}
```

---

## Verification Rules

### Errors

| Code      | Description                                                    |
|-----------|----------------------------------------------------------------|
| `ST-E001` | `step_tracker.json` does not exist or is not valid JSON        |
| `ST-E002` | `task_id` does not match the task folder name                  |
| `ST-E003` | `steps` is missing or not a list                               |
| `ST-E004` | A step is missing required fields (`step`, `name`, `description`, `status`) |
| `ST-E005` | Step numbers are not sequential starting from 1                |
| `ST-E006` | `status` is not one of the allowed values                      |

### Warnings

| Code      | Description                                                    |
|-----------|----------------------------------------------------------------|
| `ST-W001` | A completed/failed/skipped step has `log_file` set to `null`   |
| `ST-W002` | `log_file` path does not point to an existing file             |
| `ST-W003` | `started_at` is `null` for a non-pending step                  |
| `ST-W004` | `completed_at` is `null` for a completed/failed/skipped step   |
