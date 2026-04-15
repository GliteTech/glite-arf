# Predictions Asset Specification

**Version**: 2

* * *

## Purpose

This specification defines the folder structure, metadata format, and description requirements for
predictions assets in the project. A predictions asset captures the output of a WSD model (or any
disambiguation system) on a specific evaluation dataset, enabling reproducible comparison across
methods.

**Producer**: The implementation subagent of a task that runs a model on an evaluation dataset and
records per-instance predictions.

**Consumers**:
* **Analysis subagents** — load predictions to compute metrics and comparisons
* **Aggregator scripts** — combine predictions metadata across tasks
* **Human reviewers** — evaluate model coverage and quality at checkpoints
* **Verificator scripts** — validate structure and completeness

* * *

## Asset Folder Structure

Predictions assets are created **inside the task folder** that produces them. Each predictions set
is stored in its own subfolder under the task's `assets/predictions/` directory:

```text
tasks/<task_id>/assets/predictions/<predictions_id>/
├── details.json       # Structured metadata (required)
├── description.md     # Example canonical description document
└── files/             # Prediction file(s) (required, at least one file)
    ├── <filename>.jsonl
    └── <filename>.csv
```

The top-level `assets/predictions/` directory is reserved for aggregated views produced by
aggregator scripts — tasks must never write directly to it.

The `files/` subdirectory holds the actual prediction output. At least one file must be present —
predictions assets without files are not added to the project.

The canonical documentation file path is stored in `details.json` `description_path`. New v2 assets
must declare this field explicitly. Historical v1 assets may omit it; in that case consumers fall
back to `description.md`.

* * *

## Predictions ID

The predictions ID determines the folder name and serves as the canonical identifier throughout the
project.

### Rules

1. Lowercase alphanumeric characters, hyphens, and dots only.
2. Must match the regex: `^[a-z0-9]+([.\-][a-z0-9]+)*$`
3. No underscores — use hyphens for word separation.
4. No leading or trailing hyphens or dots.
5. Use a descriptive slug that includes the model name and evaluation dataset.

### Do:

```text
tasks/t0020_run_bert_wsd/assets/predictions/bert-base-wsd-on-raganato-all/
tasks/t0021_run_gpt4o/assets/predictions/gpt4o-zero-shot-semeval-2015/
tasks/t0022_run_sandwich/assets/predictions/sandwich-44m-on-raganato-all/
```

### Don't:

```text
assets/predictions/bert-base-wsd/        # Wrong: top-level, not in task folder
assets/predictions/BERT_Base_WSD/        # Wrong: uppercase and underscore
assets/predictions/-bert-base/           # Wrong: leading hyphen
assets/predictions/bert-base-/           # Wrong: trailing hyphen
```

* * *

## details.json

The metadata file contains all structured information about the predictions. All field names use
`snake_case`.

### Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version (e.g., `"1"`) |
| `predictions_id` | string | yes | Folder name slug |
| `name` | string | yes | Display name (e.g., "BERT-base WSD on Raganato ALL") |
| `short_description` | string | yes | 1-2 sentence description |
| `description_path` | string | yes in v2, no in v1 | Canonical documentation file path relative to the asset root |
| `model_id` | string \| null | yes | Model asset ID, or `null` for API-only models without a local asset |
| `model_description` | string | yes | Free-form model description (always required, even when `model_id` is provided) |
| `dataset_ids` | list[string] | yes | Dataset asset IDs that were evaluated |
| `prediction_format` | string | yes | Format of prediction files (e.g., `"jsonl"`, `"csv"`, `"tsv"`) |
| `prediction_schema` | string | yes | Free-form description of per-instance fields in the prediction files |
| `instance_count` | int \| null | no | Total number of prediction instances |
| `metrics_at_creation` | object \| null | no | Metrics computed at creation time (e.g., `{"f1": 0.821, "accuracy": 0.834}`) |
| `files` | list[PredictionFile] | yes | Prediction files with metadata (see below) |
| `categories` | list[string] | yes | Category slugs from `meta/categories/` |
| `created_by_task` | string | yes | Task ID that produced these predictions |
| `date_created` | string | yes | ISO 8601 date when predictions were generated |

### PredictionFile Object

Each entry in the `files` list describes one file in the `files/` directory.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `path` | string | yes | Relative path within the asset folder (e.g., `"files/predictions.jsonl"`) |
| `description` | string | yes | What this file contains |
| `format` | string | yes | File format (e.g., `"jsonl"`, `"csv"`, `"tsv"`) |

### Example

````json
{
  "spec_version": "2",
  "predictions_id": "bert-base-wsd-on-raganato-all",
  "name": "BERT-base WSD on Raganato ALL",
  "short_description": "Per-instance WSD predictions from a fine-tuned BERT-base model evaluated on the full Raganato ALL concatenation of five benchmark datasets.",
  "description_path": "description.md",
  "model_id": "bert-base-wsd-finetuned",
  "model_description": "BERT-base (110M params) fine-tuned on SemCor 3.0 for word sense disambiguation using a nearest-neighbor sense embedding approach.",
  "dataset_ids": [
    "raganato-all"
  ],
  "prediction_format": "jsonl",
  "prediction_schema": "Each line is a JSON object with fields: instance_id (string), token (string), gold_sense_key (string), predicted_sense_key (string), is_correct (boolean), confidence (float or null).",
  "instance_count": 7253,
  "metrics_at_creation": {
    "f1": 0.821,
    "accuracy": 0.834,
    "noun_f1": 0.861,
    "verb_f1": 0.694
  },
  "files": [
    {
      "path": "files/predictions-raganato-all.jsonl",
      "description": "Per-instance predictions on Raganato ALL (SE2 + SE3 + SE07 + SE13 + SE15)",
      "format": "jsonl"
    }
  ],
  "categories": [
    "supervised-wsd",
    "wsd-evaluation"
  ],
  "created_by_task": "t0020_run_bert_wsd",
  "date_created": "2026-04-01"
}
````

* * *

## Description Document

A detailed description of the predictions written after examining the output. The canonical
description document is the file referenced by `details.json` `description_path`. Historical v1
assets may omit that field; in that case the canonical document defaults to `description.md`.

The description must be thorough enough that a researcher reading only this file understands what
model produced the predictions, on which data, in what format, and what the results look like —
without opening any data files.

### YAML Frontmatter

```yaml
---
spec_version: "2"
predictions_id: "bert-base-wsd-on-raganato-all"
documented_by_task: "t0020_run_bert_wsd"
date_documented: "2026-04-01"
---
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version (e.g., `"1"`) |
| `predictions_id` | string | yes | Must match the folder name |
| `documented_by_task` | string | yes | Task ID that produced this description |
| `date_documented` | string | yes | ISO 8601 date |

### Mandatory Sections

The description must contain these sections in this order, each as an `##` heading. Additional
sections may be added between them where useful.

* * *

#### `## Metadata`

Quick-reference block repeating key facts from `details.json` for convenience. Format:

````markdown
## Metadata

* **Name**: BERT-base WSD on Raganato ALL
* **Model**: BERT-base (110M params) fine-tuned on SemCor 3.0
* **Datasets**: raganato-all
* **Format**: jsonl
* **Instances**: 7,253
* **Created by**: t0020_run_bert_wsd
````

* * *

#### `## Overview`

2-4 paragraphs describing what these predictions represent, why they were generated, and their role
in the project. This section should go beyond the `short_description` in `details.json`.

**Minimum**: 80 words.

* * *

#### `## Model`

Description of the model that produced these predictions. Include architecture, training data,
hyperparameters, and any other relevant details about the model configuration used.

* * *

#### `## Data`

Description of the evaluation dataset(s) used. Include dataset sizes, splits, and any preprocessing
applied before running the model.

* * *

#### `## Prediction Format`

Detailed description of the prediction file format. Include field names, types, example rows, and
any conventions used (e.g., how confidence scores are normalized, how multi-word expressions are
handled).

* * *

#### `## Metrics`

Metrics computed from these predictions. Include overall scores and any per-category or per-dataset
breakdowns. Use tables where appropriate.

* * *

#### `## Main Ideas`

Bullet points of the most important takeaways relevant to **this project**. Focus on what is
actionable — performance insights, error patterns, comparisons to baselines.

**Minimum**: 3 bullet points.

* * *

#### `## Summary`

A synthesis in 2-3 paragraphs:

1. **What these predictions are** — model, data, and purpose
2. **Key findings** — headline results and their significance for the project
3. (Optional) **Comparison to baselines** — how this model compares to others

**Minimum**: 100 words total across the paragraphs.

* * *

### Quality Criteria

A good description:

* Is self-contained — a reader understands the predictions without opening files
* Contains specific numbers for instance counts, metrics, and breakdowns
* Describes the prediction format in enough detail to parse the files
* Identifies limitations (dataset coverage gaps, known model weaknesses)
* Connects the predictions to this project's specific research needs

A bad description:

* Uses vague language ("good results", "many predictions")
* Omits metric values
* Does not describe the prediction file format
* Is under 400 words total

* * *

## Prediction Files

### Location

All prediction files go in the `files/` subdirectory within the predictions asset folder.

### Naming Convention

Use descriptive, lowercase slug names with the appropriate file extension:
````text
predictions-<dataset-slug>.<ext>
````

Examples:
* `predictions-raganato-all.jsonl`
* `predictions-semeval-2015.csv`
* `predictions-senseval-2.tsv`

### Accepted File Types

* `.jsonl` — JSON Lines (one JSON object per line, preferred)
* `.csv` / `.tsv` — tabular data
* `.json` — single JSON array or object
* `.txt` — plain text predictions

Multiple files per predictions asset are common (e.g., one per evaluation subset). List all files in
`details.json` with descriptions.

### File Size

Prediction files larger than 3 MB MUST be gzip-compressed to `.jsonl.gz` before committing. The
repository `.gitattributes` tracks `*.jsonl.gz` via Git LFS. Uncompressed files exceeding the 5 MB
pre-commit limit will be rejected.

* * *

## Verification Rules

### Errors

Errors indicate structural problems that must be fixed.

| Code | Description |
| --- | --- |
| `PR-E001` | `details.json` is missing or not valid JSON |
| `PR-E002` | The canonical description document is missing |
| `PR-E003` | `files/` directory is missing or empty |
| `PR-E004` | `predictions_id` in `details.json` does not match folder name |
| `PR-E005` | Required field missing in `details.json` |
| `PR-E007` | `predictions_id` in the canonical description document frontmatter does not match folder name |
| `PR-E008` | A file listed in `details.json` `files[].path` does not exist |
| `PR-E009` | The canonical description document is missing a mandatory section |
| `PR-E010` | `prediction_format` is empty |
| `PR-E011` | Folder name does not match the predictions ID format |
| `PR-E012` | The canonical description document is missing YAML frontmatter |
| `PR-E013` | `spec_version` is missing from `details.json` or the canonical description document frontmatter |
| `PR-E016` | An entry in `files` is not a valid PredictionFile object (missing `path`, `description`, or `format`) |

### Warnings

Warnings indicate quality concerns that should be addressed but do not block progress.

| Code | Description |
| --- | --- |
| `PR-W001` | The canonical description document total word count is under 400 |
| `PR-W003` | Main Ideas section has fewer than 3 bullet points |
| `PR-W004` | Summary section does not have 2-3 paragraphs |
| `PR-W005` | A category in `details.json` does not exist in `meta/categories/` |
| `PR-W008` | `short_description` in `details.json` is empty or under 10 words |
| `PR-W013` | Overview section word count is under 80 |
| `PR-W014` | `model_id` is null (no model asset linked) |
| `PR-W015` | `dataset_ids` is empty (no dataset assets linked) |
| `PR-W016` | `prediction_schema` is under 10 words |
| `PR-W017` | `instance_count` is null |

* * *

## Complete Example

### Folder Structure

```text
tasks/t0020_run_bert_wsd/assets/predictions/bert-base-wsd-on-raganato-all/ ├── details.json ├──
description.md └── files/ └── predictions-raganato-all.jsonl
```

### details.json

```json
{
  "spec_version": "2",
  "predictions_id": "bert-base-wsd-on-raganato-all",
  "name": "BERT-base WSD on Raganato ALL",
  "short_description": "Per-instance WSD predictions from a fine-tuned BERT-base model evaluated on the full Raganato ALL concatenation of five benchmark datasets.",
  "description_path": "description.md",
  "model_id": "bert-base-wsd-finetuned",
  "model_description": "BERT-base (110M params) fine-tuned on SemCor 3.0 for word sense disambiguation using a nearest-neighbor sense embedding approach.",
  "dataset_ids": [
    "raganato-all"
  ],
  "prediction_format": "jsonl",
  "prediction_schema": "Each line is a JSON object with fields: instance_id (string), token (string), gold_sense_key (string), predicted_sense_key (string), is_correct (boolean), confidence (float or null).",
  "instance_count": 7253,
  "metrics_at_creation": {
    "f1": 0.821,
    "accuracy": 0.834,
    "noun_f1": 0.861,
    "verb_f1": 0.694
  },
  "files": [
    {
      "path": "files/predictions-raganato-all.jsonl",
      "description": "Per-instance predictions on Raganato ALL (SE2 + SE3 + SE07 + SE13 + SE15)",
      "format": "jsonl"
    }
  ],
  "categories": [
    "supervised-wsd",
    "wsd-evaluation"
  ],
  "created_by_task": "t0020_run_bert_wsd",
  "date_created": "2026-04-01"
}
```

### Description Document

````markdown
---
spec_version: "2"
predictions_id: "bert-base-wsd-on-raganato-all"
documented_by_task: "t0020_run_bert_wsd"
date_documented: "2026-04-01"
---

# BERT-base WSD on Raganato ALL

## Metadata

* **Name**: BERT-base WSD on Raganato ALL
* **Model**: BERT-base (110M params) fine-tuned on SemCor 3.0
* **Datasets**: raganato-all
* **Format**: jsonl
* **Instances**: 7,253
* **Created by**: t0020_run_bert_wsd

## Overview

These predictions capture the per-instance output of a fine-tuned BERT-base
model on the complete Raganato ALL evaluation benchmark. The benchmark
concatenates five standard all-words WSD datasets: Senseval-2, Senseval-3,
SemEval-2007, SemEval-2013, and SemEval-2015, totaling 7,253 instances.

The predictions serve as a supervised baseline for comparison against
LLM-based and knowledge-based approaches. Each instance includes the
model's predicted sense key, the gold sense key, a correctness flag, and
a confidence score where available. This enables fine-grained error
analysis by part of speech, polysemy level, and evaluation subset.

## Model

The model is BERT-base-uncased (110M parameters) fine-tuned on SemCor 3.0
for word sense disambiguation. The approach encodes the target word in
context using BERT, then selects the nearest WordNet 3.0 sense embedding
via cosine similarity. Training used AdamW with learning rate 2e-5, batch
size 32, and 4 epochs over SemCor. No additional training data beyond
SemCor was used.

## Data

The evaluation dataset is Raganato ALL — the standard concatenation of
five all-words WSD benchmarks mapped to WordNet 3.0:

| Subset     | Instances |
|------------|-----------|
| Senseval-2 | 2,282     |
| Senseval-3 | 1,850     |
| SemEval-07 | 455       |
| SemEval-13 | 1,644     |
| SemEval-15 | 1,022     |
| **ALL**    | **7,253** |

No preprocessing beyond standard tokenization and lemmatization was
applied. Sense candidates were retrieved from WordNet 3.0 using the
gold lemma and POS tag.

## Prediction Format

Each line of `predictions-raganato-all.jsonl` is a JSON object:
````
{ "instance_id": "senseval2.d000.s000.t000", "token": "art", "gold_sense_key": "art%1:06:00::",
"predicted_sense_key": "art%1:06:00::", "is_correct": true, "confidence": 0.91 }
```text

Fields:
* `instance_id` — unique instance identifier from the Raganato framework
* `token` — the target word as it appears in context
* `gold_sense_key` — the gold-standard WordNet 3.0 sense key
* `predicted_sense_key` — the model's predicted sense key
* `is_correct` — whether the prediction matches the gold sense
* `confidence` — model confidence score (0.0-1.0), or null if unavailable

## Metrics

| Metric   | Value  |
|----------|--------|
| F1 (ALL) | **82.1** |
| Accuracy | **83.4** |
| Noun F1  | **86.1** |
| Verb F1  | **69.4** |

The MFS baseline on Raganato ALL is **65.5 F1**, so this model exceeds it
by **+16.6 F1 points**. Verb disambiguation remains the weakest category,
consistent with findings in the literature.

## Main Ideas

* BERT-base fine-tuned on SemCor achieves **82.1 F1** on Raganato ALL,
  establishing a strong supervised baseline for this project
* Verb disambiguation at **69.4 F1** lags nouns by **16.7 points**,
  confirming that verbs remain the primary bottleneck
* Per-instance predictions with confidence scores enable detailed error
  analysis — instances with low confidence correlate with polysemous
  words and rare senses

## Summary

This predictions asset contains the per-instance output of a fine-tuned
BERT-base model on the Raganato ALL benchmark, the standard five-dataset
concatenation for English all-words WSD evaluation. The model was trained
on SemCor 3.0 and uses a nearest-neighbor sense embedding approach.

The model achieves **82.1 F1** overall, with strong noun performance
(**86.1 F1**) but weaker verb disambiguation (**69.4 F1**). These
predictions serve as the primary supervised baseline for comparing against
LLM-based approaches and hybrid methods in this project.
```
