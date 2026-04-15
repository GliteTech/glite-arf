"""Verify that project/budget.json conforms to the project budget specification.

Specification: arf/specifications/project_budget_specification.md
Verificator version: 1
"""

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from arf.scripts.verificators.common.paths import PROJECT_BUDGET_PATH
from arf.scripts.verificators.common.project_budget import ProjectBudgetModel
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
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "PB"

PB_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
PB_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
PB_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
PB_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)

PB_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
PB_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)


# ---------------------------------------------------------------------------
# Verifier
# ---------------------------------------------------------------------------


def verify_project_budget(
    *,
    file_path: Path | None = None,
) -> VerificationResult:
    path: Path = file_path if file_path is not None else PROJECT_BUDGET_PATH
    diagnostics: list[Diagnostic] = []

    if not path.exists():
        diagnostics.append(
            Diagnostic(
                code=PB_E001,
                message=f"project/budget.json does not exist: {path}",
                file_path=path,
            ),
        )
        return VerificationResult(file_path=path, diagnostics=diagnostics)

    try:
        raw: str = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        diagnostics.append(
            Diagnostic(
                code=PB_E002,
                message=f"Could not read project/budget.json: {exc}",
                file_path=path,
            ),
        )
        return VerificationResult(file_path=path, diagnostics=diagnostics)

    try:
        parsed: object = json.loads(raw)
    except json.JSONDecodeError as exc:
        diagnostics.append(
            Diagnostic(
                code=PB_E002,
                message=f"project/budget.json is not valid JSON: {exc.msg}",
                file_path=path,
            ),
        )
        return VerificationResult(file_path=path, diagnostics=diagnostics)

    if not isinstance(parsed, dict):
        diagnostics.append(
            Diagnostic(
                code=PB_E003,
                message="project/budget.json top-level value is not a JSON object",
                file_path=path,
            ),
        )
        return VerificationResult(file_path=path, diagnostics=diagnostics)

    try:
        budget: ProjectBudgetModel = ProjectBudgetModel.model_validate(parsed)
    except ValidationError as exc:
        for error in exc.errors():
            location: str = ".".join(str(item) for item in error["loc"])
            diagnostics.append(
                Diagnostic(
                    code=PB_E004,
                    message=f"Invalid budget field '{location}': {error['msg']}",
                    file_path=path,
                ),
            )
        return VerificationResult(file_path=path, diagnostics=diagnostics)

    if budget.per_task_default_limit > budget.total_budget:
        diagnostics.append(
            Diagnostic(
                code=PB_W001,
                message=(
                    "per_task_default_limit exceeds total_budget; a single default task would "
                    "consume more than the full project budget"
                ),
                file_path=path,
            ),
        )

    if len(budget.available_services) == 0:
        diagnostics.append(
            Diagnostic(
                code=PB_W002,
                message="available_services is empty; paid-service usage cannot be categorized",
                file_path=path,
            ),
        )

    return VerificationResult(file_path=path, diagnostics=diagnostics)


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify project/budget.json",
    )
    parser.parse_args()

    result: VerificationResult = verify_project_budget()
    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
