"""Verificator for task.json files.

Checks task.json against the task file specification
(arf/specifications/task_file_specification.md).

Usage:
    uv run python -m arf.scripts.verificators.verify_task_file <task_id>
    uv run python -m arf.scripts.verificators.verify_task_file --all

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from arf.scripts.common.task_description import (
    CURRENT_TASK_SPEC_VERSION,
    FIELD_LONG_DESCRIPTION,
    FIELD_LONG_DESCRIPTION_FILE,
    FIELD_SPEC_VERSION,
    LEGACY_TASK_SPEC_VERSION,
    RECOMMENDED_TASK_DESCRIPTION_FILE_NAME,
    SUPPORTED_TASK_SPEC_VERSIONS,
    infer_task_spec_version,
    is_valid_task_description_file_name,
    task_description_file_path,
)
from arf.scripts.verificators.common.json_utils import (
    check_required_fields,
    load_json_file,
)
from arf.scripts.verificators.common.paths import (
    ASSET_TYPES_DIR,
    TASK_TYPES_DIR,
    TASKS_DIR,
    suggestions_path,
    task_json_path,
)
from arf.scripts.verificators.common.reporting import (
    exit_code_for_result,
    print_verification_result,
)
from arf.scripts.verificators.common.types import (
    Diagnostic,
    DiagnosticCode,
    Severity,
    VerificationResult,
)
from arf.scripts.verificators.verify_task_dependencies import (
    check_all_dependencies,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PREFIX: str = "TF"

FIELD_TASK_ID: str = "task_id"
FIELD_NAME: str = "name"
FIELD_SHORT_DESCRIPTION: str = "short_description"
FIELD_TASK_INDEX: str = "task_index"
FIELD_STATUS: str = "status"
FIELD_DEPENDENCIES: str = "dependencies"
FIELD_START_TIME: str = "start_time"
FIELD_END_TIME: str = "end_time"
FIELD_EXPECTED_ASSETS: str = "expected_assets"
FIELD_TASK_TYPES: str = "task_types"
FIELD_SOURCE_SUGGESTION: str = "source_suggestion"
FIELD_SUGGESTIONS: str = "suggestions"
FIELD_ID: str = "id"

BASE_REQUIRED_FIELDS: list[str] = [
    FIELD_TASK_ID,
    FIELD_TASK_INDEX,
    FIELD_NAME,
    FIELD_SHORT_DESCRIPTION,
    FIELD_STATUS,
    FIELD_DEPENDENCIES,
    FIELD_START_TIME,
    FIELD_END_TIME,
    FIELD_EXPECTED_ASSETS,
    FIELD_TASK_TYPES,
    FIELD_SOURCE_SUGGESTION,
]

ALLOWED_STATUSES: set[str] = {
    "not_started",
    "in_progress",
    "completed",
    "cancelled",
    "permanently_failed",
    "intervention_blocked",
}

COMPLETED_STATUSES: set[str] = {"completed", "cancelled", "permanently_failed"}

TASK_ID_PATTERN: re.Pattern[str] = re.compile(r"^t\d{4}_[a-z0-9]+(?:_[a-z0-9]+)*$")
SUGGESTION_ID_PATTERN: re.Pattern[str] = re.compile(r"^S-\d{4}-\d{2}$")

ISO_8601_PATTERN: re.Pattern[str] = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
)

MAX_NAME_LENGTH: int = 80
MAX_SHORT_DESCRIPTION_LENGTH: int = 200

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

TF_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
TF_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
TF_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
TF_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
TF_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
TF_E007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=7,
)
TF_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
TF_E009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=9,
)
TF_E010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=10,
)
TF_E011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=11,
)
TF_E012: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=12,
)
TF_E013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=13,
)
TF_E014: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=14,
)
TF_E015: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=15,
)
TF_E016: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=16,
)

TF_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
TF_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
TF_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
TF_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)
TF_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
TF_W006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=6,
)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_task_id_match(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    file_path = task_json_path(task_id=task_id)
    json_task_id: object = data.get(FIELD_TASK_ID)
    if json_task_id is None:
        return []
    if str(json_task_id) != task_id:
        return [
            Diagnostic(
                code=TF_E002,
                message=(f"task_id '{json_task_id}' does not match folder name '{task_id}'"),
                file_path=file_path,
            ),
        ]
    return []


def _check_task_id_format(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    file_path = task_json_path(task_id=task_id)
    json_task_id: str = str(data.get(FIELD_TASK_ID, task_id))
    if TASK_ID_PATTERN.match(json_task_id) is None:
        return [
            Diagnostic(
                code=TF_E005,
                message=(f"task_id '{json_task_id}' does not match required format tNNNN_slug"),
                file_path=file_path,
            ),
        ]
    return []


def _check_task_index(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    file_path: Path = task_json_path(task_id=task_id)
    raw_index: object = data.get(FIELD_TASK_INDEX)
    if raw_index is None:
        return []
    if not isinstance(raw_index, int):
        return [
            Diagnostic(
                code=TF_E010,
                message=f"task_index must be an integer, got {type(raw_index).__name__}",
                file_path=file_path,
            ),
        ]
    json_task_id: str = str(data.get(FIELD_TASK_ID, ""))
    if TASK_ID_PATTERN.match(json_task_id) is not None:
        expected_index: int = int(json_task_id[1:5])
        if raw_index != expected_index:
            return [
                Diagnostic(
                    code=TF_E010,
                    message=(
                        f"task_index {raw_index} does not match task_id "
                        f"'{json_task_id}' (expected {expected_index})"
                    ),
                    file_path=file_path,
                ),
            ]
    return []


def _check_spec_version(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    file_path: Path = task_json_path(task_id=task_id)
    raw_spec_version: object = data.get(FIELD_SPEC_VERSION)
    if raw_spec_version is None:
        return []
    if not isinstance(raw_spec_version, int) or isinstance(raw_spec_version, bool):
        return [
            Diagnostic(
                code=TF_E013,
                message=(
                    "spec_version must be an integer when present; "
                    f"got {type(raw_spec_version).__name__}"
                ),
                file_path=file_path,
            ),
        ]
    if raw_spec_version not in SUPPORTED_TASK_SPEC_VERSIONS:
        allowed_versions: str = ", ".join(str(v) for v in sorted(SUPPORTED_TASK_SPEC_VERSIONS))
        return [
            Diagnostic(
                code=TF_E013,
                message=f"spec_version '{raw_spec_version}' is not supported",
                file_path=file_path,
                detail=(
                    "Use spec_version 4 for new task files. "
                    f"Allowed versions: {allowed_versions}. "
                    "Omit the field only for legacy spec_version 3 task files."
                ),
            ),
        ]
    return []


def _check_task_description_fields(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    spec_version: int | None = infer_task_spec_version(data=data)
    if spec_version is None:
        return []

    file_path: Path = task_json_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    has_inline_field: bool = FIELD_LONG_DESCRIPTION in data
    has_file_field: bool = FIELD_LONG_DESCRIPTION_FILE in data

    inline_value: object = data.get(FIELD_LONG_DESCRIPTION)
    file_value: object = data.get(FIELD_LONG_DESCRIPTION_FILE)

    if has_inline_field and not isinstance(inline_value, str):
        diagnostics.append(
            Diagnostic(
                code=TF_E014,
                message=(
                    "long_description must be a string when present; "
                    f"got {type(inline_value).__name__}"
                ),
                file_path=file_path,
            ),
        )
    if has_file_field and not isinstance(file_value, str):
        diagnostics.append(
            Diagnostic(
                code=TF_E014,
                message=(
                    "long_description_file must be a string when present; "
                    f"got {type(file_value).__name__}"
                ),
                file_path=file_path,
            ),
        )

    if spec_version == LEGACY_TASK_SPEC_VERSION:
        if has_file_field:
            diagnostics.append(
                Diagnostic(
                    code=TF_E014,
                    message=(
                        "spec_version 3 task files must use inline long_description and "
                        "must not set long_description_file"
                    ),
                    file_path=file_path,
                ),
            )
        return diagnostics

    if has_inline_field == has_file_field:
        diagnostics.append(
            Diagnostic(
                code=TF_E014,
                message=(
                    f"spec_version {CURRENT_TASK_SPEC_VERSION} task files must set exactly one of "
                    "long_description or long_description_file"
                ),
                file_path=file_path,
            ),
        )
        return diagnostics

    if not isinstance(file_value, str):
        return diagnostics

    if not is_valid_task_description_file_name(file_name=file_value):
        diagnostics.append(
            Diagnostic(
                code=TF_E015,
                message=(
                    "long_description_file must be a single markdown file name in the task root "
                    f"(recommended: {RECOMMENDED_TASK_DESCRIPTION_FILE_NAME!r})"
                ),
                file_path=file_path,
            ),
        )
        return diagnostics

    description_path: Path = task_description_file_path(
        task_id=task_id,
        file_name=file_value,
    )
    if not description_path.is_file():
        diagnostics.append(
            Diagnostic(
                code=TF_E016,
                message=f"Referenced long_description_file does not exist: {file_value}",
                file_path=file_path,
            ),
        )
        return diagnostics

    try:
        description_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        diagnostics.append(
            Diagnostic(
                code=TF_E016,
                message=f"Referenced long_description_file is not readable as UTF-8: {file_value}",
                file_path=file_path,
            ),
        )

    return diagnostics


def _check_status(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    file_path = task_json_path(task_id=task_id)
    status: object = data.get(FIELD_STATUS)
    if status is None:
        return []
    if str(status) not in ALLOWED_STATUSES:
        return [
            Diagnostic(
                code=TF_E004,
                message=f"status '{status}' is not one of the allowed values",
                file_path=file_path,
                detail=f"Allowed: {', '.join(sorted(ALLOWED_STATUSES))}",
            ),
        ]
    return []


SKIP_DEPENDENCY_CHECK_STATUSES: set[str] = {"not_started", "cancelled"}


def _check_dependencies(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    status: str = str(data.get(FIELD_STATUS, ""))
    if status in SKIP_DEPENDENCY_CHECK_STATUSES:
        return []

    file_path = task_json_path(task_id=task_id)
    return check_all_dependencies(data=data, file_path=file_path)


def _check_timestamps(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    file_path = task_json_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    for field_name in [FIELD_START_TIME, FIELD_END_TIME]:
        value: object = data.get(field_name)
        if value is None:
            continue
        if not isinstance(value, str):
            diagnostics.append(
                Diagnostic(
                    code=TF_E007,
                    message=f"'{field_name}' is not a string or null",
                    file_path=file_path,
                ),
            )
            continue
        if ISO_8601_PATTERN.match(value) is None:
            diagnostics.append(
                Diagnostic(
                    code=TF_E007,
                    message=(
                        f"'{field_name}' value '{value}' is not valid "
                        f"ISO 8601 UTC format (YYYY-MM-DDTHH:MM:SSZ)"
                    ),
                    file_path=file_path,
                ),
            )

    return diagnostics


def _check_short_description_length(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    file_path = task_json_path(task_id=task_id)
    short_desc: object = data.get(FIELD_SHORT_DESCRIPTION)
    if isinstance(short_desc, str) and len(short_desc) > MAX_SHORT_DESCRIPTION_LENGTH:
        return [
            Diagnostic(
                code=TF_W001,
                message=(
                    f"short_description is {len(short_desc)} characters "
                    f"(maximum: {MAX_SHORT_DESCRIPTION_LENGTH})"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_name_length(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    file_path = task_json_path(task_id=task_id)
    name: object = data.get(FIELD_NAME)
    if isinstance(name, str) and len(name) > MAX_NAME_LENGTH:
        return [
            Diagnostic(
                code=TF_W002,
                message=(f"name is {len(name)} characters (maximum: {MAX_NAME_LENGTH})"),
                file_path=file_path,
            ),
        ]
    return []


def _check_start_time_consistency(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    file_path = task_json_path(task_id=task_id)
    status: str = str(data.get(FIELD_STATUS, ""))
    start_time: object = data.get(FIELD_START_TIME)
    if status == "in_progress" and start_time is None:
        return [
            Diagnostic(
                code=TF_W003,
                message="status is 'in_progress' but start_time is null",
                file_path=file_path,
            ),
        ]
    return []


def _check_end_time_consistency(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    file_path = task_json_path(task_id=task_id)
    status: str = str(data.get(FIELD_STATUS, ""))
    end_time: object = data.get(FIELD_END_TIME)
    if status in COMPLETED_STATUSES and end_time is None:
        return [
            Diagnostic(
                code=TF_W004,
                message=f"status is '{status}' but end_time is null",
                file_path=file_path,
            ),
        ]
    return []


def _get_valid_asset_type_names() -> set[str]:
    if not ASSET_TYPES_DIR.is_dir():
        return set()
    return {d.name for d in ASSET_TYPES_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")}


def _check_expected_assets(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    file_path = task_json_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []
    expected: object = data.get(FIELD_EXPECTED_ASSETS)
    if isinstance(expected, dict) and len(expected) == 0:
        diagnostics.append(
            Diagnostic(
                code=TF_W005,
                message="expected_assets is empty (task produces no assets)",
                file_path=file_path,
            ),
        )
        return diagnostics
    if isinstance(expected, dict):
        valid_names: set[str] = _get_valid_asset_type_names()
        if len(valid_names) > 0:
            for key in expected:
                key_str: str = str(key)
                if key_str not in valid_names:
                    diagnostics.append(
                        Diagnostic(
                            code=TF_W006,
                            message=(
                                f"expected_assets key '{key_str}' does not"
                                f" match any folder in meta/asset_types/"
                                f" (valid: {sorted(valid_names)})"
                            ),
                            file_path=file_path,
                        ),
                    )
    return diagnostics


def _collect_all_suggestion_ids() -> set[str]:
    if not TASKS_DIR.exists():
        return set()
    ids: set[str] = set()
    for task_dir in TASKS_DIR.iterdir():
        if not task_dir.is_dir() or task_dir.name.startswith("."):
            continue
        suggestions_file: Path = suggestions_path(task_id=task_dir.name)
        if not suggestions_file.exists():
            continue
        try:
            raw: str = suggestions_file.read_text(encoding="utf-8")
            data: object = json.loads(raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        suggestions: object = data.get(FIELD_SUGGESTIONS)
        if not isinstance(suggestions, list):
            continue
        for item in suggestions:
            if isinstance(item, dict) and isinstance(item.get(FIELD_ID), str):
                ids.add(item[FIELD_ID])
    return ids


def _check_source_suggestion(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    file_path: Path = task_json_path(task_id=task_id)
    value: object = data.get(FIELD_SOURCE_SUGGESTION)
    if value is None:
        return []
    if not isinstance(value, str):
        return [
            Diagnostic(
                code=TF_E008,
                message="source_suggestion must be a string or null",
                file_path=file_path,
            ),
        ]
    if SUGGESTION_ID_PATTERN.match(value) is None:
        return [
            Diagnostic(
                code=TF_E008,
                message=(f"source_suggestion '{value}' does not match required format S-XXXX-NN"),
                file_path=file_path,
            ),
        ]
    all_suggestion_ids: set[str] = _collect_all_suggestion_ids()
    if value not in all_suggestion_ids:
        return [
            Diagnostic(
                code=TF_E009,
                message=(
                    f"source_suggestion '{value}' does not exist in any task's suggestions.json"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_task_types(
    *,
    data: dict[str, Any],
    task_id: str,
) -> list[Diagnostic]:
    file_path: Path = task_json_path(task_id=task_id)
    value: object = data.get(FIELD_TASK_TYPES)
    if value is None:
        return []
    if not isinstance(value, list):
        return [
            Diagnostic(
                code=TF_E011,
                message="task_types must be a list",
                file_path=file_path,
            ),
        ]
    diagnostics: list[Diagnostic] = []
    for item in value:
        if not isinstance(item, str):
            diagnostics.append(
                Diagnostic(
                    code=TF_E011,
                    message=f"task_types contains non-string value: {item!r}",
                    file_path=file_path,
                ),
            )
            continue
        type_dir: Path = TASK_TYPES_DIR / item
        if not type_dir.is_dir():
            diagnostics.append(
                Diagnostic(
                    code=TF_E012,
                    message=(f"task type '{item}' does not exist in meta/task_types/"),
                    file_path=file_path,
                ),
            )
    return diagnostics


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_task_file(*, task_id: str) -> VerificationResult:
    file_path = task_json_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    # E001: file existence and validity
    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        diagnostics.append(
            Diagnostic(
                code=TF_E001,
                message=f"task.json does not exist or is not valid JSON: {file_path}",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    # E013: spec_version (optional for legacy spec_version 3 task files)
    diagnostics.extend(
        _check_spec_version(data=data, task_id=task_id),
    )

    required_fields: list[str] = list(BASE_REQUIRED_FIELDS)
    spec_version: int | None = infer_task_spec_version(data=data)
    if spec_version == LEGACY_TASK_SPEC_VERSION:
        required_fields.append(FIELD_LONG_DESCRIPTION)

    # E003: required fields
    missing: list[str] = check_required_fields(
        data=data,
        required_fields=required_fields,
    )
    if len(missing) > 0:
        diagnostics.append(
            Diagnostic(
                code=TF_E003,
                message=f"Missing required fields: {', '.join(missing)}",
                file_path=file_path,
            ),
        )

    # E002: task_id matches folder
    diagnostics.extend(
        _check_task_id_match(data=data, task_id=task_id),
    )

    # E005: task_id format
    diagnostics.extend(
        _check_task_id_format(data=data, task_id=task_id),
    )

    # E010: task_index
    diagnostics.extend(
        _check_task_index(data=data, task_id=task_id),
    )

    # E014/E015/E016: task description fields and referenced file
    diagnostics.extend(
        _check_task_description_fields(data=data, task_id=task_id),
    )

    # E004: status value
    diagnostics.extend(
        _check_status(data=data, task_id=task_id),
    )

    # Dependencies (skipped for not_started/cancelled)
    diagnostics.extend(
        _check_dependencies(data=data, task_id=task_id),
    )

    # E007: timestamps
    diagnostics.extend(
        _check_timestamps(data=data, task_id=task_id),
    )

    # W001: short_description length
    diagnostics.extend(
        _check_short_description_length(data=data, task_id=task_id),
    )

    # W002: name length
    diagnostics.extend(
        _check_name_length(data=data, task_id=task_id),
    )

    # W003: start_time consistency
    diagnostics.extend(
        _check_start_time_consistency(data=data, task_id=task_id),
    )

    # W004: end_time consistency
    diagnostics.extend(
        _check_end_time_consistency(data=data, task_id=task_id),
    )

    # W005: expected_assets empty
    diagnostics.extend(
        _check_expected_assets(data=data, task_id=task_id),
    )

    # E011/E012: task_types
    diagnostics.extend(
        _check_task_types(data=data, task_id=task_id),
    )

    # E008/E009: source_suggestion format and existence
    diagnostics.extend(
        _check_source_suggestion(data=data, task_id=task_id),
    )

    return VerificationResult(
        file_path=file_path,
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify task.json for a given task (or all tasks)",
    )
    parser.add_argument(
        "task_id",
        nargs="?",
        default=None,
        help="Task ID (e.g. t0003_download_training_corpus)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Verify all tasks in the tasks/ directory",
    )
    args: argparse.Namespace = parser.parse_args()

    if args.all:
        task_dirs: list[str] = sorted(
            d.name for d in TASKS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
        )
        has_errors: bool = False
        for tid in task_dirs:
            result: VerificationResult = verify_task_file(task_id=tid)
            print_verification_result(result=result)
            if not result.passed:
                has_errors = True
        sys.exit(1 if has_errors else 0)

    if args.task_id is None:
        parser.error("Provide a task_id or use --all")

    result = verify_task_file(task_id=args.task_id)
    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
