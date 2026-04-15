"""Verificator for overall task completion.

Runs all task-level checks to verify a task was completed correctly:
task.json status, step tracker, logs, assets, git branch, and PR.

Usage:
    uv run python -m arf.scripts.verificators.verify_task_complete <task_id>

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import argparse
import json
import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.constants import (
    ALLOWED_OUTSIDE_FILES,
    ASSET_TYPE_VERIFICATOR_MODULES,
    COMPLETED_TASK_STATUSES,
    FINISHED_STEP_STATUSES,
    MANDATORY_DIRS,
    MANDATORY_RESULT_FILES,
    TASK_BRANCH_PREFIX,
)
from arf.scripts.verificators.common.json_utils import load_json_file
from arf.scripts.verificators.common.paths import (
    REPO_ROOT,
    TASKS_DIR,
    remote_machines_path,
    step_tracker_path,
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

_PREFIX: str = "TC"

FIELD_STATUS: str = "status"
FIELD_START_TIME: str = "start_time"
FIELD_END_TIME: str = "end_time"
FIELD_EXPECTED_ASSETS: str = "expected_assets"
FIELD_STEPS: str = "steps"
FIELD_STEP: str = "step"
FIELD_NAME: str = "name"

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

TC_E001: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=1)
TC_E002: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=2)
TC_E003: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=3)
TC_E004: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=4)
TC_E005: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=5)
TC_E006: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=6)
TC_E007: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=7)
TC_E009: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=9)

TC_W005: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=5)

TC_W001: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=1)
TC_W002: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=2)
TC_W003: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=3)
TC_W004: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=4)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_task_status(
    *,
    task_data: dict[str, Any],
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    status: str = str(task_data.get(FIELD_STATUS, ""))
    if status not in COMPLETED_TASK_STATUSES:
        return [
            Diagnostic(
                code=TC_E001,
                message=(
                    f"task.json status is '{status}', expected one of: "
                    f"{', '.join(sorted(COMPLETED_TASK_STATUSES))}"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_timestamps(
    *,
    task_data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if task_data.get(FIELD_START_TIME) is None:
        diagnostics.append(
            Diagnostic(
                code=TC_E002,
                message="task.json start_time is null",
                file_path=file_path,
            ),
        )
    if task_data.get(FIELD_END_TIME) is None:
        diagnostics.append(
            Diagnostic(
                code=TC_E002,
                message="task.json end_time is null",
                file_path=file_path,
            ),
        )
    return diagnostics


def _check_all_steps_finished(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    tracker_file: Path = step_tracker_path(task_id=task_id)
    if not tracker_file.exists():
        return [
            Diagnostic(
                code=TC_E003,
                message="step_tracker.json does not exist",
                file_path=file_path,
            ),
        ]

    data: dict[str, Any] | None = load_json_file(file_path=tracker_file)
    if data is None:
        return [
            Diagnostic(
                code=TC_E003,
                message="step_tracker.json is not valid JSON",
                file_path=file_path,
            ),
        ]

    steps: object = data.get(FIELD_STEPS)
    if not isinstance(steps, list):
        return [
            Diagnostic(
                code=TC_E003,
                message="step_tracker.json has no steps list",
                file_path=file_path,
            ),
        ]

    diagnostics: list[Diagnostic] = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        step_name: str = str(step.get(FIELD_NAME, "?"))
        step_status: str = str(step.get(FIELD_STATUS, ""))
        if step_status not in FINISHED_STEP_STATUSES:
            diagnostics.append(
                Diagnostic(
                    code=TC_E004,
                    message=f"Step '{step_name}' has status '{step_status}', not finished",
                    file_path=tracker_file,
                ),
            )

    # Check sequential numbering
    step_numbers: list[int] = []
    for step in steps:
        if isinstance(step, dict):
            num: object = step.get(FIELD_STEP)
            if isinstance(num, int):
                step_numbers.append(num)

    expected: list[int] = list(range(1, len(step_numbers) + 1))
    if step_numbers != expected:
        diagnostics.append(
            Diagnostic(
                code=TC_W001,
                message=f"Step numbers are {step_numbers}, expected sequential {expected}",
                file_path=tracker_file,
            ),
        )

    return diagnostics


def _check_mandatory_dirs(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    task_dir: Path = TASKS_DIR / task_id
    diagnostics: list[Diagnostic] = []
    for dir_name in MANDATORY_DIRS:
        dir_path: Path = task_dir / dir_name
        if not dir_path.is_dir():
            diagnostics.append(
                Diagnostic(
                    code=TC_E005,
                    message=f"Mandatory directory missing: {dir_name}/",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_mandatory_result_files(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    task_dir: Path = TASKS_DIR / task_id
    diagnostics: list[Diagnostic] = []
    for rel_path in MANDATORY_RESULT_FILES:
        full_path: Path = task_dir / rel_path
        if not full_path.exists():
            diagnostics.append(
                Diagnostic(
                    code=TC_E006,
                    message=f"Mandatory result file missing: {rel_path}",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_assets_exist(
    *,
    task_data: dict[str, Any],
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    expected: object = task_data.get(FIELD_EXPECTED_ASSETS)
    if not isinstance(expected, dict):
        return []

    task_dir: Path = TASKS_DIR / task_id
    diagnostics: list[Diagnostic] = []

    for asset_type, count in expected.items():
        asset_type_str: str = str(asset_type)
        asset_dir: Path = task_dir / "assets" / asset_type_str
        if not asset_dir.is_dir():
            diagnostics.append(
                Diagnostic(
                    code=TC_E007,
                    message=f"Expected asset directory missing: assets/{asset_type_str}/",
                    file_path=file_path,
                ),
            )
            continue

        # Count asset subdirectories (each asset is a subfolder)
        asset_folders: list[Path] = [
            d for d in asset_dir.iterdir() if d.is_dir() and d.name != ".gitkeep"
        ]
        if isinstance(count, int) and len(asset_folders) < count:
            diagnostics.append(
                Diagnostic(
                    code=TC_W002,
                    message=(
                        f"Expected {count} {asset_type_str} asset(s), found {len(asset_folders)}"
                    ),
                    file_path=file_path,
                ),
            )

    return diagnostics


def _check_git_branch_exists(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    branch_name: str = TASK_BRANCH_PREFIX + task_id
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["git", "branch", "--list", branch_name],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        local_exists: bool = len(result.stdout.strip()) > 0
    except OSError:
        return []

    if not local_exists:
        # Check remote
        try:
            result = subprocess.run(
                ["git", "branch", "-r", "--list", f"origin/{branch_name}"],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
            )
            remote_exists: bool = len(result.stdout.strip()) > 0
        except OSError:
            return []

        if not remote_exists:
            return [
                Diagnostic(
                    code=TC_W003,
                    message=f"Task branch '{branch_name}' not found locally or on remote",
                    file_path=file_path,
                ),
            ]

    return []


def _check_pr_merged(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    branch_name: str = TASK_BRANCH_PREFIX + task_id
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--head",
                branch_name,
                "--state",
                "merged",
                "--json",
                "number,title",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            return []

        prs: object = json.loads(result.stdout)
        if isinstance(prs, list) and len(prs) == 0:
            return [
                Diagnostic(
                    code=TC_W005,
                    message=f"No merged PR found for branch '{branch_name}'",
                    file_path=file_path,
                ),
            ]
    except (OSError, json.JSONDecodeError):
        return []

    return []


def _check_no_files_outside_task(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    """Check that the task branch only modified files in the task folder."""
    branch_name: str = TASK_BRANCH_PREFIX + task_id
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["git", "log", f"main..origin/{branch_name}", "--name-only", "--format="],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            return []
    except OSError:
        return []

    task_prefix: str = f"tasks/{task_id}/"

    diagnostics: list[Diagnostic] = []
    violating_files: list[str] = []

    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if len(line) == 0:
            continue
        is_allowed: bool = line.startswith(task_prefix) or any(
            line == allowed or line.startswith(allowed) for allowed in ALLOWED_OUTSIDE_FILES
        )
        if not is_allowed:
            violating_files.append(line)

    if len(violating_files) > 0:
        diagnostics.append(
            Diagnostic(
                code=TC_E009,
                message=(
                    f"Task branch modified {len(violating_files)} file(s) outside "
                    f"the task folder: {', '.join(violating_files[:5])}"
                    + (" ..." if len(violating_files) > 5 else "")
                ),
                file_path=file_path,
            ),
        )

    return diagnostics


def _run_sub_verificator(
    *,
    module_name: str,
    args: list[str],
    label: str,
    file_path: Path,
) -> list[Diagnostic]:
    """Run a sub-verificator script and report if it fails."""
    if find_spec(module_name) is None:
        return [
            Diagnostic(
                code=TC_W004,
                message=f"Sub-verificator not found: {module_name}",
                file_path=file_path,
            ),
        ]

    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["uv", "run", "python", "-m", module_name] + args,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            # Extract error summary from output
            error_lines: list[str] = [
                line
                for line in result.stdout.split("\n")
                if "error:" in line.lower() or "FAILED" in line
            ]
            detail: str = "; ".join(error_lines[:3]) if len(error_lines) > 0 else ""
            return [
                Diagnostic(
                    code=TC_E007,
                    message=f"Sub-verificator failed: {label}",
                    file_path=file_path,
                    detail=detail if len(detail) > 0 else None,
                ),
            ]
    except OSError:
        pass

    return []


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_task_complete(*, task_id: str) -> VerificationResult:
    file_path: Path = task_json_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    # Load task.json
    task_data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if task_data is None:
        diagnostics.append(
            Diagnostic(
                code=TC_E001,
                message="task.json does not exist or is not valid JSON",
                file_path=file_path,
            ),
        )
        return VerificationResult(file_path=file_path, diagnostics=diagnostics)

    # E001: task status
    diagnostics.extend(
        _check_task_status(
            task_data=task_data,
            task_id=task_id,
            file_path=file_path,
        ),
    )

    # E002: timestamps
    diagnostics.extend(_check_timestamps(task_data=task_data, file_path=file_path))

    # E003, E004, W001: step tracker
    diagnostics.extend(_check_all_steps_finished(task_id=task_id, file_path=file_path))

    # E005: mandatory directories
    diagnostics.extend(_check_mandatory_dirs(task_id=task_id, file_path=file_path))

    # E006: mandatory result files
    diagnostics.extend(
        _check_mandatory_result_files(task_id=task_id, file_path=file_path),
    )

    # E007, W002: expected assets
    diagnostics.extend(
        _check_assets_exist(
            task_data=task_data,
            task_id=task_id,
            file_path=file_path,
        ),
    )

    # W003: git branch
    diagnostics.extend(_check_git_branch_exists(task_id=task_id, file_path=file_path))

    # E008: PR merged
    diagnostics.extend(_check_pr_merged(task_id=task_id, file_path=file_path))

    # E009: file isolation
    diagnostics.extend(
        _check_no_files_outside_task(task_id=task_id, file_path=file_path),
    )

    # Run sub-verificators
    diagnostics.extend(
        _run_sub_verificator(
            module_name="arf.scripts.verificators.verify_task_file",
            args=[task_id],
            label="verify_task_file",
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _run_sub_verificator(
            module_name="arf.scripts.verificators.verify_task_dependencies",
            args=[task_id],
            label="verify_task_dependencies",
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _run_sub_verificator(
            module_name="arf.scripts.verificators.verify_logs",
            args=[task_id],
            label="verify_logs",
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _run_sub_verificator(
            module_name="arf.scripts.verificators.verify_suggestions",
            args=[task_id],
            label="verify_suggestions",
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _run_sub_verificator(
            module_name="arf.scripts.verificators.verify_task_metrics",
            args=[task_id],
            label="verify_task_metrics",
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _run_sub_verificator(
            module_name="arf.scripts.verificators.verify_task_results",
            args=[task_id],
            label="verify_task_results",
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _run_sub_verificator(
            module_name="arf.scripts.verificators.verify_task_folder",
            args=[task_id],
            label="verify_task_folder",
            file_path=file_path,
        ),
    )

    # Run machine destruction verificator if remote machines were used
    rm_file: Path = remote_machines_path(task_id=task_id)
    if rm_file.exists():
        try:
            rm_raw: Any = json.loads(rm_file.read_text(encoding="utf-8"))
            if isinstance(rm_raw, list) and len(rm_raw) > 0:
                diagnostics.extend(
                    _run_sub_verificator(
                        module_name="arf.scripts.verificators.verify_machines_destroyed",
                        args=[task_id],
                        label="verify_machines_destroyed",
                        file_path=file_path,
                    ),
                )
        except (json.JSONDecodeError, OSError):
            pass

    # Run asset verificators for each asset type present
    task_dir: Path = TASKS_DIR / task_id / "assets"
    if task_dir.is_dir():
        for asset_type_dir in sorted(task_dir.iterdir()):
            if not asset_type_dir.is_dir():
                continue
            asset_type: str = asset_type_dir.name
            verificator_module: str | None = ASSET_TYPE_VERIFICATOR_MODULES.get(asset_type)
            if verificator_module is None:
                continue
            for asset_dir in sorted(asset_type_dir.iterdir()):
                if not asset_dir.is_dir() or asset_dir.name.startswith("."):
                    continue
                diagnostics.extend(
                    _run_sub_verificator(
                        module_name=verificator_module,
                        args=["--task-id", task_id, asset_dir.name],
                        label=f"verify_{asset_type}_asset {asset_dir.name}",
                        file_path=file_path,
                    ),
                )

    return VerificationResult(file_path=file_path, diagnostics=diagnostics)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify that a task was completed correctly",
    )
    parser.add_argument(
        "task_id",
        help="Task ID (e.g. t0003_download_training_corpus)",
    )
    args: argparse.Namespace = parser.parse_args()

    result: VerificationResult = verify_task_complete(task_id=args.task_id)
    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
