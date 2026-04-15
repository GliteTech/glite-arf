# How to Run a Task from the Pool

## Goal

Pick one `not_started` task and run it through every mandatory stage to a merged PR using
[`execute-task`](../../skills/execute-task/SKILL.md).

## Prerequisites

* At least one task with `status: not_started` in `tasks/`
* `doctor.py` passes
* The project's budget has headroom for whatever the task's plan will estimate

## Steps

1. List tasks ready to run. Either open
   [`overview/tasks/by-status/not_started.md`](../../../overview/tasks/by-status/not_started.md) or
   query the aggregator:

   ```bash
   uv run python -m arf.scripts.aggregators.aggregate_tasks \
       --status not_started --format markdown
   ```

2. Pick the task with the highest priority dependency-ready. Copy its task ID.

3. Invoke the skill from Claude Code (`/execute-task <task_id>`) or Codex
   (`$execute-task <task_id>`):

   ```text
   /execute-task t0042_my_task
   ```

4. The skill creates the worktree, runs every mandatory stage, commits each step, opens a PR, merges
   it, and refreshes the overview dashboard. Walk away or monitor
   [`step_tracker.json`](../../specifications/step_tracker_specification.md) from another terminal:

   ```bash
   watch -n 5 cat tasks/t0042_my_task/step_tracker.json
   ```

## Verification

* `task.json` status is `completed`
* The PR is merged into `main`
* The task's entry in [`overview/tasks/by-status/`](../../../overview/tasks/by-status/) shows
  `completed` (the skill refreshes the dashboard automatically after merge)

## Pitfalls

* **Task has unmet dependencies.** `execute-task` fails in the `check-deps` step. Either run the
  dependencies first or update `task.json` to remove stale ones.
* **Budget exceeded.** The planning stage refuses to write a plan that would push the project past
  the stop threshold in `project/budget.json`. Reduce the plan's scope or raise the budget
  explicitly.
* **Intervention required.** The task may pause with a file in `intervention/` — a dataset needs
  access approval, a credential is missing. Resolve, commit, then re-invoke `/execute-task` to
  continue.
* **Running two execute-task invocations in the same worktree.** Don't. Each task gets its own
  worktree; see [Run tasks in parallel](run_tasks_in_parallel.md).

## See Also

* [Execute-task skill](../../skills/execute-task/SKILL.md)
* [Task lifecycle](../explanation/task_lifecycle.md)
* [Run tasks in parallel](run_tasks_in_parallel.md)
* [Remote machines](../explanation/remote_machines.md) — for GPU tasks
