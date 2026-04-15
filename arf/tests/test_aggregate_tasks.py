"""Tests for arf.scripts.aggregators.aggregate_tasks."""

from pathlib import Path

import pytest

import arf.scripts.aggregators.aggregate_tasks as agg_mod
import arf.scripts.common.task_description as task_desc_mod
from arf.scripts.aggregators.aggregate_tasks import (
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_NOT_STARTED,
    TaskInfoFull,
    TaskInfoShort,
    aggregate_tasks_full,
    aggregate_tasks_short,
)
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import (
    build_complete_task,
    build_task_json,
)

TASK_A: str = "t0001_alpha"
TASK_B: str = "t0002_bravo"
TASK_C: str = "t0003_charlie"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        aggregator_modules=[agg_mod, task_desc_mod],
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------


def test_empty_returns_no_tasks_short(repo: Path) -> None:
    result: list[TaskInfoShort] = aggregate_tasks_short()
    assert len(result) == 0


def test_empty_returns_no_tasks_full(repo: Path) -> None:
    result: list[TaskInfoFull] = aggregate_tasks_full()
    assert len(result) == 0


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_discovers_multiple_tasks(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_complete_task(repo_root=repo, task_id=TASK_B, task_index=2)

    result: list[TaskInfoShort] = aggregate_tasks_short()
    ids: list[str] = [t.task_id for t in result]

    assert TASK_A in ids
    assert TASK_B in ids
    assert len(result) == 2


def test_full_has_more_fields_than_short(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)

    short: list[TaskInfoShort] = aggregate_tasks_short()
    full: list[TaskInfoFull] = aggregate_tasks_full()

    assert len(short) == 1
    assert len(full) == 1
    assert hasattr(full[0], "long_description")
    assert hasattr(full[0], "results_summary")
    assert not hasattr(short[0], "long_description")


# ---------------------------------------------------------------------------
# Filtering by status
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("filter_status", "expected_count"),
    [
        ("completed", 1),
        ("in_progress", 1),
        ("not_started", 0),
    ],
)
def test_filter_by_status(
    repo: Path,
    filter_status: str,
    expected_count: int,
) -> None:
    build_complete_task(
        repo_root=repo,
        task_id=TASK_A,
        task_index=1,
        status="completed",
    )
    build_complete_task(
        repo_root=repo,
        task_id=TASK_B,
        task_index=2,
        status="in_progress",
    )

    result: list[TaskInfoShort] = aggregate_tasks_short(
        filter_statuses=[filter_status],
    )
    assert len(result) == expected_count


def test_filter_by_multiple_statuses(repo: Path) -> None:
    build_complete_task(
        repo_root=repo,
        task_id=TASK_A,
        task_index=1,
        status="completed",
    )
    build_complete_task(
        repo_root=repo,
        task_id=TASK_B,
        task_index=2,
        status="in_progress",
    )
    build_complete_task(
        repo_root=repo,
        task_id=TASK_C,
        task_index=3,
        status="not_started",
    )

    result: list[TaskInfoShort] = aggregate_tasks_short(
        filter_statuses=["completed", "in_progress"],
    )
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Filtering by ID
# ---------------------------------------------------------------------------


def test_filter_by_ids(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_complete_task(repo_root=repo, task_id=TASK_B, task_index=2)

    result: list[TaskInfoShort] = aggregate_tasks_short(
        filter_ids=[TASK_A],
    )
    assert len(result) == 1
    assert result[0].task_id == TASK_A


# ---------------------------------------------------------------------------
# Filtering by dependency
# ---------------------------------------------------------------------------


def test_filter_by_dependency(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_complete_task(repo_root=repo, task_id=TASK_B, task_index=2)
    build_task_json(
        repo_root=repo,
        task_id=TASK_B,
        task_index=2,
        dependencies=[TASK_A],
    )

    result: list[TaskInfoShort] = aggregate_tasks_short(
        filter_has_dependency=TASK_A,
    )
    assert len(result) == 1
    assert result[0].task_id == TASK_B


# ---------------------------------------------------------------------------
# Filtering by source suggestion
# ---------------------------------------------------------------------------


def test_filter_by_source_suggestion(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_task_json(
        repo_root=repo,
        task_id=TASK_A,
        task_index=1,
        source_suggestion="S-0010-01",
    )
    build_complete_task(repo_root=repo, task_id=TASK_B, task_index=2)

    result: list[TaskInfoShort] = aggregate_tasks_short(
        filter_source_suggestion="S-0010-01",
    )
    assert len(result) == 1
    assert result[0].task_id == TASK_A


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_malformed_task_json_skipped(repo: Path) -> None:
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    # Create a malformed task.json for TASK_B
    task_dir: Path = repo / "tasks" / TASK_B
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "task.json").write_text("not-valid-json", encoding="utf-8")

    result: list[TaskInfoShort] = aggregate_tasks_short()
    assert len(result) == 1
    assert result[0].task_id == TASK_A


# ---------------------------------------------------------------------------
# Worktree-aware status override (Layer 2 safety net)
# ---------------------------------------------------------------------------


def test_worktree_override_not_started_to_in_progress(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A not_started task with an active worktree reports as in_progress."""
    build_complete_task(
        repo_root=repo,
        task_id=TASK_A,
        task_index=1,
        status="not_started",
        task_json_overrides={"start_time": None, "end_time": None},
    )
    monkeypatch.setattr(
        agg_mod,
        "_get_active_worktree_task_ids",
        lambda: {TASK_A},
    )

    result_short: list[TaskInfoShort] = aggregate_tasks_short()
    assert len(result_short) == 1
    assert result_short[0].status == TASK_STATUS_IN_PROGRESS

    result_full: list[TaskInfoFull] = aggregate_tasks_full()
    assert len(result_full) == 1
    assert result_full[0].status == TASK_STATUS_IN_PROGRESS


def test_worktree_override_does_not_affect_completed(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A completed task with an active worktree keeps completed status."""
    build_complete_task(
        repo_root=repo,
        task_id=TASK_A,
        task_index=1,
        status="completed",
    )
    monkeypatch.setattr(
        agg_mod,
        "_get_active_worktree_task_ids",
        lambda: {TASK_A},
    )

    result: list[TaskInfoShort] = aggregate_tasks_short()
    assert len(result) == 1
    assert result[0].status == "completed"


def test_worktree_override_does_not_affect_no_worktree(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A not_started task without a worktree stays not_started."""
    build_complete_task(
        repo_root=repo,
        task_id=TASK_A,
        task_index=1,
        status="not_started",
        task_json_overrides={"start_time": None, "end_time": None},
    )
    monkeypatch.setattr(
        agg_mod,
        "_get_active_worktree_task_ids",
        lambda: set(),
    )

    result: list[TaskInfoShort] = aggregate_tasks_short()
    assert len(result) == 1
    assert result[0].status == TASK_STATUS_NOT_STARTED
