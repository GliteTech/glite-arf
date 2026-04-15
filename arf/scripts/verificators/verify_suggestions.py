"""Verificator for suggestions.json files.

Validates the structure and content of task suggestion files against
the suggestions specification (arf/specifications/suggestions_specification.md).

Usage:
    uv run python -m arf.scripts.verificators.verify_suggestions <task_id>
    uv run python -m arf.scripts.verificators.verify_suggestions --all

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.paths import (
    CATEGORIES_DIR,
    TASKS_DIR,
    suggestions_path,
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

_PREFIX: str = "SG"

FIELD_SPEC_VERSION: str = "spec_version"
FIELD_SUGGESTIONS: str = "suggestions"
FIELD_ID: str = "id"
FIELD_TITLE: str = "title"
FIELD_DESCRIPTION: str = "description"
FIELD_KIND: str = "kind"
FIELD_PRIORITY: str = "priority"
FIELD_SOURCE_TASK: str = "source_task"
FIELD_SOURCE_PAPER: str = "source_paper"
FIELD_CATEGORIES: str = "categories"
FIELD_STATUS: str = "status"

REQUIRED_SUGGESTION_FIELDS: list[str] = [
    FIELD_ID,
    FIELD_TITLE,
    FIELD_DESCRIPTION,
    FIELD_KIND,
    FIELD_PRIORITY,
    FIELD_SOURCE_TASK,
    FIELD_SOURCE_PAPER,
    FIELD_CATEGORIES,
]

ALLOWED_KINDS: set[str] = {
    "experiment",
    "technique",
    "evaluation",
    "dataset",
    "library",
}

ALLOWED_PRIORITIES: set[str] = {"high", "medium", "low"}
ALLOWED_STATUSES: set[str] = {"active", "rejected"}

ID_PATTERN: re.Pattern[str] = re.compile(r"^S-\d{4}-\d{2}$")

MAX_TITLE_LENGTH: int = 120
MIN_DESCRIPTION_LENGTH: int = 20
MAX_DESCRIPTION_LENGTH: int = 1000

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

SG_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
SG_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
SG_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
SG_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
SG_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
SG_E006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=6,
)
SG_E007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=7,
)
SG_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
SG_E009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=9,
)
SG_E010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=10,
)
SG_E011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=11,
)
SG_E012: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=12,
)
SG_E013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=13,
)

SG_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
SG_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
SG_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
SG_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)
SG_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
SG_W006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=6,
)


# ---------------------------------------------------------------------------
# Internal result types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _LoadResult:
    data: dict[str, Any] | None
    diagnostics: list[Diagnostic] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class _TopLevelResult:
    suggestions: list[Any] | None
    diagnostics: list[Diagnostic] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def _load_suggestions_file(
    *,
    file_path: Path,
) -> _LoadResult:
    if not file_path.exists():
        return _LoadResult(
            data=None,
            diagnostics=[
                Diagnostic(
                    code=SG_E001,
                    message=f"suggestions.json does not exist: {file_path}",
                    file_path=file_path,
                ),
            ],
        )

    try:
        raw: str = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        return _LoadResult(
            data=None,
            diagnostics=[
                Diagnostic(
                    code=SG_E001,
                    message=f"Cannot read suggestions.json: {exc}",
                    file_path=file_path,
                ),
            ],
        )

    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _LoadResult(
            data=None,
            diagnostics=[
                Diagnostic(
                    code=SG_E001,
                    message=f"suggestions.json is not valid JSON: {exc}",
                    file_path=file_path,
                ),
            ],
        )

    if not isinstance(data, dict):
        return _LoadResult(
            data=None,
            diagnostics=[
                Diagnostic(
                    code=SG_E002,
                    message="Top-level value is not a JSON object",
                    file_path=file_path,
                ),
            ],
        )

    return _LoadResult(data=data)


# ---------------------------------------------------------------------------
# Top-level structure checks
# ---------------------------------------------------------------------------


def _check_top_level(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> _TopLevelResult:
    diagnostics: list[Diagnostic] = []

    if FIELD_SPEC_VERSION not in data:
        diagnostics.append(
            Diagnostic(
                code=SG_E003,
                message=f"Missing '{FIELD_SPEC_VERSION}' field",
                file_path=file_path,
            ),
        )

    suggestions_value: Any = data.get(FIELD_SUGGESTIONS)
    if suggestions_value is None and FIELD_SUGGESTIONS not in data:
        diagnostics.append(
            Diagnostic(
                code=SG_E004,
                message=f"Missing '{FIELD_SUGGESTIONS}' field",
                file_path=file_path,
            ),
        )
        return _TopLevelResult(suggestions=None, diagnostics=diagnostics)

    if not isinstance(suggestions_value, list):
        diagnostics.append(
            Diagnostic(
                code=SG_E004,
                message=f"'{FIELD_SUGGESTIONS}' is not an array",
                file_path=file_path,
            ),
        )
        return _TopLevelResult(suggestions=None, diagnostics=diagnostics)

    return _TopLevelResult(
        suggestions=suggestions_value,
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# Per-suggestion checks
# ---------------------------------------------------------------------------


def _check_suggestion(
    *,
    suggestion: Any,
    index: int,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    label: str = f"suggestions[{index}]"

    if not isinstance(suggestion, dict):
        diagnostics.append(
            Diagnostic(
                code=SG_E005,
                message=f"{label}: not a JSON object",
                file_path=file_path,
            ),
        )
        return diagnostics

    # E006: required fields
    for field_name in REQUIRED_SUGGESTION_FIELDS:
        if field_name not in suggestion:
            diagnostics.append(
                Diagnostic(
                    code=SG_E006,
                    message=f"{label}: missing required field '{field_name}'",
                    file_path=file_path,
                ),
            )

    # E007: id format
    suggestion_id: Any = suggestion.get(FIELD_ID)
    if isinstance(suggestion_id, str) and ID_PATTERN.match(suggestion_id) is None:
        diagnostics.append(
            Diagnostic(
                code=SG_E007,
                message=f"{label}: id '{suggestion_id}' does not match S-XXXX-NN format",
                file_path=file_path,
            ),
        )

    # E008: kind
    kind: Any = suggestion.get(FIELD_KIND)
    if isinstance(kind, str) and kind not in ALLOWED_KINDS:
        diagnostics.append(
            Diagnostic(
                code=SG_E008,
                message=(
                    f"{label}: kind '{kind}' is not allowed; "
                    f"expected one of: {', '.join(sorted(ALLOWED_KINDS))}"
                ),
                file_path=file_path,
            ),
        )

    # E009: priority
    priority: Any = suggestion.get(FIELD_PRIORITY)
    if isinstance(priority, str) and priority not in ALLOWED_PRIORITIES:
        diagnostics.append(
            Diagnostic(
                code=SG_E009,
                message=(
                    f"{label}: priority '{priority}' is not allowed; "
                    f"expected one of: {', '.join(sorted(ALLOWED_PRIORITIES))}"
                ),
                file_path=file_path,
            ),
        )

    # E010: source_task matches task_id
    source_task: Any = suggestion.get(FIELD_SOURCE_TASK)
    if isinstance(source_task, str) and source_task != task_id:
        diagnostics.append(
            Diagnostic(
                code=SG_E010,
                message=(
                    f"{label}: source_task '{source_task}' does not match task folder '{task_id}'"
                ),
                file_path=file_path,
            ),
        )

    # E012: categories is a list
    categories: Any = suggestion.get(FIELD_CATEGORIES)
    if categories is not None and not isinstance(categories, list):
        diagnostics.append(
            Diagnostic(
                code=SG_E012,
                message=f"{label}: categories is not a list",
                file_path=file_path,
            ),
        )

    # E013: status is valid (optional field)
    status: Any = suggestion.get(FIELD_STATUS)
    if status is not None and isinstance(status, str) and status not in ALLOWED_STATUSES:
        diagnostics.append(
            Diagnostic(
                code=SG_E013,
                message=(
                    f"{label}: status '{status}' is not allowed; "
                    f"expected one of: {', '.join(sorted(ALLOWED_STATUSES))}"
                ),
                file_path=file_path,
            ),
        )

    # W001: title length
    title: Any = suggestion.get(FIELD_TITLE)
    if isinstance(title, str):
        if len(title.strip()) == 0:
            diagnostics.append(
                Diagnostic(
                    code=SG_W004,
                    message=f"{label}: title is empty or whitespace-only",
                    file_path=file_path,
                ),
            )
        elif len(title) > MAX_TITLE_LENGTH:
            diagnostics.append(
                Diagnostic(
                    code=SG_W001,
                    message=(
                        f"{label}: title is {len(title)} characters, exceeds {MAX_TITLE_LENGTH}"
                    ),
                    file_path=file_path,
                ),
            )

    # W002/W003/W005: description length
    description: Any = suggestion.get(FIELD_DESCRIPTION)
    if isinstance(description, str):
        if len(description.strip()) == 0:
            diagnostics.append(
                Diagnostic(
                    code=SG_W005,
                    message=f"{label}: description is empty or whitespace-only",
                    file_path=file_path,
                ),
            )
        else:
            if len(description) < MIN_DESCRIPTION_LENGTH:
                diagnostics.append(
                    Diagnostic(
                        code=SG_W002,
                        message=(
                            f"{label}: description is {len(description)} characters, "
                            f"under {MIN_DESCRIPTION_LENGTH}"
                        ),
                        file_path=file_path,
                    ),
                )
            if len(description) > MAX_DESCRIPTION_LENGTH:
                diagnostics.append(
                    Diagnostic(
                        code=SG_W003,
                        message=(
                            f"{label}: description is {len(description)} characters, "
                            f"exceeds {MAX_DESCRIPTION_LENGTH}"
                        ),
                        file_path=file_path,
                    ),
                )

    # W006: category slugs exist
    if isinstance(categories, list):
        for cat in categories:
            if isinstance(cat, str):
                cat_dir: Path = CATEGORIES_DIR / cat
                if not cat_dir.is_dir():
                    diagnostics.append(
                        Diagnostic(
                            code=SG_W006,
                            message=(
                                f"{label}: category '{cat}' does not exist in meta/categories/"
                            ),
                            file_path=file_path,
                        ),
                    )

    return diagnostics


# ---------------------------------------------------------------------------
# Duplicate ID check
# ---------------------------------------------------------------------------


def _check_duplicate_ids(
    *,
    suggestions: list[Any],
    file_path: Path,
) -> list[Diagnostic]:
    seen: set[str] = set()
    diagnostics: list[Diagnostic] = []
    for i, suggestion in enumerate(suggestions):
        if not isinstance(suggestion, dict):
            continue
        suggestion_id: Any = suggestion.get(FIELD_ID)
        if not isinstance(suggestion_id, str):
            continue
        if suggestion_id in seen:
            diagnostics.append(
                Diagnostic(
                    code=SG_E011,
                    message=f"suggestions[{i}]: duplicate id '{suggestion_id}'",
                    file_path=file_path,
                ),
            )
        seen.add(suggestion_id)
    return diagnostics


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_suggestions(*, task_id: str) -> VerificationResult:
    file_path: Path = suggestions_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    load_result: _LoadResult = _load_suggestions_file(file_path=file_path)
    diagnostics.extend(load_result.diagnostics)

    if load_result.data is None:
        return VerificationResult(file_path=file_path, diagnostics=diagnostics)

    top_result: _TopLevelResult = _check_top_level(
        data=load_result.data,
        file_path=file_path,
    )
    diagnostics.extend(top_result.diagnostics)

    if top_result.suggestions is None:
        return VerificationResult(file_path=file_path, diagnostics=diagnostics)

    for i, suggestion in enumerate(top_result.suggestions):
        diagnostics.extend(
            _check_suggestion(
                suggestion=suggestion,
                index=i,
                task_id=task_id,
                file_path=file_path,
            ),
        )

    diagnostics.extend(
        _check_duplicate_ids(
            suggestions=top_result.suggestions,
            file_path=file_path,
        ),
    )

    return VerificationResult(file_path=file_path, diagnostics=diagnostics)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _discover_task_ids() -> list[str]:
    if not TASKS_DIR.exists():
        return []
    task_ids: list[str] = []
    for task_dir in sorted(TASKS_DIR.iterdir()):
        if not task_dir.is_dir() or task_dir.name.startswith("."):
            continue
        if suggestions_path(task_id=task_dir.name).exists():
            task_ids.append(task_dir.name)
    return task_ids


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify suggestions.json file(s)",
    )
    parser.add_argument(
        "task_id",
        nargs="?",
        default=None,
        help="Task ID to verify. If omitted, use --all.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Verify suggestions.json in all task folders.",
    )
    args: argparse.Namespace = parser.parse_args()

    task_ids: list[str]
    if args.task_id is not None:
        task_ids = [args.task_id]
    elif args.all:
        task_ids = _discover_task_ids()
        if len(task_ids) == 0:
            print("No tasks with suggestions.json found.")
            sys.exit(0)
    else:
        parser.error("Provide a task_id or use --all")
        return

    all_passed: bool = True
    for task_id in task_ids:
        result: VerificationResult = verify_suggestions(task_id=task_id)
        print_verification_result(result=result)
        if not result.passed:
            all_passed = False

    if all_passed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
