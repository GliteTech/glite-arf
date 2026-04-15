import argparse
import sys
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.json_utils import load_json_file
from arf.scripts.verificators.common.paths import (
    paper_asset_dir,
    paper_base_dir,
    paper_details_path,
    paper_files_dir,
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
from meta.asset_types.paper.verify_details import verify_paper_details
from meta.asset_types.paper.verify_summary import verify_paper_summary

# ---------------------------------------------------------------------------
# Diagnostic codes (folder-level checks only)
# ---------------------------------------------------------------------------

_PREFIX: str = "PA"

PA_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
PA_W012: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=12,
)

CITATION_KEY_FIELD: str = "citation_key"
DOWNLOAD_STATUS_FIELD: str = "download_status"


# ---------------------------------------------------------------------------
# Folder-level checks
# ---------------------------------------------------------------------------


def _check_files_dir(
    *,
    paper_id: str,
    download_status: str | None,
    task_id: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    files_dir: Path = paper_files_dir(paper_id=paper_id, task_id=task_id)
    if not files_dir.exists():
        return [
            Diagnostic(
                code=PA_E003,
                message=f"files/ directory does not exist: {files_dir}",
                file_path=file_path,
            ),
        ]
    children: list[Path] = list(files_dir.iterdir())
    if len(children) == 0 and download_status != "failed":
        return [
            Diagnostic(
                code=PA_E003,
                message=f"files/ directory is empty: {files_dir}",
                file_path=file_path,
            ),
        ]
    if len(children) == 0 and download_status == "failed":
        gitkeep: Path = files_dir / ".gitkeep"
        if not gitkeep.exists():
            return [
                Diagnostic(
                    code=PA_W012,
                    message=(
                        "files/ directory is empty for failed download"
                        " — add .gitkeep so git preserves the directory"
                    ),
                    file_path=file_path,
                ),
            ]
    return []


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_paper_asset(
    *,
    paper_id: str,
    task_id: str | None = None,
) -> VerificationResult:
    asset_dir: Path = paper_asset_dir(paper_id=paper_id, task_id=task_id)
    diagnostics: list[Diagnostic] = []

    # Read details.json early — needed for download_status and citation_key
    expected_citation_key: str | None = None
    download_status: str | None = None
    details_path: Path = paper_details_path(paper_id=paper_id, task_id=task_id)
    if details_path.exists():
        data: dict[str, Any] | None = load_json_file(file_path=details_path)
        if data is not None:
            raw_key: object = data.get(CITATION_KEY_FIELD)
            if isinstance(raw_key, str):
                expected_citation_key = raw_key
            raw_status: object = data.get(DOWNLOAD_STATUS_FIELD)
            if isinstance(raw_status, str):
                download_status = raw_status

    # Folder-level: files/ directory (skip empty check when download failed)
    diagnostics.extend(
        _check_files_dir(
            paper_id=paper_id,
            download_status=download_status,
            task_id=task_id,
            file_path=asset_dir,
        ),
    )

    # details.json checks
    diagnostics.extend(verify_paper_details(paper_id=paper_id, task_id=task_id))

    # summary.md checks
    diagnostics.extend(
        verify_paper_summary(
            paper_id=paper_id,
            expected_citation_key=expected_citation_key,
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


def _discover_paper_ids(*, task_id: str | None) -> list[str]:
    base_dir: Path = paper_base_dir(task_id=task_id)
    if not base_dir.exists():
        return []
    return sorted(d.name for d in base_dir.iterdir() if d.is_dir() and not d.name.startswith("."))


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify paper asset folder(s)",
    )
    parser.add_argument(
        "paper_id",
        nargs="?",
        default=None,
        help=(
            "Paper ID (folder name) to verify. "
            "If omitted, verifies all papers in the target directory."
        ),
    )
    parser.add_argument(
        "--task-id",
        default=None,
        help=(
            "Task ID to locate papers in tasks/<task_id>/assets/paper/. "
            "If omitted, looks in top-level assets/paper/."
        ),
    )
    args: argparse.Namespace = parser.parse_args()

    task_id: str | None = args.task_id
    paper_ids: list[str]
    if args.paper_id is not None:
        paper_ids = [args.paper_id]
    else:
        paper_ids = _discover_paper_ids(task_id=task_id)
        if len(paper_ids) == 0:
            base_dir: Path = paper_base_dir(task_id=task_id)
            print(f"No paper assets found in {base_dir}")
            sys.exit(0)

    all_passed: bool = True
    for paper_id in paper_ids:
        result: VerificationResult = verify_paper_asset(
            paper_id=paper_id,
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
