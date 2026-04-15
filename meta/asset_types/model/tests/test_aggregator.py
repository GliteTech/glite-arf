"""Tests for meta.asset_types.model.aggregator."""

from pathlib import Path

import pytest

import meta.asset_types.model.aggregator as agg_mod
from arf.tests.fixtures.asset_builders.model import build_model_asset
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import build_complete_task
from meta.asset_types.model.aggregator import (
    ModelInfoFull,
    ModelInfoShort,
    aggregate_models_full,
    aggregate_models_short,
)

TASK_A: str = "t0001_alpha"
TASK_B: str = "t0002_bravo"
MODEL_A: str = "bert-wsd-v1"
MODEL_B: str = "deberta-wsd-v1"
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


def test_empty_returns_no_models_short(repo: Path) -> None:
    result: list[ModelInfoShort] = aggregate_models_short()
    assert len(result) == 0


def test_empty_returns_no_models_full(repo: Path) -> None:
    result: list[ModelInfoFull] = aggregate_models_full()
    assert len(result) == 0


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_discovers_models_across_tasks(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_complete_task(repo_root=repo, task_id=TASK_B, task_index=2)
    build_model_asset(
        repo_root=repo,
        task_id=TASK_A,
        model_id=MODEL_A,
        name="BERT WSD v1",
    )
    build_model_asset(
        repo_root=repo,
        task_id=TASK_B,
        model_id=MODEL_B,
        name="DeBERTa WSD v1",
    )

    result: list[ModelInfoShort] = aggregate_models_short()
    ids: list[str] = [m.model_id for m in result]

    assert MODEL_A in ids
    assert MODEL_B in ids
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Short vs full
# ---------------------------------------------------------------------------


def test_full_has_more_fields_than_short(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_model_asset(repo_root=repo, task_id=TASK_A, model_id=MODEL_A)

    short: list[ModelInfoShort] = aggregate_models_short()
    full: list[ModelInfoFull] = aggregate_models_full()

    assert len(short) == 1
    assert len(full) == 1
    assert hasattr(full[0], "architecture")
    assert hasattr(full[0], "hyperparameters")


# ---------------------------------------------------------------------------
# Filtering by category
# ---------------------------------------------------------------------------


def test_filter_by_category(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_model_asset(
        repo_root=repo,
        task_id=TASK_A,
        model_id=MODEL_A,
        categories=[CATEGORY_WSD],
    )
    build_model_asset(
        repo_root=repo,
        task_id=TASK_A,
        model_id=MODEL_B,
        categories=[CATEGORY_NLP],
    )

    result: list[ModelInfoShort] = aggregate_models_short(
        filter_categories=[CATEGORY_WSD],
    )
    assert len(result) == 1
    assert result[0].model_id == MODEL_A


# ---------------------------------------------------------------------------
# Filtering by ID
# ---------------------------------------------------------------------------


def test_filter_by_id(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_model_asset(
        repo_root=repo,
        task_id=TASK_A,
        model_id=MODEL_A,
    )
    build_model_asset(
        repo_root=repo,
        task_id=TASK_A,
        model_id=MODEL_B,
    )

    result: list[ModelInfoShort] = aggregate_models_short(
        filter_ids=[MODEL_B],
    )
    assert len(result) == 1
    assert result[0].model_id == MODEL_B


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_malformed_details_json_skipped(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_model_asset(repo_root=repo, task_id=TASK_A, model_id=MODEL_A)

    bad_dir: Path = repo / "tasks" / TASK_A / "assets" / "model" / "bad-model"
    bad_dir.mkdir(parents=True, exist_ok=True)
    (bad_dir / "details.json").write_text("{invalid", encoding="utf-8")

    result: list[ModelInfoShort] = aggregate_models_short()
    ids: list[str] = [m.model_id for m in result]
    assert MODEL_A in ids
    assert "bad-model" not in ids
