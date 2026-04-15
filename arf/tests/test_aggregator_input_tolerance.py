import json
from pathlib import Path

import pytest
from pydantic import BaseModel

import arf.scripts.aggregators.aggregate_suggestions as aggregate_suggestions_module
import arf.scripts.aggregators.aggregate_tasks as aggregate_tasks_module
import meta.asset_types.answer.aggregator as aggregate_answers_module
import meta.asset_types.dataset.aggregator as aggregate_datasets_module
import meta.asset_types.library.aggregator as aggregate_libraries_module
import meta.asset_types.model.aggregator as aggregate_models_module
import meta.asset_types.paper.aggregator as aggregate_papers_module
import meta.asset_types.predictions.aggregator as aggregate_predictions_module
from arf.scripts.verificators.common import paths

TASKS_SUBDIR: str = "tasks"
ASSETS_SUBDIR: str = "assets"
DATASET_SUBDIR: str = "dataset"
PREDICTIONS_SUBDIR: str = "predictions"
TASK_JSON_FILE_NAME: str = "task.json"
DETAILS_FILE_NAME: str = "details.json"
DESCRIPTION_FILE_NAME: str = "description.md"


def _write_json(*, path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        data=json.dumps(obj=data, indent=2),
        encoding="utf-8",
    )


def _write_text(*, path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data=content, encoding="utf-8")


def _configure_repo_paths(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    tasks_dir: Path = repo_root / TASKS_SUBDIR
    dataset_assets_dir: Path = repo_root / ASSETS_SUBDIR / DATASET_SUBDIR
    predictions_assets_dir: Path = repo_root / ASSETS_SUBDIR / PREDICTIONS_SUBDIR

    tasks_dir.mkdir(parents=True, exist_ok=True)
    dataset_assets_dir.mkdir(parents=True, exist_ok=True)
    predictions_assets_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(target=paths, name="REPO_ROOT", value=repo_root)
    monkeypatch.setattr(target=paths, name="TASKS_DIR", value=tasks_dir)
    monkeypatch.setattr(target=paths, name="DATASET_ASSETS_DIR", value=dataset_assets_dir)
    monkeypatch.setattr(
        target=paths,
        name="PREDICTIONS_ASSETS_DIR",
        value=predictions_assets_dir,
    )

    monkeypatch.setattr(target=aggregate_datasets_module, name="TASKS_DIR", value=tasks_dir)
    monkeypatch.setattr(target=aggregate_predictions_module, name="TASKS_DIR", value=tasks_dir)
    monkeypatch.setattr(target=aggregate_tasks_module, name="TASKS_DIR", value=tasks_dir)


def _create_task(
    *,
    repo_root: Path,
    task_id: str,
    task_index: int,
    start_time: str,
    end_time: str | None,
    extra_fields: dict[str, object] | None = None,
) -> None:
    data: dict[str, object] = aggregate_tasks_module.TaskModel(
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
    ).model_dump()
    if extra_fields is not None:
        data.update(extra_fields)
    _write_json(
        path=repo_root / TASKS_SUBDIR / task_id / TASK_JSON_FILE_NAME,
        data=data,
    )


def _create_dataset_asset(
    *,
    repo_root: Path,
    task_id: str,
    dataset_id: str,
    extra_fields: dict[str, object] | None = None,
) -> None:
    asset_dir: Path = (
        repo_root / TASKS_SUBDIR / task_id / ASSETS_SUBDIR / DATASET_SUBDIR / dataset_id
    )
    details: dict[str, object] = aggregate_datasets_module.DatasetDetailsModel(
        spec_version="1",
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
    ).model_dump()
    if extra_fields is not None:
        details.update(extra_fields)
    _write_json(path=asset_dir / DETAILS_FILE_NAME, data=details)
    _write_text(
        path=asset_dir / DESCRIPTION_FILE_NAME,
        content=(
            "---\n"
            'spec_version: "1"\n'
            f'dataset_id: "{dataset_id}"\n'
            f'summarized_by_task: "{task_id}"\n'
            'date_summarized: "2026-04-04"\n'
            "---\n\n"
            "## Summary\n\n"
            "Dataset summary.\n"
        ),
    )
    _write_text(path=asset_dir / "files" / "data.jsonl", content='{"id": 1}\n')


def _create_predictions_asset(
    *,
    repo_root: Path,
    task_id: str,
    predictions_id: str,
    extra_fields: dict[str, object] | None = None,
) -> None:
    asset_dir: Path = (
        repo_root / TASKS_SUBDIR / task_id / ASSETS_SUBDIR / PREDICTIONS_SUBDIR / predictions_id
    )
    details: dict[str, object] = aggregate_predictions_module.PredictionsDetailsModel(
        spec_version="1",
        predictions_id=predictions_id,
        name=f"Predictions {predictions_id}",
        short_description=f"Short description for {predictions_id}.",
        model_id=None,
        model_description="Model description.",
        dataset_ids=["dataset-one"],
        prediction_format="jsonl",
        prediction_schema="JSONL rows.",
        instance_count=3,
        metrics_at_creation={"f1_all": 55.5},
        description_path="description.md",
        files=[
            aggregate_predictions_module.PredictionFileModel(
                path="files/predictions.jsonl",
                description="Predictions file",
                format="jsonl",
            ),
        ],
        categories=["wsd"],
        created_by_task=task_id,
        date_created="2026-04-04",
    ).model_dump()
    if extra_fields is not None:
        details.update(extra_fields)
    _write_json(path=asset_dir / DETAILS_FILE_NAME, data=details)
    _write_text(
        path=asset_dir / DESCRIPTION_FILE_NAME,
        content=(
            "---\n"
            'spec_version: "1"\n'
            f'predictions_id: "{predictions_id}"\n'
            f'created_by_task: "{task_id}"\n'
            'date_created: "2026-04-04"\n'
            "---\n\n"
            "## Summary\n\n"
            "Predictions summary.\n"
        ),
    )
    _write_text(path=asset_dir / "files" / "predictions.jsonl", content='{"id": 1}\n')


@pytest.mark.parametrize(
    "model",
    [
        aggregate_answers_module.AnswerDetailsModel,
        aggregate_datasets_module.AuthorModel,
        aggregate_datasets_module.InstitutionModel,
        aggregate_datasets_module.DatasetFileModel,
        aggregate_datasets_module.DatasetDetailsModel,
        aggregate_libraries_module.EntryPointModel,
        aggregate_libraries_module.LibraryDetailsModel,
        aggregate_models_module.ModelFileModel,
        aggregate_models_module.ModelDetailsModel,
        aggregate_papers_module.AuthorModel,
        aggregate_papers_module.InstitutionModel,
        aggregate_papers_module.PaperDetailsModel,
        aggregate_predictions_module.PredictionFileModel,
        aggregate_predictions_module.PredictionsDetailsModel,
        aggregate_suggestions_module.SuggestionModel,
        aggregate_suggestions_module.SuggestionsFileModel,
        aggregate_suggestions_module.TaskSourceSuggestionModel,
        aggregate_tasks_module.TaskFileModel,
        aggregate_tasks_module.TaskModel,
        aggregate_tasks_module.StepTrackerStepModel,
        aggregate_tasks_module.StepTrackerFileModel,
    ],
)
def test_aggregator_input_models_ignore_unknown_fields(model: type[BaseModel]) -> None:
    assert model.model_config.get("extra") == "ignore"


def test_aggregate_datasets_keeps_assets_with_extra_details_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: str = "t0001_dataset_task"
    dataset_id: str = "dataset-with-extras"

    _create_task(
        repo_root=tmp_path,
        task_id=task_id,
        task_index=1,
        start_time="2026-04-03T08:00:00Z",
        end_time="2026-04-04T09:30:00Z",
    )
    _create_dataset_asset(
        repo_root=tmp_path,
        task_id=task_id,
        dataset_id=dataset_id,
        extra_fields={
            "checksums": {"data.jsonl": "sha256:test"},
            "added_by_task": "wrong-task",
            "date_added": "1999-01-01",
        },
    )

    datasets: list[aggregate_datasets_module.DatasetInfoFull] = (
        aggregate_datasets_module.aggregate_datasets_full(filter_ids=[dataset_id])
    )

    assert [dataset.dataset_id for dataset in datasets] == [dataset_id]
    assert datasets[0].added_by_task == task_id
    assert datasets[0].date_added == "2026-04-04"


def test_aggregate_predictions_keeps_assets_with_extra_details_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: str = "t0002_predictions_task"
    predictions_id: str = "predictions-with-extras"

    _create_task(
        repo_root=tmp_path,
        task_id=task_id,
        task_index=2,
        start_time="2026-04-04T08:00:00Z",
        end_time="2026-04-04T09:00:00Z",
    )
    _create_predictions_asset(
        repo_root=tmp_path,
        task_id=task_id,
        predictions_id=predictions_id,
        extra_fields={
            "provenance": {"upstream_task_id": "t9999_source"},
            "upstream_summary_metrics": {"f1_all": 55.5},
        },
    )

    predictions: list[aggregate_predictions_module.PredictionsInfoFull] = (
        aggregate_predictions_module.aggregate_predictions_full(filter_ids=[predictions_id])
    )

    assert [item.predictions_id for item in predictions] == [predictions_id]
    assert predictions[0].created_by_task == task_id
    assert predictions[0].metrics_at_creation == {"f1_all": 55.5}


def test_aggregate_tasks_keeps_tasks_with_extra_fields_and_skips_non_task_dirs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_repo_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    task_id: str = "t0003_task_with_extras"

    _create_task(
        repo_root=tmp_path,
        task_id=task_id,
        task_index=3,
        start_time="2026-04-04T08:00:00Z",
        end_time=None,
        extra_fields={"owner": "research-agent"},
    )
    (tmp_path / TASKS_SUBDIR / "__pycache__").mkdir(parents=True, exist_ok=True)

    tasks: list[aggregate_tasks_module.TaskInfoFull] = aggregate_tasks_module.aggregate_tasks_full(
        filter_ids=[task_id]
    )

    assert aggregate_tasks_module._discover_task_ids() == [task_id]
    assert [task.task_id for task in tasks] == [task_id]
