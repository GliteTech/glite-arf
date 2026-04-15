# How to Run Tasks in Parallel

## Goal

Run multiple ARF tasks concurrently in isolated git worktrees.

## Prerequisites

* Each task already exists under `tasks/` with `task.json` and a unique ID
* The tasks have no ordering dependency on each other
* Clean working tree on the base branch (usually `main`)
* Read
  [`arf/specifications/task_git_specification.md`](../../specifications/task_git_specification.md)

## Steps

1. Open a separate Claude Code (or Codex) session per task. Never run two
   [`/execute-task`](../../skills/execute-task/SKILL.md) invocations in the same session.

2. Run each task end-to-end. The skill creates the worktree, branch, and folder structure
   automatically:

   ```text
   /execute-task <task_id>   # Claude Code
   $execute-task <task_id>   # Codex
   ```

3. Each skill instance merges its PR and tears down its worktree when done. Merges happen
   sequentially — parallel merges invite conflicts.

4. If two parallel tasks added overlapping paper assets or suggestions, schedule a deduplication
   task with [`/create-dedup-task`](../../skills/create-dedup-task/SKILL.md).

## Verification

* `git worktree list` shows one worktree per active task on its `task/<task_id>` branch
* Each worktree's `git status` is clean between steps
* After merging, `aggregate_tasks` lists both tasks as `completed`
* Verificators from the base branch report no cross-task file modifications

## Pitfalls

* Editing shared files (`pyproject.toml`, `uv.lock`, `ruff.toml`, `.gitignore`) in two parallel
  branches — coordinate dependency changes
* Adding paper assets with the same DOI from two parallel tasks — needs a dedup task
* Running `/execute-task` twice in the same worktree — `step_tracker.json` becomes inconsistent
* Merging PRs in parallel — do them one at a time
* Removing a worktree before its PR merges — uncommitted work is lost
* Each worktree has its own environment cache — run `uv sync` if dependencies changed on the base

## See Also

* `../../specifications/task_git_specification.md`
* `../../scripts/utils/worktree.py`
* `apply_a_correction.md`
