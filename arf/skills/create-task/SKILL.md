---
name: "create-task"
description: "Create a new not-started task folder with task.json and task_description.md. Use when any skill or workflow needs to create a new task."
---
# Create Task

**Version**: 6

## Goal

Create a new task folder under `tasks/` containing a valid `task.json` and `task_description.md`,
following the task file specification. Accept a free-form task description and derive all structured
fields from it.

## Inputs

* `$TASK_DESCRIPTION` — free-form text describing the task. May include any relevant details: what
  the task does, why it matters, dependencies on other tasks, expected outputs, compute needs,
  budget estimates, source suggestion, etc. The skill extracts all structured fields from this text.
* `$TASK_INDEX` (optional) — numeric task index (1-9999). If omitted, determine the next available
  index from the tasks aggregator output (step 1).

## Context

Read before starting:

* `arf/specifications/task_file_specification.md`

* `arf/docs/howto/use_aggregators.md` — JSON output structure for all aggregators

* Available task types:

  ```bash
  uv run python -u -m arf.scripts.aggregators.aggregate_task_types --format json
  ```

* Existing tasks (for dependency validation and next task index):

  ```bash
  uv run python -u -m arf.scripts.aggregators.aggregate_tasks \
    --format json --detail short
  ```

* Existing suggestions (for source suggestion validation):

  ```bash
  uv run python -u -m arf.scripts.aggregators.aggregate_suggestions \
    --format json --detail short
  ```

* Project context — answers, datasets, libraries, and models produced by prior tasks:

  ```bash
  uv run python -u -m arf.scripts.aggregators.aggregate_answers \
    --format json --detail short
  uv run python -u -m arf.scripts.aggregators.aggregate_datasets \
    --format json --detail short
  uv run python -u -m arf.scripts.aggregators.aggregate_libraries \
    --format json --detail short
  uv run python -u -m arf.scripts.aggregators.aggregate_models \
    --format json --detail short
  ```

## Steps

1. **Read aggregator outputs.** Run all aggregators from the Context section. The first three (task
   types, tasks, suggestions) provide validation data. The project context aggregators (answers,
   datasets, libraries, models) inform the task description — they reveal what the project has
   already produced, what resources are available, and what work has been done. Use this context to
   write better task descriptions that reference existing assets and avoid duplicating completed
   work.

2. **Derive metadata fields from `$TASK_DESCRIPTION`.** Extract:

   * `name` — concise human-readable name (under 80 characters)
   * `short_description` — one-sentence summary, **strictly under 200 characters**. This limit is
     enforced by `verify_task_file.py` (`TF-W001`). Count the characters before writing `task.json`;
     if the sentence is longer, tighten it first — do not rely on the verificator to catch the
     overrun afterwards.
   * `slug` — lowercase underscore-separated identifier derived from the name (e.g.,
     `download_semcor_dataset`). Must use only lowercase letters, digits, and underscores.
   * `dependencies` — task IDs mentioned or implied as prerequisites. Validate each against the
     tasks aggregator output. Default to `[]` unless the description explicitly states the task
     needs output from another task. See the Dependency Guidance section below.
   * `expected_assets` — map of asset type to count based on what the task produces (e.g.,
     `{"dataset": 1}`, `{"paper": 5}`). Default to `{}` if no concrete assets.
   * `task_types` — match against the available task types from the aggregator output. Default to
     `[]` if no type fits.
   * `source_suggestion` — suggestion ID (`S-XXXX-NN` format) if mentioned. Validate against the
     suggestions aggregator output. Default to `null`.

3. **Compose `task_description.md` content.** Expand and structure the free-form input into a
   well-organized markdown document covering motivation, scope, approach, and expected outputs. Do
   not just copy the input verbatim — improve clarity and completeness.

4. **Determine task index.** If `$TASK_INDEX` is not provided, use the tasks aggregator output from
   step 1 to find the highest existing task index and add 1. Zero-pad to 4 digits.

5. **Construct the task ID.** Format: `t<NNNN>_<SLUG>` where `NNNN` is the zero-padded task index
   and `SLUG` is the derived slug.

6. **Create the task folder.**

   ```bash
   mkdir -p tasks/t<NNNN>_<SLUG>
   ```

7. **Write `task.json`.** Fields:

   * `spec_version`: `4`
   * `task_id`: the constructed task ID
   * `task_index`: the numeric index (integer)
   * `name`: derived name
   * `short_description`: derived short description
   * `long_description_file`: `"task_description.md"`
   * `status`: `"not_started"`
   * `dependencies`: derived dependencies
   * `start_time`: `null`
   * `end_time`: `null`
   * `expected_assets`: derived expected assets
   * `task_types`: derived task types
   * `source_suggestion`: derived source suggestion or `null`

8. **Write `task_description.md`.** Content is the description composed in step 3.

9. **Verify the task description against the Quality Checklist** (see section below). Every item
   must be addressed or explicitly marked N/A with a reason. Items marked with (\*) may be skipped
   for simpler tasks (download-dataset, literature-survey).

10. **Format the description file.**

    ```bash
    uv run flowmark --inplace --nobackup tasks/t<NNNN>_<SLUG>/task_description.md
    ```

11. **Run the task file verificator.**

    ```bash
    uv run python -u -m arf.scripts.verificators.verify_task_file t<NNNN>_<SLUG>
    ```

    Fix any errors before proceeding.

### Task Description Quality Checklist

Before finalizing any `task_description.md`, verify it against this checklist. Every item must be
addressed or explicitly marked N/A with a reason. Items marked with (\*) may be skipped for simpler
tasks (download-dataset, literature-survey).

**Scope and completeness**:

* `short_description` is under 200 characters (enforced by `verify_task_file.py` as `TF-W001`). Trim
  the description before writing `task.json`, not after the verificator flags it.
* Motivation stated: why this task matters for the project's research questions
* All runs/configurations listed explicitly (do not say "run on all models" — name each model)
* (\*) All registered metrics computed for every run (not just one run). Check available metrics
  with `uv run python -u -m arf.scripts.aggregators.aggregate_metrics --format json`
* (\*) Efficiency metrics included when the task involves training or inference:
  `efficiency_training_time_seconds`, `efficiency_inference_time_per_item_seconds`,
  `efficiency_inference_cost_per_item_usd`
* (\*) Assets specified (model assets, predictions assets, datasets) and matching `expected_assets`
  in `task.json`

**Data handling**:

* (\*) Intermediate data (subsets, splits, generated corpora) saved to `data/` folder within the
  task
* (\*) If creating data subsets: nesting requirements specified (e.g., "1% is a strict subset of
  5%") and sampling strategy with a fixed seed
* If reusing data from a prior task: comparability stated (same data, same splits)

**Training protocol** (when applicable):

* Exact hyperparameters specified or reference to prior task's hyperparameters
* Epoch strategy: "run all N epochs, select best checkpoint by metric X" — do NOT default to early
  stopping unless specifically justified. Running all epochs and selecting the best checkpoint gives
  both the overfitting dynamics data AND the best model.
* Per-epoch metrics to log specified (training loss, dev metric, etc.)

**Compute and budget**:

* GPU type recommendations with rationale: use fast GPUs (H100/A100) for bottleneck runs, cheap GPUs
  for fast runs — optimize wall-clock time of the overall task
* Realistic budget estimate with per-run breakdown, not just a total
* If parallel execution: number of machines, which runs go on which GPU tier

**Output specification**:

* (\*) All charts listed with axis labels and what question each chart answers
* (\*) All tables listed with row/column structure
* All charts saved to `results/images/` and embedded in `results_detailed.md`
* Key questions numbered, concrete, and falsifiable

**Cross-references**:

* Source suggestion ID referenced if applicable
* Prior tasks whose results motivate or constrain this task referenced
* Dependencies listed and justified (or explicitly "no dependencies" with reason)

### Dependency Guidance

Minimize dependencies. Only add a dependency when the task genuinely cannot start without the other
task's output (e.g., it needs a dataset or library that task produces). Most research,
literature-survey, and downloading tasks are independent and should have `"dependencies": []`. NEVER
add a dependency on a not-yet-completed task unless the task truly requires that task's concrete
output — blocking on incomplete work prevents parallel execution. When unsure, default to no
dependency.

## Output Format

Two files in the new task folder:

* `task.json` — task metadata with status `"not_started"` and `long_description_file` set
* `task_description.md` — detailed task description derived from the free-form input

## Done When

* Task folder exists at `tasks/t<NNNN>_<SLUG>/`
* `task.json` is valid and passes `verify_task_file.py` with 0 errors
* `task_description.md` exists and is referenced by `task.json`
* Task description has been verified against the Quality Checklist
* No subdirectories or extra files exist in the task folder

## Forbidden

* NEVER create subdirectories (`corrections/`, `logs/`, `results/`, `assets/`, etc.) in the task
  folder — the `/execute-task` skill creates the full folder structure
* NEVER create `.gitkeep` files
* NEVER set status to anything other than `"not_started"`
* NEVER modify any existing task folder
* NEVER skip the verificator step
