import json
from pathlib import Path
from typing import Any

import pytest

import arf.scripts.utils.init_task_folders as init_task_folders_module
from arf.scripts.verificators.common import paths

type TaskID = str

TASKS_SUBDIR: str = "tasks"
TASK_JSON_FILE_NAME: str = "task.json"


def _write_json(*, path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj=data, indent=2) + "\n",
        encoding="utf-8",
    )


def _configure_repo_paths(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> Path:
    tasks_dir: Path = repo_root / TASKS_SUBDIR
    tasks_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(target=paths, name="TASKS_DIR", value=tasks_dir)
    monkeypatch.setattr(target=init_task_folders_module, name="TASKS_DIR", value=tasks_dir)
    return tasks_dir


def _create_minimal_task(*, tasks_dir: Path, task_id: TaskID) -> Path:
    task_root: Path = tasks_dir / task_id
    task_root.mkdir(parents=True, exist_ok=True)
    _write_json(
        path=task_root / TASK_JSON_FILE_NAME,
        data={
            "task_id": task_id,
            "task_index": 1,
            "name": "Test task",
            "short_description": "Short description.",
            "status": "not_started",
            "dependencies": [],
            "expected_assets": {},
            "task_types": [],
        },
    )
    return task_root


def test_init_creates_init_py_in_task_root_and_code(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks_dir: Path = _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0001_test_init_py"
    task_root: Path = _create_minimal_task(tasks_dir=tasks_dir, task_id=task_id)

    result = init_task_folders_module.init_task_folders(task_id=task_id)

    root_init: Path = task_root / "__init__.py"
    code_init: Path = task_root / "code" / "__init__.py"

    assert root_init.exists() is True, "__init__.py created in task root"
    assert code_init.exists() is True, "__init__.py created in code/"
    assert len(result.init_py_created) == 2


def test_init_does_not_overwrite_existing_init_py(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks_dir: Path = _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0002_no_overwrite"
    task_root: Path = _create_minimal_task(tasks_dir=tasks_dir, task_id=task_id)

    # Pre-create __init__.py with custom content
    task_root.joinpath("__init__.py").write_text(
        "# existing content\n",
        encoding="utf-8",
    )
    code_dir: Path = task_root / "code"
    code_dir.mkdir(parents=True, exist_ok=True)
    code_dir.joinpath("__init__.py").write_text(
        "# code init\n",
        encoding="utf-8",
    )

    result = init_task_folders_module.init_task_folders(task_id=task_id)

    assert task_root.joinpath("__init__.py").read_text(encoding="utf-8") == "# existing content\n"
    assert code_dir.joinpath("__init__.py").read_text(encoding="utf-8") == "# code init\n"
    assert len(result.init_py_created) == 0


def test_init_reports_created_init_py_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks_dir: Path = _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0003_report_init_py"
    _create_minimal_task(tasks_dir=tasks_dir, task_id=task_id)

    result = init_task_folders_module.init_task_folders(task_id=task_id)

    created_set: set[str] = set(result.init_py_created)
    assert "__init__.py" in created_set, "task root __init__.py reported"
    assert "code/__init__.py" in created_set, "code/__init__.py reported"
