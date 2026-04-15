# How to Create a Task Manually

## Goal

Create a single new `not_started` task folder outside a brainstorming session, using
[`create-task`](../../skills/create-task/SKILL.md). Use this when you know exactly what needs to
happen and do not need a full strategic review.

## Prerequisites

* The task's `task_type` exists in [`meta/task_types/`](../../../meta/task_types/) (check the
  defaults or [add a task type](add_a_task_type.md) first)
* Any dependencies the new task needs are already completed, or will be before it runs

## Steps

1. Invoke the skill:

   ```text
   /create-task
   ```

   (Codex: `$create-task`.)

2. Describe the task in free-form text. Include what the task does, why it exists, the task type,
   any dependencies, and expected assets. The skill derives all structured fields (name, slug,
   dependencies, expected assets, task types) from your description automatically.

3. The skill picks the next task index, creates `tasks/t<NNNN>_<slug>/`, writes
   [`task.json`](../../specifications/task_file_specification.md) and `task_description.md`, and
   runs [`verify_task_file`](../../scripts/verificators/verify_task_file.py).

## Verification

```bash
uv run python -m arf.scripts.aggregators.aggregate_tasks --status not_started --format ids
```

The new task ID appears in the output. The task is ready to run with
[`/execute-task`](run_a_task.md).

## Pitfalls

* **Skipping the brainstorm session for strategic tasks.** Manual creation is for when you already
  know the task is the right call. For tasks that would benefit from strategic review
  (reprioritization, deduplication against existing work, priority comparison),
  [brainstorm](brainstorm_next_tasks.md) instead.
* **Unknown task_type.** The skill refuses. Add the task type first via
  [add a task type](add_a_task_type.md).
* **Editing task.json by hand afterwards.** Don't. Re-run the skill or use a correction.

## See Also

* [Create-task skill](../../skills/create-task/SKILL.md)
* [Brainstorm next tasks](brainstorm_next_tasks.md) — when you want strategic review
* [Run a task from the pool](run_a_task.md)
