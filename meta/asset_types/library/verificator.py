import argparse
import sys
from pathlib import Path

from arf.scripts.verificators.common.paths import (
    library_asset_dir,
    library_base_dir,
)
from arf.scripts.verificators.common.reporting import (
    print_verification_result,
)
from arf.scripts.verificators.common.types import (
    Diagnostic,
    VerificationResult,
)
from meta.asset_types.library.verify_description import (
    verify_library_description,
)
from meta.asset_types.library.verify_details import (
    verify_library_details,
)

# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_library_asset(
    *,
    library_id: str,
    task_id: str | None = None,
) -> VerificationResult:
    asset_dir: Path = library_asset_dir(
        library_id=library_id,
        task_id=task_id,
    )
    diagnostics: list[Diagnostic] = []

    diagnostics.extend(
        verify_library_details(
            library_id=library_id,
            task_id=task_id,
        ),
    )

    diagnostics.extend(
        verify_library_description(
            library_id=library_id,
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


def _discover_library_ids(*, task_id: str | None) -> list[str]:
    base_dir: Path = library_base_dir(task_id=task_id)
    if not base_dir.exists():
        return []
    return sorted(d.name for d in base_dir.iterdir() if d.is_dir() and not d.name.startswith("."))


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify library asset folder(s)",
    )
    parser.add_argument(
        "library_id",
        nargs="?",
        default=None,
        help=(
            "Library ID (folder name) to verify. "
            "If omitted, verifies all libraries in the target "
            "directory."
        ),
    )
    parser.add_argument(
        "--task-id",
        default=None,
        help=(
            "Task ID to locate libraries in "
            "tasks/<task_id>/assets/library/. "
            "If omitted, looks in top-level assets/library/."
        ),
    )
    args: argparse.Namespace = parser.parse_args()

    task_id: str | None = args.task_id
    library_ids: list[str]
    if args.library_id is not None:
        library_ids = [args.library_id]
    else:
        library_ids = _discover_library_ids(task_id=task_id)
        if len(library_ids) == 0:
            base_dir: Path = library_base_dir(task_id=task_id)
            print(f"No library assets found in {base_dir}")
            sys.exit(0)

    all_passed: bool = True
    for library_id in library_ids:
        result: VerificationResult = verify_library_asset(
            library_id=library_id,
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
