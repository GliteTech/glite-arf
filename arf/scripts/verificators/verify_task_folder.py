"""Verificator for task folder structure.

Checks that a task folder contains all required directories and files
as defined in the task folder specification
(arf/specifications/task_folder_specification.md).

Usage:
    uv run python -m arf.scripts.verificators.verify_task_folder <task_id>
    uv run python -m arf.scripts.verificators.verify_task_folder --all

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import argparse
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from arf.scripts.common.task_description import (
    FIELD_LONG_DESCRIPTION_FILE,
    is_valid_task_description_file_name,
    task_description_file_path,
)
from arf.scripts.verificators.common.json_utils import load_json_file
from arf.scripts.verificators.common.paths import (
    TASKS_DIR,
    assets_dir,
    command_logs_dir,
    corrections_dir,
    costs_path,
    logs_dir,
    metrics_path,
    plan_path,
    remote_machines_path,
    research_internet_path,
    research_papers_path,
    results_detailed_path,
    results_images_dir,
    results_summary_path,
    search_logs_dir,
    session_logs_dir,
    step_logs_dir,
    step_tracker_path,
    suggestions_path,
    task_dir,
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

_PREFIX: str = "FD"
type TaskID = str

FIELD_STATUS: str = "status"
FIELD_STEPS: str = "steps"
FIELD_NAME: str = "name"
STATUS_SKIPPED: str = "skipped"


class TaskStatus(StrEnum):
    COMPLETED = "completed"


REQUIRED_TOP_DIRS: list[str] = [
    "plan",
    "research",
    "assets",
    "results",
    "corrections",
    "intervention",
    "logs",
]

ALLOWED_ROOT_FILES: set[str] = {
    "task.json",
    "step_tracker.json",
    "__init__.py",
}

OPTIONAL_ROOT_DIRS: set[str] = {
    "code",
    "data",
}

ALLOWED_ROOT_DIRS: set[str] = set(REQUIRED_TOP_DIRS) | OPTIONAL_ROOT_DIRS

# Build artifacts that may appear in task folders due to Python imports,
# pytest, or mypy runs. These are not task output and should be ignored
# by the verificator (they are already in .gitignore).
IGNORED_ROOT_DIRS: set[str] = {
    "__pycache__",
}

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

FD_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
FD_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
FD_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
FD_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
FD_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
FD_E006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=6,
)
FD_E007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=7,
)
FD_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
FD_E009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=9,
)
FD_E010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=10,
)
FD_E011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=11,
)
FD_E012: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=12,
)
FD_E013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=13,
)
FD_E014: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=14,
)
FD_E015: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=15,
)
FD_E016: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=16,
)

FD_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
FD_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
FD_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
FD_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)
FD_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
FD_W006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=6,
)


# ---------------------------------------------------------------------------
# Internal types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _CompletedFileCheck:
    file_path: Path
    code: DiagnosticCode
    label: str
    skip_if_step: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _skipped_step_names(*, task_id: TaskID) -> set[str]:
    """Return names of steps marked 'skipped' in step_tracker.json."""
    st_path: Path = step_tracker_path(task_id=task_id)
    if not st_path.exists():
        return set()
    data: object = load_json_file(file_path=st_path)
    if not isinstance(data, dict):
        return set()
    steps: object = data.get(FIELD_STEPS)
    if not isinstance(steps, list):
        return set()
    result: set[str] = set()
    for entry in steps:
        if not isinstance(entry, dict):
            continue
        name: object = entry.get(FIELD_NAME)
        status: object = entry.get(FIELD_STATUS)
        if isinstance(name, str) and status == STATUS_SKIPPED:
            result.add(name)
    return result


def _get_task_status(*, task_id: TaskID) -> TaskStatus | None:
    data: dict[str, object] | None = load_json_file(
        file_path=task_json_path(task_id=task_id),
    )
    if data is None:
        return None
    status: object = data.get(FIELD_STATUS)
    if not isinstance(status, str):
        return None
    try:
        return TaskStatus(status)
    except ValueError:
        return None


def _dir_has_content(*, directory: Path) -> bool:
    if directory.is_dir() is False:
        return False
    return any(p for p in directory.iterdir() if p.name != ".gitkeep")


def _session_transcript_files(*, directory: Path) -> list[Path]:
    if directory.is_dir() is False:
        return []
    return sorted(path for path in directory.glob("*.jsonl") if path.is_file() is True)


def _allowed_root_files(*, task_id: TaskID) -> set[str]:
    allowed_files: set[str] = set(ALLOWED_ROOT_FILES)
    data: dict[str, object] | None = load_json_file(
        file_path=task_json_path(task_id=task_id),
    )
    if data is None:
        return allowed_files

    file_name: object = data.get(FIELD_LONG_DESCRIPTION_FILE)
    if isinstance(file_name, str) and is_valid_task_description_file_name(file_name=file_name):
        description_path: Path = task_description_file_path(
            task_id=task_id,
            file_name=file_name,
        )
        if description_path.parent == task_dir(task_id=task_id):
            allowed_files.add(file_name)
    return allowed_files


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_folder_exists(*, task_id: TaskID) -> list[Diagnostic]:
    folder: Path = task_dir(task_id=task_id)
    if not folder.is_dir():
        return [
            Diagnostic(
                code=FD_E001,
                message=f"Task folder does not exist: {folder}",
                file_path=folder,
            ),
        ]
    return []


def _check_root_files(*, task_id: TaskID) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    folder: Path = task_dir(task_id=task_id)

    tj: Path = task_json_path(task_id=task_id)
    if not tj.exists():
        diagnostics.append(
            Diagnostic(
                code=FD_E002,
                message="task.json is missing",
                file_path=folder,
            ),
        )

    st: Path = step_tracker_path(task_id=task_id)
    if not st.exists():
        diagnostics.append(
            Diagnostic(
                code=FD_E003,
                message="step_tracker.json is missing",
                file_path=folder,
            ),
        )

    return diagnostics


def _check_required_dirs(*, task_id: TaskID) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    folder: Path = task_dir(task_id=task_id)

    for dir_name in REQUIRED_TOP_DIRS:
        dir_path: Path = folder / dir_name
        if not dir_path.is_dir():
            diagnostics.append(
                Diagnostic(
                    code=FD_E004,
                    message=f"Required directory is missing: {dir_name}/",
                    file_path=folder,
                ),
            )

    return diagnostics


def _check_log_subdirs(*, task_id: TaskID) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    logs: Path = logs_dir(task_id=task_id)

    if not logs.is_dir():
        return diagnostics

    subdir_paths: dict[str, Path] = {
        "commands": command_logs_dir(task_id=task_id),
        "steps": step_logs_dir(task_id=task_id),
        "searches": search_logs_dir(task_id=task_id),
        "sessions": session_logs_dir(task_id=task_id),
    }

    for name, path in subdir_paths.items():
        if not path.is_dir():
            diagnostics.append(
                Diagnostic(
                    code=FD_E005,
                    message=f"Required log subdirectory is missing: logs/{name}/",
                    file_path=logs,
                ),
            )

    return diagnostics


def _check_completed_files(*, task_id: TaskID) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    folder: Path = task_dir(task_id=task_id)

    checks: list[_CompletedFileCheck] = [
        _CompletedFileCheck(
            file_path=results_summary_path(task_id=task_id),
            code=FD_E006,
            label="results/results_summary.md",
        ),
        _CompletedFileCheck(
            file_path=results_detailed_path(task_id=task_id),
            code=FD_E007,
            label="results/results_detailed.md",
        ),
        _CompletedFileCheck(
            file_path=metrics_path(task_id=task_id),
            code=FD_E008,
            label="results/metrics.json",
        ),
        _CompletedFileCheck(
            file_path=suggestions_path(task_id=task_id),
            code=FD_E009,
            label="results/suggestions.json",
        ),
        _CompletedFileCheck(
            file_path=costs_path(task_id=task_id),
            code=FD_E010,
            label="results/costs.json",
        ),
        _CompletedFileCheck(
            file_path=remote_machines_path(task_id=task_id),
            code=FD_E011,
            label="results/remote_machines_used.json",
        ),
        _CompletedFileCheck(
            file_path=plan_path(task_id=task_id),
            code=FD_E012,
            label="plan/plan.md",
            skip_if_step="planning",
        ),
        _CompletedFileCheck(
            file_path=research_papers_path(task_id=task_id),
            code=FD_E013,
            label="research/research_papers.md",
            skip_if_step="research-papers",
        ),
        _CompletedFileCheck(
            file_path=research_internet_path(task_id=task_id),
            code=FD_E014,
            label="research/research_internet.md",
            skip_if_step="research-internet",
        ),
    ]

    skipped: set[str] = _skipped_step_names(task_id=task_id)

    for check in checks:
        if check.skip_if_step is not None and check.skip_if_step in skipped:
            continue
        if not check.file_path.exists():
            diagnostics.append(
                Diagnostic(
                    code=check.code,
                    message=f"Task is completed but {check.label} is missing",
                    file_path=folder,
                ),
            )

    steps: Path = step_logs_dir(task_id=task_id)
    if steps.is_dir():
        step_folders: list[Path] = [
            p for p in steps.iterdir() if p.is_dir() and not p.name.startswith(".")
        ]
        if len(step_folders) == 0:
            diagnostics.append(
                Diagnostic(
                    code=FD_E015,
                    message="Task is completed but logs/steps/ contains no step folders",
                    file_path=folder,
                ),
            )

    return diagnostics


def _check_root_contents(*, task_id: TaskID) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    folder: Path = task_dir(task_id=task_id)
    allowed_root_files: set[str] = _allowed_root_files(task_id=task_id)

    for entry in folder.iterdir():
        name: str = entry.name
        if name.startswith("."):
            continue
        if entry.is_dir() and name in IGNORED_ROOT_DIRS:
            continue
        if entry.is_file() and name not in allowed_root_files:
            diagnostics.append(
                Diagnostic(
                    code=FD_E016,
                    message=(
                        f"Unexpected file in task folder root: '{name}' "
                        f"(only {', '.join(sorted(allowed_root_files))} allowed)"
                    ),
                    file_path=folder,
                ),
            )
        if entry.is_dir() and name not in ALLOWED_ROOT_DIRS:
            diagnostics.append(
                Diagnostic(
                    code=FD_E016,
                    message=(
                        f"Unexpected directory in task folder root: '{name}/' "
                        f"(only {', '.join(sorted(ALLOWED_ROOT_DIRS))} allowed)"
                    ),
                    file_path=folder,
                ),
            )

    return diagnostics


def _check_warnings(*, task_id: TaskID, status: TaskStatus | None) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    folder: Path = task_dir(task_id=task_id)

    cmds: Path = command_logs_dir(task_id=task_id)
    if cmds.is_dir() and not _dir_has_content(directory=cmds):
        diagnostics.append(
            Diagnostic(
                code=FD_W001,
                message="logs/commands/ is empty (no CLI commands were logged)",
                file_path=folder,
            ),
        )

    searches: Path = search_logs_dir(task_id=task_id)
    if searches.is_dir() and not _dir_has_content(directory=searches):
        diagnostics.append(
            Diagnostic(
                code=FD_W002,
                message="logs/searches/ is empty (no search queries were logged)",
                file_path=folder,
            ),
        )

    images: Path = results_images_dir(task_id=task_id)
    if not images.is_dir():
        diagnostics.append(
            Diagnostic(
                code=FD_W003,
                message="results/images/ directory does not exist (no visualizations)",
                file_path=folder,
            ),
        )

    assets: Path = assets_dir(task_id=task_id)
    if assets.is_dir():
        has_asset_content: bool = False
        for sub in assets.iterdir():
            if sub.is_dir() and _dir_has_content(directory=sub):
                has_asset_content = True
                break
        if not has_asset_content:
            diagnostics.append(
                Diagnostic(
                    code=FD_W004,
                    message="assets/ contains no asset subdirectories with content",
                    file_path=folder,
                ),
            )

    corrections: Path = corrections_dir(task_id=task_id)
    if (
        corrections.is_dir()
        and _dir_has_content(directory=corrections)
        and status is not TaskStatus.COMPLETED
    ):
        diagnostics.append(
            Diagnostic(
                code=FD_W005,
                message="corrections/ contains files but task status is not completed",
                file_path=folder,
            ),
        )

    sessions: Path = session_logs_dir(task_id=task_id)
    if status is TaskStatus.COMPLETED and len(_session_transcript_files(directory=sessions)) == 0:
        diagnostics.append(
            Diagnostic(
                code=FD_W006,
                message=("logs/sessions/ contains no captured session transcript JSONL files"),
                file_path=folder,
            ),
        )

    return diagnostics


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_task_folder(*, task_id: TaskID) -> VerificationResult:
    folder: Path = task_dir(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    # E001: folder existence
    diagnostics.extend(_check_folder_exists(task_id=task_id))
    if not folder.is_dir():
        return VerificationResult(file_path=folder, diagnostics=diagnostics)

    # E002, E003: root files
    diagnostics.extend(_check_root_files(task_id=task_id))

    # E004: required directories
    diagnostics.extend(_check_required_dirs(task_id=task_id))

    # E005: log subdirectories
    diagnostics.extend(_check_log_subdirs(task_id=task_id))

    # E016: unexpected files/dirs in root
    diagnostics.extend(_check_root_contents(task_id=task_id))

    # E006-E015: completed task file requirements
    status: TaskStatus | None = _get_task_status(task_id=task_id)
    if status is TaskStatus.COMPLETED:
        diagnostics.extend(_check_completed_files(task_id=task_id))

    # W001-W005: warnings
    diagnostics.extend(_check_warnings(task_id=task_id, status=status))

    return VerificationResult(file_path=folder, diagnostics=diagnostics)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify task folder structure for a given task (or all tasks)",
    )
    parser.add_argument(
        "task_id",
        nargs="?",
        default=None,
        help="Task ID (e.g. t0003_download_training_corpus)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Verify all tasks in the tasks/ directory",
    )
    args: argparse.Namespace = parser.parse_args()

    if args.all:
        task_dirs: list[TaskID] = sorted(
            d.name for d in TASKS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
        )
        has_errors: bool = False
        for tid in task_dirs:
            result: VerificationResult = verify_task_folder(task_id=tid)
            print_verification_result(result=result)
            if not result.passed:
                has_errors = True
        sys.exit(1 if has_errors else 0)

    if args.task_id is None:
        parser.error("Provide a task_id or use --all")

    result = verify_task_folder(task_id=args.task_id)
    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
