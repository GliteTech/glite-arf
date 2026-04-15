"""Full-detail per-type section collectors for LLM context archives.

Each function produces sections with complete untruncated content for a single
aggregator type, intended for per-type archive files.
"""

import json
from typing import Any

from arf.scripts.aggregators.aggregate_categories import CategoryInfo
from arf.scripts.aggregators.aggregate_costs import CostAggregationFull
from arf.scripts.aggregators.aggregate_metrics import MetricInfoFull
from arf.scripts.aggregators.aggregate_suggestions import SuggestionInfoFull
from arf.scripts.aggregators.aggregate_task_types import TaskTypeInfo
from arf.scripts.aggregators.aggregate_tasks import (
    TASK_STATUS_COMPLETED,
    TaskInfoFull,
)
from arf.scripts.overview.llm_context.collect import (
    SOURCE_KIND_AGGREGATOR,
    _coalesce_nonempty_text,
    _prepare_content,
    _task_effective_date,
)
from arf.scripts.overview.llm_context.models import ArchiveSection
from meta.asset_types.answer.aggregator import AnswerInfoFull
from meta.asset_types.dataset.aggregator import DatasetInfoFull
from meta.asset_types.library.aggregator import LibraryInfoFull
from meta.asset_types.model.aggregator import ModelInfoFull
from meta.asset_types.paper.aggregator import PaperInfoFull
from meta.asset_types.predictions.aggregator import PredictionsInfoFull

SECTION_ID_FULL_TASKS: str = "full-tasks"
SECTION_ID_FULL_PAPERS: str = "full-papers"
SECTION_ID_FULL_DATASETS: str = "full-datasets"
SECTION_ID_FULL_LIBRARIES: str = "full-libraries"
SECTION_ID_FULL_ANSWERS: str = "full-answers"
SECTION_ID_FULL_SUGGESTIONS: str = "full-suggestions"
SECTION_ID_FULL_MODELS: str = "full-models"
SECTION_ID_FULL_PREDICTIONS: str = "full-predictions"
SECTION_ID_FULL_METRICS: str = "full-metrics"
SECTION_ID_FULL_CATEGORIES: str = "full-categories"
SECTION_ID_FULL_TASK_TYPES: str = "full-task-types"
SECTION_ID_FULL_COSTS: str = "full-costs"

NO_CONTENT_PLACEHOLDER: str = "No content available."


def collect_full_tasks(*, tasks: list[TaskInfoFull]) -> list[ArchiveSection]:
    ordered: list[TaskInfoFull] = sorted(tasks, key=lambda t: t.task_index)
    if len(ordered) == 0:
        return []
    lines: list[str] = [
        f"Total tasks: {len(ordered)}",
        "",
    ]
    for task in ordered:
        lines.extend(
            [
                f"## {task.name}",
                f"ID: {task.task_id}",
                f"Status: {task.status}",
                f"Effective date: {_task_effective_date(task=task)}",
                f"Short description: {task.short_description}",
            ]
        )
        if len(task.dependencies) > 0:
            lines.append("Dependencies: " + ", ".join(task.dependencies))
        if len(task.task_types) > 0:
            lines.append("Task types: " + ", ".join(task.task_types))
        if task.source_suggestion is not None:
            lines.append(f"Source suggestion: {task.source_suggestion}")
        if task.start_time is not None:
            lines.append(f"Start time: {task.start_time}")
        if task.end_time is not None:
            lines.append(f"End time: {task.end_time}")
        if len(task.long_description.strip()) > 0:
            lines.append("")
            lines.append(_prepare_content(text=task.long_description.strip()))
        if task.status == TASK_STATUS_COMPLETED and task.results_summary is not None:
            lines.append("")
            lines.append("### Results Summary")
            lines.append("")
            lines.append(_prepare_content(text=task.results_summary.strip()))
        lines.append("")
    return [
        ArchiveSection(
            section_id=SECTION_ID_FULL_TASKS,
            title="All Tasks (Full Detail)",
            source_kind=SOURCE_KIND_AGGREGATOR,
            source_name="aggregate_tasks_full",
            source_ids=[task.task_id for task in ordered],
            repo_paths=[],
            content="\n".join(lines).strip(),
        ),
    ]


def collect_full_papers(*, papers: list[PaperInfoFull]) -> list[ArchiveSection]:
    ordered: list[PaperInfoFull] = sorted(
        papers,
        key=lambda p: (
            _coalesce_nonempty_text(p.date_added, default=""),
            p.year,
            p.paper_id,
        ),
        reverse=True,
    )
    if len(ordered) == 0:
        return []
    lines: list[str] = [
        f"Papers: {len(ordered)}",
        "",
    ]
    for paper in ordered:
        author_names: str = ", ".join(a.name for a in paper.authors)
        lines.extend(
            [
                f"## {paper.title}",
                f"ID: {paper.paper_id}",
                f"Year: {paper.year}",
                f"Authors: {author_names}",
                f"Venue: {paper.journal}",
                f"Venue type: {paper.venue_kind}",
            ]
        )
        if paper.doi is not None:
            lines.append(f"DOI: {paper.doi}")
        if paper.url is not None:
            lines.append(f"URL: {paper.url}")
        if len(paper.categories) > 0:
            lines.append("Categories: " + ", ".join(paper.categories))
        lines.append(f"Added by task: {paper.added_by_task}")
        if paper.date_added is not None:
            lines.append(f"Date added: {paper.date_added}")
        lines.append("")
        summary_text: str | None = _coalesce_nonempty_text(
            paper.full_summary,
            paper.summary,
            paper.abstract,
        )
        raw_summary: str = summary_text if summary_text is not None else NO_CONTENT_PLACEHOLDER
        lines.append(_prepare_content(text=raw_summary))
        lines.append("")
    return [
        ArchiveSection(
            section_id=SECTION_ID_FULL_PAPERS,
            title="All Papers (Full Detail)",
            source_kind=SOURCE_KIND_AGGREGATOR,
            source_name="aggregate_papers_full",
            source_ids=[p.paper_id for p in ordered],
            repo_paths=[],
            content="\n".join(lines).strip(),
        ),
    ]


def collect_full_datasets(*, datasets: list[DatasetInfoFull]) -> list[ArchiveSection]:
    ordered: list[DatasetInfoFull] = sorted(
        datasets,
        key=lambda d: (
            _coalesce_nonempty_text(d.date_added, default=""),
            d.dataset_id,
        ),
    )
    if len(ordered) == 0:
        return []
    lines: list[str] = [
        f"Datasets: {len(ordered)}",
        "",
    ]
    for dataset in ordered:
        lines.extend(
            [
                f"## {dataset.name}",
                f"ID: {dataset.dataset_id}",
                f"Year: {dataset.year}",
                f"Access: {dataset.access_kind}",
                f"Size: {dataset.size_description}",
            ]
        )
        if dataset.version is not None:
            lines.append(f"Version: {dataset.version}")
        if dataset.license is not None:
            lines.append(f"License: {dataset.license}")
        if dataset.url is not None:
            lines.append(f"URL: {dataset.url}")
        if len(dataset.categories) > 0:
            lines.append("Categories: " + ", ".join(dataset.categories))
        added_by: str = _coalesce_nonempty_text(
            dataset.added_by_task,
            default="unknown",
        )
        lines.append(f"Added by task: {added_by}")
        if dataset.date_added is not None:
            lines.append(f"Date added: {dataset.date_added}")
        lines.append("")
        description_text: str | None = _coalesce_nonempty_text(
            dataset.full_description,
            dataset.description_summary,
            dataset.short_description,
        )
        raw_desc: str = description_text if description_text is not None else NO_CONTENT_PLACEHOLDER
        lines.append(_prepare_content(text=raw_desc))
        lines.append("")
    return [
        ArchiveSection(
            section_id=SECTION_ID_FULL_DATASETS,
            title="All Datasets (Full Detail)",
            source_kind=SOURCE_KIND_AGGREGATOR,
            source_name="aggregate_datasets_full",
            source_ids=[d.dataset_id for d in ordered],
            repo_paths=[],
            content="\n".join(lines).strip(),
        ),
    ]


def collect_full_libraries(*, libraries: list[LibraryInfoFull]) -> list[ArchiveSection]:
    ordered: list[LibraryInfoFull] = sorted(
        libraries,
        key=lambda lib: (lib.date_created, lib.library_id),
    )
    if len(ordered) == 0:
        return []
    lines: list[str] = [
        f"Libraries: {len(ordered)}",
        "",
    ]
    for library in ordered:
        lines.extend(
            [
                f"## {library.name}",
                f"ID: {library.library_id}",
                f"Version: {library.version}",
                f"Created by task: {library.created_by_task}",
                f"Date created: {library.date_created}",
            ]
        )
        if len(library.module_paths) > 0:
            lines.append("Module paths: " + ", ".join(library.module_paths))
        if len(library.dependencies) > 0:
            lines.append("Dependencies: " + ", ".join(library.dependencies))
        if library.test_paths is not None and len(library.test_paths) > 0:
            lines.append("Test paths: " + ", ".join(library.test_paths))
        if len(library.categories) > 0:
            lines.append("Categories: " + ", ".join(library.categories))
        for ep in library.entry_points:
            lines.append(f"Entry point: {ep.name} ({ep.kind}) — {ep.description}")
        lines.append("")
        description_text: str | None = _coalesce_nonempty_text(
            library.full_description,
            library.description_summary,
            library.short_description,
        )
        raw_desc: str = description_text if description_text is not None else NO_CONTENT_PLACEHOLDER
        lines.append(_prepare_content(text=raw_desc))
        lines.append("")
    return [
        ArchiveSection(
            section_id=SECTION_ID_FULL_LIBRARIES,
            title="All Libraries (Full Detail)",
            source_kind=SOURCE_KIND_AGGREGATOR,
            source_name="aggregate_libraries_full",
            source_ids=[lib.library_id for lib in ordered],
            repo_paths=[],
            content="\n".join(lines).strip(),
        ),
    ]


def collect_full_answers(*, answers: list[AnswerInfoFull]) -> list[ArchiveSection]:
    ordered: list[AnswerInfoFull] = sorted(
        answers,
        key=lambda a: (a.date_created, a.answer_id),
    )
    if len(ordered) == 0:
        return []
    lines: list[str] = [
        f"Answers: {len(ordered)}",
        "",
    ]
    for answer in ordered:
        lines.extend(
            [
                f"## {answer.question}",
                f"ID: {answer.answer_id}",
                f"Short title: {answer.short_title}",
                f"Confidence: {answer.confidence}",
                f"Created by: {answer.created_by_task} on {answer.date_created}",
            ]
        )
        if len(answer.categories) > 0:
            lines.append("Categories: " + ", ".join(answer.categories))
        if len(answer.answer_methods) > 0:
            lines.append("Methods: " + ", ".join(answer.answer_methods))
        if len(answer.source_paper_ids) > 0:
            lines.append("Source papers: " + ", ".join(answer.source_paper_ids))
        if len(answer.source_task_ids) > 0:
            lines.append("Source tasks: " + ", ".join(answer.source_task_ids))
        lines.append("")
        answer_text: str | None = _coalesce_nonempty_text(
            answer.full_answer,
            answer.short_answer,
        )
        raw_answer: str = answer_text if answer_text is not None else NO_CONTENT_PLACEHOLDER
        lines.append(_prepare_content(text=raw_answer))
        lines.append("")
    return [
        ArchiveSection(
            section_id=SECTION_ID_FULL_ANSWERS,
            title="All Answers (Full Detail)",
            source_kind=SOURCE_KIND_AGGREGATOR,
            source_name="aggregate_answers_full",
            source_ids=[a.answer_id for a in ordered],
            repo_paths=[],
            content="\n".join(lines).strip(),
        ),
    ]


def collect_full_suggestions(
    *,
    suggestions: list[SuggestionInfoFull],
) -> list[ArchiveSection]:
    ordered: list[SuggestionInfoFull] = sorted(
        suggestions,
        key=lambda s: (
            _coalesce_nonempty_text(s.date_added, default=""),
            s.id,
        ),
    )
    if len(ordered) == 0:
        return []
    lines: list[str] = [
        f"Suggestions: {len(ordered)}",
        "",
    ]
    for suggestion in ordered:
        lines.extend(
            [
                f"## {suggestion.title}",
                f"ID: {suggestion.id}",
                f"Status: {suggestion.status}",
                f"Priority: {suggestion.priority}",
                f"Kind: {suggestion.kind}",
                f"Source task: {suggestion.source_task}",
            ]
        )
        if suggestion.source_paper is not None:
            lines.append(f"Source paper: {suggestion.source_paper}")
        if len(suggestion.categories) > 0:
            lines.append("Categories: " + ", ".join(suggestion.categories))
        if suggestion.date_added is not None:
            lines.append(f"Date added: {suggestion.date_added}")
        lines.append("")
        if suggestion.description is not None and len(suggestion.description.strip()) > 0:
            lines.append(_prepare_content(text=suggestion.description.strip()))
        else:
            lines.append(NO_CONTENT_PLACEHOLDER)
        lines.append("")
    return [
        ArchiveSection(
            section_id=SECTION_ID_FULL_SUGGESTIONS,
            title="All Suggestions (Full Detail)",
            source_kind=SOURCE_KIND_AGGREGATOR,
            source_name="aggregate_suggestions_full",
            source_ids=[s.id for s in ordered],
            repo_paths=[],
            content="\n".join(lines).strip(),
        ),
    ]


def collect_full_models(*, models: list[ModelInfoFull]) -> list[ArchiveSection]:
    ordered: list[ModelInfoFull] = sorted(
        models,
        key=lambda m: (m.date_created, m.model_id),
    )
    if len(ordered) == 0:
        return []
    lines: list[str] = [
        f"Models: {len(ordered)}",
        "",
    ]
    for model in ordered:
        lines.extend(
            [
                f"## {model.name}",
                f"ID: {model.model_id}",
                f"Version: {model.version}",
                f"Framework: {model.framework}",
                f"Architecture: {model.architecture}",
                f"Created by task: {model.created_by_task}",
                f"Date created: {model.date_created}",
            ]
        )
        if model.base_model is not None:
            lines.append(f"Base model: {model.base_model}")
        if model.base_model_source is not None:
            lines.append(f"Base model source: {model.base_model_source}")
        lines.append(f"Training task: {model.training_task_id}")
        if len(model.training_dataset_ids) > 0:
            lines.append("Training datasets: " + ", ".join(model.training_dataset_ids))
        if model.hyperparameters is not None and len(model.hyperparameters) > 0:
            lines.append("Hyperparameters: " + _format_dict(data=model.hyperparameters))
        if model.training_metrics is not None and len(model.training_metrics) > 0:
            lines.append("Training metrics: " + _format_dict(data=model.training_metrics))
        if len(model.categories) > 0:
            lines.append("Categories: " + ", ".join(model.categories))
        lines.append("")
        description_text: str | None = _coalesce_nonempty_text(
            model.full_description,
            model.description_summary,
            model.short_description,
        )
        raw_desc: str = description_text if description_text is not None else NO_CONTENT_PLACEHOLDER
        lines.append(_prepare_content(text=raw_desc))
        lines.append("")
    return [
        ArchiveSection(
            section_id=SECTION_ID_FULL_MODELS,
            title="All Models (Full Detail)",
            source_kind=SOURCE_KIND_AGGREGATOR,
            source_name="aggregate_models_full",
            source_ids=[m.model_id for m in ordered],
            repo_paths=[],
            content="\n".join(lines).strip(),
        ),
    ]


def collect_full_predictions(
    *,
    predictions: list[PredictionsInfoFull],
) -> list[ArchiveSection]:
    ordered: list[PredictionsInfoFull] = sorted(
        predictions,
        key=lambda p: (p.date_created, p.predictions_id),
    )
    if len(ordered) == 0:
        return []
    lines: list[str] = [
        f"Predictions: {len(ordered)}",
        "",
    ]
    for pred in ordered:
        lines.extend(
            [
                f"## {pred.name}",
                f"ID: {pred.predictions_id}",
                f"Created by task: {pred.created_by_task}",
                f"Date created: {pred.date_created}",
                f"Format: {pred.prediction_format}",
                f"Schema: {pred.prediction_schema}",
            ]
        )
        if pred.model_id is not None:
            lines.append(f"Model: {pred.model_id}")
        if len(pred.model_description) > 0:
            lines.append(f"Model description: {pred.model_description}")
        if len(pred.dataset_ids) > 0:
            lines.append("Datasets: " + ", ".join(pred.dataset_ids))
        if pred.instance_count is not None:
            lines.append(f"Instance count: {pred.instance_count}")
        if pred.metrics_at_creation is not None and len(pred.metrics_at_creation) > 0:
            lines.append("Metrics at creation: " + _format_dict(data=pred.metrics_at_creation))
        if len(pred.categories) > 0:
            lines.append("Categories: " + ", ".join(pred.categories))
        lines.append("")
        description_text: str | None = _coalesce_nonempty_text(
            pred.full_description,
            pred.description_summary,
            pred.short_description,
        )
        raw_desc: str = description_text if description_text is not None else NO_CONTENT_PLACEHOLDER
        lines.append(_prepare_content(text=raw_desc))
        lines.append("")
    return [
        ArchiveSection(
            section_id=SECTION_ID_FULL_PREDICTIONS,
            title="All Predictions (Full Detail)",
            source_kind=SOURCE_KIND_AGGREGATOR,
            source_name="aggregate_predictions_full",
            source_ids=[p.predictions_id for p in ordered],
            repo_paths=[],
            content="\n".join(lines).strip(),
        ),
    ]


def collect_full_metrics(*, metrics: list[MetricInfoFull]) -> list[ArchiveSection]:
    ordered: list[MetricInfoFull] = sorted(
        metrics,
        key=lambda m: m.metric_key,
    )
    if len(ordered) == 0:
        return []
    lines: list[str] = [
        f"Metrics: {len(ordered)}",
        "",
    ]
    for metric in ordered:
        lines.extend(
            [
                f"## {metric.name}",
                f"Key: {metric.metric_key}",
                f"Unit: {metric.unit}",
                f"Value type: {metric.value_type}",
                f"Version: {metric.version}",
            ]
        )
        if len(metric.datasets) > 0:
            lines.append("Datasets: " + ", ".join(metric.datasets))
        lines.append("")
        if metric.description is not None and len(metric.description.strip()) > 0:
            lines.append(_prepare_content(text=metric.description.strip()))
        else:
            lines.append(NO_CONTENT_PLACEHOLDER)
        lines.append("")
    return [
        ArchiveSection(
            section_id=SECTION_ID_FULL_METRICS,
            title="All Metrics (Full Detail)",
            source_kind=SOURCE_KIND_AGGREGATOR,
            source_name="aggregate_metrics_full",
            source_ids=[m.metric_key for m in ordered],
            repo_paths=[],
            content="\n".join(lines).strip(),
        ),
    ]


def collect_full_categories(
    *,
    categories: list[CategoryInfo],
) -> list[ArchiveSection]:
    ordered: list[CategoryInfo] = sorted(
        categories,
        key=lambda c: c.category_id,
    )
    if len(ordered) == 0:
        return []
    lines: list[str] = [
        f"Categories: {len(ordered)}",
        "",
    ]
    for category in ordered:
        lines.extend(
            [
                f"## {category.name}",
                f"ID: {category.category_id}",
                f"Version: {category.version}",
                "",
            ]
        )
        if len(category.detailed_description.strip()) > 0:
            lines.append(_prepare_content(text=category.detailed_description.strip()))
        else:
            lines.append(NO_CONTENT_PLACEHOLDER)
        lines.append("")
    return [
        ArchiveSection(
            section_id=SECTION_ID_FULL_CATEGORIES,
            title="All Categories (Full Detail)",
            source_kind=SOURCE_KIND_AGGREGATOR,
            source_name="aggregate_categories",
            source_ids=[c.category_id for c in ordered],
            repo_paths=[],
            content="\n".join(lines).strip(),
        ),
    ]


def collect_full_task_types(
    *,
    task_types: list[TaskTypeInfo],
) -> list[ArchiveSection]:
    ordered: list[TaskTypeInfo] = sorted(
        task_types,
        key=lambda tt: tt.task_type_id,
    )
    if len(ordered) == 0:
        return []
    lines: list[str] = [
        f"Task types: {len(ordered)}",
        "",
    ]
    for tt in ordered:
        lines.extend(
            [
                f"## {tt.name}",
                f"ID: {tt.task_type_id}",
                f"Version: {tt.version}",
                f"Short description: {tt.short_description}",
            ]
        )
        if len(tt.optional_steps) > 0:
            lines.append("Optional steps: " + ", ".join(tt.optional_steps))
        lines.append("")
        if len(tt.detailed_description.strip()) > 0:
            lines.append(_prepare_content(text=tt.detailed_description.strip()))
            lines.append("")
        if len(tt.instruction.strip()) > 0:
            lines.append("### Instructions")
            lines.append("")
            lines.append(_prepare_content(text=tt.instruction.strip()))
            lines.append("")
    return [
        ArchiveSection(
            section_id=SECTION_ID_FULL_TASK_TYPES,
            title="All Task Types (Full Detail)",
            source_kind=SOURCE_KIND_AGGREGATOR,
            source_name="aggregate_task_types",
            source_ids=[tt.task_type_id for tt in ordered],
            repo_paths=[],
            content="\n".join(lines).strip(),
        ),
    ]


def collect_full_costs(
    *,
    costs: CostAggregationFull | None,
) -> list[ArchiveSection]:
    if costs is None:
        return []
    lines: list[str] = [
        f"Total budget: ${costs.budget.total_budget:.2f}",
        f"Total spent: ${costs.summary.total_cost_usd:.2f}",
        f"Budget remaining: ${costs.summary.budget_left_usd:.2f}",
        f"Spent: {costs.summary.spent_percent:.1f}%",
        "",
    ]
    if len(costs.breakdown_totals) > 0:
        lines.append("### Cost Breakdown by Category")
        lines.append("")
        for category, amount in sorted(
            costs.breakdown_totals.items(),
            key=lambda pair: pair[1],
            reverse=True,
        ):
            lines.append(f"* {category}: ${amount:.2f}")
        lines.append("")
    if len(costs.service_totals) > 0:
        lines.append("### Cost Breakdown by Service")
        lines.append("")
        for service, amount in sorted(
            costs.service_totals.items(),
            key=lambda pair: pair[1],
            reverse=True,
        ):
            lines.append(f"* {service}: ${amount:.2f}")
        lines.append("")
    if len(costs.tasks) > 0:
        lines.append("### Per-Task Costs")
        lines.append("")
        for task_cost in costs.tasks:
            lines.append(f"* {task_cost.task_id}: ${task_cost.total_cost_usd:.2f}")
        lines.append("")
    return [
        ArchiveSection(
            section_id=SECTION_ID_FULL_COSTS,
            title="Project Costs (Full Detail)",
            source_kind=SOURCE_KIND_AGGREGATOR,
            source_name="aggregate_costs_full",
            source_ids=[],
            repo_paths=[],
            content="\n".join(lines).strip(),
        ),
    ]


def _format_dict(*, data: dict[str, Any]) -> str:
    return json.dumps(data, indent=None, ensure_ascii=False)
