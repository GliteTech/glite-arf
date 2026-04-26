from pathlib import Path

import pytest

import arf.scripts.aggregators.aggregate_metric_results as agg_mod
import arf.scripts.aggregators.aggregate_metrics as metrics_def_mod
from arf.scripts.aggregators.aggregate_metric_results import (
    MetricResultsFull,
    aggregate_metric_results_full,
)
from arf.tests.fixtures.metadata_builders import build_metric
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.writers import write_json

METRIC_FOO: str = "foo"
TASK_A: str = "t0001_alpha"


@pytest.fixture()
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        aggregator_modules=[agg_mod, metrics_def_mod],
    )
    return tmp_path


def _build_task_with_metrics(
    *,
    repo_root: Path,
    task_id: str,
    metrics_payload: dict[str, object],
) -> None:
    task_dir: Path = repo_root / "tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        path=task_dir / "task.json",
        data={
            "spec_version": "5",
            "name": task_id,
            "short_description": "test",
            "long_description": "test",
            "status": "completed",
            "dependencies": [],
        },
    )
    write_json(
        path=task_dir / "results" / "metrics.json",
        data=metrics_payload,
    )


def test_full_exposes_higher_is_better_false(repo: Path) -> None:
    build_metric(
        repo_root=repo,
        metric_key=METRIC_FOO,
        overrides={"higher_is_better": False},
    )
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_A,
        metrics_payload={METRIC_FOO: 1.0},
    )
    result: list[MetricResultsFull] = aggregate_metric_results_full()
    assert len(result) == 1
    assert result[0].higher_is_better is False


def test_full_exposes_higher_is_better_true(repo: Path) -> None:
    build_metric(
        repo_root=repo,
        metric_key=METRIC_FOO,
        overrides={"higher_is_better": True},
    )
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_A,
        metrics_payload={METRIC_FOO: 1.0},
    )
    result: list[MetricResultsFull] = aggregate_metric_results_full()
    assert len(result) == 1
    assert result[0].higher_is_better is True
