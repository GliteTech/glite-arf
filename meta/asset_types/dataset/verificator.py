import argparse
import sys
from pathlib import Path

from arf.scripts.verificators.common.paths import (
    dataset_asset_dir,
    dataset_base_dir,
    dataset_files_dir,
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
from meta.asset_types.dataset.verify_description import (
    verify_dataset_description,
)
from meta.asset_types.dataset.verify_details import (
    verify_dataset_details,
)

# ---------------------------------------------------------------------------
# Diagnostic codes (folder-level checks only)
# ---------------------------------------------------------------------------

_PREFIX: str = "DA"

DA_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)


# ---------------------------------------------------------------------------
# Folder-level checks
# ---------------------------------------------------------------------------


def _check_files_dir(
    *,
    dataset_id: str,
    task_id: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    files_dir: Path = dataset_files_dir(
        dataset_id=dataset_id,
        task_id=task_id,
    )
    if not files_dir.exists():
        return [
            Diagnostic(
                code=DA_E003,
                message=f"files/ directory does not exist: {files_dir}",
                file_path=file_path,
            ),
        ]
    children: list[Path] = list(files_dir.iterdir())
    if len(children) == 0:
        return [
            Diagnostic(
                code=DA_E003,
                message=f"files/ directory is empty: {files_dir}",
                file_path=file_path,
            ),
        ]
    return []


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_dataset_asset(
    *,
    dataset_id: str,
    task_id: str | None = None,
) -> VerificationResult:
    asset_dir: Path = dataset_asset_dir(
        dataset_id=dataset_id,
        task_id=task_id,
    )
    diagnostics: list[Diagnostic] = []

    diagnostics.extend(
        _check_files_dir(
            dataset_id=dataset_id,
            task_id=task_id,
            file_path=asset_dir,
        ),
    )

    diagnostics.extend(
        verify_dataset_details(
            dataset_id=dataset_id,
            task_id=task_id,
        ),
    )

    diagnostics.extend(
        verify_dataset_description(
            dataset_id=dataset_id,
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


def _discover_dataset_ids(*, task_id: str | None) -> list[str]:
    base_dir: Path = dataset_base_dir(task_id=task_id)
    if not base_dir.exists():
        return []
    return sorted(d.name for d in base_dir.iterdir() if d.is_dir() and not d.name.startswith("."))


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify dataset asset folder(s)",
    )
    parser.add_argument(
        "dataset_id",
        nargs="?",
        default=None,
        help=(
            "Dataset ID (folder name) to verify. "
            "If omitted, verifies all datasets in the target "
            "directory."
        ),
    )
    parser.add_argument(
        "--task-id",
        default=None,
        help=(
            "Task ID to locate datasets in "
            "tasks/<task_id>/assets/dataset/. "
            "If omitted, looks in top-level assets/dataset/."
        ),
    )
    args: argparse.Namespace = parser.parse_args()

    task_id: str | None = args.task_id
    dataset_ids: list[str]
    if args.dataset_id is not None:
        dataset_ids = [args.dataset_id]
    else:
        dataset_ids = _discover_dataset_ids(task_id=task_id)
        if len(dataset_ids) == 0:
            base_dir: Path = dataset_base_dir(task_id=task_id)
            print(f"No dataset assets found in {base_dir}")
            sys.exit(0)

    all_passed: bool = True
    for dataset_id in dataset_ids:
        result: VerificationResult = verify_dataset_asset(
            dataset_id=dataset_id,
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
