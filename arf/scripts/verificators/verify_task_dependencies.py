"""Verificator for task dependency readiness.

Checks that all dependencies of a task are satisfied before it can start.
This script is also used by verify_task_file.py for dependency validation.

Usage:
    uv run python -m arf.scripts.verificators.verify_task_dependencies <task_id>

Exit codes:
    0 — all dependencies satisfied (warnings may be present)
    1 — one or more dependency errors found
"""

import argparse
import sys
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.json_utils import load_json_file
from arf.scripts.verificators.common.paths import (
    TASKS_DIR,
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

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PREFIX: str = "TD"

FIELD_TASK_ID: str = "task_id"
FIELD_STATUS: str = "status"
FIELD_DEPENDENCIES: str = "dependencies"

STATUS_COMPLETED: str = "completed"

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

TD_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
TD_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
TD_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
TD_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)

TD_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)


# ---------------------------------------------------------------------------
# Dependency checks (reusable by other verificators)
# ---------------------------------------------------------------------------


def check_dependency_exists(
    *,
    dep_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    """Check that a dependency task folder exists."""
    dep_dir: Path = TASKS_DIR / dep_id
    if not dep_dir.is_dir():
        return [
            Diagnostic(
                code=TD_E001,
                message=f"dependency '{dep_id}' does not exist as a task folder",
                file_path=file_path,
            ),
        ]
    return []


def check_dependency_completed(
    *,
    dep_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    """Check that a dependency task has status 'completed'."""
    dep_task_data: dict[str, Any] | None = load_json_file(
        file_path=task_json_path(task_id=dep_id),
    )
    if dep_task_data is None:
        return [
            Diagnostic(
                code=TD_E002,
                message=f"dependency '{dep_id}' has no readable task.json",
                file_path=file_path,
            ),
        ]

    dep_status: str = str(dep_task_data.get(FIELD_STATUS, ""))
    if dep_status != STATUS_COMPLETED:
        return [
            Diagnostic(
                code=TD_E003,
                message=(f"dependency '{dep_id}' has status '{dep_status}', expected 'completed'"),
                file_path=file_path,
            ),
        ]
    return []


def check_all_dependencies(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    """Check all dependencies exist and are completed."""
    deps: object = data.get(FIELD_DEPENDENCIES)
    if not isinstance(deps, list):
        return []

    diagnostics: list[Diagnostic] = []
    for dep_id in deps:
        dep_str: str = str(dep_id)

        exist_diags: list[Diagnostic] = check_dependency_exists(
            dep_id=dep_str,
            file_path=file_path,
        )
        diagnostics.extend(exist_diags)
        if len(exist_diags) > 0:
            continue

        diagnostics.extend(
            check_dependency_completed(
                dep_id=dep_str,
                file_path=file_path,
            ),
        )

    return diagnostics


# ---------------------------------------------------------------------------
# Full readiness check
# ---------------------------------------------------------------------------


def verify_task_dependencies(*, task_id: str) -> VerificationResult:
    file_path: Path = task_json_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        diagnostics.append(
            Diagnostic(
                code=TD_E004,
                message=f"task.json does not exist or is not valid JSON: {file_path}",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    diagnostics.extend(
        check_all_dependencies(data=data, file_path=file_path),
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
        description="Verify that all dependencies of a task are satisfied",
    )
    parser.add_argument(
        "task_id",
        help="Task ID (e.g. t0003_download_training_corpus)",
    )
    args: argparse.Namespace = parser.parse_args()

    result: VerificationResult = verify_task_dependencies(
        task_id=args.task_id,
    )
    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
