import json
from pathlib import Path
from typing import Any

import pytest

import arf.scripts.aggregators.aggregate_tasks as aggregate_tasks_module
import arf.scripts.common.task_description as task_description_module
import arf.scripts.verificators.verify_task_file as verify_task_file_module
import arf.scripts.verificators.verify_task_folder as verify_task_folder_module
from arf.scripts.common.task_description import (
    FIELD_LONG_DESCRIPTION,
    FIELD_LONG_DESCRIPTION_FILE,
    FIELD_SPEC_VERSION,
    RECOMMENDED_TASK_DESCRIPTION_FILE_NAME,
)
from arf.scripts.verificators.common import paths
from arf.scripts.verificators.common.types import VerificationResult

type TaskID = str

TASKS_SUBDIR: str = "tasks"
META_SUBDIR: str = "meta"
TASK_TYPES_SUBDIR: str = "task_types"
TASK_JSON_FILE_NAME: str = "task.json"
STEP_TRACKER_FILE_NAME: str = "step_tracker.json"
TASK_DESCRIPTION_FILE_NAME: str = "task_description.md"
TASK_STATUS_NOT_STARTED: str = "not_started"


def _write_json(*, path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj=data, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_text(*, path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _configure_repo_paths(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    tasks_dir: Path = repo_root / TASKS_SUBDIR
    task_types_dir: Path = repo_root / META_SUBDIR / TASK_TYPES_SUBDIR

    tasks_dir.mkdir(parents=True, exist_ok=True)
    task_types_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(target=paths, name="TASKS_DIR", value=tasks_dir)
    monkeypatch.setattr(target=paths, name="TASK_TYPES_DIR", value=task_types_dir)
    monkeypatch.setattr(target=verify_task_file_module, name="TASKS_DIR", value=tasks_dir)
    monkeypatch.setattr(target=verify_task_file_module, name="TASK_TYPES_DIR", value=task_types_dir)
    monkeypatch.setattr(target=verify_task_folder_module, name="TASKS_DIR", value=tasks_dir)
    monkeypatch.setattr(target=aggregate_tasks_module, name="TASKS_DIR", value=tasks_dir)
    monkeypatch.setattr(target=task_description_module, name="TASKS_DIR", value=tasks_dir)


def _task_json_data(
    *,
    task_id: TaskID,
    task_index: int,
    spec_version: int | None = None,
    long_description: str | None = "Inline long description.",
    long_description_file: str | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "task_id": task_id,
        "task_index": task_index,
        "name": "Example task",
        "short_description": "Short description.",
        "status": TASK_STATUS_NOT_STARTED,
        "dependencies": [],
        "start_time": None,
        "end_time": None,
        "expected_assets": {},
        "task_types": [],
        "source_suggestion": None,
    }
    if spec_version is not None:
        data[FIELD_SPEC_VERSION] = spec_version
    if long_description is not None:
        data[FIELD_LONG_DESCRIPTION] = long_description
    if long_description_file is not None:
        data[FIELD_LONG_DESCRIPTION_FILE] = long_description_file
    return data


def _create_minimal_task_skeleton(
    *,
    repo_root: Path,
    task_id: TaskID,
    task_json: dict[str, Any],
) -> Path:
    task_root: Path = repo_root / TASKS_SUBDIR / task_id
    _write_json(path=paths.task_json_path(task_id=task_id), data=task_json)
    _write_json(
        path=paths.step_tracker_path(task_id=task_id),
        data={
            "task_id": task_id,
            "steps": [],
        },
    )

    for dir_name in [
        "plan",
        "research",
        "assets",
        "results",
        "corrections",
        "intervention",
        "logs",
    ]:
        (task_root / dir_name).mkdir(parents=True, exist_ok=True)

    for dir_name in ["commands", "steps", "searches", "sessions"]:
        (task_root / "logs" / dir_name).mkdir(parents=True, exist_ok=True)

    return task_root


def _diagnostic_codes(
    *,
    result: VerificationResult,
) -> set[str]:
    return {diagnostic.code.text for diagnostic in result.diagnostics}


def test_verify_task_file_accepts_legacy_inline_long_description(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0001_legacy_inline"
    _write_json(
        path=paths.task_json_path(task_id=task_id),
        data=_task_json_data(
            task_id=task_id,
            task_index=1,
            spec_version=None,
        ),
    )

    result = verify_task_file_module.verify_task_file(task_id=task_id)

    assert result.passed


def test_verify_task_file_accepts_version_4_markdown_long_description(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0002_markdown_description"
    _write_json(
        path=paths.task_json_path(task_id=task_id),
        data=_task_json_data(
            task_id=task_id,
            task_index=2,
            spec_version=4,
            long_description=None,
            long_description_file=RECOMMENDED_TASK_DESCRIPTION_FILE_NAME,
        ),
    )
    _write_text(
        path=task_description_module.task_description_file_path(
            task_id=task_id,
            file_name=RECOMMENDED_TASK_DESCRIPTION_FILE_NAME,
        ),
        content="# Task description\n\nUse markdown for the long description.\n",
    )

    result = verify_task_file_module.verify_task_file(task_id=task_id)

    assert result.passed


def test_verify_task_file_rejects_both_description_sources_in_version_4(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0003_both_descriptions"
    _write_json(
        path=paths.task_json_path(task_id=task_id),
        data=_task_json_data(
            task_id=task_id,
            task_index=3,
            spec_version=4,
            long_description="Inline description.",
            long_description_file=RECOMMENDED_TASK_DESCRIPTION_FILE_NAME,
        ),
    )

    result = verify_task_file_module.verify_task_file(task_id=task_id)

    assert "TF-E014" in _diagnostic_codes(result=result)


def test_verify_task_file_rejects_missing_markdown_description_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0004_missing_description_file"
    _write_json(
        path=paths.task_json_path(task_id=task_id),
        data=_task_json_data(
            task_id=task_id,
            task_index=4,
            spec_version=4,
            long_description=None,
            long_description_file=RECOMMENDED_TASK_DESCRIPTION_FILE_NAME,
        ),
    )

    result = verify_task_file_module.verify_task_file(task_id=task_id)

    assert "TF-E016" in _diagnostic_codes(result=result)


def test_verify_task_file_rejects_non_integer_spec_version(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0005_bad_spec_version"
    _write_json(
        path=paths.task_json_path(task_id=task_id),
        data={
            **_task_json_data(
                task_id=task_id,
                task_index=5,
            ),
            "spec_version": "4",
        },
    )

    result = verify_task_file_module.verify_task_file(task_id=task_id)

    assert "TF-E013" in _diagnostic_codes(result=result)


def test_aggregate_tasks_full_resolves_markdown_long_description(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0006_aggregate_markdown_description"
    expected_long_description: str = "# Title\n\nMarkdown description body.\n"
    _write_json(
        path=paths.task_json_path(task_id=task_id),
        data=_task_json_data(
            task_id=task_id,
            task_index=6,
            spec_version=4,
            long_description=None,
            long_description_file=RECOMMENDED_TASK_DESCRIPTION_FILE_NAME,
        ),
    )
    _write_text(
        path=task_description_module.task_description_file_path(
            task_id=task_id,
            file_name=RECOMMENDED_TASK_DESCRIPTION_FILE_NAME,
        ),
        content=expected_long_description,
    )

    tasks = aggregate_tasks_module.aggregate_tasks_full(filter_ids=[task_id])

    assert len(tasks) == 1
    assert tasks[0].long_description == expected_long_description


def test_verify_task_folder_allows_referenced_task_description_markdown_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: TaskID = "t0007_folder_allows_markdown_description"
    _create_minimal_task_skeleton(
        repo_root=tmp_path,
        task_id=task_id,
        task_json=_task_json_data(
            task_id=task_id,
            task_index=7,
            spec_version=4,
            long_description=None,
            long_description_file=RECOMMENDED_TASK_DESCRIPTION_FILE_NAME,
        ),
    )
    _write_text(
        path=task_description_module.task_description_file_path(
            task_id=task_id,
            file_name=RECOMMENDED_TASK_DESCRIPTION_FILE_NAME,
        ),
        content="Markdown description.\n",
    )

    result = verify_task_folder_module.verify_task_folder(task_id=task_id)
    diagnostic_codes: set[str] = {diagnostic.code.text for diagnostic in result.diagnostics}

    assert "FD-E016" not in diagnostic_codes
