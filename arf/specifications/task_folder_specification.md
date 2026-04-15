# Task Folder Specification

**Version**: 4

* * *

## Purpose

This specification defines the mandatory folder structure for every task in the project. Every task
folder must contain a fixed set of subdirectories and files to ensure consistency, enable automated
verification, and support aggregation across tasks.

**Producer**: The `init-folders` step of the task execution skill, or manual setup.

**Consumers**:

* **Task subagents** — expect this structure when reading/writing task outputs
* **Verificator scripts** — validate folder completeness
* **Aggregator scripts** — locate results, suggestions, and assets by convention
* **Human reviewers** — navigate task outputs at checkpoints

* * *

## File Location

```text
tasks/<task_id>/
```

One folder per task. The `<task_id>` format is defined in the task file specification
(`arf/specifications/task_file_specification.md`).

* * *

## Mandatory Structure

Every task folder must contain these directories and files. Optional contents are noted; the
directories themselves are always required.

```text
tasks/<task_id>/
├── task.json                         # Task metadata (required)
├── <long_description_file>.md        # Optional task description file (spec_version 4 only)
├── step_tracker.json                 # Step execution tracking (required)
├── plan/                             # Planning outputs
│   └── plan.md                       # Execution plan (required for completed tasks)
├── research/                         # Research outputs
│   ├── research_papers.md            # Literature review (required when research-papers step was executed)
│   └── research_internet.md          # Internet research (required when research-internet step was executed)
├── assets/                           # Produced assets
│   ├── paper/                        # Paper assets (may be empty)
│   ├── dataset/                      # Dataset assets (may be empty)
│   ├── model/                        # Model assets (may be empty)
│   └── predictions/                  # Predictions assets (may be empty)
├── results/                          # Task results
│   ├── results_summary.md            # Brief summary with key metrics (required)
│   ├── results_detailed.md           # Full methodology and analysis (required)
│   ├── metrics.json                  # Structured metric data (required)
│   ├── suggestions.json              # Follow-up task suggestions (required)
│   ├── costs.json                    # API and compute cost breakdown (required)
│   └── remote_machines_used.json     # Remote machine specs (required, may be [])
├── corrections/                      # Corrections to previous tasks (may be empty)
├── intervention/                     # Human intervention requests (may be empty)
└── logs/                             # Execution logs
    ├── commands/                     # CLI command logs (may be empty)
    ├── steps/                        # Step-level log folders
    ├── searches/                     # Search query logs (may be empty)
    └── sessions/                     # Session capture logs
        ├── capture_report.json       # Session capture report
        └── *.jsonl                   # Raw session transcripts (may be empty)
```

* * *

## Directory Descriptions

### `plan/`

Contains the execution plan produced during the planning step. The `plan.md` file follows the
mandatory sections defined in the task documents rule: `Objective`, `Approach`, `Cost Estimation`,
`Step by Step`, `Remote Machines`, `Assets Needed`, `Expected Assets`, `Time Estimation`,
`Risks & Fallbacks`, and `Verification Criteria`.

### `research/`

Contains research output files produced during the research phase. Each file follows its own
specification:

* `research_papers.md` — `arf/specifications/research_papers_specification.md`
* `research_internet.md` — `arf/specifications/research_internet_specification.md`
* `research_code.md` — optional, produced by the `research-code` step

### `assets/`

Contains asset subdirectories, one per asset type. Common predefined types are `paper/`, `dataset/`,
`library/`, `answer/`, `model/`, and `predictions/`. Additional types may be added as defined in
`meta/asset_types/`. Each asset type directory contains one subfolder per asset instance, following
the corresponding asset specification.

### `results/`

Contains all task output files. Format for each file:

* `results_summary.md` — see `arf/specifications/task_results_specification.md`
* `results_detailed.md` — see task results specification
* `metrics.json` — see task results specification
* `suggestions.json` — `arf/specifications/suggestions_specification.md`
* `costs.json` — see task results specification
* `remote_machines_used.json` — see task results specification
* `images/` — optional subdirectory for charts and visualizations

### `corrections/`

Contains JSON files that correct aggregated artifacts from previous tasks. These corrections may
target suggestions and task-produced assets such as papers, answers, datasets, libraries, models,
and predictions. Multi-file assets may also use partial file overlays so a later task can replace,
add, or delete only selected files without modifying the completed task folder. Format is defined in
`arf/specifications/corrections_specification.md`. May be empty if no corrections are needed.

### `intervention/`

Contains files describing human intervention requests. May be empty if no intervention is needed.

### `logs/`

Contains execution logs organized into four subdirectories:

* `commands/` — CLI command execution logs produced by `arf.scripts.utils.run_with_logs`
* `steps/` — one subfolder per step (`NNN_step-id/`) with `step_log.md`
* `searches/` — search query logs from research phases
* `sessions/` — session capture outputs produced during the `reporting` step. Includes
  `capture_report.json` plus any copied raw CLI transcript files

Log format defined in `arf/specifications/logs_specification.md`.

* * *

## Root File Restrictions

**CRITICAL**: The task folder root may only contain the following files and directories. No other
files may be created in the root of a task folder.

### Allowed root files

* `task.json` — task metadata
* The markdown file referenced by `task.json` `long_description_file` (spec version `4` only;
  recommended name: `task_description.md`)
* `step_tracker.json` — step execution tracking
* `__init__.py` — Python package marker (auto-created, do not remove)

### Allowed root directories

* `plan/`, `research/`, `assets/`, `results/`, `corrections/`, `intervention/`, `logs/`
* `code/` — task-specific Python code (scripts, modules)
* `data/` — task-specific data files (downloaded files, intermediate datasets, generated data).
  **Recommended** for all non-temporary data the task needs. Do not store temporary or disposable
  files here; use system temp directories for those.

Any other file or directory in the task folder root is a verification error (`FD-E016`). All task
code, data, scripts, and outputs must live inside the appropriate subdirectory.

### Ignored directories (build artifacts)

The verificator silently ignores these directories if they appear in the task folder root. They are
Python build artifacts created by imports, pytest, or mypy rather than task output. They are already
excluded by `.gitignore` and will never be committed.

* `__pycache__/` — Python bytecode cache

* * *

## Completeness Requirements

Not all files are required at all times. The requirements depend on the task's `status` field in
`task.json`:

### `not_started`

* `task.json` — required
* Optional task description markdown file — allowed when referenced by `task.json`
* `step_tracker.json` — required
* All directories — required (may be empty)

### `in_progress`

* `task.json` — required
* `step_tracker.json` — required
* All directories — required
* Files accumulate as steps complete

### `completed`

All files listed in the mandatory structure are required:

* `task.json` with status `"completed"` and non-null `end_time`
* `step_tracker.json` with all required steps completed
* `plan/plan.md`
* `research/research_papers.md`
* `research/research_internet.md`
* `results/results_summary.md`
* `results/results_detailed.md`
* `results/metrics.json`
* `results/suggestions.json`
* `results/costs.json`
* `results/remote_machines_used.json`
* At least one step folder in `logs/steps/`

### `cancelled` or `permanently_failed`

* `task.json` — required
* `step_tracker.json` — required
* Other files — as many as were produced before termination

* * *

## Verification Rules

### Errors

| Code | Description |
| --- | --- |
| `FD-E001` | Task folder does not exist |
| `FD-E002` | `task.json` is missing |
| `FD-E003` | `step_tracker.json` is missing |
| `FD-E004` | A required top-level directory is missing. |
| `FD-E005` | Required log subdirectory missing (`commands/`, `steps/`, `searches/`, `sessions/`) |
| `FD-E006` | Task is completed but `results/results_summary.md` is missing |
| `FD-E007` | Task is completed but `results/results_detailed.md` is missing |
| `FD-E008` | Task is completed but `results/metrics.json` is missing |
| `FD-E009` | Task is completed but `results/suggestions.json` is missing |
| `FD-E010` | Task is completed but `results/costs.json` is missing |
| `FD-E011` | Task is completed but `results/remote_machines_used.json` is missing |
| `FD-E012` | Task is completed but `plan/plan.md` is missing |
| `FD-E013` | Task is completed but `research/research_papers.md` is missing (skipped if research-papers step is `"skipped"` in step_tracker.json) |
| `FD-E014` | Task is completed but `research/research_internet.md` is missing (skipped if research-internet step is `"skipped"` in step_tracker.json) |
| `FD-E015` | Task is completed but `logs/steps/` contains no step folders |
| `FD-E016` | Unexpected file or directory in task folder root. |

### Warnings

| Code | Description |
| --- | --- |
| `FD-W001` | `logs/commands/` is empty (no CLI commands were logged) |
| `FD-W002` | `logs/searches/` is empty (no search queries were logged) |
| `FD-W003` | `results/images/` directory does not exist (no visualizations) |
| `FD-W004` | `assets/` contains no asset subdirectories with content |
| `FD-W005` | `corrections/` contains files but task status is not `completed` |
| `FD-W006` | `logs/sessions/` contains no captured session transcript JSONL files |
