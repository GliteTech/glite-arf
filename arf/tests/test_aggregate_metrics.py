"""Tests for arf.scripts.aggregators.aggregate_metrics."""

from pathlib import Path

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

METRIC_F1: str = "f1_all"
METRIC_ACCURACY: str = "accuracy"
METRIC_LATENCY: str = "latency_ms"


@pytest.fixture()
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        aggregator_modules=[agg_mod],
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------


def test_empty_returns_no_metrics_short(repo: Path) -> None:
    result: list[MetricInfoShort] = aggregate_metrics_short()
    assert len(result) == 0


def test_empty_returns_no_metrics_full(repo: Path) -> None:
    result: list[MetricInfoFull] = aggregate_metrics_full()
    assert len(result) == 0


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_discovers_multiple_metrics(repo: Path) -> None:
    build_metric(
        repo_root=repo,
        metric_key=METRIC_F1,
        name="F1 ALL",
        unit="f1",
    )
    build_metric(
        repo_root=repo,
        metric_key=METRIC_ACCURACY,
        name="Accuracy",
        unit="percent",
    )

    result: list[MetricInfoShort] = aggregate_metrics_short()
    keys: list[str] = [m.metric_key for m in result]

    assert METRIC_F1 in keys
    assert METRIC_ACCURACY in keys
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Short vs full
# ---------------------------------------------------------------------------


def test_full_has_more_fields_than_short(repo: Path) -> None:
    build_metric(repo_root=repo, metric_key=METRIC_F1)

    short: list[MetricInfoShort] = aggregate_metrics_short()
    full: list[MetricInfoFull] = aggregate_metrics_full()

    assert len(short) == 1
    assert len(full) == 1
    assert hasattr(full[0], "description")
    assert hasattr(full[0], "datasets")
    assert not hasattr(short[0], "description")


def test_metric_fields_populated(repo: Path) -> None:
    build_metric(
        repo_root=repo,
        metric_key=METRIC_F1,
        name="F1 ALL",
        unit="f1",
        value_type="float",
        description="Micro-averaged F1 score across all datasets.",
    )

    result: list[MetricInfoFull] = aggregate_metrics_full()
    assert len(result) == 1

    m: MetricInfoFull = result[0]
    assert m.metric_key == METRIC_F1
    assert m.name == "F1 ALL"
    assert m.unit == "f1"
    assert m.value_type == "float"


# ---------------------------------------------------------------------------
# Filtering by ID
# ---------------------------------------------------------------------------


def test_filter_by_id(repo: Path) -> None:
    build_metric(repo_root=repo, metric_key=METRIC_F1)
    build_metric(repo_root=repo, metric_key=METRIC_ACCURACY)

    result: list[MetricInfoShort] = aggregate_metrics_short(
        filter_ids=[METRIC_ACCURACY],
    )
    assert len(result) == 1
    assert result[0].metric_key == METRIC_ACCURACY


# ---------------------------------------------------------------------------
# Filtering by unit
# ---------------------------------------------------------------------------


def test_filter_by_unit(repo: Path) -> None:
    build_metric(
        repo_root=repo,
        metric_key=METRIC_F1,
        unit="f1",
    )
    build_metric(
        repo_root=repo,
        metric_key=METRIC_LATENCY,
        unit="milliseconds",
        value_type="float",
    )

    result: list[MetricInfoShort] = aggregate_metrics_short(
        filter_unit=["f1"],
    )
    assert len(result) == 1
    assert result[0].metric_key == METRIC_F1


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_malformed_definition_json_skipped(repo: Path) -> None:
    build_metric(repo_root=repo, metric_key=METRIC_F1)

    bad_dir: Path = repo / "meta" / "metrics" / "bad-metric"
    bad_dir.mkdir(parents=True, exist_ok=True)
    (bad_dir / "definition.json").write_text("{invalid", encoding="utf-8")

    result: list[MetricInfoShort] = aggregate_metrics_short()
    keys: list[str] = [m.metric_key for m in result]
    assert METRIC_F1 in keys
    assert "bad-metric" not in keys


def test_sorted_alphabetically(repo: Path) -> None:
    build_metric(repo_root=repo, metric_key=METRIC_LATENCY, unit="ms")
    build_metric(repo_root=repo, metric_key=METRIC_ACCURACY, unit="percent")
    build_metric(repo_root=repo, metric_key=METRIC_F1, unit="f1")

    result: list[MetricInfoShort] = aggregate_metrics_short()
    keys: list[str] = [m.metric_key for m in result]
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# Key metrics fields
# ---------------------------------------------------------------------------


def test_is_key_field_present_in_full(repo: Path) -> None:
    build_metric(
        repo_root=repo,
        metric_key=METRIC_F1,
        is_key=True,
        emoji="\u2b50",
    )
    result: list[MetricInfoFull] = aggregate_metrics_full()
    assert len(result) == 1
    assert result[0].is_key is True
    assert result[0].emoji == "\u2b50"


def test_is_key_defaults_to_false(repo: Path) -> None:
    build_metric(repo_root=repo, metric_key=METRIC_F1)
    result: list[MetricInfoFull] = aggregate_metrics_full()
    assert len(result) == 1
    assert result[0].is_key is False


def test_emoji_defaults_to_none(repo: Path) -> None:
    build_metric(repo_root=repo, metric_key=METRIC_F1)
    result: list[MetricInfoFull] = aggregate_metrics_full()
    assert len(result) == 1
    assert result[0].emoji is None


def test_is_key_in_short(repo: Path) -> None:
    build_metric(
        repo_root=repo,
        metric_key=METRIC_F1,
        is_key=True,
        emoji="\u2b50",
    )
    result: list[MetricInfoShort] = aggregate_metrics_short()
    assert len(result) == 1
    assert result[0].is_key is True
    assert result[0].emoji == "\u2b50"
