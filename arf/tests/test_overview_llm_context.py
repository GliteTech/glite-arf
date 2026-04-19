from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

import arf.scripts.overview.common as overview_common
import arf.scripts.overview.format_dashboard as format_dashboard_module
import arf.scripts.overview.llm_context.materialize as llm_context_materialize_module
import arf.scripts.overview.llm_context.token_estimation as token_estimation_module
import arf.scripts.overview.materialize as overview_materialize_module
import arf.scripts.overview.paths as overview_paths
from arf.scripts.aggregators.aggregate_machines import (
    MachineAggregation,
    MachineSummary,
)
from arf.scripts.aggregators.aggregate_metrics import MetricInfoFull
from arf.scripts.aggregators.aggregate_suggestions import SuggestionInfoFull
from arf.scripts.aggregators.aggregate_tasks import TaskInfoFull
from arf.scripts.overview.llm_context.materialize import MaterializationResult
from arf.scripts.overview.llm_context.models import (
    ArchiveSection,
    LLMContextArchiveSummary,
    PresetDefinition,
    PresetOptions,
)
from arf.scripts.overview.llm_context.render_xml import render_archive_xml
from arf.scripts.verificators.common import paths as repo_paths
from meta.asset_types.answer.aggregator import AnswerInfoFull
from meta.asset_types.dataset.aggregator import DatasetInfoFull
from meta.asset_types.library.aggregator import EntryPointInfo, LibraryInfoFull
from meta.asset_types.paper.aggregator import AuthorInfo, PaperInfoFull


def _configure_paths(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    overview_dir: Path = repo_root / "overview"
    overview_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(target=repo_paths, name="REPO_ROOT", value=repo_root)
    monkeypatch.setattr(target=repo_paths, name="OVERVIEW_DIR", value=overview_dir)
    monkeypatch.setattr(target=overview_paths, name="REPO_ROOT", value=repo_root)
    monkeypatch.setattr(target=overview_paths, name="OVERVIEW_DIR", value=overview_dir)
    monkeypatch.setattr(target=overview_common, name="REPO_ROOT", value=repo_root)
    monkeypatch.setattr(target=overview_common, name="OVERVIEW_DIR", value=overview_dir)


def _write_text(*, path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_tasks() -> list[TaskInfoFull]:
    return [
        TaskInfoFull(
            task_id="t0001_completed_task",
            task_index=1,
            name="Completed Task",
            short_description="Completed short description.",
            long_description="Completed long description.",
            status="completed",
            task_types=["experiment-run"],
            dependencies=[],
            start_time="2026-04-01T10:00:00Z",
            end_time="2026-04-02T11:00:00Z",
            expected_assets={},
            source_suggestion=None,
            effective_date="2026-04-02",
            results_summary="## Key Result\n\nCompleted task produced a useful result summary.",
            step_progress=None,
        ),
        TaskInfoFull(
            task_id="t0002_planned_task",
            task_index=2,
            name="Planned Task",
            short_description="Planned short description.",
            long_description="Planned long description with implementation details.",
            status="not_started",
            task_types=["build-model"],
            dependencies=["t0001_completed_task"],
            start_time=None,
            end_time=None,
            expected_assets={"model": 1},
            source_suggestion="S-0001-01",
            effective_date="2026-04-03",
            results_summary=None,
            step_progress=None,
        ),
    ]


def _build_answers() -> list[AnswerInfoFull]:
    return [
        AnswerInfoFull(
            answer_id="answer-1",
            question="What did the completed task show?",
            short_title="Completed task result",
            categories=["wsd"],
            answer_methods=["paper-review"],
            source_paper_ids=["paper-1"],
            source_urls=["https://example.com/result"],
            source_task_ids=["t0001_completed_task"],
            confidence="high",
            created_by_task="t0001_completed_task",
            date_created="2026-04-02",
            short_answer_path=None,
            full_answer_path=None,
            short_answer="Short answer body.",
            full_answer="Full answer body with more detail.",
        ),
    ]


def _build_papers() -> list[PaperInfoFull]:
    return [
        PaperInfoFull(
            paper_id="paper-1",
            title="Paper One",
            doi=None,
            url="https://example.com/paper",
            pdf_url=None,
            date_published=None,
            year=2025,
            authors=[AuthorInfo(name="Author A", country=None, institution=None)],
            institutions=[],
            journal="Example Venue",
            venue_kind="conference",
            categories=["wsd"],
            abstract="Abstract text.",
            citation_key="Paper2025",
            files=[],
            download_status="downloaded",
            download_failure_reason=None,
            added_by_task="t0001_completed_task",
            date_added="2026-04-02",
            summary_path=None,
            summary="Paper summary.",
            full_summary="## Summary\n\nFull paper summary.",
        ),
    ]


def _build_datasets() -> list[DatasetInfoFull]:
    return [
        DatasetInfoFull(
            dataset_id="dataset-1",
            name="Dataset One",
            version=None,
            short_description="Dataset short description.",
            source_paper_id=None,
            url=None,
            download_url=None,
            date_published=None,
            year=2024,
            authors=[],
            institutions=[],
            license=None,
            access_kind="public",
            size_description="100 items",
            files=[],
            categories=["dataset"],
            added_by_task="t0001_completed_task",
            date_added="2026-04-02",
            description_path=None,
            description_summary="Dataset summary.",
            full_description="Dataset full description.",
        ),
    ]


def _build_libraries() -> list[LibraryInfoFull]:
    return [
        LibraryInfoFull(
            library_id="library-1",
            name="Library One",
            version="1.0.0",
            short_description="Library short description.",
            module_paths=["tasks.t0001_completed_task.code.library"],
            entry_points=[
                EntryPointInfo(
                    name="run",
                    kind="function",
                    module="tasks.t0001_completed_task.code.library",
                    description="Main entry point.",
                ),
            ],
            dependencies=["numpy"],
            test_paths=None,
            categories=["library"],
            created_by_task="t0001_completed_task",
            date_created="2026-04-02",
            description_path=None,
            description_summary="Library summary.",
            full_description="Library full description.",
        ),
    ]


def _build_metrics() -> list[MetricInfoFull]:
    return [
        MetricInfoFull(
            metric_key="f1_all",
            name="F1 All",
            description="Main F1 metric.",
            unit="score",
            value_type="float",
            version=1,
            higher_is_better=True,
            datasets=["raganato_all"],
            is_key=False,
            emoji=None,
        ),
    ]


def _build_suggestions() -> list[SuggestionInfoFull]:
    return [
        SuggestionInfoFull(
            id="S-0001-01",
            title="Try the planned task",
            description="Suggestion description.",
            kind="experiment",
            priority="high",
            source_task="t0001_completed_task",
            source_paper=None,
            categories=["wsd"],
            status="active",
            date_added="2026-04-02",
        ),
    ]


def test_token_estimation_and_compatibility() -> None:
    assert token_estimation_module.estimate_tokens(text="abcdefgh") == 2
    assert token_estimation_module.compatible_windows(estimated_tokens=120_000) == [
        "131k-class",
        "200k-class",
        "1M-class",
    ]
    assert token_estimation_module.compatible_windows(estimated_tokens=250_000) == ["1M-class"]


def test_render_archive_xml_escapes_content() -> None:
    preset: PresetDefinition = PresetDefinition(
        preset_id="sample",
        title="Sample & Title",
        file_name="sample.xml",
        description="Description",
        use_case="Use <case>",
        included_content=["project description"],
        options=PresetOptions(
            include_completed_task_details=False,
            include_planned_task_long_descriptions=False,
            include_research_documents=False,
            include_suggestions=False,
            suggestion_limit=None,
            include_papers=False,
            paper_limit=None,
            include_datasets=False,
            include_libraries=False,
            include_metrics=False,
            include_full_answers=False,
        ),
    )
    section: ArchiveSection = ArchiveSection(
        section_id="section-1",
        title="Section <One>",
        source_kind="aggregator",
        source_name="aggregate_tasks_full",
        source_ids=["t0001"],
        repo_paths=["project/description.md"],
        content="A & B < C",
    )

    xml: str = render_archive_xml(
        preset=preset,
        sections=[section],
        generated_at_utc="2026-04-04T10:00:00Z",
        char_count=100,
        byte_count=100,
        estimated_tokens=25,
        compatibility_labels=["131k-class"],
    )

    assert "<title>Sample &amp; Title</title>" in xml
    assert "<use_case>Use &lt;case&gt;</use_case>" in xml
    assert "A &amp; B &lt; C" in xml
    assert "<path>project/description.md</path>" in xml


def test_materialize_llm_context_writes_archives(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_paths(monkeypatch=monkeypatch, repo_root=tmp_path)
    _write_text(
        path=tmp_path / "project" / "description.md",
        content="# Project\n\n## Goal\n\nGoal text.\n",
    )
    _write_text(
        path=tmp_path / "tasks" / "t0001_completed_task" / "results" / "results_detailed.md",
        content="# Detailed Results\n\nDetailed result body.\n",
    )
    _write_text(
        path=tmp_path / "tasks" / "t0001_completed_task" / "research" / "research_code.md",
        content="# Research Code\n\nCode research body.\n",
    )

    result: MaterializationResult = llm_context_materialize_module.materialize_llm_context(
        tasks=_build_tasks(),
        answers=_build_answers(),
        papers=_build_papers(),
        datasets=_build_datasets(),
        libraries=_build_libraries(),
        metrics=_build_metrics(),
        suggestions=_build_suggestions(),
    )

    llm_context_dir: Path = tmp_path / "overview" / "llm-context"
    project_overview_xml: str = (llm_context_dir / "project-overview.xml").read_text(
        encoding="utf-8"
    )
    full_xml: str = (llm_context_dir / "full.xml").read_text(encoding="utf-8")
    research_history_xml: str = (llm_context_dir / "research-history.xml").read_text(
        encoding="utf-8"
    )
    readme_text: str = (llm_context_dir / "README.md").read_text(encoding="utf-8")

    assert len(result.preset_summaries) == 8
    assert "# LLM Context Archives" in readme_text
    assert "## Preset Archives" in readme_text
    assert "| Preset | Tokens | Best For |" in readme_text
    assert "| [`project-overview`](project-overview.xml) |" in readme_text
    assert "## Project Overview" in readme_text
    assert "### Included Types" in readme_text
    assert "| Included Type | Coverage |" in readme_text
    assert "Full `project/description.md`." in readme_text
    assert "Goal text." in project_overview_xml
    assert "Completed task produced a useful result summary." in project_overview_xml
    assert "Detailed result body." in full_xml
    assert "Code research body." in research_history_xml
    assert project_overview_xml.index("t0001_completed_task") < project_overview_xml.index(
        "t0002_planned_task"
    )

    assert len(result.type_summaries) > 0
    assert "## Per-Type Archives" in readme_text
    assert "| Type | Tokens | Description |" in readme_text

    type_tasks_xml: str = (llm_context_dir / "type-tasks.xml").read_text(encoding="utf-8")
    assert 'type_id="tasks"' in type_tasks_xml
    assert "Completed long description." in type_tasks_xml
    assert "Completed task produced a useful result summary." in type_tasks_xml

    type_papers_xml: str = (llm_context_dir / "type-papers.xml").read_text(encoding="utf-8")
    assert "Full paper summary." in type_papers_xml

    type_answers_xml: str = (llm_context_dir / "type-answers.xml").read_text(encoding="utf-8")
    assert "Full answer body with more detail." in type_answers_xml

    type_datasets_xml: str = (llm_context_dir / "type-datasets.xml").read_text(encoding="utf-8")
    assert "Dataset full description." in type_datasets_xml

    type_suggestions_xml: str = (llm_context_dir / "type-suggestions.xml").read_text(
        encoding="utf-8"
    )
    assert "Suggestion description." in type_suggestions_xml


def test_materialize_all_passes_llm_context_archives_to_dashboard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    archive_summary: LLMContextArchiveSummary = LLMContextArchiveSummary(
        preset_id="project-overview",
        title="Project Overview",
        file_name="project-overview.xml",
        description="desc",
        use_case="use",
        included_content=["project description"],
        section_count=4,
        char_count=100,
        byte_count=100,
        estimated_tokens=25,
        compatibility_labels=["131k-class"],
    )

    monkeypatch.setattr(overview_materialize_module, "aggregate_task_types", lambda: [])
    monkeypatch.setattr(overview_materialize_module, "aggregate_tasks_full", lambda: _build_tasks())
    monkeypatch.setattr(overview_materialize_module, "aggregate_costs_full", lambda: object())
    monkeypatch.setattr(
        overview_materialize_module,
        "aggregate_answers_full",
        lambda **_: _build_answers(),
    )
    monkeypatch.setattr(
        overview_materialize_module,
        "aggregate_papers_full",
        lambda **_: _build_papers(),
    )
    monkeypatch.setattr(
        overview_materialize_module,
        "aggregate_datasets_full",
        lambda **_: _build_datasets(),
    )
    monkeypatch.setattr(
        overview_materialize_module,
        "aggregate_libraries_full",
        lambda **_: _build_libraries(),
    )
    monkeypatch.setattr(overview_materialize_module, "aggregate_models_full", lambda **_: [])
    monkeypatch.setattr(overview_materialize_module, "aggregate_predictions_full", lambda **_: [])
    monkeypatch.setattr(
        overview_materialize_module,
        "aggregate_metrics_full",
        lambda: _build_metrics(),
    )
    monkeypatch.setattr(
        overview_materialize_module,
        "aggregate_suggestions_full",
        lambda: _build_suggestions(),
    )
    monkeypatch.setattr(overview_materialize_module, "collect_suggestion_task_map", lambda: {})
    monkeypatch.setattr(overview_materialize_module, "aggregate_categories", lambda: [])
    monkeypatch.setattr(overview_materialize_module, "materialize_task_types", lambda **_: None)
    monkeypatch.setattr(overview_materialize_module, "materialize_tasks", lambda **_: None)
    monkeypatch.setattr(overview_materialize_module, "materialize_costs", lambda **_: None)
    monkeypatch.setattr(overview_materialize_module, "materialize_answers", lambda **_: None)
    monkeypatch.setattr(overview_materialize_module, "materialize_papers", lambda **_: None)
    monkeypatch.setattr(overview_materialize_module, "materialize_datasets", lambda **_: None)
    monkeypatch.setattr(overview_materialize_module, "materialize_libraries", lambda **_: None)
    monkeypatch.setattr(overview_materialize_module, "materialize_models", lambda **_: None)
    monkeypatch.setattr(overview_materialize_module, "materialize_predictions", lambda **_: None)
    monkeypatch.setattr(overview_materialize_module, "materialize_metrics", lambda **_: None)
    monkeypatch.setattr(
        overview_materialize_module, "aggregate_metric_results_full", lambda **_: []
    )
    monkeypatch.setattr(overview_materialize_module, "materialize_metric_results", lambda **_: None)
    monkeypatch.setattr(overview_materialize_module, "materialize_suggestions", lambda **_: None)
    monkeypatch.setattr(overview_materialize_module, "materialize_categories", lambda **_: None)
    monkeypatch.setattr(overview_materialize_module, "materialize_news", lambda: [])
    monkeypatch.setattr(
        overview_materialize_module,
        "materialize_llm_context",
        lambda **_: MaterializationResult(
            preset_summaries=[archive_summary],
            type_summaries=[],
        ),
    )

    def _capture_dashboard(*, data: Any) -> None:
        captured["data"] = data

    monkeypatch.setattr(overview_materialize_module, "materialize_dashboard", _capture_dashboard)

    overview_materialize_module.materialize_all()

    dashboard_data = captured["data"]
    assert dashboard_data.llm_context_archives == [archive_summary]


def test_dashboard_formats_featured_llm_context_line() -> None:
    costs = cast(
        Any,
        SimpleNamespace(
            summary=SimpleNamespace(
                total_cost_usd=0.0,
                spent_percent=0.0,
                budget_left_usd=100.0,
            ),
            budget=SimpleNamespace(total_budget=100.0),
            tasks=[],
        ),
    )
    archives: list[LLMContextArchiveSummary] = [
        LLMContextArchiveSummary(
            preset_id="project-overview",
            title="Project Overview",
            file_name="project-overview.xml",
            description="desc",
            use_case="use",
            included_content=["project description"],
            section_count=4,
            char_count=100,
            byte_count=100,
            estimated_tokens=18_900,
            compatibility_labels=["131k-class"],
            short_name="overview",
            featured_rank=1,
        ),
        LLMContextArchiveSummary(
            preset_id="roadmap",
            title="Roadmap",
            file_name="roadmap.xml",
            description="desc",
            use_case="use",
            included_content=["project description"],
            section_count=5,
            char_count=100,
            byte_count=100,
            estimated_tokens=48_700,
            compatibility_labels=["131k-class"],
            short_name="roadmap",
            featured_rank=2,
        ),
    ]
    dashboard_text: str = format_dashboard_module._format_dashboard(
        data=format_dashboard_module.DashboardData(
            tasks=[],
            costs=costs,
            machines=MachineAggregation(
                summary=MachineSummary(
                    total_machines=0,
                    total_failed_attempts=0,
                    failure_rate=0.0,
                    avg_provisioning_seconds=None,
                    total_cost_usd=0.0,
                    total_wasted_cost_usd=0.0,
                    gpu_tier_costs={},
                    failure_reasons={},
                ),
                tasks=[],
            ),
            suggestions=[],
            suggestion_task_map={},
            answers=[],
            papers=[],
            datasets=[],
            models=[],
            predictions=[],
            libraries=[],
            metrics=[],
            metric_results=[],
            task_types=[],
            categories=[],
            llm_context_archives=archives,
            news_days=[],
        )
    )

    assert (
        "**[LLM Contexts](llm-context/README.md)**: "
        "[overview](llm-context/project-overview.xml) (19K) | "
        "[roadmap](llm-context/roadmap.xml) (49K)"
    ) in dashboard_text
    assert "## [LLM Context Archives" not in dashboard_text
