"""Tests for meta.asset_types.library.aggregator."""

from pathlib import Path

import pytest

import meta.asset_types.library.aggregator as agg_mod
from arf.tests.fixtures.asset_builders.library import build_library_asset
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import build_complete_task
from meta.asset_types.library.aggregator import (
    LibraryInfoFull,
    LibraryInfoShort,
    aggregate_libraries_full,
    aggregate_libraries_short,
)

TASK_A: str = "t0001_alpha"
TASK_B: str = "t0002_bravo"
LIB_A: str = "wsd-loader"
LIB_B: str = "wsd-scorer"
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


def test_empty_returns_no_libraries_short(repo: Path) -> None:
    result: list[LibraryInfoShort] = aggregate_libraries_short()
    assert len(result) == 0


def test_empty_returns_no_libraries_full(repo: Path) -> None:
    result: list[LibraryInfoFull] = aggregate_libraries_full()
    assert len(result) == 0


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_discovers_libraries_across_tasks(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_complete_task(repo_root=repo, task_id=TASK_B, task_index=2)
    build_library_asset(
        repo_root=repo,
        task_id=TASK_A,
        library_id=LIB_A,
        name="WSD Loader",
    )
    build_library_asset(
        repo_root=repo,
        task_id=TASK_B,
        library_id=LIB_B,
        name="WSD Scorer",
    )

    result: list[LibraryInfoShort] = aggregate_libraries_short()
    ids: list[str] = [lib.library_id for lib in result]

    assert LIB_A in ids
    assert LIB_B in ids
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Short vs full
# ---------------------------------------------------------------------------


def test_full_has_more_fields_than_short(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_library_asset(repo_root=repo, task_id=TASK_A, library_id=LIB_A)

    short: list[LibraryInfoShort] = aggregate_libraries_short()
    full: list[LibraryInfoFull] = aggregate_libraries_full()

    assert len(short) == 1
    assert len(full) == 1
    assert hasattr(full[0], "entry_points")
    assert hasattr(full[0], "dependencies")


# ---------------------------------------------------------------------------
# Filtering by category
# ---------------------------------------------------------------------------


def test_filter_by_category(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_library_asset(
        repo_root=repo,
        task_id=TASK_A,
        library_id=LIB_A,
        categories=[CATEGORY_WSD],
    )
    build_library_asset(
        repo_root=repo,
        task_id=TASK_A,
        library_id=LIB_B,
        categories=[CATEGORY_NLP],
    )

    result: list[LibraryInfoShort] = aggregate_libraries_short(
        filter_categories=[CATEGORY_WSD],
    )
    assert len(result) == 1
    assert result[0].library_id == LIB_A


# ---------------------------------------------------------------------------
# Filtering by ID
# ---------------------------------------------------------------------------


def test_filter_by_id(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_library_asset(
        repo_root=repo,
        task_id=TASK_A,
        library_id=LIB_A,
    )
    build_library_asset(
        repo_root=repo,
        task_id=TASK_A,
        library_id=LIB_B,
    )

    result: list[LibraryInfoShort] = aggregate_libraries_short(
        filter_ids=[LIB_B],
    )
    assert len(result) == 1
    assert result[0].library_id == LIB_B


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_malformed_details_json_skipped(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_library_asset(repo_root=repo, task_id=TASK_A, library_id=LIB_A)

    bad_dir: Path = repo / "tasks" / TASK_A / "assets" / "library" / "bad-lib"
    bad_dir.mkdir(parents=True, exist_ok=True)
    (bad_dir / "details.json").write_text("{invalid", encoding="utf-8")

    result: list[LibraryInfoShort] = aggregate_libraries_short()
    ids: list[str] = [lib.library_id for lib in result]
    assert LIB_A in ids
    assert "bad-lib" not in ids
