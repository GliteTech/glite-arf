# Utilities Reference

Helper scripts for task execution. They live in `arf/scripts/utils/`.

## All Utilities

| Script | Purpose |
| --- | --- |
| [`prestep.py`](../../scripts/utils/prestep.py) | Pre-step validation: check preconditions, mark step `in_progress`, create log folder |
| [`poststep.py`](../../scripts/utils/poststep.py) | Post-step verification: validate outputs, mark step `completed`, auto-commit `step_tracker.json` |
| [`run_with_logs.py`](../../scripts/utils/run_with_logs.py) | Wrap CLI commands; capture stdout/stderr; write JSON metadata to `logs/commands/` |
| [`init_task_folders.py`](../../scripts/utils/init_task_folders.py) | Create mandatory task folder structure from `task.json` |
| [`worktree.py`](../../scripts/utils/worktree.py) | Create and manage git worktrees for task isolation |
| [`doi_to_slug.py`](../../scripts/utils/doi_to_slug.py) | Convert a DOI to a deterministic folder-name slug |
| [`find_similar_papers.py`](../../scripts/utils/find_similar_papers.py) | Find similar papers across the corpus for deduplication |
| [`capture_task_sessions.py`](../../scripts/utils/capture_task_sessions.py) | Capture CLI session transcripts for a task |
| [`skip_step.py`](../../scripts/utils/skip_step.py) | Mark steps as skipped and create their step logs |

## CLI Usage

### prestep

```bash
uv run python -m arf.scripts.utils.prestep <task_id> <step_id>
```

### poststep

```bash
uv run python -m arf.scripts.utils.poststep <task_id> <step_id>
```

### run_with_logs

```bash
uv run python -m arf.scripts.utils.run_with_logs --task-id <task_id> -- <command...>
```

All CLI tool calls inside a task branch must be wrapped with `run_with_logs`.

### init_task_folders

```bash
uv run python -m arf.scripts.utils.init_task_folders <task_id>
```

### worktree

```bash
uv run python -m arf.scripts.utils.worktree create <task_id>
uv run python -m arf.scripts.utils.worktree remove <task_id>
```

### doi_to_slug

```bash
uv run python -m arf.scripts.utils.doi_to_slug "<doi>"
```

### find_similar_papers

```bash
uv run python -m arf.scripts.utils.find_similar_papers --title "Paper Title" \
    [--authors "Author One" "Author Two"] [--doi "10.1234/example"] [--year 2025] \
    [--threshold 0.7]
```

### capture_task_sessions

```bash
uv run python -m arf.scripts.utils.capture_task_sessions --task-id <task_id>
```

### skip_step

```bash
uv run python -m arf.scripts.utils.skip_step <task_id> <step_id> "<reason>" \
    [<step_id> "<reason>" ...]
```
