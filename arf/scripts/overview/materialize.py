"""Materialize aggregator outputs as markdown section folders in overview/.

Generates human-readable markdown snapshots of task types, tasks, costs,
answers, papers, datasets, libraries, models, predictions, metrics, and
suggestions for browsing on GitHub, plus XML LLM context archives under
`overview/llm-context/`. Each top-level overview section is materialized as
`overview/<section>/README.md`, with additional view subfolders where
applicable.
Scripts and skills must use the aggregator APIs directly — never read from
overview/.

Usage:
    uv run python -m arf.scripts.overview.materialize
"""

import argparse

from arf.scripts.aggregators.aggregate_categories import (
    CategoryInfo,
    aggregate_categories,
)
from arf.scripts.aggregators.aggregate_costs import (
    CostAggregationFull,
    aggregate_costs_full,
)
from arf.scripts.aggregators.aggregate_machines import (
    MachineAggregation,
    aggregate_machines,
)
from arf.scripts.aggregators.aggregate_metric_results import (
    MetricResultsFull,
    aggregate_metric_results_full,
)
from arf.scripts.aggregators.aggregate_metrics import (
    MetricInfoFull,
    aggregate_metrics_full,
)
from arf.scripts.aggregators.aggregate_suggestions import (
    SuggestionInfoFull,
    aggregate_suggestions_full,
    collect_suggestion_task_map,
)
from arf.scripts.aggregators.aggregate_task_types import (
    TaskTypeInfo,
    aggregate_task_types,
)
from arf.scripts.aggregators.aggregate_tasks import (
    TaskInfoFull,
    aggregate_tasks_full,
)
from arf.scripts.overview.format_categories import materialize_categories
from arf.scripts.overview.format_costs import materialize_costs
from arf.scripts.overview.format_dashboard import (
    DashboardData,
    materialize_dashboard,
)
from arf.scripts.overview.format_machines import materialize_machines
from arf.scripts.overview.format_metric_results import (
    materialize_metric_results,
)
from arf.scripts.overview.format_metrics import materialize_metrics
from arf.scripts.overview.format_news import NewsDayInfo, materialize_news
from arf.scripts.overview.format_suggestions import materialize_suggestions
from arf.scripts.overview.format_task_types import materialize_task_types
from arf.scripts.overview.format_tasks import (
    TaskKeyMetric,
    materialize_tasks,
)
from arf.scripts.overview.llm_context import (
    LLMContextArchiveSummary,
    MaterializationResult,
    materialize_llm_context,
)
from meta.asset_types.answer.aggregator import (
    AnswerInfoFull,
    aggregate_answers_full,
)
from meta.asset_types.answer.format_overview import materialize_answers
from meta.asset_types.dataset.aggregator import (
    DatasetInfoFull,
    aggregate_datasets_full,
)
from meta.asset_types.dataset.format_overview import materialize_datasets
from meta.asset_types.library.aggregator import (
    LibraryInfoFull,
    aggregate_libraries_full,
)
from meta.asset_types.library.format_overview import materialize_libraries
from meta.asset_types.model.aggregator import (
    ModelInfoFull,
    aggregate_models_full,
)
from meta.asset_types.model.format_overview import materialize_models
from meta.asset_types.paper.aggregator import (
    PaperInfoFull,
    aggregate_papers_full,
)
from meta.asset_types.paper.format_overview import materialize_papers
from meta.asset_types.predictions.aggregator import (
    PredictionsInfoFull,
    aggregate_predictions_full,
)
from meta.asset_types.predictions.format_overview import materialize_predictions


def _is_better(
    *,
    new_value: float | int,
    current_best: float | int,
    higher_is_better: bool,
) -> bool:
    return new_value > current_best if higher_is_better else new_value < current_best


def _build_key_metrics_by_task(
    *,
    metric_results: list[MetricResultsFull],
) -> dict[str, list[TaskKeyMetric]]:
    # For each key metric, keep only the best value per task across
    # all variants. "Best" means max for higher-is-better metrics and
    # min for lower-is-better ones (latency, error, cost, ...).
    result: dict[str, list[TaskKeyMetric]] = {}
    for mr in metric_results:
        if not mr.is_key:
            continue
        best_by_task: dict[str, float | int] = {}
        for entry in mr.entries:
            if entry.value is None:
                continue
            if not isinstance(entry.value, int | float):
                continue
            current_best: float | int | None = best_by_task.get(entry.task_id)
            if current_best is None or _is_better(
                new_value=entry.value,
                current_best=current_best,
                higher_is_better=mr.higher_is_better,
            ):
                best_by_task[entry.task_id] = entry.value
        for task_id, best_value in best_by_task.items():
            key_metric: TaskKeyMetric = TaskKeyMetric(
                metric_name=mr.metric_name,
                emoji=mr.emoji,
                value=best_value,
            )
            if task_id not in result:
                result[task_id] = []
            result[task_id].append(key_metric)
    return result


def materialize_all() -> None:
    print("Materializing overview files...")

    task_types: list[TaskTypeInfo] = aggregate_task_types()
    materialize_task_types(task_types=task_types)

    tasks: list[TaskInfoFull] = aggregate_tasks_full()

    costs: CostAggregationFull = aggregate_costs_full()
    materialize_costs(aggregation=costs)

    machines: MachineAggregation = aggregate_machines()
    materialize_machines(aggregation=machines)

    answers: list[AnswerInfoFull] = aggregate_answers_full(
        include_short_answer=True,
        include_full_answer=True,
    )
    materialize_answers(answers=answers)

    papers: list[PaperInfoFull] = aggregate_papers_full(
        include_full_summary=True,
    )
    materialize_papers(papers=papers)

    datasets: list[DatasetInfoFull] = aggregate_datasets_full(
        include_full_description=True,
    )
    materialize_datasets(datasets=datasets)

    libraries: list[LibraryInfoFull] = aggregate_libraries_full(
        include_full_description=True,
    )
    materialize_libraries(libraries=libraries)

    models: list[ModelInfoFull] = aggregate_models_full(
        include_full_description=True,
    )
    materialize_models(models=models)

    predictions: list[PredictionsInfoFull] = aggregate_predictions_full(
        include_full_description=True,
    )
    materialize_predictions(predictions=predictions)

    metrics: list[MetricInfoFull] = aggregate_metrics_full()
    materialize_metrics(metrics=metrics)

    metric_results: list[MetricResultsFull] = aggregate_metric_results_full()
    task_name_map: dict[str, str] = {t.task_id: t.name for t in tasks}
    materialize_metric_results(
        metric_results=metric_results,
        task_name_map=task_name_map,
    )

    key_metrics_by_task: dict[str, list[TaskKeyMetric]] = _build_key_metrics_by_task(
        metric_results=metric_results
    )
    materialize_tasks(
        tasks=tasks,
        key_metrics_by_task=key_metrics_by_task,
    )

    suggestions: list[SuggestionInfoFull] = aggregate_suggestions_full()
    task_map: dict[str, str] = collect_suggestion_task_map()
    materialize_suggestions(
        suggestions=suggestions,
        task_map=task_map,
    )

    news_days: list[NewsDayInfo] = materialize_news()

    categories: list[CategoryInfo] = aggregate_categories()

    materialize_categories(
        categories=categories,
        tasks=tasks,
        papers=papers,
        answers=answers,
        suggestions=suggestions,
        suggestion_task_map=task_map,
        datasets=datasets,
        libraries=libraries,
        models=models,
        predictions=predictions,
    )

    llm_context_result: MaterializationResult = materialize_llm_context(
        tasks=tasks,
        answers=answers,
        papers=papers,
        datasets=datasets,
        libraries=libraries,
        metrics=metrics,
        suggestions=suggestions,
        models=models,
        predictions=predictions,
        categories=categories,
        task_types=task_types,
        costs=costs,
    )
    llm_context_archives: list[LLMContextArchiveSummary] = llm_context_result.preset_summaries

    dashboard_data: DashboardData = DashboardData(
        tasks=tasks,
        costs=costs,
        machines=machines,
        suggestions=suggestions,
        suggestion_task_map=task_map,
        answers=answers,
        papers=papers,
        datasets=datasets,
        models=models,
        predictions=predictions,
        libraries=libraries,
        metrics=metrics,
        metric_results=metric_results,
        task_types=task_types,
        categories=categories,
        llm_context_archives=llm_context_archives,
        news_days=news_days,
    )
    materialize_dashboard(data=dashboard_data)

    print("Done.")


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description=("Materialize aggregator outputs as markdown section folders in overview/"),
    )
    parser.parse_args()
    materialize_all()


if __name__ == "__main__":
    main()
