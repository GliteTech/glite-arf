# Dataset Asset Specification

**Version**: 2

* * *

## Purpose

This specification defines the folder structure, metadata format, and description requirements for
dataset assets in the project.

**Producer**: The implementation subagent of a task that downloads or generates a dataset.

**Consumers**:
* **Implementation subagents** — load and use datasets during task implementation
* **Aggregator scripts** — combine dataset metadata across tasks
* **Human reviewers** — evaluate dataset coverage at checkpoints
* **Verificator scripts** — validate structure and completeness

* * *

## Asset Folder Structure

Dataset assets are created **inside the task folder** that produces them. Each dataset is stored in
its own subfolder under the task's `assets/dataset/` directory:

```text
tasks/<task_id>/assets/dataset/<dataset_id>/
├── details.json       # Structured metadata (required)
├── description.md     # Example canonical description document
└── files/             # Dataset file(s) (required, at least one file)
    ├── <filename>.xml
    └── <filename>.csv
```

The top-level `assets/dataset/` directory is reserved for aggregated views produced by aggregator
scripts — tasks must never write directly to it.

The `files/` subdirectory holds the actual dataset content. At least one file must be present —
unlike paper assets, datasets without files are not added to the project.

The canonical documentation file path is stored in `details.json` `description_path`. New v2 assets
must declare this field explicitly. Historical v1 assets may omit it; in that case consumers fall
back to `description.md`.

* * *

## Dataset ID

The dataset ID determines the folder name and serves as the canonical identifier throughout the
project.

### Rules

1. Lowercase alphanumeric characters, hyphens, and dots only.
2. Must match the regex: `^[a-z0-9]+([.\-][a-z0-9]+)*$`
3. No underscores — use hyphens for word separation.
4. No leading or trailing hyphens or dots.
5. When the dataset has an explicit version, append it after a hyphen.

### Do:

```text
tasks/0003-adding-datasets/assets/dataset/semcor-3.0/
tasks/0003-adding-datasets/assets/dataset/raganato-all/
tasks/0003-adding-datasets/assets/dataset/semeval-2007-task-17/
tasks/0003-adding-datasets/assets/dataset/ontonotes-5.0/
```

### Don't:

```text
assets/dataset/semcor-3.0/     # Wrong: top-level, not in task folder
assets/dataset/SemCor_3.0/     # Wrong: uppercase and underscore
assets/dataset/-semcor/        # Wrong: leading hyphen
assets/dataset/semcor-/        # Wrong: trailing hyphen
```

* * *

## details.json

The metadata file contains all structured information about the dataset. All field names use
`snake_case`.

### Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version (e.g., `"1"`) |
| `dataset_id` | string | yes | Folder name slug |
| `name` | string | yes | Display name (e.g., "SemCor 3.0") |
| `version` | string \| null | yes | Dataset version, or `null` if unversioned |
| `short_description` | string | yes | 1-2 sentence description |
| `description_path` | string | yes in v2, no in v1 | Canonical documentation file path relative to the asset root |
| `source_paper_id` | string \| null | yes | Paper asset ID that introduced this dataset, or `null` |
| `url` | string \| null | yes | Landing page URL |
| `download_url` | string \| null | no | Direct download URL |
| `year` | int | yes | Publication or release year |
| `date_published` | string \| null | no | ISO 8601 date (`YYYY-MM-DD`), as precise as known (`YYYY` or `YYYY-MM` acceptable) |
| `authors` | list[Author] | yes | Ordered list of dataset creators |
| `institutions` | list[Institution] | yes | Unique institutions across all authors |
| `license` | string \| null | yes | License identifier (e.g., `"CC-BY-4.0"`, `"research-only"`) or `null` if unknown |
| `access_kind` | string | yes | One of: `"public"`, `"restricted"`, `"proprietary"` |
| `size_description` | string | yes | Free-form description of dataset size (e.g., "226,036 sense-annotated tokens across 352 documents") |
| `files` | list[DatasetFile] | yes | Dataset files with metadata (see below) |
| `categories` | list[string] | yes | Category slugs from `meta/categories/` |

### Author Object

Identical to the paper asset Author object.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | yes | Full name as it appears on the dataset |
| `country` | string \| null | no | ISO 3166-1 alpha-2 code (e.g., `US`, `IT`) |
| `institution` | string \| null | no | Affiliated institution name |
| `orcid` | string \| null | no | ORCID identifier |

### Institution Object

Identical to the paper asset Institution object.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | yes | Institution name in English |
| `country` | string | yes | ISO 3166-1 alpha-2 code |

### DatasetFile Object

Each entry in the `files` list describes one file in the `files/` directory.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `path` | string | yes | Relative path within the asset folder (e.g., `"files/semcor-3.0.xml"`) |
| `description` | string | yes | What this file contains |
| `format` | string | yes | File format (e.g., `"xml"`, `"csv"`, `"jsonl"`, `"tsv"`, `"zip"`) |

### Example

````json
{
  "spec_version": "2",
  "dataset_id": "semcor-3.0",
  "name": "SemCor 3.0",
  "version": "3.0",
  "short_description": "Largest manually sense-annotated corpus for English WSD, mapping all content words to WordNet 3.0 synsets.",
  "description_path": "description.md",
  "source_paper_id": "10.18653_v1_E17-1010",
  "url": "https://web.eecs.umich.edu/~miMDalMDal/downloads/smart/",
  "download_url": null,
  "year": 1998,
  "date_published": "1998",
  "authors": [
    {
      "name": "George A. Miller",
      "country": "US",
      "institution": "Princeton University",
      "orcid": null
    }
  ],
  "institutions": [
    {
      "name": "Princeton University",
      "country": "US"
    }
  ],
  "license": "research-only",
  "access_kind": "public",
  "size_description": "226,036 sense-annotated tokens across 352 documents from the Brown Corpus",
  "files": [
    {
      "path": "files/semcor-3.0.xml",
      "description": "Full SemCor corpus in XML format with WordNet 3.0 sense annotations",
      "format": "xml"
    }
  ],
  "categories": [
    "dataset",
    "wsd"
  ]
}
````

* * *

## Description Document

A detailed description of the dataset written after examining its contents. The canonical
description document is the file referenced by `details.json` `description_path`. Historical v1
assets may omit that field; in that case the canonical document defaults to `description.md`.

The description must be thorough enough that a researcher reading only this file understands what
the dataset contains, how to use it, and why it matters — without opening any data files.

### YAML Frontmatter

```yaml
---
spec_version: "2"
dataset_id: "semcor-3.0"
summarized_by_task: "0003-adding-datasets"
date_summarized: "2026-03-30"
---
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version (e.g., `"1"`) |
| `dataset_id` | string | yes | Must match the folder name |
| `summarized_by_task` | string | yes | Task ID that produced this description |
| `date_summarized` | string | yes | ISO 8601 date |

### Mandatory Sections

The description must contain these sections in this order, each as an `##` heading. Additional
sections may be added between them where useful.

* * *

#### `## Metadata`

Quick-reference block repeating key facts from `details.json` for convenience. Format:

````markdown
## Metadata

* **Name**: SemCor 3.0
* **Year**: 1998
* **Authors**: George A. Miller
* **License**: research-only
* **Access**: public
* **Size**: 226,036 sense-annotated tokens across 352 documents
````

* * *

#### `## Overview`

2-4 paragraphs describing what the dataset is, who created it, why it was created, and its role in
the field. This section should go beyond the `short_description` in `details.json`.

**Minimum**: 80 words.

* * *

#### `## Content & Annotation`

Detailed description of what the dataset contains and how it is annotated. This is where
domain-specific information belongs — for example, sense inventory used, annotation scheme, POS
coverage, languages, inter-annotator agreement, and annotation guidelines.

* * *

#### `## Statistics`

Detailed size and distribution information. Tables are encouraged. Include number of documents,
tokens, annotations, senses, splits, and any other relevant counts.

* * *

#### `## Usage Notes`

How to load the data, known quirks, preprocessing needed, file format details, common pitfalls, and
recommended tools or libraries.

* * *

#### `## Main Ideas`

Bullet points of the most important takeaways relevant to **this project**. Focus on what is
actionable — how to use the dataset, known limitations, comparisons to alternatives.

**Minimum**: 3 bullet points.

* * *

#### `## Summary`

A synthesis in 2-3 paragraphs:

1. **What the dataset is** — scope, content, and purpose
2. **How it fits the project** — practical implications, limitations, and connection to research
   goals
3. (Optional) **Comparison to alternatives** — how this dataset compares to similar resources

**Minimum**: 100 words total across the paragraphs.

* * *

### Quality Criteria

A good description:

* Is self-contained — a reader understands the dataset without opening any files
* Contains specific numbers for sizes, counts, and distributions
* Describes the annotation scheme in enough detail to use the data
* Identifies limitations (coverage gaps, known errors, annotation quality)
* Connects the dataset to this project's specific research needs
* Includes practical loading and usage guidance

A bad description:

* Uses vague language ("a large dataset", "many annotations")
* Omits annotation details
* Does not mention known limitations
* Is under 400 words total

* * *

## Dataset Files

### Location

All dataset files go in the `files/` subdirectory within the dataset asset folder.

### Naming Convention

Use descriptive, lowercase slug names with the appropriate file extension:
````text
<dataset-name>-<version>.<ext>
````

Examples:
* `semcor-3.0.xml`
* `raganato-all-test.xml`
* `semeval-2007-task-17-train.csv`

### Accepted File Types

* `.xml` — structured annotation formats
* `.csv` / `.tsv` — tabular data
* `.jsonl` / `.json` — JSON-based formats
* `.conll` — CoNLL column format
* `.txt` — plain text
* `.zip` / `.tar.gz` — compressed archives (when original format is an archive)

Multiple files per dataset are common. List all files in `details.json` with descriptions.

* * *

## Verification Rules

### Errors

Errors indicate structural problems that must be fixed.

| Code | Description |
| --- | --- |
| `DA-E001` | `details.json` is missing or not valid JSON |
| `DA-E002` | The canonical description document is missing |
| `DA-E003` | `files/` directory is missing or empty |
| `DA-E004` | `dataset_id` in `details.json` does not match folder name |
| `DA-E005` | Required field missing in `details.json` |
| `DA-E007` | `dataset_id` in the canonical description document frontmatter does not match folder name |
| `DA-E008` | A file listed in `details.json` `files[].path` does not exist |
| `DA-E009` | The canonical description document is missing a mandatory section |
| `DA-E010` | `access_kind` is not one of the allowed values |
| `DA-E011` | Folder name does not match the dataset ID format |
| `DA-E012` | The canonical description document is missing YAML frontmatter |
| `DA-E013` | `spec_version` is missing from `details.json` or the canonical description document frontmatter |
| `DA-E016` | An entry in `files` is not a valid DatasetFile object (missing `path`, `description`, or `format`) |

### Warnings

Warnings indicate quality concerns that should be addressed but do not block progress.

| Code | Description |
| --- | --- |
| `DA-W001` | The canonical description document total word count is under 400 |
| `DA-W003` | Main Ideas section has fewer than 3 bullet points |
| `DA-W004` | Summary section does not have 2-3 paragraphs |
| `DA-W005` | A category in `details.json` does not exist in `meta/categories/` |
| `DA-W007` | No author has a non-null `country` field |
| `DA-W008` | `short_description` in `details.json` is empty or under 10 words |
| `DA-W009` | `date_published` is `null` (only `year` is known) |
| `DA-W010` | A `country` field is not a valid ISO 3166-1 alpha-2 code, or an institution has `null` country |
| `DA-W011` | `date_published` does not match ISO 8601 format (`YYYY`, `YYYY-MM`, or `YYYY-MM-DD`) |
| `DA-W012` | `size_description` is empty |
| `DA-W013` | Overview section word count is under 80 |

* * *

## Complete Example

### Folder Structure

```text
tasks/0003-adding-datasets/assets/dataset/semcor-3.0/ ├── details.json ├── description.md └── files/
└── semcor-3.0.xml
```

### details.json

```json
{
  "spec_version": "2",
  "dataset_id": "semcor-3.0",
  "name": "SemCor 3.0",
  "version": "3.0",
  "short_description": "Largest manually sense-annotated corpus for English WSD, mapping all content words to WordNet 3.0 synsets.",
  "description_path": "description.md",
  "source_paper_id": null,
  "url": "https://web.eecs.umich.edu/~miMDalMDal/downloads/smart/",
  "download_url": null,
  "year": 1998,
  "date_published": "1998",
  "authors": [
    {
      "name": "George A. Miller",
      "country": "US",
      "institution": "Princeton University",
      "orcid": null
    }
  ],
  "institutions": [
    {
      "name": "Princeton University",
      "country": "US"
    }
  ],
  "license": "research-only",
  "access_kind": "public",
  "size_description": "226,036 sense-annotated tokens across 352 documents from the Brown Corpus",
  "files": [
    {
      "path": "files/semcor-3.0.xml",
      "description": "Full SemCor corpus in XML format with WordNet 3.0 sense annotations",
      "format": "xml"
    }
  ],
  "categories": [
    "dataset",
    "wsd"
  ]
}
```

### Description Document

````markdown
---
spec_version: "2"
dataset_id: "semcor-3.0"
summarized_by_task: "0003-adding-datasets"
date_summarized: "2026-03-30"
---

# SemCor 3.0

## Metadata

* **Name**: SemCor 3.0
* **Year**: 1998
* **Authors**: George A. Miller
* **License**: research-only
* **Access**: public
* **Size**: 226,036 sense-annotated tokens across 352 documents

## Overview

SemCor is the largest manually sense-annotated corpus for English word
sense disambiguation. Originally created at Princeton University as part
of the WordNet project, it maps content words in a subset of the Brown
Corpus to WordNet synsets. Version 3.0 aligns annotations with WordNet
3.0, making it compatible with the Raganato unified evaluation framework.

SemCor serves as the primary training corpus for virtually all supervised
WSD systems. Its size and quality make it the de facto standard, though
its age means it does not cover modern vocabulary or domains.

## Content & Annotation

The corpus contains 352 documents from the Brown Corpus, a balanced
corpus of American English published in 1961. Every content word (noun,
verb, adjective, adverb) is manually annotated with its WordNet 3.0
synset. Annotation was performed by trained lexicographers at Princeton.

The sense inventory is WordNet 3.0, containing approximately 117,659
synsets. Annotations cover all four open-class parts of speech. The
corpus uses an XML format with sentence boundaries, tokenization, lemma,
POS tag, and sense key for each annotated token.

## Statistics

| Metric                    | Value   |
|---------------------------|---------|
| Documents                 | 352     |
| Sense-annotated tokens    | 226,036 |
| Unique lemmas             | ~33,000 |
| Unique synsets referenced | ~26,000 |
| POS coverage              | noun, verb, adj, adv |

## Usage Notes

SemCor is typically loaded via the NLTK library (`nltk.corpus.semcor`)
or as preprocessed XML from the Raganato framework. When using it as
training data, note that verb senses are underrepresented relative to
nouns. The Brown Corpus source means the text is from 1961, so modern
vocabulary and usage patterns are absent.

## Main Ideas

* SemCor is the standard training corpus for supervised WSD — all
  experiments in this project should use it as the primary training
  source
* Verb sense coverage is weaker than noun coverage, which partly
  explains why verb disambiguation remains the hardest subproblem
* The 1961 source text limits coverage of modern vocabulary — consider
  supplementing with more recent annotated data for contemporary
  domains

## Summary

SemCor 3.0 is the foundational training resource for English word sense
disambiguation, providing 226,036 manually annotated tokens mapped to
WordNet 3.0 synsets across 352 documents from the Brown Corpus.

For this project, SemCor is essential as the primary training corpus for
any supervised WSD approach. Its main limitations — aging source text and
uneven POS coverage — should inform experimental design, particularly
when evaluating verb disambiguation performance.

## Aggregator-Derived Project Registry Fields

Dataset `details.json` does not store project registry metadata such as
which task added the dataset to the project overview or when it first
appeared in the project. Those fields are derived by framework
aggregators:

* `added_by_task` is derived from the owning task folder path when the
  dataset lives under `tasks/<task_id>/assets/dataset/<dataset_id>/`.
* `date_added` is derived from the owning task timing, preferring the
  task `end_time` and falling back to `start_time` when `end_time` is
  unavailable.
````
