# Research Papers Specification

## Purpose

This specification defines the format, structure, and quality requirements for the
`research_papers.md` file produced during the "research in existing papers" task stage.

**Producer**: The research-papers subagent, which reviews papers already downloaded and catalogued
in previous tasks.

**Consumers**:

* **Planning subagent** — uses findings and methodology insights to inform the task plan
* **Human reviewers** — evaluate research thoroughness at checkpoints
* **Verificator** — validates structure, cross-references, and minimum depth programmatically

## File Location

```text
tasks/<task_id>/research/research_papers.md
```

## Format

The file is a Markdown document with YAML frontmatter. All content is UTF-8 encoded.

## YAML Frontmatter

The file must begin with a YAML frontmatter block containing the following required fields:

```yaml
---
spec_version: "1"
task_id: "0015-cohort-discrimination-analysis"
research_stage: "papers"
papers_reviewed: 12
papers_cited: 8
categories_consulted:
  - "psychometrics"
  - "item-response-theory"
date_completed: "2026-03-29"
status: "complete"
---
```

| Field | Type | Description |
| --- | --- | --- |
| `spec_version` | string | Always `"1"` for this version |
| `task_id` | string | Must exactly match the task folder name |
| `research_stage` | string | Always `"papers"` for this file |
| `papers_reviewed` | int | Total papers examined (including those not cited) |
| `papers_cited` | int | Papers referenced in body and listed in Paper Index |
| `categories_consulted` | list[string] | Category slugs from `meta/categories/` |
| `date_completed` | string | ISO 8601 date (YYYY-MM-DD) |
| `status` | string | `"complete"` or `"partial"` (see below) |

If `status` is `"partial"`, the Task Objective section must explain why (e.g., no relevant papers
exist yet in the project).

## Mandatory Sections

The document must contain at least these seven sections in this order, each as an `## ` heading. The
mandatory sections define the minimum structure — authors are encouraged to add additional `## `
sections wherever they would improve clarity (e.g., `## Historical Context`,
`## Comparative Analysis`, `## Dataset Landscape`, `## Theoretical Framework`). Task-specific and
project-specific sections are expected; the research should be as thorough and detailed as the topic
demands.

* * *

### `## Task Objective`

**Minimum**: 30 words

Restate what this task aims to accomplish. Paraphrase or quote from `task.json` and, when present,
the markdown file referenced by `long_description_file`. The purpose is to make this file
self-contained — a reader should not need to open another file to understand why these papers are
being reviewed.

* * *

### `## Category Selection Rationale`

**Minimum**: 50 words

Explain which categories from `meta/categories/` were consulted and why. Document excluded
categories with reasoning. This section makes the research scope auditable — humans can spot if the
agent missed an obvious category.

* * *

### `## Key Findings`

**Minimum**: 200 words

The core of the document. Findings must be organized **by topic, not by paper**. Each topic is a
`### ` subsection.

This is critical: by-topic organization forces synthesis across papers. Per-paper summaries produce
low-value literature dumps. The goal is to extract cross-cutting themes, compare approaches, and
identify consensus and disagreements.

Requirements:

* At least one `### ` subsection
* Every factual claim must have an inline citation `[CitationKey]`
* Each subsection should reference multiple papers where possible
* Identify agreements and disagreements between papers
* Extract **hypotheses** — testable claims or conjectures emerging from the literature that this
  task or future tasks could validate
* Identify **best practices** — established approaches the research community converges on, proven
  configurations, and common pitfalls
* Include **specific numbers** — accuracy scores, effect sizes, sample sizes, hyperparameter values.
  Vague claims like "significantly outperforms" without numbers are unacceptable.

* * *

### `## Methodology Insights`

**Minimum**: 100 words

Specific, actionable techniques from the reviewed papers that are directly applicable to executing
this task. This includes: algorithms, hyperparameter ranges, dataset recommendations, evaluation
protocols, preprocessing steps, implementation details, best practices, and testable hypotheses.

This section is prescriptive, not descriptive. Key Findings says "X is true"; Methodology Insights
says "therefore, when executing this task, do Y." It should also surface **best practices** the
literature converges on and **hypotheses** worth testing during task execution.

* * *

### `## Gaps and Limitations`

**Minimum**: 50 words

What the reviewed papers do NOT cover that is relevant to this task. What questions remain
unanswered. Where the existing literature is weak, contradictory, or outdated. Be specific about
what is missing — vague statements like "more research is needed" are not useful.

* * *

### `## Recommendations for This Task`

**Minimum**: 50 words

Concrete, prioritized recommendations derived from the research. These should directly inform the
planning stage. Each recommendation should be traceable to findings or methodology insights above.

* * *

### `## Paper Index`

A structured reference list of all papers cited in the document. The number of entries must equal
`papers_cited` in the frontmatter.

Each entry uses the citation key as a `### ` heading and contains these required fields:

| Field | Required | Description |
| --- | --- | --- |
| Title | yes | Full paper title |
| Authors | yes | First author et al. acceptable for 3+ authors |
| Year | yes | Publication year |
| DOI | yes | Canonical identifier; also used as asset folder name (with `/` replaced by `_`). For papers without a DOI, use the paper asset folder name (e.g., `no-doi_Smith2024_wsd-benchmark`). See the paper asset specification for the full naming convention. |
| Asset | yes | Relative path to the paper's asset folder |
| Categories | yes | Category slugs assigned to this paper |
| Relevance | yes | 1-2 sentences on why this paper matters for THIS task |

## Additional Sections

Beyond the mandatory sections above, authors should add any sections that help communicate the
research thoroughly. Common useful additions include:

* `## Historical Context` — evolution of approaches in this subfield
* `## Benchmark Comparison` — table comparing published results across papers
* `## Dataset Landscape` — what datasets exist, their sizes, domains, licenses
* `## Theoretical Framework` — underlying theory relevant to the task
* `## Open Questions` — deeper exploration of unresolved debates
* `## Risk Analysis` — what could go wrong based on literature findings
* Any other task-specific section the author deems valuable

The verificator only checks for mandatory sections. Additional sections are never penalized and are
strongly encouraged.

## Citation Format

Use `[CitationKey]` for inline references (e.g., `[Navigli2009]`, `[Embretson2000]`). Citation keys
follow the pattern `[FirstAuthorLastNameYear]`. For multiple works by the same author in the same
year, append a lowercase letter: `[Navigli2009a]`, `[Navigli2009b]`.

Rules:

* Every `[CitationKey]` in the body must have a matching `### [CitationKey]` entry in the Paper
  Index
* Every Paper Index entry should be cited at least once in the body (unused entries indicate
  padding)
* Multiple citations in sequence use commas: `[Navigli2009, Embretson2000]`

## Quality Criteria

### What makes a good `research_papers.md`

* Key Findings are synthesized themes that compare and contrast across papers with specific numbers
  and effect sizes
* Methodology Insights contain specific, actionable guidance (hyperparameter values, dataset names,
  evaluation commands, code references)
* Gaps and Limitations identify concrete questions with enough specificity to guide follow-up
  research
* Hypotheses are explicitly stated as testable propositions
* Best practices are identified where the literature converges
* Citations are precise — claims are attributed to specific papers
* Additional sections are added wherever the task demands deeper treatment
* The document is long enough to be genuinely useful — a researcher reading only this file should
  have a thorough understanding of the relevant literature

### What makes a bad `research_papers.md`

* Sequential paper summaries presented as Key Findings (no synthesis)
* Vague Methodology Insights ("transformers work well", "use a large dataset")
* Empty or pro-forma Gaps section ("no significant gaps identified")
* Missing citations — claims without attribution
* Numbers missing — "significantly outperforms" without actual metrics
* Too short — a research document that could have been an email
* No additional sections even when the task clearly warrants them

## Verificator Rules

The verificator produces errors (E) that block the pipeline, and warnings (W) that are logged but do
not halt execution. Agents should have VERY serious reasons to continue if there are errors.

### Errors

| Code | Check |
| --- | --- |
| `RP-E001` | File does not exist at `tasks/<task_id>/research/research_papers.md` |
| `RP-E002` | YAML frontmatter is missing or not parseable |
| `RP-E003` | `task_id` in frontmatter does not match the task folder name |
| `RP-E004` | One or more mandatory sections is missing (see list below) |
| `RP-E005` | `papers_cited` < 1 and `status` is not `"partial"` |
| `RP-E006` | An inline `[CitationKey]` has no matching entry in Paper Index |
| `RP-E007` | Paper Index entry count != `papers_cited` in frontmatter |
| `RP-E008` | A Paper Index entry is missing the DOI field |
| `RP-E009` | Total content (excluding frontmatter) is fewer than 300 words |
| `RP-E010` | `spec_version` is missing from frontmatter |

The mandatory sections checked by `RP-E004` are: `## Task Objective`,
`## Category Selection Rationale`, `## Key Findings`, `## Methodology Insights`,
`## Gaps and Limitations`, `## Recommendations for This Task`, `## Paper Index`.

### Warnings

| Code | Check |
| --- | --- |
| `RP-W001` | A mandatory section is below its minimum word count |
| `RP-W002` | A DOI in the Paper Index does not correspond to any existing paper asset folder |
| `RP-W003` | A category in `categories_consulted` or in a Paper Index entry does not exist in `meta/categories/` |
| `RP-W004` | `papers_reviewed` < `papers_cited` (likely a frontmatter error) |
| `RP-W005` | `## Key Findings` section contains no `### ` subsections |
| `RP-W006` | A Paper Index entry is never cited in the body text |

## Complete Example

```markdown
---
spec_version: "1"
task_id: "0008-baseline-sentiment-classifier"
research_stage: "papers"
papers_reviewed: 8
papers_cited: 6
categories_consulted:
  - "sentiment-analysis"
  - "transformer-models"
  - "text-classification"
date_completed: "2026-03-28"
status: "complete"
---

## Task Objective

Implement a baseline sentiment classifier using fine-tuned BERT on the
SST-2 and IMDb benchmarks. The goal is to establish baseline accuracy
numbers before exploring domain adaptation, few-shot, and multi-task
approaches in subsequent tasks. This baseline will serve as the reference
point for all future sentiment experiments in this project.

## Category Selection Rationale

Consulted `sentiment-analysis` because this task directly implements a
sentiment classifier. Consulted `transformer-models` because the approach
is BERT-based. Consulted `text-classification` to understand general
evaluation protocols and ensure our results are comparable to published
work.

Excluded `aspect-based-sentiment` — this task focuses on document-level
polarity, not fine-grained aspect extraction. Excluded `multilingual-nlp`
— the baseline targets English only; multilingual extension is a separate
planned task.

## Key Findings

### Fine-Tuning Outperforms Feature Extraction for Sentiment

Multiple studies demonstrate that fine-tuning the full BERT model produces
significantly higher accuracy than using frozen representations.
[Devlin2019] reported **93.5% accuracy** on SST-2 with fine-tuning vs.
**84.2%** with feature extraction (a frozen BERT feeding a linear head).
[Sun2019] confirmed this on multiple sentiment benchmarks and found that
fine-tuning the last 3 layers achieves **92.8%** — close to full
fine-tuning at lower cost.

The gap between frozen and fine-tuned is larger for sentiment than for
other NLP tasks. [Howard2018] explains that sentiment is encoded
diffusely across layers, so allowing gradient flow through the full model
is critical. This has a practical implication: unlike tasks where frozen
BERT suffices, sentiment classification strongly favors fine-tuning.

**Hypothesis**: If fine-tuning only the last 3 layers achieves 92.8% vs.
93.5% for full fine-tuning on SST-2, the gap may widen on longer-document
benchmarks (IMDb) where deeper context integration matters more. This
should be tested.

### Learning Rate and Warm-Up Are Critical for Stability

[Devlin2019] recommended a learning rate of **2e-5** with linear warm-up
over 10% of training steps for classification fine-tuning. [Sun2019]
conducted a systematic ablation and found:

| Learning rate | Warm-up ratio | SST-2 Acc | IMDb Acc | Stability |
|---------------|---------------|-----------|----------|-----------|
| 1e-5          | 0.06          | 92.9      | 94.1     | High      |
| 2e-5          | 0.10          | 93.5      | 95.0     | High      |
| 3e-5          | 0.10          | 93.3      | 94.7     | Medium    |
| 5e-5          | 0.10          | 92.1      | 93.2     | Low       |

Beyond **3e-5**, fine-tuning becomes unstable with significant run-to-run
variance. [Mosbach2021] provided a theoretical explanation: higher
learning rates cause catastrophic forgetting of pre-trained features in
early layers.

**Best practice**: Use **2e-5** learning rate with **10% warm-up** as the
default. This is the most thoroughly documented configuration across
multiple benchmarks.

### Dataset Size Significantly Affects Fine-Tuning Strategies

[Sun2019] tested fine-tuning strategies across datasets of varying sizes
and found that approach effectiveness depends heavily on training set
size:

| Dataset   | Train size | Test size | BERT-base Acc | BERT-large Acc |
|-----------|------------|-----------|---------------|----------------|
| SST-2     | 67,349     | 872       | 93.5          | 94.9           |
| IMDb      | 25,000     | 25,000    | 95.0          | 95.5           |
| Yelp-2    | 560,000    | 38,000    | 97.8          | 98.1           |
| MR        | 8,662      | 2,000     | 87.5          | 88.2           |

With fewer than 10,000 training examples (MR dataset), BERT-base is only
**0.7 points** behind BERT-large, suggesting that the smaller model is
sufficient for low-resource scenarios. With abundant data (Yelp-2), the
gap narrows even further to **0.3 points**.

**Best practice**: Start with BERT-base for initial experiments. Use
BERT-large only if BERT-base falls short of target accuracy and training
data exceeds 20,000 examples.

### Document Length Affects Model Choice

[Adhikari2019] systematically evaluated how input length truncation affects
sentiment accuracy. BERT processes at most 512 tokens, but many sentiment
benchmarks (IMDb, Yelp) contain longer documents. Their truncation study:

| Strategy          | IMDb Acc | Avg tokens used |
|-------------------|----------|-----------------|
| First 512 tokens  | 95.0     | 512             |
| Last 512 tokens   | 94.3     | 512             |
| Head + tail (256) | 95.4     | 512             |
| Hierarchical BERT | 95.7     | full document   |

The head-plus-tail strategy (first 256 + last 256 tokens) outperforms
simple truncation by **+0.4 points** on IMDb at no additional compute.
Hierarchical approaches add another **+0.3** but require significant
engineering.

[Howard2018] explains that sentiment-bearing content concentrates at
document beginnings (thesis statements) and endings (conclusions),
making head+tail a strong heuristic.

## Methodology Insights

* **Fine-tuning configuration**: Use BERT-base-uncased with learning rate
  **2e-5**, batch size **32**, and **3 epochs** [Devlin2019]. This is the
  standard configuration and achieves **93.5%** on SST-2. Use linear
  warm-up over 10% of training steps.

* **Tokenization**: Use the default BERT WordPiece tokenizer. For documents
  longer than 512 tokens, use the head+tail strategy (first 256 + last
  256 tokens) [Adhikari2019]. This is simple to implement and gives
  **+0.4 points** over naive truncation.

* **Evaluation protocol**: Report accuracy on SST-2 and IMDb. Use the
  standard train/test splits. Report mean and standard deviation over
  5 random seeds to capture run-to-run variance [Mosbach2021].

* **Baseline reference**: A majority-class baseline achieves **50.9%** on
  SST-2. Any model below this indicates a bug. A TF-IDF + logistic
  regression baseline achieves **85.3%** [Maas2011]. Our fine-tuned BERT
  should exceed this comfortably.

* **Best practice — early stopping**: Monitor validation accuracy after
  each epoch. Stop if validation accuracy does not improve for 2 epochs.
  This prevents overfitting on small datasets like MR [Sun2019].

* **Hypothesis to test**: Data augmentation via back-translation may
  improve accuracy on the smallest benchmarks (MR, < 10K examples) where
  fine-tuning is data-starved. Not tested in the reviewed literature for
  BERT-based sentiment classification.

## Gaps and Limitations

* **Domain transfer**: None of the reviewed papers systematically measure
  cross-domain performance (e.g., train on movie reviews, test on product
  reviews). For a project that may need domain-general sentiment, this is
  a significant gap.

* **Inference latency**: No reviewed paper reports per-example inference
  time for BERT-based sentiment. We will need to benchmark this ourselves
  for production-readiness assessment.

* **Calibration**: No paper evaluates whether BERT's softmax probabilities
  are well-calibrated for sentiment confidence estimation. This matters if
  downstream systems need reliable confidence scores.

* **Negation handling**: [Sun2019] notes that negation remains a failure
  mode (e.g., "not bad" classified as negative) but no paper provides a
  targeted analysis with error rates on negation-bearing examples.

## Recommendations for This Task

1. **Use BERT-base-uncased with standard fine-tuning** — achieves
   **93.5%** on SST-2 [Devlin2019]. Start here before trying larger
   models.

2. **Use 2e-5 learning rate, 32 batch size, 3 epochs** — the most stable
   configuration across reviewed papers [Sun2019].

3. **Evaluate on both SST-2 and IMDb** — SST-2 tests short sentences,
   IMDb tests longer documents. Both are standard benchmarks.

4. **Report 5-seed mean and standard deviation** — captures fine-tuning
   variance [Mosbach2021].

5. **Implement head+tail truncation for IMDb** — simple improvement worth
   **+0.4 accuracy** over naive truncation [Adhikari2019].

6. **Benchmark inference speed** — fill the gap in the literature.

## Paper Index

### [Devlin2019]

* **Title**: BERT: Pre-training of Deep Bidirectional Transformers for
  Language Understanding
* **Authors**: Devlin, J., Chang, M., Lee, K., Toutanova, K.
* **Year**: 2019
* **DOI**: `10.18653/v1/N19-1423`
* **Asset**: `assets/paper/10.18653_v1_N19-1423/`
* **Categories**: `transformer-models`, `text-classification`
* **Relevance**: Defines the standard BERT fine-tuning protocol for
  classification tasks. Primary source for hyperparameters and SST-2
  baseline (93.5% accuracy).

### [Sun2019]

* **Title**: How to Fine-Tune BERT for Text Classification
* **Authors**: Sun, C., Qiu, X., Xu, Y., Huang, X.
* **Year**: 2019
* **DOI**: `10.1007/978-3-030-32381-3_16`
* **Asset**: `assets/paper/10.1007_978-3-030-32381-3_16/`
* **Categories**: `sentiment-analysis`, `transformer-models`
* **Relevance**: Systematic study of fine-tuning strategies across multiple
  sentiment benchmarks. Provides learning rate ablation and dataset-size
  recommendations directly applicable to this task.

### [Howard2018]

* **Title**: Universal Language Model Fine-tuning for Text Classification
* **Authors**: Howard, J., Ruder, S.
* **Year**: 2018
* **DOI**: `10.18653/v1/P18-1031`
* **Asset**: `assets/paper/10.18653_v1_P18-1031/`
* **Categories**: `text-classification`, `transfer-learning`
* **Relevance**: Introduced discriminative fine-tuning and gradual
  unfreezing. Explains why sentiment-bearing features are distributed
  across layers, motivating full fine-tuning over feature extraction.

### [Adhikari2019]

* **Title**: DocBERT: BERT for Document Classification
* **Authors**: Adhikari, A., Ram, A., Tang, R., Lin, J.
* **Year**: 2019
* **DOI**: `10.48550/arXiv.1904.08398`
* **Asset**: `assets/paper/10.48550_arXiv.1904.08398/`
* **Categories**: `text-classification`, `transformer-models`
* **Relevance**: Head+tail truncation strategy achieving +0.4 points on
  long-document benchmarks. Directly applicable to our IMDb evaluation.

### [Mosbach2021]

* **Title**: On the Stability of Fine-tuning BERT
* **Authors**: Mosbach, M., Andriushchenko, M., Klakow, D.
* **Year**: 2021
* **DOI**: `10.48550/arXiv.2006.04884`
* **Asset**: `assets/paper/10.48550_arXiv.2006.04884/`
* **Categories**: `transformer-models`, `optimization`
* **Relevance**: Explains fine-tuning instability and provides evidence for
  multi-seed reporting. Recommends longer warm-up and lower learning rates
  for stable convergence.

### [Maas2011]

* **Title**: Learning Word Vectors for Sentiment Analysis
* **Authors**: Maas, A., Daly, R., Pham, P., Huang, D., Ng, A., Potts, C.
* **Year**: 2011
* **DOI**: `10.18653/v1/P11-1015`
* **Asset**: `assets/paper/10.18653_v1_P11-1015/`
* **Categories**: `sentiment-analysis`
* **Relevance**: Introduced the IMDb benchmark dataset (25K train / 25K
  test). Provides the TF-IDF baseline (85.3%) that any neural system must
  beat.

### [Smith2024]

* **Title**: A New Benchmark for Word Sense Disambiguation
* **Authors**: Smith, J., Lee, K.
* **Year**: 2024
* **DOI**: `no-doi_Smith2024_wsd-benchmark` (no DOI available; uses paper asset folder name)
* **Asset**: `assets/paper/no-doi_Smith2024_wsd-benchmark/`
* **Categories**: `wsd-evaluation`
* **Relevance**: Proposes a new evaluation benchmark addressing known
  limitations of existing WSD test sets.
```
