---
name: "human-brainstorm"
description: "Run an interactive brainstorming session to review state and choose next actions."
---
# Human Brainstorm

**Version**: 9

## Goal

Run an interactive brainstorming session with the researcher to review project state and make
strategic decisions: reprioritize or reject suggestions, cancel or update planned tasks, create new
tasks, and propose new suggestions.

## Inputs

None required. The skill aggregates project state automatically.

## Context

Read before starting:

* `arf/specifications/suggestions_specification.md`
* `arf/specifications/corrections_specification.md`
* `arf/specifications/task_file_specification.md`
* `arf/specifications/logs_specification.md` — step log folder naming, frontmatter, mandatory
  sections, and session capture format
* `arf/specifications/task_steps_specification.md` — canonical step IDs and step numbering rules
* `arf/docs/howto/use_aggregators.md` — JSON output structure for all aggregators
* `arf/skills/create-task/SKILL.md` — referenced in Phase 5 for task creation
* `meta/asset_types/answer/specification.md` — referenced in Phase 5 for answer assets

## Steps

### Phase 1: Review Project State

1. Run the task aggregator to get an overview of all tasks:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_tasks \
     --format json --detail short
   ```

   Returns `{"task_count": N, "tasks": [...]}`. Each task has: `task_id`, `name`,
   `short_description`, `status`, `task_types`, `dependencies`, `source_suggestion`,
   `effective_date`.

   For recently completed tasks that need deeper review, fetch full details selectively:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_tasks \
     --format json --detail full --ids <task_id_1> <task_id_2> ...
   ```

2. Run the suggestion aggregator. First get titles and priorities for all actionable suggestions:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_suggestions \
     --format json --detail short --uncovered
   ```

   Returns `{"suggestion_count": N, "suggestions": [...]}`. Each suggestion has: `id`, `title`,
   `kind`, `priority`, `source_task`, `categories`, `status`, `date_added`.

   Then read full descriptions only for high-priority suggestions and any categories the researcher
   specifically requests:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_suggestions \
     --format json --detail full --uncovered --priority high
   ```

   Present a count of remaining suggestions by priority level so the researcher can request deeper
   review of specific categories.

3. Run the answer aggregator to read all answer assets:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_answers \
     --format json --detail full
   ```

   Returns `{"answer_count": N, "answers": [...]}`. Each answer has: `answer_id`, `question`,
   `short_title`, `categories`, `answer_methods`, `confidence`, `created_by_task`, `short_answer`.

4. Run the cost aggregator to get budget status:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_costs \
     --format json --detail short
   ```

   Returns `{"budget": {...}, "summary": {...}, "tasks": [...], "skipped_tasks": [...]}`. Key fields
   in `data["summary"]`: `total_cost_usd`, `budget_left_usd`, `spent_percent`,
   `stop_threshold_reached`, `warn_threshold_reached`. Key fields in `data["budget"]`:
   `total_budget`, `per_task_default_limit`.

   Include total spent, budget remaining, and any threshold warnings in the project state
   presentation.

5. Read `results/results_summary.md` for every task completed since the last brainstorm session.
   Identify which tasks are new by comparing against the most recent brainstorm-results task's
   dependency list. Extract specific metrics, findings, and failure patterns — not just "task X
   completed."

6. Read `results/compare_literature.md` for each task completed since the last brainstorm that has
   one. Extract published results that significantly beat our results, methods not yet tried, and
   surprising discrepancies worth investigating.

**Deep reading before presenting**: Do NOT present project state to the researcher until you have
completed all aggregation AND reading steps above. The initial presentation must reflect
understanding of actual experimental results (specific F1 numbers, failure patterns, key findings
from answers), not just task completion statuses. Surface-level summaries that only report "task X
completed" without mentioning its key findings are insufficient.

7. Run the overview materializer so the latest state is readable on GitHub:

   ```bash
   uv run python -u -m arf.scripts.overview.materialize
   ```

8. **Form independent priority assessment**: Before presenting project state, independently reassess
   every active suggestion's priority based on what completed task results and answers actually
   show. Do NOT echo priority labels from `suggestions.json` — they were assigned at creation time
   and may be stale. Base your reassessment on:

   * What completed task results actually show (e.g., if a suggestion proposes "try technique X" but
     a completed task already showed technique X performs poorly, deprioritize it)
   * What answer assets reveal about feasibility or relevance
   * Whether the suggestion's assumptions still hold given new findings
   * The project's stated research questions and success criteria in `project/description.md`

9. Present project state to the researcher:

   * Completed tasks and their key findings (with specific metrics, not just "completed")
   * In-progress and not-started tasks
   * Actionable suggestions with your reassessed priorities and rationale for any changes from
     original priority
   * Key insights from answer assets that affect strategic direction
   * Dependency graph

10. Recommend the researcher also review the project state in the browser for easier reading:

    * Tasks: [overview/tasks/README.md](../../../overview/tasks/README.md)
    * Suggestions: [overview/suggestions/README.md](../../../overview/suggestions/README.md)

### Phase 1.5: Clarify

11. Ask the researcher: "Do you have any notes, ideas, or context that should guide this session?"
    If the researcher provides notes, read them carefully and integrate their content into your
    analysis before proceeding. Reference specific points from the notes when proposing tasks or
    assessing suggestions. Do not treat researcher notes as a secondary input — they often contain
    the most important strategic direction for the session.

12. Ask the researcher 3-5 clarifying questions. Wait for answers before proceeding. Example
    questions:

    * "What area of the project are you most interested in advancing right now?"
    * "Any budget limits for upcoming tasks?"
    * "Preferences on parallelism, remote execution, or interactive vs autonomous execution?"
    * "Are there any results or findings from completed tasks that surprised you or changed your
      thinking?"
    * "Are you looking to create a few focused tasks or a broader batch?"

    Adapt questions to the current project state. Skip questions whose answers are obvious from
    context. The goal is to avoid assumptions about the researcher's priorities and knowledge level.

    Before printing the clarifier list, remove every question that has already been answered in the
    current conversation — explicit researcher statements (e.g., "use GPT-5.4"), the selected plan,
    or a prior accepted default all count as answers. Re-asking a resolved question wastes a round
    trip and erodes trust. If every clarifier you would have asked is already resolved, skip Phase
    1.5 entirely and advance to Phase 2.

### Phase 2: Discuss (Structured Rounds)

The discussion covers three topic areas. Rounds may overlap if the researcher's input naturally
covers multiple concerns. Ensure all three areas (new tasks, suggestion cleanup, confirmation) are
addressed before proceeding to Phase 4.

Round 1: New tasks

13. Propose specific tasks with names, dependencies, scope, and execution details. For each task,
    include:

    * What it does and why
    * Dependencies (minimize — only add when genuinely needed)
    * Whether it needs remote compute or API budget
    * Which suggestion it covers (if any)

14. Wait for researcher input. Iterate until the researcher is satisfied with the task list.

Round 2: Suggestion cleanup

15. Proactively review ALL remaining active suggestions and propose which to reject or deprioritize.
    Present as: "These N suggestions are still active after accounting for the new tasks. Here are
    ones I recommend dropping or deprioritizing..."

    Default to keeping suggestions unless they are clearly redundant, superseded by a new task, or
    no longer relevant. The researcher may see value the AI does not — don't aggressively prune.

    Tasks tend to generate many suggestions and the backlog grows quickly. The brainstorm session is
    the right time to prune.

16. Wait for researcher input. The researcher approves each rejection or reprioritization
    individually.

Round 3: Confirm

17. Summarize all decisions in a compact list:

    * New tasks (with IDs, names, dependencies)
    * Suggestions rejected
    * Suggestions reprioritized
    * Tasks cancelled or updated

    Cross-check every numeric count mentioned in the narrative against the count derivable from the
    structured list in the same message. Approximations like "about 17" are a bug when the table
    lists 19 — state the verified numbers explicitly (e.g., "rejections: 19 — verified against the
    correction-file table"). This one-line discipline catches a class of summary-vs-list drift that
    the researcher otherwise has to catch manually.

18. Wait for explicit confirmation before creating anything.

Once the researcher has explicitly confirmed the decision list, the remaining Phases 3-6 execute
without any additional confirmation gate. The Phase 2 Round 3 confirmation authorizes the full
remaining sequence including the shared-state actions in Phase 6: push to origin, PR creation,
pre-merge verificator, and merge. Do not pause to ask the researcher for a second "go" before push,
PR, or merge — that is redundant and slows the session for no benefit. If the pre-merge verificator
surfaces errors, fix them and continue; do not interpret errors as a reason to pause for additional
confirmation.

### Phase 3: Determine Next Task ID

19. Use the tasks aggregator output from Phase 1 to find the highest existing task index `M` (or `0`
    if the project is empty). The brainstorm-results task's `task_index` is `M + 1`. This index must
    be reserved before any child task is created.

    Ordering invariant: for any brainstorm-results task `tNNNN_brainstorm_results_K`, every task
    that this brainstorm session creates (Phase 5 `/create-task` calls, plus any answer-asset tasks)
    must have `task_index > NNNN`. The brainstorm task is the causal parent of its children and must
    appear before them in task history. Do not pick a higher task index for the brainstorm task "so
    the children get the lower numbers" — that inverts the causal order and is a bug. This ordering
    is enforced by the sequencing of Phase 4 (brainstorm task folder created first) and Phase 5
    (child tasks created afterward via `/create-task`, which picks the next available index and
    therefore returns indices strictly greater than the brainstorm task's index).

### Phase 4: Create Brainstorm-Results Task Branch

20. Create a branch: `task/tNNNN_brainstorm_results_N` where `NNNN` is the next task ID and `N` is
    the brainstorming session number.

21. Create the brainstorm-results task folder with the full mandatory structure:

    ```text
    tasks/tNNNN_brainstorm_results_N/
    ├── __init__.py
    ├── task.json
    ├── task_description.md
    ├── step_tracker.json
    ├── plan/
    │   └── plan.md
    ├── research/
    │   ├── research_papers.md
    │   ├── research_internet.md
    │   └── research_code.md
    ├── assets/
    │   └── .gitkeep
    ├── corrections/
    ├── intervention/
    │   └── .gitkeep
    ├── results/
    │   ├── results_summary.md
    │   ├── results_detailed.md
    │   ├── metrics.json
    │   ├── suggestions.json
    │   ├── costs.json
    │   └── remote_machines_used.json
    └── logs/
        ├── session_log.md
        ├── commands/
        │   └── .gitkeep
        ├── searches/
        │   └── .gitkeep
        ├── sessions/
        │   └── .gitkeep
        └── steps/
            ├── 001_review-project-state/
            │   └── step_log.md
            ├── 002_discuss-decisions/
            │   └── step_log.md
            ├── 003_apply-decisions/
            │   └── step_log.md
            └── 004_finalize/
                └── step_log.md
    ```

    The step log folder names must match the regex `^\d{3}_` (zero-padded 3-digit prefix). The file
    inside each folder must be called `step_log.md`. These rules are enforced by
    `arf/scripts/verificators/verify_logs.py` (codes `LG-E005`, `LG-E008`). See
    `arf/specifications/logs_specification.md` for the authoritative convention.

    Placeholder file contents for brainstorm tasks:

    `metrics.json`:

    ```json
    {}
    ```

    `costs.json`:

    ```json
    {
      "total_cost_usd": 0.00,
      "breakdown": {}
    }
    ```

    `remote_machines_used.json`:

    ```json
    []
    ```

    Each research file (`research_papers.md`, `research_internet.md`, `research_code.md`) must have
    the standard section headings (Objective, Background, Methodology Review, Key Findings,
    Recommended Approach, References) with content stating "No research required for brainstorming
    session."

    `plan/plan.md` should be minimal with standard sections (Objective, Approach, Cost Estimation,
    Step by Step, Remote Machines, Assets Needed, Expected Assets, Time Estimation, Risks &
    Fallbacks, Verification Criteria) filled in briefly for a planning-only task.

22. Write `task.json` with `spec_version: 4`, status `"completed"`, dependencies listing all
    currently completed tasks, `source_suggestion: null`, `expected_assets: {}`, and either: inline
    `long_description` or `long_description_file`. Prefer `long_description_file` with
    `task_description.md`. If the session produces answer assets, update `expected_assets`
    accordingly (e.g., `{"answer": 1}`).

23. Write `step_tracker.json` with the standard brainstorm steps. The brainstorm flow uses custom
    step names (not canonical step IDs from `task_steps_specification.md`) because it does not fit
    the preflight → research → planning → implementation → analysis → reporting sequence. Custom
    names produce a `TS-W001` warning from the step-tracker verificator, which is expected and
    non-blocking. Each `log_file` must point at the step folder (trailing slash), not a directory
    prefix or the root `logs/steps/` directory — `verify_logs.py` matches on the folder's `^\d{3}_`
    prefix.

    ```json
    {
      "task_id": "tNNNN_brainstorm_results_N",
      "steps": [
        {
          "step": 1,
          "name": "review-project-state",
          "description": "Aggregate and present project state to researcher.",
          "status": "completed",
          "started_at": "<ISO 8601>",
          "completed_at": "<ISO 8601>",
          "log_file": "logs/steps/001_review-project-state/"
        },
        {
          "step": 2,
          "name": "discuss-decisions",
          "description": "Structured discussion with researcher on tasks and suggestions.",
          "status": "completed",
          "started_at": "<ISO 8601>",
          "completed_at": "<ISO 8601>",
          "log_file": "logs/steps/002_discuss-decisions/"
        },
        {
          "step": 3,
          "name": "apply-decisions",
          "description": "Create new task folders, correction files, and suggestion updates.",
          "status": "completed",
          "started_at": "<ISO 8601>",
          "completed_at": "<ISO 8601>",
          "log_file": "logs/steps/003_apply-decisions/"
        },
        {
          "step": 4,
          "name": "finalize",
          "description": "Write results, step logs, session capture, run verificators, PR, merge.",
          "status": "completed",
          "started_at": "<ISO 8601>",
          "completed_at": "<ISO 8601>",
          "log_file": "logs/steps/004_finalize/"
        }
      ]
    }
    ```

### Step Log Format

Every `step_log.md` in `logs/steps/<NNN>_<step-name>/` must follow this format (from
`arf/specifications/logs_specification.md`). Missing frontmatter fields or missing sections are
reported as `LG-E005` errors by `verify_logs.py`.

```yaml
---
spec_version: "3"
task_id: "tNNNN_brainstorm_results_N"
step_number: <N>
step_name: "<step-name>"
status: "completed"
started_at: "<ISO 8601 UTC>"
completed_at: "<ISO 8601 UTC>"
---
```

Mandatory sections, in this order:

* `## Summary` — 1-3 sentences describing what the step accomplished. Minimum 20 words or
  `verify_logs.py` raises `LG-W003`.
* `## Actions Taken` — numbered list of concrete actions. Minimum 2 items.
* `## Outputs` — bullet list of files created or modified in this step. Use "None" if the step
  produced no files.
* `## Issues` — problems encountered, or the literal string `No issues encountered.`

The `step_number` field must match the `step` field of the corresponding entry in
`step_tracker.json` or `verify_logs.py` raises `LG-E007`. The `task_id` field must match the task
folder name or `verify_logs.py` raises `LG-E006`.

### Phase 5: Apply Decisions

For each decision agreed with the researcher:

Reject suggestion:

24. Write a correction file in the brainstorm task's `corrections/` folder following
    `corrections_specification.md`:

    ```text
    corrections/suggestion_S-XXXX-NN.json
    ```

    With `action: "update"`, `changes: {"status": "rejected"}`, and a rationale.

Reprioritize suggestion:

25. Write a correction file with `action: "update"`, `changes: {"priority": "<new_priority>"}`, and
    a rationale.

Cancel not-started task:

26. Directly edit the target task's `task.json` to set `"status": "cancelled"`. Only cancel tasks
    with status `"not_started"`. Never modify a completed or in-progress task.

Update not-started task:

27. Directly edit the target task's `task.json` to update fields (dependencies, description, etc.).
    If the task uses `long_description_file`, edit the referenced markdown file instead of forcing
    the description back inline. Only update tasks with status `"not_started"`.

Create new task:

28. Sanity check before calling `/create-task`: confirm the brainstorm-results task folder
    (`tasks/tNNNN_brainstorm_results_K/`) already exists on disk and has a valid `task.json` with
    `task_index = NNNN`. If it does not, return to Phase 4 and complete it first. `/create-task`
    relies on the tasks aggregator to pick the next available index; if the brainstorm task is not
    yet on disk, `/create-task` will claim `NNNN` for a child task and break the ordering invariant
    from Phase 3 step 19.

    For each new task, follow the `/create-task` skill instructions
    (`arf/skills/create-task/SKILL.md`). Pass the task description agreed with the researcher as
    `$TASK_DESCRIPTION`. Include the source suggestion ID (e.g., `S-0012-03`) in the description
    text when the task covers a suggestion — `/create-task` extracts it for the `source_suggestion`
    field. The `/create-task` skill auto-determines the next task index and derives all structured
    fields from the free-form description.

    When creating many tasks (5+), run the aggregators once before the first `/create-task`
    invocation and reuse the cached output. Use parallel agents to create tasks concurrently.

New suggestion:

29. Write to the brainstorm task's `results/suggestions.json` following
    `suggestions_specification.md`. Use the brainstorm task ID for `source_task` and suggestion ID
    prefix.

Answer asset:

30. Create answer assets in the brainstorm task's `assets/answer/<answer_id>/` folder following
    `meta/asset_types/answer/specification.md`. Each answer asset requires:

    * `details.json` — structured metadata with question, categories, sources, confidence
    * `short_answer.md` — YAML frontmatter + `## Question`, `## Answer` (2-5 sentences),
      `## Sources`
    * `full_answer.md` — YAML frontmatter (include `confidence`) + `## Question`, `## Short Answer`,
      `## Research Process`, `## Evidence from Papers`, `## Evidence from Internet Sources`,
      `## Evidence from Code or Experiments`, `## Synthesis`, `## Limitations`, `## Sources`

    Run `uv run flowmark --inplace --nobackup` on the markdown files after writing.

### Phase 6: Record and Finalize

31. Write `results/results_summary.md` documenting all decisions. Must contain these sections in
    this order:

    * `## Summary` — 2-3 sentences with headline counts and key outcomes

    * `## Session Overview` — date, context, what prompted the session

    * `## Decisions` — numbered list of every decision with rationale

    * `## Metrics` — table with counts for created, covered, rejected, reprioritized items, and
      corrections written

    * `## Verification` — list of verificators run and their results

    * `## Next Steps` — execution order and wave structure

32. Write `results/results_detailed.md` with sections:

    * `## Summary`
    * `## Methodology` — step-by-step process followed
    * `## Metrics` — same table as results_summary
    * `## Limitations` — "Planning task, no experiments run"
    * `## Files Created` — list of all files/folders created
    * `## Verification` — verificator results

33. Write `logs/session_log.md` with the complete chat transcript of the brainstorming session. This
    is the primary audit trail. Include every question asked and every answer the researcher gave.
    Structure:

    ```markdown
    # Brainstorm Session N — Full Transcript

    ## Project State Presented

    <paste the full project state summary that was shown to the
    researcher, including all tasks, suggestions, and dependency graph>

    ## Clarification Questions

    AI: <clarifying questions asked>

    Researcher: <answers>

    ## Discussion — Round 1: New Tasks

    AI: <task proposals>

    Researcher: <feedback>

    ...

    ## Discussion — Round 2: Suggestion Cleanup

    AI: <rejection/reprioritization proposals>

    Researcher: <decisions>

    ...

    ## Discussion — Round 3: Confirmation

    AI: <summary of all decisions>

    Researcher: <confirmation>

    ## Decisions Summary

    <numbered list of final decisions>
    ```

    Include the complete exchange for all decisions, questions, answers, and rejected ideas with
    reasoning. For very long sessions (1M+ context), a structured summary preserving all
    decision-relevant exchanges is acceptable. Never omit a decision, rationale, or researcher
    instruction. The log must allow a reader to reconstruct what was discussed and decided.

34. Capture raw CLI session transcripts and write the session capture report:

    ```bash
    uv run python -m arf.scripts.utils.run_with_logs --task-id $TASK_ID -- \
      uv run python -m arf.scripts.utils.capture_task_sessions --task-id $TASK_ID
    ```

    The capture utility scans supported CLI transcript roots (currently Codex and Claude Code),
    copies every matching JSONL transcript into `logs/sessions/`, and writes
    `logs/sessions/capture_report.json`. If no matching transcript is found, proceed — the
    verificators emit a warning, but the reporting step still records what was checked.

    After capturing sessions, compress any JSONL files that trigger false-positive secret detection
    patterns (e.g., skill text containing `API_KEY`) before committing:

    ```bash
    for f in logs/sessions/*.jsonl; do
      if grep -q 'API_KEY\|SECRET_KEY\|PRIVATE KEY' "$f" 2>/dev/null; then
        gzip "$f"
      fi
    done
    ```

35. Run verificators. All four must pass with zero errors before committing; warnings may be
    reviewed but are non-blocking.

    ```bash
    uv run python -u -m arf.scripts.verificators.verify_task_file tNNNN_brainstorm_results_N
    uv run python -u -m arf.scripts.verificators.verify_corrections tNNNN_brainstorm_results_N
    uv run python -u -m arf.scripts.verificators.verify_suggestions tNNNN_brainstorm_results_N
    uv run python -u -m arf.scripts.verificators.verify_logs tNNNN_brainstorm_results_N
    ```

    Expected warnings for a pure-planning brainstorm task:

    * `LG-W005 No command logs found in logs/commands/` — the brainstorm skill runs aggregators and
      verificators directly from the orchestrator, not through `run_with_logs.py`. This warning is
      expected when the skill produces no wrapped CLI calls. If the warning is noisy, wrap the Phase
      6 aggregator and verificator calls in `run_with_logs.py` after `init-folders`:

      ```bash
      uv run python -m arf.scripts.utils.run_with_logs --task-id $TASK_ID -- \
        uv run python -u -m arf.scripts.verificators.verify_task_file $TASK_ID
      ```

    * `LG-W007` / `LG-W008` — cleared by Step 34's session capture. If they persist, re-run the
      capture utility and verify that `logs/sessions/capture_report.json` exists and is valid JSON.

    * `TF-W005 expected_assets is empty` — expected when the brainstorm session produces no answer
      assets. If the session produces answer assets, set `expected_assets` in `task.json`
      accordingly and the warning clears.

36. Re-run the overview materializer to reflect all changes:

    ```bash
    uv run python -u -m arf.scripts.overview.materialize
    ```

37. Run `uv run flowmark --inplace --nobackup <changed.md>` for edited markdown files. Run
    `uv run ruff check --fix . && uv run ruff format .` if any Python files were created.

38. Commit all changes with descriptive message.

39. Push branch and create PR. The PR must follow `arf/specifications/task_git_specification.md`:

    Title: `<task_id>: <task name>` (e.g.,
    `t0016_brainstorm_results_4: Brainstorm results session 4`)

    Body (use this exact structure):

    ```markdown
    ## Summary

    * <2-3 bullet points describing what the session decided>

    ## Assets Produced

    * No assets (brainstorm-results task)
    * New tasks created: <list task IDs>

    ## Verification

    All verificators pass with 0 errors:

    * verify_task_file.py — PASSED
    * verify_corrections.py — PASSED
    * verify_suggestions.py — PASSED
    * verify_logs.py — PASSED
    ```

40. Run the pre-merge verificator:

    ```bash
    uv run python -m arf.scripts.verificators.verify_pr_premerge \
      <task_id> --pr-number <number>
    ```

    Fix any errors before proceeding. Do NOT merge with errors.

41. Merge the PR with a merge commit (not squash).

## Output Format

The brainstorm-results task folder contains:

* `__init__.py` — Python package marker
* `task.json` — task metadata with status `"completed"`
* `task_description.md` — referenced from `task.json` via `long_description_file`
* `step_tracker.json` — 4-step brainstorm tracker with per-step `log_file` folder pointers
* `plan/plan.md` — minimal plan for the brainstorm session
* `research/research_papers.md` — placeholder (no research needed)
* `research/research_internet.md` — placeholder (no research needed)
* `research/research_code.md` — placeholder (no research needed)
* `corrections/*.json` — one file per suggestion correction
* `results/suggestions.json` — new suggestions (if any), or empty array
* `results/results_summary.md` — decisions narrative with metrics
* `results/results_detailed.md` — detailed methodology and file list
* `results/metrics.json` — empty `{}`
* `results/costs.json` — zero-cost record
* `results/remote_machines_used.json` — empty `[]`
* `logs/session_log.md` — complete chat transcript of the session
* `logs/sessions/capture_report.json` — session capture report with scanned roots and copied files
* `logs/sessions/*.jsonl` — raw CLI session transcripts captured for the task (if found)
* `logs/steps/001_review-project-state/step_log.md` — step 1 log
* `logs/steps/002_discuss-decisions/step_log.md` — step 2 log
* `logs/steps/003_apply-decisions/step_log.md` — step 3 log
* `logs/steps/004_finalize/step_log.md` — step 4 log

## Done When

* All researcher decisions are recorded in the task folder

* `logs/session_log.md` contains the session transcript (verbatim or structured summary for long
  sessions)

* Every completed step in `step_tracker.json` has a matching `logs/steps/<NNN>_<step-name>/` folder
  with a `step_log.md` that has valid frontmatter and the four mandatory sections

* Task file verificator passes with no errors

* Correction verificator passes with no errors

* Suggestion verificator passes with no errors (if suggestions exist)

* Logs verificator passes with no errors (warnings `LG-W005`, `LG-W007`, `LG-W008` acceptable only
  when explicitly justified above)

* Pre-merge verificator passes with no errors

* Overview is rebuilt (`materialize.py` ran after all changes)

* Updated aggregator output reflects corrections:

  ```bash
  uv run python -u -m arf.scripts.aggregators.aggregate_suggestions \
    --format markdown --detail short --uncovered
  ```

  Shows rejected suggestions excluded and reprioritized ones with new priority.

* PR is merged to main

## Forbidden

* Never pause for a second authorization between Phase 5 and Phase 6. The Phase 2 Round 3
  confirmation is the authorization for the entire remaining lifecycle including push, PR, and
  merge.

* Never create child tasks in Phase 5 before the brainstorm-results task folder exists on disk with
  a valid `task.json`. Breaking Phase 4 → Phase 5 ordering inverts the task-index ordering invariant
  from Phase 3 step 19.

* NEVER modify a completed task's folder contents (use corrections)

* NEVER make decisions without researcher approval

* NEVER skip writing rationale for any decision

* Never create correction files without reading the corrections specification first

* Never create subdirectories or extra files in new task folders. New not-started tasks may contain
  `task.json` and a referenced `task_description.md`, but nothing else.

* Never omit decisions, rationales, or researcher instructions from the session log

* Never aggressively reject suggestions; default to keeping unless clearly redundant or superseded
