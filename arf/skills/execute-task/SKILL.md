---
name: "execute-task"
description: "Run an ARF task through all required stages and merge the final PR."
---
# Execute Task

**Version**: 20

## Goal

Execute a complete task through all mandatory stages and finish with a merged PR and refreshed
`overview/` on `main`.

## Inputs

* `$TASK_ID` — the task folder name (e.g., `t0003_download_semcor_dataset`)

## Context

Read before starting:

* `project/description.md` — project goals, scope, and research questions

* `project/budget.json` — project budget and per-task spending limits

* `arf/specifications/project_budget_specification.md` — `project/budget.json` schema and threshold
  rules

* `tasks/$TASK_ID/task.json` — task objective, dependencies, expected assets

* `arf/specifications/task_steps_specification.md` — canonical step IDs and phase order

* `arf/specifications/task_git_specification.md` — branching, commit, and PR conventions

* `arf/specifications/task_file_specification.md` — `task.json` format

* `arf/specifications/logs_specification.md` — log directory structure

* `arf/specifications/research_papers_specification.md` — `research_papers.md` format

* `arf/specifications/research_internet_specification.md` — `research_internet.md` format

* `arf/specifications/research_code_specification.md` — `research_code.md` format

* `arf/specifications/plan_specification.md` — `plan.md` format

* `arf/specifications/compare_literature_specification.md` — `compare_literature.md` format (for
  tasks that include the compare-literature step)

* `arf/docs/howto/use_aggregators.md` — JSON output structure for all aggregators

* Task type definitions via aggregator — determines which optional steps apply:

  ```bash
  uv run python -u -m arf.scripts.aggregators.aggregate_task_types --format json
  ```

  Returns `{"task_types": [{"task_type_id", "name", "optional_steps", "instruction", ...}]}`. Access
  task types via `data["task_types"]`.

* Current project spend and budget left — run after the worktree is created:

  ```bash
  uv run python -u -m arf.scripts.aggregators.aggregate_costs --format json --detail full
  ```

  Returns `{"budget": {...}, "summary": {...}, "tasks": [...], "skipped_tasks": [...]}`. Key fields
  in `summary`: `total_cost_usd`, `budget_left_usd`, `spent_percent`, `stop_threshold_reached`,
  `warn_threshold_reached`.

* Asset type specifications in `meta/asset_types/` for the expected assets

## Critical Rules

1. Never modify files outside the task folder (except `pyproject.toml`, `uv.lock`, `ruff.toml`, the
   root `.gitignore`, `.gitattributes`, `mypy.ini`). Never create `.gitignore` files inside task
   folders. Infrastructure fixes found during task execution must be deferred to a separate PR on
   `main`.

2. Step numbers are sequential (1, 2, 3, ...) with no gaps, regardless of which canonical steps are
   skipped.

3. Every step follows the prestep/do/poststep cycle — no exceptions.

4. Every CLI command on a task branch must be wrapped with `run_with_logs.py`.

5. Read the relevant specification before creating any file. Do not guess the format — read the
   spec, then write the file, then run the verificator.

6. Run the asset verificator before committing any asset (paper, dataset, etc.).

7. Commit after each step with format: `<task_id> [<step_id>]: <description>`.

8. The orchestrator owns the step lifecycle. Step skills (e.g., `/research-papers`,
   `/implementation`, `/generate-suggestions`) only produce output and run their verificator.
   Prestep, commit, step log, and poststep are always handled here — never inside the step skill.

9. Every skill invocation must run in a spawned subagent. When a step uses a skill (e.g.,
   `/research-papers`, `/research-internet`, `/implementation`, `/add-paper`,
   `/generate-suggestions`), always spawn a dedicated Agent. Never execute skill logic inline in the
   orchestrator. When producing multiple assets of the same type, spawn one subagent per asset. This
   protects the orchestrator's context and enforces isolation.

10. Never override or restrict a skill's instructions when spawning its subagent. Pass the task ID
    and any required context, but do not add constraints like "do NOT add papers" or "skip Phase 3".
    The skill's `SKILL.md` defines what it does — the orchestrator must not second-guess or
    abbreviate it.

11. Post-merge overview sync happens only on `main` in the main repo. Rebuild, commit, and push
    `overview/` only after the task PR is merged, the worktree is removed, and `main` is updated.
    Never do this from the task branch or task worktree, and do not use `run_with_logs.py` for these
    main-repo commands.

12. NEVER gitignore, exclude, or skip committing files that the task requires as deliverables. If
    output files seem too large for git, ask the user before excluding them.

13. If a subagent fails due to a transient error (API connection failure, timeout, socket error),
    retry once before falling back to inline execution by the orchestrator. Log the failure and
    retry in the step log.

14. NEVER rewrite history on a `task/*` branch. `git lfs migrate import`, `git filter-repo`, and any
    `git push --force` / `--force-with-lease` on a task branch rewrite commits that are already
    shared with the PR. GitHub sees the force-push as the branch disappearing and auto-closes the
    PR, and the audit trail for every earlier step is corrupted. To recover from an oversized file
    caught by `verify_pr_premerge` (PM-E011, 5 MB threshold), compress the file in place and create
    a normal follow-up commit — see Phase 7 Step 3.

## Writing Code

See `arf/skills/implementation/SKILL.md` for all code writing rules (file location, style
requirements, quality checks, running scripts). The `/implementation` subagent handles code creation
during the implementation step.

Cross-task import rule: tasks must not import from other tasks' `code/` directories. The only
cross-task import mechanism is libraries (registered in `assets/library/`). Non-library code must be
copied into the current task's `code/` directory.

### Planning Phase: Code Design

When the plan calls for writing code, the `plan/plan.md` Step by Step section must specify:

* Which scripts will be created (file names in `code/`)
* What each script does (inputs, outputs, algorithm)
* Which existing project libraries or utilities to reuse
* Any new dependencies needed in `pyproject.toml`

## Step Lifecycle

Every step follows this exact sequence:

```text
1. uv run python -m arf.scripts.utils.prestep  $TASK_ID <step_id>
2. Do the step work
3. CRITICAL: Run `uv run flowmark --inplace --nobackup` on ALL `.md` files created or modified in
   this step — including `step_log.md` and any other files the orchestrator writes directly, not
   just subagent output. Run `uv run ruff check --fix . && uv run ruff format .` on any `.py`
   files. The pre-commit hook rejects commits with unformatted `.md` files.
4. Commit the step work (include step_tracker.json — see note below)
5. uv run python -m arf.scripts.utils.poststep $TASK_ID <step_id>
   (auto-commits `step_tracker.json`)
```

Never skip prestep or poststep.

**Type-checking task code**: Always invoke mypy as `uv run mypy -p tasks.$TASK_ID.code`, not
`uv run mypy tasks/$TASK_ID/code`. Task folders are Python packages (`tNNNN_slug`), and path-based
mypy invocation triggers duplicate-module-name errors across task folders unless
`--explicit-package-bases` is also set. The `-p` form uses the absolute package path and works in
every task unchanged.

**`step_tracker.json` staging rule**: `prestep` modifies `step_tracker.json` (sets the step status
to `in_progress`). Stage `step_tracker.json` along with your step work files in step 4 so that
`poststep` finds a clean working tree. `poststep` then modifies `step_tracker.json` again (marks the
step `completed`) and auto-commits that change. Do not make a separate manual commit for
`step_tracker.json` — just include it in your normal step work commit.

### Step Log Template

Every `step_log.md` must use this format (from `arf/specifications/logs_specification.md`):

```yaml
---
spec_version: "3"
task_id: "$TASK_ID"
step_number: <N>
step_name: "<step-id>"
status: "completed"
started_at: "<ISO8601 UTC>"
completed_at: "<ISO8601 UTC>"
---
```

Mandatory sections: `## Summary` (min 20 words), `## Actions Taken` (numbered list, min 2 items),
`## Outputs` (bullet list of files), `## Issues` (problems or "No issues encountered.").

**Skipped steps**: Use the `skip_step.py` utility to mark steps as skipped in batch. It creates the
step log directory, writes a minimal `step_log.md` with correct frontmatter and mandatory sections,
and updates `step_tracker.json`:

```bash
uv run python -m arf.scripts.utils.skip_step $TASK_ID \
  research-papers "No relevant papers in corpus for this task." \
  research-code "No prior task code relevant to this work."
```

Do NOT run prestep or poststep for skipped steps. Commit all skipped step logs **before** running
prestep for the next active step — prestep requires a clean working tree.

## Steps

### Phase 0: Preparation (before any steps)

Phase 0 critical rule: use only the Read tool to read files. Do not run any CLI commands (`uv run`,
`python`, aggregator scripts) before the worktree is created. Commands wrapped with
`run_with_logs.py` that run before the worktree write logs to the main repo directory, where they
are never committed. All CLI commands must wait until after `create-branch` (Phase 1).

1. Read `tasks/$TASK_ID/task.json` using the Read tool — understand the objective, dependencies,
   expected assets, and `task_types`. If it contains `long_description_file`, also read the
   referenced markdown file from the task root before deciding the step plan.

2. Read `arf/specifications/task_steps_specification.md` using the Read tool — understand the
   canonical steps and which are required vs optional.

3. Read asset type specifications in `meta/asset_types/` using the Read tool for each expected asset
   type listed in `task.json`.

4. Note the dependency list and `task_types` from `task.json` — these will be verified via CLI
   commands after the worktree is created.

### Phase 1: Preflight

#### Step: `create-branch`

```bash
uv run python -m arf.scripts.utils.worktree create $TASK_ID
```

The `create` command prints the worktree path to stdout. **Change your working directory to the
worktree path immediately.** All subsequent steps, commands, and file operations must happen inside
the worktree:

```bash
cd <printed_worktree_path>
```

Now run prestep (which auto-creates a minimal `step_tracker.json`):

```bash
uv run python -m arf.scripts.utils.prestep $TASK_ID create-branch
```

#### Step planning (inside worktree, before writing `step_tracker.json`)

Now that all commands run inside the worktree, verify dependencies and determine the step list:

1. For each dependency in `task.json`, run the task aggregator to verify it is completed and
   understand what it produced:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_tasks \
     --format json --detail short --ids <dep_id_1> <dep_id_2> ...
   ```

   Returns `{"task_count": N, "tasks": [{...}, ...]}`. Each task object has: `task_id`, `name`,
   `short_description`, `status`, `task_types`, `dependencies`. Only fetch dependency tasks, not the
   full project task list.

2. Check current project spend and budget left, but only if this task's task types can incur paid
   external costs. Load the task type definitions via `aggregate_task_types.py` and inspect the
   `has_external_costs` field on each entry listed in `task.json` `task_types`:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_task_types --format json
   ```

   * If at least one listed task type has `has_external_costs: true`, or if `task_types` is empty
     and the task fallback inference (see step 3) classifies this as an experiment-style task, run
     the cost aggregator:

     ```bash
     uv run python -u -m arf.scripts.aggregators.aggregate_costs --format json --detail full
     ```

     Returns `{"budget": {...}, "summary": {...}, "tasks": [...], "skipped_tasks": [...]}`.

     If `data["summary"]["stop_threshold_reached"]` is `true` or
     `data["summary"]["budget_left_before_stop_usd"] <= 0`, create
     `tasks/$TASK_ID/intervention/project_budget_exhausted.md` and STOP. Record the remaining budget
     for the planning and setup-machines prompts.

   * If every listed task type has `has_external_costs: false`, skip the cost aggregator and the
     budget gate entirely. Mechanical, analytical, and retrieval task types (download-paper,
     deduplication, brainstorming, data-analysis, correction, write-library, etc.) cannot move the
     project spend total and must not be blocked on it. Record a single log line in the step log
     noting that the budget gate was skipped because no listed task type has external costs.

   The budget gate applies per task, not per project. A project with `total_budget: 0.0` must still
   be able to run cost-free task types without producing an intervention file.

3. Determine which steps this task needs. Always include all 7 required steps. For the 8 optional
   steps, use task type definitions to decide inclusion:

   Always required (include in every task):

   * `create-branch`, `check-deps`, `init-folders` — preflight
   * `implementation` — implementation
   * `results`, `suggestions`, `reporting` — analysis and reporting

   Optional (inclusion depends on task type):

   * `research-papers`, `research-internet`, `research-code` — research
   * `planning` — planning
   * `setup-machines`, `teardown` — remote compute
   * `creative-thinking`, `compare-literature` — analysis

   Task-type-based step selection:

   If `task_types` in `task.json` is non-empty:

   * Load the task type definitions via the aggregator:

     ```bash
     uv run python -u -m arf.scripts.aggregators.aggregate_task_types --format json
     ```

     Returns `{"task_types": [...]}`. Each entry has `task_type_id`, `optional_steps`,
     `instruction`. Note: this aggregator does NOT support `--detail`.

   * For each type in `task_types`, read its `optional_steps` list.

   * Compute the union of all `optional_steps` across all matched types.

   * Include those optional steps. Skip optional steps not in the union.

   * Note: if `setup-machines` is included, `teardown` must also be included.

   * The agent may still apply judgment — `optional_steps` is guidance, not absolute. If a step
     seems clearly needed despite not being listed (or clearly unnecessary despite being listed),
     adjust with a brief note in the step description.

   * For `correction` tasks, always inspect the task text directly before finalizing the step list.
     The default `optional_steps` may be empty, but:

     * include `research-code` if the correction depends on understanding prior code, assets, or
       existing outputs

     * include `research-papers` or `research-internet` only if the correction requires external
       factual validation

     * include `planning` if the correction spans multiple artifacts, introduces replacement assets,
       or uses non-trivial `file_changes`

     * skip research and planning for straightforward corrections whose target and fix are already
       explicit in the task text

   If `task_types` is empty (unclassified task), fall back to these criteria:

   * `research-papers` — include if the task involves methods, techniques, or evaluations where
     existing papers in the corpus may inform the approach. Skip for mechanical tasks (downloading,
     infrastructure, deduplication).

   * `research-internet` — include if the task requires knowledge not already captured in the paper
     corpus or prior tasks (new tools, APIs, recent publications). Skip for tasks that operate
     entirely on local data or prior work.

   * `research-code` — include if prior tasks produced code, libraries, datasets, or other reusable
     assets that might inform this task. Skip for the first few tasks in a project or when the task
     is independent of prior work.

   * `planning` — include for tasks with non-trivial implementation requiring design decisions, cost
     estimation, or multi-step execution. Skip for simple mechanical tasks (downloading a single
     file, deduplication).

   * `setup-machines` — include if the plan requires remote compute (GPU training, large-scale
     inference, distributed processing). Skip for local-only tasks (downloads, data processing,
     analysis).

   * `teardown` — include if and only if `setup-machines` is included.

   * `creative-thinking` — include for experiment tasks where alternative approaches or
     out-of-the-box analysis could yield insights. Skip for mechanical tasks (downloading, data
     conversion, infrastructure).

   * `compare-literature` — include for experiment tasks that produce quantitative results
     comparable to published results. Skip for tasks that don't produce performance metrics.

4. Plan the step list:

   * Sequential step numbers (1, 2, 3, ...) with no gaps
   * Canonical step IDs as the `name` field
   * All steps set to `"pending"`
   * A `description` field tailored to this specific task

   The first three steps are always:

   1. `create-branch`
   2. `check-deps`
   3. `init-folders`

   Then the task-specific steps follow in canonical phase order (research, planning, execution,
   analysis, reporting). Number them sequentially starting from 4.

   For every canonical optional step NOT included in the task's step list, add it to
   `step_tracker.json` with status `"skipped"` and a brief description explaining why. All canonical
   optional steps must appear in `step_tracker.json` — either as `"pending"` / `"completed"` (if
   executed) or `"skipped"` (if not).

   Example for a `data-analysis` task (optional steps: research-papers, research-code, planning,
   creative-thinking):

   ```text
   1: create-branch
   2: check-deps
   3: init-folders
   4: research-papers
   5: research-code
   6: planning
   7: implementation
   8: creative-thinking
   9: results
   10: suggestions
   11: reporting
   ```

   Example for a `download-dataset` task (optional steps: planning):

   ```text
   1: create-branch
   2: check-deps
   3: init-folders
   4: planning
   5: implementation
   6: results
   7: suggestions
   8: reporting
   ```

   Example for an `answer-question` task (optional steps: research-papers, research-internet,
   research-code, planning, creative-thinking):

   ```text
   1: create-branch
   2: check-deps
   3: init-folders
   4: research-papers
   5: research-internet
   6: research-code
   7: planning
   8: implementation
   9: creative-thinking
   10: results
   11: suggestions
   12: reporting
   ```

Write the full `step_tracker.json` with all steps planned above (this overwrites the minimal tracker
created by prestep).

Write `logs/steps/001_create-branch/branch_info.txt`:

```text
branch: task/$TASK_ID
base_branch: main
base_commit: <commit_hash>
worktree_path: <worktree_path>
created_at: <ISO8601_UTC>
```

Commit and run poststep.

#### Step: `check-deps`

```bash
uv run python -m arf.scripts.utils.prestep $TASK_ID check-deps
```

Prestep runs `verify_task_dependencies.py` automatically. Write the output to
`logs/steps/002_check-deps/deps_report.json`:

```json
{
  "task_id": "<task_id>",
  "checked_at": "<ISO8601_UTC>",
  "result": "passed",
  "dependencies": [
    {"task_id": "<dep_id>", "status": "completed", "satisfied": true}
  ],
  "errors": 0,
  "warnings": 0
}
```

Commit and run poststep.

#### Step: `init-folders`

```bash
uv run python -m arf.scripts.utils.prestep $TASK_ID init-folders
```

Create the mandatory task folder structure using the init script:

```bash
uv run python -m arf.scripts.utils.run_with_logs --task-id $TASK_ID -- \
  uv run python -m arf.scripts.utils.init_task_folders $TASK_ID \
  --step-log-dir tasks/$TASK_ID/logs/steps/003_init-folders/
```

The script creates all required directories, reads `task.json` `expected_assets` for asset
subdirectories, and adds `.gitkeep` to every empty directory. The `--step-log-dir` flag causes the
script to automatically write `logs/steps/003_init-folders/folders_created.txt`. Stage both the
created directories (including `.gitkeep` files) AND the step log directory
(`logs/steps/003_init-folders/`), then commit and run poststep.

### Phase 2: Research

#### Step: `research-papers` (optional)

Include this step if the task type's `optional_steps` lists `research-papers` or if task-content
judgment says it is needed. Skip for task types that exclude it (e.g., `write-library`,
`download-dataset`, `infrastructure-setup`) unless the task text clearly requires literature
validation. For `correction` tasks, include this only when the correction itself depends on paper
evidence.

```bash
uv run python -m arf.scripts.utils.prestep $TASK_ID research-papers
```

Spawn a subagent to execute the `/research-papers` skill:

```text
Use the Agent tool to launch a subagent with this prompt:
"Execute the /research-papers skill for task $TASK_ID.
Read arf/skills/research-papers/SKILL.md and follow all steps."
```

The subagent will review existing papers and write `research/research_papers.md`. After the subagent
completes, verify the output exists and the verificator passes:

```bash
uv run python -m arf.scripts.utils.run_with_logs --task-id $TASK_ID -- \
  uv run python -m arf.scripts.verificators.verify_research_papers $TASK_ID
```

Write `logs/steps/NNN_research-papers/step_log.md`. Commit and run poststep. If skipped, the step
must still appear in `step_tracker.json` with status `"skipped"`.

#### Step: `research-internet` (optional)

Include this step if the task type's `optional_steps` lists `research-internet` or if task-content
judgment says it is needed. Skip for task types that exclude it (e.g., `download-dataset`,
`download-paper`, `deduplication`) unless the task text clearly requires new external information.
For `correction` tasks, include this only when the correction depends on current external facts,
documentation, or recent changes not already captured in the project.

```bash
uv run python -m arf.scripts.utils.prestep $TASK_ID research-internet
```

Spawn a subagent to execute the `/research-internet` skill:

```text
Use the Agent tool to launch a subagent with this prompt:
"Execute the /research-internet skill for task $TASK_ID.
Read arf/skills/research-internet/SKILL.md and follow all steps."
```

The subagent will search the internet and write `research/research_internet.md` with a
`## Discovered Papers` section listing all new papers found. After the subagent completes, verify
the output exists and the verificator passes:

```bash
uv run python -m arf.scripts.utils.run_with_logs --task-id $TASK_ID -- \
  uv run python -m arf.scripts.verificators.verify_research_internet $TASK_ID
```

Write `logs/steps/NNN_research-internet/step_log.md`. Commit and run poststep. If skipped, the step
must still appear in `step_tracker.json` with status `"skipped"`.

**Paper addition from Discovered Papers**: After the research-internet step completes successfully,
parse the `## Discovered Papers` section of `research/research_internet.md`. For each paper listed
that is not already in the corpus (check via `aggregate_papers.py` comparing DOIs and normalized
titles), spawn an `/add-paper` subagent. Spawn subagents for ALL discovered papers, max 3 running
concurrently. If more than 3 papers need adding, queue the remainder and spawn each as a slot frees.
Every discovered paper must be attempted. These paper-addition subagents run **in parallel with
subsequent steps** — do not wait for them to finish before proceeding to `research-code` or
`planning`. Only the `compare-literature` step (if included) and the final `reporting` step should
wait for all paper subagents to complete. Track paper-addition subagents in a local list and check
completion before those later steps. If any paper-addition subagent fails (API error, timeout,
etc.), log the failure and attempt the paper addition inline during the `reporting` step. Before
running poststep for any step, run `git status` to check for untracked files from parallel agents
(e.g., paper downloads in `assets/paper/`). If present, stage and commit them before running
poststep so the working tree is clean.

#### Step: `research-code` (optional)

Include this step if prior tasks produced code, libraries, datasets, answers, models, predictions,
or other reusable assets that might inform this task. This step is especially important for
`correction` tasks when the target artifact, replacement artifact, or partial file overlay must be
understood before the fix is applied. If skipped, the step must still appear in `step_tracker.json`
with status `"skipped"`.

```bash
uv run python -m arf.scripts.utils.prestep $TASK_ID research-code
```

Spawn a subagent to execute the `/research-code` skill:

```text
Use the Agent tool to launch a subagent with this prompt:
"Execute the /research-code skill for task $TASK_ID.
Read arf/skills/research-code/SKILL.md and follow all steps."
```

The subagent will review existing libraries, answer assets, and completed tasks, then write
`research/research_code.md`. After the subagent completes, verify the output exists and the
verificator passes:

```bash
uv run python -m arf.scripts.utils.run_with_logs --task-id $TASK_ID -- \
  uv run python -m arf.scripts.verificators.verify_research_code $TASK_ID
```

Write `logs/steps/NNN_research-code/step_log.md`. Commit and run poststep.

### Phase 3: Planning

#### Step: `planning` (optional)

Include this step if the task type's `optional_steps` lists `planning` or if task-content judgment
says planning is needed. Skip for task types that exclude it (e.g., `download-paper`,
`brainstorming`) unless the task text clearly calls for multi-step design work. For `correction`
tasks, include planning when the correction spans multiple targets, introduces replacement assets,
or needs careful verification of file overlays and aggregator behavior.

```bash
uv run python -m arf.scripts.utils.prestep $TASK_ID planning
```

Spawn a subagent to execute the `/planning` skill. Include any user-provided context about budget
authorization, speed preferences, special instructions, and the current budget summary from
`aggregate_costs.py` in the prompt:

```text
Use the Agent tool to launch a subagent with this prompt:
"Execute the /planning skill for task $TASK_ID.
Read arf/skills/planning/SKILL.md and follow all steps.
[Include any user context here, e.g.: The user authorized up to $40 for
faster compute. The user wants to prioritize speed over cost savings.]"
```

The subagent will synthesize all research outputs, scan existing answer assets via the answer
aggregator, and write `plan/plan.md` with all 11 mandatory sections. The plan's `## Step by Step`
must cover only implementation work — ending at "compute metrics and produce charts." Results
writing, suggestions, and compare-literature are orchestrator steps managed by execute-task — do not
include them in the plan.

After the subagent completes, verify the output exists and the verificator passes:

```bash
uv run python -m arf.scripts.utils.run_with_logs --task-id $TASK_ID -- \
  uv run python -m arf.scripts.verificators.verify_plan $TASK_ID
```

Write `logs/steps/NNN_planning/step_log.md`. Commit and run poststep. If skipped, the step must
still appear in `step_tracker.json` with status `"skipped"`.

### Phase 4: Execution

#### Step: `setup-machines` (optional)

Include this step ONLY when the plan requires remote compute (GPU training, large-scale inference,
distributed processing). Skip for local-only tasks.

```bash
uv run python -m arf.scripts.utils.prestep $TASK_ID setup-machines
```

Spawn a subagent to execute the `/setup-remote-machine` skill. Include any user-provided budget
authorization, speed preferences, and the current budget summary from `aggregate_costs.py` in the
prompt:

```text
Execute the /setup-remote-machine skill for task $TASK_ID.
Read arf/skills/setup-remote-machine/SKILL.md and follow all steps
through Phase 5 (Prepare the Environment).
[Include any user context here, e.g.: The user authorized up to $40
for faster compute. Prefer speed over cost savings.]
```

After the subagent completes, verify:

* `machine_log.json` exists in the step log directory with all required fields per
  `arf/specifications/remote_machines_specification.md`

* SSH connection and GPU verified (check the `gpu_verified` field)

Write step log. Commit and run poststep. If skipped, the step must still appear in
`step_tracker.json` with status `"skipped"`.

#### Step: `implementation`

```bash
uv run python -m arf.scripts.utils.prestep $TASK_ID implementation
```

Spawn a subagent to execute the `/implementation` skill:

Use the Agent tool to launch a subagent with this prompt:

```text
Execute the /implementation skill for task $TASK_ID.
Read arf/skills/implementation/SKILL.md and follow all steps.
```

After the subagent completes, verify that all expected assets from `task.json` exist and pass their
verificators. Also review the subagent's final `Requirement Completion Checklist`: every `REQ-*`
item must be marked `done`, or the task must have a documented intervention explaining why it is
`partial` or `blocked`.

For experiment tasks with multiple variants, check cumulative API cost after each variant run
completes. If the plan specifies a budget cap, compare the running total against it. If the cap is
exceeded, stop further variant runs and document the overrun in `results/costs.json` `note` field.

Write step log. Commit and run poststep.

#### Step: `teardown` (optional)

Include if and only if `setup-machines` is included. Skip for local-only tasks. If all GPU work
completed during implementation, run teardown IMMEDIATELY after implementation — before
compare-literature, results, or suggestions. When the task used multiple machines and some were
already destroyed during implementation, the teardown step handles only machines not yet destroyed
and updates final cost tracking in `results/costs.json` and `results/remote_machines_used.json`.

```bash
uv run python -m arf.scripts.utils.prestep $TASK_ID teardown
```

Spawn a subagent to execute the Teardown Protocol from the `/setup-remote-machine` skill:

```text
Execute the Teardown Protocol from arf/skills/setup-remote-machine/SKILL.md
for task $TASK_ID. Download all results, destroy the instance, and update
machine_log.json, remote_machines_used.json, and costs.json.
```

After the subagent completes, verify:

* `machine_log.json` has a non-null `destroyed_at` timestamp

* `results/remote_machines_used.json` and `results/costs.json` reflect the machine usage

* Run `verify_machines_destroyed.py`:

  ```bash
  uv run python -m arf.scripts.verificators.verify_machines_destroyed \
    --task-id $TASK_ID
  ```

Write step log. Commit and run poststep.

### Phase 5: Analysis

#### Step: `creative-thinking` (optional)

Out-of-the-box analysis and alternative approaches. If skipped, the step must still appear in
`step_tracker.json` with status `"skipped"`.

#### Step: `results`

```bash
uv run python -m arf.scripts.utils.prestep $TASK_ID results
```

Write all results files:

* `results/results_summary.md` — must contain exactly these mandatory sections: `## Summary` (2-3
  sentences), `## Metrics` (min 3 bullet points with specific numbers), `## Verification` (list
  verificator outcomes)

* `results/results_detailed.md` — must contain these mandatory sections: `## Summary` (2-5
  sentences), `## Methodology` (machine specs, runtime, timestamps), `## Verification` (verificator
  results), `## Limitations` (constraints and caveats), `## Files Created` (bullet list of outputs),
  `## Task Requirement Coverage` (must be the final section). For experiment tasks, also include
  `## Examples` (min 10 concrete instances from prediction files — never fabricate examples). Each
  example must show the complete input-output pair: actual input given to the system and the actual
  raw output it produced, both in fenced code blocks. A summary table (e.g., item/prediction/correct
  columns) is NOT sufficient — the reader must see exactly what went in and what came out. For
  instance, if the task calls an LLM, show the actual prompt and the actual model response; if the
  task runs a classifier, show the feature vector and the raw prediction. Read
  `arf/specifications/task_results_specification.md` § "## Examples" for full requirements. Use
  `spec_version: "2"` in the YAML frontmatter (this is the results_detailed.md format version, not
  the specification document version). Before writing, re-read `tasks/$TASK_ID/task.json` and
  `plan/plan.md` `## Task Requirement Checklist`. This file must summarize all result artifacts
  produced by the task, not just the highlights. If a dedicated file is too long to inline fully,
  include the key findings in `results_detailed.md` and link to the full file. In the
  `## Task Requirement Coverage` section:

  * quote the operative task text from `task.json` plus the resolved long description verbatim
  * list every concrete `REQ-*` item from the plan
  * give a direct answer/result for each item
  * mark each item as `Done`, `Partial`, or `Not done`
  * point to the exact file/table/image/asset path that supports the claim

* `results/metrics.json` — only registered project metrics from `meta/metrics/` (e.g., `f1_all`,
  `accuracy_se2`, `efficiency_inference_cost_per_item_usd`). Two formats are valid:

  * Legacy flat format for a single metrics set:

    ```json
    {"f1_all": 82.3}
    ```

  * Explicit variant format for multiple metrics sets produced by one task:

    ```json
    {
      "variants": [
        {
          "variant_id": "model-a_prompt-short",
          "label": "Model A + short prompt",
          "dimensions": {"model": "model-a", "prompt": "short"},
          "metrics": {"f1_all": 82.3}
        }
      ]
    }
    ```

  Use the explicit variant format whenever one task compares multiple models, prompts, dataset
  sizes, hyperparameter settings, or other conditions that each produce their own metric set. Write
  `{}` if this task did not measure any registered metrics. Task-specific operational data (corpus
  sizes, download stats, counts) belongs in `results_detailed.md` or dedicated result files, NOT
  here. To discover available registered metric keys:

  ```bash
  uv run python -u -m arf.scripts.aggregators.aggregate_metrics --format ids
  ```

  To see full details (name, description, unit, datasets):

  ```bash
  uv run python -u -m arf.scripts.aggregators.aggregate_metrics --format json --detail full
  ```

  Run `verify_task_metrics.py` to validate before committing.

* `results/costs.json` — follow `arf/specifications/task_results_specification.md`. Required fields:
  `total_cost_usd` and `breakdown`. For zero-cost tasks: `{"total_cost_usd": 0, "breakdown": {}}`

* `results/remote_machines_used.json` — `[]` if none

* `results/images/` — charts and graphs (if applicable)

**Metrics cross-check**: Before writing `results_summary.md` or `results_detailed.md`, read
`results/metrics.json`. Verify that every number quoted in the markdown exactly matches the JSON
source. If any metric is `0.0` or `null` for a value that should have a real measurement,
investigate the implementation output before writing results. Numbers in markdown and JSON must be
identical — no rounding, no "approximately."

**Charts**: For experiment tasks, `results/images/` must contain at least 2 charts (e.g., metric
comparison bar chart, per-category breakdown). Every PNG in `results/images/` must be embedded in
`results_detailed.md` with `![description](images/filename.png)` and a 1-3 sentence description of
what the chart shows and the key takeaway.

Do not treat auxiliary result files as a substitute for `results_detailed.md`. The reader should be
able to understand the full output surface from `results_detailed.md` alone, using relative links
only for drill-down detail.

**Plan assumption check**: Re-read the plan's Objective and Approach sections. If actual results
contradict any stated assumption, hypothesis, or prior-task claim, document the discrepancy
prominently in `results_detailed.md` under `## Analysis`. Contradicted assumptions are findings —
they must be reported, not buried.

Write step log. Commit and run poststep.

#### Step: `compare-literature` (optional)

Include for experiment tasks that produce quantitative results comparable to published results. Skip
for tasks that do not produce performance metrics. If skipped, the step must still appear in
`step_tracker.json` with status `"skipped"`.

```bash
uv run python -m arf.scripts.utils.prestep $TASK_ID compare-literature
```

Spawn a subagent to execute the `/compare-literature` skill:

```text
Use the Agent tool to launch a subagent with this prompt:
"Execute the /compare-literature skill for task $TASK_ID.
Read arf/skills/compare-literature/SKILL.md and follow all steps."
```

The subagent will compare results against published results and write
`results/compare_literature.md`. After the subagent completes, verify the output exists and the
verificator passes:

```bash
uv run python -m arf.scripts.utils.run_with_logs --task-id $TASK_ID -- \
  uv run python -m arf.scripts.verificators.verify_compare_literature $TASK_ID
```

Fix all errors. Re-run until zero errors. Write step log. Commit and run poststep.

### Phase 6: Reporting

#### Step: `suggestions`

```bash
uv run python -m arf.scripts.utils.prestep $TASK_ID suggestions
```

Spawn a subagent to execute the `/generate-suggestions` skill:

```text
Use the Agent tool to launch a subagent with this prompt:
"Execute the /generate-suggestions skill for task $TASK_ID.
Read arf/skills/generate-suggestions/SKILL.md and follow all steps."
```

The subagent will review results, check existing suggestions for duplicates, and write
`results/suggestions.json`. After the subagent completes, verify the output exists and the
verificator passes:

```bash
uv run python -m arf.scripts.utils.run_with_logs --task-id $TASK_ID -- \
  uv run python -m arf.scripts.verificators.verify_suggestions $TASK_ID
```

Fix all errors. Re-run until zero errors. Write step log. Commit and run poststep.

#### Step: `reporting`

```bash
uv run python -m arf.scripts.utils.prestep $TASK_ID reporting
```

1. Run ALL relevant verificators with `run_with_logs.py`:

   * `verify_task_file.py`
   * `verify_task_dependencies.py`
   * `verify_suggestions.py`
   * `verify_task_metrics.py`
   * `verify_task_results.py`
   * `verify_task_folder.py`
   * `verify_logs.py`
   * Asset verificators for each produced asset type (all use `--task-id $TASK_ID`; pass a specific
     asset ID as positional arg, or omit to verify all assets of that type):
     * `verify_paper_asset.py --task-id $TASK_ID [paper_id]`
     * `verify_predictions_asset.py --task-id $TASK_ID [predictions_id]`,
       `verify_predictions_description.py --task-id $TASK_ID [predictions_id]`,
       `verify_predictions_details.py --task-id $TASK_ID [predictions_id]`
     * `verify_model_asset.py --task-id $TASK_ID [model_id]`
     * `verify_library_asset.py --task-id $TASK_ID [library_id]`
   * `verify_corrections.py $TASK_ID` (if corrections/ contains files)
   * `verify_research_papers.py` (if paper research was done)
   * `verify_research_internet.py` (if internet research was done)
   * `verify_compare_literature.py` (if compare-literature step was done)
   * `verify_machines_destroyed.py` (if remote machines were used)

2. Capture raw agent session transcripts and write the session capture report. Run the shared
   utility through `run_with_logs.py`:

   ```bash
   uv run python -m arf.scripts.utils.run_with_logs --task-id $TASK_ID -- \
     uv run python -m arf.scripts.utils.capture_task_sessions --task-id $TASK_ID
   ```

   The capture utility scans supported CLI transcript roots (currently Codex and Claude Code),
   copies every matching JSONL transcript into `logs/sessions/`, and writes
   `logs/sessions/capture_report.json`. If no matching transcript is found, proceed — the
   verificators emit a warning, but the reporting step still records what was checked.

3. Update `task.json`: set `status` to `"completed"` and set `end_time`. Note: `start_time` is
   already set by `worktree create` — do not overwrite it.

4. Write step log. Commit and run poststep.

### Phase 7: PR and Merge

1. Push the task branch:

   ```bash
   git push -u origin task/$TASK_ID
   ```

2. Create PR:

   ```bash
   gh pr create --title "$TASK_ID: <task name>" --body "..."
   ```

   PR body must contain: Summary (2-3 bullets), Assets Produced, Verification (all verificators
   passed).

3. Run the pre-merge verificator:

   ```bash
   uv run python -m arf.scripts.verificators.verify_pr_premerge $TASK_ID --pr-number <number>
   ```

   This checks file isolation, branch naming, PR format, task state, sensitive files, large files,
   merge conflicts, and runs all sub-verificators. If errors are found: fix the issues, commit,
   re-push, and re-run until zero errors. Do NOT merge with errors.

   **Recovering from PM-E011 (large file)**: the threshold is 5 MB (`LARGE_FILE_THRESHOLD_BYTES` in
   `verify_pr_premerge.py`). Fix it in place with a forward commit — never rewrite history:

   * For PDFs, rasterize with PyMuPDF at about 100 DPI / JPEG quality 60 and overwrite the file at
     its original path inside the task folder.
   * For other binary assets, reduce the file at its source (e.g., re-export at a lower resolution,
     recompress) and overwrite the path.
   * Then
     `git add <path> && git commit -m "$TASK_ID [reporting]: Compress <file> to satisfy PM-E011"`
     and `git push`. Re-run `verify_pr_premerge` until clean.

   NEVER run `git lfs migrate import`, `git filter-repo`, or `git push --force*` on the task branch.
   Those rewrite history shared with the PR and cause GitHub to auto-close it (see Critical Rule
   14).

4. If the PR has merge conflicts (common when parallel tasks merge to main during execution), merge
   `origin/main` into the task branch:

   ```bash
   git fetch origin main
   git merge origin/main
   # Resolve conflicts — for task.json, keep the task branch version
   git add <resolved files>
   git commit -m "$TASK_ID [reporting]: Merge main to resolve conflicts"
   git push
   ```

   Re-run `verify_pr_premerge` after resolving conflicts.

5. Merge with merge commit (preserve history):

   ```bash
   gh pr merge <number> --merge
   ```

6. Return to the main repo and remove the worktree:

   ```bash
   cd <main_repo_root>
   git checkout main
   uv run python -m arf.scripts.utils.worktree remove $TASK_ID
   git pull --ff-only
   ```

7. Clean up orphaned untracked files in the task folder. Commands wrapped with `run_with_logs.py`
   that ran before the worktree was created (Phase 0 violation) or after the final commit leave
   untracked log files on `main`. Delete them:

   ```bash
   git clean -fd tasks/$TASK_ID/logs/commands/
   ```

   If `git clean` reports files it would delete, that confirms orphaned logs existed. If there is
   nothing to clean, this is a harmless no-op.

### Phase 8: Final Verification

Run the completion verificator from the main repo (after worktree removal and `git pull`) to confirm
everything is in order:

```bash
uv run python -m arf.scripts.verificators.verify_task_complete $TASK_ID
```

This checks: task status, timestamps, all steps finished, mandatory dirs and files, expected assets,
git branch exists, PR merged, no files modified outside task folder, and runs all sub-verificators
(task file, dependencies, asset verificators). Fix any errors before considering the task done.

The reporting-step capture (Phase 6 Step 2) is the final session capture for the task. Do NOT re-run
`capture_task_sessions` here — a completed task folder is immutable (see `arf/README.md`
"Immutability of Completed Tasks"), and any commit landing in `tasks/$TASK_ID/logs/sessions/` after
this point mutates a task whose branch has already been merged.

### Phase 9: Overview Sync

After `verify_task_complete.py` passes, refresh the generated overview from the main repo on `main`:

1. Confirm you are in the main repo root on branch `main`.

2. Rebuild the overview:

   ```bash
   uv run python -u -m arf.scripts.overview.materialize
   ```

3. Review the resulting diff. If `overview/` is unchanged, skip the commit and push.

4. If `overview/` changed:

   * Stage only `overview/`. Do not include unrelated local changes from the main repo.

   * If `overview/` already contains unrelated user edits, stop and resolve that conflict instead of
     overwriting them blindly.

   * Commit directly on `main` as a separate maintenance commit, for example:

     ```bash
     git add overview
     git commit -m "overview: refresh after $TASK_ID"
     ```

   * Push the updated `main` branch:

     ```bash
     git push origin main
     ```

## Done When

* All steps in `step_tracker.json` are `completed` (or `skipped` with documented reason)

* `task.json` has `status: "completed"` with `start_time` (set by `worktree create`) and `end_time`

* All expected assets exist and pass their verificators

* `results/results_detailed.md` exhaustively covers every concrete task requirement and ends with
  `## Task Requirement Coverage`

* All verificators pass with zero errors

* PR is created, reviewed, and merged to `main`

* Task branch is pushed (kept for audit trail)

* `overview/` has been rebuilt from the main repo on `main`, and any resulting diff is committed and
  pushed as a separate `main` commit

## Forbidden

* NEVER modify files outside the task folder on a task branch

* NEVER skip prestep or poststep for any step

* NEVER use non-sequential step numbers in `step_tracker.json`

* NEVER create an asset without reading its specification first

* NEVER commit an asset without running its verificator

* NEVER run CLI commands on a task branch without `run_with_logs.py`

* NEVER use `run_with_logs.py` before the worktree is created (Phase 0) — logs land on `main` and
  are never committed

* NEVER use `run_with_logs.py` after the PR is merged (Phases 8-9) — logs land on `main` and are
  never committed

* NEVER claim "no papers to add" without verifying every cited paper exists in the corpus

* NEVER make a separate commit just for `step_tracker.json` — stage it with your step work; poststep
  auto-commits the completion update

* NEVER modify infrastructure files (arf/, .claude/, specs) on a task branch

* NEVER override or restrict a skill's behavior when spawning its subagent

* NEVER create multiple assets inline — spawn one subagent per asset

* NEVER execute skill logic directly in the orchestrator — always use a subagent

* NEVER place Python files or scripts outside `code/` — all code goes in `tasks/$TASK_ID/code/`

* NEVER commit Python code without running `ruff check --fix`, `ruff format`, and `mypy`

* NEVER run `worktree.py create` or `worktree.py remove` from inside a worktree. Run these from the
  main repo only

* NEVER run `git lfs migrate import`, `git filter-repo`, or `git push --force` /
  `--force-with-lease` on a `task/*` branch — they rewrite history shared with the PR, cause GitHub
  to auto-close it, and corrupt the audit trail. To recover from PM-E011 (large file), compress the
  file in place and commit forward (see Critical Rule 14 and Phase 7 Step 3)

* NEVER rebuild, commit, or push `overview/` from a task branch or task worktree
