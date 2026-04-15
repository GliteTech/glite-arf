---
name: "generate-suggestions"
description: "Generate follow-up task suggestions from completed task outputs and project context."
---
# Generate Suggestions

**Version**: 4

## Goal

Generate follow-up task suggestions by synthesizing all available research, results, and logs from
the current task, then deduplicating against existing suggestions.

## Inputs

* `$TASK_ID` — the task folder name (e.g., `t0003_download_semcor_dataset`)

## Context

Read before starting:

* `arf/docs/howto/use_aggregators.md` — JSON output structure for all aggregators

* `project/description.md` — project research questions and success criteria (guides suggestion
  relevance and priority)

* `tasks/$TASK_ID/task.json` — task objective, description, expected assets

* `arf/specifications/suggestions_specification.md` — authoritative format for
  `results/suggestions.json`

* Task type definitions — load available types to recommend for suggestions:

  ```bash
  uv run python -u -m arf.scripts.aggregators.aggregate_task_types --format json
  ```

## Steps

### Phase 1: Gather All Task Context

1. Read `tasks/$TASK_ID/task.json` to understand the task objective and scope. If it contains
   `long_description_file`, also read the referenced markdown file.

2. Read all available research files (skip any that do not exist):

   * `tasks/$TASK_ID/research/research_papers.md`
   * `tasks/$TASK_ID/research/research_internet.md`
   * `tasks/$TASK_ID/research/research_code.md`

3. Read the task results (skip any that do not exist):

   * `tasks/$TASK_ID/results/results_summary.md`
   * `tasks/$TASK_ID/results/results_detailed.md`
   * `tasks/$TASK_ID/results/metrics.json`
     * If the file uses explicit variants, inspect all variants and note the comparison dimensions.
       Do not reduce the task to one assumed canonical metrics set.

4. Read the task plan:

   * `tasks/$TASK_ID/plan/plan.md`

5. Scan step logs for notable findings, errors, or unexpected outcomes:

   * List `tasks/$TASK_ID/logs/steps/` and read `step_log.md` files.

6. Read comparison with literature if it exists:

   * `tasks/$TASK_ID/results/compare_literature.md` or any comparison file in `results/`.

### Phase 2: Generate Candidate Suggestions

7. Based on all gathered context, brainstorm suggestion candidates. Consider:

   * Gaps found during research — topics with insufficient coverage, methods not yet tried, datasets
     not yet explored.

   * **Follow-up experiments** — natural next steps from the task results, ablations, scaling
     experiments, alternative approaches.

     * For multi-variant tasks, look for gaps or promising directions revealed by the differences
       between variants, not just the best number in the file.

   * **Techniques from papers** — methods described in research that were not applied in this task
     but could be valuable.

   * **Errors and surprises** — unexpected findings in logs or results that warrant investigation.

   * **Infrastructure needs** — libraries, tools, or datasets that would accelerate future tasks.

   * Evaluation improvements — new metrics, benchmarks, or evaluation methods to adopt.

8. For each candidate, draft: `title`, `description`, `kind`, `priority`, `source_paper` (if
   applicable), and `categories`.

   * `recommended_task_types` — list of task type slugs from `meta/task_types/` that match this
     suggestion. Load available types via the aggregator and select the most appropriate one(s)
     based on the suggestion's nature. Include this in the description text as "Recommended task
     types: X, Y" so the task creation flow can assign them to `task.json`.

9. Aim for 3-10 candidates. Prefer fewer high-quality suggestions over many weak ones.

### Phase 3: Deduplicate Against Existing Suggestions and Tasks

10. Run the suggestions aggregator with `--uncovered` to retrieve only suggestions not yet covered
    by any task (via the `source_suggestion` field in `task.json`):

    ```bash
    uv run python -u -m arf.scripts.aggregators.aggregate_suggestions \
      --format json --detail full --uncovered
    ```

11. Run the task aggregator to get all tasks with names, descriptions, and statuses:

    ```bash
    uv run python -u -m arf.scripts.aggregators.aggregate_tasks \
      --format json --detail short
    ```

    A suggestion is redundant if an existing task (completed, in-progress, or not-yet-started)
    already covers the same objective — even if `source_suggestion` was not set for that task.

12. Compare each candidate against both the aggregator output and the task list. A candidate is a
    duplicate if:

    * An existing suggestion covers the same core idea — even if the wording differs.
    * An existing task already addresses the same objective, regardless of its status. Check titles,
      descriptions, source papers, and task objectives for overlap.

13. Remove candidates that are duplicates of existing suggestions or tasks.

14. For candidates that partially overlap (e.g., same method but different dataset, or same dataset
    but different method), refine the candidate to focus on the non-overlapping aspect.

### Phase 4: Refine and Finalize

15. Review the remaining candidates. For each one:

    * Ensure `title` is under 120 characters and specific (not vague like "Try more experiments").

    * Ensure `description` is 20-1000 characters and explains *why* this suggestion matters and
      *what* concrete action to take.

    * Assign `kind` from: `experiment`, `technique`, `evaluation`, `dataset`, `library`.

    * Assign `priority`: `high` for suggestions critical to project goals, `medium` for valuable but
      not urgent, `low` for nice-to-have.

    * Set `source_paper` to the paper ID if the suggestion stems from a specific paper, or `null`
      otherwise.

    * Assign `categories` from existing categories in `meta/categories/`.

16. Assign sequential IDs in format `S-XXXX-NN` where `XXXX` is the zero-padded `task_index` from
    `task.json` and `NN` starts at `01`.

### Phase 5: Write and Verify

17. Write `tasks/$TASK_ID/results/suggestions.json` following
    `arf/specifications/suggestions_specification.md`. The file must contain:

    ```json
    {
      "spec_version": "1",
      "suggestions": [...]
    }
    ```

18. Run the verificator:

    ```bash
    uv run python -u -m arf.scripts.verificators.verify_suggestions $TASK_ID
    ```

19. Fix all errors. Re-run until zero errors.

## Done When

* `tasks/$TASK_ID/results/suggestions.json` exists and follows the specification
* Verificator passes with zero errors
* Every suggestion has a specific, actionable title and description
* No suggestion duplicates an existing suggestion or an existing task's objective
* Each suggestion has valid `kind`, `priority`, `source_task`, and `categories`

## Forbidden

* NEVER run `prestep` or `poststep` — the orchestrator handles the step lifecycle

* NEVER commit — the orchestrator handles all commits

* NEVER modify `step_tracker.json` — the orchestrator manages step state

* NEVER write `step_log.md` — the orchestrator writes it after this skill completes

* NEVER generate suggestions before reading all available task context (research, results, logs).

* NEVER check existing suggestions before generating initial candidates — generate first,
  deduplicate second.

* NEVER fabricate paper IDs for `source_paper`. Verify the paper exists in the task's research files
  or use `null`.

* NEVER produce vague suggestions like "Investigate more" or "Try other approaches". Every
  suggestion must specify a concrete action.

* NEVER assign categories that do not exist in `meta/categories/`.

* NEVER skip the verificator step.
