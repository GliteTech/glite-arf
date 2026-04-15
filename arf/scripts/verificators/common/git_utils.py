import subprocess
from pathlib import Path

from arf.scripts.verificators.common.constants import ALLOWED_OUTSIDE_FILES

GIT_CMD: str = "git"
TASKS_PREFIX: str = "tasks/"


def get_current_branch(*, repo_root: Path) -> str | None:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [GIT_CMD, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except OSError:
        return None


def get_changed_files(
    *,
    repo_root: Path,
    base: str,
    head: str,
) -> list[str] | None:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [GIT_CMD, "diff", "--name-only", f"{base}...{head}"],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        if result.returncode != 0:
            return None
    except OSError:
        return None

    files: list[str] = list(
        dict.fromkeys(
            stripped
            for line in result.stdout.strip().split("\n")
            if len(stripped := line.strip()) > 0
        ),
    )
    return files


def find_violating_files(
    *,
    changed_files: list[str],
    task_id: str,
) -> list[str]:
    task_prefix: str = f"{TASKS_PREFIX}{task_id}/"
    violations: list[str] = []
    for file_path in changed_files:
        is_allowed: bool = file_path.startswith(task_prefix) or any(
            file_path == allowed or file_path.startswith(allowed)
            for allowed in ALLOWED_OUTSIDE_FILES
        )
        if not is_allowed:
            violations.append(file_path)
    return violations


def get_commit_subjects(
    *,
    repo_root: Path,
    base: str,
    head: str,
) -> list[str] | None:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [GIT_CMD, "log", f"{base}..{head}", "--format=%s"],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        if result.returncode != 0:
            return None
    except OSError:
        return None

    subjects: list[str] = []
    for line in result.stdout.strip().split("\n"):
        stripped: str = line.strip()
        if len(stripped) > 0:
            subjects.append(stripped)
    return subjects


def get_file_size_in_head(
    *,
    repo_root: Path,
    file_path: str,
    head: str,
) -> int | None:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [GIT_CMD, "cat-file", "-s", f"{head}:{file_path}"],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        if result.returncode != 0:
            return None
        return int(result.stdout.strip())
    except (OSError, ValueError):
        return None
