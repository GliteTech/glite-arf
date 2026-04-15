"""Tests for meta.asset_types.dataset.aggregator."""

from pathlib import Path

import pytest

import meta.asset_types.dataset.aggregator as agg_mod
from arf.tests.fixtures.asset_builders.dataset import build_dataset_asset
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import build_complete_task
from meta.asset_types.dataset.aggregator import (
    DatasetInfoFull,
    DatasetInfoShort,
    aggregate_datasets_full,
    aggregate_datasets_short,
)

TASK_A: str = "t0001_alpha"
TASK_B: str = "t0002_bravo"
DATASET_A: str = "raganato-all"
DATASET_B: str = "semcor-train"
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


def test_empty_returns_no_datasets_short(repo: Path) -> None:
    result: list[DatasetInfoShort] = aggregate_datasets_short()
    assert len(result) == 0


def test_empty_returns_no_datasets_full(repo: Path) -> None:
    result: list[DatasetInfoFull] = aggregate_datasets_full()
    assert len(result) == 0


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_discovers_datasets_across_tasks(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_complete_task(repo_root=repo, task_id=TASK_B, task_index=2)
    build_dataset_asset(
        repo_root=repo,
        task_id=TASK_A,
        dataset_id=DATASET_A,
        name="Raganato ALL",
    )
    build_dataset_asset(
        repo_root=repo,
        task_id=TASK_B,
        dataset_id=DATASET_B,
        name="SemCor Train",
    )

    result: list[DatasetInfoShort] = aggregate_datasets_short()
    ids: list[str] = [d.dataset_id for d in result]

    assert DATASET_A in ids
    assert DATASET_B in ids
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Short vs full
# ---------------------------------------------------------------------------


def test_full_has_more_fields_than_short(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_dataset_asset(repo_root=repo, task_id=TASK_A, dataset_id=DATASET_A)

    short: list[DatasetInfoShort] = aggregate_datasets_short()
    full: list[DatasetInfoFull] = aggregate_datasets_full()

    assert len(short) == 1
    assert len(full) == 1
    assert hasattr(full[0], "url")
    assert hasattr(full[0], "license")


# ---------------------------------------------------------------------------
# Filtering by category
# ---------------------------------------------------------------------------


def test_filter_by_category(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_dataset_asset(
        repo_root=repo,
        task_id=TASK_A,
        dataset_id=DATASET_A,
        categories=[CATEGORY_WSD],
    )
    build_dataset_asset(
        repo_root=repo,
        task_id=TASK_A,
        dataset_id=DATASET_B,
        categories=[CATEGORY_NLP],
    )

    result: list[DatasetInfoShort] = aggregate_datasets_short(
        filter_categories=[CATEGORY_WSD],
    )
    assert len(result) == 1
    assert result[0].dataset_id == DATASET_A


# ---------------------------------------------------------------------------
# Filtering by ID
# ---------------------------------------------------------------------------


def test_filter_by_id(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_dataset_asset(
        repo_root=repo,
        task_id=TASK_A,
        dataset_id=DATASET_A,
    )
    build_dataset_asset(
        repo_root=repo,
        task_id=TASK_A,
        dataset_id=DATASET_B,
    )

    result: list[DatasetInfoShort] = aggregate_datasets_short(
        filter_ids=[DATASET_B],
    )
    assert len(result) == 1
    assert result[0].dataset_id == DATASET_B


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_malformed_details_json_skipped(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_dataset_asset(repo_root=repo, task_id=TASK_A, dataset_id=DATASET_A)

    bad_dir: Path = repo / "tasks" / TASK_A / "assets" / "dataset" / "bad-ds"
    bad_dir.mkdir(parents=True, exist_ok=True)
    (bad_dir / "details.json").write_text("{invalid", encoding="utf-8")

    result: list[DatasetInfoShort] = aggregate_datasets_short()
    ids: list[str] = [d.dataset_id for d in result]
    assert DATASET_A in ids
    assert "bad-ds" not in ids
