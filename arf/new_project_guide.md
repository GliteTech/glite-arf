# How to Start a New ARF Research Project

This guide describes what to do after forking the ARF template repository. The fork already contains
the directory structure, infrastructure files, specifications, and framework scripts.

## Step 1: Fork and Clone

Fork the template repository on GitHub, rename it for your research topic, then clone locally.

```bash
git clone <your-fork-url>
cd <project-name>
```

## Step 2: Set Up the Environment

Run `/setup-project` in Claude Code, or `$setup-project` in Codex. This is the canonical onboarding
path for every new fork. The skill:

* Shows the safety acknowledgement and stops unless you accept it exactly
* Detects or installs `uv`, runs `uv sync`, installs pre-commit hooks, allows `direnv`, initializes
  Git LFS, and runs `doctor.py`
* Runs `/create-project-description` inline to create `project/description.md` and
  `project/budget.json`
* Provisions only the paid services declared in `project/budget.json`
* Runs `/add-category`, `/add-metric`, `/add-task-type`, and `/add-asset-type` to populate `meta/`
* Replaces the template `README.md` with a project-specific README
* Runs `/human-brainstorm` to plan the first tasks

Do not run the lower-level setup skills first. They are still available for later repairs and
incremental changes, but `/setup-project` owns the initial project creation flow.

## Step 3: Review Project Identity

After `/setup-project` finishes, review what it wrote:

* `project/description.md`
* `project/budget.json`
* `README.md`
* `meta/categories/`, `meta/metrics/`, `meta/task_types/`, and any extra `meta/asset_types/`

If the project needs domain dependencies, update `pyproject.toml` and `uv.lock` intentionally. If
the root `CLAUDE.md` needs project-specific context beyond `project/description.md`, add it at the
top without changing the framework rules.

## Step 4: Verify Setup

Run the same checks `/setup-project` uses if you need to confirm the final state:

```bash
python3 doctor.py
uv run python -u -m arf.scripts.verificators.verify_project_description
uv run python -u -m arf.scripts.verificators.verify_project_budget
uv run python -m arf.scripts.aggregators.aggregate_categories --format ids
uv run python -m arf.scripts.aggregators.aggregate_metrics --format ids
uv run python -m arf.scripts.aggregators.aggregate_task_types --format ids
```

## Step 5: Execute the First Task

`/setup-project` ends by running `/human-brainstorm`, so a new project should already have at least
one planned task or an explicit decision to defer task creation. List queued tasks:

```bash
uv run python -m arf.scripts.aggregators.aggregate_tasks --status not_started --format ids
```

Then run one:

```text
/execute-task <task_id>   # Claude Code
$execute-task <task_id>   # Codex
```

## Checklist

Before starting research tasks, verify:

* [ ] Git LFS is installed (`git lfs install`)
* [ ] `doctor.py` passes all checks
* [ ] `/setup-project` completed or exited with a clear blocker
* [ ] `project/description.md` and `project/budget.json` exist and pass verification
* [ ] `README.md` is project-specific, not the template README
* [ ] `meta/` entries were reviewed after `/setup-project` populated them
* [ ] Paid services in `project/budget.json` match the credentials you actually configured
* [ ] First tasks were planned by `/human-brainstorm`, or task creation was explicitly deferred
