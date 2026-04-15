# Specifications Reference

Specifications are the contract for every artifact format in ARF. They are the sole source of truth:
verificators implement them, skills produce files that conform to them.

All specs live in `arf/specifications/`. Every spec is versioned.

## Task & Execution

| File | Version | What It Defines |
| --- | --- | --- |
| [`task_file_specification.md`](../../specifications/task_file_specification.md) | 4 | `task.json` schema and required fields |
| [`task_folder_specification.md`](../../specifications/task_folder_specification.md) | 4 | Mandatory folder and subfolder layout for a task |
| [`task_git_specification.md`](../../specifications/task_git_specification.md) | 3 | Branch naming, commit, and PR rules for tasks |
| [`task_steps_specification.md`](../../specifications/task_steps_specification.md) | 4 | Mandatory stages and steps every task must execute |
| [`task_type_specification.md`](../../specifications/task_type_specification.md) | 1 | Allowed task types and their semantics |
| [`step_tracker_specification.md`](../../specifications/step_tracker_specification.md) | 1 | `step_tracker.json` schema for tracking step execution |

## Plans & Logs

| File | Version | What It Defines |
| --- | --- | --- |
| [`logs_specification.md`](../../specifications/logs_specification.md) | 4 | Format and required fields for entries under `logs/` |
| [`plan_specification.md`](../../specifications/plan_specification.md) | 5 | Required sections and content of `plan/plan.md` |

## Research

| File | Version | What It Defines |
| --- | --- | --- |
| [`research_code_specification.md`](../../specifications/research_code_specification.md) | 1 | Format and sections of `research/research_code.md` |
| [`research_internet_specification.md`](../../specifications/research_internet_specification.md) | 1 | Format and sections of `research/research_internet.md` |
| [`research_papers_specification.md`](../../specifications/research_papers_specification.md) | 1 | Format and sections of `research/research_papers.md` |

## Results & Output

| File | Version | What It Defines |
| --- | --- | --- |
| [`compare_literature_specification.md`](../../specifications/compare_literature_specification.md) | 1 | Format of `results/compare_literature.md` |
| [`suggestions_specification.md`](../../specifications/suggestions_specification.md) | 2 | Schema and content rules for task suggestions |
| [`task_results_specification.md`](../../specifications/task_results_specification.md) | 7 | Required files and sections under `results/` |

## Assets & Metadata

| File | Version | What It Defines |
| --- | --- | --- |
| [`agent_skills_specification.md`](../../specifications/agent_skills_specification.md) | 1 | Skill file format, frontmatter, and discovery symlinks |
| [`category_specification.md`](../../specifications/category_specification.md) | 1 | Category folder layout and metadata |
| [`corrections_specification.md`](../../specifications/corrections_specification.md) | 3 | Correction file format for overriding prior task outputs |
| [`metrics_specification.md`](../../specifications/metrics_specification.md) | 4 | `metrics.json` schema and metric registration |

## Project & Infrastructure

| File | Version | What It Defines |
| --- | --- | --- |
| [`daily_news_specification.md`](../../specifications/daily_news_specification.md) | 2 | Format of `news/<date>.md` and `news/<date>.json` |
| [`project_budget_specification.md`](../../specifications/project_budget_specification.md) | 1 | Schema of `project/budget.json` |
| [`project_description_specification.md`](../../specifications/project_description_specification.md) | 1 | Required sections of `project/description.md` |
| [`remote_machines_specification.md`](../../specifications/remote_machines_specification.md) | 1 | Remote machine records and lifecycle files |

## Versioning

Specs use plain integer versions (1, 2, 3). On every change, increment by one and update the
`Version` line near the top. Files produced under a spec carry a matching `spec_version` field.
