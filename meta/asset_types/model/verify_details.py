import re
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.json_utils import (
    check_required_fields,
    load_json_file,
)
from arf.scripts.verificators.common.markdown_sections import count_words
from arf.scripts.verificators.common.paths import (
    CATEGORIES_DIR,
    model_asset_dir,
    model_details_path,
)
from arf.scripts.verificators.common.types import (
    Diagnostic,
    DiagnosticCode,
    Severity,
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
ARCHITECTURE_FIELD: str = "architecture"
TRAINING_TASK_ID_FIELD: str = "training_task_id"
TRAINING_DATASET_IDS_FIELD: str = "training_dataset_ids"
HYPERPARAMETERS_FIELD: str = "hyperparameters"
TRAINING_METRICS_FIELD: str = "training_metrics"
FILES_FIELD: str = "files"
CATEGORIES_FIELD: str = "categories"
CREATED_BY_TASK_FIELD: str = "created_by_task"
DATE_CREATED_FIELD: str = "date_created"
LEGACY_SPEC_VERSION: str = "1"

REQUIRED_FIELDS: list[str] = [
    SPEC_VERSION_FIELD,
    MODEL_ID_FIELD,
    NAME_FIELD,
    VERSION_FIELD,
    SHORT_DESCRIPTION_FIELD,
    FRAMEWORK_FIELD,
    BASE_MODEL_FIELD,
    ARCHITECTURE_FIELD,
    TRAINING_TASK_ID_FIELD,
    TRAINING_DATASET_IDS_FIELD,
    FILES_FIELD,
    CATEGORIES_FIELD,
    CREATED_BY_TASK_FIELD,
    DATE_CREATED_FIELD,
]

ALLOWED_FRAMEWORKS: list[str] = [
    "pytorch",
    "tensorflow",
    "jax",
    "onnx",
    "other",
]

MODEL_FILE_REQUIRED_KEYS: list[str] = [
    "path",
    "description",
    "format",
]

MIN_SHORT_DESCRIPTION_WORDS: int = 10

_MODEL_ID_PATTERN: re.Pattern[str] = re.compile(
    r"^[a-z0-9]+([.\-][a-z0-9]+)*$",
)

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "MA"

MA_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
MA_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
MA_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
MA_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
MA_E010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=10,
)
MA_E011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=11,
)
MA_E013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=13,
)
MA_E016: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=16,
)
MA_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
MA_W008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=8,
)
MA_W014: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=14,
)
MA_W015: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=15,
)
MA_W016: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=16,
)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_model_id_match(
    *,
    data: dict[str, Any],
    model_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    json_id: object = data.get(MODEL_ID_FIELD)
    if json_id is None:
        return []
    if str(json_id) != model_id:
        return [
            Diagnostic(
                code=MA_E004,
                message=(f"model_id '{json_id}' does not match folder name '{model_id}'"),
                file_path=file_path,
            ),
        ]
    return []


def _check_required_fields_model(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    missing: list[str] = check_required_fields(
        data=data,
        required_fields=REQUIRED_FIELDS,
    )
    diagnostics: list[Diagnostic] = []
    for field_name in missing:
        diagnostics.append(
            Diagnostic(
                code=MA_E005,
                message=f"Required field missing: '{field_name}'",
                file_path=file_path,
            ),
        )
    return diagnostics


def _check_spec_version(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    version: object = data.get(SPEC_VERSION_FIELD)
    if version is None:
        return [
            Diagnostic(
                code=MA_E013,
                message="spec_version is missing from details.json",
                file_path=file_path,
            ),
        ]
    return []


def _check_description_path_field(
    *,
    data: dict[str, Any],
    model_id: str,
    task_id: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    version: object = data.get(SPEC_VERSION_FIELD)
    value: object = data.get(DESCRIPTION_PATH_FIELD)
    if (
        isinstance(version, str)
        and version != LEGACY_SPEC_VERSION
        and (not isinstance(value, str) or len(value.strip()) == 0)
    ):
        return [
            Diagnostic(
                code=MA_E005,
                message=f"Required string field missing: '{DESCRIPTION_PATH_FIELD}'",
                file_path=file_path,
            ),
        ]
    if value is None:
        return []
    if not isinstance(value, str) or len(value.strip()) == 0:
        return [
            Diagnostic(
                code=MA_E005,
                message=f"Field '{DESCRIPTION_PATH_FIELD}' must be a non-empty string",
                file_path=file_path,
            ),
        ]
    declared_path: Path = (
        model_asset_dir(
            model_id=model_id,
            task_id=task_id,
        )
        / value
    )
    if not declared_path.exists():
        return [
            Diagnostic(
                code=MA_E008,
                message=f"Declared description path does not exist: '{value}'",
                file_path=file_path,
            ),
        ]
    return []


def _check_files_structure(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    files: object = data.get(FILES_FIELD)
    if not isinstance(files, list):
        return []
    diagnostics: list[Diagnostic] = []
    for i, entry in enumerate(files):
        if not isinstance(entry, dict):
            diagnostics.append(
                Diagnostic(
                    code=MA_E016,
                    message=f"files[{i}] is not an object",
                    file_path=file_path,
                ),
            )
            continue
        for key in MODEL_FILE_REQUIRED_KEYS:
            value: object = entry.get(key)
            if value is None or not isinstance(value, str):
                diagnostics.append(
                    Diagnostic(
                        code=MA_E016,
                        message=(f"files[{i}] is missing required string field '{key}'"),
                        file_path=file_path,
                    ),
                )
    return diagnostics


def _check_files_exist(
    *,
    data: dict[str, Any],
    model_id: str,
    task_id: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    files: object = data.get(FILES_FIELD)
    if not isinstance(files, list):
        return []
    asset_dir: Path = model_asset_dir(
        model_id=model_id,
        task_id=task_id,
    )
    diagnostics: list[Diagnostic] = []
    for entry in files:
        if not isinstance(entry, dict):
            continue
        path_value: object = entry.get("path")
        if not isinstance(path_value, str):
            continue
        full_path: Path = asset_dir / path_value
        if not full_path.exists():
            diagnostics.append(
                Diagnostic(
                    code=MA_E008,
                    message=f"Listed file does not exist: '{path_value}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_framework(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    framework: object = data.get(FRAMEWORK_FIELD)
    if framework is None:
        return []
    if str(framework) not in ALLOWED_FRAMEWORKS:
        return [
            Diagnostic(
                code=MA_E010,
                message=(f"framework '{framework}' is not one of: {', '.join(ALLOWED_FRAMEWORKS)}"),
                file_path=file_path,
            ),
        ]
    return []


def _check_model_id_format(
    *,
    model_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    if _MODEL_ID_PATTERN.match(model_id) is None:
        return [
            Diagnostic(
                code=MA_E011,
                message=(
                    f"Folder name '{model_id}' does not match "
                    "model ID format (lowercase alphanumeric, "
                    "hyphens, dots)"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_categories_exist(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    categories: object = data.get(CATEGORIES_FIELD)
    if not isinstance(categories, list):
        return []
    diagnostics: list[Diagnostic] = []
    for category in categories:
        if not isinstance(category, str):
            continue
        category_dir: Path = CATEGORIES_DIR / category
        if not category_dir.exists():
            diagnostics.append(
                Diagnostic(
                    code=MA_W005,
                    message=(f"Category '{category}' does not exist in meta/categories/"),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_short_description_length(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    desc: object = data.get(SHORT_DESCRIPTION_FIELD)
    if not isinstance(desc, str):
        return []
    word_count: int = count_words(text=desc)
    if word_count < MIN_SHORT_DESCRIPTION_WORDS:
        return [
            Diagnostic(
                code=MA_W008,
                message=(
                    f"short_description has {word_count} words "
                    f"(minimum: {MIN_SHORT_DESCRIPTION_WORDS})"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_training_dataset_ids(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    ids: object = data.get(TRAINING_DATASET_IDS_FIELD)
    if not isinstance(ids, list) or len(ids) == 0:
        return [
            Diagnostic(
                code=MA_W014,
                message="training_dataset_ids is empty",
                file_path=file_path,
            ),
        ]
    return []


def _check_hyperparameters(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    hp: object = data.get(HYPERPARAMETERS_FIELD)
    if hp is None or (isinstance(hp, dict) and len(hp) == 0):
        return [
            Diagnostic(
                code=MA_W015,
                message="hyperparameters is missing or empty",
                file_path=file_path,
            ),
        ]
    return []


def _check_training_metrics(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    tm: object = data.get(TRAINING_METRICS_FIELD)
    if tm is None or (isinstance(tm, dict) and len(tm) == 0):
        return [
            Diagnostic(
                code=MA_W016,
                message="training_metrics is missing or empty",
                file_path=file_path,
            ),
        ]
    return []


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def verify_model_details(
    *,
    model_id: str,
    task_id: str | None = None,
) -> list[Diagnostic]:
    file_path: Path = model_details_path(
        model_id=model_id,
        task_id=task_id,
    )

    if not file_path.exists():
        return [
            Diagnostic(
                code=MA_E001,
                message=f"details.json does not exist: {file_path}",
                file_path=file_path,
            ),
        ]

    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return [
            Diagnostic(
                code=MA_E001,
                message=f"details.json is not valid JSON: {file_path}",
                file_path=file_path,
            ),
        ]

    diagnostics: list[Diagnostic] = []

    diagnostics.extend(
        _check_model_id_format(
            model_id=model_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_required_fields_model(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_spec_version(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_description_path_field(
            data=data,
            model_id=model_id,
            task_id=task_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_model_id_match(
            data=data,
            model_id=model_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_files_structure(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_files_exist(
            data=data,
            model_id=model_id,
            task_id=task_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_framework(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_categories_exist(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_short_description_length(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_training_dataset_ids(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_hyperparameters(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_training_metrics(
            data=data,
            file_path=file_path,
        ),
    )

    return diagnostics
