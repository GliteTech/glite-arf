"""Tests for arf.scripts.aggregators.aggregate_task_types."""

from pathlib import Path

import pytest

import arf.scripts.aggregators.aggregate_task_types as agg_mod
from arf.scripts.aggregators.aggregate_task_types import (
    TaskTypeInfo,
    aggregate_task_types,
)
from arf.tests.fixtures.metadata_builders import build_task_type
from arf.tests.fixtures.paths import configure_repo_paths

TYPE_RESEARCH: str = "research"
TYPE_EXPERIMENT: str = "experiment"
TYPE_ANALYSIS: str = "analysis"


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


def test_empty_returns_no_task_types(repo: Path) -> None:
    result: list[TaskTypeInfo] = aggregate_task_types()
    assert len(result) == 0


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_discovers_multiple_task_types(repo: Path) -> None:
    build_task_type(
        repo_root=repo,
        task_type_slug=TYPE_RESEARCH,
        name="Research",
    )
    build_task_type(
        repo_root=repo,
        task_type_slug=TYPE_EXPERIMENT,
        name="Experiment",
    )

    result: list[TaskTypeInfo] = aggregate_task_types()
    slugs: list[str] = [tt.task_type_id for tt in result]

    assert TYPE_RESEARCH in slugs
    assert TYPE_EXPERIMENT in slugs
    assert len(result) == 2


def test_task_type_fields_populated(repo: Path) -> None:
    build_task_type(
        repo_root=repo,
        task_type_slug=TYPE_RESEARCH,
        name="Research",
        short_description="A research task type.",
        optional_steps=["creative_thinking"],
    )

    result: list[TaskTypeInfo] = aggregate_task_types()
    assert len(result) == 1

    tt: TaskTypeInfo = result[0]
    assert tt.task_type_id == TYPE_RESEARCH
    assert tt.name == "Research"
    assert tt.short_description == "A research task type."
    assert "creative_thinking" in tt.optional_steps


def test_has_external_costs_passed_through(repo: Path) -> None:
    """The aggregator must surface ``has_external_costs`` so the execute-task
    orchestrator can decide whether to gate the Phase 1 budget check on the
    current task's task types.
    """
    build_task_type(
        repo_root=repo,
        task_type_slug="no-external-costs-type",
        name="No External Costs Type",
        overrides={"has_external_costs": False},
    )
    build_task_type(
        repo_root=repo,
        task_type_slug="has-external-costs-type",
        name="Has External Costs Type",
        overrides={"has_external_costs": True},
    )

    result: list[TaskTypeInfo] = aggregate_task_types()
    by_slug: dict[str, TaskTypeInfo] = {tt.task_type_id: tt for tt in result}

    assert "no-external-costs-type" in by_slug
    assert "has-external-costs-type" in by_slug
    assert by_slug["no-external-costs-type"].has_external_costs is False
    assert by_slug["has-external-costs-type"].has_external_costs is True


def test_instruction_loaded(repo: Path) -> None:
    build_task_type(
        repo_root=repo,
        task_type_slug=TYPE_RESEARCH,
        name="Research",
    )

    result: list[TaskTypeInfo] = aggregate_task_types()
    assert len(result) == 1
    assert len(result[0].instruction) > 0


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_malformed_description_json_skipped(repo: Path) -> None:
    build_task_type(repo_root=repo, task_type_slug=TYPE_RESEARCH)

    bad_dir: Path = repo / "meta" / "task_types" / "bad-type"
    bad_dir.mkdir(parents=True, exist_ok=True)
    (bad_dir / "description.json").write_text("{invalid", encoding="utf-8")

    result: list[TaskTypeInfo] = aggregate_task_types()
    slugs: list[str] = [tt.task_type_id for tt in result]
    assert TYPE_RESEARCH in slugs
    assert "bad-type" not in slugs


def test_sorted_alphabetically(repo: Path) -> None:
    build_task_type(repo_root=repo, task_type_slug=TYPE_RESEARCH)
    build_task_type(repo_root=repo, task_type_slug=TYPE_ANALYSIS)
    build_task_type(repo_root=repo, task_type_slug=TYPE_EXPERIMENT)

    result: list[TaskTypeInfo] = aggregate_task_types()
    slugs: list[str] = [tt.task_type_id for tt in result]
    assert slugs == sorted(slugs)
