# Task Git Specification

**Version**: 3

* * *

## Purpose

This specification defines the branching strategy, commit conventions, and pull request workflow for
task execution. Every task follows the same git lifecycle: branch, commit per step, PR, merge.

**Producer**: Task agents (create branches, commits, and PRs).

**Consumers**:

* **Task agents** — follow this workflow during execution
* **Verificator scripts** — validate branch names, commit history, and PR state
* **Human reviewers** — audit task history via PR diffs
* **CI/CD** — run checks before merge

* * *

## Branch Naming

```text
task/<task_id>
```

One branch per task. The branch name must exactly match the pattern `task/` followed by the
`task_id` from `task.json`.

Examples:

* `task/t0001_initial_literature_survey`
* `task/t0003_download_training_corpus`
* `task/t0042_bert_baseline_wsd`

* * *

## Worktree Layout

Each task executes in its own **git worktree** — an independent working directory with its own
branch. This allows multiple tasks to run in parallel without interfering with each other. The main
repository checkout always stays on `main`.

### Location

```text
../<repo-name>-worktrees/<task_id>/
```

The worktree base directory is a sibling of the main repository, auto-derived from the repo name.
For example, if the repo lives at `/home/user/research-wsd`, worktrees are created under
`/home/user/research-wsd-worktrees/`.

### Properties

* Each worktree is a full working copy on branch `task/<task_id>`
* Worktrees share the git object store with the main repo (minimal disk overhead — only working tree
  files are duplicated)
* The `arf/` scripts, `meta/`, and `project/` directories exist in each worktree, so all scripts
  resolve paths correctly
* `uv sync` runs automatically during worktree creation to set up the Python environment

### Management

Use `uv run python -m arf.scripts.utils.worktree` for all worktree operations:

```bash
uv run python -m arf.scripts.utils.worktree create <task_id>
uv run python -m arf.scripts.utils.worktree remove <task_id> [--force]
uv run python -m arf.scripts.utils.worktree list
uv run python -m arf.scripts.utils.worktree path <task_id>
```

### Parallel Execution

Multiple tasks can run concurrently in separate worktrees. Be aware of these coordination points:

* **step_tracker.json**: Created on the task branch (inside the worktree), not on `main`. This
  avoids polluting other tasks' worktrees with unrelated step trackers.
* **Dependency changes**: If two parallel tasks both add entries to `pyproject.toml` or `uv.lock`,
  their PRs may have merge conflicts. Resolve these during the merge step.
* **Aggregator visibility**: A worktree branches from `main` at creation time. It does not see
  changes merged to `main` after the worktree was created. This is correct for task isolation but
  means aggregators in a long-running worktree may miss recently completed tasks.

* * *

## Branch Lifecycle

### 1. Create Worktree and Branch

Before starting any task work, create the task worktree from `main`. The worktree helper creates
both the branch and the working directory:

```bash
# From the main repo (on main branch)
uv run python -m arf.scripts.utils.worktree create <task_id>
cd <printed_worktree_path>
```

All subsequent work happens inside the worktree directory.

The `worktree create` command automatically sets `task.json` `status` to `"in_progress"` and
`start_time` to the current UTC timestamp on `main`, then commits and pushes the change to
`origin/main` before creating the branch. The task branch inherits the updated status. This makes
in-progress tasks visible on `main` through the dashboard and aggregators.

If the push fails (e.g., offline or remote has diverged), a warning is printed but worktree creation
continues. The aggregator provides a safety net: it checks for active worktrees and overrides
`not_started` to `in_progress` for any task with an active worktree. To manually fix status
inconsistencies, use `sync-status`:

```bash
uv run python -m arf.scripts.utils.worktree sync-status --dry-run  # report only
uv run python -m arf.scripts.utils.worktree sync-status            # fix and push
```

### 2. Work and Commit

All task work happens inside the worktree. Each step produces at least one commit. See Commit
Strategy below.

### 3. Create Pull Request

When all steps are complete and all verificators pass, the agent creates a PR targeting `main`:

```bash
gh pr create --title "<task_id>: <task name>" --body "..."
```

### 4. Merge and Clean Up

After the PR is created and CI checks pass, the agent merges the PR using a **merge commit** (not
squash) to preserve per-step history, then removes the worktree:

```bash
gh pr merge <pr_number> --merge
# Return to main repo and clean up
cd <main_repo_root>
uv run python -m arf.scripts.utils.worktree remove <task_id>
git pull
```

Branches are kept after merge for audit trail purposes.

* * *

## Commit Strategy

### One Commit Per Step

Each step in `step_tracker.json` must produce at least one commit. Steps that involve multiple
distinct actions (e.g., downloading 10 papers) may produce multiple commits, but each commit must be
self-contained and well-described.

### Commit at Stage Boundaries

At minimum, commit at these points:

* After task folder initialization (task.json, step_tracker.json)
* After each research stage completes
* After planning completes
* After each execution step completes
* After results and reporting are written
* After all verificators pass (final commit)

### Commit Message Format

```text
<task_id> [<step_id>]: <short description>

<optional body with details>
```

* First line: under 72 characters, starts with task ID and step ID
* Step IDs come from `arf/specifications/task_steps_specification.md`
* Body: separated by a blank line, wraps at 100 characters
* Use imperative mood ("Add research papers" not "Added research papers")

### Do:

```text
t0003_download_training_corpus [implementation]: Download and verify training corpus

Downloaded annotated training corpus from the official repository.
Verified file integrity via SHA-256 checksum. Corpus contains 352
documents with 226,000 labeled instances across 15 categories.
```

```text
t0003_download_training_corpus [results]: Write dataset description and metrics
```

```text
t0003_download_training_corpus [reporting]: Final verification pass
```

### Don't:

```text
update files
```

```text
WIP
```

```text
fix
```

* * *

## Pull Request Format

### Title

```text
<task_id>: <task name>
```

Must be under 72 characters. Use the `name` field from `task.json`.

### Body

The PR body must contain:

* **Summary** — 2-3 bullet points describing what the task accomplished
* **Assets produced** — list of assets created (papers, datasets, libraries, answers, etc.)
* **Verification** — confirmation that all verificators passed with zero errors

### Example

```markdown
## Summary

* Downloaded annotated training corpus (226,000 labeled instances)
* Documented dataset structure, statistics, and label distribution
* Registered as dataset asset with full metadata

## Assets Produced

* `assets/dataset/training-corpus-v3/` — dataset asset with details.json
  and description.md

## Verification

All verificators pass with 0 errors:
* verify_task_file.py — PASSED
* verify_task_dependencies.py — PASSED
* verify_logs.py — PASSED
```

* * *

## File Isolation Rules

A task branch must **only** modify files within its own task folder. The only exceptions are:

* `pyproject.toml` — adding dependencies
* `uv.lock` — updated by dependency changes
* `ruff.toml` — linter configuration
* `.gitignore` — ignore patterns
* `mypy.ini` — type checker configuration

These restrictions apply to task branches such as `task/<task_id>`. Repository maintenance work that
intentionally updates shared files in `arf/`, `.claude/`, or `.codex/` must use a separate non-task
branch and worktree.

### Forbidden

* Modifying any other task's folder
* Modifying files in `arf/` (specifications, scripts, skills)
* Modifying files in `meta/` (categories, asset types)
* Modifying `.claude/` (settings, rules, skills)

A verificator should check that no files outside the allowed set are modified on the task branch
compared to `main`.

* * *

## Verification Rules

### Errors

| Code | Description |
| --- | --- |
| `TG-E001` | Branch name does not match `task/<task_id>` pattern |
| `TG-E002` | Task branch modifies files outside the allowed set |
| `TG-E003` | No commits found on the task branch |
| `TG-E004` | A completed step in `step_tracker.json` has no associated commit |
| `TG-E005` | PR does not target `main` |

### Warnings

| Code | Description |
| --- | --- |
| `TG-W001` | Commit message does not include task ID and step ID |
| `TG-W002` | Commit message first line exceeds 72 characters |
| `TG-W003` | PR title does not match expected format |
| `TG-W004` | PR body is missing a required section |

* * *

## Large Files and Git LFS

The repository uses a pre-commit hook (`check-added-large-files`) that rejects any file larger than
5 MB. Large files must be tracked via Git LFS patterns in `.gitattributes`.

### Rules

1. Before committing, check if any output file exceeds 3 MB. If so, gzip-compress it (e.g.,
   `predictions.jsonl` → `predictions.jsonl.gz`) or ensure it matches an existing LFS pattern.
2. The `.gitattributes` file already tracks common large-file patterns: `*.pdf`, `*.jsonl.gz`,
   `*.tar.gz`, `*.ckpt.part_*`. Check the current `.gitattributes` before adding new patterns.
3. When adding a new LFS pattern, use task-scoped paths when possible (e.g.,
   `tasks/t0070_*/results/*.cbm`) rather than broad globs.
4. Session transcripts (`logs/sessions/*.jsonl`) are automatically compressed during capture if they
   exceed 4 MB.
