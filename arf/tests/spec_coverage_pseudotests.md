# Specification Coverage Pseudo-Tests

This document lists every error code (XX-E###) and warning code (XX-W###) from every specification
file in `arf/specifications/` and `meta/asset_types/*/specification.md`. For each code, it describes
the triggering condition, a setup to reproduce it, and the expected diagnostic.

* * *

## Specification Files Audited

1. `arf/specifications/task_file_specification.md` (TF codes)
2. `arf/specifications/task_folder_specification.md` (FD codes)
3. `arf/specifications/task_git_specification.md` (TG codes)
4. `arf/specifications/task_steps_specification.md` (TS codes)
5. `arf/specifications/task_results_specification.md` (TR codes)
6. `arf/specifications/task_type_specification.md` (TY codes)
7. `arf/specifications/logs_specification.md` (LG codes)
8. `arf/specifications/plan_specification.md` (PL codes)
9. `arf/specifications/suggestions_specification.md` (SG codes)
10. `arf/specifications/corrections_specification.md` (no formal codes)
11. `arf/specifications/metrics_specification.md` (MT codes)
12. `arf/specifications/research_papers_specification.md` (RP codes)
13. `arf/specifications/research_internet_specification.md` (RI codes)
14. `arf/specifications/research_code_specification.md` (RC codes)
15. `arf/specifications/step_tracker_specification.md` (ST codes)
16. `arf/specifications/category_specification.md` (CA codes)
17. `arf/specifications/compare_literature_specification.md` (CL codes)
18. `arf/specifications/remote_machines_specification.md` (RM codes)
19. `arf/specifications/agent_skills_specification.md` (SK codes)
20. `arf/specifications/project_budget_specification.md` (PB codes)
21. `arf/specifications/project_description_specification.md` (PD codes)
22. `meta/asset_types/paper/specification.md` (PA codes)
23. `meta/asset_types/library/specification.md` (LA codes)
24. `meta/asset_types/dataset/specification.md` (DA codes)
25. `meta/asset_types/answer/specification.md` (AA codes)
26. `meta/asset_types/model/specification.md` (MA codes)
27. `meta/asset_types/predictions/specification.md` (PR codes)

* * *

## 1. Task File Specification (TF)

**Spec**: `arf/specifications/task_file_specification.md`

### TF-E001: task.json does not exist or is not valid JSON

* **Trigger**: `task.json` file does not exist in task folder, OR contains invalid JSON
* **Setup 1**: Create task folder without `task.json`
* **Assert 1**: Error TF-E001 is in diagnostics
* **Setup 2**: Create `task.json` with content `not valid json {`
* **Assert 2**: Error TF-E001 is in diagnostics

### TF-E002: task_id does not match the task folder name

* **Trigger**: The `task_id` field value does not equal the folder name
* **Setup**: Create `tasks/t0001_foo/task.json` with `"task_id": "t0002_bar"`
* **Assert**: Error TF-E002 is in diagnostics

### TF-E003: A required field is missing

* **Trigger**: Any required field is absent from task.json (`task_id`, `task_index`, `name`,
  `short_description`, `status`, `dependencies`, `start_time`, `end_time`, `expected_assets`,
  `task_types`, `source_suggestion`)
* **Setup**: Create task.json missing the `name` field
* **Assert**: Error TF-E003 is in diagnostics
* **Note**: Test each required field individually to ensure full coverage

### TF-E004: status is not one of the allowed values

* **Trigger**: `status` is not one of `"not_started"`, `"in_progress"`, `"completed"`,
  `"cancelled"`, `"permanently_failed"`, `"intervention_blocked"`
* **Setup**: Create task.json with `"status": "running"`
* **Assert**: Error TF-E004 is in diagnostics

### TF-E005: task_id format is invalid

* **Trigger**: `task_id` does not match `tNNNN_slug` pattern
* **Setup 1**: Create task folder `0001_foo` with matching task.json
* **Assert 1**: Error TF-E005 (missing `t` prefix)
* **Setup 2**: Create task folder `t1_foo` with matching task.json
* **Assert 2**: Error TF-E005 (not zero-padded)
* **Setup 3**: Create task folder `t0001-foo` with matching task.json
* **Assert 3**: Error TF-E005 (hyphens not allowed)

### TF-E006: A dependency references a task ID that does not exist

* **Trigger**: An entry in `dependencies` names a task folder that does not exist
* **Setup**: Create task.json with `"dependencies": ["t9999_nonexistent"]`
* **Assert**: Error TF-E006 is in diagnostics

### TF-E007: start_time or end_time is not valid ISO 8601 or null

* **Trigger**: `start_time` or `end_time` is a string that is not valid ISO 8601 and is not `null`
* **Setup**: Create task.json with `"start_time": "last tuesday"`
* **Assert**: Error TF-E007 is in diagnostics

### TF-E008: source_suggestion format invalid

* **Trigger**: `source_suggestion` is not a string, `null`, or does not match `S-XXXX-NN` format
* **Setup 1**: Create task.json with `"source_suggestion": 42`
* **Assert 1**: Error TF-E008 is in diagnostics
* **Setup 2**: Create task.json with `"source_suggestion": "S-01-1"`
* **Assert 2**: Error TF-E008 (bad format)

### TF-E009: source_suggestion references a suggestion ID that does not exist

* **Trigger**: `source_suggestion` is a valid format string but no task's `suggestions.json`
  contains that ID
* **Setup**: Create task.json with `"source_suggestion": "S-9999-01"` where no such suggestion
  exists
* **Assert**: Error TF-E009 is in diagnostics

### TF-E010: task_index is not an integer or does not match numeric part of task_id

* **Trigger**: `task_index` is not an int, or does not match the 4-digit portion of `task_id`
* **Setup 1**: Create `t0003_foo/task.json` with `"task_index": 5`
* **Assert 1**: Error TF-E010 (mismatch)
* **Setup 2**: Create task.json with `"task_index": "three"`
* **Assert 2**: Error TF-E010 (not integer)

### TF-E011: task_types is not a list

* **Trigger**: `task_types` is a string or object instead of a list
* **Setup**: Create task.json with `"task_types": "download-dataset"`
* **Assert**: Error TF-E011 is in diagnostics

### TF-E012: A task type slug does not exist in meta/task_types/

* **Trigger**: An entry in `task_types` references a slug without a corresponding folder
* **Setup**: Create task.json with `"task_types": ["nonexistent-type"]`
* **Assert**: Error TF-E012 is in diagnostics

### TF-E013: spec_version is not an integer or not a supported version

* **Trigger**: `spec_version` is a non-integer or unsupported value
* **Setup 1**: Create task.json with `"spec_version": "four"`
* **Assert 1**: Error TF-E013
* **Setup 2**: Create task.json with `"spec_version": 99`
* **Assert 2**: Error TF-E013 (unsupported version)

### TF-E014: Long-description fields invalid for the selected spec version

* **Trigger**: Spec version rules for `long_description` and `long_description_file` are violated
* **Setup 1**: Spec version 4 with neither `long_description` nor `long_description_file`
* **Assert 1**: Error TF-E014
* **Setup 2**: Spec version 4 with both `long_description` and `long_description_file` set
* **Assert 2**: Error TF-E014
* **Setup 3**: Spec version 3 (or omitted) with `long_description_file` present
* **Assert 3**: Error TF-E014
* **Setup 4**: Spec version 3 without `long_description`
* **Assert 4**: Error TF-E014

### TF-E015: long_description_file is not a valid markdown file name in the task root

* **Trigger**: `long_description_file` contains a path separator or is not a simple filename
* **Setup**: Create task.json with `"long_description_file": "subdir/desc.md"`
* **Assert**: Error TF-E015 is in diagnostics

### TF-E016: The referenced long_description_file is missing or unreadable

* **Trigger**: `long_description_file` points to a file that does not exist
* **Setup**: Create task.json with `"long_description_file": "task_description.md"` but do not
  create that file
* **Assert**: Error TF-E016 is in diagnostics

### TF-W001: short_description exceeds 200 characters

* **Trigger**: `short_description` string is longer than 200 characters
* **Setup**: Create task.json with a 201-character `short_description`
* **Assert**: Warning TF-W001 is in diagnostics

### TF-W002: name exceeds 80 characters

* **Trigger**: `name` string is longer than 80 characters
* **Setup**: Create task.json with an 81-character `name`
* **Assert**: Warning TF-W002 is in diagnostics

### TF-W003: Status is in_progress but start_time is null

* **Trigger**: `status` is `"in_progress"` and `start_time` is `null`
* **Setup**: Create task.json with `"status": "in_progress", "start_time": null`
* **Assert**: Warning TF-W003 is in diagnostics

### TF-W004: Status is completed but end_time is null

* **Trigger**: `status` is `"completed"` and `end_time` is `null`
* **Setup**: Create task.json with `"status": "completed", "end_time": null`
* **Assert**: Warning TF-W004 is in diagnostics

### TF-W005: expected_assets is empty

* **Trigger**: `expected_assets` is `{}`
* **Setup**: Create task.json with `"expected_assets": {}`
* **Assert**: Warning TF-W005 is in diagnostics

### TF-W006: A dependency task does not have status completed

* **Trigger**: A task in `dependencies` exists but its status is not `"completed"`
* **Setup**: Create two tasks; task B depends on task A; set task A status to `"in_progress"`
* **Assert**: Warning TF-W006 is in diagnostics

* * *

## 2. Task Folder Specification (FD)

**Spec**: `arf/specifications/task_folder_specification.md`

### FD-E001: Task folder does not exist

* **Trigger**: The task folder path does not exist on disk
* **Setup**: Run verificator for `t9999_nonexistent` without creating the folder
* **Assert**: Error FD-E001 is in diagnostics

### FD-E002: task.json is missing

* **Trigger**: Task folder exists but `task.json` is not inside it
* **Setup**: Create empty task folder without `task.json`
* **Assert**: Error FD-E002 is in diagnostics

### FD-E003: step_tracker.json is missing

* **Trigger**: Task folder exists but `step_tracker.json` is not inside it
* **Setup**: Create task folder with `task.json` but no `step_tracker.json`
* **Assert**: Error FD-E003 is in diagnostics

### FD-E004: A required top-level directory is missing

* **Trigger**: One of the mandatory directories (`plan/`, `research/`, `assets/`, `results/`,
  `corrections/`, `intervention/`, `logs/`) is missing
* **Setup**: Create task folder without `plan/` directory
* **Assert**: Error FD-E004 is in diagnostics

### FD-E005: Required log subdirectory missing

* **Trigger**: `logs/` exists but one of `commands/`, `steps/`, `searches/`, `sessions/` is missing
* **Setup**: Create `logs/` with only `commands/` and `steps/` (missing `searches/` and `sessions/`)
* **Assert**: Error FD-E005 is in diagnostics

### FD-E006: Task completed but results_summary.md missing

* **Trigger**: Task status is `"completed"` but `results/results_summary.md` does not exist
* **Setup**: Set task status to completed without creating `results/results_summary.md`
* **Assert**: Error FD-E006 is in diagnostics

### FD-E007: Task completed but results_detailed.md missing

* **Trigger**: Task status is `"completed"` but `results/results_detailed.md` does not exist
* **Setup**: Set task status to completed without creating `results/results_detailed.md`
* **Assert**: Error FD-E007 is in diagnostics

### FD-E008: Task completed but metrics.json missing

* **Trigger**: Task status is `"completed"` but `results/metrics.json` does not exist
* **Setup**: Set task status to completed without creating `results/metrics.json`
* **Assert**: Error FD-E008 is in diagnostics

### FD-E009: Task completed but suggestions.json missing

* **Trigger**: Task status is `"completed"` but `results/suggestions.json` does not exist
* **Setup**: Set task status to completed without creating `results/suggestions.json`
* **Assert**: Error FD-E009 is in diagnostics

### FD-E010: Task completed but costs.json missing

* **Trigger**: Task status is `"completed"` but `results/costs.json` does not exist
* **Setup**: Set task status to completed without creating `results/costs.json`
* **Assert**: Error FD-E010 is in diagnostics

### FD-E011: Task completed but remote_machines_used.json missing

* **Trigger**: Task status is `"completed"` but `results/remote_machines_used.json` does not exist
* **Setup**: Set task status to completed without creating `results/remote_machines_used.json`
* **Assert**: Error FD-E011 is in diagnostics

### FD-E012: Task completed but plan/plan.md missing

* **Trigger**: Task status is `"completed"` but `plan/plan.md` does not exist
* **Setup**: Set task status to completed without creating `plan/plan.md`
* **Assert**: Error FD-E012 is in diagnostics

### FD-E013: Task completed but research_papers.md missing

* **Trigger**: Task status is `"completed"` and research-papers step is not `"skipped"` but
  `research/research_papers.md` does not exist
* **Setup**: Set task to completed with research-papers step as `"completed"` but no
  `research_papers.md`
* **Assert**: Error FD-E013 is in diagnostics
* **Note**: Skipped if research-papers step is `"skipped"` in step_tracker.json

### FD-E014: Task completed but research_internet.md missing

* **Trigger**: Task status is `"completed"` and research-internet step is not `"skipped"` but
  `research/research_internet.md` does not exist
* **Setup**: Set task to completed with research-internet step as `"completed"` but no
  `research_internet.md`
* **Assert**: Error FD-E014 is in diagnostics
* **Note**: Skipped if research-internet step is `"skipped"` in step_tracker.json

### FD-E015: Task completed but logs/steps/ contains no step folders

* **Trigger**: Task status is `"completed"` but `logs/steps/` is empty
* **Setup**: Set task to completed with an empty `logs/steps/` directory
* **Assert**: Error FD-E015 is in diagnostics

### FD-E016: Unexpected file or directory in task folder root

* **Trigger**: A file or directory exists in the task root that is not in the allowed list
  (`task.json`, `step_tracker.json`, `__init__.py`, the `long_description_file`, and the allowed
  directories)
* **Setup**: Create `tasks/t0001_foo/random_file.txt`
* **Assert**: Error FD-E016 is in diagnostics
* **Note**: `__pycache__/` is silently ignored

### FD-W001: logs/commands/ is empty

* **Trigger**: `logs/commands/` directory exists but contains no files
* **Setup**: Create empty `logs/commands/` directory
* **Assert**: Warning FD-W001 is in diagnostics

### FD-W002: logs/searches/ is empty

* **Trigger**: `logs/searches/` directory exists but contains no files
* **Setup**: Create empty `logs/searches/` directory
* **Assert**: Warning FD-W002 is in diagnostics

### FD-W003: results/images/ directory does not exist

* **Trigger**: `results/images/` does not exist
* **Setup**: Create `results/` directory without `images/` subdirectory
* **Assert**: Warning FD-W003 is in diagnostics

### FD-W004: assets/ contains no asset subdirectories with content

* **Trigger**: `assets/` exists but no asset type subdirectory contains any asset instances
* **Setup**: Create `assets/paper/` as an empty directory
* **Assert**: Warning FD-W004 is in diagnostics

### FD-W005: corrections/ contains files but task status is not completed

* **Trigger**: Task has correction files but status is not `"completed"`
* **Setup**: Create correction files in `corrections/` with task status `"in_progress"`
* **Assert**: Warning FD-W005 is in diagnostics

### FD-W006: logs/sessions/ contains no captured session transcript JSONL files

* **Trigger**: `logs/sessions/` exists but contains no `.jsonl` files
* **Setup**: Create `logs/sessions/` with only `capture_report.json`
* **Assert**: Warning FD-W006 is in diagnostics

* * *

## 3. Task Git Specification (TG)

**Spec**: `arf/specifications/task_git_specification.md`

### TG-E001: Branch name does not match task/<task_id> pattern

* **Trigger**: The branch name is not `task/<task_id>`
* **Setup**: Create a branch named `feature/t0001_foo` instead of `task/t0001_foo`
* **Assert**: Error TG-E001 is in diagnostics

### TG-E002: Task branch modifies files outside the allowed set

* **Trigger**: Files outside the task folder (and not in the allowed exceptions like
  `pyproject.toml`, `uv.lock`, `ruff.toml`, `.gitignore`, `mypy.ini`) are modified
* **Setup**: Modify a file in `arf/` or another task's folder on the task branch
* **Assert**: Error TG-E002 is in diagnostics

### TG-E003: No commits found on the task branch

* **Trigger**: The task branch has no commits beyond the branch point from main
* **Setup**: Create a task branch but make no commits
* **Assert**: Error TG-E003 is in diagnostics

### TG-E004: A completed step has no associated commit

* **Trigger**: A step in step_tracker.json is marked `"completed"` but there is no commit for it
* **Setup**: Mark a step as completed in step_tracker.json but do not make a commit for that step
* **Assert**: Error TG-E004 is in diagnostics

### TG-E005: PR does not target main

* **Trigger**: The pull request targets a branch other than `main`
* **Setup**: Create a PR targeting `develop` instead of `main`
* **Assert**: Error TG-E005 is in diagnostics

### TG-W001: Commit message does not include task ID and step ID

* **Trigger**: A commit message does not contain both the task ID and a step ID
* **Setup**: Make a commit with message `"update files"`
* **Assert**: Warning TG-W001 is in diagnostics

### TG-W002: Commit message first line exceeds 72 characters

* **Trigger**: The first line of a commit message is longer than 72 characters
* **Setup**: Make a commit with a 73-character first line
* **Assert**: Warning TG-W002 is in diagnostics

### TG-W003: PR title does not match expected format

* **Trigger**: PR title does not follow `<task_id>: <task name>` format
* **Setup**: Create a PR with title `"Fix stuff"`
* **Assert**: Warning TG-W003 is in diagnostics

### TG-W004: PR body is missing a required section

* **Trigger**: PR body does not contain Summary, Assets produced, or Verification sections
* **Setup**: Create a PR with an empty body
* **Assert**: Warning TG-W004 is in diagnostics

* * *

## 4. Task Steps Specification (TS)

**Spec**: `arf/specifications/task_steps_specification.md`

### TS-E001: Step ID is not a valid slug format

* **Trigger**: A step's `name` field in step_tracker.json is not a valid lowercase slug
* **Setup**: Create step_tracker.json with a step named `"Research Papers"` (uppercase, spaces)
* **Assert**: Error TS-E001 is in diagnostics

### TS-E002: A required step is missing from step_tracker.json

* **Trigger**: A required step (`create-branch`, `check-deps`, `init-folders`, `implementation`,
  `results`, `suggestions`, `reporting`) is not present in the steps list
* **Setup**: Create step_tracker.json without the `implementation` step
* **Assert**: Error TS-E002 is in diagnostics

### TS-E003: Step order numbers are not sequential

* **Trigger**: The `step` numbers have gaps (e.g., 1, 2, 4)
* **Setup**: Create step_tracker.json with steps numbered 1, 2, 5
* **Assert**: Error TS-E003 is in diagnostics

### TS-W001: Step ID is not in the canonical list (custom step)

* **Trigger**: A step name is not one of the canonical step IDs
* **Setup**: Create a step named `"custom-validation"`
* **Assert**: Warning TS-W001 is in diagnostics

### TS-W002: Steps are out of canonical order

* **Trigger**: Steps appear in an order different from the canonical order (e.g., `implementation`
  before `planning`)
* **Setup**: Place `implementation` step before `planning` step in the steps list
* **Assert**: Warning TS-W002 is in diagnostics

* * *

## 5. Task Results Specification (TR)

**Spec**: `arf/specifications/task_results_specification.md`

### TR-E001: results_summary.md does not exist

* **Trigger**: `results/results_summary.md` file is missing
* **Setup**: Create results directory without `results_summary.md`
* **Assert**: Error TR-E001 is in diagnostics

### TR-E002: results_detailed.md does not exist

* **Trigger**: `results/results_detailed.md` file is missing
* **Setup**: Create results directory without `results_detailed.md`
* **Assert**: Error TR-E002 is in diagnostics

### TR-E003: metrics.json does not exist or is not valid JSON

* **Trigger**: `results/metrics.json` is missing or contains invalid JSON
* **Setup 1**: Do not create `metrics.json`
* **Assert 1**: Error TR-E003
* **Setup 2**: Create `metrics.json` with content `{broken`
* **Assert 2**: Error TR-E003

### TR-E004: costs.json does not exist or is not valid JSON

* **Trigger**: `results/costs.json` is missing or contains invalid JSON
* **Setup**: Do not create `costs.json`
* **Assert**: Error TR-E004 is in diagnostics

### TR-E005: remote_machines_used.json does not exist or is not valid JSON

* **Trigger**: `results/remote_machines_used.json` is missing or contains invalid JSON
* **Setup**: Do not create `remote_machines_used.json`
* **Assert**: Error TR-E005 is in diagnostics

### TR-E006: results_summary.md missing a mandatory section

* **Trigger**: `results_summary.md` is missing `## Summary`, `## Metrics`, or `## Verification`
* **Setup**: Create `results_summary.md` without `## Metrics` section
* **Assert**: Error TR-E006 is in diagnostics

### TR-E007: results_detailed.md missing a mandatory section

* **Trigger**: `results_detailed.md` is missing `## Summary`, `## Methodology`, `## Verification`,
  `## Limitations`, `## Files Created`, or (for spec_version "2") `## Task Requirement Coverage`
* **Setup**: Create `results_detailed.md` without `## Methodology`
* **Assert**: Error TR-E007 is in diagnostics
* **Note**: Section set depends on `spec_version` in frontmatter

### TR-E008: metrics.json top-level value is not a JSON object

* **Trigger**: `metrics.json` contains a JSON array or scalar at the top level
* **Setup**: Create `metrics.json` with content `[1, 2, 3]`
* **Assert**: Error TR-E008 is in diagnostics

### TR-E009: (Removed in v2)

* **Note**: This code was removed. Empty `{}` is now valid for tasks with no registered metrics.

### TR-E010: metrics.json uses an invalid metric payload shape

* **Trigger**: The structure does not match either the legacy flat format or the explicit variant
  format
* **Setup 1**: Create `metrics.json` with `{"variants": []}` (empty variants array is invalid)
* **Assert 1**: Error TR-E010
* **Setup 2**: Create a variant entry missing `variant_id`
* **Assert 2**: Error TR-E010

### TR-E011: costs.json missing total_cost_usd or breakdown

* **Trigger**: `costs.json` does not contain `total_cost_usd` or `breakdown` field
* **Setup**: Create `costs.json` with `{"total_cost_usd": 5}` (missing `breakdown`)
* **Assert**: Error TR-E011 is in diagnostics

### TR-E012: costs.json breakdown is not a JSON object, or a breakdown entry is invalid

* **Trigger**: `breakdown` is not a dict, or an entry in it is neither a number nor a valid rich
  object with `cost_usd`
* **Setup 1**: Create `costs.json` with `"breakdown": [1, 2]`
* **Assert 1**: Error TR-E012
* **Setup 2**: Create a breakdown entry as `"service": "invalid"`
* **Assert 2**: Error TR-E012

### TR-E013: remote_machines_used.json top-level value is not a JSON array

* **Trigger**: File contains a JSON object instead of an array
* **Setup**: Create `remote_machines_used.json` with content `{}`
* **Assert**: Error TR-E013 is in diagnostics

### TR-E014: A machine entry is missing a required field

* **Trigger**: A machine object in `remote_machines_used.json` is missing `provider`, `machine_id`,
  `gpu`, `gpu_count`, `ram_gb`, `duration_hours`, or `cost_usd`
* **Setup**: Create a machine entry missing the `gpu` field
* **Assert**: Error TR-E014 is in diagnostics

### TR-E015: costs.json total_cost_usd is not a non-negative number

* **Trigger**: `total_cost_usd` is negative, or not a number
* **Setup**: Create `costs.json` with `"total_cost_usd": -5.0`
* **Assert**: Error TR-E015 is in diagnostics

### TR-E016: costs.json services is not a JSON object of non-negative numbers

* **Trigger**: `services` field exists but is not an object, or values are negative or non-numeric
* **Setup**: Create `costs.json` with `"services": {"openai": -1.0}`
* **Assert**: Error TR-E016 is in diagnostics

### TR-E017: costs.json budget_limit is not a non-negative number

* **Trigger**: `budget_limit` exists but is negative or non-numeric
* **Setup**: Create `costs.json` with `"budget_limit": "fifty"`
* **Assert**: Error TR-E017 is in diagnostics

### TR-E018: costs.json note is not a string

* **Trigger**: `note` exists but is not a string
* **Setup**: Create `costs.json` with `"note": 42`
* **Assert**: Error TR-E018 is in diagnostics

### TR-E019: results_detailed.md spec_version not recognized

* **Trigger**: `spec_version` in `results_detailed.md` frontmatter is not `"1"` or `"2"`
* **Setup**: Create `results_detailed.md` with `spec_version: "3"` in frontmatter
* **Assert**: Error TR-E019 is in diagnostics

### TR-W001: results_summary.md total word count is under 80

* **Trigger**: Total word count of `results_summary.md` is below 80
* **Setup**: Create a minimal `results_summary.md` with 50 words
* **Assert**: Warning TR-W001 is in diagnostics

### TR-W002: results_detailed.md total word count is under 200

* **Trigger**: Total word count of `results_detailed.md` is below 200
* **Setup**: Create a minimal `results_detailed.md` with 100 words
* **Assert**: Warning TR-W002 is in diagnostics

### TR-W003: Metrics section in results_summary.md has fewer than 3 bullet points

* **Trigger**: The `## Metrics` section has fewer than 3 bullet items
* **Setup**: Create `results_summary.md` with only 2 bullet points in `## Metrics`
* **Assert**: Warning TR-W003 is in diagnostics

### TR-W004: results/images/ directory does not exist

* **Trigger**: `results/images/` subdirectory is absent
* **Setup**: Do not create `results/images/`
* **Assert**: Warning TR-W004 is in diagnostics

### TR-W005: costs.json total_cost_usd does not match sum of breakdown values

* **Trigger**: The numeric total does not equal the sum of breakdown entries
* **Setup**: Create `costs.json` with `"total_cost_usd": 10, "breakdown": {"a": 3, "b": 4}` (sum =
  7, not 10)
* **Assert**: Warning TR-W005 is in diagnostics

### TR-W006: A metrics.json metric or dimension key is not snake_case

* **Trigger**: A key in metrics or dimensions uses hyphens or uppercase
* **Setup**: Create a variant with `"dimensions": {"Model-Name": "bert"}`
* **Assert**: Warning TR-W006 is in diagnostics

### TR-W007: Verification section in results_summary.md mentions no verificator results

* **Trigger**: The `## Verification` section does not reference any verificator
* **Setup**: Create `## Verification` section with only `"All good."`
* **Assert**: Warning TR-W007 is in diagnostics

### TR-W008: Files Created section lists no file paths

* **Trigger**: The `## Files Created` section in `results_detailed.md` has no file paths
* **Setup**: Create `## Files Created` section with text but no paths
* **Assert**: Warning TR-W008 is in diagnostics

### TR-W009: (Promoted to error TM-E005)

* **Note**: Unregistered metric keys are now errors, handled by `verify_task_metrics.py`.

### TR-W010: Task Requirement Coverage does not contain REQ-* items

* **Trigger**: `## Task Requirement Coverage` section has no `REQ-*` pattern
* **Setup**: Create the section without any `REQ-1`, `REQ-2`, etc.
* **Assert**: Warning TR-W010 is in diagnostics

### TR-W011: Task Requirement Coverage lacks Done / Partial / Not done labels

* **Trigger**: The coverage section has `REQ-*` items but no status labels
* **Setup**: Create `REQ-1` entries without `Done`, `Partial`, or `Not done` text
* **Assert**: Warning TR-W011 is in diagnostics

### TR-W012: Task Requirement Coverage is not the last ## section

* **Trigger**: Another `##` section appears after `## Task Requirement Coverage`
* **Setup**: Add `## Appendix` after `## Task Requirement Coverage`
* **Assert**: Warning TR-W012 is in diagnostics

### TR-W013: Examples section missing in results_detailed.md for experiment-type task

* **Trigger**: Task is experiment-type but `## Examples` section is absent
* **Setup**: Create `results_detailed.md` without `## Examples` for a task with experiment-type
  task_types
* **Assert**: Warning TR-W013 is in diagnostics

### TR-W014: Examples section has fewer than 10 bullet points

* **Trigger**: `## Examples` section exists but has fewer than 10 examples
* **Setup**: Create `## Examples` with only 5 bullet points
* **Assert**: Warning TR-W014 is in diagnostics

* * *

## 6. Task Type Specification (TY)

**Spec**: `arf/specifications/task_type_specification.md`

### TY-E001: description.json missing or not valid JSON

* **Trigger**: `description.json` does not exist in the task type folder, or is not valid JSON
* **Setup**: Create task type folder without `description.json`
* **Assert**: Error TY-E001 is in diagnostics

### TY-E002: Required field missing in description.json

* **Trigger**: Any required field (`spec_version`, `name`, `short_description`,
  `detailed_description`, `optional_steps`) is missing
* **Setup**: Create `description.json` without `name`
* **Assert**: Error TY-E002 is in diagnostics

### TY-E003: spec_version is not an integer

* **Trigger**: `spec_version` is a string or other non-integer type
* **Setup**: Create `description.json` with `"spec_version": "1"`
* **Assert**: Error TY-E003 is in diagnostics

### TY-E004: Task type slug is invalid

* **Trigger**: Folder name contains uppercase, underscores, spaces, or starts with a non-letter
* **Setup**: Create `meta/task_types/Download_Dataset/description.json`
* **Assert**: Error TY-E004 is in diagnostics

### TY-E005: instruction.md is missing

* **Trigger**: `instruction.md` does not exist in the task type folder
* **Setup**: Create task type folder with `description.json` but no `instruction.md`
* **Assert**: Error TY-E005 is in diagnostics

### TY-E006: instruction.md missing planning or implementation guidelines heading

* **Trigger**: `instruction.md` does not contain `## Planning Guidelines` or
  `## Implementation Guidelines`
* **Setup**: Create `instruction.md` without `## Planning Guidelines`
* **Assert**: Error TY-E006 is in diagnostics

### TY-E007: A value in optional_steps is not a valid optional step ID

* **Trigger**: An entry in `optional_steps` is not one of the valid optional step IDs
* **Setup**: Create `description.json` with `"optional_steps": ["nonexistent-step"]`
* **Assert**: Error TY-E007 is in diagnostics

### TY-W001: short_description exceeds 200 characters

* **Trigger**: `short_description` is longer than 200 characters
* **Setup**: Create a 201-character `short_description`
* **Assert**: Warning TY-W001 is in diagnostics

### TY-W002: detailed_description is under 50 characters

* **Trigger**: `detailed_description` is shorter than 50 characters
* **Setup**: Create `"detailed_description": "Short."`
* **Assert**: Warning TY-W002 is in diagnostics

### TY-W003: detailed_description exceeds 1000 characters

* **Trigger**: `detailed_description` is longer than 1000 characters
* **Setup**: Create a 1001-character `detailed_description`
* **Assert**: Warning TY-W003 is in diagnostics

### TY-W004: name exceeds 50 characters

* **Trigger**: `name` is longer than 50 characters
* **Setup**: Create a 51-character `name`
* **Assert**: Warning TY-W004 is in diagnostics

### TY-W005: instruction.md is under 200 characters

* **Trigger**: `instruction.md` file content is fewer than 200 characters
* **Setup**: Create a very short `instruction.md`
* **Assert**: Warning TY-W005 is in diagnostics

* * *

## 7. Logs Specification (LG)

**Spec**: `arf/specifications/logs_specification.md`

### LG-E001: logs/ directory does not exist

* **Trigger**: The `logs/` directory is missing from the task folder
* **Setup**: Create task folder without `logs/` directory
* **Assert**: Error LG-E001 is in diagnostics

### LG-E002: logs/commands/ directory does not exist

* **Trigger**: `logs/commands/` is missing
* **Setup**: Create `logs/` without `commands/` subdirectory
* **Assert**: Error LG-E002 is in diagnostics

### LG-E003: logs/steps/ directory does not exist

* **Trigger**: `logs/steps/` is missing
* **Setup**: Create `logs/` without `steps/` subdirectory
* **Assert**: Error LG-E003 is in diagnostics

### LG-E004: A command log JSON is invalid or missing required fields

* **Trigger**: A `.json` file in `logs/commands/` is not valid JSON or lacks required fields
  (`spec_version`, `task_id`, `command`, `exit_code`, `duration_seconds`, `started_at`,
  `completed_at`, `working_directory`, `stdout_file`, `stderr_file`, `stdout_lines`, `stderr_lines`,
  `truncated`)
* **Setup**: Create a command log JSON missing the `command` field
* **Assert**: Error LG-E004 is in diagnostics

### LG-E005: A step log is missing YAML frontmatter or mandatory sections

* **Trigger**: A `step_log.md` file has no frontmatter, or is missing `## Summary`,
  `## Actions Taken`, `## Outputs`, or `## Issues`
* **Setup**: Create `step_log.md` without `## Outputs` section
* **Assert**: Error LG-E005 is in diagnostics

### LG-E006: task_id in a log does not match the task folder name

* **Trigger**: The `task_id` field in a command log JSON or step log frontmatter does not match
* **Setup**: Create a command log with `"task_id": "t0002_wrong"`
* **Assert**: Error LG-E006 is in diagnostics

### LG-E007: Step log step_number has no matching step in step_tracker.json

* **Trigger**: A step log's `step_number` frontmatter value does not appear in step_tracker.json
* **Setup**: Create a step log with `step_number: 99` when step_tracker has only steps 1-7
* **Assert**: Error LG-E007 is in diagnostics

### LG-E008: A completed step in step_tracker.json has no step log

* **Trigger**: A step is marked `"completed"` but no corresponding step log folder exists
* **Setup**: Mark step 5 as completed but do not create `logs/steps/005_*/`
* **Assert**: Error LG-E008 is in diagnostics

### LG-W001: logs/searches/ directory does not exist

* **Trigger**: `logs/searches/` is missing
* **Setup**: Create `logs/` without `searches/` subdirectory
* **Assert**: Warning LG-W001 is in diagnostics

### LG-W002: A search log JSON is missing optional fields

* **Trigger**: A search log in `logs/searches/` is missing optional fields like `snippet` or
  `relevance_note`
* **Setup**: Create a search log result entry without `snippet`
* **Assert**: Warning LG-W002 is in diagnostics

### LG-W003: Step log section below minimum word count

* **Trigger**: A mandatory section in `step_log.md` is below its minimum word count (e.g.,
  `## Summary` under 20 words, `## Actions Taken` under 2 items)
* **Setup**: Create `## Summary` section with 10 words
* **Assert**: Warning LG-W003 is in diagnostics

### LG-W004: Command log has non-zero exit code

* **Trigger**: A command log has `"exit_code"` != 0
* **Setup**: Create a command log with `"exit_code": 1`
* **Assert**: Warning LG-W004 is in diagnostics

### LG-W005: No command logs found

* **Trigger**: `logs/commands/` exists but is empty
* **Setup**: Create empty `logs/commands/` directory
* **Assert**: Warning LG-W005 is in diagnostics

### LG-W006: step_tracker.json step is missing log_file field

* **Trigger**: A step in step_tracker.json does not have a `log_file` field at all
* **Setup**: Create a completed step entry without the `log_file` key
* **Assert**: Warning LG-W006 is in diagnostics

### LG-W007: logs/sessions/ directory is missing or contains no transcript JSONL files

* **Trigger**: `logs/sessions/` does not exist or has no `.jsonl` files
* **Setup**: Create `logs/sessions/` with only `capture_report.json`
* **Assert**: Warning LG-W007 is in diagnostics

### LG-W008: logs/sessions/capture_report.json is missing or inconsistent

* **Trigger**: `capture_report.json` does not exist or has inconsistencies (e.g., `copied_sessions`
  count does not match actual JSONL files present)
* **Setup**: Do not create `capture_report.json` in `logs/sessions/`
* **Assert**: Warning LG-W008 is in diagnostics

* * *

## 8. Plan Specification (PL)

**Spec**: `arf/specifications/plan_specification.md`

### PL-E001: File does not exist

* **Trigger**: `tasks/<task_id>/plan/plan.md` does not exist
* **Setup**: Create task folder without `plan/plan.md`
* **Assert**: Error PL-E001 is in diagnostics

### PL-E002: YAML frontmatter present but not parseable

* **Trigger**: The file starts with `---` but the YAML between the delimiters is not valid
* **Setup**: Create `plan.md` with `---\n: bad: yaml\n---`
* **Assert**: Error PL-E002 is in diagnostics

### PL-E003: task_id in frontmatter does not match the task folder name

* **Trigger**: Frontmatter `task_id` differs from the folder name
* **Setup**: Create `plan.md` in `t0001_foo/` with `task_id: "t0002_bar"` in frontmatter
* **Assert**: Error PL-E003 is in diagnostics

### PL-E004: One or more mandatory sections is missing

* **Trigger**: The document is missing any of: `## Objective`, `## Task Requirement Checklist`,
  `## Approach`, `## Cost Estimation`, `## Step by Step`, `## Remote Machines`, `## Assets Needed`,
  `## Expected Assets`, `## Time Estimation`, `## Risks & Fallbacks`, `## Verification Criteria`
* **Setup**: Create `plan.md` without `## Risks & Fallbacks`
* **Assert**: Error PL-E004 is in diagnostics
* **Note**: Legacy `spec_version: "1"` may omit `## Task Requirement Checklist`

### PL-E005: Total content fewer than 200 words

* **Trigger**: The plan body (excluding frontmatter) has fewer than 200 words
* **Setup**: Create a plan.md with 100 words of content
* **Assert**: Error PL-E005 is in diagnostics

### PL-E006: Step by Step section has no numbered items

* **Trigger**: `## Step by Step` section does not contain any `1.` numbered list items
* **Setup**: Create `## Step by Step` with only bullet points, no numbered items
* **Assert**: Error PL-E006 is in diagnostics

### PL-E007: spec_version missing from frontmatter (when frontmatter present)

* **Trigger**: Frontmatter block is present but does not include `spec_version`
* **Setup**: Create `plan.md` with `---\ntask_id: "t0001_foo"\n---` (no spec_version)
* **Assert**: Error PL-E007 is in diagnostics

### PL-W001: A mandatory section is below its minimum word count

* **Trigger**: Any mandatory section has fewer words than its specified minimum (e.g.,
  `## Objective` < 30 words, `## Approach` < 50 words, `## Step by Step` < 100 words)
* **Setup**: Create `## Objective` with 15 words
* **Assert**: Warning PL-W001 is in diagnostics

### PL-W002: Risks & Fallbacks contains no markdown table

* **Trigger**: `## Risks & Fallbacks` section has no `|` table syntax
* **Setup**: Write `## Risks & Fallbacks` section with only prose, no table
* **Assert**: Warning PL-W002 is in diagnostics

### PL-W003: YAML frontmatter is missing entirely

* **Trigger**: The file does not start with `---` frontmatter
* **Setup**: Create `plan.md` starting directly with `# Plan` heading
* **Assert**: Warning PL-W003 is in diagnostics

### PL-W004: Cost Estimation does not mention a dollar amount

* **Trigger**: `## Cost Estimation` section contains no `$` character
* **Setup**: Write `## Cost Estimation` as `"All resources are free."`
* **Assert**: Warning PL-W004 is in diagnostics

### PL-W005: Verification Criteria has fewer than 3 bullet points

* **Trigger**: `## Verification Criteria` section has fewer than 3 bullet items
* **Setup**: Create `## Verification Criteria` with only 2 bullets
* **Assert**: Warning PL-W005 is in diagnostics

### PL-W006: Task Requirement Checklist contains no clear REQ-* items

* **Trigger**: `## Task Requirement Checklist` exists but has no `REQ-1`, `REQ-2`, etc.
* **Setup**: Write the section as prose without `REQ-*` labels
* **Assert**: Warning PL-W006 is in diagnostics

### PL-W007: Step by Step does not reference any REQ-* items

* **Trigger**: `## Step by Step` section contains no `REQ-*` pattern
* **Setup**: Write numbered steps without mentioning any `REQ-*` IDs
* **Assert**: Warning PL-W007 is in diagnostics

### PL-W008: Step by Step contains expensive operations but no validation gate

* **Trigger**: Steps mention API calls, remote compute, or large-scale processing but do not mention
  a baseline comparison or validation gate
* **Setup**: Write a step like "Run full evaluation on 10,000 instances via OpenAI API" without any
  validation gate or baseline reference
* **Assert**: Warning PL-W008 is in diagnostics

* * *

## 9. Suggestions Specification (SG)

**Spec**: `arf/specifications/suggestions_specification.md`

### SG-E001: File is missing or not valid JSON

* **Trigger**: `results/suggestions.json` does not exist or is not valid JSON
* **Setup**: Create `suggestions.json` with content `not json`
* **Assert**: Error SG-E001 is in diagnostics

### SG-E002: Top-level value is not a JSON object

* **Trigger**: The file contains a JSON array or scalar at top level
* **Setup**: Create `suggestions.json` with content `[]`
* **Assert**: Error SG-E002 is in diagnostics

### SG-E003: Missing spec_version field

* **Trigger**: Top-level object does not contain `spec_version`
* **Setup**: Create `suggestions.json` with `{"suggestions": []}`
* **Assert**: Error SG-E003 is in diagnostics

### SG-E004: Missing or non-array suggestions field

* **Trigger**: `suggestions` key is missing or its value is not an array
* **Setup**: Create `suggestions.json` with `{"spec_version": "2", "suggestions": "none"}`
* **Assert**: Error SG-E004 is in diagnostics

### SG-E005: Array element is not a JSON object

* **Trigger**: An entry in the `suggestions` array is a string or number
* **Setup**: Create `suggestions.json` with
  `{"spec_version": "2", "suggestions": ["not an object"]}`
* **Assert**: Error SG-E005 is in diagnostics

### SG-E006: Required field missing in suggestion object

* **Trigger**: A suggestion object is missing any of `id`, `title`, `description`, `kind`,
  `priority`, `source_task`, `source_paper`, `categories`
* **Setup**: Create a suggestion without the `priority` field
* **Assert**: Error SG-E006 is in diagnostics

### SG-E007: id does not match format S-XXXX-NN

* **Trigger**: `id` does not match regex `^S-\d{4}-\d{2}$`
* **Setup**: Create a suggestion with `"id": "S-1-1"`
* **Assert**: Error SG-E007 is in diagnostics

### SG-E008: kind is not one of the allowed values

* **Trigger**: `kind` is not one of `experiment`, `technique`, `evaluation`, `dataset`, `library`
* **Setup**: Create a suggestion with `"kind": "paper"`
* **Assert**: Error SG-E008 is in diagnostics

### SG-E009: priority is not one of the allowed values

* **Trigger**: `priority` is not one of `high`, `medium`, `low`
* **Setup**: Create a suggestion with `"priority": "critical"`
* **Assert**: Error SG-E009 is in diagnostics

### SG-E010: source_task does not match the containing task folder name

* **Trigger**: `source_task` value differs from the task folder that contains this file
* **Setup**: Create `suggestions.json` in `t0002_foo/` with `"source_task": "t0003_bar"`
* **Assert**: Error SG-E010 is in diagnostics

### SG-E011: Duplicate suggestion id within the file

* **Trigger**: Two suggestions in the same file have the same `id`
* **Setup**: Create two suggestions both with `"id": "S-0002-01"`
* **Assert**: Error SG-E011 is in diagnostics

### SG-E012: categories is not a list

* **Trigger**: `categories` is a string or other non-list type
* **Setup**: Create a suggestion with `"categories": "evaluation"`
* **Assert**: Error SG-E012 is in diagnostics

### SG-E013: status is not one of the allowed values

* **Trigger**: `status` is present but not `"active"` or `"rejected"`
* **Setup**: Create a suggestion with `"status": "pending"`
* **Assert**: Error SG-E013 is in diagnostics

### SG-W001: title exceeds 120 characters

* **Trigger**: `title` is longer than 120 characters
* **Setup**: Create a suggestion with a 121-character `title`
* **Assert**: Warning SG-W001 is in diagnostics

### SG-W002: description is under 20 characters

* **Trigger**: `description` is shorter than 20 characters
* **Setup**: Create a suggestion with `"description": "Short."`
* **Assert**: Warning SG-W002 is in diagnostics

### SG-W003: description exceeds 1000 characters

* **Trigger**: `description` is longer than 1000 characters
* **Setup**: Create a suggestion with a 1001-character `description`
* **Assert**: Warning SG-W003 is in diagnostics

### SG-W004: title is empty or whitespace-only

* **Trigger**: `title` is `""` or `" "`
* **Setup**: Create a suggestion with `"title": ""`
* **Assert**: Warning SG-W004 is in diagnostics

### SG-W005: description is empty or whitespace-only

* **Trigger**: `description` is `""` or `" "`
* **Setup**: Create a suggestion with `"description": ""`
* **Assert**: Warning SG-W005 is in diagnostics

### SG-W006: A category slug does not exist in meta/categories/

* **Trigger**: A category in `categories` list does not correspond to a folder in `meta/categories/`
* **Setup**: Create a suggestion with `"categories": ["nonexistent-category"]`
* **Assert**: Warning SG-W006 is in diagnostics

* * *

## 10. Corrections Specification

**Spec**: `arf/specifications/corrections_specification.md`

**Note**: This specification does not define formal error/warning codes with a `XX-E###` / `XX-W###`
pattern. Instead, it lists prose verification rules. The verificator must check:

* Required fields are present (`spec_version`, `correction_id`, `correcting_task`, `target_task`,
  `target_kind`, `target_id`, `action`, `changes`, `rationale`)
* `correction_id` matches `C-XXXX-NN` format and the XXXX matches the correcting task index
* `correcting_task` matches the containing task folder
* `target_task` exists as a task folder
* `target_kind` is one of: `suggestion`, `paper`, `answer`, `dataset`, `library`, `model`,
  `predictions`
* `action` is one of: `update`, `delete`, `replace`
* The target artifact exists in the target task
* `changes` matches the action semantics (`null` for delete, has `replacement_task`/`replacement_id`
  for replace)
* `file_changes` is only used with `action: "update"` and only for asset kinds (not `suggestion`)
* Referenced replacement artifacts and files exist
* Self-references and cycles are rejected
* Filename matches `<target_kind>_<target_id>.json`

**Ambiguity**: No formal diagnostic codes are defined. Tests should verify each prose rule produces
some error diagnostic. The implementor must decide on code naming (possibly `CO-E###`).

* * *

## 11. Metrics Specification (MT)

**Spec**: `arf/specifications/metrics_specification.md`

### MT-E001: Metric definition file is missing or not valid JSON

* **Trigger**: `description.json` does not exist in `meta/metrics/<key>/` or is not valid JSON
* **Setup**: Create metric folder without `description.json`
* **Assert**: Error MT-E001 is in diagnostics

### MT-E002: Required field missing

* **Trigger**: Any of `spec_version`, `name`, `description`, `unit`, `value_type` is missing
* **Setup**: Create `description.json` without `unit`
* **Assert**: Error MT-E002 is in diagnostics

### MT-E003: spec_version is not an integer

* **Trigger**: `spec_version` is a string or float
* **Setup**: Create `description.json` with `"spec_version": "1"`
* **Assert**: Error MT-E003 is in diagnostics

### MT-E004: unit is not one of the allowed values

* **Trigger**: `unit` is not one of `f1`, `accuracy`, `precision`, `recall`, `ratio`, `count`,
  `usd`, `seconds`, `bytes`, `instances_per_second`, `none`
* **Setup**: Create `description.json` with `"unit": "percentage"`
* **Assert**: Error MT-E004 is in diagnostics

### MT-E005: value_type is not one of the allowed values

* **Trigger**: `value_type` is not one of `float`, `int`, `bool`, `string`
* **Setup**: Create `description.json` with `"value_type": "number"`
* **Assert**: Error MT-E005 is in diagnostics

### MT-E006: File name does not match snake_case pattern

* **Trigger**: The metric folder name uses hyphens, uppercase, or other non-snake_case characters
* **Setup**: Create `meta/metrics/My-Metric/description.json`
* **Assert**: Error MT-E006 is in diagnostics

### MT-E007: datasets is not a list of strings

* **Trigger**: `datasets` field exists but is not a list, or contains non-strings
* **Setup**: Create `description.json` with `"datasets": "semcor"`
* **Assert**: Error MT-E007 is in diagnostics

### MT-E008: A dataset ID in datasets does not exist in any task's assets/dataset/

* **Trigger**: A dataset ID is listed but no task has that dataset asset
* **Setup**: Create `description.json` with `"datasets": ["nonexistent-dataset"]`
* **Assert**: Error MT-E008 is in diagnostics

### MT-W001: description is under 20 characters

* **Trigger**: `description` field is shorter than 20 characters
* **Setup**: Create `description.json` with `"description": "A metric."`
* **Assert**: Warning MT-W001 is in diagnostics

### MT-W002: name exceeds 80 characters

* **Trigger**: `name` is longer than 80 characters
* **Setup**: Create `description.json` with an 81-character `name`
* **Assert**: Warning MT-W002 is in diagnostics

* * *

## 12. Research Papers Specification (RP)

**Spec**: `arf/specifications/research_papers_specification.md`

### RP-E001: File does not exist

* **Trigger**: `tasks/<task_id>/research/research_papers.md` does not exist
* **Setup**: Create task folder without `research/research_papers.md`
* **Assert**: Error RP-E001 is in diagnostics

### RP-E002: YAML frontmatter is missing or not parseable

* **Trigger**: File has no `---` delimiters or YAML cannot be parsed
* **Setup**: Create `research_papers.md` without frontmatter
* **Assert**: Error RP-E002 is in diagnostics

### RP-E003: task_id in frontmatter does not match the task folder name

* **Trigger**: Frontmatter `task_id` differs from the folder name
* **Setup**: Create file in `t0001_foo/` with `task_id: "t0002_bar"` in frontmatter
* **Assert**: Error RP-E003 is in diagnostics

### RP-E004: One or more mandatory sections is missing

* **Trigger**: Missing any of: `## Task Objective`, `## Category Selection Rationale`,
  `## Key Findings`, `## Methodology Insights`, `## Gaps and Limitations`,
  `## Recommendations for This Task`, `## Paper Index`
* **Setup**: Create file without `## Key Findings`
* **Assert**: Error RP-E004 is in diagnostics

### RP-E005: papers_cited < 1 and status is not partial

* **Trigger**: `papers_cited` is 0 but `status` is `"complete"`
* **Setup**: Create frontmatter with `papers_cited: 0` and `status: "complete"`
* **Assert**: Error RP-E005 is in diagnostics

### RP-E006: An inline [CitationKey] has no matching entry in Paper Index

* **Trigger**: A `[CitationKey]` in body text has no `### [CitationKey]` in `## Paper Index`
* **Setup**: Reference `[Smith2024]` in Key Findings but do not add it to Paper Index
* **Assert**: Error RP-E006 is in diagnostics

### RP-E007: Paper Index entry count != papers_cited in frontmatter

* **Trigger**: Number of `###` entries in Paper Index does not equal `papers_cited`
* **Setup**: Set `papers_cited: 3` but provide 2 Paper Index entries
* **Assert**: Error RP-E007 is in diagnostics

### RP-E008: A Paper Index entry is missing the DOI field

* **Trigger**: A Paper Index entry does not include a DOI line
* **Setup**: Create a Paper Index entry without `DOI:`
* **Assert**: Error RP-E008 is in diagnostics

### RP-E009: Total content fewer than 300 words

* **Trigger**: Body text (excluding frontmatter) is under 300 words
* **Setup**: Create `research_papers.md` with 200 words of content
* **Assert**: Error RP-E009 is in diagnostics

### RP-E010: spec_version is missing from frontmatter

* **Trigger**: Frontmatter does not contain `spec_version`
* **Setup**: Create frontmatter without `spec_version`
* **Assert**: Error RP-E010 is in diagnostics

### RP-W001: A mandatory section is below its minimum word count

* **Trigger**: Any section is below its minimum (e.g., `## Task Objective` < 30 words,
  `## Key Findings` < 200 words, `## Methodology Insights` < 100 words)
* **Setup**: Create `## Task Objective` with 15 words
* **Assert**: Warning RP-W001 is in diagnostics

### RP-W002: A DOI in the Paper Index does not correspond to any existing paper asset folder

* **Trigger**: A DOI is listed but no paper asset folder exists for that DOI
* **Setup**: List a DOI in Paper Index that does not exist in any task's `assets/paper/`
* **Assert**: Warning RP-W002 is in diagnostics

### RP-W003: A category does not exist in meta/categories/

* **Trigger**: A category in `categories_consulted` or in a Paper Index entry does not match a
  folder in `meta/categories/`
* **Setup**: Use `categories_consulted: ["fake-category"]`
* **Assert**: Warning RP-W003 is in diagnostics

### RP-W004: papers_reviewed < papers_cited

* **Trigger**: `papers_reviewed` is less than `papers_cited`
* **Setup**: Set `papers_reviewed: 2` and `papers_cited: 5`
* **Assert**: Warning RP-W004 is in diagnostics

### RP-W005: Key Findings section contains no ### subsections

* **Trigger**: `## Key Findings` has no `###` headings
* **Setup**: Write `## Key Findings` as flat prose without subsections
* **Assert**: Warning RP-W005 is in diagnostics

### RP-W006: A Paper Index entry is never cited in the body text

* **Trigger**: A `### [CitationKey]` entry exists but `[CitationKey]` never appears in body
* **Setup**: Add a Paper Index entry that is not referenced anywhere in the document body
* **Assert**: Warning RP-W006 is in diagnostics

* * *

## 13. Research Internet Specification (RI)

**Spec**: `arf/specifications/research_internet_specification.md`

### RI-E001: File does not exist

* **Trigger**: `tasks/<task_id>/research/research_internet.md` does not exist
* **Setup**: Create task folder without `research/research_internet.md`
* **Assert**: Error RI-E001 is in diagnostics

### RI-E002: YAML frontmatter is missing or not parseable

* **Trigger**: File has no frontmatter or YAML cannot be parsed
* **Setup**: Create file without `---` delimiters
* **Assert**: Error RI-E002 is in diagnostics

### RI-E003: task_id in frontmatter does not match

* **Trigger**: Frontmatter `task_id` differs from folder name
* **Setup**: Set `task_id: "wrong_id"` in frontmatter
* **Assert**: Error RI-E003 is in diagnostics

### RI-E004: One or more mandatory sections is missing

* **Trigger**: Missing any of: `## Task Objective`, `## Gaps Addressed`, `## Search Strategy`,
  `## Key Findings`, `## Methodology Insights`, `## Discovered Papers`,
  `## Recommendations for This Task`, `## Source Index`
* **Setup**: Omit `## Gaps Addressed`
* **Assert**: Error RI-E004 is in diagnostics

### RI-E005: sources_cited < 1 and status is not partial

* **Trigger**: `sources_cited: 0` and `status: "complete"`
* **Setup**: Create frontmatter with those values
* **Assert**: Error RI-E005 is in diagnostics

### RI-E006: An inline [SourceKey] has no matching entry in Source Index

* **Trigger**: A `[SourceKey]` in body has no matching entry
* **Setup**: Reference `[Unknown-2024]` without adding to Source Index
* **Assert**: Error RI-E006 is in diagnostics

### RI-E007: Source Index entry count != sources_cited

* **Trigger**: Number of Source Index entries does not match `sources_cited`
* **Setup**: Set `sources_cited: 5` but provide 3 entries
* **Assert**: Error RI-E007 is in diagnostics

### RI-E008: A Source Index entry is missing the URL field

* **Trigger**: A Source Index entry has no URL
* **Setup**: Create a Source Index entry without `URL:`
* **Assert**: Error RI-E008 is in diagnostics

### RI-E009: Total content fewer than 400 words

* **Trigger**: Body text (excluding frontmatter) under 400 words
* **Setup**: Create file with 300 words
* **Assert**: Error RI-E009 is in diagnostics

### RI-E010: Gaps Addressed section does not reference research_papers.md

* **Trigger**: `## Gaps Addressed` section does not mention `research_papers.md`
* **Setup**: Write `## Gaps Addressed` without any reference to `research_papers.md`
* **Assert**: Error RI-E010 is in diagnostics

### RI-E011: spec_version is missing from frontmatter

* **Trigger**: Frontmatter does not include `spec_version`
* **Setup**: Create frontmatter without `spec_version`
* **Assert**: Error RI-E011 is in diagnostics

### RI-W001: A mandatory section is below its minimum word count

* **Trigger**: Any section below minimum (e.g., `## Search Strategy` < 100 words)
* **Setup**: Create `## Search Strategy` with 50 words
* **Assert**: Warning RI-W001 is in diagnostics

### RI-W002: Search Strategy lists fewer than 3 search queries

* **Trigger**: `## Search Strategy` has fewer than 3 distinct queries
* **Setup**: List only 2 queries
* **Assert**: Warning RI-W002 is in diagnostics

### RI-W003: Key Findings section contains no ### subsections

* **Trigger**: `## Key Findings` has no `###` headings
* **Setup**: Write flat prose without subsections
* **Assert**: Warning RI-W003 is in diagnostics

### RI-W004: A Source Index entry is missing the Peer-reviewed field

* **Trigger**: A Source Index entry lacks `Peer-reviewed:` line
* **Setup**: Create Source Index entry without `Peer-reviewed`
* **Assert**: Warning RI-W004 is in diagnostics

### RI-W005: A Source Index entry is never cited in the body text

* **Trigger**: An entry in Source Index is not referenced by `[SourceKey]` in the body
* **Setup**: Add a Source Index entry that is never cited
* **Assert**: Warning RI-W005 is in diagnostics

### RI-W006: papers_discovered mismatch with Discovered Papers section

* **Trigger**: `papers_discovered` > 0 but `## Discovered Papers` has no entries (or vice versa)
* **Setup**: Set `papers_discovered: 2` but leave `## Discovered Papers` empty
* **Assert**: Warning RI-W006 is in diagnostics

### RI-W007: searches_conducted does not match number of queries listed

* **Trigger**: `searches_conducted` in frontmatter differs from the number of queries in
  `## Search Strategy`
* **Setup**: Set `searches_conducted: 10` but list only 5 queries
* **Assert**: Warning RI-W007 is in diagnostics

* * *

## 14. Research Code Specification (RC)

**Spec**: `arf/specifications/research_code_specification.md`

### RC-E001: File does not exist

* **Trigger**: `tasks/<task_id>/research/research_code.md` does not exist
* **Setup**: Create task folder without `research/research_code.md`
* **Assert**: Error RC-E001 is in diagnostics

### RC-E002: YAML frontmatter is missing or not parseable

* **Trigger**: File has no frontmatter or YAML parse fails
* **Setup**: Create file without frontmatter
* **Assert**: Error RC-E002 is in diagnostics

### RC-E003: task_id in frontmatter does not match

* **Trigger**: Frontmatter `task_id` differs from folder name
* **Setup**: Set `task_id: "wrong_id"` in frontmatter
* **Assert**: Error RC-E003 is in diagnostics

### RC-E004: One or more mandatory sections is missing

* **Trigger**: Missing any of: `## Task Objective`, `## Library Landscape`, `## Key Findings`,
  `## Reusable Code and Assets`, `## Lessons Learned`, `## Recommendations for This Task`,
  `## Task Index`
* **Setup**: Omit `## Library Landscape`
* **Assert**: Error RC-E004 is in diagnostics

### RC-E005: tasks_cited < 1 and status is not partial

* **Trigger**: `tasks_cited: 0` and `status: "complete"`
* **Setup**: Create frontmatter with those values
* **Assert**: Error RC-E005 is in diagnostics

### RC-E006: An inline [tXXXX] has no matching entry in Task Index

* **Trigger**: A `[t0012]` reference in body has no `### [t0012]` in Task Index
* **Setup**: Reference `[t0099]` without adding to Task Index
* **Assert**: Error RC-E006 is in diagnostics

### RC-E007: Task Index entry is missing the Task ID field

* **Trigger**: A Task Index entry lacks the Task ID field
* **Setup**: Create a Task Index entry without `Task ID:`
* **Assert**: Error RC-E007 is in diagnostics

### RC-E008: spec_version is missing from frontmatter

* **Trigger**: Frontmatter does not include `spec_version`
* **Setup**: Create frontmatter without `spec_version`
* **Assert**: Error RC-E008 is in diagnostics

### RC-E009: Total content fewer than 300 words

* **Trigger**: Body text under 300 words
* **Setup**: Create file with 200 words
* **Assert**: Error RC-E009 is in diagnostics

### RC-W001: A mandatory section is below its minimum word count

* **Trigger**: Any section below minimum (e.g., `## Key Findings` < 200 words)
* **Setup**: Create `## Key Findings` with 100 words
* **Assert**: Warning RC-W001 is in diagnostics

### RC-W002: A task ID in the Task Index does not match an existing task folder

* **Trigger**: A task ID referenced in Task Index does not correspond to an actual task folder
* **Setup**: Reference `t9999_nonexistent` in Task Index
* **Assert**: Warning RC-W002 is in diagnostics

### RC-W003: Key Findings section contains no ### subsections

* **Trigger**: `## Key Findings` has no `###` headings
* **Setup**: Write flat prose
* **Assert**: Warning RC-W003 is in diagnostics

### RC-W004: A Task Index entry is never cited in the body text

* **Trigger**: A `### [tXXXX]` entry exists but `[tXXXX]` never appears in body
* **Setup**: Add a Task Index entry that is never cited
* **Assert**: Warning RC-W004 is in diagnostics

### RC-W005: tasks_reviewed < tasks_cited

* **Trigger**: `tasks_reviewed` is less than `tasks_cited`
* **Setup**: Set `tasks_reviewed: 2` and `tasks_cited: 5`
* **Assert**: Warning RC-W005 is in diagnostics

* * *

## 15. Step Tracker Specification (ST)

**Spec**: `arf/specifications/step_tracker_specification.md`

### ST-E001: step_tracker.json does not exist or is not valid JSON

* **Trigger**: File is missing or contains invalid JSON
* **Setup**: Do not create `step_tracker.json`
* **Assert**: Error ST-E001 is in diagnostics

### ST-E002: task_id does not match the task folder name

* **Trigger**: `task_id` field value does not equal folder name
* **Setup**: Create `step_tracker.json` with `"task_id": "wrong_id"`
* **Assert**: Error ST-E002 is in diagnostics

### ST-E003: steps is missing or not a list

* **Trigger**: `steps` key is absent or is not an array
* **Setup**: Create `step_tracker.json` with `"steps": "not a list"`
* **Assert**: Error ST-E003 is in diagnostics

### ST-E004: A step is missing required fields

* **Trigger**: A step object lacks `step`, `name`, `description`, or `status`
* **Setup**: Create a step entry without the `status` field
* **Assert**: Error ST-E004 is in diagnostics

### ST-E005: Step numbers are not sequential starting from 1

* **Trigger**: Step numbers have gaps or do not start at 1
* **Setup**: Create steps with `"step"` values 1, 3, 4
* **Assert**: Error ST-E005 is in diagnostics

### ST-E006: status is not one of the allowed values

* **Trigger**: A step's `status` is not `pending`, `in_progress`, `completed`, `failed`, `skipped`
* **Setup**: Create a step with `"status": "running"`
* **Assert**: Error ST-E006 is in diagnostics

### ST-W001: A completed/failed/skipped step has log_file set to null

* **Trigger**: A step with terminal status has `"log_file": null`
* **Setup**: Create a completed step with `"log_file": null`
* **Assert**: Warning ST-W001 is in diagnostics

### ST-W002: log_file path does not point to an existing file

* **Trigger**: `log_file` is set but the path does not exist on disk
* **Setup**: Set `"log_file": "logs/steps/099_nonexistent/"`
* **Assert**: Warning ST-W002 is in diagnostics

### ST-W003: started_at is null for a non-pending step

* **Trigger**: A step with status other than `pending` has `"started_at": null`
* **Setup**: Create an `in_progress` step with `"started_at": null`
* **Assert**: Warning ST-W003 is in diagnostics

### ST-W004: completed_at is null for a completed/failed/skipped step

* **Trigger**: A terminal-status step has `"completed_at": null`
* **Setup**: Create a completed step with `"completed_at": null`
* **Assert**: Warning ST-W004 is in diagnostics

* * *

## 16. Category Specification (CA)

**Spec**: `arf/specifications/category_specification.md`

### CA-E001: description.json is missing or not valid JSON

* **Trigger**: `description.json` does not exist or is not valid JSON
* **Setup**: Create category folder without `description.json`
* **Assert**: Error CA-E001 is in diagnostics

### CA-E002: Required field missing in description.json

* **Trigger**: Any of `spec_version`, `name`, `short_description`, `detailed_description` is missing
* **Setup**: Create `description.json` without `name`
* **Assert**: Error CA-E002 is in diagnostics

### CA-E003: spec_version is not an integer

* **Trigger**: `spec_version` is a string or other non-integer
* **Setup**: Create `description.json` with `"spec_version": "1"`
* **Assert**: Error CA-E003 is in diagnostics

### CA-E004: Category slug format is invalid

* **Trigger**: Folder name uses uppercase, underscores, spaces, or starts with a non-letter
* **Setup**: Create `meta/categories/Supervised_WSD/`
* **Assert**: Error CA-E004 is in diagnostics

### CA-W001: short_description exceeds 200 characters

* **Trigger**: `short_description` longer than 200 characters
* **Setup**: Create a 201-character `short_description`
* **Assert**: Warning CA-W001 is in diagnostics

### CA-W002: detailed_description is under 50 characters

* **Trigger**: `detailed_description` shorter than 50 characters
* **Setup**: Create `"detailed_description": "Brief."`
* **Assert**: Warning CA-W002 is in diagnostics

### CA-W003: detailed_description exceeds 1000 characters

* **Trigger**: `detailed_description` longer than 1000 characters
* **Setup**: Create a 1001-character string
* **Assert**: Warning CA-W003 is in diagnostics

### CA-W004: name exceeds 50 characters

* **Trigger**: `name` longer than 50 characters
* **Setup**: Create a 51-character `name`
* **Assert**: Warning CA-W004 is in diagnostics

* * *

## 17. Compare Literature Specification (CL)

**Spec**: `arf/specifications/compare_literature_specification.md`

### CL-E001: File exists but has no YAML frontmatter

* **Trigger**: `compare_literature.md` exists but does not start with `---` frontmatter
* **Setup**: Create `compare_literature.md` starting with a heading
* **Assert**: Error CL-E001 is in diagnostics

### CL-E002: Frontmatter missing required field

* **Trigger**: Frontmatter does not contain `spec_version`, `task_id`, or `date_compared`
* **Setup**: Create frontmatter without `date_compared`
* **Assert**: Error CL-E002 is in diagnostics

### CL-E003: Missing mandatory section

* **Trigger**: File is missing any of: `## Summary`, `## Comparison Table`,
  `## Methodology Differences`, `## Analysis`, `## Limitations`
* **Setup**: Create file without `## Analysis`
* **Assert**: Error CL-E003 is in diagnostics

### CL-E004: Comparison Table section has no markdown table

* **Trigger**: `## Comparison Table` section exists but contains no `|...|` table syntax
* **Setup**: Write `## Comparison Table` section with only prose
* **Assert**: Error CL-E004 is in diagnostics

### CL-E005: Comparison table has fewer than 2 data rows

* **Trigger**: The markdown table has only a header and separator but fewer than 2 data rows
* **Setup**: Create a comparison table with only 1 data row
* **Assert**: Error CL-E005 is in diagnostics

### CL-W001: Total word count is under 150

* **Trigger**: The file has fewer than 150 words
* **Setup**: Create a minimal file with 100 words
* **Assert**: Warning CL-W001 is in diagnostics

### CL-W002: Table data rows missing numeric values

* **Trigger**: Published Value or Our Value columns contain non-numeric content (like `"--"`)
* **Setup**: Create a data row with `--` in Published Value column
* **Assert**: Warning CL-W002 is in diagnostics

### CL-W003: No citation keys or paper references found

* **Trigger**: The document contains no citation keys like `Raganato2017`
* **Setup**: Write the document without any citation keys
* **Assert**: Warning CL-W003 is in diagnostics

* * *

## 18. Remote Machines Specification (RM)

**Spec**: `arf/specifications/remote_machines_specification.md`

### RM-E001: machine_log.json lists a machine without destroyed_at

* **Trigger**: A machine entry in `machine_log.json` has `"destroyed_at": null` when the task is
  complete
* **Setup**: Create `machine_log.json` with a machine where `destroyed_at` is null
* **Assert**: Error RM-E001 is in diagnostics

### RM-E002: Vast.ai API confirms instance is still running/active

* **Trigger**: The API reports the instance is not destroyed
* **Setup**: Have an instance ID that the API shows as running
* **Assert**: Error RM-E002 is in diagnostics

### RM-E003: machine_log.json is missing or not valid JSON

* **Trigger**: File does not exist or contains invalid JSON
* **Setup**: Do not create `machine_log.json` when setup-machines step was executed
* **Assert**: Error RM-E003 is in diagnostics

### RM-E004: A required field is missing from a machine entry

* **Trigger**: A machine object is missing any required field (e.g., `provider`, `instance_id`,
  `offer_id`, `search_criteria`, `selected_offer`, `selection_rationale`, `image`, `disk_gb`,
  `ssh_host`, `ssh_port`, `gpu_verified`, `cuda_version`, `created_at`, `ready_at`, `destroyed_at`,
  `total_duration_hours`, `total_cost_usd`)
* **Setup**: Create a machine entry without `ssh_host`
* **Assert**: Error RM-E004 is in diagnostics

### RM-E005: instance_id mismatch with remote_machines_used.json

* **Trigger**: `instance_id` in `machine_log.json` does not match `machine_id` in
  `remote_machines_used.json`
* **Setup**: Use `"instance_id": "123"` in machine_log but `"machine_id": "456"` in
  remote_machines_used
* **Assert**: Error RM-E005 is in diagnostics

### RM-E006: total_cost_usd mismatch with remote_machines_used.json

* **Trigger**: `total_cost_usd` in `machine_log.json` does not match `cost_usd` in
  `remote_machines_used.json`
* **Setup**: Use `total_cost_usd: 5.0` in machine_log but `cost_usd: 3.0` in remote_machines_used
* **Assert**: Error RM-E006 is in diagnostics

### RM-W001: Vast.ai API unreachable

* **Trigger**: Cannot contact the API to confirm destruction, but `destroyed_at` is present
* **Setup**: Make the API unreachable (network mocking) while `destroyed_at` is set
* **Assert**: Warning RM-W001 is in diagnostics

### RM-W002: Actual cost exceeds plan estimate by more than 50%

* **Trigger**: `total_cost_usd` is more than 1.5x the planned cost
* **Setup**: Set `total_cost_usd: 15.0` when the plan estimated $8.0
* **Assert**: Warning RM-W002 is in diagnostics

### RM-W003: Machine was running for more than 12 hours

* **Trigger**: `total_duration_hours` exceeds 12
* **Setup**: Set `"total_duration_hours": 15.0`
* **Assert**: Warning RM-W003 is in diagnostics

### RM-W004: selection_rationale is empty or under 20 characters

* **Trigger**: `selection_rationale` is `""` or very short
* **Setup**: Set `"selection_rationale": "cheap"`
* **Assert**: Warning RM-W004 is in diagnostics

* * *

## 19. Agent Skills Specification (SK)

**Spec**: `arf/specifications/agent_skills_specification.md`

### SK-E001: SKILL.md is missing or empty

* **Trigger**: `arf/skills/<skill_name>/SKILL.md` does not exist or is empty
* **Setup**: Create skill directory without `SKILL.md`
* **Assert**: Error SK-E001 is in diagnostics

### SK-E002: YAML frontmatter is missing or not delimited by ---

* **Trigger**: `SKILL.md` does not start with `---` delimited YAML
* **Setup**: Create `SKILL.md` without frontmatter
* **Assert**: Error SK-E002 is in diagnostics

### SK-E003: name is missing from frontmatter

* **Trigger**: Frontmatter does not include a `name` field
* **Setup**: Create frontmatter with only `description`
* **Assert**: Error SK-E003 is in diagnostics

### SK-E004: description is missing from frontmatter

* **Trigger**: Frontmatter does not include a `description` field
* **Setup**: Create frontmatter with only `name`
* **Assert**: Error SK-E004 is in diagnostics

### SK-E005: Frontmatter name does not match the skill directory slug

* **Trigger**: `name` field differs from the directory name
* **Setup**: Create `arf/skills/research-internet/SKILL.md` with `name: "research-papers"`
* **Assert**: Error SK-E005 is in diagnostics

### SK-E006: Required body section is missing

* **Trigger**: Body is missing any of: `# <title>`, `**Version**: N`, `## Goal`, `## Inputs`,
  `## Context`, `## Steps`, `## Done When`, `## Forbidden`
* **Setup**: Create `SKILL.md` without `## Forbidden`
* **Assert**: Error SK-E006 is in diagnostics

### SK-E007: .claude/skills/<skill_name> is missing or has the wrong link

* **Trigger**: The Claude Code discovery symlink does not exist or points to the wrong target
* **Setup**: Do not create `.claude/skills/<skill_name>` symlink
* **Assert**: Error SK-E007 is in diagnostics

### SK-E008: .codex/skills/<skill_name> is missing or has the wrong link

* **Trigger**: The Codex discovery symlink does not exist or points to the wrong target
* **Setup**: Do not create `.codex/skills/<skill_name>` symlink
* **Assert**: Error SK-E008 is in diagnostics

### SK-E009: A discovery symlink does not resolve to a directory with SKILL.md

* **Trigger**: The symlink exists but resolves to a directory without `SKILL.md`
* **Setup**: Create a symlink pointing to an empty directory
* **Assert**: Error SK-E009 is in diagnostics

### SK-W001: The description is too vague to explain when the skill should run

* **Trigger**: `description` is too generic (e.g., "A skill.")
* **Setup**: Create frontmatter with `description: "Does things."`
* **Assert**: Warning SK-W001 is in diagnostics

### SK-W002: Output Format is missing for a skill that produces files

* **Trigger**: Skill produces output files but has no `## Output Format` section
* **Setup**: Create a skill with `## Steps` that write files but no `## Output Format`
* **Assert**: Warning SK-W002 is in diagnostics

### SK-W003: Optional tool-specific metadata appears without clear need

* **Trigger**: Frontmatter contains tool-specific keys that are not clearly needed
* **Setup**: Add `claude_specific_key: true` to frontmatter
* **Assert**: Warning SK-W003 is in diagnostics

* * *

## 20. Project Budget Specification (PB)

**Spec**: `arf/specifications/project_budget_specification.md`

### PB-E001: project/budget.json does not exist

* **Trigger**: `project/budget.json` file is missing
* **Setup**: Do not create `project/budget.json`
* **Assert**: Error PB-E001 is in diagnostics

### PB-E002: project/budget.json is not readable JSON

* **Trigger**: File contains invalid JSON
* **Setup**: Create `budget.json` with content `{broken`
* **Assert**: Error PB-E002 is in diagnostics

### PB-E003: top-level value is not a JSON object

* **Trigger**: File contains an array or scalar
* **Setup**: Create `budget.json` with content `[]`
* **Assert**: Error PB-E003 is in diagnostics

### PB-E004: A required field is missing or has the wrong type/value

* **Trigger**: Any of `total_budget`, `currency`, `per_task_default_limit`, `available_services`,
  `alerts` (with `warn_at_percent`, `stop_at_percent`) is missing or has wrong type
* **Setup 1**: Omit `currency` field
* **Assert 1**: Error PB-E004
* **Setup 2**: Set `total_budget` to `"two thousand"`
* **Assert 2**: Error PB-E004
* **Setup 3**: Set `currency` to `"usd"` (not uppercase)
* **Assert 3**: Error PB-E004
* **Setup 4**: Set `stop_at_percent` to 70 and `warn_at_percent` to 80 (stop < warn)
* **Assert 4**: Error PB-E004
* **Note**: The spec lists many sub-rules that this error covers: negative numbers, non-3-letter
  currency, duplicate services, percent bounds, etc.

### PB-W001: per_task_default_limit exceeds total_budget

* **Trigger**: `per_task_default_limit` > `total_budget`
* **Setup**: Set `total_budget: 100` and `per_task_default_limit: 200`
* **Assert**: Warning PB-W001 is in diagnostics

### PB-W002: available_services is empty

* **Trigger**: `available_services` is `[]`
* **Setup**: Create `budget.json` with `"available_services": []`
* **Assert**: Warning PB-W002 is in diagnostics

* * *

## 21. Project Description Specification (PD)

**Spec**: `arf/specifications/project_description_specification.md`

### PD-E001: project/description.md does not exist

* **Trigger**: `project/description.md` is missing
* **Setup**: Do not create `project/description.md`
* **Assert**: Error PD-E001 is in diagnostics

### PD-E002: Missing mandatory section

* **Trigger**: Any of `## Goal`, `## Scope`, `## Research Questions`, `## Success Criteria`,
  `## Key References`, `## Current Phase` is missing
* **Setup**: Create file without `## Research Questions`
* **Assert**: Error PD-E002 is in diagnostics

### PD-E003: No # heading or multiple # headings

* **Trigger**: File has zero or more than one `#` title heading
* **Setup 1**: Create file without any `#` heading
* **Assert 1**: Error PD-E003
* **Setup 2**: Create file with two `#` headings
* **Assert 2**: Error PD-E003

### PD-E004: Scope section missing In Scope or Out of Scope subsection

* **Trigger**: `## Scope` exists but is missing `### In Scope` or `### Out of Scope`
* **Setup**: Create `## Scope` without `### Out of Scope`
* **Assert**: Error PD-E004 is in diagnostics

### PD-W001: Goal section under 30 words

* **Trigger**: `## Goal` has fewer than 30 words
* **Setup**: Write `## Goal` with 15 words
* **Assert**: Warning PD-W001 is in diagnostics

### PD-W002: Research Questions has fewer than 3 numbered items

* **Trigger**: `## Research Questions` has fewer than 3 numbered list items
* **Setup**: Write only 2 numbered questions
* **Assert**: Warning PD-W002 is in diagnostics

### PD-W003: Research Questions has more than 7 numbered items

* **Trigger**: `## Research Questions` has more than 7 numbered items
* **Setup**: Write 8 numbered questions
* **Assert**: Warning PD-W003 is in diagnostics

### PD-W004: Success Criteria has fewer than 3 bullet items

* **Trigger**: `## Success Criteria` has fewer than 3 bullets
* **Setup**: Write only 2 bullet criteria
* **Assert**: Warning PD-W004 is in diagnostics

### PD-W005: Key References has fewer than 3 bullet items

* **Trigger**: `## Key References` has fewer than 3 bullets
* **Setup**: Write only 2 bullet references
* **Assert**: Warning PD-W005 is in diagnostics

### PD-W006: Current Phase under 15 words

* **Trigger**: `## Current Phase` has fewer than 15 words
* **Setup**: Write `## Current Phase` with 10 words
* **Assert**: Warning PD-W006 is in diagnostics

* * *

## 22. Paper Asset Specification (PA)

**Spec**: `meta/asset_types/paper/specification.md`

### PA-E001: details.json is missing or not valid JSON

* **Trigger**: `details.json` does not exist or is invalid JSON
* **Setup**: Create paper folder without `details.json`
* **Assert**: Error PA-E001 is in diagnostics

### PA-E002: The canonical summary document is missing

* **Trigger**: The file referenced by `summary_path` (or fallback `summary.md`) does not exist
* **Setup**: Create paper folder with `details.json` but no summary document
* **Assert**: Error PA-E002 is in diagnostics

### PA-E003: files/ directory missing or empty when download_status is success

* **Trigger**: `download_status` is `"success"` but `files/` is missing or empty
* **Setup**: Create paper with `"download_status": "success"` but empty `files/`
* **Assert**: Error PA-E003 is in diagnostics

### PA-E004: paper_id in details.json does not match folder name

* **Trigger**: `paper_id` value differs from the folder name
* **Setup**: Create folder `10.1234_v1_foo/` with `"paper_id": "10.1234_v1_bar"`
* **Assert**: Error PA-E004 is in diagnostics

### PA-E005: Required field missing in details.json

* **Trigger**: Any required field is absent (`spec_version`, `paper_id`, `doi`, `title`, `url`,
  `year`, `authors`, `institutions`, `journal`, `venue_type`, `categories`, `abstract`,
  `citation_key`, `files`, `download_status`, `download_failure_reason`, `added_by_task`,
  `date_added`; plus `summary_path` in v3)
* **Setup**: Create `details.json` without `title`
* **Assert**: Error PA-E005 is in diagnostics

### PA-E006: citation_key in summary frontmatter does not match details.json

* **Trigger**: Summary frontmatter `citation_key` differs from `details.json`
* **Setup**: Set `citation_key: "Wrong2024"` in summary frontmatter
* **Assert**: Error PA-E006 is in diagnostics

### PA-E007: paper_id in summary frontmatter does not match details.json

* **Trigger**: Summary frontmatter `paper_id` differs from `details.json`
* **Setup**: Set `paper_id: "wrong_id"` in summary frontmatter
* **Assert**: Error PA-E007 is in diagnostics

### PA-E008: A file listed in details.json files does not exist

* **Trigger**: A path in the `files` array does not exist on disk
* **Setup**: List `"files/nonexistent.pdf"` in `files` but do not create the file
* **Assert**: Error PA-E008 is in diagnostics

### PA-E009: The canonical summary document is missing a mandatory section

* **Trigger**: Summary is missing any of: `## Metadata`, `## Abstract`, `## Overview`,
  `## Architecture, Models and Methods`, `## Results`, `## Innovations`, `## Datasets`,
  `## Main Ideas`, `## Summary`
* **Setup**: Create summary without `## Innovations`
* **Assert**: Error PA-E009 is in diagnostics

### PA-E010: venue_type is not one of the allowed values

* **Trigger**: `venue_type` is not one of `journal`, `conference`, `workshop`, `preprint`, `book`,
  `thesis`, `technical_report`, `other`
* **Setup**: Create `details.json` with `"venue_type": "magazine"`
* **Assert**: Error PA-E010 is in diagnostics

### PA-E011: Folder name contains / characters (unescaped DOI)

* **Trigger**: The folder name has literal `/` characters
* **Setup**: Create folder `10.1234/v1/foo/` (impossible on most filesystems, but the check guards
  against it)
* **Assert**: Error PA-E011 is in diagnostics

### PA-E012: The canonical summary document is missing YAML frontmatter

* **Trigger**: Summary document has no `---` delimited frontmatter
* **Setup**: Create summary.md without frontmatter
* **Assert**: Error PA-E012 is in diagnostics

### PA-E013: spec_version is missing from details.json or summary frontmatter

* **Trigger**: `spec_version` is absent from either file
* **Setup**: Create `details.json` without `spec_version`
* **Assert**: Error PA-E013 is in diagnostics

### PA-E014: download_status is failed but download_failure_reason is null or empty

* **Trigger**: `download_status` is `"failed"` but `download_failure_reason` is `null` or `""`
* **Setup**: Set `"download_status": "failed", "download_failure_reason": null`
* **Assert**: Error PA-E014 is in diagnostics

### PA-E015: download_status is not success or failed

* **Trigger**: `download_status` is an unexpected value
* **Setup**: Set `"download_status": "pending"`
* **Assert**: Error PA-E015 is in diagnostics

### PA-W001: The canonical summary document total word count is under 500

* **Trigger**: Summary has fewer than 500 words
* **Setup**: Create a 300-word summary
* **Assert**: Warning PA-W001 is in diagnostics

### PA-W002: Results section has fewer than 5 bullet points

* **Trigger**: `## Results` section has fewer than 5 bullet items
* **Setup**: Create `## Results` with 3 bullets
* **Assert**: Warning PA-W002 is in diagnostics

### PA-W003: Main Ideas section has fewer than 3 bullet points

* **Trigger**: `## Main Ideas` has fewer than 3 bullets
* **Setup**: Create `## Main Ideas` with 2 bullets
* **Assert**: Warning PA-W003 is in diagnostics

### PA-W004: Summary section does not have 4 paragraphs

* **Trigger**: `## Summary` section does not have exactly 4 paragraphs
* **Setup**: Create `## Summary` with 2 paragraphs
* **Assert**: Warning PA-W004 is in diagnostics

### PA-W005: A category does not exist in meta/categories/

* **Trigger**: A category slug in `categories` does not match a folder
* **Setup**: Use `"categories": ["nonexistent-cat"]`
* **Assert**: Warning PA-W005 is in diagnostics

### PA-W006: doi is null but folder name does not start with no-doi_

* **Trigger**: `doi` is `null` but folder name does not follow the `no-doi_*` convention
* **Setup**: Create folder `custom-name/` with `"doi": null`
* **Assert**: Warning PA-W006 is in diagnostics

### PA-W007: No author has a non-null country field

* **Trigger**: All authors have `"country": null`
* **Setup**: Create all authors without country
* **Assert**: Warning PA-W007 is in diagnostics

### PA-W008: abstract field is empty or under 50 words

* **Trigger**: `abstract` is `""` or under 50 words
* **Setup**: Create `"abstract": "Short."`
* **Assert**: Warning PA-W008 is in diagnostics

### PA-W009: date_published is null

* **Trigger**: `date_published` is `null`
* **Setup**: Set `"date_published": null`
* **Assert**: Warning PA-W009 is in diagnostics

### PA-W010: Invalid ISO 3166-1 alpha-2 country, or institution has null country

* **Trigger**: A `country` field is not a valid 2-letter code, or an institution has `null` country
* **Setup**: Set author `"country": "USA"` (3 letters) or institution `"country": null`
* **Assert**: Warning PA-W010 is in diagnostics

### PA-W011: date_published does not match ISO 8601 format

* **Trigger**: `date_published` is not `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`
* **Setup**: Set `"date_published": "March 2024"`
* **Assert**: Warning PA-W011 is in diagnostics

* * *

## 23. Library Asset Specification (LA)

**Spec**: `meta/asset_types/library/specification.md`

### LA-E001: details.json is missing or not valid JSON

* **Trigger**: `details.json` does not exist or is invalid JSON
* **Setup**: Create library folder without `details.json`
* **Assert**: Error LA-E001 is in diagnostics

### LA-E002: The canonical description document is missing

* **Trigger**: The file referenced by `description_path` (or fallback `description.md`) does not
  exist
* **Setup**: Create library with `details.json` but no description document
* **Assert**: Error LA-E002 is in diagnostics

### LA-E004: library_id in details.json does not match folder name

* **Trigger**: `library_id` differs from folder name
* **Setup**: Create folder `wsd_loader/` with `"library_id": "wsd_scorer"`
* **Assert**: Error LA-E004 is in diagnostics

### LA-E005: Required field missing in details.json

* **Trigger**: Any required field is absent (`spec_version`, `library_id`, `name`, `version`,
  `short_description`, `module_paths`, `entry_points`, `dependencies`, `categories`,
  `created_by_task`, `date_created`; plus `description_path` in v2)
* **Setup**: Create `details.json` without `version`
* **Assert**: Error LA-E005 is in diagnostics

### LA-E006: module_paths is empty

* **Trigger**: `module_paths` is `[]`
* **Setup**: Create `details.json` with `"module_paths": []`
* **Assert**: Error LA-E006 is in diagnostics

### LA-E008: A file in module_paths does not exist

* **Trigger**: A path in `module_paths` does not exist relative to task root
* **Setup**: List `"code/nonexistent.py"` in `module_paths`
* **Assert**: Error LA-E008 is in diagnostics

### LA-E009: The canonical description document is missing a mandatory section

* **Trigger**: Description is missing any of: `## Metadata`, `## Overview`, `## API Reference`,
  `## Usage Examples`, `## Dependencies`, `## Testing`, `## Main Ideas`, `## Summary`
* **Setup**: Create description without `## API Reference`
* **Assert**: Error LA-E009 is in diagnostics

### LA-E010: entry_points[].kind is not one of the allowed values

* **Trigger**: An entry point's `kind` is not `function`, `class`, or `script`
* **Setup**: Create an entry point with `"kind": "method"`
* **Assert**: Error LA-E010 is in diagnostics

### LA-E011: Folder name does not match library ID format

* **Trigger**: Folder name does not match `^[a-z][a-z0-9]*(_[a-z0-9]+)*$`
* **Setup**: Create folder `WSD-Loader/`
* **Assert**: Error LA-E011 is in diagnostics

### LA-E012: The canonical description document is missing YAML frontmatter

* **Trigger**: Description document has no frontmatter
* **Setup**: Create description.md without `---` delimiters
* **Assert**: Error LA-E012 is in diagnostics

### LA-E013: spec_version is missing from details.json or description frontmatter

* **Trigger**: `spec_version` absent from either file
* **Setup**: Create `details.json` without `spec_version`
* **Assert**: Error LA-E013 is in diagnostics

### LA-E016: An entry_points entry is missing required fields

* **Trigger**: An entry point object lacks `name`, `kind`, `module`, or `description`
* **Setup**: Create entry point without `module`
* **Assert**: Error LA-E016 is in diagnostics

### LA-W001: The canonical description document total word count is under 400

* **Trigger**: Description has fewer than 400 words
* **Setup**: Create a 300-word description
* **Assert**: Warning LA-W001 is in diagnostics

### LA-W003: Main Ideas section has fewer than 3 bullet points

* **Trigger**: `## Main Ideas` has fewer than 3 bullets
* **Setup**: Create 2 bullet points
* **Assert**: Warning LA-W003 is in diagnostics

### LA-W004: Summary section does not have 2-3 paragraphs

* **Trigger**: `## Summary` has 1 or 4+ paragraphs
* **Setup**: Create `## Summary` with 1 paragraph
* **Assert**: Warning LA-W004 is in diagnostics

### LA-W005: A category does not exist in meta/categories/

* **Trigger**: A category slug is not a real folder
* **Setup**: Use `"categories": ["fake-cat"]`
* **Assert**: Warning LA-W005 is in diagnostics

### LA-W008: short_description is empty or under 10 words

* **Trigger**: `short_description` is very short
* **Setup**: Set `"short_description": "A lib."`
* **Assert**: Warning LA-W008 is in diagnostics

### LA-W013: Overview section word count is under 80

* **Trigger**: `## Overview` has fewer than 80 words
* **Setup**: Write a 50-word overview
* **Assert**: Warning LA-W013 is in diagnostics

### LA-W014: No test_paths provided

* **Trigger**: `test_paths` is absent or empty
* **Setup**: Omit `test_paths` from `details.json`
* **Assert**: Warning LA-W014 is in diagnostics

### LA-W015: A test_paths file does not exist

* **Trigger**: A path in `test_paths` does not exist
* **Setup**: List `"code/test_nonexistent.py"` in `test_paths`
* **Assert**: Warning LA-W015 is in diagnostics

### LA-W016: API Reference section word count is under 100

* **Trigger**: `## API Reference` has fewer than 100 words
* **Setup**: Write a 50-word API Reference
* **Assert**: Warning LA-W016 is in diagnostics

* * *

## 24. Dataset Asset Specification (DA)

**Spec**: `meta/asset_types/dataset/specification.md`

### DA-E001: details.json is missing or not valid JSON

* **Trigger**: `details.json` absent or invalid
* **Setup**: Create dataset folder without `details.json`
* **Assert**: Error DA-E001 is in diagnostics

### DA-E002: The canonical description document is missing

* **Trigger**: Description file does not exist
* **Setup**: Create dataset with `details.json` but no description document
* **Assert**: Error DA-E002 is in diagnostics

### DA-E003: files/ directory is missing or empty

* **Trigger**: `files/` does not exist or contains no files
* **Setup**: Create dataset folder without `files/` directory
* **Assert**: Error DA-E003 is in diagnostics

### DA-E004: dataset_id in details.json does not match folder name

* **Trigger**: `dataset_id` value differs from folder name
* **Setup**: Create folder `semcor-3.0/` with `"dataset_id": "semcor-2.0"`
* **Assert**: Error DA-E004 is in diagnostics

### DA-E005: Required field missing in details.json

* **Trigger**: Any required field is absent (`spec_version`, `dataset_id`, `name`, `version`,
  `short_description`, `source_paper_id`, `url`, `year`, `authors`, `institutions`, `license`,
  `access_kind`, `size_description`, `files`, `categories`; plus `description_path` in v2)
* **Setup**: Create `details.json` without `year`
* **Assert**: Error DA-E005 is in diagnostics

### DA-E007: dataset_id in description frontmatter does not match folder name

* **Trigger**: Description frontmatter `dataset_id` differs from folder name
* **Setup**: Set `dataset_id: "wrong-id"` in description frontmatter
* **Assert**: Error DA-E007 is in diagnostics

### DA-E008: A file listed in details.json files[].path does not exist

* **Trigger**: A `path` in the `files` list does not exist on disk
* **Setup**: List `"files/nonexistent.xml"` in `files`
* **Assert**: Error DA-E008 is in diagnostics

### DA-E009: The canonical description document is missing a mandatory section

* **Trigger**: Description is missing any of: `## Metadata`, `## Overview`,
  `## Content & Annotation`, `## Statistics`, `## Usage Notes`, `## Main Ideas`, `## Summary`
* **Setup**: Create description without `## Statistics`
* **Assert**: Error DA-E009 is in diagnostics

### DA-E010: access_kind is not one of the allowed values

* **Trigger**: `access_kind` is not `public`, `restricted`, or `proprietary`
* **Setup**: Set `"access_kind": "open"`
* **Assert**: Error DA-E010 is in diagnostics

### DA-E011: Folder name does not match dataset ID format

* **Trigger**: Folder name does not match `^[a-z0-9]+([.\-][a-z0-9]+)*$`
* **Setup**: Create folder `SemCor_3.0/`
* **Assert**: Error DA-E011 is in diagnostics

### DA-E012: The canonical description document is missing YAML frontmatter

* **Trigger**: Description has no frontmatter
* **Setup**: Create description without `---` delimiters
* **Assert**: Error DA-E012 is in diagnostics

### DA-E013: spec_version is missing from details.json or description frontmatter

* **Trigger**: `spec_version` absent from either file
* **Setup**: Omit `spec_version` from `details.json`
* **Assert**: Error DA-E013 is in diagnostics

### DA-E016: An entry in files is not a valid DatasetFile object

* **Trigger**: A `files` entry is missing `path`, `description`, or `format`
* **Setup**: Create a file entry without `format`
* **Assert**: Error DA-E016 is in diagnostics

### DA-W001: The canonical description document total word count is under 400

* **Trigger**: Description under 400 words
* **Setup**: Create a 300-word description
* **Assert**: Warning DA-W001 is in diagnostics

### DA-W003: Main Ideas section has fewer than 3 bullet points

* **Trigger**: `## Main Ideas` under 3 bullets
* **Setup**: Write 2 bullets
* **Assert**: Warning DA-W003 is in diagnostics

### DA-W004: Summary section does not have 2-3 paragraphs

* **Trigger**: `## Summary` not 2-3 paragraphs
* **Setup**: Write 1 paragraph
* **Assert**: Warning DA-W004 is in diagnostics

### DA-W005: A category does not exist in meta/categories/

* **Trigger**: Category slug has no folder
* **Setup**: Use `"categories": ["fake"]`
* **Assert**: Warning DA-W005 is in diagnostics

### DA-W007: No author has a non-null country field

* **Trigger**: All authors have null country
* **Setup**: Create all authors without country
* **Assert**: Warning DA-W007 is in diagnostics

### DA-W008: short_description is empty or under 10 words

* **Trigger**: Very short `short_description`
* **Setup**: Set `"short_description": "Data."`
* **Assert**: Warning DA-W008 is in diagnostics

### DA-W009: date_published is null

* **Trigger**: `date_published` is null
* **Setup**: Set `"date_published": null`
* **Assert**: Warning DA-W009 is in diagnostics

### DA-W010: A country field is not a valid ISO 3166-1 alpha-2 code, or institution null country

* **Trigger**: Invalid country code or null institution country
* **Setup**: Set institution `"country": null`
* **Assert**: Warning DA-W010 is in diagnostics

### DA-W011: date_published does not match ISO 8601 format

* **Trigger**: `date_published` is not `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`
* **Setup**: Set `"date_published": "Jan 2020"`
* **Assert**: Warning DA-W011 is in diagnostics

### DA-W012: size_description is empty

* **Trigger**: `size_description` is `""`
* **Setup**: Set `"size_description": ""`
* **Assert**: Warning DA-W012 is in diagnostics

### DA-W013: Overview section word count is under 80

* **Trigger**: `## Overview` under 80 words
* **Setup**: Write 50-word overview
* **Assert**: Warning DA-W013 is in diagnostics

* * *

## 25. Answer Asset Specification (AA)

**Spec**: `meta/asset_types/answer/specification.md`

### AA-E001: details.json does not exist or is not valid JSON

* **Trigger**: `details.json` missing or invalid JSON
* **Setup**: Create answer folder without `details.json`
* **Assert**: Error AA-E001 is in diagnostics

### AA-E002: A canonical answer document is missing

* **Trigger**: Either the short answer or full answer canonical document does not exist
* **Setup**: Create answer folder with `details.json` but no `short_answer.md`
* **Assert**: Error AA-E002 is in diagnostics

### AA-E003: answer_id does not match the folder name

* **Trigger**: `answer_id` differs from folder name
* **Setup**: Create folder `when-to-use-gpu/` with `"answer_id": "when-to-use-cpu"`
* **Assert**: Error AA-E003 is in diagnostics

### AA-E004: answer_id format is invalid

* **Trigger**: `answer_id` does not match `^[a-z0-9]+(-[a-z0-9]+)*$`
* **Setup**: Create folder `When_To_Use/`
* **Assert**: Error AA-E004 is in diagnostics

### AA-E005: A required metadata field is missing

* **Trigger**: Any required field is absent (`spec_version`, `answer_id`, `question`, `short_title`,
  `categories`, `answer_methods`, `source_paper_ids`, `source_urls`, `source_task_ids`,
  `confidence`, `created_by_task`, `date_created`; plus `short_answer_path` and `full_answer_path`
  in v2)
* **Setup**: Create `details.json` without `question`
* **Assert**: Error AA-E005 is in diagnostics

### AA-E006: answer_methods contains an unknown value

* **Trigger**: An entry in `answer_methods` is not a recognized value
* **Setup**: Set `"answer_methods": ["magic"]`
* **Assert**: Error AA-E006 is in diagnostics
* **Ambiguity**: The spec lists `answer_methods` as required and says they must align with evidence
  but does not explicitly list all allowed values. The recognized values appear to include at least
  `"internet"`, `"code-experiment"`, and likely `"papers"` based on the evidence sections.

### AA-E007: confidence is not one of the allowed values

* **Trigger**: `confidence` is not `high`, `medium`, or `low`
* **Setup**: Set `"confidence": "very-high"`
* **Assert**: Error AA-E007 is in diagnostics

### AA-E008: A referenced task ID does not exist

* **Trigger**: A task ID in `source_task_ids` does not correspond to an existing task folder
* **Setup**: Set `"source_task_ids": ["t9999_nonexistent"]`
* **Assert**: Error AA-E008 is in diagnostics

### AA-E009: A referenced paper ID does not exist

* **Trigger**: A paper ID in `source_paper_ids` does not correspond to an existing paper asset
* **Setup**: Set `"source_paper_ids": ["10.9999_nonexistent"]`
* **Assert**: Error AA-E009 is in diagnostics

### AA-E010: A referenced URL is not a valid HTTP or HTTPS URL

* **Trigger**: A URL in `source_urls` is not a valid HTTP/HTTPS URL
* **Setup**: Set `"source_urls": ["ftp://example.com"]`
* **Assert**: Error AA-E010 is in diagnostics

### AA-E011: The canonical short answer document is missing a mandatory section

* **Trigger**: Short answer is missing `## Question`, `## Answer`, or `## Sources`
* **Setup**: Create short answer without `## Sources`
* **Assert**: Error AA-E011 is in diagnostics

### AA-E012: The canonical full answer document is missing a mandatory section

* **Trigger**: Full answer is missing any of: `## Question`, `## Short Answer`,
  `## Research Process`, `## Evidence from Papers`, `## Evidence from Internet Sources`,
  `## Evidence from Code or Experiments`, `## Synthesis`, `## Limitations`, `## Sources`
* **Setup**: Create full answer without `## Synthesis`
* **Assert**: Error AA-E012 is in diagnostics

### AA-E013: Answer in short answer document is not 2-5 sentences

* **Trigger**: `## Answer` section has fewer than 2 or more than 5 sentences
* **Setup**: Create `## Answer` with 1 sentence
* **Assert**: Error AA-E013 is in diagnostics

### AA-E014: No evidence references are provided in details.json

* **Trigger**: All three lists `source_paper_ids`, `source_urls`, `source_task_ids` are empty
* **Setup**: Set all three to `[]`
* **Assert**: Error AA-E014 is in diagnostics

### AA-W001: A category slug does not exist in meta/categories/

* **Trigger**: Category slug has no corresponding folder
* **Setup**: Use `"categories": ["fake"]`
* **Assert**: Warning AA-W001 is in diagnostics

### AA-W002: The question is suspiciously short

* **Trigger**: The `question` field is very short
* **Setup**: Set `"question": "Why?"`
* **Assert**: Warning AA-W002 is in diagnostics

### AA-W003: A required evidence section is present but too shallow

* **Trigger**: An evidence section (e.g., `## Evidence from Papers`) exists but is very short
* **Setup**: Write `## Evidence from Papers` with 1 sentence
* **Assert**: Warning AA-W003 is in diagnostics

### AA-W004: The full answer is very short for a research artifact

* **Trigger**: The full answer document total word count is very low
* **Setup**: Create a full answer with 100 words
* **Assert**: Warning AA-W004 is in diagnostics

* * *

## 26. Model Asset Specification (MA)

**Spec**: `meta/asset_types/model/specification.md`

### MA-E001: details.json is missing or not valid JSON

* **Trigger**: `details.json` absent or invalid
* **Setup**: Create model folder without `details.json`
* **Assert**: Error MA-E001 is in diagnostics

### MA-E002: The canonical description document is missing

* **Trigger**: Description file does not exist
* **Setup**: Create model with `details.json` but no description document
* **Assert**: Error MA-E002 is in diagnostics

### MA-E003: files/ directory is missing or empty

* **Trigger**: `files/` does not exist or is empty
* **Setup**: Create model folder without `files/` directory
* **Assert**: Error MA-E003 is in diagnostics

### MA-E004: model_id in details.json does not match folder name

* **Trigger**: `model_id` differs from folder name
* **Setup**: Create folder `bert-v1/` with `"model_id": "bert-v2"`
* **Assert**: Error MA-E004 is in diagnostics

### MA-E005: Required field missing in details.json

* **Trigger**: Any required field is absent (`spec_version`, `model_id`, `name`, `version`,
  `short_description`, `framework`, `base_model`, `architecture`, `training_task_id`,
  `training_dataset_ids`, `files`, `categories`, `created_by_task`, `date_created`; plus
  `description_path` in v2)
* **Setup**: Create `details.json` without `framework`
* **Assert**: Error MA-E005 is in diagnostics

### MA-E007: model_id in description frontmatter does not match folder name

* **Trigger**: Description frontmatter `model_id` differs from folder name
* **Setup**: Set `model_id: "wrong-id"` in description frontmatter
* **Assert**: Error MA-E007 is in diagnostics

### MA-E008: A file listed in details.json files[].path does not exist

* **Trigger**: A `path` in `files` does not exist on disk
* **Setup**: List `"files/nonexistent.pt"` in `files`
* **Assert**: Error MA-E008 is in diagnostics

### MA-E009: The canonical description document is missing a mandatory section

* **Trigger**: Description is missing any of: `## Metadata`, `## Overview`, `## Architecture`,
  `## Training`, `## Evaluation`, `## Usage Notes`, `## Main Ideas`, `## Summary`
* **Setup**: Create description without `## Training`
* **Assert**: Error MA-E009 is in diagnostics

### MA-E010: framework is not one of the allowed values

* **Trigger**: `framework` is not `pytorch`, `tensorflow`, `jax`, `onnx`, or `other`
* **Setup**: Set `"framework": "keras"`
* **Assert**: Error MA-E010 is in diagnostics

### MA-E011: Folder name does not match the model ID format

* **Trigger**: Folder name does not match `^[a-z0-9]+([.\-][a-z0-9]+)*$`
* **Setup**: Create folder `BERT_Base/`
* **Assert**: Error MA-E011 is in diagnostics

### MA-E012: The canonical description document is missing YAML frontmatter

* **Trigger**: Description has no frontmatter
* **Setup**: Create description without `---` delimiters
* **Assert**: Error MA-E012 is in diagnostics

### MA-E013: spec_version is missing from details.json or description frontmatter

* **Trigger**: `spec_version` absent from either file
* **Setup**: Omit `spec_version` from `details.json`
* **Assert**: Error MA-E013 is in diagnostics

### MA-E016: An entry in files is not a valid ModelFile object

* **Trigger**: A `files` entry is missing `path`, `description`, or `format`
* **Setup**: Create file entry without `description`
* **Assert**: Error MA-E016 is in diagnostics

### MA-W001: The canonical description document total word count is under 400

* **Trigger**: Description under 400 words
* **Setup**: Create 300-word description
* **Assert**: Warning MA-W001 is in diagnostics

### MA-W003: Main Ideas section has fewer than 3 bullet points

* **Trigger**: `## Main Ideas` under 3 bullets
* **Setup**: Write 2 bullets
* **Assert**: Warning MA-W003 is in diagnostics

### MA-W004: Summary section does not have 2-3 paragraphs

* **Trigger**: `## Summary` not 2-3 paragraphs
* **Setup**: Write 1 paragraph
* **Assert**: Warning MA-W004 is in diagnostics

### MA-W005: A category does not exist in meta/categories/

* **Trigger**: Category slug has no folder
* **Setup**: Use `"categories": ["fake"]`
* **Assert**: Warning MA-W005 is in diagnostics

### MA-W008: short_description is empty or under 10 words

* **Trigger**: Very short `short_description`
* **Setup**: Set `"short_description": "Model."`
* **Assert**: Warning MA-W008 is in diagnostics

### MA-W013: Overview section word count is under 80

* **Trigger**: `## Overview` under 80 words
* **Setup**: Write 50-word overview
* **Assert**: Warning MA-W013 is in diagnostics

### MA-W014: training_dataset_ids is empty

* **Trigger**: `training_dataset_ids` is `[]`
* **Setup**: Set `"training_dataset_ids": []`
* **Assert**: Warning MA-W014 is in diagnostics

### MA-W015: hyperparameters is missing or empty

* **Trigger**: `hyperparameters` is `null` or `{}`
* **Setup**: Omit `hyperparameters`
* **Assert**: Warning MA-W015 is in diagnostics

### MA-W016: training_metrics is missing or empty

* **Trigger**: `training_metrics` is `null` or `{}`
* **Setup**: Omit `training_metrics`
* **Assert**: Warning MA-W016 is in diagnostics

* * *

## 27. Predictions Asset Specification (PR)

**Spec**: `meta/asset_types/predictions/specification.md`

### PR-E001: details.json is missing or not valid JSON

* **Trigger**: `details.json` absent or invalid
* **Setup**: Create predictions folder without `details.json`
* **Assert**: Error PR-E001 is in diagnostics

### PR-E002: The canonical description document is missing

* **Trigger**: Description file does not exist
* **Setup**: Create predictions with `details.json` but no description document
* **Assert**: Error PR-E002 is in diagnostics

### PR-E003: files/ directory is missing or empty

* **Trigger**: `files/` does not exist or is empty
* **Setup**: Create predictions folder without `files/`
* **Assert**: Error PR-E003 is in diagnostics

### PR-E004: predictions_id in details.json does not match folder name

* **Trigger**: `predictions_id` differs from folder name
* **Setup**: Create folder `bert-on-raganato/` with `"predictions_id": "gpt-on-raganato"`
* **Assert**: Error PR-E004 is in diagnostics

### PR-E005: Required field missing in details.json

* **Trigger**: Any required field is absent (`spec_version`, `predictions_id`, `name`,
  `short_description`, `model_id`, `model_description`, `dataset_ids`, `prediction_format`,
  `prediction_schema`, `files`, `categories`, `created_by_task`, `date_created`; plus
  `description_path` in v2)
* **Setup**: Create `details.json` without `model_description`
* **Assert**: Error PR-E005 is in diagnostics

### PR-E007: predictions_id in description frontmatter does not match folder name

* **Trigger**: Description frontmatter `predictions_id` differs from folder name
* **Setup**: Set `predictions_id: "wrong-id"` in description frontmatter
* **Assert**: Error PR-E007 is in diagnostics

### PR-E008: A file listed in details.json files[].path does not exist

* **Trigger**: A `path` in `files` does not exist on disk
* **Setup**: List `"files/nonexistent.jsonl"` in `files`
* **Assert**: Error PR-E008 is in diagnostics

### PR-E009: The canonical description document is missing a mandatory section

* **Trigger**: Description is missing any of: `## Metadata`, `## Overview`, `## Model`, `## Data`,
  `## Prediction Format`, `## Metrics`, `## Main Ideas`, `## Summary`
* **Setup**: Create description without `## Prediction Format`
* **Assert**: Error PR-E009 is in diagnostics

### PR-E010: prediction_format is empty

* **Trigger**: `prediction_format` is `""`
* **Setup**: Set `"prediction_format": ""`
* **Assert**: Error PR-E010 is in diagnostics

### PR-E011: Folder name does not match the predictions ID format

* **Trigger**: Folder name does not match `^[a-z0-9]+([.\-][a-z0-9]+)*$`
* **Setup**: Create folder `BERT_Predictions/`
* **Assert**: Error PR-E011 is in diagnostics

### PR-E012: The canonical description document is missing YAML frontmatter

* **Trigger**: Description has no frontmatter
* **Setup**: Create description without `---` delimiters
* **Assert**: Error PR-E012 is in diagnostics

### PR-E013: spec_version is missing from details.json or description frontmatter

* **Trigger**: `spec_version` absent from either file
* **Setup**: Omit `spec_version` from `details.json`
* **Assert**: Error PR-E013 is in diagnostics

### PR-E016: An entry in files is not a valid PredictionFile object

* **Trigger**: A `files` entry is missing `path`, `description`, or `format`
* **Setup**: Create file entry without `format`
* **Assert**: Error PR-E016 is in diagnostics

### PR-W001: The canonical description document total word count is under 400

* **Trigger**: Description under 400 words
* **Setup**: Create 300-word description
* **Assert**: Warning PR-W001 is in diagnostics

### PR-W003: Main Ideas section has fewer than 3 bullet points

* **Trigger**: `## Main Ideas` under 3 bullets
* **Setup**: Write 2 bullets
* **Assert**: Warning PR-W003 is in diagnostics

### PR-W004: Summary section does not have 2-3 paragraphs

* **Trigger**: `## Summary` not 2-3 paragraphs
* **Setup**: Write 1 paragraph
* **Assert**: Warning PR-W004 is in diagnostics

### PR-W005: A category does not exist in meta/categories/

* **Trigger**: Category slug has no folder
* **Setup**: Use `"categories": ["fake"]`
* **Assert**: Warning PR-W005 is in diagnostics

### PR-W008: short_description is empty or under 10 words

* **Trigger**: Very short `short_description`
* **Setup**: Set `"short_description": "Preds."`
* **Assert**: Warning PR-W008 is in diagnostics

### PR-W013: Overview section word count is under 80

* **Trigger**: `## Overview` under 80 words
* **Setup**: Write 50-word overview
* **Assert**: Warning PR-W013 is in diagnostics

### PR-W014: model_id is null

* **Trigger**: `model_id` is `null` (no model asset linked)
* **Setup**: Set `"model_id": null`
* **Assert**: Warning PR-W014 is in diagnostics

### PR-W015: dataset_ids is empty

* **Trigger**: `dataset_ids` is `[]`
* **Setup**: Set `"dataset_ids": []`
* **Assert**: Warning PR-W015 is in diagnostics

### PR-W016: prediction_schema is under 10 words

* **Trigger**: `prediction_schema` is very short
* **Setup**: Set `"prediction_schema": "JSON lines."`
* **Assert**: Warning PR-W016 is in diagnostics

### PR-W017: instance_count is null

* **Trigger**: `instance_count` is `null`
* **Setup**: Omit or set `"instance_count": null`
* **Assert**: Warning PR-W017 is in diagnostics

* * *

## Summary Statistics

| Spec | Prefix | Errors | Warnings | Total |
| --- | --- | --- | --- | --- |
| Task File | TF | 16 | 6 | 22 |
| Task Folder | FD | 16 | 6 | 22 |
| Task Git | TG | 5 | 4 | 9 |
| Task Steps | TS | 3 | 2 | 5 |
| Task Results | TR | 18 (TR-E009 removed) | 13 (TR-W009 promoted) | 31 |
| Task Type | TY | 7 | 5 | 12 |
| Logs | LG | 8 | 8 | 16 |
| Plan | PL | 7 | 8 | 15 |
| Suggestions | SG | 13 | 6 | 19 |
| Corrections | (prose) | ~12 rules | 0 | ~12 |
| Metrics | MT | 8 | 2 | 10 |
| Research Papers | RP | 10 | 6 | 16 |
| Research Internet | RI | 11 | 7 | 18 |
| Research Code | RC | 9 | 5 | 14 |
| Step Tracker | ST | 6 | 4 | 10 |
| Category | CA | 4 | 4 | 8 |
| Compare Literature | CL | 5 | 3 | 8 |
| Remote Machines | RM | 6 | 4 | 10 |
| Agent Skills | SK | 9 | 3 | 12 |
| Project Budget | PB | 4 | 2 | 6 |
| Project Description | PD | 4 | 6 | 10 |
| Paper Asset | PA | 15 | 11 | 26 |
| Library Asset | LA | 12 | 9 | 21 |
| Dataset Asset | DA | 12 | 11 | 23 |
| Answer Asset | AA | 14 | 4 | 18 |
| Model Asset | MA | 13 | 9 | 22 |
| Predictions Asset | PR | 13 | 9 | 22 |
| **TOTAL** |  | **~262** | **~157** | **~419** |

* * *

## Ambiguities and Notes

1. **Corrections Specification**: No formal error/warning codes are defined. The verificator must
   translate the prose rules into diagnostic codes. The implementor decides the prefix (e.g.,
   `CO-`).

2. **TR-E009**: Explicitly marked as "Removed in v2" in the spec. No test should exist for it.

3. **TR-W009**: Explicitly marked as "Promoted to error TM-E005 in verify_task_metrics.py". The
   `TM-E005` code is referenced but not formally defined in any specification file -- it is an
   implementation-level code in the metrics verificator.

4. **AA-E006 (answer_methods)**: The spec says `answer_methods` must contain allowed values but does
   not provide an exhaustive list in a table. The allowed values must be inferred from the evidence
   sections: likely `"papers"`, `"internet"`, `"code-experiment"`, and possibly `"prior-tasks"`.

5. **FD-E013 and FD-E014**: These errors are skipped when the corresponding step is `"skipped"` in
   `step_tracker.json`. Tests should cover both the error case and the skip-exemption case.

6. **PA-E003**: When `download_status` is `"failed"`, the `files/` directory must contain a
   `.gitkeep` file. The error only fires when `download_status` is `"success"`.

7. **Corrections file_changes**: The spec defines `add`, `delete`, and `replace` as file-level
   actions but does not assign formal error codes for violations of file_changes rules.

8. **Gap in library codes**: LA-E003, LA-E007, LA-E014, LA-E015 are not defined in the spec (numbers
   are skipped). This is intentional -- the spec jumps from E002 to E004 and from E006 to E008, etc.

9. **Gap in dataset codes**: DA-E006, DA-E014, DA-E015 are not defined. Similar intentional gaps.

10. **Gap in model codes**: MA-E006, MA-E014, MA-E015 are not defined. Similar pattern.

11. **Gap in predictions codes**: PR-E006, PR-E014, PR-E015 are not defined. Similar pattern.

12. **Gap in paper codes**: PA-E016 and beyond are not defined. The paper spec stops at PA-E015.

13. **TR-W013 and TR-W014**: These warnings apply specifically to "experiment-type tasks". The spec
    does not define exactly how experiment-type is determined -- likely from `task_types` in
    `task.json`.
