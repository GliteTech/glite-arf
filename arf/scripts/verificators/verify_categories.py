"""Verify that all category folders conform to the category specification.

Specification: arf/specifications/category_specification.md
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
    CATEGORIES_DIR,
    category_description_path,
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

REQUIRED_FIELDS: list[str] = [
    VERSION_FIELD,
    NAME_FIELD,
    SHORT_DESCRIPTION_FIELD,
    DETAILED_DESCRIPTION_FIELD,
]

_SLUG_PATTERN: re.Pattern[str] = re.compile(r"^[a-z][a-z0-9-]*$")

MAX_SHORT_DESCRIPTION_LENGTH: int = 200
MIN_DETAILED_DESCRIPTION_LENGTH: int = 50
MAX_DETAILED_DESCRIPTION_LENGTH: int = 1000
MAX_NAME_LENGTH: int = 50

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "CA"

CA_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
CA_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
CA_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
CA_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)

CA_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
CA_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
CA_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
CA_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_slug_format(
    *,
    category_slug: str,
    file_path: Path,
) -> list[Diagnostic]:
    if _SLUG_PATTERN.match(category_slug) is None:
        return [
            Diagnostic(
                code=CA_E004,
                message=(
                    f"Category slug '{category_slug}' is invalid"
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
                code=CA_E002,
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
                code=CA_E003,
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
                code=CA_W004,
                message=(f"name has {len(name)} characters (maximum: {MAX_NAME_LENGTH})"),
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
                code=CA_W001,
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
                code=CA_W002,
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
                code=CA_W003,
                message=(
                    f"detailed_description has {len(detailed_desc)} characters"
                    f" (maximum: {MAX_DETAILED_DESCRIPTION_LENGTH})"
                ),
                file_path=file_path,
            ),
        )
    return diagnostics


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def verify_category(*, category_slug: str) -> VerificationResult:
    file_path: Path = category_description_path(
        category_slug=category_slug,
    )
    diagnostics: list[Diagnostic] = []

    diagnostics.extend(
        _check_slug_format(
            category_slug=category_slug,
            file_path=file_path,
        ),
    )

    if not file_path.exists():
        diagnostics.append(
            Diagnostic(
                code=CA_E001,
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
                code=CA_E001,
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

    return VerificationResult(
        file_path=file_path,
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _discover_category_slugs() -> list[str]:
    if not CATEGORIES_DIR.exists():
        return []
    return sorted(
        d.name for d in CATEGORIES_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
    )


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify category folder(s)",
    )
    parser.add_argument(
        "category_slug",
        nargs="?",
        default=None,
        help=(
            "Category slug (folder name) to verify."
            " If omitted, verifies all categories in meta/categories/."
        ),
    )
    args: argparse.Namespace = parser.parse_args()

    category_slugs: list[str]
    if args.category_slug is not None:
        category_slugs = [args.category_slug]
    else:
        category_slugs = _discover_category_slugs()
        if len(category_slugs) == 0:
            print("No categories found in meta/categories/")
            sys.exit(0)

    all_passed: bool = True
    for slug in category_slugs:
        result: VerificationResult = verify_category(category_slug=slug)
        print_verification_result(result=result)
        if not result.passed:
            all_passed = False

    if all_passed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
