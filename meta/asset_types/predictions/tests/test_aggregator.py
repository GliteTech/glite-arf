"""Tests for meta.asset_types.predictions.aggregator."""

from pathlib import Path

import pytest

import meta.asset_types.predictions.aggregator as agg_mod
from arf.tests.fixtures.asset_builders.predictions import build_predictions_asset
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import build_complete_task
from meta.asset_types.predictions.aggregator import (
    PredictionsInfoFull,
    PredictionsInfoShort,
    aggregate_predictions_full,
    aggregate_predictions_short,
)

TASK_A: str = "t0001_alpha"
TASK_B: str = "t0002_bravo"
PRED_A: str = "bert-wsd-raganato"
PRED_B: str = "deberta-wsd-semeval"
CATEGORY_WSD: str = "wsd-evaluation"
CATEGORY_NLP: str = "nlp-general"


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


def test_empty_returns_no_predictions_short(repo: Path) -> None:
    result: list[PredictionsInfoShort] = aggregate_predictions_short()
    assert len(result) == 0


def test_empty_returns_no_predictions_full(repo: Path) -> None:
    result: list[PredictionsInfoFull] = aggregate_predictions_full()
    assert len(result) == 0


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_discovers_predictions_across_tasks(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_complete_task(repo_root=repo, task_id=TASK_B, task_index=2)
    build_predictions_asset(
        repo_root=repo,
        task_id=TASK_A,
        predictions_id=PRED_A,
        name="BERT WSD Raganato",
    )
    build_predictions_asset(
        repo_root=repo,
        task_id=TASK_B,
        predictions_id=PRED_B,
        name="DeBERTa WSD SemEval",
    )

    result: list[PredictionsInfoShort] = aggregate_predictions_short()
    ids: list[str] = [p.predictions_id for p in result]

    assert PRED_A in ids
    assert PRED_B in ids
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Short vs full
# ---------------------------------------------------------------------------


def test_full_has_more_fields_than_short(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_predictions_asset(
        repo_root=repo,
        task_id=TASK_A,
        predictions_id=PRED_A,
    )

    short: list[PredictionsInfoShort] = aggregate_predictions_short()
    full: list[PredictionsInfoFull] = aggregate_predictions_full()

    assert len(short) == 1
    assert len(full) == 1
    assert hasattr(full[0], "prediction_format")
    assert hasattr(full[0], "instance_count")


# ---------------------------------------------------------------------------
# Filtering by category
# ---------------------------------------------------------------------------


def test_filter_by_category(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_predictions_asset(
        repo_root=repo,
        task_id=TASK_A,
        predictions_id=PRED_A,
        categories=[CATEGORY_WSD],
    )
    build_predictions_asset(
        repo_root=repo,
        task_id=TASK_A,
        predictions_id=PRED_B,
        categories=[CATEGORY_NLP],
    )

    result: list[PredictionsInfoShort] = aggregate_predictions_short(
        filter_categories=[CATEGORY_WSD],
    )
    assert len(result) == 1
    assert result[0].predictions_id == PRED_A


# ---------------------------------------------------------------------------
# Filtering by ID
# ---------------------------------------------------------------------------


def test_filter_by_id(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_predictions_asset(
        repo_root=repo,
        task_id=TASK_A,
        predictions_id=PRED_A,
    )
    build_predictions_asset(
        repo_root=repo,
        task_id=TASK_A,
        predictions_id=PRED_B,
    )

    result: list[PredictionsInfoShort] = aggregate_predictions_short(
        filter_ids=[PRED_B],
    )
    assert len(result) == 1
    assert result[0].predictions_id == PRED_B


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_malformed_details_json_skipped(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_predictions_asset(
        repo_root=repo,
        task_id=TASK_A,
        predictions_id=PRED_A,
    )

    bad_dir: Path = repo / "tasks" / TASK_A / "assets" / "predictions" / "bad-pred"
    bad_dir.mkdir(parents=True, exist_ok=True)
    (bad_dir / "details.json").write_text("{invalid", encoding="utf-8")

    result: list[PredictionsInfoShort] = aggregate_predictions_short()
    ids: list[str] = [p.predictions_id for p in result]
    assert PRED_A in ids
    assert "bad-pred" not in ids
