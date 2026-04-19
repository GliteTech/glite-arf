import json
from pathlib import Path

import pytest

import arf.scripts.aggregators.aggregate_suggestions as aggregate_suggestions_module
import arf.scripts.aggregators.aggregate_tasks as aggregate_tasks_module
import arf.scripts.overview.common as overview_common
import arf.scripts.overview.format_metrics as format_metrics_module
import arf.scripts.overview.paths as overview_paths
import meta.asset_types.dataset.aggregator as aggregate_datasets_module
import meta.asset_types.dataset.format_overview as format_datasets_module
from arf.scripts.verificators.common import paths

TASKS_SUBDIR: str = "tasks"
OVERVIEW_SUBDIR: str = "overview"
DATASETS_SUBDIR: str = "dataset"
META_SUBDIR: str = "meta"
ASSETS_SUBDIR: str = "assets"
RESULTS_SUBDIR: str = "results"
DESCRIPTION_FILE_NAME: str = "description.md"
DETAILS_FILE_NAME: str = "details.json"
README_FILE_NAME: str = "README.md"
TASK_JSON_FILE_NAME: str = "task.json"
SUGGESTIONS_FILE_NAME: str = "suggestions.json"
DATASETS_MARKDOWN_FILE_NAME: str = "datasets.md"
METRICS_MARKDOWN_FILE_NAME: str = "metrics.md"
BY_DATE_ADDED_SUBDIR: str = "by-date-added"
BY_CATEGORY_SUBDIR: str = "by-category"
SPEC_VERSION_1: str = "1"
SPEC_VERSION_2: str = "2"


def _write_json(*, path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        data=json.dumps(obj=data, indent=2),
        encoding="utf-8",
    )


def _write_text(*, path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        data=content,
        encoding="utf-8",
    )


def _configure_repo_paths(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    tasks_dir: Path = repo_root / TASKS_SUBDIR
    overview_dir: Path = repo_root / OVERVIEW_SUBDIR
    metrics_dir: Path = repo_root / META_SUBDIR / "metrics"
    dataset_assets_dir: Path = repo_root / ASSETS_SUBDIR / DATASETS_SUBDIR

    tasks_dir.mkdir(parents=True, exist_ok=True)
    overview_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    dataset_assets_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(target=paths, name="REPO_ROOT", value=repo_root)
    monkeypatch.setattr(target=paths, name="TASKS_DIR", value=tasks_dir)
    monkeypatch.setattr(target=paths, name="OVERVIEW_DIR", value=overview_dir)
    monkeypatch.setattr(target=paths, name="METRICS_DIR", value=metrics_dir)
    monkeypatch.setattr(
        target=paths,
        name="DATASET_ASSETS_DIR",
        value=dataset_assets_dir,
    )

    monkeypatch.setattr(target=aggregate_tasks_module, name="TASKS_DIR", value=tasks_dir)
    monkeypatch.setattr(
        target=aggregate_suggestions_module,
        name="TASKS_DIR",
        value=tasks_dir,
    )
    monkeypatch.setattr(
        target=aggregate_datasets_module,
        name="TASKS_DIR",
        value=tasks_dir,
    )

    monkeypatch.setattr(target=overview_common, name="REPO_ROOT", value=repo_root)
    monkeypatch.setattr(target=overview_common, name="OVERVIEW_DIR", value=overview_dir)
    monkeypatch.setattr(target=overview_paths, name="REPO_ROOT", value=repo_root)
    monkeypatch.setattr(target=overview_paths, name="OVERVIEW_DIR", value=overview_dir)

    monkeypatch.setattr(
        format_datasets_module,
        "DATASETS_README",
        overview_dir / DATASETS_SUBDIR / README_FILE_NAME,
    )
    monkeypatch.setattr(
        format_datasets_module,
        "DATASETS_BY_DATE_DIR",
        overview_dir / DATASETS_SUBDIR / BY_DATE_ADDED_SUBDIR,
    )
    monkeypatch.setattr(
        format_datasets_module,
        "DATASETS_BY_DATE_README",
        overview_dir / DATASETS_SUBDIR / BY_DATE_ADDED_SUBDIR / README_FILE_NAME,
    )
    # `DATASETS_BY_CATEGORY_DIR` is resolved from `REPO_ROOT` at import time.
    # If left unpatched, `materialize_datasets` calls `remove_dir_if_exists`
    # against the real `overview/datasets/by-category/` and silently deletes
    # project files every time the test runs.
    monkeypatch.setattr(
        format_datasets_module,
        "DATASETS_BY_CATEGORY_DIR",
        overview_dir / DATASETS_SUBDIR / BY_CATEGORY_SUBDIR,
    )
    monkeypatch.setattr(
        format_metrics_module,
        "METRICS_README",
        overview_dir / "metrics" / README_FILE_NAME,
    )


def _create_task(
    *,
    repo_root: Path,
    task_id: str,
    task_index: int,
    start_time: str | None,
    end_time: str | None,
) -> None:
    _write_json(
        path=repo_root / TASKS_SUBDIR / task_id / TASK_JSON_FILE_NAME,
        data=aggregate_tasks_module.TaskModel(
            task_id=task_id,
            task_index=task_index,
            name=f"Task {task_index}",
            short_description=f"Short description for {task_id}.",
            long_description=f"Long description for {task_id}.",
            status="completed",
            dependencies=[],
            start_time=start_time,
            end_time=end_time,
            task_types=[],
            expected_assets={},
            source_suggestion=None,
        ).model_dump(),
    )


def _create_suggestions_file(*, repo_root: Path, task_id: str, suggestion_id: str) -> None:
    _write_json(
        path=repo_root / TASKS_SUBDIR / task_id / RESULTS_SUBDIR / SUGGESTIONS_FILE_NAME,
        data=aggregate_suggestions_module.SuggestionsFileModel(
            spec_version=SPEC_VERSION_2,
            suggestions=[
                aggregate_suggestions_module.SuggestionModel(
                    id=suggestion_id,
                    title="Suggestion title",
                    description="Detailed suggestion description for testing.",
                    kind="dataset",
                    priority="high",
                    source_task=task_id,
                    source_paper=None,
                    categories=["dataset"],
                    status="active",
                ),
            ],
        ).model_dump(),
    )


def _create_dataset_asset(*, repo_root: Path, task_id: str, dataset_id: str) -> None:
    asset_dir: Path = (
        repo_root / TASKS_SUBDIR / task_id / ASSETS_SUBDIR / DATASETS_SUBDIR / dataset_id
    )
    _write_json(
        path=asset_dir / DETAILS_FILE_NAME,
        data=aggregate_datasets_module.DatasetDetailsModel(
            spec_version=SPEC_VERSION_1,
            dataset_id=dataset_id,
            name=f"Dataset {dataset_id}",
            version=None,
            short_description=f"Short description for {dataset_id}.",
            source_paper_id=None,
            url=None,
            download_url=None,
            year=2024,
            date_published=None,
            authors=[],
            institutions=[],
            license=None,
            access_kind="public",
            size_description="10 rows",
            files=[
                aggregate_datasets_module.DatasetFileModel(
                    path="files/data.jsonl",
                    description="Data file",
                    format="jsonl",
                ),
            ],
            categories=["dataset"],
        ).model_dump(),
    )
    _write_text(
        path=asset_dir / DESCRIPTION_FILE_NAME,
        content=(
            "---\n"
            'spec_version: "1"\n'
            f'dataset_id: "{dataset_id}"\n'
            f'summarized_by_task: "{task_id}"\n'
            'date_summarized: "2026-04-03"\n'
            "---\n\n"
            "## Summary\n\n"
            "Dataset summary.\n"
        ),
    )


def test_aggregate_tasks_and_suggestions_prefer_task_end_time(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: str = "t0001_source_task"
    suggestion_id: str = "S-0001-01"

    _create_task(
        repo_root=tmp_path,
        task_id=task_id,
        task_index=1,
        start_time="2026-04-01T08:00:00Z",
        end_time="2026-04-02T12:30:00Z",
    )
    _create_suggestions_file(
        repo_root=tmp_path,
        task_id=task_id,
        suggestion_id=suggestion_id,
    )

    tasks: list[aggregate_tasks_module.TaskInfoFull] = aggregate_tasks_module.aggregate_tasks_full(
        filter_ids=[task_id],
    )
    suggestions: list[aggregate_suggestions_module.SuggestionInfoFull] = (
        aggregate_suggestions_module.aggregate_suggestions_full(
            filter_ids=[suggestion_id],
        )
    )

    assert len(tasks) == 1
    assert tasks[0].effective_date == "2026-04-02"

    assert len(suggestions) == 1
    assert suggestions[0].date_added == "2026-04-02"


def test_aggregate_datasets_use_end_time_then_start_time(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)

    first_task_id: str = "t0001_dataset_done"
    second_task_id: str = "t0002_dataset_started"

    _create_task(
        repo_root=tmp_path,
        task_id=first_task_id,
        task_index=1,
        start_time="2026-04-01T09:00:00Z",
        end_time="2026-04-02T10:00:00Z",
    )
    _create_task(
        repo_root=tmp_path,
        task_id=second_task_id,
        task_index=2,
        start_time="2026-04-05T11:00:00Z",
        end_time=None,
    )
    _create_dataset_asset(repo_root=tmp_path, task_id=first_task_id, dataset_id="dataset-one")
    _create_dataset_asset(repo_root=tmp_path, task_id=second_task_id, dataset_id="dataset-two")

    datasets: list[aggregate_datasets_module.DatasetInfoFull] = (
        aggregate_datasets_module.aggregate_datasets_full(
            filter_ids=["dataset-one", "dataset-two"],
        )
    )
    dataset_map: dict[str, aggregate_datasets_module.DatasetInfoFull] = {
        dataset.dataset_id: dataset for dataset in datasets
    }

    assert dataset_map["dataset-one"].date_added == "2026-04-02"
    assert dataset_map["dataset-two"].date_added == "2026-04-05"


def test_materializers_write_folder_based_readmes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)

    old_datasets_file: Path = tmp_path / OVERVIEW_SUBDIR / DATASETS_MARKDOWN_FILE_NAME
    old_metrics_file: Path = tmp_path / OVERVIEW_SUBDIR / METRICS_MARKDOWN_FILE_NAME
    _write_text(path=old_datasets_file, content="old datasets")
    _write_text(path=old_metrics_file, content="old metrics")

    format_datasets_module.materialize_datasets(datasets=[])
    format_metrics_module.materialize_metrics(metrics=[])

    assert (tmp_path / OVERVIEW_SUBDIR / DATASETS_SUBDIR / README_FILE_NAME).exists()
    assert (
        tmp_path / OVERVIEW_SUBDIR / DATASETS_SUBDIR / BY_DATE_ADDED_SUBDIR / README_FILE_NAME
    ).exists()
    assert (tmp_path / OVERVIEW_SUBDIR / "metrics" / README_FILE_NAME).exists()
    assert not old_datasets_file.exists()
    assert not old_metrics_file.exists()
