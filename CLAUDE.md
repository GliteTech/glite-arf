# Glite ARF Template

Template repository for starting a research project using the Glite Autonomous Research Framework
(Glite ARF). Fork this repo and replace this section with your project-specific description.

## Commands

```bash
# Setup
# New fork onboarding: run /setup-project in Claude Code or $setup-project in Codex
uv sync                                            # Install deps
uv run pre-commit install                          # Activate git hooks
python3 doctor.py                                  # Validate environment

# Development
uv run python -u <script.py>                        # Run a script
uv run python arf/scripts/utils/run_with_logs.py <cmd>    # ARF logging (tasks)

# Quality
uv run flowmark --inplace --nobackup <path.md>      # Format markdown
uv run ruff check --fix . && uv run ruff format .   # Lint and format Python
uv run mypy .                                        # Type check
uv run pytest                                        # Run framework tests in arf/tests
```

## Key References

* Project description and goals: create `project/description.md` in your fork
* New project onboarding: @arf/skills/setup-project/SKILL.md
* ARF architecture and glossary: @arf/README.md
* Python style guide: @arf/styleguide/python_styleguide.md
* Markdown style guide: @arf/styleguide/markdown_styleguide.md
* Agent instructions style guide: @arf/styleguide/agent_instructions_styleguide.md
* Paper asset specification: @meta/asset_types/paper/specification.md
* Aggregators reference: @arf/docs/reference/aggregators.md

## Key Rules

0. Framework / infrastructure / specification / skill / verificator / aggregator / materializer
   changes in `arf/`, generic `meta/`, and generic boilerplate are not task work. Do not create a
   `tasks/tXXXX_*` folder for such changes.
1. All CLI tool calls MUST be wrapped in `arf/scripts/utils/run_with_logs.py`
2. One task = one folder = one branch = one PR
3. **NEVER** modify files outside the task folder. Only top-level tooling files may change:
   `pyproject.toml`, `uv.lock`, `ruff.toml`, `.gitignore`
4. Each task stage and each action is a separate well-described commit
5. Nothing in a completed task folder may be changed; use the corrections mechanism in later tasks
6. Run `uv run flowmark --inplace --nobackup <changed.md>` on edited markdown files, then run
   `uv run ruff check --fix . && uv run ruff format . && uv run mypy .` before commit
7. Framework tests live in `arf/tests/`. Task-specific tests live in
   `tasks/$TASK_ID/code/test_*.py`. Do not create or use a top-level `tests/` directory.
8. Full data normalization; no duplication across task folders
9. **Always use aggregators to enumerate cross-task data.** Never walk `tasks/` with
   Glob/Grep/find/Explore to list tasks, papers, suggestions, answers, datasets, libraries, models,
   predictions, costs, metrics, or metric results. Aggregators in `arf/scripts/aggregators/` apply
   the corrections overlay; raw filesystem walks silently miss corrections and produce stale
   answers. See `arf/docs/reference/aggregators.md` for the full list and flags.

## Task Workflow

* Tasks live in `tasks/tXXXX_slug/` (t prefix + 4-digit ID + underscore slug)
* Each task runs in its own git worktree on branch `task/<task_id>`
* Multiple tasks can execute in parallel (each in a separate worktree)
* New tasks branch: `new_tasks/<first_index>-<last_index>`
* Mandatory stages: research -> planning -> implementation -> analysis -> reporting
* Every step must be logged in `logs/`; verificators enforce this
* Aggregators collect data across tasks AND apply corrections overlays — use them instead of walking
  `tasks/` directly (see rule 9)
* Format specs for task documents: `arf/specifications/`
