"""Tests for meta.asset_types.paper.aggregator."""

from pathlib import Path

import pytest

import meta.asset_types.paper.aggregator as agg_mod
from arf.tests.fixtures.asset_builders.paper import build_paper_asset
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import build_complete_task
from meta.asset_types.paper.aggregator import (
    PaperInfoFull,
    PaperInfoShort,
    aggregate_papers_full,
    aggregate_papers_short,
)

TASK_A: str = "t0001_alpha"
TASK_B: str = "t0002_bravo"
PAPER_A: str = "10.1234_test-paper-a"
PAPER_B: str = "10.5678_test-paper-b"
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


def test_empty_returns_no_papers_short(repo: Path) -> None:
    result: list[PaperInfoShort] = aggregate_papers_short()
    assert len(result) == 0


def test_empty_returns_no_papers_full(repo: Path) -> None:
    result: list[PaperInfoFull] = aggregate_papers_full()
    assert len(result) == 0


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_discovers_papers_across_tasks(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_complete_task(repo_root=repo, task_id=TASK_B, task_index=2)
    build_paper_asset(
        repo_root=repo,
        task_id=TASK_A,
        paper_id=PAPER_A,
        title="Paper A",
    )
    build_paper_asset(
        repo_root=repo,
        task_id=TASK_B,
        paper_id=PAPER_B,
        title="Paper B",
    )

    result: list[PaperInfoShort] = aggregate_papers_short()
    ids: list[str] = [p.paper_id for p in result]

    assert PAPER_A in ids
    assert PAPER_B in ids
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Short vs full
# ---------------------------------------------------------------------------


def test_full_has_more_fields_than_short(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_paper_asset(repo_root=repo, task_id=TASK_A, paper_id=PAPER_A)

    short: list[PaperInfoShort] = aggregate_papers_short()
    full: list[PaperInfoFull] = aggregate_papers_full()

    assert len(short) == 1
    assert len(full) == 1
    assert hasattr(full[0], "abstract")
    assert hasattr(full[0], "doi")
    assert not hasattr(short[0], "abstract")


def test_include_full_summary_flag(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_paper_asset(repo_root=repo, task_id=TASK_A, paper_id=PAPER_A)

    without: list[PaperInfoFull] = aggregate_papers_full(
        include_full_summary=False,
    )
    with_summary: list[PaperInfoFull] = aggregate_papers_full(
        include_full_summary=True,
    )

    assert len(without) == 1
    assert len(with_summary) == 1
    assert without[0].full_summary is None
    # with_summary may or may not have full_summary depending on file content


# ---------------------------------------------------------------------------
# Filtering by category
# ---------------------------------------------------------------------------


def test_filter_by_category(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_paper_asset(
        repo_root=repo,
        task_id=TASK_A,
        paper_id=PAPER_A,
        categories=[CATEGORY_WSD],
    )
    build_paper_asset(
        repo_root=repo,
        task_id=TASK_A,
        paper_id=PAPER_B,
        categories=[CATEGORY_NLP],
    )

    result: list[PaperInfoShort] = aggregate_papers_short(
        filter_categories=[CATEGORY_WSD],
    )
    assert len(result) == 1
    assert result[0].paper_id == PAPER_A


# ---------------------------------------------------------------------------
# Filtering by ID
# ---------------------------------------------------------------------------


def test_filter_by_id(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_paper_asset(
        repo_root=repo,
        task_id=TASK_A,
        paper_id=PAPER_A,
    )
    build_paper_asset(
        repo_root=repo,
        task_id=TASK_A,
        paper_id=PAPER_B,
    )

    result: list[PaperInfoShort] = aggregate_papers_short(
        filter_ids=[PAPER_B],
    )
    assert len(result) == 1
    assert result[0].paper_id == PAPER_B


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_malformed_details_json_skipped(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_paper_asset(repo_root=repo, task_id=TASK_A, paper_id=PAPER_A)

    # Create a malformed paper
    bad_dir: Path = repo / "tasks" / TASK_A / "assets" / "paper" / "bad-paper"
    bad_dir.mkdir(parents=True, exist_ok=True)
    (bad_dir / "details.json").write_text("{invalid", encoding="utf-8")

    result: list[PaperInfoShort] = aggregate_papers_short()
    ids: list[str] = [p.paper_id for p in result]
    assert PAPER_A in ids
    assert "bad-paper" not in ids
