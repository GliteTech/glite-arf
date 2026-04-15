"""Verify that all task type folders conform to the task type specification.

Specification: arf/specifications/task_type_specification.md
Verificator version: 1.0
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
    TASK_TYPES_DIR,
    task_type_description_path,
    task_type_instruction_path,
)
from arf.scripts.verificators.common.reporting import (
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

VERSION_FIELD: str = "spec_version"
NAME_FIELD: str = "name"
SHORT_DESCRIPTION_FIELD: str = "short_description"
DETAILED_DESCRIPTION_FIELD: str = "detailed_description"
OPTIONAL_STEPS_FIELD: str = "optional_steps"
HAS_EXTERNAL_COSTS_FIELD: str = "has_external_costs"

REQUIRED_FIELDS: list[str] = [
    VERSION_FIELD,
    NAME_FIELD,
    SHORT_DESCRIPTION_FIELD,
    DETAILED_DESCRIPTION_FIELD,
    OPTIONAL_STEPS_FIELD,
    HAS_EXTERNAL_COSTS_FIELD,
]

_SLUG_PATTERN: re.Pattern[str] = re.compile(r"^[a-z][a-z0-9-]*$")

MAX_SHORT_DESCRIPTION_LENGTH: int = 200
MIN_DETAILED_DESCRIPTION_LENGTH: int = 50
MAX_DETAILED_DESCRIPTION_LENGTH: int = 1000
MAX_NAME_LENGTH: int = 50
MIN_INSTRUCTION_LENGTH: int = 200

VALID_OPTIONAL_STEPS: list[str] = [
    "research-papers",
    "research-internet",
    "research-code",
    "planning",
    "setup-machines",
    "teardown",
    "creative-thinking",
    "compare-literature",
]

REQUIRED_INSTRUCTION_HEADINGS: list[str] = [
    "## Planning Guidelines",
    "## Implementation Guidelines",
]

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "TY"

TY_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
TY_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
TY_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
TY_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
TY_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
TY_E006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=6,
)
TY_E007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=7,
)
TY_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)

TY_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
TY_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
TY_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
TY_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)
TY_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_slug_format(
    *,
    task_type_slug: str,
    file_path: Path,
) -> list[Diagnostic]:
    if _SLUG_PATTERN.match(task_type_slug) is None:
        return [
            Diagnostic(
                code=TY_E004,
                message=(
                    f"Task type slug '{task_type_slug}' is invalid"
                    " (must be lowercase letters, digits, and hyphens;"
                    " must start with a letter)"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_required_fields(
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
                code=TY_E002,
                message=f"Required field missing: '{field_name}'",
                file_path=file_path,
            ),
        )
    return diagnostics


def _check_version_is_int(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    version: object = data.get(VERSION_FIELD)
    if version is None:
        return []  # Already reported by required-fields check.
    if not isinstance(version, int) or isinstance(version, bool):
        return [
            Diagnostic(
                code=TY_E003,
                message=f"version must be an integer, got: {type(version).__name__}",
                file_path=file_path,
            ),
        ]
    return []


def _check_name_length(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    name: object = data.get(NAME_FIELD)
    if not isinstance(name, str):
        return []
    if len(name) > MAX_NAME_LENGTH:
        return [
            Diagnostic(
                code=TY_W004,
                message=f"name has {len(name)} characters (maximum: {MAX_NAME_LENGTH})",
                file_path=file_path,
            ),
        ]
    return []


def _check_short_description_length(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    short_desc: object = data.get(SHORT_DESCRIPTION_FIELD)
    if not isinstance(short_desc, str):
        return []
    if len(short_desc) > MAX_SHORT_DESCRIPTION_LENGTH:
        return [
            Diagnostic(
                code=TY_W001,
                message=(
                    f"short_description has {len(short_desc)} characters"
                    f" (maximum: {MAX_SHORT_DESCRIPTION_LENGTH})"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_detailed_description_length(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    detailed_desc: object = data.get(DETAILED_DESCRIPTION_FIELD)
    if not isinstance(detailed_desc, str):
        return []
    diagnostics: list[Diagnostic] = []
    if len(detailed_desc) < MIN_DETAILED_DESCRIPTION_LENGTH:
        diagnostics.append(
            Diagnostic(
                code=TY_W002,
                message=(
                    f"detailed_description has {len(detailed_desc)} characters"
                    f" (minimum: {MIN_DETAILED_DESCRIPTION_LENGTH})"
                ),
                file_path=file_path,
            ),
        )
    if len(detailed_desc) > MAX_DETAILED_DESCRIPTION_LENGTH:
        diagnostics.append(
            Diagnostic(
                code=TY_W003,
                message=(
                    f"detailed_description has {len(detailed_desc)} characters"
                    f" (maximum: {MAX_DETAILED_DESCRIPTION_LENGTH})"
                ),
                file_path=file_path,
            ),
        )
    return diagnostics


def _check_has_external_costs_is_bool(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    if HAS_EXTERNAL_COSTS_FIELD not in data:
        return []  # Already reported by required-fields check.
    value: object = data[HAS_EXTERNAL_COSTS_FIELD]
    if not isinstance(value, bool):
        return [
            Diagnostic(
                code=TY_E008,
                message=(f"{HAS_EXTERNAL_COSTS_FIELD} must be a bool, got: {type(value).__name__}"),
                file_path=file_path,
            ),
        ]
    return []


def _check_optional_steps(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    steps: object = data.get(OPTIONAL_STEPS_FIELD)
    if steps is None:
        return []  # Already reported by required-fields check.
    if not isinstance(steps, list):
        return [
            Diagnostic(
                code=TY_E007,
                message=(f"optional_steps must be a list, got: {type(steps).__name__}"),
                file_path=file_path,
            ),
        ]
    diagnostics: list[Diagnostic] = []
    for item in steps:
        if not isinstance(item, str) or item not in VALID_OPTIONAL_STEPS:
            diagnostics.append(
                Diagnostic(
                    code=TY_E007,
                    message=(
                        f"Invalid value in optional_steps: '{item}'"
                        f" (valid values: {VALID_OPTIONAL_STEPS})"
                    ),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_instruction_exists(
    *,
    task_type_slug: str,
) -> list[Diagnostic]:
    instruction_path: Path = task_type_instruction_path(
        task_type_slug=task_type_slug,
    )
    if not instruction_path.exists():
        return [
            Diagnostic(
                code=TY_E005,
                message=f"instruction.md does not exist: {instruction_path}",
                file_path=instruction_path,
            ),
        ]
    return []


def _check_instruction_headings(
    *,
    task_type_slug: str,
) -> list[Diagnostic]:
    instruction_path: Path = task_type_instruction_path(
        task_type_slug=task_type_slug,
    )
    if not instruction_path.exists():
        return []  # Already reported by _check_instruction_exists.
    try:
        content: str = instruction_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    diagnostics: list[Diagnostic] = []
    for heading in REQUIRED_INSTRUCTION_HEADINGS:
        if heading not in content:
            diagnostics.append(
                Diagnostic(
                    code=TY_E006,
                    message=(f"instruction.md is missing required heading: '{heading}'"),
                    file_path=instruction_path,
                ),
            )
    return diagnostics


def _check_instruction_length(
    *,
    task_type_slug: str,
) -> list[Diagnostic]:
    instruction_path: Path = task_type_instruction_path(
        task_type_slug=task_type_slug,
    )
    if not instruction_path.exists():
        return []  # Already reported by _check_instruction_exists.
    try:
        content: str = instruction_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    if len(content) < MIN_INSTRUCTION_LENGTH:
        return [
            Diagnostic(
                code=TY_W005,
                message=(
                    f"instruction.md has {len(content)} characters"
                    f" (minimum: {MIN_INSTRUCTION_LENGTH})"
                ),
                file_path=instruction_path,
            ),
        ]
    return []


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def verify_task_type(*, task_type_slug: str) -> VerificationResult:
    file_path: Path = task_type_description_path(
        task_type_slug=task_type_slug,
    )
    diagnostics: list[Diagnostic] = []

    diagnostics.extend(
        _check_slug_format(
            task_type_slug=task_type_slug,
            file_path=file_path,
        ),
    )

    if not file_path.exists():
        diagnostics.append(
            Diagnostic(
                code=TY_E001,
                message=f"description.json does not exist: {file_path}",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        diagnostics.append(
            Diagnostic(
                code=TY_E001,
                message=f"description.json is not valid JSON: {file_path}",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    diagnostics.extend(
        _check_required_fields(data=data, file_path=file_path),
    )
    diagnostics.extend(
        _check_version_is_int(data=data, file_path=file_path),
    )
    diagnostics.extend(
        _check_name_length(data=data, file_path=file_path),
    )
    diagnostics.extend(
        _check_short_description_length(data=data, file_path=file_path),
    )
    diagnostics.extend(
        _check_detailed_description_length(data=data, file_path=file_path),
    )
    diagnostics.extend(
        _check_optional_steps(data=data, file_path=file_path),
    )
    diagnostics.extend(
        _check_has_external_costs_is_bool(data=data, file_path=file_path),
    )
    diagnostics.extend(
        _check_instruction_exists(task_type_slug=task_type_slug),
    )
    diagnostics.extend(
        _check_instruction_headings(task_type_slug=task_type_slug),
    )
    diagnostics.extend(
        _check_instruction_length(task_type_slug=task_type_slug),
    )

    return VerificationResult(
        file_path=file_path,
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _discover_task_type_slugs() -> list[str]:
    if not TASK_TYPES_DIR.exists():
        return []
    return sorted(
        d.name for d in TASK_TYPES_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
    )


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify task type folder(s)",
    )
    parser.add_argument(
        "task_type_slug",
        nargs="?",
        default=None,
        help=(
            "Task type slug (folder name) to verify."
            " If omitted, verifies all task types in meta/task_types/."
        ),
    )
    args: argparse.Namespace = parser.parse_args()

    task_type_slugs: list[str]
    if args.task_type_slug is not None:
        task_type_slugs = [args.task_type_slug]
    else:
        task_type_slugs = _discover_task_type_slugs()
        if len(task_type_slugs) == 0:
            print("No task types found in meta/task_types/")
            sys.exit(0)

    all_passed: bool = True
    for slug in task_type_slugs:
        result: VerificationResult = verify_task_type(task_type_slug=slug)
        print_verification_result(result=result)
        if not result.passed:
            all_passed = False

    if all_passed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
