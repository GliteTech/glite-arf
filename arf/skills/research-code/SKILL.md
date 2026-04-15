---
name: "research-code"
description: "Review libraries and prior tasks to write implementation-oriented code research."
model: "claude-sonnet-4-6"
---
# Research Code

**Version**: 3

## Goal

Review all libraries and completed tasks relevant to the current task, analyze code quality, answer
assets, and reusability, and produce a structured `research_code.md` that informs planning and
implementation.

## Inputs

* `$TASK_ID` — the task folder name (e.g., `t0016_baseline_wsd_with_bert`)

## Context

Read before starting:

* `arf/docs/howto/use_aggregators.md` — JSON output structure for all aggregators

* `project/description.md` — project goals and scope

* `tasks/$TASK_ID/task.json` — task objective, dependencies, expected assets

* `arf/specifications/research_code_specification.md` — authoritative format specification for
  `research_code.md`

* `arf/styleguide/markdown_styleguide.md` — formatting rules (100-char lines, `*` bullets, heading
  hierarchy)

## Steps

### Phase 1: Understand the Task

1. Read `tasks/$TASK_ID/task.json` and extract the task objective, description, and dependencies. If
   it contains `long_description_file`, also read the referenced markdown file.

2. Note what kind of code, data, or infrastructure this task needs — this guides relevance
   assessment of prior tasks and libraries.

### Phase 2: Discover Libraries

1. Run the library aggregator to get all libraries:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_libraries \
     --format json --detail short
   ```

2. For each library, assess whether it is relevant to the current task based on its name,
   description, categories, and entry points.

3. For relevant libraries, get full details including the complete description:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_libraries \
     --format json --detail full --include-full-description \
     --ids <lib_id_1> <lib_id_2> ...
   ```

4. Note whether the aggregator output already reflects corrections. Library replacements are
   resolved automatically, and other aggregated asset kinds may also expose effective corrected
   metadata or file paths.

5. For relevant libraries, read their source code to understand the API:

   * Read the module files listed in `module_paths`
   * Note function signatures, classes, and data structures
   * Check test files for usage examples

### Phase 2b: Discover Existing Answers

1. Run the answer aggregator to get all answer assets:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_answers \
     --format json --detail short
   ```

2. For each answer, assess whether the question or conclusion is relevant to the current task.

3. For relevant answers, get full details including the complete researched answer:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_answers \
     --format json --detail full --include-full-answer \
     --ids <answer_id_1> <answer_id_2> ...
   ```

4. Treat relevant answer assets as synthesized prior findings. Use them to shortcut repeated
   research, but still confirm any reusable code or assets they reference. If an answer asset was
   corrected, trust the aggregator's effective state rather than the original upstream files.

### Phase 3: Discover and Assess Prior Tasks

1. Run the task aggregator for completed tasks:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_tasks \
     --format json --detail short --status completed
   ```

2. For each completed task, assess potential relevance based on name, description, and expected
   assets.

3. Tasks that are direct dependencies of the current task (from `task.json`) are automatically
   relevant — include them regardless of name matching.

4. For relevant-sounding tasks, get full details:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_tasks \
     --format json --detail full --ids <task_id_1> <task_id_2> ...
   ```

### Phase 4: Deep Dive into Relevant Tasks

For each relevant task, read its key outputs:

1. Code directory — list files with `ls tasks/<task_id>/code/`. For tasks that produced code, read
   key source files. Note:

   * File names, sizes, and purposes
   * Function signatures and class definitions
   * Data structures and constants
   * Patterns that could be reused (path management, data loading, evaluation)

2. Results — read `tasks/<task_id>/results/results_summary.md` to understand what the task achieved.
   Note metrics, success/failure, and any issues encountered.

3. Plan — read `tasks/<task_id>/plan/plan.md` to understand the approach. Note what worked as
   planned and what required adjustments.

4. Prior code research — if `tasks/<task_id>/research/research_code.md` exists, read it to
   understand what that task found about earlier tasks.

5. Datasets — check `tasks/<task_id>/assets/dataset/` for relevant data produced by the task. Note
   dataset IDs, sizes, and formats.

6. Answers — check `tasks/<task_id>/assets/answer/` for prior conclusions that may already address
   part of the current task. Note answer IDs, questions, confidence, and supporting source types.

### Phase 5: Analyze Reusability

1. Determine what code should be imported via library — only libraries registered in
   `assets/library/` may be imported across tasks. Note the import paths (e.g.,
   `from tasks.tXXXX_slug.code.module import func`).

2. Determine what code should be copied from other tasks into the current task's `code/` directory.
   For each piece of code to copy:

   * Note the exact source file path
   * Describe what to adapt (task-specific paths, constants, imports)
   * Estimate the size (line count)

3. Check for common patterns across tasks — shared approaches to path management, data loading,
   evaluation, logging.

### Phase 6: Synthesize and Write research_code.md

1. Organize findings by topic, not by task. Each topic becomes a `### ` subsection under
   `## Key Findings`. This is critical — by-topic organization forces synthesis across tasks.

2. Write the full `research_code.md` at `tasks/$TASK_ID/research/research_code.md` following
   `arf/specifications/research_code_specification.md`:

   * YAML frontmatter with all required fields (`spec_version`, `task_id`, `research_stage`,
     `tasks_reviewed`, `tasks_cited`, `libraries_found`, `libraries_relevant`, `date_completed`,
     `status`)

   * All 7 mandatory sections: Task Objective, Library Landscape, Key Findings, Reusable Code and
     Assets, Lessons Learned, Recommendations for This Task, Task Index

   * Additional sections wherever the task demands deeper treatment (e.g., Dataset Landscape, Common
     Patterns, Architecture Overview)

3. Ensure every `[tXXXX]` citation has a Task Index entry and vice versa.

4. In the Reusable Code and Assets section, explicitly label each item as "import via library" or
   "copy into task".

5. Include specific details everywhere — file paths, function signatures, line counts, performance
   numbers.

### Phase 7: Verify

1. Run the verificator:

   ```bash
   uv run python -u -m arf.scripts.verificators.verify_research_code $TASK_ID
   ```

2. Fix all errors. Address warnings unless there is a documented reason to skip them.

3. Re-run until zero errors.

## Done When

* `tasks/$TASK_ID/research/research_code.md` exists and follows the specification
* Verificator passes with zero errors
* Every `[tXXXX]` citation has a Task Index entry and vice versa
* Library Landscape documents all discovered libraries with relevance assessment
* Key Findings are organized by topic with `### ` subsections (not by task)
* Reusable Code section includes specific file paths and function signatures
* Each reusable item is labeled as "import via library" or "copy into task"
* At least 1 task is cited (or `status` is `"partial"` with explanation)

## Forbidden

* NEVER run `prestep` or `poststep` — the orchestrator handles the step lifecycle

* NEVER commit — the orchestrator handles all commits

* NEVER modify `step_tracker.json` — the orchestrator manages step state

* NEVER write `step_log.md` — the orchestrator writes it after this skill completes

* NEVER organize Key Findings by task — synthesize across tasks by topic.

* NEVER claim "no relevant prior tasks" without running both the library and task aggregators.

* NEVER recommend importing from another task's `code/` directory. Only library imports are allowed
  cross-task. Non-library code must be copied into the current task's `code/`.

* NEVER skip examining actual source code files for relevant tasks. Read the code, do not guess what
  it contains.

* NEVER fabricate file paths, function signatures, line counts, or code snippets. Read the actual
  files.

* NEVER skip the library aggregator — even if no libraries seem relevant, document what exists in
  the Library Landscape section.

* NEVER use vague descriptions like "there is useful code in t0012" — include specific file paths,
  function names, and what they do.
