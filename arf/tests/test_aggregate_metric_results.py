"""Tests for arf.scripts.aggregators.aggregate_metric_results."""

from pathlib import Path

import pytest

import arf.scripts.aggregators.aggregate_metric_results as agg_mod
import arf.scripts.aggregators.aggregate_metrics as metrics_def_mod
from arf.scripts.aggregators.aggregate_metric_results import (
    MetricResultEntry,
    MetricResultsFull,
    MetricResultsShort,
    aggregate_metric_results_full,
    aggregate_metric_results_short,
)
from arf.tests.fixtures.metadata_builders import build_metric
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.writers import write_json

METRIC_F1: str = "f1_all"
METRIC_ACCURACY: str = "accuracy_all"
TASK_A: str = "t0001_alpha"
TASK_B: str = "t0002_beta"


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
    metrics_payload: dict[str, object] | None = None,
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
    if metrics_payload is not None:
        write_json(
            path=task_dir / "results" / "metrics.json",
            data=metrics_payload,
        )


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------


def test_empty_returns_no_results_short(repo: Path) -> None:
    result: list[MetricResultsShort] = aggregate_metric_results_short()
    assert len(result) == 0


def test_empty_returns_no_results_full(repo: Path) -> None:
    result: list[MetricResultsFull] = aggregate_metric_results_full()
    assert len(result) == 0


# ---------------------------------------------------------------------------
# Legacy flat format
# ---------------------------------------------------------------------------


def test_legacy_format_single_task(repo: Path) -> None:
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_A,
        metrics_payload={METRIC_F1: 79.6, METRIC_ACCURACY: 80.0},
    )
    result: list[MetricResultsShort] = aggregate_metric_results_short()
    keys: list[str] = [r.metric_key for r in result]
    assert METRIC_ACCURACY in keys
    assert METRIC_F1 in keys

    f1_results: MetricResultsShort = next(r for r in result if r.metric_key == METRIC_F1)
    assert f1_results.result_count == 1
    assert f1_results.entries[0].task_id == TASK_A
    assert f1_results.entries[0].variant_id == ""
    assert f1_results.entries[0].variant_label is None
    assert f1_results.entries[0].value == 79.6


# ---------------------------------------------------------------------------
# Explicit variants format
# ---------------------------------------------------------------------------


def test_explicit_variants_format(repo: Path) -> None:
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_A,
        metrics_payload={
            "variants": [
                {
                    "variant_id": "model-a",
                    "label": "Model A",
                    "dimensions": {"model": "a"},
                    "metrics": {METRIC_F1: 85.0},
                },
                {
                    "variant_id": "model-b",
                    "label": "Model B",
                    "dimensions": {"model": "b"},
                    "metrics": {METRIC_F1: 90.0},
                },
            ],
        },
    )
    result: list[MetricResultsShort] = aggregate_metric_results_short()
    assert len(result) == 1
    assert result[0].metric_key == METRIC_F1
    assert result[0].result_count == 2

    ids: list[str] = [e.variant_id for e in result[0].entries]
    assert "model-a" in ids
    assert "model-b" in ids

    model_b: MetricResultEntry = next(e for e in result[0].entries if e.variant_id == "model-b")
    assert model_b.variant_label == "Model B"
    assert model_b.value == 90.0


# ---------------------------------------------------------------------------
# Multiple tasks same metric
# ---------------------------------------------------------------------------


def test_multiple_tasks_same_metric(repo: Path) -> None:
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_A,
        metrics_payload={METRIC_F1: 79.6},
    )
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_B,
        metrics_payload={METRIC_F1: 82.1},
    )
    result: list[MetricResultsShort] = aggregate_metric_results_short()
    assert len(result) == 1
    assert result[0].result_count == 2
    task_ids: list[str] = [e.task_id for e in result[0].entries]
    assert TASK_A in task_ids
    assert TASK_B in task_ids


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def test_filter_by_metric_key(repo: Path) -> None:
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_A,
        metrics_payload={METRIC_F1: 79.6, METRIC_ACCURACY: 80.0},
    )
    result: list[MetricResultsShort] = aggregate_metric_results_short(
        filter_metric_keys=[METRIC_ACCURACY],
    )
    assert len(result) == 1
    assert result[0].metric_key == METRIC_ACCURACY


def test_filter_by_task_id(repo: Path) -> None:
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_A,
        metrics_payload={METRIC_F1: 79.6},
    )
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_B,
        metrics_payload={METRIC_F1: 82.1},
    )
    result: list[MetricResultsShort] = aggregate_metric_results_short(
        filter_task_ids=[TASK_B],
    )
    assert len(result) == 1
    assert result[0].entries[0].task_id == TASK_B


# ---------------------------------------------------------------------------
# Null values
# ---------------------------------------------------------------------------


def test_null_values_included(repo: Path) -> None:
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_A,
        metrics_payload={METRIC_F1: None},
    )
    result: list[MetricResultsShort] = aggregate_metric_results_short()
    assert len(result) == 1
    assert result[0].entries[0].value is None


# ---------------------------------------------------------------------------
# Full with metric definitions
# ---------------------------------------------------------------------------


def test_full_joins_metric_definitions(repo: Path) -> None:
    build_metric(
        repo_root=repo,
        metric_key=METRIC_F1,
        name="F1 ALL",
        unit="f1",
        value_type="float",
        is_key=True,
        emoji="\u2b50",
    )
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_A,
        metrics_payload={METRIC_F1: 79.6},
    )
    result: list[MetricResultsFull] = aggregate_metric_results_full()
    assert len(result) == 1
    assert result[0].metric_name == "F1 ALL"
    assert result[0].unit == "f1"
    assert result[0].is_key is True
    assert result[0].emoji == "\u2b50"


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------


def test_sorted_by_metric_key(repo: Path) -> None:
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_A,
        metrics_payload={"z_metric": 1.0, "a_metric": 2.0},
    )
    result: list[MetricResultsShort] = aggregate_metric_results_short()
    keys: list[str] = [r.metric_key for r in result]
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_malformed_metrics_json_skipped(repo: Path) -> None:
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_A,
        metrics_payload={METRIC_F1: 79.6},
    )
    # Create a task with malformed metrics.json
    bad_dir: Path = repo / "tasks" / TASK_B / "results"
    bad_dir.mkdir(parents=True, exist_ok=True)
    (bad_dir / "metrics.json").write_text("{invalid", encoding="utf-8")

    result: list[MetricResultsShort] = aggregate_metric_results_short()
    assert len(result) == 1
    assert result[0].entries[0].task_id == TASK_A


def test_task_without_metrics_json_skipped(repo: Path) -> None:
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_A,
        metrics_payload=None,
    )
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_B,
        metrics_payload={METRIC_F1: 82.1},
    )
    result: list[MetricResultsShort] = aggregate_metric_results_short()
    assert len(result) == 1
    assert result[0].entries[0].task_id == TASK_B


def test_empty_metrics_json_returns_no_entries(repo: Path) -> None:
    _build_task_with_metrics(
        repo_root=repo,
        task_id=TASK_A,
        metrics_payload={},
    )
    result: list[MetricResultsShort] = aggregate_metric_results_short()
    assert len(result) == 0
