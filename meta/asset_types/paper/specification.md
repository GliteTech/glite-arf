# Paper Asset Specification

**Version**: 3

* * *

## Purpose

This specification defines the folder structure, metadata format, and summary requirements for paper
assets in the project.

**Producer**: The research subagent (during paper download and summarization stages) or a dedicated
paper-download skill.

**Consumers**:
* **Research subagents** — read summaries to inform task research
* **Planning subagents** — use paper findings to design task plans
* **Aggregator scripts** — combine paper metadata and summaries across tasks
* **Human reviewers** — evaluate paper coverage at checkpoints
* **Verificator scripts** — validate structure and completeness

* * *

## Asset Folder Structure

Paper assets are created **inside the task folder** that produces them. Each paper is stored in its
own subfolder under the task's `assets/paper/` directory:

```text
tasks/<task_id>/assets/paper/<paper_id>/
├── details.json       # Structured metadata (required)
├── summary.md         # Example canonical summary document
└── files/             # Paper file(s) (required, at least one file)
    ├── <filename>.pdf
    └── <filename>.md  # (optional: markdown conversion)
```

The top-level `assets/paper/` directory is reserved for aggregated views produced by aggregator
scripts — tasks must never write directly to it.

The `files/` subdirectory holds the actual paper content — PDF, markdown conversion, DOCX, or any
other format. At least one file must be present when `download_status` is `"success"`. When
`download_status` is `"failed"`, the `files/` directory must contain a `.gitkeep` file to ensure git
preserves the directory. The paper asset still has value for its metadata and abstract-based
summary.

The canonical summary file path is stored in `details.json` `summary_path`. New v3 assets must
declare this field explicitly. Historical v2 assets may omit it; in that case consumers fall back to
`summary.md`.

* * *

## Paper ID

The paper ID determines the folder name and serves as the canonical identifier throughout the
project.

### Rules

1. **If the paper has a DOI**: generate the slug using the canonical module
   `arf.scripts.utils.doi_to_slug`. This module strips URL prefixes, replaces every `/` with `_`,
   and validates the result. Always use this module — never convert DOIs by hand.
   * `uv run python -u -m arf.scripts.utils.doi_to_slug "10.18653/v1/E17-1010"` →
     `10.18653_v1_E17-1010`
   * `uv run python -u -m arf.scripts.utils.doi_to_slug "10.1145/1459352.1459355"` →
     `10.1145_1459352.1459355`
   * The script also accepts `https://doi.org/` prefixed URLs.

2. **If the paper has no DOI** (preprints, working papers, presentations): use the format
   `no-doi_<FirstAuthorLastName><Year>_<slug>`.
   * Example: `no-doi_Smith2024_wsd-benchmark-proposal`
   * The slug is 2-5 lowercase words from the title, separated by hyphens.

### Do:

```text
tasks/0001-initial-survey/assets/paper/10.18653_v1_E17-1010/
tasks/0001-initial-survey/assets/paper/no-doi_Smith2024_wsd-benchmark-proposal/
```

### Don't:

```text
assets/paper/10.18653_v1_E17-1010/   # Wrong: top-level, not in task folder
assets/paper/raganato_2017/          # Wrong: uses author name for DOI paper
assets/paper/10.18653/v1/E17-1010/   # Wrong: slashes not replaced
assets/paper/Smith2024/              # Wrong: missing no-doi_ prefix
```

* * *

## details.json

The metadata file contains all structured information about the paper. All field names use
`snake_case`.

### Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version (e.g., `"3"`) |
| `paper_id` | string | yes | Folder name (DOI-based or fallback) |
| `doi` | string \| null | yes | Original DOI with slashes, or `null` |
| `title` | string | yes | Full paper title |
| `url` | string \| null | yes | Web page URL (landing page, not PDF) |
| `pdf_url` | string \| null | no | Direct URL to downloadable PDF |
| `date_published` | string \| null | no | ISO 8601 date: `YYYY-MM-DD`, `YYYY-MM`, or `YYYY` |
| `year` | int | yes | Publication year |
| `authors` | list[Author] | yes | Ordered list of authors (see below) |
| `institutions` | list[Institution] | yes | Unique institutions across all authors |
| `journal` | string | yes | Journal name, conference name, or `"preprint"` for unrefereed work |
| `venue_type` | string | yes | Publication venue type; see allowed values below |
| `categories` | list[string] | yes | Category slugs from `meta/categories/` |
| `abstract` | string | yes | Full abstract text |
| `citation_key` | string | yes | `FirstAuthorLastNameYear`; append `a`, `b` if needed |
| `summary_path` | string | yes in v3, no in v2 | Canonical summary path |
| `files` | list[string] | yes | Relative paths in `files/`; use `[]` when download failed |
| `download_status` | string | yes | `"success"` or `"failed"` |
| `download_failure_reason` | string \| null | yes | Explanation when `"failed"`; else `null` |
| `added_by_task` | string | yes | Task ID that first added this paper |
| `date_added` | string | yes | ISO 8601 date when added to the project |

### Author Object

Allowed `venue_type` values: `"journal"`, `"conference"`, `"workshop"`, `"preprint"`, `"book"`,
`"thesis"`, `"technical_report"`, and `"other"`.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | yes | Full name as it appears on the paper |
| `country` | string \| null | no | ISO 3166-1 alpha-2 code (e.g., `US`, `IT`, `CN`) |
| `institution` | string \| null | no | Affiliated institution name |
| `orcid` | string \| null | no | ORCID identifier (e.g., `0000-0002-1234-5678`) |

### Institution Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | yes | Institution name in English |
| `country` | string | yes | ISO 3166-1 alpha-2 code |

### Example

````json
{
  "spec_version": "3",
  "paper_id": "10.18653_v1_E17-1010",
  "doi": "10.18653/v1/E17-1010",
  "title": "Word Sense Disambiguation: A Unified Evaluation Framework and Empirical Comparison",
  "url": "https://aclanthology.org/E17-1010/",
  "pdf_url": "https://aclanthology.org/E17-1010.pdf",
  "date_published": "2017-04-03",
  "year": 2017,
  "authors": [
    {
      "name": "Alessandro Raganato",
      "country": "IT",
      "institution": "University of Helsinki",
      "orcid": null
    },
    {
      "name": "Jose Camacho-Collados",
      "country": "ES",
      "institution": "Sapienza University of Rome",
      "orcid": null
    },
    {
      "name": "Roberto Navigli",
      "country": "IT",
      "institution": "Sapienza University of Rome",
      "orcid": "0000-0002-1855-8615"
    }
  ],
  "institutions": [
    {
      "name": "University of Helsinki",
      "country": "FI"
    },
    {
      "name": "Sapienza University of Rome",
      "country": "IT"
    }
  ],
  "journal": "EACL 2017",
  "venue_type": "conference",
  "categories": [
    "supervised-wsd",
    "wsd-evaluation"
  ],
  "abstract": "Unified WSD evaluation framework with five all-words datasets and a toolkit.",
  "citation_key": "Raganato2017",
  "summary_path": "summary.md",
  "files": [
    "files/raganato_2017_wsd-unified-eval.pdf"
  ],
  "download_status": "success",
  "download_failure_reason": null,
  "added_by_task": "0001-initial-survey",
  "date_added": "2026-03-29"
}
````

* * *

## Summary Document

A detailed summary of the paper written after reading the full text. The canonical summary document
is the file referenced by `details.json` `summary_path`. Historical v2 assets may omit that field;
in that case the canonical document defaults to `summary.md`.

The summary must be thorough enough that a researcher reading only this file gains a solid
understanding of the paper's contributions, methods, and results without opening the original PDF.

### YAML Frontmatter

```yaml
---
spec_version: "3"
paper_id: "10.18653_v1_E17-1010"
citation_key: "Raganato2017"
summarized_by_task: "0001-initial-survey"
date_summarized: "2026-03-29"
---
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version (e.g., `"3"`) |
| `paper_id` | string | yes | Must match the folder name |
| `citation_key` | string | yes | Must match `details.json` |
| `summarized_by_task` | string | yes | Task ID that produced this summary |
| `date_summarized` | string | yes | ISO 8601 date |

### Mandatory Sections

The summary must contain these sections in this order, each as an `##` heading. Additional sections
may be added between them where useful.

* * *

#### `## Metadata`

Quick-reference block repeating key facts from `details.json` for convenience. Format:

````markdown
## Metadata

* **File**: `files/raganato_2017_wsd-unified-eval.pdf`
* **Published**: 2017
* **Authors**: Alessandro Raganato 🇮🇹, Jose Camacho-Collados 🇪🇸,
  Roberto Navigli 🇮🇹
* **Venue**: EACL 2017
* **DOI**: `10.18653/v1/E17-1010`
````

Use emoji country flags after author names. If country is unknown, omit the flag.

* * *

#### `## Abstract`

The paper's abstract, copied verbatim from the original paper. Do not paraphrase, reword, or
summarize — reproduce the exact text. This provides a quick, authoritative reference for what the
paper claims.

If the paper could not be downloaded, copy the abstract from the metadata collected in
`details.json`.

* * *

#### `## Overview`

2-5 paragraphs describing what the paper does and finds. This section must be written **after
reading the full paper**, not just the abstract. It must cover methodology, key results, and
significance — information that goes well beyond what the paper's abstract contains. Do NOT
paraphrase or reword the paper's abstract — write an original overview based on the full paper
content. If the paper could not be downloaded, this must be explicitly stated and the section should
acknowledge its limitations.

**Minimum**: 100 words.

* * *

#### `## Architecture, Models and Methods`

Detailed description of the methodology:

* Algorithms, model architectures, frameworks used
* Training procedures, hyperparameters, optimization details
* Evaluation methodology and metrics
* Sample sizes, statistical techniques, experimental design
* Hardware and compute requirements (if reported)

Be specific. Include numbers: layer counts, embedding dimensions, learning rates, batch sizes,
training epochs, dataset splits.

**Minimum**: 150 words.

* * *

#### `## Results`

Key findings presented as bullet points with specific quantitative values. Every number the paper
reports that matters should appear here.

#### Do:

```markdown
* Unified framework achieves **65.5 F1** (MFS baseline) across 5 datasets
* Best supervised system (IMS+embeddings) reaches **71.3 F1** on ALL
* Noun-only performance: **72.1 F1** (best) vs. verb-only: **57.4 F1**
* Context window of 3 sentences outperforms full-document by **+1.2 F1**
```

#### Don't:

````markdown
* The results were good across multiple datasets
* Performance varied by part of speech
* Larger context windows helped somewhat
````

**Minimum**: 5 bullet points with specific numbers.

* * *

#### `## Innovations`

What is novel or influential about this paper. Use named subheadings for each distinct contribution:

```markdown
## Innovations

### Unified Evaluation Framework

First standardized benchmark combining five all-words WSD datasets
(Senseval-2, Senseval-3, SemEval-2007, SemEval-2013, SemEval-2015) with
a common scorer and consistent preprocessing...

### Fine-Grained POS Analysis

First systematic comparison of WSD performance broken down by part of
speech, revealing that verbs are significantly harder...
```

* * *

#### `## Datasets`

Datasets used in the paper:

* Dataset names and versions
* Sizes (number of instances, tokens, senses)
* Languages and domains
* Availability (public, restricted, license type)
* Links or references to obtain them
* Participant demographics (for human studies)

For theoretical papers with no datasets, write: "This is a theoretical paper; no datasets were
used."

* * *

#### `## Main Ideas`

Bullet points of the most important takeaways relevant to **this project**. Focus on what is
actionable — methods to adopt, pitfalls to avoid, baselines to compare against.

**Minimum**: 3 bullet points.

* * *

#### `## Summary`

A comprehensive synthesis in exactly 4 paragraphs:

1. **What the paper does** — research question, scope, motivation
2. **How it does it** — methodology and key design decisions
3. **What it finds** — headline results and their significance
4. **Why it matters for this project** — practical implications, limitations, and how findings
   connect to our research goals

**Minimum**: 200 words total across the 4 paragraphs.

* * *

### Quality Criteria

A good summary:

* Is self-contained — a reader understands the paper without opening the PDF
* Contains specific numbers, not vague qualifiers ("good", "improved", "significant")
* Distinguishes the paper's claimed contributions from the summarizer's interpretation
* Identifies limitations the authors acknowledge and limitations they do not
* Connects findings to this project's specific research context
* Is detailed enough to support planning decisions (hyperparameter choices, dataset selection,
  baseline comparisons)

A bad summary:

* Paraphrases only the abstract
* Uses vague language ("the authors propose a method", "results were promising")
* Omits quantitative results
* Does not connect the paper to this project's needs
* Is under 500 words total

* * *

## Paper Files

### Location

All paper files go in the `files/` subdirectory within the paper asset folder.

### Naming Convention

```text
<first_author_last_name>_<year>_<slug>.<ext>
```

* Use the first author's last name (lowercase)
* Publication year (4 digits)
* A slug of 2-5 lowercase words from the title, separated by hyphens
* The original file extension

Examples:
* `raganato_2017_wsd-unified-eval.pdf`
* `navigli_2009_wsd-survey.pdf`
* `wiedemann_2019_bert-wsd.pdf`
* `wiedemann_2019_bert-wsd.md` (markdown conversion of the same paper)

### Accepted File Types

* `.pdf` — preferred for published papers
* `.md` — markdown conversion (useful for full-text search and LLM processing)
* `.docx` — Word documents (rare, typically for working papers)
* `.html` — saved web pages (rare, for online-only publications)

Multiple formats of the same paper are allowed and encouraged. List all files in `details.json`
`files` field.

* * *

## Verification Rules

### Errors

Errors indicate structural problems that must be fixed.

| Code | Description |
| --- | --- |
| `PA-E001` | `details.json` is missing or not valid JSON |
| `PA-E002` | The canonical summary document is missing |
| `PA-E003` | `files/` directory is missing or empty when `download_status` is `"success"` |
| `PA-E004` | `paper_id` in `details.json` does not match folder name |
| `PA-E005` | Required field missing in `details.json` |
| `PA-E006` | `citation_key` in summary frontmatter does not match `details.json` |
| `PA-E007` | `paper_id` in summary frontmatter does not match `details.json` |
| `PA-E008` | A file listed in `details.json` `files` does not exist |
| `PA-E009` | The canonical summary document is missing a mandatory section |
| `PA-E010` | `venue_type` is not one of the allowed values |
| `PA-E011` | Folder name contains `/` characters (unescaped DOI) |
| `PA-E012` | The canonical summary document is missing YAML frontmatter |
| `PA-E013` | `spec_version` is missing from `details.json` or summary frontmatter |
| `PA-E014` | `download_status` is `"failed"` but `download_failure_reason` is `null` or empty |
| `PA-E015` | `download_status` is not `"success"` or `"failed"` |

### Warnings

Warnings indicate quality concerns that should be addressed but do not block progress.

| Code | Description |
| --- | --- |
| `PA-W001` | The canonical summary document total word count is under 500 |
| `PA-W002` | Results section has fewer than 5 bullet points |
| `PA-W003` | Main Ideas section has fewer than 3 bullet points |
| `PA-W004` | Summary section does not have 4 paragraphs |
| `PA-W005` | A category in `details.json` does not exist in `meta/categories/` |
| `PA-W006` | `doi` is `null` but folder name does not start with `no-doi_` |
| `PA-W007` | No author has a non-null `country` field |
| `PA-W008` | `abstract` field in `details.json` is empty or under 50 words |
| `PA-W009` | `date_published` is `null` (only `year` is known) |
| `PA-W010` | Invalid ISO 3166-1 alpha-2 `country`, or institution has `null` country |
| `PA-W011` | `date_published` does not match ISO 8601 format (`YYYY`, `YYYY-MM`, or `YYYY-MM-DD`) |

* * *

## Complete Example

### Folder Structure

```text
tasks/0001-initial-survey/assets/paper/10.18653_v1_E17-1010/
├── details.json
├── summary.md
└── files/
    └── raganato_2017_wsd-unified-eval.pdf
```

### details.json

`````json
{
  "spec_version": "3",
  "paper_id": "10.18653_v1_E17-1010",
  "doi": "10.18653/v1/E17-1010",
  "title": "Word Sense Disambiguation: A Unified Evaluation Framework and Empirical Comparison",
  "url": "https://aclanthology.org/E17-1010/",
  "pdf_url": "https://aclanthology.org/E17-1010.pdf",
  "date_published": "2017-04-03",
  "year": 2017,
  "authors": [
    {
      "name": "Alessandro Raganato",
      "country": "IT",
      "institution": "University of Helsinki",
      "orcid": null
    },
    {
      "name": "Jose Camacho-Collados",
      "country": "ES",
      "institution": "Sapienza University of Rome",
      "orcid": null
    },
    {
      "name": "Roberto Navigli",
      "country": "IT",
      "institution": "Sapienza University of Rome",
      "orcid": "0000-0002-1855-8615"
    }
  ],
  "institutions": [
    {
      "name": "University of Helsinki",
      "country": "FI"
    },
    {
      "name": "Sapienza University of Rome",
      "country": "IT"
    }
  ],
  "journal": "EACL 2017",
  "venue_type": "conference",
  "categories": [
    "supervised-wsd",
    "wsd-evaluation"
  ],
  "abstract": "Unified WSD evaluation framework, system benchmark, and evaluation study.",
  "citation_key": "Raganato2017",
  "summary_path": "summary.md",
  "files": [
    "files/raganato_2017_wsd-unified-eval.pdf"
  ],
  "download_status": "success",
  "download_failure_reason": null,
  "added_by_task": "0001-initial-survey",
  "date_added": "2026-03-29"
}
`````

### Summary Document

````markdown
---
spec_version: "3"
paper_id: "10.18653_v1_E17-1010"
citation_key: "Raganato2017"
summarized_by_task: "0001-initial-survey"
date_summarized: "2026-03-29"
---

# Word Sense Disambiguation: A Unified Evaluation Framework and Empirical Comparison

## Metadata

* **File**: `files/raganato_2017_wsd-unified-eval.pdf`
* **Published**: 2017
* **Authors**: Alessandro Raganato 🇮🇹, Jose Camacho-Collados 🇪🇸,
  Roberto Navigli 🇮🇹
* **Venue**: EACL 2017
* **DOI**: `10.18653/v1/E17-1010`

## Abstract

Word Sense Disambiguation is a long-standing task in Natural Language
Processing, lying at the confluence between knowledge representation and
computational linguistics. In this paper we present a unified evaluation
framework for WSD, providing a standard benchmark of five all-words
datasets, a fine-grained evaluation methodology, and an open-source
evaluation toolkit. We use this framework to evaluate and compare a large
number of WSD systems from different paradigms, and to assess the effect
of fine-grained evaluation measures and domain-specific settings on
system performance.

## Overview

This paper addresses a longstanding fragmentation problem in WSD
evaluation. Prior to this work, different systems were tested on different
subsets of data using different scoring conventions, making cross-system
comparison unreliable. The authors propose a unified evaluation framework
that standardizes five existing all-words WSD datasets into a single
benchmark with consistent preprocessing, sense inventory (WordNet 3.0),
and scoring.

The framework includes an open-source Java toolkit for evaluation and
supports fine-grained analysis by part of speech, domain, and polysemy
level. Using this framework, the authors conduct the largest comparative
evaluation of WSD systems to date, covering knowledge-based, supervised,
and hybrid approaches.

## Architecture, Models and Methods

The framework unifies five all-words WSD datasets: Senseval-2 (SE2),
Senseval-3 (SE3), SemEval-2007 Task 17 (SE07), SemEval-2013 Task 12
(SE13), and SemEval-2015 Task 13 (SE15). All datasets are converted to
a common XML format with sense annotations mapped to WordNet 3.0 synsets.

Evaluation uses standard precision, recall, and F1 over polysemous content
words. The Most Frequent Sense (MFS) baseline from SemCor serves as the
primary reference. The authors also evaluate by part of speech (noun,
verb, adjective, adverb) and by concatenation of all datasets (ALL).

Systems compared include IMS (SVM-based supervised), UKB (graph-based
knowledge), Babelfy (knowledge+graph hybrid), and Lesk variants
(definition overlap). All systems use WordNet 3.0 as the sense inventory
and SemCor as the primary training corpus for supervised systems.

## Results

* MFS baseline achieves **65.5 F1** on the ALL concatenation
* Best supervised system (IMS+embeddings) achieves **71.3 F1** on ALL
* Knowledge-based UKB achieves **63.7 F1** with WordNet only
* Nouns are easiest: **72.1 F1** (best system) vs. verbs: **57.4 F1**
* Adjectives: **78.5 F1** (best), adverbs: **83.6 F1** (best, but
  very few instances)
* SemEval-2007 (SE07) is the hardest dataset at **62.8 F1** for MFS
* SemEval-2015 (SE15) is the easiest at **67.8 F1** for MFS
* Adding word embeddings to IMS improves verb F1 by **+3.1 points**
* Domain-specific evaluation shows significant variation: biomedical
  texts see **-5.2 F1** drop for general-domain systems

## Innovations

### Unified Five-Dataset Benchmark

First standardized benchmark combining Senseval-2, Senseval-3,
SemEval-2007, SemEval-2013, and SemEval-2015 with consistent
preprocessing and WordNet 3.0 sense mapping. This became the de facto
standard for WSD evaluation in subsequent years.

### Fine-Grained POS Analysis

First systematic comparison of WSD performance broken down by part of
speech across all major systems, conclusively demonstrating that verb
disambiguation is the primary bottleneck (14+ F1 points below nouns).

### Open-Source Evaluation Toolkit

Released a Java-based scorer that standardizes evaluation, eliminating
discrepancies caused by different tokenization, lemmatization, and
back-off strategies.

## Datasets

* **Senseval-2** (SE2): 2,282 instances, English all-words, 2001
* **Senseval-3** (SE3): 1,850 instances, English all-words, 2004
* **SemEval-2007 Task 17** (SE07): 455 instances, English all-words
* **SemEval-2013 Task 12** (SE13): 1,644 instances, English all-words
* **SemEval-2015 Task 13** (SE15): 1,022 instances, English all-words
* **ALL**: concatenation of all five datasets, 7,253 instances total
* **SemCor**: 226,036 sense-annotated tokens used as training data

All datasets are publicly available. The unified XML versions and scorer
are released at the paper's companion repository.

## Main Ideas

* The MFS baseline (**65.5 F1**) remains a strong reference point —
  any WSD system must beat this to demonstrate value
* Verb disambiguation is the hardest subproblem and the main driver
  of overall performance differences between systems
* Supervised approaches consistently outperform knowledge-based ones
  when training data is available, but the gap narrows on rare senses
* Fine-grained evaluation by POS, domain, and polysemy level reveals
  patterns invisible in aggregate F1
* The unified framework and scorer should be used for all WSD evaluation
  in this project to ensure comparability with published results

## Summary

Raganato et al. address the fragmentation of WSD evaluation by proposing
a unified framework that standardizes five major all-words English WSD
datasets. Prior to this work, comparing systems required navigating
inconsistent preprocessing, different WordNet versions, and incompatible
scoring conventions — making published results difficult to compare.

The framework maps all datasets to WordNet 3.0, provides a common XML
format, and includes an open-source Java scorer. The authors use this
framework to evaluate dozens of systems spanning knowledge-based,
supervised, and hybrid paradigms, producing the most comprehensive
cross-system comparison in WSD literature at that time.

The key finding is that supervised systems (IMS at **71.3 F1**) lead,
but the MFS baseline (**65.5 F1**) remains surprisingly competitive,
especially on verbs where all systems struggle. The POS breakdown
reveals that nouns reach **72.1 F1** while verbs lag at **57.4 F1**,
identifying verb disambiguation as the primary unsolved bottleneck.

For this project, the Raganato framework is essential as the standard
benchmark. All WSD experiments should use the unified five-dataset
evaluation with the provided scorer. The POS-stratified analysis pattern
should be adopted for our own results reporting, and the MFS baseline
must be included as the minimum reference point in every experiment.
````
