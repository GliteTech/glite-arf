---
name: "implementation"
description: "Execute `plan/plan.md`, produce assets, and verify results."
---
# Implementation

**Version**: 8

## Goal

Execute the task plan: carry out all actions specified in `plan/plan.md`, create all expected
assets, write code where required, run verificators, and return control to the orchestrator.

## Inputs

* `$TASK_ID` — the task folder name (e.g., `t0003_download_semcor_dataset`)

## Context

Read before starting:

* `arf/docs/howto/use_aggregators.md` — JSON output structure for all aggregators

* `project/description.md` — project goals and scope

* `tasks/$TASK_ID/task.json` — task objective, dependencies, expected assets

* `tasks/$TASK_ID/plan/plan.md` — the plan to execute (Step by Step section)

* `tasks/$TASK_ID/research/research_papers.md` — findings from existing papers

* `tasks/$TASK_ID/research/research_internet.md` — findings from internet research

* Asset type specifications in `meta/asset_types/` for each expected asset type

* `meta/task_types/<task_type>/instruction.md` — task-type-specific instructions (read for each type
  listed in `task.json` `task_types` or recommended in `plan/plan.md`)

* `arf/styleguide/python_styleguide.md` — if the plan involves writing code

## Critical Rules

1. Never commit. The orchestrator owns the step lifecycle — prestep, commit, step log, and poststep
   are handled by the orchestrator, not by this skill.

2. Never run prestep or poststep.

3. Never modify files outside the task folder (except `pyproject.toml`, `uv.lock`, `ruff.toml`, the
   root `.gitignore`, `mypy.ini`). Never create `.gitignore` files inside task folders.

4. Every CLI command must be wrapped with `run_with_logs.py`:

   ```bash
   uv run python -m arf.scripts.utils.run_with_logs --task-id $TASK_ID -- <command>
   ```

5. Read the relevant specification before creating any file. Do not guess the format — read the
   spec, then write the file, then run the verificator.

6. Run the asset verificator for every asset produced. Fix all errors before proceeding.

7. When producing multiple assets of the same type (e.g., 6 datasets), spawn one subagent per asset
   — do not create assets inline. Each subagent receives the asset type specification path, the
   specific asset details, and instructions to create the asset and run its verificator.

8. Never import from another task's `code/` directory (e.g.,
   `from tasks.t0012_other_task.code.module import func`). The only cross-task import mechanism is
   libraries registered in `assets/library/`. Non-library code from other tasks must be copied into
   the current task's `code/` directory and adapted as needed.

## Steps

### Phase 1: Understand the Plan and Research

1. Read `tasks/$TASK_ID/plan/plan.md`.

2. Read `tasks/$TASK_ID/task.json` again and compare it against the plan.

   * If `task.json` contains `long_description_file`, read that markdown file and treat it as the
     long description for all coverage checks.

   * Find the `## Task Requirement Checklist` section in `plan/plan.md`.

   * Confirm every concrete requirement from the task text has a `REQ-*` entry.

   * If the plan checklist is missing, incomplete, or contradicts `task.json`, do not silently
     proceed. Record the gap in your final report back to the orchestrator and treat the missing
     coverage as a task-quality issue.

3. Load task type instructions. Read `task.json` for the `task_types` field. Also check
   `plan/plan.md` Approach section for recommended task types.

   * Collect the union of types from both sources.
   * For each type, read `meta/task_types/<slug>/instruction.md`.
   * Follow the Implementation Guidelines and Common Pitfalls sections throughout execution.
   * Use the Verification Additions section during Phase 3 (Final Verification).
   * If no task types are specified in either source, skip this step.

4. Identify from the "Step by Step" section:

   * What actions to take and in what order
   * What assets to create (and their types)
   * Whether remote machines are involved (provisioned in `setup-machines`)
   * What code to write (if any)
   * Which `REQ-*` items each step claims to satisfy

5. Build a working completion checklist for every `REQ-*` item. Track status as `done`, `partial`,
   or `blocked` while you execute the plan.

6. Read research outputs to inform implementation decisions:

   * `tasks/$TASK_ID/research/research_papers.md` — key findings, methodology insights, and
     recommendations from existing papers

   * `tasks/$TASK_ID/research/research_internet.md` — additional findings from internet research,
     including tools, libraries, and recent developments

7. Scan all existing answer assets in question-only short form:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_answers \
     --format json --detail short
   ```

   * Review each answer's question, title, categories, methods, confidence, and source task ID.
   * Use this pass to identify existing conclusions that may affect execution choices, verification
     expectations, or evidence already established by prior tasks.

8. For relevant answers, fetch full details including the full researched answer:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_answers \
     --format json --detail full --include-full-answer \
     --ids <answer_id_1> <answer_id_2> ...
   ```

   Treat relevant answers as reusable synthesized knowledge, but still verify any code, datasets,
   libraries, or external claims they reference before reusing them.

9. Read asset type specifications for each expected asset type listed in `task.json` →
   `expected_assets`.

### Phase 1.5: Preflight Inspection

Before running any expensive operation (API calls, remote compute, large-scale data processing),
perform mandatory input/output verification on individual examples. Aggregate metrics hide semantic
bugs. Individual inspection catches them.

This phase applies every time the plan includes a step that costs money, takes more than a few
minutes, or processes more than 100 items. Repeat the inspection for each distinct expensive step
(e.g., once for inference, once for training).

When hardcoding or embedding metric values from prior tasks, ALWAYS read the actual source file
(`results/metrics.json`, `results/results_detailed.md`, or the relevant asset file) and verify each
value matches. Never write comparison constants from memory or plan text. Add a source comment:
`# Source: tasks/<task_id>/results/metrics.json`

1. **Print and read 3 individual inputs.** Before making any API call or running any model, print
   the exact input that will be sent for 3 randomly chosen instances. Read each one carefully:

   * For LLM tasks: print the full prompt (system + user message). Verify every element is correct —
     the right input data, the right candidate options, the right context, the right format.
   * For data processing: print 3 input records. Verify fields, types, and values look correct.
   * For training: print 3 training examples. Verify labels match inputs.

   If anything looks wrong in even one example, fix the code before proceeding.

2. **Run on 5-10 instances and read individual outputs.** Use `--limit 10` (or equivalent) to
   produce a small sample. Then read 5 individual outputs — not the aggregate summary:

   * For each output: is the model's response reasonable given the input it received?
   * For each output: does the scoring/evaluation logic produce the correct result for this specific
     case?
   * For each output: if the result is marked wrong, is it genuinely wrong, or is the evaluation
     buggy?

   Do NOT skip this step even if the aggregate metric looks reasonable. A 70% accuracy on 10
   instances can hide a systematic bug that affects 30% of all instances.

3. **Compare against the known trivial baseline.** Every experiment has a trivial baseline (majority
   class for classification, random for retrieval, frequency heuristic for tagging). The plan should
   specify this baseline in its validation gates.

   * If the small-run result is **at or below the trivial baseline**, STOP. The pipeline has a bug.
     Do not proceed to the full run. Do not interpret this as a scientific finding. Debug individual
     predictions until you find the cause.
   * A model with access to context that performs at or below a context-free heuristic is broken,
     not bad.
   * Create an intervention file if you cannot resolve the issue.

4. **Verify evaluation correctness on known-answer instances.** Pick 3-5 instances where you can
   determine the correct answer independently (e.g., unambiguous items, trivially classifiable
   examples). Verify the pipeline scores all of them correct. If any known-correct instance is
   scored wrong, the evaluation logic has a bug.

### Phase 2: Execute Plan Steps

Follow `plan/plan.md` "Step by Step" section sequentially.

For each action:

* Wrap ALL commands with `run_with_logs.py`

* Keep the `REQ-*` checklist current. When a step completes, update which requirements now have
  concrete evidence.

* If a step is marked `[CRITICAL]` and becomes blocked (download fails, service unavailable,
  permissions denied), do not substitute a different approach. Create an intervention file at
  `tasks/$TASK_ID/intervention/critical_step_blocked.md` explaining what failed, what was tried, and
  what human action is needed. Then STOP and return control to the orchestrator. Silently pivoting
  to a fundamentally different approach (e.g., using cached predictions instead of running
  inference) changes what the task accomplishes and must not happen without explicit approval.

* If the action creates an asset:

  1. Read the asset type specification FIRST
  2. Create the asset following the spec exactly
  3. Run the asset verificator
  4. Fix all errors before proceeding

* If the action creates correction files:

  1. Read `arf/specifications/corrections_specification.md` first

  2. Write correction files only in the current task's `corrections/` folder

  3. NEVER modify completed upstream task folders

  4. If a correction changes the effective file inventory of an asset, keep the structured metadata
     aligned as well (for example `files`, `module_paths`, or `test_paths`)

  5. Run `verify_corrections.py` before proceeding

Asset verificator invocation examples:

```bash
uv run python -m arf.scripts.verificators.verify_dataset_asset \
  --task-id $TASK_ID <dataset_id>

uv run python -m arf.scripts.verificators.verify_paper_asset \
  --task-id $TASK_ID <paper_id>

uv run python -m arf.scripts.verificators.verify_library_asset \
  --task-id $TASK_ID <library_id>

uv run python -m arf.scripts.verificators.verify_answer_asset \
  --task-id $TASK_ID <answer_id>

uv run python -m arf.scripts.verificators.verify_model_asset \
  --task-id $TASK_ID <model_id>

uv run python -m arf.scripts.verificators.verify_predictions_asset \
  --task-id $TASK_ID <predictions_id>
```

Missing paper addition: If the plan identifies missing papers (from the planning phase paper gap
check), spawn `/add-paper` subagents for each missing paper. Run a maximum of 3 concurrent
`/add-paper` subagents.

Remote execution: When running on a remote machine provisioned in `setup-machines`, use `tmux` for
long-running jobs so they survive SSH disconnection. See the "Execution on Remote Machines" section
in `arf/skills/setup-remote-machine/SKILL.md` for the tmux pattern, monitoring commands, and
reconnection procedures.

When the plan involves more than 3 remote machines, spawn a subagent per machine. Each subagent:
uploads data, runs its experiment, downloads results, and destroys the machine. For 3 or fewer
machines, handle them directly. After all machine subagents return, do post-processing locally
(metrics, charts, assets).

### Phase 3: Final Verification

Run all relevant asset verificators one final time. Confirm all expected assets from `task.json` →
`expected_assets` have been created and pass verification.

**Metrics format**: Before writing `results/metrics.json`, read
`arf/specifications/metrics_specification.md` for the exact required structure. Two formats exist:
legacy flat (single metric set) and explicit variant (array of variant objects with `variant_id`,
`label`, `dimensions`, `metrics`). Use the explicit variant format when the task compares multiple
conditions.

**Costs format**: Before writing `results/costs.json`, read
`arf/specifications/task_results_specification.md` § "## costs.json" for the exact structure. The
`breakdown` field must be a JSON object (not an array), mapping cost category strings to USD amounts
or rich objects with `cost_usd`.

**Metrics consistency check**: Read `results/metrics.json` and confirm every value traces to actual
script output. Flag any `0.0` values for metrics that should have real measurements — investigate
before returning to the orchestrator.

Before the requirement review, check metrics coverage. Run:

```bash
uv run python -u -m arf.scripts.aggregators.aggregate_metrics --format ids
```

Compare the registered metric IDs against what is in `results/metrics.json`. For each registered
metric not present, ask: "Did this task perform the activity this metric measures?" Specifically:

* If the task trained a model, `efficiency_training_time_seconds` should be present.
* If the task ran inference (not backfilled from a prior task),
  `efficiency_inference_time_per_item_seconds` and `efficiency_inference_cost_per_item_usd` should
  be present.
* If the task evaluated on standard benchmarks, the corresponding `f1_*` and `accuracy_*` metrics
  should be present.

If an applicable metric is missing and the data to compute it exists (e.g., training time is in logs
but not in metrics.json), add it now. If the metric cannot be measured (e.g., inference was
backfilled, not freshly run), note this in the completion checklist so the omission is deliberate.

Then perform a requirement-by-requirement completion review:

* Re-read `task.json` and `plan/plan.md` `## Task Requirement Checklist`

* Confirm every `REQ-*` item is `done`, `partial`, or `blocked`

* Collect concrete evidence for each item: file paths, tables, asset IDs, commands, metric values,
  or explanation of what remains missing

* If any requirement is `partial` or `blocked`, say so explicitly in your final report to the
  orchestrator. Do not imply the task is complete.

* End your response with a section titled `Requirement Completion Checklist` and list every `REQ-*`
  item with:

  * status (`done`, `partial`, or `blocked`)
  * one-sentence result
  * evidence paths or outputs

* * *

## Writing Code

When the plan requires Python scripts (data processing, extraction, analysis, evaluation), follow
these rules strictly.

### File Location

All Python files and scripts must live in `tasks/$TASK_ID/code/`. Never place `.py` files in the
task root or any other subdirectory. The `code/` folder is created during `init-folders`.

```text
tasks/<task_id>/code/
├── paths.py             # All Path constants for this task
├── constants.py         # Column names, magic strings, enums
├── extract.py           # Example: data extraction script
└── analyze.py           # Example: analysis script
```

### Before Writing Code

1. Read `arf/styleguide/python_styleguide.md` — the full style guide.
2. Check if the task needs new dependencies. If so, add them to `pyproject.toml` and run `uv sync`.

### Style Requirements

Follow the Python style guide. The most critical rules:

* Python 3.12+ syntax: `list[int]` not `List[int]`, `X | None` not `Optional[X]`, `type Word = str`
  not `TypeAlias`

* Line length: 100 characters maximum

* Absolute imports only: `from tasks.XXXX_slug.code.paths import X`, never relative imports

* Keyword arguments: required for functions with 2+ heterogeneous parameters

* Dataclasses: `@dataclass(frozen=True, slots=True)` for all structured data; never return tuples

* Path constants: centralize all file paths in `code/paths.py` using `pathlib.Path`

* Named constants: no hardcoded strings — use typed constants in `code/constants.py`

* Explicit type annotations: on all function signatures, variable declarations for collections, and
  anywhere mypy needs help

* Explicit checks: `if x is None:` not `if not x:`, `if len(lst) == 0:` not `if not lst:`

* Pydantic at boundaries: `BaseModel` for JSON file I/O, `@dataclass` for internal data

* `pathlib.Path` always, never `os.path`

* `argparse` for CLI arguments, `tqdm` for progress bars

### Quality Checks

Before committing, check output file sizes. Files larger than 3 MB must be gzip-compressed or must
match an existing LFS pattern in `.gitattributes`. See
`arf/specifications/task_git_specification.md` Large Files section.

Run markdown formatting on any edited `.md` files, then run the Python quality checks before
returning control to the orchestrator:

```bash
uv run flowmark --inplace --nobackup path/to/file.md
uv run ruff check --fix . && uv run ruff format . && uv run mypy .
```

The project uses strict mypy (`strict = true` in `pyproject.toml`) and ruff with pycodestyle,
pyflakes, pyupgrade, flake8-bugbear, flake8-simplify, isort, and no-relative-imports rules. Fix all
errors — do not use `# type: ignore` or `# noqa` without a documented reason.

### Running Scripts

All script executions must be wrapped with `run_with_logs.py`:

```bash
uv run python -m arf.scripts.utils.run_with_logs --task-id $TASK_ID -- \
  uv run python -u tasks/$TASK_ID/code/extract.py
```

Use `-u` (unbuffered) with Python to ensure real-time output in logs.

* * *

## Creating Library Assets

When a task produces a library (Python code for reuse by downstream tasks):

1. Code location: All Python files go in `tasks/$TASK_ID/code/` as usual.

2. Tests: Create test files at `tasks/$TASK_ID/code/test_*.py`. Run tests with
   `uv run pytest tasks/$TASK_ID/code/test_*.py -v`. Generic framework tests for `arf/` code belong
   in `arf/tests/`, not in a repo-top-level `tests/` directory.

3. Asset folder: Create `tasks/$TASK_ID/assets/library/<library_id>/` with only `details.json` and
   the canonical description document — no `files/` directory. The code stays in `code/`, referenced
   via `module_paths` in `details.json`. In current spec versions, `details.json` must also declare
   `description_path`. Use the canonical document path from metadata; do not assume consumers will
   look for `description.md`.

4. Read the specification first: `meta/asset_types/library/specification.md`

5. Run the verificator before returning:

   ```bash
   uv run python -m arf.scripts.verificators.verify_library_asset \
     --task-id $TASK_ID <library_id>
   ```

6. Library ID format: lowercase letters, digits, underscores. Must start with a letter. Example:
   `wsd_data_loader`, `wsd_scorer`.

* * *

## Creating Answer Assets

When a task produces one or more answer assets:

1. One asset per question: Create one folder per question at
   `tasks/$TASK_ID/assets/answer/<answer_id>/`.

2. Required files: Each folder must contain `details.json`, the canonical short answer document, and
   the canonical full answer document. In current spec versions, `details.json` must also declare
   `short_answer_path` and `full_answer_path`.

3. Read the specification first: `meta/asset_types/answer/specification.md`

4. Source traceability: Record every supporting paper ID, URL, and task ID in `details.json`, then
   reflect the same evidence in the answer documents.

5. Code experiments: If the answer depends on a new experiment, keep the scripts in
   `tasks/$TASK_ID/code/` and describe the experiment explicitly in the canonical full answer
   document.

6. Run the verificator before returning:

   ```bash
   uv run python -m arf.scripts.verificators.verify_answer_asset \
     --task-id $TASK_ID <answer_id>
   ```

* * *

## Creating Model Assets

When a task trains or fine-tunes a model:

1. Asset folder: Create `tasks/$TASK_ID/assets/model/<model_id>/` with `details.json`, the canonical
   description document, and a `files/` directory containing the model checkpoint, config, and
   tokenizer files. In current spec versions, `details.json` must also declare `description_path`.

2. Read the specification first: `meta/asset_types/model/specification.md`

3. Model ID format: lowercase alphanumeric, hyphens, dots. Example: `bert-base-wsd-v1`,
   `deberta-large-semcor-1.0`.

4. Key metadata: Record `framework`, `base_model`, `architecture`, `training_dataset_ids`, and
   `hyperparameters` in `details.json`.

5. After copying model files to the asset's `files/` directory, remove intermediate copies (e.g.,
   from `results/` or working directories) to avoid committing duplicates and wasting disk space
   during LFS staging.

6. Run the verificator before returning:

   ```bash
   uv run python -m arf.scripts.verificators.verify_model_asset \
     --task-id $TASK_ID <model_id>
   ```

* * *

## Creating Predictions Assets

When a task runs inference and produces per-instance predictions:

1. Asset folder: Create `tasks/$TASK_ID/assets/predictions/<predictions_id>/` with `details.json`,
   the canonical description document, and a `files/` directory containing prediction output files
   (JSONL, CSV, etc.). In current spec versions, `details.json` must also declare
   `description_path`.

2. Read the specification first: `meta/asset_types/predictions/specification.md`

3. Predictions ID format: lowercase alphanumeric, hyphens, dots. Example:
   `bert-base-wsd-on-raganato-all`, `gpt4o-zero-shot-semeval-2015`.

4. Key metadata: Record `model_id` (or null for API-based models), `model_description`,
   `dataset_ids`, `prediction_format`, and `prediction_schema` in `details.json`.

5. Include per-instance data: Each prediction file must contain instance IDs, gold labels, predicted
   labels, and confidence scores where available.

6. Run the verificator before returning:

   ```bash
   uv run python -m arf.scripts.verificators.verify_predictions_asset \
     --task-id $TASK_ID <predictions_id>
   ```

* * *

## LLM Task Examples

When writing the `## Examples` section for LLM-based tasks, include actual prompt text and raw model
responses in fenced code blocks. Do not reduce examples to prediction tables — show what the model
saw and what it said.

## Done When

* All steps in `plan/plan.md` "Step by Step" section are completed

* Every concrete requirement from `task.json` has a `REQ-*` status in the final
  `Requirement Completion Checklist`

* All expected assets from `task.json` → `expected_assets` exist and pass their verificators with
  zero errors

* All code passes `ruff check`, `ruff format`, and `mypy` (if applicable)

## Forbidden

* NEVER commit — the orchestrator handles all commits

* NEVER run `prestep.py` or `poststep.py`

* NEVER modify files outside the task folder (except dependency files)

* NEVER skip asset verificators

* NEVER use `# type: ignore` or `# noqa` without documented reason

* NEVER import from another task's `code/` directory — only library imports are allowed cross-task;
  copy non-library code into this task's `code/`

* NEVER silently skip or substitute a `[CRITICAL]` step — create an intervention file and stop

* NEVER declare implementation complete without an explicit requirement-by-requirement completion
  checklist

* NEVER write `results/results_summary.md`, `results/results_detailed.md`, `results/costs.json`,
  `results/remote_machines_used.json`, `results/suggestions.json`, or
  `results/compare_literature.md` — these are produced by later orchestrator steps (results,
  suggestions, compare-literature), not by the implementation skill. Implementation produces:
  `code/`, `assets/`, `corrections/`, `results/metrics.json`, and `results/images/`
