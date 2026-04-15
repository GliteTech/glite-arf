---
name: "compare-literature"
description: "Compare task results against published literature and write the comparison output."
---
# Compare Literature

**Version**: 4

## Goal

Compare task results against published results from the literature and write
`results/compare_literature.md` following the specification.

## Inputs

* `$TASK_ID` — the task folder name (e.g., `t0019_mfs_baseline_raganato`)

## Context

Read before starting:

* `arf/specifications/compare_literature_specification.md` — authoritative format for
  `results/compare_literature.md`

* `tasks/$TASK_ID/task.json` — task objective, description, expected assets

* `tasks/$TASK_ID/results/metrics.json` — quantitative results; this may be a legacy flat metrics
  object or an explicit multi-variant file

* `tasks/$TASK_ID/results/results_detailed.md` — methodology and detailed numbers

* `tasks/$TASK_ID/results/results_summary.md` — headline metrics

## Steps

### Phase 1: Gather Task Context

1. Read `tasks/$TASK_ID/task.json` to understand the task objective and scope. If it contains
   `long_description_file`, also read the referenced markdown file.

2. Read `tasks/$TASK_ID/results/metrics.json` for quantitative results.

   * If the file uses explicit variants, list all variants and their dimensions first.
   * Do not assume the task has one canonical structured metrics block. Choose the relevant variant
     or variants for each literature comparison row based on the compared conditions.

3. Read `tasks/$TASK_ID/results/results_detailed.md` for methodology and detailed numbers.

4. Read `tasks/$TASK_ID/results/results_summary.md` for headline metrics.

5. Read all available research files (skip any that do not exist):

   * `tasks/$TASK_ID/research/research_papers.md`
   * `tasks/$TASK_ID/research/research_internet.md`
   * `tasks/$TASK_ID/research/research_code.md`

6. Scan step logs in `tasks/$TASK_ID/logs/steps/` for implementation details that affect
   comparability (e.g., preprocessing choices, model configuration).

### Phase 2: Identify Published Results

7. From the research files, extract published performance numbers relevant to this task's metrics.

8. Identify the specific metrics reported (F1, accuracy, etc.) and the evaluation conditions (test
   set, preprocessing, model size).

9. Note which papers report results on the same datasets and metrics as this task.

10. List at least 2 comparable published results. If fewer than 2 exist in the research files, state
    this explicitly in the Limitations section.

### Phase 3: Build Comparison Table

11. For each published result, record: Method / Paper, Metric, Published Value, Our Value, Delta,
    Notes.

    * If your task has multiple variants, include the variant label or dimensions in the method name
      or Notes column so the comparison is unambiguous.

12. Compute deltas as Our Value minus Published Value (positive means this task outperforms the
    published result).

13. Flag any non-comparable conditions in the Notes column (e.g., "different test split", "few-shot
    vs zero-shot", "different training data").

14. Include at least 2 data rows in the comparison table.

### Phase 4: Analyze and Write

15. Write `tasks/$TASK_ID/results/compare_literature.md` with all mandatory sections per the
    specification:

    * `## Summary` — 2-4 sentences: what was compared, headline finding

    * `## Comparison Table` — the comparison table from Phase 3

    * `## Methodology Differences` — bullet list of key differences between this task and the
      published methods

    * `## Analysis` — interpret the comparison honestly: explain gaps, note agreements, highlight
      surprising results

    * `## Limitations` — note missing references, different conditions, or non-comparable metrics

16. Include YAML frontmatter with `spec_version`, `task_id`, and `date_compared` (today's date in
    ISO 8601 format).

17. Use citation keys (e.g., `Raganato2017`) when referencing published results. Verify each
    citation key exists in the research files. Every published metric value in the comparison table
    must cite the specific table, figure, or page from the source paper. Use format:
    `[AuthorYear, Table N]` or `[AuthorYear, p. N]`. If a value cannot be traced to a specific table
    in a specific paper, omit it rather than estimating.

18. Use `**bold**` for specific quantitative values.

19. When the plan cites specific results from prior project tasks as motivation or baselines,
    include a `### Prior Task Comparison` subsection. Compare the current task's results against
    those cited values. If results contradict prior-task conclusions, highlight this as a finding —
    it is just as important as the literature comparison.

### Phase 5: Verify

20. Run the verificator:

    ```bash
    uv run python -u -m arf.scripts.verificators.verify_compare_literature \
      $TASK_ID
    ```

21. Fix all errors. Re-run until zero errors.

## Done When

* `tasks/$TASK_ID/results/compare_literature.md` exists and follows the specification
* Verificator passes with zero errors
* At least 2 published results compared with specific numbers
* Methodology differences documented for each comparison
* Analysis is honest — negative results (where this task underperforms) are not omitted

## Forbidden

* NEVER run `prestep` or `poststep` — the orchestrator handles the step lifecycle

* NEVER commit — the orchestrator handles all commits

* NEVER modify `step_tracker.json` — the orchestrator manages step state

* NEVER write `step_log.md` — the orchestrator writes it after this skill completes

* NEVER fabricate published numbers. Every published value must come from a paper in the research
  files. If a number cannot be verified, omit it and note this in Limitations.

* NEVER omit negative results. If this task underperforms a published result, report the delta
  honestly and explain possible causes.

* NEVER compare against published results without noting condition differences in the Notes column
  or Methodology Differences section.

* NEVER use vague qualifiers ("similar", "comparable", "competitive") in place of specific numbers.

* NEVER skip the verificator step.

* NEVER cite a published metric without specifying the exact table, figure, or page number.
