---
name: "research-internet"
description: "Conduct structured internet research and write `research/research_internet.md`."
model: "claude-sonnet-4-6"
---
# Research Internet

**Version**: 4

## Goal

Conduct comprehensive internet research to extract all available human knowledge relevant to the
current task, discover new papers, add them to the project, and produce a structured
`research_internet.md`.

## Inputs

* `$TASK_ID` — the task folder name (e.g., `t0003_baseline_wsd_with_bert`)

## Context

Read before starting:

* `project/description.md` — project goals and scope (defines search boundaries)

* `tasks/$TASK_ID/task.json` — understand the task objective

* `tasks/$TASK_ID/research/research_papers.md` — identify gaps and context

* `arf/specifications/research_internet_specification.md` — authoritative format specification for
  `research_internet.md`

* `arf/styleguide/markdown_styleguide.md` — formatting rules (100-char lines, `*` bullets, heading
  hierarchy)

## Steps

### Phase 1: Define Research Scope

1. Read `tasks/$TASK_ID/task.json` and extract the task objective. If it contains
   `long_description_file`, also read the referenced markdown file.

2. Read `tasks/$TASK_ID/research/research_papers.md`. Extract:

   * Gaps from the Gaps and Limitations section
   * Key topics, methods, and open questions from Key Findings
   * Terminology and author names for targeted searches

3. Formulate two lists:

   * Gap-filling questions — one per gap from `research_papers.md`
   * Broadening questions — what else exists about this topic that the paper corpus does not cover?
     Think: recent advances, alternative approaches, practical implementations, community best
     practices, available tools/libraries, datasets, benchmarks, blog posts with reproducibility
     insights, and any non-academic knowledge

### Phase 2: Systematic Multi-Source Search

Execute a structured, multi-pass search strategy.

1. Define search parameters before searching:

   * Target sources: Google Scholar, Semantic Scholar, arXiv, ACL Anthology, GitHub, Hugging Face,
     Papers With Code, relevant blogs, documentation sites, Stack Overflow, Reddit, Twitter/X
     threads, conference workshops

   * Keywords with synonyms and Boolean operators

   * Date range and inclusion/exclusion criteria

   * Minimum 8 distinct search queries

2. Pass 1 — Gap-targeted queries using WebSearch:

   * One query per gap from Phase 1
   * Use specific terminology from the papers already reviewed

3. Pass 2 — Broadening queries using WebSearch:

   * Survey queries for the general topic (recent advances, state of the art)
   * Code/implementation queries (GitHub, model hubs, pip packages)
   * Practical experience queries (blog posts, tutorials, benchmarks)
   * Community discussion queries (forums, issue trackers)

4. Pass 3 — Snowball queries based on findings from passes 1-2:

   * Follow references mentioned in discovered sources
   * Search for specific authors, tools, or datasets uncovered
   * Check structured sources: Papers With Code leaderboards, Hugging Face model/dataset hubs,
     conference proceedings pages

5. Deep-read promising sources using WebFetch:

   * Read full content of the most relevant blog posts, documentation pages, and repository READMEs
   * Extract specific numbers, benchmarks, and implementation details
   * Note reliability of each source (peer-reviewed vs. not)

6. Record every query — exact text and source. Do not paraphrase.

### Phase 3: Identify and Add New Papers

**Deliverable-first rule**: Write `research/research_internet.md` including the
`## Discovered Papers` section. If context is running low, prioritize completing the research
document — the Discovered Papers section is enough for the orchestrator to add papers later.

List ALL relevant papers in the `## Discovered Papers` section — not just papers about the narrow
task topic, but any paper relevant to the broader project. A paper referenced in search results,
cited by other papers, or appearing in related work sections counts. If `research_papers.md` cites a
paper that is not yet in the corpus, list it. The goal is to grow the project's paper corpus
comprehensively.

1. Compile all papers encountered during search into the `## Discovered Papers` section of
   `research_internet.md` using the format from
   `arf/specifications/research_internet_specification.md`. Include:

   * Papers directly about the task topic
   * Foundational/seminal papers referenced by multiple sources
   * Papers cited in `research_papers.md` that are not yet in the corpus
   * Papers defining datasets, benchmarks, or evaluation frameworks used by the project
   * Recent papers that advance the state of the art in related areas

2. Run the paper aggregator to get existing papers with titles and DOIs:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_papers \
     --format json --detail short
   ```

3. Cross-reference discovered papers against the existing corpus by comparing DOIs, normalized
   titles (lowercase, stripped punctuation), and author+year combinations. Remove duplicates.

4. Write all new papers into the `## Discovered Papers` section of `research_internet.md`. Do NOT
   invoke `/add-paper` or `/download_paper`. The orchestrator handles paper addition after this
   skill completes.

### Phase 4: Synthesize and Write research_internet.md

1. Organize all findings by topic, not by source. Each topic becomes a `### ` subsection under
   `## Key Findings`.

2. For every gap from `research_papers.md`, determine resolution status: Resolved, Partially
   resolved, or Unresolved.

3. Write the full `research_internet.md` following the format in
   `arf/specifications/research_internet_specification.md`:

   * YAML frontmatter with all required fields

   * All 8 mandatory sections: Task Objective, Gaps Addressed, Search Strategy, Key Findings,
     Methodology Insights, Discovered Papers, Recommendations for This Task, Source Index

   * Additional sections wherever the task demands deeper treatment (e.g., Tool and Library
     Landscape, Benchmark Comparison, Implementation Patterns, Community Discussions, Dataset
     Availability)

4. Ensure every factual claim has an inline `[SourceKey]` citation.

5. Ensure every Source Index entry is cited at least once, and vice versa.

6. Distinguish peer-reviewed from non-peer-reviewed sources in the text.

7. Include specific numbers everywhere. Reject vague claims like "performs well" — replace with
   actual metrics.

8. Extract and explicitly state:

   * Hypotheses — testable claims emerging from the research
   * Best practices — community-converged approaches and pitfalls
   * Contradictions — where new findings disagree with existing papers

### Phase 5: Verify

1. Run the verificator:

   ```bash
   uv run python -u -m arf.scripts.verificators.verify_research_internet $TASK_ID
   ```

2. Fix all errors. Address warnings unless there is a documented reason to skip them.

3. Re-run until zero errors.

## Done When

* All discovered papers are listed in the `## Discovered Papers` section of `research_internet.md`
* `tasks/$TASK_ID/research/research_internet.md` exists and follows the specification
* Verificator passes with zero errors
* Every gap from `research_papers.md` has a resolution status
* At least 8 distinct search queries are documented in Search Strategy
* Research covers both gap-filling AND broad topic exploration
* Every inline `[SourceKey]` has a Source Index entry and vice versa

## Forbidden

* NEVER run `prestep` or `poststep` — the orchestrator handles the step lifecycle

* NEVER commit — the orchestrator handles all commits

* NEVER modify `step_tracker.json` — the orchestrator manages step state

* NEVER write `step_log.md` — the orchestrator writes it after this skill completes

* NEVER fabricate sources, URLs, or metrics. If a search yields nothing, say so.

* NEVER paraphrase search queries — record the exact text used.

* NEVER skip the gap analysis from `research_papers.md`.

* NEVER cite non-peer-reviewed sources without noting their reliability.

* NEVER add papers without checking the aggregator for duplicates first.

* NEVER invoke `/add-paper` or `/download_paper` — paper addition is the orchestrator's
  responsibility

* NEVER skip listing a paper just because it is not "about" the narrow task topic. If a paper is
  relevant to the project's research area, list it in Discovered Papers.

* NEVER claim "no new papers to list" without verifying that every paper cited in
  `research_papers.md` and every paper encountered in search results already exists in the corpus.
