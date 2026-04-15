"""Per-aggregator-type archive definitions and section dispatcher."""

from typing import assert_never

from arf.scripts.overview.llm_context.collect_full import (
    collect_full_answers,
    collect_full_categories,
    collect_full_costs,
    collect_full_datasets,
    collect_full_libraries,
    collect_full_metrics,
    collect_full_models,
    collect_full_papers,
    collect_full_predictions,
    collect_full_suggestions,
    collect_full_task_types,
    collect_full_tasks,
)
from arf.scripts.overview.llm_context.models import (
    ArchiveSection,
    ProjectSnapshot,
    TypeArchiveDefinition,
)

TYPE_ID_TASKS: str = "tasks"
TYPE_ID_PAPERS: str = "papers"
TYPE_ID_DATASETS: str = "datasets"
TYPE_ID_LIBRARIES: str = "libraries"
TYPE_ID_ANSWERS: str = "answers"
TYPE_ID_SUGGESTIONS: str = "suggestions"
TYPE_ID_MODELS: str = "models"
TYPE_ID_PREDICTIONS: str = "predictions"
TYPE_ID_METRICS: str = "metrics"
TYPE_ID_CATEGORIES: str = "categories"
TYPE_ID_TASK_TYPES: str = "task-types"
TYPE_ID_COSTS: str = "costs"

ALL_TYPE_IDS: list[str] = [
    TYPE_ID_TASKS,
    TYPE_ID_PAPERS,
    TYPE_ID_DATASETS,
    TYPE_ID_LIBRARIES,
    TYPE_ID_ANSWERS,
    TYPE_ID_SUGGESTIONS,
    TYPE_ID_MODELS,
    TYPE_ID_PREDICTIONS,
    TYPE_ID_METRICS,
    TYPE_ID_CATEGORIES,
    TYPE_ID_TASK_TYPES,
    TYPE_ID_COSTS,
]


def build_type_archive_definitions() -> list[TypeArchiveDefinition]:
    return [
        TypeArchiveDefinition(
            type_id=TYPE_ID_TASKS,
            title="All Tasks",
            file_name="type-tasks.xml",
            description=(
                "Complete task data with full descriptions, results summaries,"
                " dependencies, and status."
            ),
            included_content=[
                "all tasks with full descriptions and results summaries",
            ],
        ),
        TypeArchiveDefinition(
            type_id=TYPE_ID_PAPERS,
            title="All Papers",
            file_name="type-papers.xml",
            description=("Complete paper corpus with full summaries, metadata, and abstracts."),
            included_content=[
                "all papers with full summaries and metadata",
            ],
        ),
        TypeArchiveDefinition(
            type_id=TYPE_ID_DATASETS,
            title="All Datasets",
            file_name="type-datasets.xml",
            description=(
                "Complete dataset inventory with full descriptions, access info, and sizes."
            ),
            included_content=[
                "all datasets with full descriptions",
            ],
        ),
        TypeArchiveDefinition(
            type_id=TYPE_ID_LIBRARIES,
            title="All Libraries",
            file_name="type-libraries.xml",
            description=(
                "Complete library registry with full descriptions, module paths, and entry points."
            ),
            included_content=[
                "all libraries with full descriptions and entry points",
            ],
        ),
        TypeArchiveDefinition(
            type_id=TYPE_ID_ANSWERS,
            title="All Answers",
            file_name="type-answers.xml",
            description=("Complete question and answer corpus with full answer bodies."),
            included_content=[
                "all answers with full answer bodies",
            ],
        ),
        TypeArchiveDefinition(
            type_id=TYPE_ID_SUGGESTIONS,
            title="All Suggestions",
            file_name="type-suggestions.xml",
            description=("Complete suggestion list with full descriptions, priority, and status."),
            included_content=[
                "all suggestions with full descriptions",
            ],
        ),
        TypeArchiveDefinition(
            type_id=TYPE_ID_MODELS,
            title="All Models",
            file_name="type-models.xml",
            description=(
                "Complete model registry with full descriptions, architectures,"
                " and training details."
            ),
            included_content=[
                "all models with full descriptions and training info",
            ],
        ),
        TypeArchiveDefinition(
            type_id=TYPE_ID_PREDICTIONS,
            title="All Predictions",
            file_name="type-predictions.xml",
            description=(
                "Complete predictions inventory with full descriptions,"
                " metrics, and model references."
            ),
            included_content=[
                "all predictions with full descriptions and metrics",
            ],
        ),
        TypeArchiveDefinition(
            type_id=TYPE_ID_METRICS,
            title="All Metrics",
            file_name="type-metrics.xml",
            description=(
                "Complete metric definitions with full descriptions, units,"
                " and associated datasets."
            ),
            included_content=[
                "all metrics with full descriptions",
            ],
        ),
        TypeArchiveDefinition(
            type_id=TYPE_ID_CATEGORIES,
            title="All Categories",
            file_name="type-categories.xml",
            description=("Complete category definitions with full detailed descriptions."),
            included_content=[
                "all categories with detailed descriptions",
            ],
        ),
        TypeArchiveDefinition(
            type_id=TYPE_ID_TASK_TYPES,
            title="All Task Types",
            file_name="type-task-types.xml",
            description=("Complete task type definitions with descriptions and instructions."),
            included_content=[
                "all task types with descriptions and instructions",
            ],
        ),
        TypeArchiveDefinition(
            type_id=TYPE_ID_COSTS,
            title="Project Costs",
            file_name="type-costs.xml",
            description=("Complete cost breakdown with budget, per-service, and per-task details."),
            included_content=[
                "budget summary and per-task cost breakdown",
            ],
        ),
    ]


def collect_sections_for_type(
    *,
    type_id: str,
    snapshot: ProjectSnapshot,
) -> list[ArchiveSection]:
    if type_id == TYPE_ID_TASKS:
        return collect_full_tasks(tasks=snapshot.tasks)
    if type_id == TYPE_ID_PAPERS:
        return collect_full_papers(papers=snapshot.papers)
    if type_id == TYPE_ID_DATASETS:
        return collect_full_datasets(datasets=snapshot.datasets)
    if type_id == TYPE_ID_LIBRARIES:
        return collect_full_libraries(libraries=snapshot.libraries)
    if type_id == TYPE_ID_ANSWERS:
        return collect_full_answers(answers=snapshot.answers)
    if type_id == TYPE_ID_SUGGESTIONS:
        return collect_full_suggestions(suggestions=snapshot.suggestions)
    if type_id == TYPE_ID_MODELS:
        return collect_full_models(models=snapshot.models)
    if type_id == TYPE_ID_PREDICTIONS:
        return collect_full_predictions(predictions=snapshot.predictions)
    if type_id == TYPE_ID_METRICS:
        return collect_full_metrics(metrics=snapshot.metrics)
    if type_id == TYPE_ID_CATEGORIES:
        return collect_full_categories(categories=snapshot.categories)
    if type_id == TYPE_ID_TASK_TYPES:
        return collect_full_task_types(task_types=snapshot.task_types)
    if type_id == TYPE_ID_COSTS:
        return collect_full_costs(costs=snapshot.costs)

    assert type_id in ALL_TYPE_IDS, f"type_id is one of the known types, got {type_id}"
    assert_never(type_id)  # type: ignore[arg-type]
