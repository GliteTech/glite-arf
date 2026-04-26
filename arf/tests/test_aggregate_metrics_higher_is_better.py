import json
from pathlib import Path
from typing import Any

import pytest

import arf.scripts.aggregators.aggregate_metrics as agg_mod
from arf.scripts.aggregators.aggregate_metrics import (
    MetricInfoFull,
    MetricInfoShort,
    aggregate_metrics_full,
    aggregate_metrics_short,
)
from arf.tests.fixtures.metadata_builders import build_metric
from arf.tests.fixtures.paths import configure_repo_paths

METRIC_FOO: str = "foo"


@pytest.fixture()
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        aggregator_modules=[agg_mod],
    )
    return tmp_path


def test_metric_info_full_exposes_higher_is_better(repo: Path) -> None:
    build_metric(
        repo_root=repo,
        metric_key=METRIC_FOO,
        overrides={"higher_is_better": False},
    )
    result: list[MetricInfoFull] = aggregate_metrics_full()
    assert len(result) == 1
    assert result[0].higher_is_better is False


def test_metric_info_full_higher_is_better_true(repo: Path) -> None:
    build_metric(
        repo_root=repo,
        metric_key=METRIC_FOO,
        overrides={"higher_is_better": True},
    )
    result: list[MetricInfoFull] = aggregate_metrics_full()
    assert len(result) == 1
    assert result[0].higher_is_better is True


def test_metric_info_short_exposes_higher_is_better(repo: Path) -> None:
    build_metric(
        repo_root=repo,
        metric_key=METRIC_FOO,
        overrides={"higher_is_better": False},
    )
    result: list[MetricInfoShort] = aggregate_metrics_short()
    assert len(result) == 1
    assert result[0].higher_is_better is False


def test_json_output_full_contains_higher_is_better(repo: Path) -> None:
    build_metric(
        repo_root=repo,
        metric_key=METRIC_FOO,
        overrides={"higher_is_better": False},
    )
    full_metrics: list[MetricInfoFull] = aggregate_metrics_full()
    raw_json: str = agg_mod._format_full_json(metrics=full_metrics)
    payload: Any = json.loads(raw_json)
    assert isinstance(payload, dict)
    assert payload["metric_count"] == 1
    entry: dict[str, Any] = payload["metrics"][0]
    assert "higher_is_better" in entry, f"Keys present: {list(entry.keys())}"
    assert entry["higher_is_better"] is False


def test_json_output_short_contains_higher_is_better(repo: Path) -> None:
    build_metric(
        repo_root=repo,
        metric_key=METRIC_FOO,
        overrides={"higher_is_better": True},
    )
    short_metrics: list[MetricInfoShort] = aggregate_metrics_short()
    raw_json: str = agg_mod._format_short_json(metrics=short_metrics)
    payload: Any = json.loads(raw_json)
    assert isinstance(payload, dict)
    entry: dict[str, Any] = payload["metrics"][0]
    assert "higher_is_better" in entry, f"Keys present: {list(entry.keys())}"
    assert entry["higher_is_better"] is True
