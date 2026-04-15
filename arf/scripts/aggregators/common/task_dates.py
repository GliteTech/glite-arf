"""Helpers for deriving task-based dates used by overview-facing aggregators."""

import subprocess
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, ValidationError

from arf.scripts.verificators.common import paths as repo_paths


@dataclass(frozen=True, slots=True)
class TaskTimingInfo:
    start_time: str | None
    end_time: str | None


class TaskTimingFileModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="allow",
    )

    start_time: str | None = None
    end_time: str | None = None


def normalize_task_date(*, value: str | None) -> str | None:
    if value is None:
        return None
    stripped: str = value.strip()
    if len(stripped) < 10:
        return None
    return stripped[:10]


def _git_creation_date(*, task_id: str) -> str | None:
    file_path: Path = repo_paths.task_json_path(task_id=task_id)
    if not file_path.exists():
        return None
    try:
        relative_path: str = str(file_path.relative_to(repo_paths.REPO_ROOT))
    except ValueError:
        return None
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [
                "git",
                "log",
                "--diff-filter=A",
                "--format=%ai",
                "--",
                relative_path,
            ],
            capture_output=True,
            text=True,
            cwd=repo_paths.REPO_ROOT,
            timeout=5.0,
        )
        if result.returncode != 0:
            return None
        lines: list[str] = result.stdout.strip().splitlines()
        if len(lines) == 0:
            return None
        return normalize_task_date(value=lines[-1])
    except (OSError, subprocess.TimeoutExpired):
        return None


def derive_effective_task_date(
    *,
    start_time: str | None,
    end_time: str | None,
    task_id: str | None = None,
) -> str | None:
    end_date: str | None = normalize_task_date(value=end_time)
    if end_date is not None:
        return end_date

    start_date: str | None = normalize_task_date(value=start_time)
    if start_date is not None:
        return start_date

    if task_id is not None:
        return _git_creation_date(task_id=task_id)

    return None


def load_task_timing(*, task_id: str | None) -> TaskTimingInfo | None:
    if task_id is None:
        return None

    file_path: Path = repo_paths.task_json_path(task_id=task_id)
    if not file_path.exists():
        return None

    try:
        task_file: TaskTimingFileModel = TaskTimingFileModel.model_validate_json(
            file_path.read_text(encoding="utf-8"),
        )
    except (OSError, ValidationError):
        return None

    return TaskTimingInfo(
        start_time=task_file.start_time,
        end_time=task_file.end_time,
    )


def load_task_effective_date(*, task_id: str | None) -> str | None:
    task_timing: TaskTimingInfo | None = load_task_timing(task_id=task_id)
    if task_timing is None:
        return None
    return derive_effective_task_date(
        start_time=task_timing.start_time,
        end_time=task_timing.end_time,
        task_id=task_id,
    )
