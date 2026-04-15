"""Tests for meta.asset_types.answer.aggregator."""

from pathlib import Path

import pytest

import meta.asset_types.answer.aggregator as agg_mod
from arf.tests.fixtures.asset_builders.answer import build_answer_asset
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import build_complete_task
from meta.asset_types.answer.aggregator import (
    AnswerInfoFull,
    AnswerInfoShort,
    aggregate_answers_full,
    aggregate_answers_short,
)

TASK_A: str = "t0001_alpha"
TASK_B: str = "t0002_bravo"
ANSWER_A: str = "what-is-wsd"
ANSWER_B: str = "best-baseline"
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


def test_empty_returns_no_answers_short(repo: Path) -> None:
    result: list[AnswerInfoShort] = aggregate_answers_short()
    assert len(result) == 0


def test_empty_returns_no_answers_full(repo: Path) -> None:
    result: list[AnswerInfoFull] = aggregate_answers_full()
    assert len(result) == 0


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_discovers_answers_across_tasks(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_complete_task(repo_root=repo, task_id=TASK_B, task_index=2)
    build_answer_asset(
        repo_root=repo,
        task_id=TASK_A,
        answer_id=ANSWER_A,
    )
    build_answer_asset(
        repo_root=repo,
        task_id=TASK_B,
        answer_id=ANSWER_B,
    )

    result: list[AnswerInfoShort] = aggregate_answers_short()
    ids: list[str] = [a.answer_id for a in result]

    assert ANSWER_A in ids
    assert ANSWER_B in ids
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Short vs full
# ---------------------------------------------------------------------------


def test_full_has_more_fields_than_short(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_answer_asset(repo_root=repo, task_id=TASK_A, answer_id=ANSWER_A)

    short: list[AnswerInfoShort] = aggregate_answers_short()
    full: list[AnswerInfoFull] = aggregate_answers_full()

    assert len(short) == 1
    assert len(full) == 1
    assert hasattr(full[0], "question")
    assert hasattr(full[0], "short_answer")


# ---------------------------------------------------------------------------
# Filtering by category
# ---------------------------------------------------------------------------


def test_filter_by_category(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_answer_asset(
        repo_root=repo,
        task_id=TASK_A,
        answer_id=ANSWER_A,
        categories=[CATEGORY_WSD],
    )
    build_answer_asset(
        repo_root=repo,
        task_id=TASK_A,
        answer_id=ANSWER_B,
        categories=[CATEGORY_NLP],
    )

    result: list[AnswerInfoShort] = aggregate_answers_short(
        filter_categories=[CATEGORY_WSD],
    )
    assert len(result) == 1
    assert result[0].answer_id == ANSWER_A


# ---------------------------------------------------------------------------
# Filtering by ID
# ---------------------------------------------------------------------------


def test_filter_by_id(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_answer_asset(
        repo_root=repo,
        task_id=TASK_A,
        answer_id=ANSWER_A,
    )
    build_answer_asset(
        repo_root=repo,
        task_id=TASK_A,
        answer_id=ANSWER_B,
    )

    result: list[AnswerInfoShort] = aggregate_answers_short(
        filter_ids=[ANSWER_B],
    )
    assert len(result) == 1
    assert result[0].answer_id == ANSWER_B


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_malformed_details_json_skipped(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_answer_asset(repo_root=repo, task_id=TASK_A, answer_id=ANSWER_A)

    bad_dir: Path = repo / "tasks" / TASK_A / "assets" / "answer" / "bad-answer"
    bad_dir.mkdir(parents=True, exist_ok=True)
    (bad_dir / "details.json").write_text("{invalid", encoding="utf-8")

    result: list[AnswerInfoShort] = aggregate_answers_short()
    ids: list[str] = [a.answer_id for a in result]
    assert ANSWER_A in ids
    assert "bad-answer" not in ids
