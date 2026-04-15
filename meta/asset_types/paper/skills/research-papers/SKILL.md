---
name: "research-papers"
description: "Review downloaded papers and write `research/research_papers.md`."
model: "claude-sonnet-4-6"
---
# Research Papers

**Version**: 2

## Goal

Review already-downloaded papers relevant to the current task and produce a structured
`research_papers.md` that synthesizes findings by topic with inline citations.

## Inputs

* `$TASK_ID` — the task folder name (e.g., `t0003_baseline_wsd_with_bert`)

## Context

Read before starting:

* `project/description.md` — project goals and research questions (guides relevance assessment)

* `tasks/$TASK_ID/task.json` — understand the task objective

* `arf/specifications/research_papers_specification.md` — authoritative format specification for
  `research_papers.md`

* `arf/styleguide/markdown_styleguide.md` — formatting rules (100-char lines, `*` bullets, heading
  hierarchy)

## Steps

### Phase 1: Understand the Task

1. Read `tasks/$TASK_ID/task.json` and extract the task objective, description, and dependencies. If
   it contains `long_description_file`, also read the referenced markdown file.

2. Note any specific methods, datasets, or approaches mentioned — these guide category selection and
   paper relevance assessment.

### Phase 2: Select Categories

1. List all available categories using the aggregator:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_categories --format json
   ```

2. For each category, assess whether its papers are likely relevant to the task objective. Select
   categories whose descriptions overlap with the task's methods, data, evaluation approach, or
   research area.

3. Document reasoning for included and excluded categories — this becomes the Category Selection
   Rationale section.

### Phase 3: Discover Papers

1. Run the paper aggregator filtered by the selected categories to get short summaries:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_papers \
     --format json --detail short --categories <cat1> <cat2> ...
   ```

2. Also run without category filter to catch cross-category papers that might be relevant:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_papers \
     --format json --detail short
   ```

3. From both results, identify papers whose titles, venues, and categories suggest relevance to the
   task. Compile a list of paper IDs to read in detail.

### Phase 4: Read Paper Summaries and Full Papers

1. For the most relevant papers, retrieve full summaries via the aggregator:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_papers \
     --format json --detail full --include-full-summary \
     --ids <paper_id_1> <paper_id_2> ...
   ```

2. Read each summary carefully. Extract:

   * Key results with specific numbers (F1 scores, accuracy, effect sizes)
   * Methods, architectures, hyperparameters
   * Datasets used and their properties
   * Claimed contributions and limitations
   * Hypotheses and best practices

3. If a summary lacks critical details needed for the task (e.g., specific hyperparameter values,
   training procedures, implementation details, ablation results), read the actual paper file
   directly:

   ```text
   tasks/<source_task_id>/assets/paper/<paper_id>/files/<filename>.pdf
   ```

   or the markdown conversion if available:

   ```text
   tasks/<source_task_id>/assets/paper/<paper_id>/files/<filename>.md
   ```

   The source task ID is available in the `added_by_task` field from the aggregator output.

4. Track which papers were reviewed (including those ultimately not cited) and which were cited —
   these counts go into the YAML frontmatter.

### Phase 5: Synthesize and Write research_papers.md

1. Organize findings by topic, not by paper. Each topic becomes a `### ` subsection under
   `## Key Findings`. This is critical — by-topic organization forces synthesis across papers.
   Per-paper summaries are not acceptable.

2. Write the full `research_papers.md` at `tasks/$TASK_ID/research/research_papers.md` following
   `arf/specifications/research_papers_specification.md`:

   * YAML frontmatter with all required fields (`task_id`, `research_stage`, `papers_reviewed`,
     `papers_cited`, `categories_consulted`, `date_completed`, `status`)

   * All 7 mandatory sections: Task Objective, Category Selection Rationale, Key Findings,
     Methodology Insights, Gaps and Limitations, Recommendations for This Task, Paper Index

   * Additional sections wherever the task demands deeper treatment (e.g., Benchmark Comparison,
     Dataset Landscape, Historical Context)

3. Ensure every factual claim has an inline `[CitationKey]` citation.

4. Ensure every Paper Index entry is cited at least once in the body, and every inline citation has
   a matching Paper Index entry.

5. Include specific numbers everywhere — accuracy scores, F1, effect sizes, hyperparameter values,
   dataset sizes. Reject vague claims like "performs well" or "significantly outperforms." For every
   metric value cited as a reproduction target or baseline, record the exact table/figure number and
   page from the source paper (e.g., `[AuthorYear, Table 3, p. 7]`). Always specify whether a metric
   comes from a dev/validation set or a test set. If a dataset is used for model selection or early
   stopping, label it as "dev set" — do not include it in test-set comparison tables. If the exact
   number cannot be located in the paper, write "not found in paper" — never estimate or infer
   metric values.

6. Extract and explicitly state:

   * Hypotheses — testable claims emerging from the literature
   * Best practices — community-converged approaches, proven configurations, common pitfalls
   * Contradictions — where papers disagree with each other

7. Paper Index entries must include all required fields: Title, Authors, Year, DOI, Asset,
   Categories, Relevance.

### Phase 6: Verify

1. Run the verificator:

   ```bash
   uv run python -u -m arf.scripts.verificators.verify_research_papers $TASK_ID
   ```

2. Fix all errors. Address warnings unless there is a documented reason to skip them.

3. Re-run until zero errors.

## Done When

* `tasks/$TASK_ID/research/research_papers.md` exists and follows the specification
* Verificator passes with zero errors
* Every inline `[CitationKey]` has a Paper Index entry and vice versa
* Key Findings are organized by topic with `### ` subsections (not by paper)
* At least 1 paper is cited (or `status` is `"partial"` with explanation in Task Objective)
* All Paper Index entries include the DOI field
* Specific numbers are present for all quantitative claims

## Forbidden

* NEVER run `prestep` or `poststep` — the orchestrator handles the step lifecycle

* NEVER commit — the orchestrator handles all commits

* NEVER modify `step_tracker.json` — the orchestrator manages step state

* NEVER write `step_log.md` — the orchestrator writes it after this skill completes

* NEVER fabricate citations, paper titles, DOIs, or metrics. If a paper does not report a specific
  number, say so explicitly.

* NEVER organize Key Findings by paper — synthesize across papers by topic.

* NEVER use vague claims ("performs well", "significantly better") without specific numbers.

* NEVER skip reading paper summaries before citing a paper. Read first, cite second.

* NEVER include a paper in the Paper Index without citing it in the body text.

* NEVER omit the DOI field from Paper Index entries.

* NEVER cite a metric value without specifying its source table, figure, or page in the paper.

* NEVER mix dev-set and test-set metrics in the same comparison without explicit labels.

* NEVER claim "no relevant papers found" without having run the aggregator both with and without
  category filters.

* NEVER copy paper abstracts as Key Findings. Synthesize across multiple papers to produce
  cross-cutting themes.
