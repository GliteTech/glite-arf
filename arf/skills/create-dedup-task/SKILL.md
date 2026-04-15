---
name: "create-dedup-task"
description: "Create a deduplication checkpoint task that scans for duplicate papers and overlapping work. Use when the project needs a new dedup checkpoint."
---
# Create Deduplication Task

**Version**: 3

## Goal

Create a deduplication checkpoint task that will scan for duplicate papers and similar suggestions
across completed tasks, then resolve them using the corrections mechanism.

## Inputs

* `$NEXT_TASK_ID` — the next available task ID (e.g., `0014`)

## Context

Read before starting:

* `arf/specifications/corrections_specification.md` — correction format for all aggregated artifact
  kinds; dedup tasks typically use `paper` and `suggestion` targets
* `arf/skills/create-task/SKILL.md` — generic task creation steps

## Steps

1. Determine the checkpoint number. Run the tasks aggregator to list all tasks:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_tasks \
     --format json --detail short
   ```

   Count tasks whose ID contains `dedup_checkpoint` and add 1.

2. Compose the dedup-specific long description. It must specify what the task does during execution:

   * Scan all `tasks/*/assets/paper/` directories for papers with the same `paper_id` appearing in
     multiple tasks (exact duplicates)
   * Run cross-paper similarity checks for near-duplicates (different paper_id but same DOI or
     highly similar title)
   * Compare all uncovered active suggestions across tasks for title/description similarity
   * For each duplicate paper set: determine the canonical copy (earliest `date_added`, then lowest
     task ID) and create a paper correction to delete the others
   * For each similar suggestion pair: determine which to keep and create a suggestion correction to
     reject the other
   * Run `verify_corrections.py` on all created corrections
   * Run aggregators to confirm corrections are applied

   The description must also specify which standard task steps to skip:

   * Skip: `research-papers`, `research-internet`, `suggestions` (not needed for cleanup tasks)
   * Include: `create-branch`, `check-deps`, `init-folders`, `planning`, `execution`, `results`,
     `reporting`

3. Follow the `/create-task` skill instructions (`arf/skills/create-task/SKILL.md`) to create the
   task folder. Pass the description composed in step 2 as `$TASK_DESCRIPTION` and `$NEXT_TASK_ID`
   as `$TASK_INDEX`. The `/create-task` skill derives all structured fields from the description.

## Output Format

Two files in the new task folder:

* `task.json`
* `task_description.md`

The task itself is executed later via `/execute-task`.

## Done When

* Task folder exists with a valid `task.json`
* `task_description.md` describes the full scanning and correction procedure
* The task metadata passes `verify_task_file.py`

## Forbidden

* NEVER scan for duplicates in this skill — that is the task's execution work
* NEVER create correction files — that is done when the task is executed
* NEVER modify any existing task folder
* NEVER list specific duplicate paper_ids or suggestion IDs in the description — the task discovers
  these during execution
