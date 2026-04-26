"""Verificator for metric definition files.

Validates metric definitions in meta/metrics/ against the metrics
specification (arf/specifications/metrics_specification.md).

Usage:
    uv run python -m arf.scripts.verificators.verify_metrics <metric_key>
    uv run python -m arf.scripts.verificators.verify_metrics --all

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.json_utils import (
    check_required_fields,
    load_json_file,
)
from arf.scripts.verificators.common.paths import (
    METRICS_DIR,
    TASKS_DIR,
    dataset_base_dir,
    metric_definition_path,
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

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PREFIX: str = "MT"

FIELD_VERSION: str = "spec_version"
FIELD_NAME: str = "name"
FIELD_DESCRIPTION: str = "description"
FIELD_UNIT: str = "unit"
FIELD_VALUE_TYPE: str = "value_type"
FIELD_HIGHER_IS_BETTER: str = "higher_is_better"
FIELD_DATASETS: str = "datasets"
FIELD_IS_KEY: str = "is_key"
FIELD_EMOJI: str = "emoji"

REQUIRED_FIELDS: list[str] = [
    FIELD_VERSION,
    FIELD_NAME,
    FIELD_DESCRIPTION,
    FIELD_UNIT,
    FIELD_VALUE_TYPE,
    FIELD_HIGHER_IS_BETTER,
]

ALLOWED_UNITS: set[str] = {
    "f1",
    "accuracy",
    "precision",
    "recall",
    "ratio",
    "count",
    "usd",
    "seconds",
    "bytes",
    "instances_per_second",
    "none",
}

ALLOWED_VALUE_TYPES: set[str] = {
    "float",
    "int",
    "bool",
    "string",
}

SNAKE_CASE_PATTERN: re.Pattern[str] = re.compile(
    r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$",
)

MAX_NAME_LENGTH: int = 80
MIN_DESCRIPTION_LENGTH: int = 20

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

MT_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
MT_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
MT_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
MT_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
MT_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
MT_E006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=6,
)
MT_E007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=7,
)
MT_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
MT_E009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=9,
)

MT_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
MT_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
MT_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
MT_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)
MT_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)


# ---------------------------------------------------------------------------
# Dataset discovery
# ---------------------------------------------------------------------------


def _collect_all_dataset_ids() -> set[str]:
    if not TASKS_DIR.is_dir():
        return set()
    ids: set[str] = set()
    for task_directory in TASKS_DIR.iterdir():
        if not task_directory.is_dir() or task_directory.name.startswith("."):
            continue
        dataset_dir: Path = dataset_base_dir(task_id=task_directory.name)
        if not dataset_dir.is_dir():
            continue
        for entry in dataset_dir.iterdir():
            if entry.is_dir() and not entry.name.startswith("."):
                ids.add(entry.name)
    return ids


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_file_name(*, metric_key: str) -> list[Diagnostic]:
    file_path: Path = metric_definition_path(metric_key=metric_key)
    if SNAKE_CASE_PATTERN.match(metric_key) is None:
        return [
            Diagnostic(
                code=MT_E006,
                message=(f"File name '{metric_key}' does not match snake_case pattern"),
                file_path=file_path,
            ),
        ]
    return []


def _check_fields(
    *,
    data: dict[str, Any],
    metric_key: str,
) -> list[Diagnostic]:
    file_path: Path = metric_definition_path(metric_key=metric_key)
    diagnostics: list[Diagnostic] = []

    # E003: version must be int
    version: object = data.get(FIELD_VERSION)
    if version is not None and not isinstance(version, int):
        diagnostics.append(
            Diagnostic(
                code=MT_E003,
                message=f"'{FIELD_VERSION}' is not an integer",
                file_path=file_path,
            ),
        )

    # E004: unit must be allowed
    unit: object = data.get(FIELD_UNIT)
    if isinstance(unit, str) and unit not in ALLOWED_UNITS:
        diagnostics.append(
            Diagnostic(
                code=MT_E004,
                message=(
                    f"'{FIELD_UNIT}' value '{unit}' is not allowed; "
                    f"expected one of: {', '.join(sorted(ALLOWED_UNITS))}"
                ),
                file_path=file_path,
            ),
        )

    # E005: value_type must be allowed
    value_type: object = data.get(FIELD_VALUE_TYPE)
    if isinstance(value_type, str) and value_type not in ALLOWED_VALUE_TYPES:
        diagnostics.append(
            Diagnostic(
                code=MT_E005,
                message=(
                    f"'{FIELD_VALUE_TYPE}' value '{value_type}' is not allowed; "
                    f"expected one of: {', '.join(sorted(ALLOWED_VALUE_TYPES))}"
                ),
                file_path=file_path,
            ),
        )

    # W001: description length
    description: object = data.get(FIELD_DESCRIPTION)
    if isinstance(description, str) and len(description) < MIN_DESCRIPTION_LENGTH:
        diagnostics.append(
            Diagnostic(
                code=MT_W001,
                message=(
                    f"'{FIELD_DESCRIPTION}' is {len(description)} characters, "
                    f"under {MIN_DESCRIPTION_LENGTH}"
                ),
                file_path=file_path,
            ),
        )

    # W002: name length
    name: object = data.get(FIELD_NAME)
    if isinstance(name, str) and len(name) > MAX_NAME_LENGTH:
        diagnostics.append(
            Diagnostic(
                code=MT_W002,
                message=(f"'{FIELD_NAME}' is {len(name)} characters, exceeds {MAX_NAME_LENGTH}"),
                file_path=file_path,
            ),
        )

    # E007: datasets must be a list of strings (optional field)
    datasets: object = data.get(FIELD_DATASETS)
    if datasets is not None:
        if not isinstance(datasets, list):
            diagnostics.append(
                Diagnostic(
                    code=MT_E007,
                    message=f"'{FIELD_DATASETS}' is not a list",
                    file_path=file_path,
                ),
            )
        else:
            for i, item in enumerate(datasets):
                if not isinstance(item, str):
                    diagnostics.append(
                        Diagnostic(
                            code=MT_E007,
                            message=f"'{FIELD_DATASETS}[{i}]' is not a string",
                            file_path=file_path,
                        ),
                    )

            # E008: dataset IDs must exist
            all_dataset_ids: set[str] = _collect_all_dataset_ids()
            if len(all_dataset_ids) > 0:
                for item in datasets:
                    if isinstance(item, str) and item not in all_dataset_ids:
                        diagnostics.append(
                            Diagnostic(
                                code=MT_E008,
                                message=(
                                    f"dataset '{item}' does not exist in any task's assets/dataset/"
                                ),
                                file_path=file_path,
                            ),
                        )

    # E009: higher_is_better must be a bool when present. The field is
    # required, so absence is reported by the upstream MT-E002 check;
    # here we only catch the wrong-type case. `isinstance(x, int)` is
    # True for bools in Python, so the bool check must come first.
    higher_is_better: object = data.get(FIELD_HIGHER_IS_BETTER)
    if higher_is_better is not None and not isinstance(higher_is_better, bool):
        diagnostics.append(
            Diagnostic(
                code=MT_E009,
                message=f"'{FIELD_HIGHER_IS_BETTER}' is present but not a boolean",
                file_path=file_path,
            ),
        )

    # W003: is_key must be a bool if present
    is_key: object = data.get(FIELD_IS_KEY)
    if is_key is not None and not isinstance(is_key, bool):
        diagnostics.append(
            Diagnostic(
                code=MT_W003,
                message=f"'{FIELD_IS_KEY}' is present but not a boolean",
                file_path=file_path,
            ),
        )

    # W004: emoji must be a string if present
    emoji: object = data.get(FIELD_EMOJI)
    if emoji is not None and not isinstance(emoji, str):
        diagnostics.append(
            Diagnostic(
                code=MT_W004,
                message=f"'{FIELD_EMOJI}' is present but not a string",
                file_path=file_path,
            ),
        )

    # W005: emoji without is_key
    if emoji is not None and is_key is not True:
        diagnostics.append(
            Diagnostic(
                code=MT_W005,
                message=(f"'{FIELD_EMOJI}' is present but '{FIELD_IS_KEY}' is not true"),
                file_path=file_path,
            ),
        )

    return diagnostics


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_metric(*, metric_key: str) -> VerificationResult:
    file_path: Path = metric_definition_path(metric_key=metric_key)
    diagnostics: list[Diagnostic] = []

    # E006: file name format
    diagnostics.extend(_check_file_name(metric_key=metric_key))

    # E001: file existence and validity
    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        diagnostics.append(
            Diagnostic(
                code=MT_E001,
                message=(f"Metric definition does not exist or is not valid JSON: {file_path}"),
                file_path=file_path,
            ),
        )
        return VerificationResult(file_path=file_path, diagnostics=diagnostics)

    # E002: required fields
    missing: list[str] = check_required_fields(
        data=data,
        required_fields=REQUIRED_FIELDS,
    )
    if len(missing) > 0:
        diagnostics.append(
            Diagnostic(
                code=MT_E002,
                message=f"Missing required fields: {', '.join(missing)}",
                file_path=file_path,
            ),
        )

    # E003-E005, W001-W002: field validation
    diagnostics.extend(_check_fields(data=data, metric_key=metric_key))

    return VerificationResult(file_path=file_path, diagnostics=diagnostics)


def collect_registered_metric_keys() -> set[str]:
    if not METRICS_DIR.is_dir():
        return set()
    keys: set[str] = set()
    for entry in METRICS_DIR.iterdir():
        if entry.is_dir() and not entry.name.startswith("."):
            keys.add(entry.name)
    return keys


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _discover_metric_keys() -> list[str]:
    if not METRICS_DIR.is_dir():
        return []
    keys: list[str] = []
    for entry in sorted(METRICS_DIR.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            keys.append(entry.name)
    return keys


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify metric definition files (or all metrics)",
    )
    parser.add_argument(
        "metric_key",
        nargs="?",
        default=None,
        help="Metric key (e.g. f1_all)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Verify all metrics in meta/metrics/",
    )
    args: argparse.Namespace = parser.parse_args()

    if args.all:
        keys: list[str] = _discover_metric_keys()
        if len(keys) == 0:
            print("No metric definitions found in meta/metrics/.")
            sys.exit(0)
        has_errors: bool = False
        for key in keys:
            result: VerificationResult = verify_metric(metric_key=key)
            print_verification_result(result=result)
            if not result.passed:
                has_errors = True
        sys.exit(1 if has_errors else 0)

    if args.metric_key is None:
        parser.error("Provide a metric_key or use --all")

    result = verify_metric(metric_key=args.metric_key)
    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
