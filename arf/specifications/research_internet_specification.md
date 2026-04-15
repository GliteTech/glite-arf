# Research Internet Specification

**Version**: 1

## Purpose

This specification defines the format, structure, and quality requirements for the
`research_internet.md` file produced during the "research in internet and papers not yet found" task
stage.

**Producer**: The internet-research subagent, which searches the web for relevant papers, blog
posts, code repositories, datasets, and other resources not yet catalogued in the project.

**Consumers**:
* **Planning subagent** — uses findings to inform the task plan
* **Paper-downloading subagent** — uses the Discovered Papers section to know which new papers to
  download and catalogue
* **Human reviewers** — evaluate whether the search was thorough and unbiased
* **Verificator** — validates structure, cross-references, and minimum depth programmatically

## Relationship to `research_papers.md`

This file is produced **after** `research_papers.md`. Its primary job is to fill gaps identified
there and to find knowledge that doesn't yet exist in the project's paper corpus. The Gaps Addressed
section must explicitly reference the gaps from `research_papers.md` and state whether each gap was
resolved, partially resolved, or remains open.

## File Location

```text
tasks/<task_id>/research/research_internet.md
```

## Format

The file is a Markdown document with YAML frontmatter. All content is UTF-8 encoded.

## YAML Frontmatter

The file must begin with a YAML frontmatter block containing the following required fields:

```yaml
---
spec_version: "1"
task_id: "0015-cohort-discrimination-analysis"
research_stage: "internet"
searches_conducted: 8
sources_cited: 12
papers_discovered: 3
date_completed: "2026-03-29"
status: "complete"
---
```

| Field | Type | Description |
| --- | --- | --- |
| `spec_version` | string | Always `"1"` for this version |
| `task_id` | string | Must exactly match the task folder name |
| `research_stage` | string | Always `"internet"` for this file |
| `searches_conducted` | int | Number of distinct search queries executed |
| `sources_cited` | int | Total sources referenced in the body (papers, blogs, repos, docs, etc.) |
| `papers_discovered` | int | New papers found that should be downloaded and added as paper assets (0 is valid) |
| `date_completed` | string | ISO 8601 date (YYYY-MM-DD) |
| `status` | string | `"complete"` or `"partial"` (see below) |

If `status` is `"partial"`, the Task Objective section must explain why (e.g., search APIs were
unavailable, or the topic is too novel for published work).

## Mandatory Sections

The document must contain at least these eight sections in this order, each as an `## ` heading. The
mandatory sections define the minimum structure — authors are encouraged to add additional `## `
sections wherever they would improve clarity (e.g., `## Tool and Library Landscape`,
`## Community Discussions`, `## Benchmark Comparison`, `## Implementation Patterns`). Task-specific
and project-specific sections are expected; the research should be as thorough and detailed as the
topic demands.

* * *

### `## Task Objective`

**Minimum**: 30 words

Restate what this task aims to accomplish. Same purpose as in `research_papers.md` — makes the file
self-contained for human review.

* * *

### `## Gaps Addressed`

**Minimum**: 50 words

Explicitly list each gap from the `research_papers.md` Gaps and Limitations section and state its
resolution status. This creates a traceable chain between the two research stages.

Each gap should be marked with one of:
* **Resolved** — internet research found sufficient information
* **Partially resolved** — some information found but questions remain
* **Unresolved** — no relevant information found despite searching

* * *

### `## Search Strategy`

**Minimum**: 100 words

Document the search process so that humans can assess thoroughness and reproducibility. This section
must include:

* **Databases and sources searched** — e.g., Google Scholar, Semantic Scholar, arXiv, ACL Anthology,
  GitHub, specific blogs or documentation sites
* **Search queries used** — list the actual queries, not paraphrases
* **Date range** — what publication years were targeted
* **Inclusion/exclusion criteria** — what made a source relevant or irrelevant
* **Search iterations** — if initial queries led to refined follow-up searches, document the
  progression

* * *

### `## Key Findings`

**Minimum**: 200 words

Synthesized findings organized **by topic, not by source**. Each topic is a `### ` subsection with
inline citations.

This section should focus on **new information** not available from the existing paper corpus. Avoid
repeating what `research_papers.md` already covers — instead, extend, update, or contradict it.

Requirements:
* At least one `### ` subsection
* Every factual claim must have an inline citation `[SourceKey]`
* Clearly indicate when a finding updates or contradicts something from `research_papers.md`
* Distinguish between peer-reviewed and non-peer-reviewed sources
* Extract **hypotheses** — testable claims or conjectures emerging from the research that this task
  or future tasks could validate
* Identify **best practices** — established patterns, conventions, or approaches that the community
  converges on
* Include **specific numbers** — accuracy scores, benchmarks, timings, resource requirements. Vague
  claims without numbers are unacceptable.

* * *

### `## Methodology Insights`

**Minimum**: 100 words

Actionable techniques discovered through internet research. This section is prescriptive — it tells
the planning and execution stages what to do.

Pay special attention to:
* **Best practices** — established approaches the community converges on, common pitfalls to avoid,
  proven configurations
* **Hypotheses** — testable conjectures that emerge from the research; state them explicitly so the
  planning stage can decide whether to test them
* Implementation details from code repositories and documentation
* Practical tips from blog posts and tutorials (with source reliability noted)
* Configuration details, hyperparameters, or tricks not found in papers
* Available pretrained models, datasets, or tools discovered during search

* * *

### `## Discovered Papers`

**Minimum**: 0 words (section heading required even if empty)

List all papers found during internet research that should be downloaded and added to the project's
paper corpus. These are papers that were not already catalogued but are relevant to this or future
tasks.

Each entry must include enough information for the paper-downloading subagent to find and process
it:

| Field | Required | Description |
| --- | --- | --- |
| Title | yes | Full paper title |
| Authors | yes | First author et al. acceptable for 3+ authors |
| Year | yes | Publication year |
| DOI | if available | Canonical identifier |
| URL | yes | Direct link to the paper |
| Suggested categories | yes | Category slugs to assign |
| Why download | yes | 1-2 sentences on why this paper is worth adding |

If no new papers were discovered, state this explicitly with reasoning.

* * *

### `## Recommendations for This Task`

**Minimum**: 50 words

Concrete, prioritized recommendations that combine insights from internet research. Where internet
findings update or contradict recommendations from `research_papers.md`, note the change explicitly.

* * *

### `## Source Index`

A structured reference list of all sources cited in the document. The number of entries must equal
`sources_cited` in the frontmatter.

Sources are more diverse than in `research_papers.md` — they may include papers, blog posts, GitHub
repositories, documentation pages, dataset cards, or forum discussions. Each source type has
slightly different required fields.

#### Paper sources

| Field | Required | Description |
| --- | --- | --- |
| Type | yes | `paper` |
| Title | yes | Full paper title |
| Authors | yes | First author et al. for 3+ authors |
| Year | yes | Publication year |
| DOI | if known | Canonical identifier |
| URL | yes | Direct link to the paper |
| Peer-reviewed | yes | `yes` or `no` |
| Relevance | yes | 1-2 sentences on why this matters for THIS task |

#### Non-paper sources (blog posts, repos, docs, datasets)

| Field | Required | Description |
| --- | --- | --- |
| Type | yes | `blog`, `repository`, `documentation`, `dataset`, `forum` |
| Title | yes | Title or name |
| Author/Org | yes | Author name or organization |
| Date | yes | ISO date or YYYY-MM |
| URL | yes | Direct link |
| Last updated | if available | For repos/docs that change over time |
| Peer-reviewed | yes | `yes` or `no` |
| Relevance | yes | 1-2 sentences on why this matters for THIS task |

## Additional Sections

Beyond the mandatory sections above, authors should add any sections that help communicate the
research thoroughly. Common useful additions include:

* `## Tool and Library Landscape` — available implementations, frameworks, pretrained models
* `## Community Discussions` — insights from forums, issue trackers, Twitter/X threads
* `## Benchmark Comparison` — table comparing published and newly found results
* `## Implementation Patterns` — code patterns and architectural choices seen across repositories
* `## Dataset Availability` — newly found datasets, their sizes, licenses, access requirements
* `## Cost and Resource Analysis` — compute requirements, API costs, hardware needs found in
  practice
* Any other task-specific section the author deems valuable

The verificator only checks for mandatory sections. Additional sections are never penalized and are
strongly encouraged.

## Citation Format

Use `[SourceKey]` for inline references. Source keys follow these patterns:
* Papers: `[FirstAuthorLastNameYear]` — e.g., `[Navigli2009]`
* Blog posts: `[OrgOrAuthor-Topic-Year]` — e.g., `[HF-WSD-2024]`
* Repositories: `[ShortName-GH]` — e.g., `[mirt-GH]`
* Datasets: `[DatasetName-Year]` — e.g., `[SemCor-2017]`

Rules:
* Every `[SourceKey]` in the body must have a matching entry in Source Index
* Every Source Index entry should be cited at least once in the body
* When citing non-peer-reviewed sources, note this in the text on first use (e.g., "a blog post by
  ETS Research [ETS-IRT-2024] reports...")

## Quality Criteria

### What makes a good `research_internet.md`

* Search strategy is specific and reproducible — actual queries listed, not vague descriptions like
  "searched for relevant papers"
* Every gap from `research_papers.md` is explicitly addressed with a resolution status
* Findings include specific numbers, benchmarks, and concrete details
* Findings clearly distinguish peer-reviewed from non-peer-reviewed sources
* Hypotheses are explicitly stated as testable propositions
* Best practices are identified where community consensus exists
* New papers are identified for download with enough metadata to find them
* Recommendations update or extend `research_papers.md` recommendations rather than repeating them
* Additional sections are added wherever the task demands deeper treatment
* The document is detailed enough that a researcher reading only this file and `research_papers.md`
  has a comprehensive understanding of the state of the art

### What makes a bad `research_internet.md`

* Search strategy is vague ("searched Google Scholar for relevant papers")
* Gaps from `research_papers.md` are ignored or not cross-referenced
* Non-peer-reviewed sources cited without noting their reliability
* Numbers missing — "performs well" without actual metrics
* No new papers discovered despite obvious gaps in the corpus
* Findings repeat `research_papers.md` content without adding new information
* Source URLs are broken or point to paywalled content without noting access requirements
* Too short — a research document that could have been an email
* No additional sections even when the task clearly warrants them

## Verificator Rules

The verificator produces errors (E) that block the pipeline, and warnings (W) that are logged but do
not halt execution. Agents should have VERY serious reasons to continue if there are errors.

### Errors

| Code | Check |
| --- | --- |
| `RI-E001` | File does not exist at `tasks/<task_id>/research/research_internet.md` |
| `RI-E002` | YAML frontmatter is missing or not parseable |
| `RI-E003` | `task_id` in frontmatter does not match the task folder name |
| `RI-E004` | One or more mandatory sections is missing (see list below) |
| `RI-E005` | `sources_cited` < 1 and `status` is not `"partial"` |
| `RI-E006` | An inline `[SourceKey]` has no matching entry in Source Index |
| `RI-E007` | Source Index entry count != `sources_cited` in frontmatter |
| `RI-E008` | A Source Index entry is missing the URL field |
| `RI-E009` | Total content (excluding frontmatter) is fewer than 400 words |
| `RI-E010` | `## Gaps Addressed` section does not reference `research_papers.md` |
| `RI-E011` | `spec_version` is missing from frontmatter |

The mandatory sections checked by `RI-E004` are: `## Task Objective`, `## Gaps Addressed`,
`## Search Strategy`, `## Key Findings`, `## Methodology Insights`, `## Discovered Papers`,
`## Recommendations for This Task`, `## Source Index`.

### Warnings

| Code | Check |
| --- | --- |
| `RI-W001` | A mandatory section is below its minimum word count |
| `RI-W002` | `## Search Strategy` lists fewer than 3 search queries |
| `RI-W003` | `## Key Findings` section contains no `### ` subsections |
| `RI-W004` | A Source Index entry is missing the `Peer-reviewed` field |
| `RI-W005` | A Source Index entry is never cited in the body text |
| `RI-W006` | `papers_discovered` > 0 but `## Discovered Papers` section has no entries (or vice versa) |
| `RI-W007` | `searches_conducted` in frontmatter does not match the number of queries listed in `## Search Strategy` |

## Complete Example

```markdown
---
spec_version: "1"
task_id: "0015-cohort-discrimination-analysis"
research_stage: "internet"
searches_conducted: 10
sources_cited: 9
papers_discovered: 2
date_completed: "2026-03-28"
status: "complete"
---

## Task Objective

Analyze how well different vocabulary test versions discriminate between
known-groups cohorts (native speakers, high-proficiency learners,
low-proficiency learners). The goal is to compute Cohen's d effect sizes
and IRT-based discrimination indices for each test version, identifying
which item formats and scoring methods produce the strongest group
separation. This informs future item selection and test design.

## Gaps Addressed

From `research_papers.md` Gaps and Limitations:

1. **Open-source IRT implementations for yes/no vocabulary tests** —
   **Resolved**. Found the R `mirt` package [mirt-GH] and the Python
   `py-irt` library [PyIRT-GH] which both support 2PL and 3PL models
   suitable for binary response data. The `mirt` package has over 2,500
   citations and supports multidimensional models. `py-irt` is newer but
   integrates with NumPy/pandas workflows used in this project.

2. **Benchmarks for Cohen's d in language testing** — **Resolved**. A
   Shiken Research Bulletin post (not peer-reviewed) [Shiken-2024]
   compiled effect sizes from 14 published vocabulary test validation
   studies. Typical native-vs-L2 Cohen's d values range from **1.2 to
   2.8** depending on test format. Yes/no checklist formats with nonword
   foils achieve **d = 1.8-2.4**, while multiple-choice formats achieve
   **d = 1.4-1.9**.

3. **Signal Detection Theory applied to yes/no vocabulary tests** —
   **Partially resolved**. Found [Huibregtse2002] which applies SDT
   (d-prime, response bias *c*) to yes/no vocabulary tests and shows
   that SDT-corrected scores correlate **r = 0.92** with independent
   proficiency measures, vs. **r = 0.81** for raw hit rates. However,
   no paper applies SDT metrics to IRT-based item selection.

4. **False alarm rates by proficiency level** — **Unresolved**. No
   source provides false alarm rate distributions stratified by
   proficiency tier. This remains an empirical gap our task must fill.

## Search Strategy

**Sources searched**: Google Scholar, Semantic Scholar API, ERIC
database, ResearchGate, GitHub code search, CRAN package repository,
PyPI, Language Testing journal archive.

**Queries executed** (10 total):

*Initial queries (targeting gaps directly):*
1. `"yes/no vocabulary test" IRT "item response theory" discrimination`
2. `Cohen's d vocabulary test "known groups" native L2 benchmark`
3. `signal detection theory vocabulary assessment d-prime false alarm`
4. `mirt R package binary response IRT 2PL tutorial`
5. `python IRT library vocabulary test item analysis`

*Follow-up queries (prompted by initial findings):*
6. `Huibregtse SDT vocabulary checklist scoring correction`
7. `"py-irt" python item response theory documentation`
8. `vocabulary size test nonword false alarm proficiency`
9. `Rasch model yes-no vocabulary test item difficulty`
10. `language testing effect size benchmarks meta-analysis`

**Date range**: 2000-2026. For foundational IRT references, no date
restriction.

**Inclusion criteria**: Must provide at least one of: (a) IRT or CTT
analysis of yes/no vocabulary tests, (b) effect size benchmarks for
language test discrimination, (c) implementation code for IRT or SDT
analysis, (d) false alarm analysis in vocabulary assessment. Excluded:
non-English vocabulary tests, listening/speaking assessments, studies
without quantitative results.

**Search iterations**: Queries 6-9 were follow-ups. Query 6 was prompted
by discovering [Huibregtse2002] in initial results. Query 7 was triggered
by finding py-irt mentioned in a Stack Overflow answer.

## Key Findings

### IRT 2PL Models Are Standard for Yes/No Vocabulary Items

Multiple sources confirm that the two-parameter logistic (2PL) IRT model
is the standard for yes/no vocabulary checklist items. A tutorial by
ETS (not peer-reviewed) [ETS-IRT-2024] explains that 2PL is preferred
over 1PL (Rasch) because item discrimination varies substantially across
vocabulary items — high-frequency words have low discrimination (everyone
knows them) while mid-frequency words discriminate well between
proficiency levels.

[Beglar2010] calibrated 158 yes/no vocabulary items using 2PL and found
discrimination parameters ranging from **a = 0.4** (low-frequency
technical terms) to **a = 2.8** (mid-frequency academic vocabulary). The
median discrimination was **a = 1.3**, which is considered "moderate to
high" in IRT conventions. Items with **a < 0.5** should be flagged for
removal or replacement.

**Best practice**: Use 2PL, not Rasch, for yes/no vocabulary tests.
Items with discrimination below **a = 0.5** are likely poor items
regardless of their difficulty level.

### SDT Corrections Significantly Improve Validity

[Huibregtse2002] demonstrated that raw hit rates overestimate vocabulary
knowledge for respondents who guess liberally (low response threshold).
SDT-corrected scores using d-prime (d') adjust for response bias:

| Scoring method    | Correlation with TOEFL | Correlation with C-test |
|-------------------|------------------------|-------------------------|
| Raw hits          | 0.81                   | 0.76                    |
| Hits minus FAs    | 0.87                   | 0.83                    |
| d-prime (SDT)     | 0.92                   | 0.89                    |
| IRT theta         | 0.93                   | 0.91                    |

SDT d-prime achieves near-IRT validity with much simpler computation.
The **hits-minus-false-alarms** method is a rough but useful approximation
when full SDT calibration is impractical.

**Hypothesis**: If SDT d-prime and IRT theta correlate strongly with
external measures but differ on individual examinees, the disagreement
cases may reveal examinees with extreme response biases. Comparing the
two scoring methods per examinee could identify test-takers who benefit
most from SDT correction.

### Effect Size Benchmarks for Vocabulary Test Validation

A compilation by [Shiken-2024] and cross-referenced with [Beglar2010]:

| Comparison                  | Format         | Typical Cohen's d |
|-----------------------------|----------------|-------------------|
| Native vs. low-proficiency  | Yes/No + foils | 2.0 - 2.8        |
| Native vs. mid-proficiency  | Yes/No + foils | 1.2 - 1.8        |
| High vs. low proficiency    | Yes/No + foils | 1.4 - 2.2        |
| Native vs. low-proficiency  | Multiple choice| 1.4 - 1.9        |
| High vs. low proficiency    | Multiple choice| 0.9 - 1.5        |

Yes/no formats with nonword foils consistently produce **higher effect
sizes** than multiple-choice formats for the same cohort comparisons.
This is because yes/no tests can include more items in the same time
(~200 items in 10 minutes vs. ~40 multiple-choice items).

**Best practice**: For our analysis, any test version with native vs.
low-proficiency Cohen's d below **1.5** should be flagged as having
weak discrimination power.

## Methodology Insights

* **IRT software**: Use the `mirt` R package (v1.41+) for 2PL
  calibration [mirt-GH]. It handles binary response matrices natively
  and supports parallel processing for large datasets. For Python
  integration, export results as CSV and load into pandas.

* **SDT computation**: Compute d-prime as `Z(hit_rate) - Z(false_alarm_rate)`
  where Z is the inverse normal CDF. Apply the standard correction of
  adding 0.5 to all cells when hit rate = 1.0 or FA rate = 0.0 to avoid
  infinite values [Huibregtse2002].

* **Effect size**: Compute Cohen's d with pooled standard deviation. Use
  the Welch correction for unequal group sizes. Report 95% confidence
  intervals [Shiken-2024].

* **Sample size**: For stable 2PL estimates, [Beglar2010] recommends at
  least **200 respondents per group** and **100+ items**. Below 200,
  discrimination parameter estimates become unreliable.

* **Best practice — reporting**: Report per-item discrimination (a),
  per-item difficulty (b), test-level Cohen's d, and SDT d-prime. Present
  discrimination distributions as histograms, not just means.

* **Hypothesis to test**: Items that appear in context sentences (not
  isolated) may have different discrimination profiles than isolated
  items. This interaction between item format and IRT discrimination has
  not been explored in the reviewed literature.

## Discovered Papers

### [Huibregtse2002]
* **Title**: Effects of Merging Different Measures of Receptive Vocabulary
  on the Validity of the Yes/No Test
* **Authors**: Huibregtse, I., Admiraal, W., Meara, P.
* **Year**: 2002
* **DOI**: `10.1191/0265532202lt233oa`
* **URL**: https://journals.sagepub.com/doi/10.1191/0265532202lt233oa
* **Suggested categories**: `psychometrics`, `vocabulary-assessment`
* **Why download**: Foundational paper applying SDT to yes/no vocabulary
  tests with detailed validity correlations. Directly applicable to our
  scoring methodology.

### [Beglar2010]
* **Title**: A Rasch-based validation of the Vocabulary Size Test
* **Authors**: Beglar, D.
* **Year**: 2010
* **DOI**: `10.1177/0265532209340194`
* **URL**: https://journals.sagepub.com/doi/10.1177/0265532209340194
* **Suggested categories**: `psychometrics`, `item-response-theory`
* **Why download**: Large-scale IRT calibration of vocabulary items with
  detailed discrimination statistics. Provides benchmarks for item quality
  thresholds.

## Recommendations for This Task

1. **Use 2PL IRT model via `mirt`** — standard for binary vocabulary
   items. Export item parameters for Python analysis. This updates
   `research_papers.md` which did not specify a software tool.

2. **Apply SDT d-prime correction** — achieves **r = 0.92** correlation
   with external proficiency [Huibregtse2002]. Compute for all test
   versions as an alternative to raw hit rates.

3. **Flag items with discrimination a < 0.5** — these contribute little
   to group separation [Beglar2010].

4. **Flag test versions with native-vs-low d < 1.5** — below the
   typical range for yes/no formats [Shiken-2024].

5. **Download [Huibregtse2002] and [Beglar2010]** — both directly address
   methodology gaps from `research_papers.md`.

6. **Report per-item discrimination histograms** — fill the gap in our
   understanding of item quality distributions across test versions.

## Source Index

### [ETS-IRT-2024]
* **Type**: blog
* **Title**: Choosing IRT Models for Binary Language Test Items
* **Author/Org**: ETS Research
* **Date**: 2024-03-10
* **URL**: https://www.ets.org/research/irt-binary-items
* **Peer-reviewed**: no
* **Relevance**: Practical guide for selecting 2PL vs. Rasch for
  vocabulary tests. Explains when discrimination parameters are worth
  estimating and provides interpretive benchmarks for item parameters.

### [Huibregtse2002]
* **Type**: paper
* **Title**: Effects of Merging Different Measures of Receptive Vocabulary
  on the Validity of the Yes/No Test
* **Authors**: Huibregtse, I., Admiraal, W., Meara, P.
* **Year**: 2002
* **DOI**: `10.1191/0265532202lt233oa`
* **URL**: https://journals.sagepub.com/doi/10.1191/0265532202lt233oa
* **Peer-reviewed**: yes (Language Testing)
* **Relevance**: Foundational SDT analysis of yes/no vocabulary tests.
  d-prime scoring achieves r = 0.92 with TOEFL, establishing SDT as the
  gold-standard correction for guessing bias.

### [Beglar2010]
* **Type**: paper
* **Title**: A Rasch-based validation of the Vocabulary Size Test
* **Authors**: Beglar, D.
* **Year**: 2010
* **DOI**: `10.1177/0265532209340194`
* **URL**: https://journals.sagepub.com/doi/10.1177/0265532209340194
* **Peer-reviewed**: yes (Language Testing)
* **Relevance**: IRT calibration of 158 vocabulary items with
  discrimination range a = 0.4-2.8. Provides item quality thresholds and
  sample size recommendations directly applicable to our analysis.

### [mirt-GH]
* **Type**: repository
* **Title**: mirt — Multidimensional Item Response Theory
* **Author/Org**: Chalmers, R. P.
* **URL**: https://github.com/philchalmers/mirt
* **Last updated**: 2024-06
* **Peer-reviewed**: no (accompanies peer-reviewed CRAN package)
* **Relevance**: R package for 2PL/3PL IRT calibration with 2,500+
  citations. Handles binary response matrices, parallel processing,
  and model comparison. Use for item parameter estimation.

### [PyIRT-GH]
* **Type**: repository
* **Title**: py-irt — Python Item Response Theory
* **Author/Org**: Educational Testing Research Lab
* **URL**: https://github.com/nd-ball/py-irt
* **Last updated**: 2024-01
* **Peer-reviewed**: no
* **Relevance**: Python-native IRT library compatible with NumPy/pandas.
  Simpler than mirt for basic 2PL but fewer features. Useful if we prefer
  staying in the Python ecosystem.

### [Shiken-2024]
* **Type**: blog
* **Title**: Effect Size Benchmarks in Language Testing Validation Studies
* **Author/Org**: Shiken Research Bulletin
* **Date**: 2024-05-22
* **URL**: https://shiken.org/blog/effect-size-benchmarks
* **Peer-reviewed**: no
* **Relevance**: Compilation of Cohen's d values from 14 vocabulary test
  validation studies. Provides the benchmarks (d = 1.5-2.8 for yes/no
  formats) that we use as quality thresholds.

### [SciPy-Stats]
* **Type**: documentation
* **Title**: scipy.stats — Statistical Functions
* **Author/Org**: SciPy Project
* **URL**: https://docs.scipy.org/doc/scipy/reference/stats.html
* **Peer-reviewed**: no
* **Relevance**: API for computing inverse normal CDF (ppf), t-tests for
  Cohen's d confidence intervals, and distribution fitting. Core dependency
  for all statistical computations.

### [PWC-LangTest]
* **Type**: documentation
* **Title**: Papers With Code — Language Proficiency Assessment
* **Author/Org**: Papers With Code
* **URL**: https://paperswithcode.com/task/language-proficiency-assessment
* **Peer-reviewed**: no
* **Relevance**: Aggregated leaderboard showing state-of-the-art approaches
  to automated language assessment. Useful for contextualizing our test
  discrimination analysis within the broader field.

### [Pandas-Docs]
* **Type**: documentation
* **Title**: pandas GroupBy and Pivot Tables
* **Author/Org**: pandas Project
* **URL**: https://pandas.pydata.org/docs/user_guide/groupby.html
* **Peer-reviewed**: no
* **Relevance**: API reference for grouped aggregations (Cohen's d per
  test version, per cohort pair) and pivot tables used in the analysis
  pipeline.
```
