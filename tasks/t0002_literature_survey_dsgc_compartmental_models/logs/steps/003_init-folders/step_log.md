---
spec_version: "3"
task_id: "t0002_literature_survey_dsgc_compartmental_models"
step_number: 3
step_name: "init-folders"
status: "completed"
started_at: "2026-04-18T23:12:40Z"
completed_at: "2026-04-18T23:13:00Z"
---
# Step 3: init-folders

## Summary

Initialised the mandatory task folder structure via `arf.scripts.utils.init_task_folders`. Created
13 top-level subdirectories with `.gitkeep` placeholders covering plan, research, results (with
`results/images/`), corrections, intervention, code, logs (with `commands/`, `searches/`,
`sessions/`, `steps/`), and the two expected asset-type folders (`assets/paper/` and
`assets/answer/`). The task root and `code/` directory each received an `__init__.py` so the package
can be imported as `tasks.t0002_literature_survey_dsgc_compartmental_models.code`.

## Actions Taken

1. Ran
   `uv run python -m arf.scripts.utils.init_task_folders t0002_literature_survey_dsgc_compartmental_models --step-log-dir logs/steps/003_init-folders`
   which created the 13 mandatory subdirectories with `.gitkeep` files plus `__init__.py` at the
   task root and in `code/`.
2. Confirmed that `assets/paper/` and `assets/answer/` exist since they are the expected asset
   directories for this survey (20 papers + 1 answer).

## Outputs

* `tasks/t0002_literature_survey_dsgc_compartmental_models/plan/.gitkeep`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/research/.gitkeep`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/results/.gitkeep`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/results/images/.gitkeep`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/corrections/.gitkeep`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/intervention/.gitkeep`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/code/.gitkeep`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/code/__init__.py`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/__init__.py`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/logs/commands/.gitkeep`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/logs/searches/.gitkeep`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/logs/sessions/.gitkeep`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/logs/steps/.gitkeep`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/assets/paper/.gitkeep`
* `tasks/t0002_literature_survey_dsgc_compartmental_models/assets/answer/.gitkeep`

## Issues

A first invocation with an absolute `--step-log-dir` argument was rejected by `init_task_folders`
because the helper requires a path relative to `tasks/<task_id>/`. The folder creation still
completed on the first run; the second invocation with a relative path was idempotent.
