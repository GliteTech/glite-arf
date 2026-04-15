"""Tests for arf.scripts.aggregators.aggregate_costs."""

from pathlib import Path

import pytest

import arf.scripts.aggregators.aggregate_costs as agg_mod
import arf.scripts.aggregators.aggregate_tasks as tasks_mod
import arf.scripts.common.task_description as task_desc_mod
from arf.scripts.aggregators.aggregate_costs import (
    CostAggregationFull,
    CostAggregationShort,
    aggregate_costs_full,
    aggregate_costs_short,
)
from arf.scripts.verificators.common.project_budget import (
    ProjectBudgetModel,
    load_project_budget,
)
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.project_builder import build_project_budget
from arf.tests.fixtures.results_builders import build_costs_file
from arf.tests.fixtures.task_builder import build_complete_task

TASK_A: str = "t0001_alpha"
TASK_B: str = "t0002_bravo"

COSTS_WITH_SPEND: dict[str, object] = {
    "total_cost_usd": 12.50,
    "breakdown": {
        "openai_api": {
            "cost_usd": 10.00,
            "description": "GPT-4 API calls",
        },
        "anthropic_api": {
            "cost_usd": 2.50,
            "description": "Claude API calls",
        },
    },
}

COSTS_ZERO: dict[str, object] = {
    "total_cost_usd": 0.0,
    "breakdown": {},
}


def _patch_load_budget(
    *,
    monkeypatch: pytest.MonkeyPatch,
    repo_root: Path,
) -> None:
    """Patch load_project_budget to read from the test repo budget path."""
    original_load = load_project_budget

    def _patched_load(
        *,
        file_path: Path = repo_root / "project" / "budget.json",
    ) -> ProjectBudgetModel | None:
        return original_load(file_path=file_path)

    monkeypatch.setattr(agg_mod, "load_project_budget", _patched_load)


@pytest.fixture()
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        aggregator_modules=[agg_mod, tasks_mod, task_desc_mod],
    )
    _patch_load_budget(monkeypatch=monkeypatch, repo_root=tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# Empty state (no budget raises)
# ---------------------------------------------------------------------------


def test_missing_budget_raises(repo: Path) -> None:
    with pytest.raises(RuntimeError):
        aggregate_costs_full()


# ---------------------------------------------------------------------------
# Empty state with budget
# ---------------------------------------------------------------------------


def test_empty_returns_zero_costs(repo: Path) -> None:
    build_project_budget(repo_root=repo)

    result: CostAggregationFull = aggregate_costs_full()
    assert result.summary.discovered_task_count == 0
    assert result.summary.total_cost_usd == 0.0


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_discovers_task_costs(repo: Path) -> None:
    build_project_budget(repo_root=repo)
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_costs_file(
        repo_root=repo,
        task_id=TASK_A,
        payload=COSTS_WITH_SPEND,
    )

    result: CostAggregationFull = aggregate_costs_full()
    assert result.summary.discovered_task_count >= 1
    assert result.summary.total_cost_usd == pytest.approx(12.50)


def test_aggregates_multiple_task_costs(repo: Path) -> None:
    build_project_budget(repo_root=repo)
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_complete_task(repo_root=repo, task_id=TASK_B, task_index=2)
    build_costs_file(
        repo_root=repo,
        task_id=TASK_A,
        payload=COSTS_WITH_SPEND,
    )
    build_costs_file(
        repo_root=repo,
        task_id=TASK_B,
        payload=COSTS_WITH_SPEND,
    )

    result: CostAggregationFull = aggregate_costs_full()
    assert result.summary.total_cost_usd == pytest.approx(25.0)


# ---------------------------------------------------------------------------
# Short vs full
# ---------------------------------------------------------------------------


def test_short_has_fewer_fields(repo: Path) -> None:
    build_project_budget(repo_root=repo)
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_costs_file(
        repo_root=repo,
        task_id=TASK_A,
        payload=COSTS_WITH_SPEND,
    )

    short: CostAggregationShort = aggregate_costs_short()
    full: CostAggregationFull = aggregate_costs_full()

    assert hasattr(full, "breakdown_totals")
    assert hasattr(full, "service_totals")
    assert not hasattr(short, "breakdown_totals")


# ---------------------------------------------------------------------------
# Filtering by status
# ---------------------------------------------------------------------------


def test_filter_by_status(repo: Path) -> None:
    build_project_budget(repo_root=repo)
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
    build_costs_file(
        repo_root=repo,
        task_id=TASK_A,
        payload=COSTS_WITH_SPEND,
    )
    build_costs_file(
        repo_root=repo,
        task_id=TASK_B,
        payload=COSTS_WITH_SPEND,
    )

    result: CostAggregationFull = aggregate_costs_full(
        filter_statuses=["completed"],
    )
    assert result.summary.discovered_task_count == 1


# ---------------------------------------------------------------------------
# Filtering by ID
# ---------------------------------------------------------------------------


def test_filter_by_id(repo: Path) -> None:
    build_project_budget(repo_root=repo)
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    build_complete_task(repo_root=repo, task_id=TASK_B, task_index=2)
    build_costs_file(
        repo_root=repo,
        task_id=TASK_A,
        payload=COSTS_WITH_SPEND,
    )
    build_costs_file(
        repo_root=repo,
        task_id=TASK_B,
        payload=COSTS_ZERO,
    )

    result: CostAggregationFull = aggregate_costs_full(
        filter_ids=[TASK_A],
    )
    assert result.summary.discovered_task_count == 1
    assert result.summary.total_cost_usd == pytest.approx(12.50)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_missing_costs_file_reported_as_skipped(repo: Path) -> None:
    build_project_budget(repo_root=repo)
    build_complete_task(repo_root=repo, task_id=TASK_A, task_index=1)
    # Deliberately do not create costs.json

    result: CostAggregationFull = aggregate_costs_full()
    assert result.summary.skipped_task_count >= 1
