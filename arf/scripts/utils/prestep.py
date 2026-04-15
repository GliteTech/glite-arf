"""Pre-step script: validate preconditions, mark step in_progress, create log folder.

Run this before starting work on any step. It checks that all prerequisites
are met, then sets up the step for execution.

Usage:
    uv run python -m arf.scripts.utils.prestep <task_id> <step_id>

What it does:
    1. Loads step_tracker.json and finds the step.
    2. Checks previous steps are completed.
    3. Checks we are on the correct branch (task/<task_id>).
    4. Checks working tree is clean (prior step committed).
    5. Checks step folder does not already exist.
    6. For step 1 (check-deps): runs dependency verification.
    7. Creates the step log folder.
    8. Marks the step as in_progress with started_at timestamp.

Exit codes:
    0 — preconditions met, step is now in_progress
    1 — preconditions failed
"""

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.paths import (
    TASKS_DIR,
    step_folder_path,
    step_tracker_path,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FIELD_STEPS: str = "steps"
FIELD_STEP: str = "step"
FIELD_NAME: str = "name"
FIELD_STATUS: str = "status"
FIELD_STARTED_AT: str = "started_at"
FIELD_LOG_FILE: str = "log_file"

STATUS_PENDING: str = "pending"
STATUS_IN_PROGRESS: str = "in_progress"
STATUS_COMPLETED: str = "completed"
STATUS_SKIPPED: str = "skipped"
STATUS_FAILED: str = "failed"

FINISHED_STATUSES: set[str] = {STATUS_COMPLETED, STATUS_SKIPPED, STATUS_FAILED}

TASK_BRANCH_PREFIX: str = "task/"
CHECK_DEPS_STEP_ID: str = "check-deps"
CREATE_BRANCH_STEP_ID: str = "create-branch"


def _detect_repo_root() -> Path:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and len(result.stdout.strip()) > 0:
            return Path(result.stdout.strip())
    except OSError:
        pass
    return Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_tracker(*, task_id: str) -> dict[str, Any] | None:
    tracker_path: Path = step_tracker_path(task_id=task_id)
    if not tracker_path.exists():
        return None
    try:
        raw: str = tracker_path.read_text(encoding="utf-8")
        data: object = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def _save_tracker(*, task_id: str, data: dict[str, Any]) -> None:
    tracker_path: Path = step_tracker_path(task_id=task_id)
    tracker_path.write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8",
    )


def _get_current_branch(*, repo_root: Path) -> str | None:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except OSError:
        return None


def _is_working_tree_clean(*, repo_root: Path) -> bool:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        return result.returncode == 0 and len(result.stdout.strip()) == 0
    except OSError:
        return False


def _find_step_in_tracker(
    *,
    tracker: dict[str, Any],
    step_id: str,
) -> dict[str, Any] | None:
    steps: object = tracker.get(FIELD_STEPS)
    if not isinstance(steps, list):
        return None
    for step in steps:
        if isinstance(step, dict) and step.get(FIELD_NAME) == step_id:
            return step
    return None


def _get_previous_steps(
    *,
    tracker: dict[str, Any],
    step_order: int,
) -> list[dict[str, Any]]:
    steps: object = tracker.get(FIELD_STEPS)
    if not isinstance(steps, list):
        return []
    previous: list[dict[str, Any]] = []
    for step in steps:
        if isinstance(step, dict):
            order: object = step.get(FIELD_STEP)
            if isinstance(order, int) and order < step_order:
                previous.append(step)
    return previous


def _error(message: str) -> None:
    print(f"PRESTEP ERROR: {message}", file=sys.stderr)


def _info(message: str) -> None:
    print(f"PRESTEP: {message}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _create_minimal_tracker(*, task_id: str) -> dict[str, Any]:
    """Create a minimal step_tracker with just the create-branch step.

    Used when prestep is called for create-branch before the full tracker
    exists (step_tracker.json is now created on the task branch, not main).
    The execute-task skill overwrites this with the full step list immediately
    after prestep completes.
    """
    tracker: dict[str, Any] = {
        "task_id": task_id,
        FIELD_STEPS: [
            {
                FIELD_STEP: 1,
                FIELD_NAME: CREATE_BRANCH_STEP_ID,
                "description": f"Create task/{task_id} branch from main.",
                FIELD_STATUS: STATUS_PENDING,
                FIELD_STARTED_AT: None,
                "completed_at": None,
                FIELD_LOG_FILE: None,
            },
        ],
    }
    _save_tracker(task_id=task_id, data=tracker)
    _info("Created minimal step_tracker.json for create-branch")
    return tracker


def run_prestep(*, task_id: str, step_id: str) -> int:
    repo_root: Path = _detect_repo_root()

    # Load tracker (auto-create for create-branch if missing)
    tracker: dict[str, Any] | None = _load_tracker(task_id=task_id)
    if tracker is None:
        if step_id == CREATE_BRANCH_STEP_ID:
            tracker = _create_minimal_tracker(task_id=task_id)
        else:
            _error(f"Cannot load step_tracker.json for task {task_id}")
            return 1

    # Find step
    step: dict[str, Any] | None = _find_step_in_tracker(
        tracker=tracker,
        step_id=step_id,
    )
    if step is None:
        _error(f"Step '{step_id}' not found in step_tracker.json")
        return 1

    step_order: object = step.get(FIELD_STEP)
    if not isinstance(step_order, int):
        _error(f"Step '{step_id}' has no valid step number")
        return 1

    # Check step is pending
    current_status: str = str(step.get(FIELD_STATUS, ""))
    if current_status != STATUS_PENDING:
        _error(f"Step '{step_id}' has status '{current_status}', expected '{STATUS_PENDING}'")
        return 1

    # Check previous steps are finished (skip for create-branch — it's step 1)
    if step_id != CREATE_BRANCH_STEP_ID:
        previous: list[dict[str, Any]] = _get_previous_steps(
            tracker=tracker,
            step_order=step_order,
        )
        for prev in previous:
            prev_status: str = str(prev.get(FIELD_STATUS, ""))
            prev_name: str = str(prev.get(FIELD_NAME, "?"))
            if prev_status not in FINISHED_STATUSES:
                _error(
                    f"Previous step '{prev_name}' has status "
                    f"'{prev_status}', must be completed/skipped/failed"
                )
                return 1

    # Check correct branch (skip for create-branch — it creates the branch)
    if step_id != CREATE_BRANCH_STEP_ID:
        expected_branch: str = TASK_BRANCH_PREFIX + task_id
        actual_branch: str | None = _get_current_branch(repo_root=repo_root)
        if actual_branch != expected_branch:
            _error(
                f"Expected branch '{expected_branch}', currently on '{actual_branch}'. "
                "Are you running inside the correct worktree?"
            )
            return 1

    # Check working tree is clean (skip for create-branch — it's the first step)
    if step_id != CREATE_BRANCH_STEP_ID and not _is_working_tree_clean(repo_root=repo_root):
        _error("Working tree is not clean — commit previous step first")
        return 1

    # Check step folder doesn't already exist
    folder: Path = step_folder_path(
        task_id=task_id,
        step_order=step_order,
        step_id=step_id,
    )
    if folder.exists():
        _error(f"Step folder already exists: {folder}")
        return 1

    # For check-deps: run dependency verification
    if step_id == CHECK_DEPS_STEP_ID:
        dep_result: subprocess.CompletedProcess[str] = subprocess.run(
            [
                "uv",
                "run",
                "python",
                str(repo_root / "arf" / "scripts" / "verificators" / "verify_task_dependencies.py"),
                task_id,
            ],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        if dep_result.returncode != 0:
            _error("Dependency check failed:")
            print(dep_result.stdout, file=sys.stderr)
            return 1

    # --- All checks passed ---

    # Create step log folder
    folder.mkdir(parents=True, exist_ok=True)
    _info(f"Created step folder: {folder.relative_to(TASKS_DIR.parent)}")

    # Mark step as in_progress
    now: str = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    step[FIELD_STATUS] = STATUS_IN_PROGRESS
    step[FIELD_STARTED_AT] = now
    step[FIELD_LOG_FILE] = (
        str(
            folder.relative_to(TASKS_DIR / task_id),
        )
        + "/"
    )
    _save_tracker(task_id=task_id, data=tracker)
    _info(f"Step '{step_id}' is now in_progress (started_at: {now})")

    return 0


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Pre-step: validate preconditions and mark step in_progress",
    )
    parser.add_argument(
        "task_id",
        help="Task ID (e.g. t0003_download_training_corpus)",
    )
    parser.add_argument(
        "step_id",
        help="Step ID (e.g. research-papers, implementation)",
    )
    args: argparse.Namespace = parser.parse_args()

    sys.exit(run_prestep(task_id=args.task_id, step_id=args.step_id))


if __name__ == "__main__":
    main()
