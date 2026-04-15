"""Pre-merge PR verificator.

Usage:
    uv run python -m arf.scripts.verificators.verify_pr_premerge <task_id> [--pr-number <N>]
        [--timeout <seconds>] [--quick]

If --pr-number is omitted, discovers the open PR for the task branch.

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import argparse
import fnmatch
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.constants import (
    ASSET_TYPE_VERIFICATOR_MODULES,
    COMPLETED_TASK_STATUSES,
    FINISHED_STEP_STATUSES,
    MANDATORY_DIRS,
    MANDATORY_RESULT_FILES,
    TASK_BRANCH_PREFIX,
)
from arf.scripts.verificators.common.git_utils import (
    GIT_CMD,
    find_violating_files,
    get_changed_files,
    get_commit_subjects,
    get_current_branch,
    get_file_size_in_head,
)
from arf.scripts.verificators.common.json_utils import load_json_file
from arf.scripts.verificators.common.paths import (
    REPO_ROOT,
    TASKS_DIR,
    step_tracker_path,
    task_json_path,
)
from arf.scripts.verificators.common.pr_utils import (
    find_open_pr,
    get_pr_json,
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

_PREFIX: str = "PM"

MAIN_BRANCH: str = "main"
CODE_DIR_NAME: str = "code"
LFS_FILTER_MARKER: str = "filter=lfs"
MERGE_STATE_CONFLICTING: str = "CONFLICTING"
MAX_SUBJECT_LENGTH: int = 100
LARGE_FILE_THRESHOLD_BYTES: int = 5 * 1024 * 1024  # 5 MB
DEFAULT_TIMEOUT_SECONDS: float = 300.0
MAX_DISPLAY_FILES: int = 5

FIELD_STATUS: str = "status"
FIELD_START_TIME: str = "start_time"
FIELD_END_TIME: str = "end_time"
FIELD_EXPECTED_ASSETS: str = "expected_assets"
FIELD_STEPS: str = "steps"
FIELD_NAME: str = "name"
FIELD_STEP_ID: str = "step_id"
FIELD_BASE_REF_NAME: str = "baseRefName"
FIELD_BODY: str = "body"
FIELD_TITLE: str = "title"
FIELD_MERGEABLE: str = "mergeable"

STATUS_COMPLETED: str = "completed"

ERROR_MARKER: str = "error:"
FAILED_MARKER: str = "FAILED"

SENSITIVE_FILE_PATTERNS: list[str] = [
    "*.env",
    ".env.*",
    "*.pem",
    "*private*.key",
    "*_key.pem",
    "id_*.key",
    "*.p12",
    "*credential*",
    "*secret*",
    "*password*",
]

SENSITIVE_CONTENT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"API_KEY\s*=\s*\S+"),
    re.compile(r"SECRET_KEY\s*=\s*\S+"),
    re.compile(r"aws_secret_access_key\s*=\s*\S+"),
    re.compile(r"-----BEGIN.*PRIVATE KEY-----"),
    re.compile(r"ANTHROPIC_API_KEY\s*=\s*\S+"),
    re.compile(r"OPENAI_API_KEY\s*=\s*\S+"),
]

REQUIRED_PR_SECTIONS: list[str] = [
    "## Summary",
    "## Assets Produced",
    "## Verification",
]

COMMIT_STEP_PATTERN: re.Pattern[str] = re.compile(r"\[(\w[\w-]*)\]")


@dataclass(frozen=True, slots=True)
class SubVerificatorCall:
    module_name: str
    args: list[str]
    label: str


# ---------------------------------------------------------------------------
# Diagnostic codes — Errors
# ---------------------------------------------------------------------------

PM_E001: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=1)
PM_E002: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=2)
PM_E003: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=3)
PM_E004: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=4)
PM_E005: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=5)
PM_E006: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=6)
PM_E007: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=7)
PM_E008: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=8)
PM_E009: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=9)
PM_E010: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=10)
PM_E011: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=11)
PM_E012: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=12)
PM_E013: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=13)
PM_E014: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.ERROR, number=14)

# ---------------------------------------------------------------------------
# Diagnostic codes — Warnings
# ---------------------------------------------------------------------------

PM_W001: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=1)
PM_W002: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=2)
PM_W003: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=3)
PM_W004: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=4)
PM_W005: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=5)
PM_W006: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=6)
PM_W007: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=7)
PM_W008: DiagnosticCode = DiagnosticCode(prefix=_PREFIX, severity=Severity.WARNING, number=8)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_branch_name(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    branch: str | None = get_current_branch(repo_root=REPO_ROOT)
    if branch is None:
        return []
    expected: str = TASK_BRANCH_PREFIX + task_id
    if branch != expected:
        return [
            Diagnostic(
                code=PM_E001,
                message=f"Branch is '{branch}', expected '{expected}'",
                file_path=file_path,
            ),
        ]
    return []


def _check_pr_target(
    *,
    pr_number: int,
    file_path: Path,
) -> list[Diagnostic]:
    data: dict[str, Any] | None = get_pr_json(
        repo_root=REPO_ROOT,
        pr_number=pr_number,
        fields=FIELD_BASE_REF_NAME,
    )
    if data is None:
        return []
    base: object = data.get(FIELD_BASE_REF_NAME)
    if isinstance(base, str) and base != MAIN_BRANCH:
        return [
            Diagnostic(
                code=PM_E002,
                message=f"PR targets '{base}', expected '{MAIN_BRANCH}'",
                file_path=file_path,
            ),
        ]
    return []


def _get_changed_files_for_task(*, task_id: str) -> list[str] | None:
    branch_name: str = TASK_BRANCH_PREFIX + task_id
    changed: list[str] | None = get_changed_files(
        repo_root=REPO_ROOT,
        base=MAIN_BRANCH,
        head=f"origin/{branch_name}",
    )
    if changed is None:
        changed = get_changed_files(
            repo_root=REPO_ROOT,
            base=MAIN_BRANCH,
            head="HEAD",
        )
    return changed


def _check_file_isolation(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    changed: list[str] | None = _get_changed_files_for_task(task_id=task_id)
    if changed is None:
        return []

    violations: list[str] = find_violating_files(
        changed_files=changed,
        task_id=task_id,
    )
    if len(violations) > 0:
        display: str = ", ".join(violations[:MAX_DISPLAY_FILES])
        suffix: str = " ..." if len(violations) > MAX_DISPLAY_FILES else ""
        return [
            Diagnostic(
                code=PM_E003,
                message=(
                    f"Branch modified {len(violations)} file(s) outside the task "
                    f"folder: {display}{suffix}"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_has_commits(
    *,
    file_path: Path,
) -> list[Diagnostic]:
    subjects: list[str] | None = get_commit_subjects(
        repo_root=REPO_ROOT,
        base=MAIN_BRANCH,
        head="HEAD",
    )
    if subjects is not None and len(subjects) == 0:
        return [
            Diagnostic(
                code=PM_E004,
                message=f"No commits found on this branch compared to {MAIN_BRANCH}",
                file_path=file_path,
            ),
        ]
    return []


def _check_task_status(
    *,
    task_data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    status: str = str(task_data.get(FIELD_STATUS, ""))
    if status not in COMPLETED_TASK_STATUSES:
        return [
            Diagnostic(
                code=PM_E005,
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
                code=PM_E006,
                message="task.json start_time is null",
                file_path=file_path,
            ),
        )
    if task_data.get(FIELD_END_TIME) is None:
        diagnostics.append(
            Diagnostic(
                code=PM_E006,
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
                code=PM_E007,
                message="step_tracker.json does not exist",
                file_path=file_path,
            ),
        ]

    data: dict[str, Any] | None = load_json_file(file_path=tracker_file)
    if data is None:
        return [
            Diagnostic(
                code=PM_E007,
                message="step_tracker.json is not valid JSON",
                file_path=file_path,
            ),
        ]

    steps: object = data.get(FIELD_STEPS)
    if not isinstance(steps, list):
        return [
            Diagnostic(
                code=PM_E007,
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
                    code=PM_E007,
                    message=(f"Step '{step_name}' has status '{step_status}', not finished"),
                    file_path=tracker_file,
                ),
            )
    return diagnostics


def _check_mandatory_dirs(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    task_folder: Path = TASKS_DIR / task_id
    diagnostics: list[Diagnostic] = []
    for dir_name in MANDATORY_DIRS:
        dir_path: Path = task_folder / dir_name
        if not dir_path.is_dir():
            diagnostics.append(
                Diagnostic(
                    code=PM_E008,
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
    task_folder: Path = TASKS_DIR / task_id
    diagnostics: list[Diagnostic] = []
    for rel_path in MANDATORY_RESULT_FILES:
        full_path: Path = task_folder / rel_path
        if not full_path.exists():
            diagnostics.append(
                Diagnostic(
                    code=PM_E009,
                    message=f"Mandatory result file missing: {rel_path}",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_sensitive_files(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    changed: list[str] | None = _get_changed_files_for_task(task_id=task_id)
    if changed is None:
        return []

    diagnostics: list[Diagnostic] = []
    sensitive_found: list[str] = []

    for changed_file in changed:
        filename: str = changed_file.rsplit("/", maxsplit=1)[-1]
        for pattern in SENSITIVE_FILE_PATTERNS:
            if fnmatch.fnmatch(filename.lower(), pattern):
                sensitive_found.append(changed_file)
                break

    if len(sensitive_found) > 0:
        display: str = ", ".join(sensitive_found[:MAX_DISPLAY_FILES])
        suffix: str = " ..." if len(sensitive_found) > MAX_DISPLAY_FILES else ""
        diagnostics.append(
            Diagnostic(
                code=PM_E010,
                message=f"Sensitive file(s) detected: {display}{suffix}",
                file_path=file_path,
            ),
        )

    # Check diff content for secret patterns
    task_folder: Path = TASKS_DIR / task_id
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [
                GIT_CMD,
                "diff",
                f"{MAIN_BRANCH}...HEAD",
                "--",
                str(task_folder),
                ":(exclude)*/logs/sessions/*",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode == 0:
            added_lines: str = "\n".join(
                line
                for line in result.stdout.splitlines()
                if line.startswith("+") and not line.startswith("+++")
            )
            for secret_re in SENSITIVE_CONTENT_PATTERNS:
                if secret_re.search(added_lines) is not None:
                    diagnostics.append(
                        Diagnostic(
                            code=PM_E010,
                            message=(
                                f"Possible secret in diff matching pattern: {secret_re.pattern}"
                            ),
                            file_path=file_path,
                        ),
                    )
                    break
    except OSError:
        pass

    return diagnostics


def _load_lfs_patterns() -> list[str]:
    gitattributes: Path = REPO_ROOT / ".gitattributes"
    if not gitattributes.exists():
        return []
    patterns: list[str] = []
    try:
        for line in gitattributes.read_text(encoding="utf-8").splitlines():
            if LFS_FILTER_MARKER in line:
                parts: list[str] = line.split()
                if len(parts) > 0:
                    patterns.append(parts[0])
    except OSError:
        pass
    return patterns


def _check_large_files(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    changed: list[str] | None = _get_changed_files_for_task(task_id=task_id)
    if changed is None:
        return []

    lfs_patterns: list[str] = _load_lfs_patterns()
    diagnostics: list[Diagnostic] = []

    for changed_file in changed:
        filename: str = changed_file.rsplit("/", maxsplit=1)[-1]
        is_lfs: bool = any(
            fnmatch.fnmatch(filename, pat) or fnmatch.fnmatch(changed_file, pat)
            for pat in lfs_patterns
        )
        if is_lfs:
            continue

        size: int | None = get_file_size_in_head(
            repo_root=REPO_ROOT,
            file_path=changed_file,
            head="HEAD",
        )
        if size is not None and size > LARGE_FILE_THRESHOLD_BYTES:
            size_mb: float = size / (1024 * 1024)
            diagnostics.append(
                Diagnostic(
                    code=PM_E011,
                    message=(f"Large file ({size_mb:.1f} MB) not tracked by LFS: {changed_file}"),
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
    if find_spec(module_name) is None:
        return []

    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["uv", "run", "python", "-m", module_name] + args,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            error_lines: list[str] = [
                line
                for line in result.stdout.split("\n")
                if ERROR_MARKER in line.lower() or FAILED_MARKER in line
            ]
            detail: str = "; ".join(error_lines[:3]) if len(error_lines) > 0 else ""
            return [
                Diagnostic(
                    code=PM_E012,
                    message=f"Sub-verificator failed: {label}",
                    file_path=file_path,
                    detail=detail if len(detail) > 0 else None,
                ),
            ]
    except OSError:
        pass

    return []


def _check_pr_body_sections(
    *,
    pr_number: int,
    file_path: Path,
) -> list[Diagnostic]:
    data: dict[str, Any] | None = get_pr_json(
        repo_root=REPO_ROOT,
        pr_number=pr_number,
        fields=FIELD_BODY,
    )
    if data is None:
        return []

    body: str = str(data.get(FIELD_BODY, ""))
    diagnostics: list[Diagnostic] = []

    for section in REQUIRED_PR_SECTIONS:
        if section not in body:
            diagnostics.append(
                Diagnostic(
                    code=PM_E013,
                    message=f"PR body missing required section: '{section}'",
                    file_path=file_path,
                ),
            )

    return diagnostics


def _check_merge_conflicts(
    *,
    pr_number: int,
    file_path: Path,
) -> list[Diagnostic]:
    data: dict[str, Any] | None = get_pr_json(
        repo_root=REPO_ROOT,
        pr_number=pr_number,
        fields=FIELD_MERGEABLE,
    )
    if data is None:
        return []

    mergeable: object = data.get(FIELD_MERGEABLE)
    if mergeable == MERGE_STATE_CONFLICTING:
        return [
            Diagnostic(
                code=PM_E014,
                message="PR has merge conflicts — resolve before merging",
                file_path=file_path,
            ),
        ]
    return []


# ---------------------------------------------------------------------------
# Warning checks
# ---------------------------------------------------------------------------


def _check_commit_messages(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    subjects: list[str] | None = get_commit_subjects(
        repo_root=REPO_ROOT,
        base=MAIN_BRANCH,
        head="HEAD",
    )
    if subjects is None:
        return []

    diagnostics: list[Diagnostic] = []
    for subject in subjects:
        if task_id not in subject:
            diagnostics.append(
                Diagnostic(
                    code=PM_W001,
                    message=f"Commit missing task ID: '{subject}'",
                    file_path=file_path,
                ),
            )
        elif COMMIT_STEP_PATTERN.search(subject) is None:
            diagnostics.append(
                Diagnostic(
                    code=PM_W001,
                    message=f"Commit missing step ID in brackets: '{subject}'",
                    file_path=file_path,
                ),
            )

        if len(subject) > MAX_SUBJECT_LENGTH:
            diagnostics.append(
                Diagnostic(
                    code=PM_W002,
                    message=(
                        f"Commit subject exceeds {MAX_SUBJECT_LENGTH} chars "
                        f"({len(subject)}): '{subject[:50]}...'"
                    ),
                    file_path=file_path,
                ),
            )

    return diagnostics


def _check_pr_title(
    *,
    task_id: str,
    pr_number: int,
    file_path: Path,
) -> list[Diagnostic]:
    data: dict[str, Any] | None = get_pr_json(
        repo_root=REPO_ROOT,
        pr_number=pr_number,
        fields=FIELD_TITLE,
    )
    if data is None:
        return []

    title: str = str(data.get(FIELD_TITLE, ""))
    diagnostics: list[Diagnostic] = []

    short_id: str = task_id.split("_", maxsplit=1)[0]
    if not title.startswith(f"{task_id}:") and not title.startswith(f"{short_id}:"):
        diagnostics.append(
            Diagnostic(
                code=PM_W003,
                message=(f"PR title does not start with '{task_id}:' or '{short_id}:': '{title}'"),
                file_path=file_path,
            ),
        )

    return diagnostics


def _check_step_commit_mapping(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    tracker_file: Path = step_tracker_path(task_id=task_id)
    data: dict[str, Any] | None = load_json_file(file_path=tracker_file)
    if data is None:
        return []

    steps: object = data.get(FIELD_STEPS)
    if not isinstance(steps, list):
        return []

    subjects: list[str] | None = get_commit_subjects(
        repo_root=REPO_ROOT,
        base=MAIN_BRANCH,
        head="HEAD",
    )
    if subjects is None:
        return []

    commit_text: str = " ".join(subjects)
    diagnostics: list[Diagnostic] = []

    for step in steps:
        if not isinstance(step, dict):
            continue
        step_status: str = str(step.get(FIELD_STATUS, ""))
        if step_status != STATUS_COMPLETED:
            continue
        step_id: str = str(step.get(FIELD_STEP_ID, step.get(FIELD_NAME, "?")))
        if step_id not in commit_text:
            diagnostics.append(
                Diagnostic(
                    code=PM_W004,
                    message=f"Completed step '{step_id}' has no associated commit",
                    file_path=tracker_file,
                ),
            )

    return diagnostics


def _check_expected_assets(
    *,
    task_data: dict[str, Any],
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    expected: object = task_data.get(FIELD_EXPECTED_ASSETS)
    if not isinstance(expected, dict):
        return []

    task_folder: Path = TASKS_DIR / task_id
    diagnostics: list[Diagnostic] = []

    for asset_kind, count in expected.items():
        asset_kind_str: str = str(asset_kind)
        asset_dir: Path = task_folder / "assets" / asset_kind_str
        if not asset_dir.is_dir() and asset_kind_str.endswith("s"):
            asset_dir = task_folder / "assets" / asset_kind_str[:-1]
        if not asset_dir.is_dir():
            continue

        asset_folders: list[Path] = [
            d for d in asset_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
        ]
        if isinstance(count, int) and len(asset_folders) < count:
            diagnostics.append(
                Diagnostic(
                    code=PM_W005,
                    message=(
                        f"Expected {count} {asset_kind_str} asset(s), found {len(asset_folders)}"
                    ),
                    file_path=file_path,
                ),
            )

    return diagnostics


def _check_ruff(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    task_folder: Path = TASKS_DIR / task_id
    code_dir: Path = task_folder / CODE_DIR_NAME
    if not code_dir.is_dir():
        return []

    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["uv", "run", "ruff", "check", str(code_dir)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            issue_count: int = len(
                [line for line in result.stdout.strip().split("\n") if len(line.strip()) > 0]
            )
            return [
                Diagnostic(
                    code=PM_W006,
                    message=f"ruff check reported {issue_count} issue(s) in task code",
                    file_path=file_path,
                    detail=result.stdout[:200] if len(result.stdout) > 0 else None,
                ),
            ]
    except OSError:
        pass
    return []


def _check_mypy(
    *,
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    task_folder: Path = TASKS_DIR / task_id
    code_dir: Path = task_folder / CODE_DIR_NAME
    if not code_dir.is_dir():
        return []

    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["uv", "run", "mypy", str(code_dir)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            error_lines: list[str] = [
                line for line in result.stdout.strip().split("\n") if ERROR_MARKER in line.lower()
            ]
            if len(error_lines) > 0:
                return [
                    Diagnostic(
                        code=PM_W007,
                        message=(f"mypy reported {len(error_lines)} error(s) in task code"),
                        file_path=file_path,
                        detail="\n".join(error_lines[:3]),
                    ),
                ]
    except OSError:
        pass
    return []


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_pr_premerge(
    *,
    task_id: str,
    pr_number: int | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    quick: bool = False,
) -> VerificationResult:
    file_path: Path = task_json_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    # Resolve PR number if not provided
    resolved_pr: int | None = pr_number
    if resolved_pr is None:
        branch_name: str = TASK_BRANCH_PREFIX + task_id
        resolved_pr = find_open_pr(repo_root=REPO_ROOT, branch=branch_name)
        if resolved_pr is None:
            diagnostics.append(
                Diagnostic(
                    code=PM_E002,
                    message=(
                        f"No open PR found for branch '{branch_name}'. "
                        "Use --pr-number to specify explicitly."
                    ),
                    file_path=file_path,
                ),
            )
            return VerificationResult(
                file_path=file_path,
                diagnostics=diagnostics,
            )

    # E001: Branch naming
    diagnostics.extend(_check_branch_name(task_id=task_id, file_path=file_path))

    # E002: PR targets main
    diagnostics.extend(_check_pr_target(pr_number=resolved_pr, file_path=file_path))

    # E003: File isolation
    diagnostics.extend(_check_file_isolation(task_id=task_id, file_path=file_path))

    # E004: Has commits
    diagnostics.extend(_check_has_commits(file_path=file_path))

    # Load task.json for state checks
    task_data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if task_data is None:
        diagnostics.append(
            Diagnostic(
                code=PM_E005,
                message="task.json does not exist or is not valid JSON",
                file_path=file_path,
            ),
        )
    else:
        # E005: Task status
        diagnostics.extend(
            _check_task_status(task_data=task_data, file_path=file_path),
        )
        # E006: Timestamps
        diagnostics.extend(
            _check_timestamps(task_data=task_data, file_path=file_path),
        )
        # W005: Expected assets
        diagnostics.extend(
            _check_expected_assets(
                task_data=task_data,
                task_id=task_id,
                file_path=file_path,
            ),
        )

    # E007: Step tracker
    diagnostics.extend(
        _check_all_steps_finished(task_id=task_id, file_path=file_path),
    )

    # E008: Mandatory dirs
    diagnostics.extend(
        _check_mandatory_dirs(task_id=task_id, file_path=file_path),
    )

    # E009: Mandatory result files
    diagnostics.extend(
        _check_mandatory_result_files(task_id=task_id, file_path=file_path),
    )

    # E010: Sensitive files
    diagnostics.extend(
        _check_sensitive_files(task_id=task_id, file_path=file_path),
    )

    # E011: Large files
    diagnostics.extend(
        _check_large_files(task_id=task_id, file_path=file_path),
    )

    # E012: Sub-verificators
    sub_verificator_start: float = time.monotonic()
    timed_out: bool = False

    sub_verificator_calls: list[SubVerificatorCall] = [
        SubVerificatorCall(
            module_name="arf.scripts.verificators.verify_task_file",
            args=[task_id],
            label="verify_task_file",
        ),
        SubVerificatorCall(
            module_name="arf.scripts.verificators.verify_task_dependencies",
            args=[task_id],
            label="verify_task_dependencies",
        ),
        SubVerificatorCall(
            module_name="arf.scripts.verificators.verify_suggestions",
            args=[task_id],
            label="verify_suggestions",
        ),
        SubVerificatorCall(
            module_name="arf.scripts.verificators.verify_task_metrics",
            args=[task_id],
            label="verify_task_metrics",
        ),
        SubVerificatorCall(
            module_name="arf.scripts.verificators.verify_task_results",
            args=[task_id],
            label="verify_task_results",
        ),
        SubVerificatorCall(
            module_name="arf.scripts.verificators.verify_task_folder",
            args=[task_id],
            label="verify_task_folder",
        ),
        SubVerificatorCall(
            module_name="arf.scripts.verificators.verify_logs",
            args=[task_id],
            label="verify_logs",
        ),
    ]

    for call in sub_verificator_calls:
        elapsed: float = time.monotonic() - sub_verificator_start
        if elapsed > timeout:
            diagnostics.append(
                Diagnostic(
                    code=PM_W008,
                    message=(
                        f"Sub-verificator timeout ({timeout:.0f}s) exceeded "
                        f"after {elapsed:.0f}s; skipping remaining checks"
                    ),
                    file_path=file_path,
                ),
            )
            timed_out = True
            break
        diagnostics.extend(
            _run_sub_verificator(
                module_name=call.module_name,
                args=call.args,
                label=call.label,
                file_path=file_path,
            ),
        )

    # Run asset verificators for each asset type present
    if quick is not True and timed_out is not True:
        assets_path: Path = TASKS_DIR / task_id / "assets"
        if assets_path.is_dir():
            for asset_kind_dir in sorted(assets_path.iterdir()):
                if not asset_kind_dir.is_dir():
                    continue
                asset_kind: str = asset_kind_dir.name
                verificator_module: str | None = ASSET_TYPE_VERIFICATOR_MODULES.get(asset_kind)
                if verificator_module is None:
                    continue
                for asset_dir in sorted(asset_kind_dir.iterdir()):
                    if not asset_dir.is_dir() or asset_dir.name.startswith("."):
                        continue
                    elapsed = time.monotonic() - sub_verificator_start
                    if elapsed > timeout:
                        diagnostics.append(
                            Diagnostic(
                                code=PM_W008,
                                message=(
                                    f"Sub-verificator timeout "
                                    f"({timeout:.0f}s) exceeded after "
                                    f"{elapsed:.0f}s; skipping remaining "
                                    "asset checks"
                                ),
                                file_path=file_path,
                            ),
                        )
                        timed_out = True
                        break
                    diagnostics.extend(
                        _run_sub_verificator(
                            module_name=verificator_module,
                            args=[
                                "--task-id",
                                task_id,
                                asset_dir.name,
                            ],
                            label=(f"verify_{asset_kind}_asset {asset_dir.name}"),
                            file_path=file_path,
                        ),
                    )
                if timed_out is True:
                    break

    # E013: PR body sections
    diagnostics.extend(
        _check_pr_body_sections(pr_number=resolved_pr, file_path=file_path),
    )

    # E014: Merge conflicts
    diagnostics.extend(
        _check_merge_conflicts(pr_number=resolved_pr, file_path=file_path),
    )

    # W001, W002: Commit messages
    diagnostics.extend(
        _check_commit_messages(task_id=task_id, file_path=file_path),
    )

    # W003: PR title
    diagnostics.extend(
        _check_pr_title(
            task_id=task_id,
            pr_number=resolved_pr,
            file_path=file_path,
        ),
    )

    # W004: Step-commit mapping
    diagnostics.extend(
        _check_step_commit_mapping(task_id=task_id, file_path=file_path),
    )

    # W006: Ruff
    diagnostics.extend(_check_ruff(task_id=task_id, file_path=file_path))

    # W007: Mypy
    diagnostics.extend(_check_mypy(task_id=task_id, file_path=file_path))

    return VerificationResult(file_path=file_path, diagnostics=diagnostics)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Pre-merge PR verificator — run between PR creation and merge",
    )
    parser.add_argument(
        "task_id",
        help="Task ID (e.g. t0003_download_training_corpus)",
    )
    parser.add_argument(
        "--pr-number",
        type=int,
        default=None,
        help="PR number (auto-discovered if omitted)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Maximum seconds for sub-verificator execution (default: 300)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        default=False,
        help="Skip asset-level sub-verificators, run structural checks only",
    )
    args: argparse.Namespace = parser.parse_args()

    result: VerificationResult = verify_pr_premerge(
        task_id=args.task_id,
        pr_number=args.pr_number,
        timeout=args.timeout,
        quick=args.quick,
    )
    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
