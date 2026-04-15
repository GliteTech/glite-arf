"""Manage git worktrees for parallel task execution.

Usage:
    uv run python -m arf.scripts.utils.worktree create <task_id>
    uv run python -m arf.scripts.utils.worktree remove <task_id> [--force]
    uv run python -m arf.scripts.utils.worktree list
    uv run python -m arf.scripts.utils.worktree path <task_id>
    uv run python -m arf.scripts.utils.worktree raw-path <slug>
    uv run python -m arf.scripts.utils.worktree sync-status [--dry-run]

Worktrees are created in a sibling directory:
    ../<repo-name>-worktrees/<slug>/

The `path` subcommand validates its argument as a task ID. The `raw-path`
subcommand accepts any slug (including `infra_*` for framework-change
worktrees) and computes the same sibling-directory path without validation.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT: Path = Path(__file__).resolve().parents[3]
TASKS_DIR: Path = REPO_ROOT / "tasks"
WORKTREES_BASE: Path = REPO_ROOT.parent / f"{REPO_ROOT.name}-worktrees"

TASK_BRANCH_PREFIX: str = "task/"
TASK_ID_PATTERN: re.Pattern[str] = re.compile(r"^t\d{4}_.+$")

_WORKTREE_LINE_PREFIX: str = "worktree "
_BRANCH_LINE_PREFIX: str = "branch refs/heads/"

CMD_CREATE: str = "create"
CMD_REMOVE: str = "remove"
CMD_LIST: str = "list"
CMD_PATH: str = "path"
CMD_RAW_PATH: str = "raw-path"
CMD_SYNC_STATUS: str = "sync-status"

FIELD_STATUS: str = "status"
FIELD_START_TIME: str = "start_time"
STATUS_NOT_STARTED: str = "not_started"
STATUS_IN_PROGRESS: str = "in_progress"
ISO8601_UTC_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"

REMOTE_NAME: str = "origin"
MAIN_BRANCH: str = "main"

DISK_SPACE_EXTRA_BYTES: int = 10 * 1024**3  # 10 GB reserved for task work


@dataclass(frozen=True, slots=True)
class WorktreeEntry:
    task_id: str
    branch: str


def worktree_path_for(*, slug: str) -> Path:
    """Compute the worktree path for an arbitrary slug.

    Pure function: no validation, no filesystem access, no git calls.
    Returns ``WORKTREES_BASE / slug``. Use this from any caller that needs
    the sibling-worktree path convention without requiring the slug to
    match the ``tNNNN_*`` task-ID pattern — in particular from
    framework-change (``infra/*``) tooling and from skills that need to
    print the path for a user-facing command.
    """
    return WORKTREES_BASE / slug


def _worktree_path(*, task_id: str) -> Path:
    return worktree_path_for(slug=task_id)


def _run_git(
    *,
    args: list[str],
    cwd: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        cwd=cwd if cwd is not None else REPO_ROOT,
        check=check,
    )


def _validate_task_id(*, task_id: str) -> None:
    if TASK_ID_PATTERN.match(task_id) is None:
        print(
            f"Error: invalid task_id format '{task_id}'. "
            "Expected tNNNN_slug (e.g. t0003_download_semcor_dataset)",
            file=sys.stderr,
        )
        sys.exit(1)


def _branch_exists(*, branch_name: str) -> bool:
    result: subprocess.CompletedProcess[str] = _run_git(
        args=["rev-parse", "--verify", f"refs/heads/{branch_name}"],
        check=False,
    )
    return result.returncode == 0


def _worktree_exists(*, worktree_path: Path) -> bool:
    result: subprocess.CompletedProcess[str] = _run_git(
        args=["worktree", "list", "--porcelain"],
    )
    resolved: str = str(worktree_path.resolve())
    for line in result.stdout.splitlines():
        wt_prefix_len: int = len(_WORKTREE_LINE_PREFIX)
        if line.startswith(_WORKTREE_LINE_PREFIX) and line[wt_prefix_len:] == resolved:
            return True
    return False


# -------------------------------------------------------------------
# Worktree entry listing (shared by cmd_list and cmd_sync_status)
# -------------------------------------------------------------------


def _list_worktree_entries() -> list[WorktreeEntry]:
    result: subprocess.CompletedProcess[str] = _run_git(
        args=["worktree", "list", "--porcelain"],
    )

    worktrees_prefix: str = str(WORKTREES_BASE.resolve())
    current_path: str = ""
    current_branch: str = ""

    entries: list[WorktreeEntry] = []

    for line in result.stdout.splitlines():
        if line.startswith(_WORKTREE_LINE_PREFIX):
            current_path = line[len(_WORKTREE_LINE_PREFIX) :]
            current_branch = ""
        elif line.startswith(_BRANCH_LINE_PREFIX):
            current_branch = line[len(_BRANCH_LINE_PREFIX) :]
        elif len(line) == 0:
            if current_path.startswith(worktrees_prefix):
                task_id: str = Path(current_path).name
                entries.append(
                    WorktreeEntry(task_id=task_id, branch=current_branch),
                )
            current_path = ""
            current_branch = ""

    return entries


# -------------------------------------------------------------------
# Status transition helpers
# -------------------------------------------------------------------


def _push_main(*, task_id: str) -> bool:
    result: subprocess.CompletedProcess[str] = _run_git(
        args=["push", REMOTE_NAME, MAIN_BRANCH],
        check=False,
    )
    if result.returncode != 0:
        print(
            f"Warning: failed to push 'Start task {task_id}' commit "
            f"to {REMOTE_NAME}.\n"
            f"  {result.stderr.strip()}\n"
            "  The worktree will still be created. Push manually:\n"
            f"    git push {REMOTE_NAME} {MAIN_BRANCH}",
            file=sys.stderr,
        )
        return False
    return True


def _mark_task_in_progress(*, task_id: str, task_json_path: Path) -> bool:
    raw: str = task_json_path.read_text(encoding="utf-8")
    data: dict[str, Any] = json.loads(raw)

    current_status: object = data.get(FIELD_STATUS)
    if current_status != STATUS_NOT_STARTED:
        print(
            f"Warning: task status is '{current_status}', "
            f"expected '{STATUS_NOT_STARTED}'. "
            "Skipping in_progress update on main.",
            file=sys.stderr,
        )
        return True

    now: str = datetime.now(tz=UTC).strftime(ISO8601_UTC_FORMAT)
    data[FIELD_STATUS] = STATUS_IN_PROGRESS
    data[FIELD_START_TIME] = now

    task_json_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    task_folder: Path = task_json_path.parent
    relative_folder: str = str(task_folder.relative_to(REPO_ROOT))
    add_result: subprocess.CompletedProcess[str] = _run_git(
        args=["add", relative_folder],
        check=False,
    )
    if add_result.returncode != 0:
        print(
            f"Error staging task folder:\n{add_result.stderr}",
            file=sys.stderr,
        )
        return False

    commit_result: subprocess.CompletedProcess[str] = _run_git(
        args=["commit", "-m", f"Start task {task_id}"],
        check=False,
    )
    if commit_result.returncode != 0:
        print(
            f"Error committing task.json:\n{commit_result.stderr}",
            file=sys.stderr,
        )
        return False

    # Push to remote so the status survives local main resets
    _push_main(task_id=task_id)

    return True


def _revert_last_commit() -> None:
    _run_git(args=["reset", "--soft", "HEAD~1"], check=False)
    _run_git(args=["checkout", "--", "."], check=False)


# -------------------------------------------------------------------
# Disk space helpers
# -------------------------------------------------------------------

_LFS_SIZE_PATTERN: re.Pattern[str] = re.compile(r"\(([0-9.]+)\s+(B|KB|MB|GB)\)\s*$")

_LFS_UNIT_MULTIPLIERS: dict[str, int] = {
    "B": 1,
    "KB": 1024,
    "MB": 1024**2,
    "GB": 1024**3,
}


def _estimate_worktree_bytes() -> int:
    """Estimate the disk space a full worktree checkout would consume."""
    # Non-LFS blob sizes from git tree
    tree_result: subprocess.CompletedProcess[str] = _run_git(
        args=["ls-tree", "-r", "-l", "HEAD"],
        check=False,
    )
    tree_bytes: int = 0
    if tree_result.returncode == 0:
        for line in tree_result.stdout.splitlines():
            parts: list[str] = line.split()
            if len(parts) >= 4 and parts[3] != "-":
                tree_bytes += int(parts[3])

    # Actual LFS file sizes (replace pointer sizes with real sizes)
    lfs_result: subprocess.CompletedProcess[str] = _run_git(
        args=["lfs", "ls-files", "-s"],
        check=False,
    )
    lfs_bytes: int = 0
    if lfs_result.returncode == 0:
        for line in lfs_result.stdout.splitlines():
            m: re.Match[str] | None = _LFS_SIZE_PATTERN.search(line)
            if m is not None:
                value: float = float(m.group(1))
                unit: str = m.group(2)
                lfs_bytes += int(value * _LFS_UNIT_MULTIPLIERS[unit])

    return tree_bytes + lfs_bytes


def _check_disk_space() -> bool:
    """Return True if enough disk space exists for a new worktree."""
    estimated: int = _estimate_worktree_bytes()
    required: int = estimated + DISK_SPACE_EXTRA_BYTES

    check_path: Path = WORKTREES_BASE if WORKTREES_BASE.exists() else WORKTREES_BASE.parent
    free: int = shutil.disk_usage(check_path).free

    if free < required:
        estimated_gb: float = estimated / 1024**3
        extra_gb: float = DISK_SPACE_EXTRA_BYTES / 1024**3
        required_gb: float = required / 1024**3
        free_gb: float = free / 1024**3
        print(
            f"Error: not enough disk space to create a worktree.\n"
            f"  Worktree checkout: {estimated_gb:.1f} GB\n"
            f"  Task work reserve: {extra_gb:.0f} GB\n"
            f"  Total required:    {required_gb:.1f} GB\n"
            f"  Available:         {free_gb:.1f} GB\n"
            f"  Shortfall:         {(required - free) / 1024**3:.1f} GB\n"
            f"\n"
            f"Free disk space or remove unused worktrees:\n"
            f"  uv run python -m arf.scripts.utils.worktree list\n"
            f"  uv run python -m arf.scripts.utils.worktree remove <task_id>",
            file=sys.stderr,
        )
        return False

    return True


# -------------------------------------------------------------------
# Subcommands
# -------------------------------------------------------------------


def cmd_create(*, task_id: str) -> int:
    _validate_task_id(task_id=task_id)

    task_json: Path = TASKS_DIR / task_id / "task.json"
    if not task_json.exists():
        print(
            f"Error: {task_json.relative_to(REPO_ROOT)} does not exist. "
            "Register the task on main before creating a worktree.",
            file=sys.stderr,
        )
        return 1

    branch_name: str = TASK_BRANCH_PREFIX + task_id
    wt_path: Path = _worktree_path(task_id=task_id)

    if _branch_exists(branch_name=branch_name):
        print(
            f"Error: branch '{branch_name}' already exists.\n"
            f"  To reuse it: git worktree add {wt_path} {branch_name}\n"
            f"  To delete it: git branch -D {branch_name}",
            file=sys.stderr,
        )
        return 1

    if wt_path.exists():
        print(
            f"Error: worktree directory already exists: {wt_path}\n"
            f"  Remove it first: git worktree remove {wt_path}",
            file=sys.stderr,
        )
        return 1

    if _worktree_exists(worktree_path=wt_path):
        print(
            f"Error: a git worktree is already registered at {wt_path}",
            file=sys.stderr,
        )
        return 1

    if not _check_disk_space():
        return 1

    # Mark task as in_progress on main before branching
    status_updated: bool = _mark_task_in_progress(
        task_id=task_id,
        task_json_path=task_json,
    )
    if not status_updated:
        return 1

    # Create worktree with new branch
    WORKTREES_BASE.mkdir(parents=True, exist_ok=True)
    result: subprocess.CompletedProcess[str] = _run_git(
        args=["worktree", "add", str(wt_path), "-b", branch_name],
        check=False,
    )
    if result.returncode != 0:
        print(f"Error creating worktree:\n{result.stderr}", file=sys.stderr)
        _revert_last_commit()
        return 1

    # Run uv sync in the new worktree
    sync_result: subprocess.CompletedProcess[str] = subprocess.run(
        ["uv", "sync"],
        capture_output=True,
        text=True,
        cwd=wt_path,
    )
    if sync_result.returncode != 0:
        print(
            f"Warning: uv sync failed in worktree:\n{sync_result.stderr}",
            file=sys.stderr,
        )

    # Symlink .env from main repo (gitignored, needed for API keys)
    env_source: Path = REPO_ROOT / ".env"
    env_target: Path = wt_path / ".env"
    if env_source.exists() and not env_target.exists():
        env_target.symlink_to(env_source)

    # Run direnv allow (non-fatal if direnv is not installed)
    subprocess.run(
        ["direnv", "allow"],
        capture_output=True,
        text=True,
        cwd=wt_path,
    )

    print(str(wt_path))
    return 0


def cmd_remove(*, task_id: str, force: bool) -> int:
    _validate_task_id(task_id=task_id)

    wt_path: Path = _worktree_path(task_id=task_id)

    if not _worktree_exists(worktree_path=wt_path):
        print(
            f"Error: no worktree found at {wt_path}",
            file=sys.stderr,
        )
        return 1

    args: list[str] = ["worktree", "remove", str(wt_path)]
    if force:
        args.append("--force")

    result: subprocess.CompletedProcess[str] = _run_git(
        args=args,
        check=False,
    )
    if result.returncode != 0:
        print(
            f"Error removing worktree:\n{result.stderr}"
            "Use --force to remove worktrees with uncommitted changes.",
            file=sys.stderr,
        )
        return 1

    print(f"Removed worktree for {task_id}")
    return 0


def cmd_list() -> int:
    entries: list[WorktreeEntry] = _list_worktree_entries()

    if len(entries) == 0:
        print("No active task worktrees.")
        return 0

    for entry in entries:
        wt: Path = _worktree_path(task_id=entry.task_id)
        print(f"{entry.task_id}  branch={entry.branch}  path={wt}")

    return 0


def cmd_path(*, task_id: str) -> int:
    _validate_task_id(task_id=task_id)
    print(str(_worktree_path(task_id=task_id)))
    return 0


def cmd_raw_path(*, slug: str) -> int:
    print(str(worktree_path_for(slug=slug)))
    return 0


def cmd_sync_status(*, dry_run: bool) -> int:
    """Detect and fix status inconsistencies between worktrees and main.

    For each active worktree on a task/ branch, reads the task status from
    main's task.json. If main says not_started but the worktree exists (meaning
    the task was started), updates main to in_progress and pushes.
    """
    entries: list[WorktreeEntry] = _list_worktree_entries()

    if len(entries) == 0:
        print("No active task worktrees.")
        return 0

    fixed_count: int = 0
    error_count: int = 0

    for entry in entries:
        if not entry.branch.startswith(TASK_BRANCH_PREFIX):
            continue

        task_json: Path = TASKS_DIR / entry.task_id / "task.json"
        if not task_json.exists():
            continue

        raw: str = task_json.read_text(encoding="utf-8")
        data: dict[str, Any] = json.loads(raw)
        current_status: object = data.get(FIELD_STATUS)

        if current_status != STATUS_NOT_STARTED:
            continue

        # Inconsistency: worktree exists but main says not_started
        if dry_run:
            print(
                f"[dry-run] {entry.task_id}: status is "
                f"'{STATUS_NOT_STARTED}' on main but worktree exists"
            )
            fixed_count += 1
            continue

        now: str = datetime.now(tz=UTC).strftime(ISO8601_UTC_FORMAT)
        data[FIELD_STATUS] = STATUS_IN_PROGRESS
        data[FIELD_START_TIME] = now

        task_json.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        relative_folder: str = str(task_json.parent.relative_to(REPO_ROOT))
        add_result: subprocess.CompletedProcess[str] = _run_git(
            args=["add", relative_folder],
            check=False,
        )
        if add_result.returncode != 0:
            print(
                f"Error staging {entry.task_id}:\n{add_result.stderr}",
                file=sys.stderr,
            )
            error_count += 1
            continue

        commit_result: subprocess.CompletedProcess[str] = _run_git(
            args=[
                "commit",
                "-m",
                f"Fix status: mark {entry.task_id} as in_progress",
            ],
            check=False,
        )
        if commit_result.returncode != 0:
            print(
                f"Error committing {entry.task_id}:\n{commit_result.stderr}",
                file=sys.stderr,
            )
            error_count += 1
            continue

        print(f"Fixed {entry.task_id}: {STATUS_NOT_STARTED} -> {STATUS_IN_PROGRESS}")
        fixed_count += 1

    # Push all fixes in one push
    if not dry_run and fixed_count > 0:
        push_result: subprocess.CompletedProcess[str] = _run_git(
            args=["push", REMOTE_NAME, MAIN_BRANCH],
            check=False,
        )
        if push_result.returncode != 0:
            print(
                f"Warning: push failed.\n  {push_result.stderr.strip()}\n"
                f"  Push manually: git push {REMOTE_NAME} {MAIN_BRANCH}",
                file=sys.stderr,
            )

    label: str = "Would fix" if dry_run else "Fixed"
    print(f"\n{label} {fixed_count} inconsistencies, {error_count} errors.")
    return 1 if error_count > 0 else 0


# -------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Manage git worktrees for parallel task execution",
    )
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser] = parser.add_subparsers(
        dest="command", required=True
    )

    # create
    create_parser: argparse.ArgumentParser = subparsers.add_parser(
        CMD_CREATE,
        help="Create a worktree for a task",
    )
    create_parser.add_argument(
        "task_id",
        help="Task ID (e.g. t0003_download_semcor_dataset)",
    )

    # remove
    remove_parser: argparse.ArgumentParser = subparsers.add_parser(
        CMD_REMOVE,
        help="Remove a task worktree",
    )
    remove_parser.add_argument(
        "task_id",
        help="Task ID (e.g. t0003_download_semcor_dataset)",
    )
    remove_parser.add_argument(
        "--force",
        action="store_true",
        help="Force removal even with uncommitted changes",
    )

    # list
    subparsers.add_parser(
        CMD_LIST,
        help="List active task worktrees",
    )

    # path
    path_parser: argparse.ArgumentParser = subparsers.add_parser(
        CMD_PATH,
        help="Print worktree path for a task",
    )
    path_parser.add_argument(
        "task_id",
        help="Task ID (e.g. t0003_download_semcor_dataset)",
    )

    # raw-path
    raw_path_parser: argparse.ArgumentParser = subparsers.add_parser(
        CMD_RAW_PATH,
        help="Print worktree path for any slug (no task-ID validation)",
    )
    raw_path_parser.add_argument(
        "slug",
        help="Arbitrary slug (e.g. infra_import_self_skills or t0003_foo)",
    )

    # sync-status
    sync_parser: argparse.ArgumentParser = subparsers.add_parser(
        CMD_SYNC_STATUS,
        help="Detect and fix status inconsistencies between worktrees and main",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report inconsistencies without fixing them",
    )

    args: argparse.Namespace = parser.parse_args()

    if args.command == CMD_CREATE:
        sys.exit(cmd_create(task_id=args.task_id))
    elif args.command == CMD_REMOVE:
        sys.exit(cmd_remove(task_id=args.task_id, force=args.force))
    elif args.command == CMD_LIST:
        sys.exit(cmd_list())
    elif args.command == CMD_PATH:
        sys.exit(cmd_path(task_id=args.task_id))
    elif args.command == CMD_RAW_PATH:
        sys.exit(cmd_raw_path(slug=args.slug))
    elif args.command == CMD_SYNC_STATUS:
        sys.exit(cmd_sync_status(dry_run=args.dry_run))
    else:
        msg: str = f"Unknown command: {args.command}"
        raise AssertionError(msg)  # noqa: TRY004 — unreachable guard


if __name__ == "__main__":
    main()
