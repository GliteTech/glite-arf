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
    predictions_asset_dir,
    predictions_details_path,
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
PREDICTIONS_ID_FIELD: str = "predictions_id"
NAME_FIELD: str = "name"
SHORT_DESCRIPTION_FIELD: str = "short_description"
DESCRIPTION_PATH_FIELD: str = "description_path"
MODEL_ID_FIELD: str = "model_id"
MODEL_DESCRIPTION_FIELD: str = "model_description"
DATASET_IDS_FIELD: str = "dataset_ids"
PREDICTION_FORMAT_FIELD: str = "prediction_format"
PREDICTION_SCHEMA_FIELD: str = "prediction_schema"
FILES_FIELD: str = "files"
CATEGORIES_FIELD: str = "categories"
CREATED_BY_TASK_FIELD: str = "created_by_task"
DATE_CREATED_FIELD: str = "date_created"
INSTANCE_COUNT_FIELD: str = "instance_count"
LEGACY_SPEC_VERSION: str = "1"

REQUIRED_FIELDS: list[str] = [
    SPEC_VERSION_FIELD,
    PREDICTIONS_ID_FIELD,
    NAME_FIELD,
    SHORT_DESCRIPTION_FIELD,
    MODEL_ID_FIELD,
    MODEL_DESCRIPTION_FIELD,
    DATASET_IDS_FIELD,
    PREDICTION_FORMAT_FIELD,
    PREDICTION_SCHEMA_FIELD,
    FILES_FIELD,
    CATEGORIES_FIELD,
    CREATED_BY_TASK_FIELD,
    DATE_CREATED_FIELD,
]

PREDICTION_FILE_PATH_FIELD: str = "path"
PREDICTION_FILE_DESCRIPTION_FIELD: str = "description"
PREDICTION_FILE_FORMAT_FIELD: str = "format"

PREDICTION_FILE_REQUIRED_KEYS: list[str] = [
    PREDICTION_FILE_PATH_FIELD,
    PREDICTION_FILE_DESCRIPTION_FIELD,
    PREDICTION_FILE_FORMAT_FIELD,
]

MIN_SHORT_DESCRIPTION_WORDS: int = 10
MIN_PREDICTION_SCHEMA_WORDS: int = 10

_PREDICTIONS_ID_PATTERN: re.Pattern[str] = re.compile(
    r"^[a-z0-9]+([.\-][a-z0-9]+)*$",
)

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "PR"

PR_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
PR_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
PR_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
PR_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
PR_E010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=10,
)
PR_E011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=11,
)
PR_E013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=13,
)
PR_E016: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=16,
)
PR_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
PR_W008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=8,
)
PR_W014: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=14,
)
PR_W015: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=15,
)
PR_W016: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=16,
)
PR_W017: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=17,
)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_predictions_id_match(
    *,
    data: dict[str, Any],
    predictions_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    json_id: object = data.get(PREDICTIONS_ID_FIELD)
    if json_id is None:
        return []
    if str(json_id) != predictions_id:
        return [
            Diagnostic(
                code=PR_E004,
                message=(
                    f"predictions_id '{json_id}' does not match folder name '{predictions_id}'"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_required_fields_pr(
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
                code=PR_E005,
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
                code=PR_E013,
                message="spec_version is missing from details.json",
                file_path=file_path,
            ),
        ]
    return []


def _check_description_path_field(
    *,
    data: dict[str, Any],
    predictions_id: str,
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
                code=PR_E005,
                message=f"Required string field missing: '{DESCRIPTION_PATH_FIELD}'",
                file_path=file_path,
            ),
        ]
    if value is None:
        return []
    if not isinstance(value, str) or len(value.strip()) == 0:
        return [
            Diagnostic(
                code=PR_E005,
                message=f"Field '{DESCRIPTION_PATH_FIELD}' must be a non-empty string",
                file_path=file_path,
            ),
        ]
    declared_path: Path = (
        predictions_asset_dir(
            predictions_id=predictions_id,
            task_id=task_id,
        )
        / value
    )
    if not declared_path.exists():
        return [
            Diagnostic(
                code=PR_E008,
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
                    code=PR_E016,
                    message=f"files[{i}] is not an object",
                    file_path=file_path,
                ),
            )
            continue
        for key in PREDICTION_FILE_REQUIRED_KEYS:
            value: object = entry.get(key)
            if value is None or not isinstance(value, str):
                diagnostics.append(
                    Diagnostic(
                        code=PR_E016,
                        message=(f"files[{i}] is missing required string field '{key}'"),
                        file_path=file_path,
                    ),
                )
    return diagnostics


def _check_files_exist(
    *,
    data: dict[str, Any],
    predictions_id: str,
    task_id: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    files: object = data.get(FILES_FIELD)
    if not isinstance(files, list):
        return []
    asset_dir: Path = predictions_asset_dir(
        predictions_id=predictions_id,
        task_id=task_id,
    )
    diagnostics: list[Diagnostic] = []
    for entry in files:
        if not isinstance(entry, dict):
            continue
        path_value: object = entry.get(PREDICTION_FILE_PATH_FIELD)
        if not isinstance(path_value, str):
            continue
        full_path: Path = asset_dir / path_value
        if not full_path.exists():
            diagnostics.append(
                Diagnostic(
                    code=PR_E008,
                    message=f"Listed file does not exist: '{path_value}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_prediction_format(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    prediction_format: object = data.get(PREDICTION_FORMAT_FIELD)
    if prediction_format is None:
        return []
    if isinstance(prediction_format, str) and len(prediction_format.strip()) == 0:
        return [
            Diagnostic(
                code=PR_E010,
                message="prediction_format is empty",
                file_path=file_path,
            ),
        ]
    return []


def _check_predictions_id_format(
    *,
    predictions_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    if _PREDICTIONS_ID_PATTERN.match(predictions_id) is None:
        return [
            Diagnostic(
                code=PR_E011,
                message=(
                    f"Folder name '{predictions_id}' does not match "
                    "predictions ID format (lowercase alphanumeric, "
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
                    code=PR_W005,
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
                code=PR_W008,
                message=(
                    f"short_description has {word_count} words "
                    f"(minimum: {MIN_SHORT_DESCRIPTION_WORDS})"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_model_id(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    model_id: object = data.get(MODEL_ID_FIELD)
    if model_id is None:
        return [
            Diagnostic(
                code=PR_W014,
                message="model_id is null (no model asset linked)",
                file_path=file_path,
            ),
        ]
    return []


def _check_dataset_ids(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    dataset_ids: object = data.get(DATASET_IDS_FIELD)
    if not isinstance(dataset_ids, list):
        return []
    if len(dataset_ids) == 0:
        return [
            Diagnostic(
                code=PR_W015,
                message="dataset_ids is empty (no dataset assets linked)",
                file_path=file_path,
            ),
        ]
    return []


def _check_prediction_schema(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    schema: object = data.get(PREDICTION_SCHEMA_FIELD)
    if not isinstance(schema, str):
        return []
    word_count: int = count_words(text=schema)
    if word_count < MIN_PREDICTION_SCHEMA_WORDS:
        return [
            Diagnostic(
                code=PR_W016,
                message=(
                    f"prediction_schema has {word_count} words "
                    f"(minimum: {MIN_PREDICTION_SCHEMA_WORDS})"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_instance_count(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    instance_count: object = data.get(INSTANCE_COUNT_FIELD)
    if instance_count is None:
        return [
            Diagnostic(
                code=PR_W017,
                message="instance_count is null",
                file_path=file_path,
            ),
        ]
    return []


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def verify_predictions_details(
    *,
    predictions_id: str,
    task_id: str | None = None,
) -> list[Diagnostic]:
    file_path: Path = predictions_details_path(
        predictions_id=predictions_id,
        task_id=task_id,
    )

    if not file_path.exists():
        return [
            Diagnostic(
                code=PR_E001,
                message=f"details.json does not exist: {file_path}",
                file_path=file_path,
            ),
        ]

    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return [
            Diagnostic(
                code=PR_E001,
                message=f"details.json is not valid JSON: {file_path}",
                file_path=file_path,
            ),
        ]

    diagnostics: list[Diagnostic] = []

    diagnostics.extend(
        _check_predictions_id_format(
            predictions_id=predictions_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_required_fields_pr(
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
            predictions_id=predictions_id,
            task_id=task_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_predictions_id_match(
            data=data,
            predictions_id=predictions_id,
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
            predictions_id=predictions_id,
            task_id=task_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_prediction_format(
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
        _check_model_id(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_dataset_ids(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_prediction_schema(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_instance_count(
            data=data,
            file_path=file_path,
        ),
    )

    return diagnostics
