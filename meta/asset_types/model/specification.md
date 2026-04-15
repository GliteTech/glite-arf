# Model Asset Specification

**Version**: 3

* * *

## Purpose

This specification defines the folder structure, metadata format, and description requirements for
model assets in the project. A model asset represents a trained machine learning model produced by a
task, including its weights, configuration, and documentation.

**Producer**: The implementation subagent of a task that trains or fine-tunes a model.

**Consumers**:
* **Implementation subagents** -- load models for inference or further fine-tuning
* **Aggregator scripts** -- combine model metadata across tasks
* **Human reviewers** -- evaluate model coverage at checkpoints
* **Verificator scripts** -- validate structure and completeness

* * *

## Asset Folder Structure

Model assets are created **inside the task folder** that produces them. Each model is stored in its
own subfolder under the task's `assets/model/` directory:

```text
tasks/<task_id>/assets/model/<model_id>/
├── details.json       # Structured metadata (required)
├── description.md     # Example canonical description document
└── files/             # Model file(s) (required, at least one file)
    ├── model.pt
    └── config.json
```

The top-level `assets/model/` directory is reserved for aggregated views produced by aggregator
scripts -- tasks must never write directly to it.

The `files/` subdirectory holds the actual model artifacts (weights, configs, tokenizer files,
etc.). At least one file must be present.

The canonical documentation file path is stored in `details.json` `description_path`. New v2 assets
must declare this field explicitly. Historical v1 assets may omit it; in that case consumers fall
back to `description.md`.

* * *

## Model ID

The model ID determines the folder name and serves as the canonical identifier throughout the
project.

### Rules

1. Lowercase alphanumeric characters, hyphens, and dots only.
2. Must match the regex: `^[a-z0-9]+([.\-][a-z0-9]+)*$`
3. No underscores -- use hyphens for word separation.
4. No leading or trailing hyphens or dots.
5. When the model has an explicit version, append it after a hyphen.

### Do:

```text
tasks/t0020_train_baseline/assets/model/bert-base-wsd-v1/
tasks/t0025_finetune_deberta/assets/model/deberta-large-semcor-1.0/
tasks/t0030_train_biencoder/assets/model/biencoder-wsd-0.1/
```

### Don't:

```text
assets/model/bert-base-wsd-v1/        # Wrong: top-level, not in task folder
assets/model/BERT_Base_WSD/           # Wrong: uppercase and underscore
assets/model/-bert-wsd/               # Wrong: leading hyphen
assets/model/bert-wsd-/               # Wrong: trailing hyphen
```

* * *

## details.json

The metadata file contains all structured information about the model. All field names use
`snake_case`.

### Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version (e.g., `"1"`) |
| `model_id` | string | yes | Folder name slug |
| `name` | string | yes | Display name (e.g., "BERT Base WSD v1") |
| `version` | string | yes | Model version (e.g., `"1.0.0"`) |
| `short_description` | string | yes | 1-2 sentence description |
| `description_path` | string | yes in v2, no in v1 | Canonical documentation file path relative to the asset root |
| `framework` | string | yes | One of: `"pytorch"`, `"tensorflow"`, `"jax"`, `"onnx"`, `"other"` |
| `base_model` | string \| null | yes | Pretrained model identifier (e.g., `"bert-base-uncased"`) or `null` if trained from scratch |
| `base_model_source` | string \| null | no | Source of the base model (e.g., `"huggingface"`, `"torchvision"`) |
| `architecture` | string | yes | Free-form architecture description (e.g., "BERT-base with linear WSD head") |
| `training_task_id` | string | yes | Task ID that trained this model |
| `training_dataset_ids` | list[string] | yes | Dataset asset IDs used for training |
| `hyperparameters` | object \| null | no | Free-form JSON object with training hyperparameters |
| `training_metrics` | object \| null | no | Free-form JSON object with training metrics (loss, accuracy, etc.) |
| `files` | list[ModelFile] | yes | Model files with metadata (see below) |
| `categories` | list[string] | yes | Category slugs from `meta/categories/` |
| `created_by_task` | string | yes | Task ID that created this model |
| `date_created` | string | yes | ISO 8601 date when the model was created |

### ModelFile Object

Each entry in the `files` list describes one file in the `files/` directory.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `path` | string | yes | Relative path within the asset folder (e.g., `"files/model.pt"`) |
| `description` | string | yes | What this file contains |
| `format` | string | yes | File format (e.g., `"pt"`, `"safetensors"`, `"json"`, `"bin"`, `"onnx"`) |

### Example

````json
{
  "spec_version": "2",
  "model_id": "bert-base-wsd-v1",
  "name": "BERT Base WSD v1",
  "version": "1.0.0",
  "short_description": "BERT-base fine-tuned on SemCor 3.0 for all-words WSD with a linear classification head over WordNet 3.0 synsets.",
  "description_path": "description.md",
  "framework": "pytorch",
  "base_model": "bert-base-uncased",
  "base_model_source": "huggingface",
  "architecture": "BERT-base (12 layers, 768 hidden, 110M params) with a linear WSD classification head mapping contextual embeddings to WordNet 3.0 synset probabilities",
  "training_task_id": "t0020_train_baseline",
  "training_dataset_ids": [
    "semcor-3.0"
  ],
  "hyperparameters": {
    "learning_rate": 2e-5,
    "batch_size": 32,
    "epochs": 10,
    "optimizer": "AdamW",
    "weight_decay": 0.01,
    "warmup_steps": 500,
    "max_seq_length": 256
  },
  "training_metrics": {
    "best_val_f1": 0.742,
    "best_val_loss": 0.83,
    "final_train_loss": 0.41,
    "training_time_hours": 2.5
  },
  "files": [
    {
      "path": "files/model.pt",
      "description": "PyTorch model weights (state_dict)",
      "format": "pt"
    },
    {
      "path": "files/config.json",
      "description": "Model architecture configuration",
      "format": "json"
    }
  ],
  "categories": [
    "supervised-wsd"
  ],
  "created_by_task": "t0020_train_baseline",
  "date_created": "2026-04-01"
}
````

* * *

## Description Document

A detailed description of the model written after training is complete. The canonical description
document is the file referenced by `details.json` `description_path`. Historical v1 assets may omit
that field; in that case the canonical document defaults to `description.md`.

The description must be thorough enough that a researcher reading only this file understands the
model's architecture, training procedure, and performance -- without inspecting any model files.

### YAML Frontmatter

```yaml
---
spec_version: "2"
model_id: "bert-base-wsd-v1"
documented_by_task: "t0020_train_baseline"
date_documented: "2026-04-01"
---
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version (e.g., `"1"`) |
| `model_id` | string | yes | Must match the folder name |
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

* **Name**: BERT Base WSD v1
* **Version**: 1.0.0
* **Framework**: pytorch
* **Base model**: bert-base-uncased (huggingface)
* **Training task**: t0020_train_baseline
* **Date created**: 2026-04-01
````

* * *

#### `## Overview`

2-4 paragraphs describing what the model does, why it was trained, and its role in the project. This
section should go beyond the `short_description` in `details.json`.

**Minimum**: 80 words.

* * *

#### `## Architecture`

Detailed description of the model architecture:

* Base model and its configuration
* Any modifications or additions (classification heads, adapters, etc.)
* Input/output format and dimensions
* Number of parameters (total and trainable)

* * *

#### `## Training`

Detailed description of the training procedure:

* Datasets used and their sizes
* Hyperparameters (learning rate, batch size, epochs, optimizer, etc.)
* Training hardware and compute time
* Training curves or convergence behavior
* Any data augmentation or preprocessing

* * *

#### `## Evaluation`

Performance metrics on evaluation datasets:

* Per-dataset and per-subset results
* Comparison to baselines and published results
* Statistical significance tests if available
* Error analysis highlights

* * *

#### `## Usage Notes`

How to load and use the model:

* Required dependencies and versions
* Loading code snippet
* Input format and preprocessing
* Known limitations or failure modes

* * *

#### `## Main Ideas`

Bullet points of the most important takeaways relevant to **this project**. Focus on what is
actionable -- what worked, what did not, what to try next.

**Minimum**: 3 bullet points.

* * *

#### `## Summary`

A synthesis in 2-3 paragraphs:

1. **What the model is** -- architecture, training data, and purpose
2. **How it performs** -- key metrics and comparison to alternatives
3. (Optional) **Next steps** -- improvements, follow-up experiments

**Minimum**: 100 words total across the paragraphs.

* * *

### Quality Criteria

A good description:

* Is self-contained -- a reader understands the model without inspecting files
* Contains specific numbers for metrics, parameters, and training details
* Describes the architecture in enough detail to reproduce the model
* Identifies limitations (failure cases, dataset biases, scalability)
* Connects the model to this project's specific research needs
* Includes practical loading and usage guidance

A bad description:

* Uses vague language ("a large model", "good performance")
* Omits training details or hyperparameters
* Does not mention known limitations
* Is under 400 words total

* * *

## Model Files

### Location

All model files go in the `files/` subdirectory within the model asset folder.

### Naming Convention

Use descriptive, lowercase names with the appropriate file extension:
````text
<model-name>.<ext>
````

Examples:
* `model.pt`
* `model.safetensors`
* `config.json`
* `tokenizer.json`
* `vocab.txt`

### Accepted File Types

* `.pt` / `.pth` -- PyTorch model weights
* `.safetensors` -- Safe serialization format
* `.bin` -- generic binary (e.g., TensorFlow SavedModel components)
* `.onnx` -- ONNX model format
* `.json` -- configuration files
* `.txt` -- vocabulary files
* `.zip` / `.tar.gz` -- compressed archives

Multiple files per model are common. List all files in `details.json` with descriptions.

* * *

## Large File Handling

Model weight files often exceed the repository file size limit (configured in
`.pre-commit-config.yaml` under `check-added-large-files`). All model weight files must be committed
via Git LFS.

Before committing model files:

1. Verify Git LFS is initialized: `git lfs install`
2. Check `.gitattributes` for tracked extensions. If the weight file extension is not tracked, add
   it: `git lfs track "*.pt"` (or `.bin`, `.safetensors`, `.onnx`, `.npz` as appropriate)
3. Commit the updated `.gitattributes` before committing model files

Some tokenizer files (especially `tokenizer.json` for modern tokenizers like SentencePiece or BPE)
can exceed 5 MB. Check file sizes before committing and track large tokenizer files with Git LFS
alongside model weight files.

Git LFS per-file limit on GitHub is 5 GB. If a single checkpoint exceeds 5 GB, split it or store
externally with a reference file in `files/`.

The `files/` directory must always contain at least the training configuration and metadata files,
even when weights are stored via LFS. The `details.json` `files` field must list all files including
LFS-tracked ones.

* * *

## Verification Rules

### Errors

Errors indicate structural problems that must be fixed.

| Code | Description |
| --- | --- |
| `MA-E001` | `details.json` is missing or not valid JSON |
| `MA-E002` | The canonical description document is missing |
| `MA-E003` | `files/` directory is missing or empty |
| `MA-E004` | `model_id` in `details.json` does not match folder name |
| `MA-E005` | Required field missing in `details.json` |
| `MA-E007` | `model_id` in the canonical description document frontmatter does not match folder name |
| `MA-E008` | A file listed in `details.json` `files[].path` does not exist |
| `MA-E009` | The canonical description document is missing a mandatory section |
| `MA-E010` | `framework` is not one of the allowed values |
| `MA-E011` | Folder name does not match the model ID format |
| `MA-E012` | The canonical description document is missing YAML frontmatter |
| `MA-E013` | `spec_version` is missing from `details.json` or the canonical description document frontmatter |
| `MA-E016` | An entry in `files` is not a valid ModelFile object (missing `path`, `description`, or `format`) |

### Warnings

Warnings indicate quality concerns that should be addressed but do not block progress.

| Code | Description |
| --- | --- |
| `MA-W001` | The canonical description document total word count is under 400 |
| `MA-W003` | Main Ideas section has fewer than 3 bullet points |
| `MA-W004` | Summary section does not have 2-3 paragraphs |
| `MA-W005` | A category in `details.json` does not exist in `meta/categories/` |
| `MA-W008` | `short_description` in `details.json` is empty or under 10 words |
| `MA-W013` | Overview section word count is under 80 |
| `MA-W014` | `training_dataset_ids` is empty |
| `MA-W015` | `hyperparameters` is missing or empty |
| `MA-W016` | `training_metrics` is missing or empty |

* * *

## Complete Example

### Folder Structure

```text
tasks/t0020_train_baseline/assets/model/bert-base-wsd-v1/
├── details.json
├── description.md
└── files/
    ├── model.pt
    └── config.json
```

### details.json

```json
{
  "spec_version": "2",
  "model_id": "bert-base-wsd-v1",
  "name": "BERT Base WSD v1",
  "version": "1.0.0",
  "short_description": "BERT-base fine-tuned on SemCor 3.0 for all-words WSD with a linear classification head over WordNet 3.0 synsets.",
  "description_path": "description.md",
  "framework": "pytorch",
  "base_model": "bert-base-uncased",
  "base_model_source": "huggingface",
  "architecture": "BERT-base (12 layers, 768 hidden, 110M params) with a linear WSD classification head mapping contextual embeddings to WordNet 3.0 synset probabilities",
  "training_task_id": "t0020_train_baseline",
  "training_dataset_ids": [
    "semcor-3.0"
  ],
  "hyperparameters": {
    "learning_rate": 2e-5,
    "batch_size": 32,
    "epochs": 10,
    "optimizer": "AdamW",
    "weight_decay": 0.01,
    "warmup_steps": 500,
    "max_seq_length": 256
  },
  "training_metrics": {
    "best_val_f1": 0.742,
    "best_val_loss": 0.83,
    "final_train_loss": 0.41,
    "training_time_hours": 2.5
  },
  "files": [
    {
      "path": "files/model.pt",
      "description": "PyTorch model weights (state_dict)",
      "format": "pt"
    },
    {
      "path": "files/config.json",
      "description": "Model architecture configuration",
      "format": "json"
    }
  ],
  "categories": [
    "supervised-wsd"
  ],
  "created_by_task": "t0020_train_baseline",
  "date_created": "2026-04-01"
}
```

### Description Document

````markdown
---
spec_version: "2"
model_id: "bert-base-wsd-v1"
documented_by_task: "t0020_train_baseline"
date_documented: "2026-04-01"
---

# BERT Base WSD v1

## Metadata

* **Name**: BERT Base WSD v1
* **Version**: 1.0.0
* **Framework**: pytorch
* **Base model**: bert-base-uncased (huggingface)
* **Training task**: t0020_train_baseline
* **Date created**: 2026-04-01

## Overview

BERT Base WSD v1 is a supervised word sense disambiguation model built by
fine-tuning BERT-base-uncased on the SemCor 3.0 training corpus. The model
serves as the project's first baseline for comparing against more advanced
architectures and LLM-based approaches.

The model takes a sentence with a marked target word as input and predicts
the most likely WordNet 3.0 synset for that word. It uses a simple linear
classification head on top of the target word's contextual embedding,
making it lightweight and fast at inference time.

## Architecture

The model uses the standard BERT-base architecture (12 transformer layers,
768 hidden dimensions, 12 attention heads, 110M parameters) from Hugging
Face. A single linear layer maps the contextual embedding of the target
token to a probability distribution over candidate WordNet 3.0 synsets.

Total parameters: **110.5M** (110M base + 0.5M classification head).
All parameters are trainable during fine-tuning.

Input format: tokenized sentence with the target word marked by special
tokens. Maximum sequence length: 256 subword tokens.

## Training

The model was trained on SemCor 3.0 (226,036 sense-annotated tokens).
Training used AdamW optimizer with a learning rate of **2e-5**, batch size
of **32**, and linear warmup over **500** steps. The model was trained for
**10** epochs with early stopping based on validation F1.

Training was performed on a single NVIDIA A100 GPU and took approximately
**2.5 hours**. The best checkpoint was selected based on validation F1
score on a held-out 10% split of SemCor.

## Evaluation

* Raganato ALL concatenation: **74.2 F1**
* Senseval-2: **76.8 F1**
* Senseval-3: **73.1 F1**
* SemEval-2007: **68.5 F1**
* SemEval-2013: **75.0 F1**
* SemEval-2015: **74.9 F1**
* MFS baseline comparison: **+8.7 F1** over MFS (65.5)

## Usage Notes

Load the model using PyTorch and the Hugging Face transformers library:

```python
import torch
from transformers import BertModel, BertTokenizer

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")
state_dict = torch.load("files/model.pt")
model.load_state_dict(state_dict, strict=False)
```

The model requires the target word to be marked with special tokens in
the input. See the training task's code for the exact preprocessing
pipeline.

## Main Ideas

* BERT-base fine-tuned on SemCor achieves **74.2 F1** on Raganato ALL,
  establishing a solid baseline for this project
* The simple linear head approach is fast to train (2.5 hours on one
  A100) and straightforward to implement
* Verb disambiguation remains the weakest point, consistent with
  findings from Raganato2017

## Summary

BERT Base WSD v1 is a baseline supervised WSD model that fine-tunes
BERT-base-uncased on SemCor 3.0 with a linear classification head. It
achieves **74.2 F1** on the Raganato ALL benchmark, outperforming the
MFS baseline by **8.7 points**.

The model serves as the project's reference point for comparing more
advanced approaches including bi-encoders, cross-encoders, and
LLM-based methods. Its main limitation is the simple classification
head, which does not leverage sense definitions or gloss information.
```
````
