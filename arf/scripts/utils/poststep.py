"""Post-step script: verify step outputs, mark step completed.

Run this after finishing work on a step. It checks that all required
outputs exist and the work is committed, then marks the step as completed.

Usage:
    uv run python -m arf.scripts.utils.poststep <task_id> <step_id>

What it does:
    1. Loads step_tracker.json and finds the step.
    2. Checks the step is currently in_progress.
    3. Runs verify_step.py to check step folder and required files.
    4. Checks working tree is clean (step work is committed).
    5. Checks latest commit message contains the step ID.
    6. Marks the step as completed with completed_at timestamp.

Exit codes:
    0 — step verified and marked completed
    1 — verification failed
"""

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.paths import (
    step_tracker_path,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FIELD_STEPS: str = "steps"
FIELD_STEP: str = "step"
FIELD_NAME: str = "name"
FIELD_STATUS: str = "status"
FIELD_COMPLETED_AT: str = "completed_at"

STATUS_IN_PROGRESS: str = "in_progress"
STATUS_COMPLETED: str = "completed"
STATUS_SKIPPED: str = "skipped"

STEP_LOG_FILENAME: str = "step_log.md"

_SCRIPTS_DIR: Path = Path(__file__).resolve().parents[1]
VERIFY_STEP_SCRIPT: Path = _SCRIPTS_DIR / "verificators" / "verify_step.py"


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


def _is_working_tree_clean(*, repo_root: Path) -> bool:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        return result.returncode == 0 and len(result.stdout.strip()) == 0
    except OSError:
        return False


def _get_latest_commit_message(*, repo_root: Path) -> str | None:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["git", "log", "-1", "--format=%s"],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except OSError:
        return None


def _error(message: str) -> None:
    print(f"POSTSTEP ERROR: {message}", file=sys.stderr)


def _info(message: str) -> None:
    print(f"POSTSTEP: {message}")


def _warn(message: str) -> None:
    print(f"POSTSTEP WARNING: {message}")


def _warn_missing_skipped_step_logs(
    *,
    task_id: str,
    tracker: dict[str, Any],
    current_step_order: int,
) -> None:
    steps: object = tracker.get(FIELD_STEPS)
    if not isinstance(steps, list):
        return
    from arf.scripts.verificators.common.paths import step_logs_dir

    steps_dir: Path = step_logs_dir(task_id=task_id)
    for entry in steps:
        if not isinstance(entry, dict):
            continue
        order: object = entry.get(FIELD_STEP)
        if not isinstance(order, int) or order >= current_step_order:
            continue
        if entry.get(FIELD_STATUS) != STATUS_SKIPPED:
            continue
        name: object = entry.get(FIELD_NAME)
        if not isinstance(name, str):
            continue
        step_dir_pattern: str = f"{order:03d}_{name}"
        step_dir: Path = steps_dir / step_dir_pattern
        log_file: Path = step_dir / STEP_LOG_FILENAME
        if not log_file.exists():
            _warn(
                f"Skipped step '{name}' (step {order}) is missing "
                f"{step_dir_pattern}/{STEP_LOG_FILENAME} — "
                f"create it before the reporting step"
            )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run_poststep(*, task_id: str, step_id: str) -> int:
    repo_root: Path = _detect_repo_root()

    # Load tracker
    tracker: dict[str, Any] | None = _load_tracker(task_id=task_id)
    if tracker is None:
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

    # Warn about missing skipped-step logs (non-blocking)
    _warn_missing_skipped_step_logs(
        task_id=task_id,
        tracker=tracker,
        current_step_order=step_order,
    )

    # Check step is in_progress
    current_status: str = str(step.get(FIELD_STATUS, ""))
    if current_status != STATUS_IN_PROGRESS:
        _error(f"Step '{step_id}' has status '{current_status}', expected '{STATUS_IN_PROGRESS}'")
        return 1

    # Run verify_step.py
    verify_result: subprocess.CompletedProcess[str] = subprocess.run(
        [
            "uv",
            "run",
            "python",
            str(VERIFY_STEP_SCRIPT),
            task_id,
            step_id,
            "--step-number",
            str(step_order),
        ],
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    if verify_result.returncode != 0:
        _error("Step verification failed:")
        if len(verify_result.stdout) > 0:
            print(verify_result.stdout)
        if len(verify_result.stderr) > 0:
            print(verify_result.stderr, file=sys.stderr)
        return 1
    _info("Step verification passed")

    # Check working tree is clean
    if not _is_working_tree_clean(repo_root=repo_root):
        _error("Working tree is not clean — commit step work first")
        return 1

    # Check latest commit contains step ID (warning only)
    latest_commit: str | None = _get_latest_commit_message(repo_root=repo_root)
    if latest_commit is not None and step_id not in latest_commit:
        _warn(f"Latest commit does not contain step ID '{step_id}': '{latest_commit}'")

    # --- All checks passed ---

    # Mark step as completed
    now: str = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    step[FIELD_STATUS] = STATUS_COMPLETED
    step[FIELD_COMPLETED_AT] = now
    _save_tracker(task_id=task_id, data=tracker)
    _info(f"Step '{step_id}' is now completed (completed_at: {now})")

    # Auto-commit the tracker update
    tracker_file: str = str(
        step_tracker_path(task_id=task_id).relative_to(repo_root),
    )
    subprocess.run(
        ["git", "add", tracker_file],
        cwd=repo_root,
    )
    commit_msg: str = f"{task_id} [{step_id}]: Mark step completed"
    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=repo_root,
    )
    _info("Committed step_tracker.json update")

    return 0


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Post-step: verify outputs and mark step completed",
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

    sys.exit(run_poststep(task_id=args.task_id, step_id=args.step_id))


if __name__ == "__main__":
    main()
