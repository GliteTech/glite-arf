from pathlib import Path

from arf.scripts.verificators.common import paths
from arf.tests.fixtures.writers import write_json, write_text

STATUS_COMPLETED: str = "completed"
STATUS_IN_PROGRESS: str = "in_progress"
STATUS_NOT_STARTED: str = "not_started"
DEFAULT_START_TIME: str = "2026-04-01T00:00:00Z"
DEFAULT_END_TIME: str = "2026-04-02T00:00:00Z"

REQUIRED_TOP_DIRS: list[str] = [
    "plan",
    "research",
    "assets",
    "results",
    "corrections",
    "intervention",
    "logs",
]
REQUIRED_LOG_SUBDIRS: list[str] = [
    "commands",
    "steps",
    "searches",
    "sessions",
]


def build_task_json(
    *,
    repo_root: Path,
    task_id: str,
    task_index: int = 1,
    status: str = STATUS_COMPLETED,
    spec_version: int = 4,
    name: str = "Test Task",
    short_description: str = "A test task for unit testing.",
    long_description_file: str | None = "task_description.md",
    long_description: str | None = None,
    start_time: str | None = DEFAULT_START_TIME,
    end_time: str | None = DEFAULT_END_TIME,
    dependencies: list[str] | None = None,
    expected_assets: dict[str, int] | None = None,
    task_types: list[str] | None = None,
    source_suggestion: str | None = None,
    overrides: dict[str, object] | None = None,
) -> Path:
    data: dict[str, object] = {
        "spec_version": spec_version,
        "task_id": task_id,
        "task_index": task_index,
        "name": name,
        "short_description": short_description,
        "status": status,
        "dependencies": dependencies if dependencies is not None else [],
        "start_time": start_time,
        "end_time": end_time,
        "expected_assets": (expected_assets if expected_assets is not None else {}),
        "task_types": task_types if task_types is not None else [],
        "source_suggestion": source_suggestion,
    }
    if long_description_file is not None:
        data["long_description_file"] = long_description_file
    elif long_description is not None:
        data["long_description"] = long_description
    else:
        data["long_description_file"] = "task_description.md"

    if overrides is not None:
        data.update(overrides)

    task_json_path: Path = paths.task_json_path(task_id=task_id)
    write_json(path=task_json_path, data=data)

    if long_description_file is not None and "long_description_file" in data:
        desc_path: Path = paths.task_dir(task_id=task_id) / str(data["long_description_file"])
        if not desc_path.exists():
            write_text(
                path=desc_path,
                content="# Test Task\n\nA detailed task description.\n",
            )

    return task_json_path


def build_task_folder(
    *,
    repo_root: Path,
    task_id: str,
    subdirs: list[str] | None = None,
    include_log_subdirs: bool = True,
    include_init_py: bool = True,
) -> Path:
    task_root: Path = paths.task_dir(task_id=task_id)
    dirs_to_create: list[str] = subdirs if subdirs is not None else REQUIRED_TOP_DIRS
    for dir_name in dirs_to_create:
        (task_root / dir_name).mkdir(parents=True, exist_ok=True)
    if include_log_subdirs:
        for log_sub in REQUIRED_LOG_SUBDIRS:
            (task_root / "logs" / log_sub).mkdir(parents=True, exist_ok=True)
    if include_init_py:
        init_path: Path = task_root / "__init__.py"
        if not init_path.exists():
            write_text(path=init_path, content="")
    return task_root


def build_step_tracker(
    *,
    repo_root: Path,
    task_id: str,
    steps: list[dict[str, object]] | None = None,
) -> Path:
    data: dict[str, object] = {
        "task_id": task_id,
        "steps": steps if steps is not None else [],
    }
    tracker_path: Path = paths.step_tracker_path(task_id=task_id)
    write_json(path=tracker_path, data=data)
    return tracker_path


def build_complete_task(
    *,
    repo_root: Path,
    task_id: str,
    task_index: int = 1,
    status: str = STATUS_COMPLETED,
    task_json_overrides: dict[str, object] | None = None,
) -> Path:
    build_task_folder(repo_root=repo_root, task_id=task_id)
    build_task_json(
        repo_root=repo_root,
        task_id=task_id,
        task_index=task_index,
        status=status,
        overrides=task_json_overrides,
    )
    build_step_tracker(repo_root=repo_root, task_id=task_id)
    return paths.task_dir(task_id=task_id)
