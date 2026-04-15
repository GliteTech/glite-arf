from pathlib import Path

from arf.scripts.verificators.common.paths import (
    model_asset_dir,
    model_description_path,
    model_details_path,
    model_files_dir,
)
from arf.tests.fixtures.writers import (
    write_frontmatter_md,
    write_json,
    write_text,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPEC_VERSION_FIELD: str = "spec_version"
MODEL_ID_FIELD: str = "model_id"
NAME_FIELD: str = "name"
VERSION_FIELD: str = "version"
SHORT_DESCRIPTION_FIELD: str = "short_description"
DESCRIPTION_PATH_FIELD: str = "description_path"
FRAMEWORK_FIELD: str = "framework"
BASE_MODEL_FIELD: str = "base_model"
BASE_MODEL_SOURCE_FIELD: str = "base_model_source"
ARCHITECTURE_FIELD: str = "architecture"
TRAINING_TASK_ID_FIELD: str = "training_task_id"
TRAINING_DATASET_IDS_FIELD: str = "training_dataset_ids"
HYPERPARAMETERS_FIELD: str = "hyperparameters"
TRAINING_METRICS_FIELD: str = "training_metrics"
FILES_FIELD: str = "files"
CATEGORIES_FIELD: str = "categories"
CREATED_BY_TASK_FIELD: str = "created_by_task"
DATE_CREATED_FIELD: str = "date_created"

DEFAULT_SPEC_VERSION: str = "2"
DEFAULT_MODEL_ID: str = "test-model-v1"
DEFAULT_TASK_ID: str = "t0001_test"
DEFAULT_NAME: str = "Test WSD Model"
DEFAULT_VERSION: str = "1.0"
DEFAULT_SHORT_DESCRIPTION: str = (
    "A test bi-encoder model for word sense disambiguation trained "
    "on SemCor with WordNet 3.0 sense inventory for evaluation on "
    "standard benchmarks."
)
DEFAULT_DESCRIPTION_PATH: str = "description.md"
DEFAULT_FRAMEWORK: str = "pytorch"
DEFAULT_BASE_MODEL: str = "bert-base-uncased"
DEFAULT_BASE_MODEL_SOURCE: str = "huggingface"
DEFAULT_ARCHITECTURE: str = "bi-encoder with cross-attention"
DEFAULT_TRAINING_TASK_ID: str = "t0001_test"
DEFAULT_DATE_CREATED: str = "2026-01-20"
DEFAULT_WEIGHTS_FILENAME: str = "files/model_weights.pt"

_OVERVIEW_TEXT: str = (
    "This model implements a bi-encoder architecture for word sense "
    "disambiguation. It encodes the target word in context and each "
    "candidate sense definition separately, then computes similarity "
    "scores to rank candidate senses. The model is trained on SemCor "
    "and evaluated on the Raganato unified benchmark."
)

_DESCRIPTION_BODY: str = (
    "# Test WSD Model\n\n"
    "## Metadata\n\n"
    "* **Name**: Test WSD Model\n"
    "* **Version**: 1.0\n"
    "* **Framework**: PyTorch\n"
    "* **Base model**: bert-base-uncased\n\n"
    "## Overview\n\n"
    f"{_OVERVIEW_TEXT}\n\n"
    "## Architecture\n\n"
    "The model uses a bi-encoder architecture with BERT-base as the "
    "backbone. The context encoder processes the target word in its "
    "surrounding sentence. The gloss encoder processes each candidate "
    "sense definition from WordNet 3.0. Cross-attention layers align "
    "the context and gloss representations before computing the final "
    "similarity score.\n\n"
    "## Training\n\n"
    "Trained on SemCor (226036 tokens) for 20 epochs with AdamW "
    "optimizer, learning rate 2e-5, batch size 32, and linear warmup "
    "over the first 10% of steps. Training completed on a single "
    "A100 GPU in approximately 4 hours.\n\n"
    "## Evaluation\n\n"
    "Evaluated on the Raganato ALL concatenation achieving 71.3 F1 "
    "with per-POS breakdown: nouns 72.1 F1, verbs 57.4 F1, "
    "adjectives 78.5 F1, adverbs 83.6 F1.\n\n"
    "## Usage Notes\n\n"
    "Load the model weights with `torch.load` and use the provided "
    "inference script for batch prediction.\n\n"
    "## Main Ideas\n\n"
    "* Bi-encoder architecture enables efficient sense ranking\n"
    "* Cross-attention improves context-gloss alignment\n"
    "* Verb disambiguation remains the primary bottleneck\n\n"
    "## Summary\n\n"
    "This bi-encoder WSD model uses BERT-base as a backbone with "
    "cross-attention layers for context-gloss alignment. Trained on "
    "SemCor it achieves competitive results on the Raganato benchmark. "
    "The model demonstrates strong performance on nouns and adjectives "
    "while verbs remain challenging as expected from literature.\n"
)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def build_model_asset(
    *,
    repo_root: Path,
    model_id: str = DEFAULT_MODEL_ID,
    task_id: str = DEFAULT_TASK_ID,
    spec_version: str = DEFAULT_SPEC_VERSION,
    name: str = DEFAULT_NAME,
    version: str = DEFAULT_VERSION,
    short_description: str = DEFAULT_SHORT_DESCRIPTION,
    description_path: str = DEFAULT_DESCRIPTION_PATH,
    framework: str = DEFAULT_FRAMEWORK,
    base_model: str | None = DEFAULT_BASE_MODEL,
    base_model_source: str | None = DEFAULT_BASE_MODEL_SOURCE,
    architecture: str = DEFAULT_ARCHITECTURE,
    training_task_id: str = DEFAULT_TRAINING_TASK_ID,
    training_dataset_ids: list[str] | None = None,
    hyperparameters: dict[str, object] | None = None,
    training_metrics: dict[str, object] | None = None,
    categories: list[str] | None = None,
    date_created: str = DEFAULT_DATE_CREATED,
    include_description: bool = True,
    include_files_dir: bool = True,
    details_overrides: dict[str, object] | None = None,
    description_body: str | None = None,
) -> Path:
    asset_dir: Path = model_asset_dir(
        model_id=model_id,
        task_id=task_id,
    )
    asset_dir.mkdir(parents=True, exist_ok=True)

    resolved_dataset_ids: list[str] = (
        training_dataset_ids if training_dataset_ids is not None else ["test-dataset"]
    )
    resolved_hyperparameters: dict[str, object] | None = (
        hyperparameters
        if hyperparameters is not None
        else {
            "learning_rate": 2e-5,
            "batch_size": 32,
            "epochs": 20,
        }
    )
    resolved_training_metrics: dict[str, object] | None = (
        training_metrics
        if training_metrics is not None
        else {
            "train_loss": 0.12,
            "val_f1": 71.3,
        }
    )
    resolved_categories: list[str] = categories if categories is not None else []

    files_list: list[dict[str, str]] = (
        [
            {
                "path": DEFAULT_WEIGHTS_FILENAME,
                "description": "Model weights in PyTorch format",
                "format": "pt",
            },
        ]
        if include_files_dir
        else []
    )

    details: dict[str, object] = {
        SPEC_VERSION_FIELD: spec_version,
        MODEL_ID_FIELD: model_id,
        NAME_FIELD: name,
        VERSION_FIELD: version,
        SHORT_DESCRIPTION_FIELD: short_description,
        DESCRIPTION_PATH_FIELD: description_path,
        FRAMEWORK_FIELD: framework,
        BASE_MODEL_FIELD: base_model,
        BASE_MODEL_SOURCE_FIELD: base_model_source,
        ARCHITECTURE_FIELD: architecture,
        TRAINING_TASK_ID_FIELD: training_task_id,
        TRAINING_DATASET_IDS_FIELD: resolved_dataset_ids,
        HYPERPARAMETERS_FIELD: resolved_hyperparameters,
        TRAINING_METRICS_FIELD: resolved_training_metrics,
        FILES_FIELD: files_list,
        CATEGORIES_FIELD: resolved_categories,
        CREATED_BY_TASK_FIELD: task_id,
        DATE_CREATED_FIELD: date_created,
    }

    if details_overrides is not None:
        details.update(details_overrides)

    write_json(
        path=model_details_path(
            model_id=model_id,
            task_id=task_id,
        ),
        data=details,
    )

    if include_description:
        frontmatter: dict[str, str | int] = {
            SPEC_VERSION_FIELD: spec_version,
            MODEL_ID_FIELD: model_id,
            "documented_by_task": task_id,
            "date_documented": date_created,
        }
        write_frontmatter_md(
            path=model_description_path(
                model_id=model_id,
                task_id=task_id,
            ),
            frontmatter=frontmatter,
            body=(description_body if description_body is not None else _DESCRIPTION_BODY),
        )

    if include_files_dir:
        files_dir: Path = model_files_dir(
            model_id=model_id,
            task_id=task_id,
        )
        files_dir.mkdir(parents=True, exist_ok=True)
        write_text(
            path=asset_dir / DEFAULT_WEIGHTS_FILENAME,
            content="(placeholder model weights)",
        )

    return asset_dir
