"""Tests for arf.scripts.aggregators.aggregate_suggestions."""

from pathlib import Path

import pytest

import arf.scripts.aggregators.aggregate_suggestions as agg_mod
from arf.scripts.aggregators.aggregate_suggestions import (
    SuggestionInfoFull,
    SuggestionInfoShort,
    aggregate_suggestions_full,
    aggregate_suggestions_short,
    collect_covered_suggestion_ids,
    collect_suggestion_task_map,
)
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.suggestion_builder import (
    build_suggestion,
    build_suggestions_file,
)
from arf.tests.fixtures.task_builder import build_complete_task, build_task_json

TASK_A: str = "t0001_alpha"
TASK_B: str = "t0002_bravo"
SUGGESTION_A: str = "S-0001-01"
SUGGESTION_B: str = "S-0002-01"
KIND_EXPERIMENT: str = "experiment"
KIND_DATASET: str = "dataset_download"
CATEGORY_WSD: str = "wsd-evaluation"


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


def test_empty_returns_no_suggestions_short(repo: Path) -> None:
    result: list[SuggestionInfoShort] = aggregate_suggestions_short()
    assert len(result) == 0


def test_empty_returns_no_suggestions_full(repo: Path) -> None:
    result: list[SuggestionInfoFull] = aggregate_suggestions_full()
    assert len(result) == 0


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_discovers_suggestions_across_tasks(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_complete_task(repo_root=repo, task_id=TASK_B, task_index=2)
    build_suggestions_file(
        repo_root=repo,
        task_id=TASK_A,
        suggestions=[
            build_suggestion(
                suggestion_id=SUGGESTION_A,
                source_task=TASK_A,
                kind=KIND_EXPERIMENT,
            ),
        ],
    )
    build_suggestions_file(
        repo_root=repo,
        task_id=TASK_B,
        suggestions=[
            build_suggestion(
                suggestion_id=SUGGESTION_B,
                source_task=TASK_B,
                kind=KIND_DATASET,
            ),
        ],
    )

    result: list[SuggestionInfoShort] = aggregate_suggestions_short()
    ids: list[str] = [s.id for s in result]

    assert SUGGESTION_A in ids
    assert SUGGESTION_B in ids
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Short vs full
# ---------------------------------------------------------------------------


def test_full_has_description(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_suggestions_file(
        repo_root=repo,
        task_id=TASK_A,
        suggestions=[
            build_suggestion(suggestion_id=SUGGESTION_A, source_task=TASK_A),
        ],
    )

    short: list[SuggestionInfoShort] = aggregate_suggestions_short()
    full: list[SuggestionInfoFull] = aggregate_suggestions_full()

    assert len(short) == 1
    assert len(full) == 1
    assert hasattr(full[0], "description")
    assert not hasattr(short[0], "description")


# ---------------------------------------------------------------------------
# Filtering by kind
# ---------------------------------------------------------------------------


def test_filter_by_kind(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_suggestions_file(
        repo_root=repo,
        task_id=TASK_A,
        suggestions=[
            build_suggestion(
                suggestion_id=SUGGESTION_A,
                source_task=TASK_A,
                kind=KIND_EXPERIMENT,
            ),
            build_suggestion(
                suggestion_id=SUGGESTION_B,
                source_task=TASK_A,
                kind=KIND_DATASET,
            ),
        ],
    )

    result: list[SuggestionInfoShort] = aggregate_suggestions_short(
        filter_kinds=[KIND_EXPERIMENT],
    )
    assert len(result) == 1
    assert result[0].id == SUGGESTION_A


# ---------------------------------------------------------------------------
# Filtering by ID
# ---------------------------------------------------------------------------


def test_filter_by_id(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_suggestions_file(
        repo_root=repo,
        task_id=TASK_A,
        suggestions=[
            build_suggestion(
                suggestion_id=SUGGESTION_A,
                source_task=TASK_A,
            ),
            build_suggestion(
                suggestion_id=SUGGESTION_B,
                source_task=TASK_A,
            ),
        ],
    )

    result: list[SuggestionInfoShort] = aggregate_suggestions_short(
        filter_ids=[SUGGESTION_B],
    )
    assert len(result) == 1
    assert result[0].id == SUGGESTION_B


# ---------------------------------------------------------------------------
# Filtering by category
# ---------------------------------------------------------------------------


def test_filter_by_category(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_suggestions_file(
        repo_root=repo,
        task_id=TASK_A,
        suggestions=[
            build_suggestion(
                suggestion_id=SUGGESTION_A,
                source_task=TASK_A,
                categories=[CATEGORY_WSD],
            ),
            build_suggestion(
                suggestion_id=SUGGESTION_B,
                source_task=TASK_A,
                categories=["other"],
            ),
        ],
    )

    result: list[SuggestionInfoShort] = aggregate_suggestions_short(
        filter_categories=[CATEGORY_WSD],
    )
    assert len(result) == 1
    assert result[0].id == SUGGESTION_A


# ---------------------------------------------------------------------------
# collect_suggestion_task_map / collect_covered_suggestion_ids
# ---------------------------------------------------------------------------


def test_collect_suggestion_task_map(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_task_json(
        repo_root=repo,
        task_id=TASK_A,
        task_index=1,
        source_suggestion=SUGGESTION_A,
    )

    mapping: dict[str, str] = collect_suggestion_task_map()
    assert mapping[SUGGESTION_A] == TASK_A


def test_collect_covered_suggestion_ids(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_task_json(
        repo_root=repo,
        task_id=TASK_A,
        task_index=1,
        source_suggestion=SUGGESTION_A,
    )

    covered: set[str] = collect_covered_suggestion_ids()
    assert SUGGESTION_A in covered
    assert SUGGESTION_B not in covered


def test_collect_suggestion_task_map_empty(repo: Path) -> None:
    mapping: dict[str, str] = collect_suggestion_task_map()
    assert len(mapping) == 0


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_malformed_suggestions_file_skipped(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_suggestions_file(
        repo_root=repo,
        task_id=TASK_A,
        suggestions=[
            build_suggestion(
                suggestion_id=SUGGESTION_A,
                source_task=TASK_A,
            ),
        ],
    )

    # Create a malformed suggestions file in another task
    build_complete_task(repo_root=repo, task_id=TASK_B, task_index=2)
    bad_path: Path = repo / "tasks" / TASK_B / "results" / "suggestions.json"
    bad_path.parent.mkdir(parents=True, exist_ok=True)
    bad_path.write_text("{invalid", encoding="utf-8")

    result: list[SuggestionInfoShort] = aggregate_suggestions_short()
    ids: list[str] = [s.id for s in result]
    assert SUGGESTION_A in ids
