import argparse
import sys
from pathlib import Path

from arf.scripts.verificators.common.paths import (
    model_asset_dir,
    model_base_dir,
    model_files_dir,
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
from meta.asset_types.model.verify_description import (
    verify_model_description,
)
from meta.asset_types.model.verify_details import (
    verify_model_details,
)

# ---------------------------------------------------------------------------
# Diagnostic codes (folder-level checks only)
# ---------------------------------------------------------------------------

_PREFIX: str = "MA"

MA_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)


# ---------------------------------------------------------------------------
# Folder-level checks
# ---------------------------------------------------------------------------


def _check_files_dir(
    *,
    model_id: str,
    task_id: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    files_dir: Path = model_files_dir(
        model_id=model_id,
        task_id=task_id,
    )
    if not files_dir.exists():
        return [
            Diagnostic(
                code=MA_E003,
                message=f"files/ directory does not exist: {files_dir}",
                file_path=file_path,
            ),
        ]
    children: list[Path] = list(files_dir.iterdir())
    if len(children) == 0:
        return [
            Diagnostic(
                code=MA_E003,
                message=f"files/ directory is empty: {files_dir}",
                file_path=file_path,
            ),
        ]
    return []


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_model_asset(
    *,
    model_id: str,
    task_id: str | None = None,
) -> VerificationResult:
    asset_dir: Path = model_asset_dir(
        model_id=model_id,
        task_id=task_id,
    )
    diagnostics: list[Diagnostic] = []

    diagnostics.extend(
        _check_files_dir(
            model_id=model_id,
            task_id=task_id,
            file_path=asset_dir,
        ),
    )

    diagnostics.extend(
        verify_model_details(
            model_id=model_id,
            task_id=task_id,
        ),
    )

    diagnostics.extend(
        verify_model_description(
            model_id=model_id,
            task_id=task_id,
        ),
    )

    return VerificationResult(
        file_path=asset_dir,
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _discover_model_ids(*, task_id: str | None) -> list[str]:
    base_dir: Path = model_base_dir(task_id=task_id)
    if not base_dir.exists():
        return []
    return sorted(d.name for d in base_dir.iterdir() if d.is_dir() and not d.name.startswith("."))


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify model asset folder(s)",
    )
    parser.add_argument(
        "model_id",
        nargs="?",
        default=None,
        help=(
            "Model ID (folder name) to verify. "
            "If omitted, verifies all models in the target "
            "directory."
        ),
    )
    parser.add_argument(
        "--task-id",
        default=None,
        help=(
            "Task ID to locate models in "
            "tasks/<task_id>/assets/model/. "
            "If omitted, looks in top-level assets/model/."
        ),
    )
    args: argparse.Namespace = parser.parse_args()

    task_id: str | None = args.task_id
    model_ids: list[str]
    if args.model_id is not None:
        model_ids = [args.model_id]
    else:
        model_ids = _discover_model_ids(task_id=task_id)
        if len(model_ids) == 0:
            base_dir: Path = model_base_dir(task_id=task_id)
            print(f"No model assets found in {base_dir}")
            sys.exit(0)

    all_passed: bool = True
    for model_id in model_ids:
        result: VerificationResult = verify_model_asset(
            model_id=model_id,
            task_id=task_id,
        )
        print_verification_result(result=result)
        if not result.passed:
            all_passed = False

    if all_passed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
