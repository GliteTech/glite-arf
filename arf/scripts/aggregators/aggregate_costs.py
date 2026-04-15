"""Aggregate task costs together with the project budget state.

Reads `project/budget.json` and every valid `results/costs.json` file, then reports
project-level spend, budget left, threshold status, and per-task cost summaries.

Aggregator version: 1
"""

import argparse
import json
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, TypeGuard

from arf.scripts.aggregators.aggregate_tasks import (
    ALL_TASK_STATUSES,
    TaskInfoFull,
    aggregate_tasks_full,
)
from arf.scripts.aggregators.common.cli import (
    DETAIL_LEVEL_FULL,
    DETAIL_LEVEL_SHORT,
    OUTPUT_FORMAT_IDS,
    OUTPUT_FORMAT_JSON,
    OUTPUT_FORMAT_MARKDOWN,
    add_detail_level_arg,
    add_output_format_arg,
)
from arf.scripts.verificators.common.json_utils import load_json_file
from arf.scripts.verificators.common.paths import costs_path
from arf.scripts.verificators.common.project_budget import (
    ProjectBudgetModel,
    budget_threshold_usd,
    load_project_budget,
    normalize_service_key,
    service_aliases,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

COSTS_FIELD_TOTAL: str = "total_cost_usd"
COSTS_FIELD_BREAKDOWN: str = "breakdown"
COSTS_FIELD_COST_USD: str = "cost_usd"
COSTS_FIELD_SERVICES: str = "services"
COSTS_FIELD_BUDGET_LIMIT: str = "budget_limit"
COSTS_FIELD_NOTE: str = "note"
COSTS_FIELD_DESCRIPTION: str = "description"

MISSING_BUDGET_ERROR: str = "project/budget.json is missing or invalid"
MISSING_COSTS_REASON: str = "results/costs.json is missing or invalid"
INVALID_TOTAL_REASON: str = "results/costs.json missing a numeric total_cost_usd"
INVALID_BREAKDOWN_REASON: str = "results/costs.json missing a valid breakdown object"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class BudgetInfo:
    total_budget: float
    currency: str
    per_task_default_limit: float
    available_services: list[str]
    warn_at_percent: int
    stop_at_percent: int
    warn_threshold_usd: float
    stop_threshold_usd: float


@dataclass(frozen=True, slots=True)
class CostSummary:
    discovered_task_count: int
    cost_record_count: int
    skipped_task_count: int
    nonzero_cost_task_count: int
    total_cost_usd: float
    budget_left_usd: float
    budget_left_before_warn_usd: float
    budget_left_before_stop_usd: float
    spent_percent: float
    warn_threshold_reached: bool
    stop_threshold_reached: bool
    tasks_over_limit: list[str]


@dataclass(frozen=True, slots=True)
class SkippedTaskCost:
    task_id: str
    reason: str


@dataclass(frozen=True, slots=True)
class TaskCostInfoShort:
    task_id: str
    task_index: int
    name: str
    status: str
    total_cost_usd: float
    effective_budget_limit_usd: float
    exceeds_budget_limit: bool


@dataclass(frozen=True, slots=True)
class TaskCostInfoFull:
    task_id: str
    task_index: int
    name: str
    status: str
    total_cost_usd: float
    task_budget_limit_usd: float | None
    effective_budget_limit_usd: float
    exceeds_budget_limit: bool
    cost_breakdown: dict[str, float]
    service_breakdown: dict[str, float]
    note: str | None


@dataclass(frozen=True, slots=True)
class CostAggregationShort:
    budget: BudgetInfo
    summary: CostSummary
    tasks: list[TaskCostInfoShort]
    skipped_tasks: list[SkippedTaskCost]


@dataclass(frozen=True, slots=True)
class CostAggregationFull:
    budget: BudgetInfo
    summary: CostSummary
    breakdown_totals: dict[str, float]
    service_totals: dict[str, float]
    tasks: list[TaskCostInfoFull]
    skipped_tasks: list[SkippedTaskCost]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _is_number(value: object) -> TypeGuard[int | float]:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _sorted_cost_map(*, costs: dict[str, float]) -> dict[str, float]:
    pairs: list[tuple[str, float]] = sorted(
        costs.items(),
        key=lambda item: (-item[1], item[0]),
    )
    return {key: value for key, value in pairs}


def _extract_cost_value(*, value: object) -> float | None:
    if _is_number(value):
        return float(value)
    if isinstance(value, dict):
        nested_cost: object = value.get(COSTS_FIELD_COST_USD)
        if _is_number(nested_cost):
            return float(nested_cost)
    return None


def _extract_breakdown_totals(*, costs_data: dict[str, Any]) -> dict[str, float] | None:
    breakdown: object = costs_data.get(COSTS_FIELD_BREAKDOWN)
    if not isinstance(breakdown, dict):
        return None

    totals: dict[str, float] = {}
    for key, value in breakdown.items():
        cost_value: float | None = _extract_cost_value(value=value)
        if cost_value is None:
            continue
        totals[key] = cost_value
    return _sorted_cost_map(costs=totals)


def _infer_service_from_key(
    *,
    key: str,
    available_services: list[str],
) -> str | None:
    normalized_key: str = normalize_service_key(value=key)
    best_match: str | None = None
    best_length: int = -1

    for service in available_services:
        for alias in service_aliases(service=service):
            normalized_alias: str = normalize_service_key(value=alias)
            if len(normalized_alias) == 0:
                continue
            if not normalized_key.startswith(normalized_alias):
                continue
            if len(normalized_alias) <= best_length:
                continue
            best_match = service
            best_length = len(normalized_alias)

    return best_match


def _extract_service_breakdown(
    *,
    costs_data: dict[str, Any],
    breakdown_totals: dict[str, float],
    available_services: list[str],
) -> dict[str, float]:
    services: object = costs_data.get(COSTS_FIELD_SERVICES)
    if isinstance(services, dict):
        direct_totals: dict[str, float] = {}
        for key, value in services.items():
            if not _is_number(value):
                continue
            direct_totals[key] = float(value)
        if len(direct_totals) > 0:
            return _sorted_cost_map(costs=direct_totals)

    inferred: dict[str, float] = {}
    for key, value in breakdown_totals.items():
        service: str | None = _infer_service_from_key(
            key=key,
            available_services=available_services,
        )
        if service is None:
            continue
        inferred[service] = inferred.get(service, 0.0) + value

    return _sorted_cost_map(costs=inferred)


def _load_task_cost(
    *,
    task: TaskInfoFull,
    budget: ProjectBudgetModel,
) -> TaskCostInfoFull | SkippedTaskCost:
    file_path: Path = costs_path(task_id=task.task_id)
    if not file_path.exists():
        return SkippedTaskCost(task_id=task.task_id, reason=MISSING_COSTS_REASON)

    costs_data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if costs_data is None:
        return SkippedTaskCost(task_id=task.task_id, reason=MISSING_COSTS_REASON)

    total_cost: object = costs_data.get(COSTS_FIELD_TOTAL)
    if not _is_number(total_cost):
        return SkippedTaskCost(task_id=task.task_id, reason=INVALID_TOTAL_REASON)

    breakdown_totals: dict[str, float] | None = _extract_breakdown_totals(costs_data=costs_data)
    if breakdown_totals is None:
        return SkippedTaskCost(task_id=task.task_id, reason=INVALID_BREAKDOWN_REASON)

    service_breakdown: dict[str, float] = _extract_service_breakdown(
        costs_data=costs_data,
        breakdown_totals=breakdown_totals,
        available_services=budget.available_services,
    )

    task_budget_limit_usd: float | None = None
    raw_budget_limit: object = costs_data.get(COSTS_FIELD_BUDGET_LIMIT)
    if _is_number(raw_budget_limit):
        task_budget_limit_usd = float(raw_budget_limit)

    effective_limit: float = (
        task_budget_limit_usd
        if task_budget_limit_usd is not None
        else budget.per_task_default_limit
    )

    note: str | None = None
    raw_note: object = costs_data.get(COSTS_FIELD_NOTE)
    if isinstance(raw_note, str):
        note = raw_note

    total_cost_usd: float = float(total_cost)
    return TaskCostInfoFull(
        task_id=task.task_id,
        task_index=task.task_index,
        name=task.name,
        status=task.status,
        total_cost_usd=total_cost_usd,
        task_budget_limit_usd=task_budget_limit_usd,
        effective_budget_limit_usd=effective_limit,
        exceeds_budget_limit=total_cost_usd > effective_limit,
        cost_breakdown=breakdown_totals,
        service_breakdown=service_breakdown,
        note=note,
    )


def _build_budget_info(*, budget: ProjectBudgetModel) -> BudgetInfo:
    warn_threshold: float = budget_threshold_usd(
        total_budget=budget.total_budget,
        threshold_percent=budget.alerts.warn_at_percent,
    )
    stop_threshold: float = budget_threshold_usd(
        total_budget=budget.total_budget,
        threshold_percent=budget.alerts.stop_at_percent,
    )
    return BudgetInfo(
        total_budget=budget.total_budget,
        currency=budget.currency,
        per_task_default_limit=budget.per_task_default_limit,
        available_services=list(budget.available_services),
        warn_at_percent=budget.alerts.warn_at_percent,
        stop_at_percent=budget.alerts.stop_at_percent,
        warn_threshold_usd=warn_threshold,
        stop_threshold_usd=stop_threshold,
    )


def _build_summary(
    *,
    budget: BudgetInfo,
    discovered_task_count: int,
    tasks: list[TaskCostInfoFull],
    skipped_tasks: list[SkippedTaskCost],
) -> CostSummary:
    total_cost_usd: float = sum(task.total_cost_usd for task in tasks)
    spent_percent: float = 0.0
    if budget.total_budget > 0:
        spent_percent = total_cost_usd / budget.total_budget * 100.0

    budget_left_usd: float = max(budget.total_budget - total_cost_usd, 0.0)
    budget_left_before_warn_usd: float = max(budget.warn_threshold_usd - total_cost_usd, 0.0)
    budget_left_before_stop_usd: float = max(budget.stop_threshold_usd - total_cost_usd, 0.0)

    tasks_over_limit: list[str] = [task.task_id for task in tasks if task.exceeds_budget_limit]

    return CostSummary(
        discovered_task_count=discovered_task_count,
        cost_record_count=len(tasks),
        skipped_task_count=len(skipped_tasks),
        nonzero_cost_task_count=sum(1 for task in tasks if task.total_cost_usd > 0),
        total_cost_usd=total_cost_usd,
        budget_left_usd=budget_left_usd,
        budget_left_before_warn_usd=budget_left_before_warn_usd,
        budget_left_before_stop_usd=budget_left_before_stop_usd,
        spent_percent=spent_percent,
        warn_threshold_reached=total_cost_usd >= budget.warn_threshold_usd,
        stop_threshold_reached=total_cost_usd >= budget.stop_threshold_usd,
        tasks_over_limit=tasks_over_limit,
    )


def _aggregate_cost_maps(
    *,
    tasks: list[TaskCostInfoFull],
    accessor: Callable[[TaskCostInfoFull], dict[str, float]],
) -> dict[str, float]:
    totals: dict[str, float] = {}
    for task in tasks:
        cost_map: dict[str, float] = accessor(task)
        for key, value in cost_map.items():
            totals[key] = totals.get(key, 0.0) + value
    return _sorted_cost_map(costs=totals)


def _to_short(*, task: TaskCostInfoFull) -> TaskCostInfoShort:
    return TaskCostInfoShort(
        task_id=task.task_id,
        task_index=task.task_index,
        name=task.name,
        status=task.status,
        total_cost_usd=task.total_cost_usd,
        effective_budget_limit_usd=task.effective_budget_limit_usd,
        exceeds_budget_limit=task.exceeds_budget_limit,
    )


def _aggregate_full(
    *,
    filter_statuses: list[str] | None = None,
    filter_ids: list[str] | None = None,
) -> CostAggregationFull:
    budget: ProjectBudgetModel | None = load_project_budget()
    if budget is None:
        raise RuntimeError(MISSING_BUDGET_ERROR)

    discovered_tasks: list[TaskInfoFull] = aggregate_tasks_full(
        filter_statuses=filter_statuses,
        filter_ids=filter_ids,
    )

    loaded_tasks: list[TaskCostInfoFull] = []
    skipped_tasks: list[SkippedTaskCost] = []
    for task in discovered_tasks:
        loaded: TaskCostInfoFull | SkippedTaskCost = _load_task_cost(task=task, budget=budget)
        if isinstance(loaded, TaskCostInfoFull):
            loaded_tasks.append(loaded)
        else:
            skipped_tasks.append(loaded)

    loaded_tasks.sort(key=lambda task: task.task_index)

    budget_info: BudgetInfo = _build_budget_info(budget=budget)
    summary: CostSummary = _build_summary(
        budget=budget_info,
        discovered_task_count=len(discovered_tasks),
        tasks=loaded_tasks,
        skipped_tasks=skipped_tasks,
    )

    return CostAggregationFull(
        budget=budget_info,
        summary=summary,
        breakdown_totals=_aggregate_cost_maps(
            tasks=loaded_tasks,
            accessor=lambda t: t.cost_breakdown,
        ),
        service_totals=_aggregate_cost_maps(
            tasks=loaded_tasks,
            accessor=lambda t: t.service_breakdown,
        ),
        tasks=loaded_tasks,
        skipped_tasks=skipped_tasks,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def aggregate_costs_short(
    *,
    filter_statuses: list[str] | None = None,
    filter_ids: list[str] | None = None,
) -> CostAggregationShort:
    full: CostAggregationFull = _aggregate_full(
        filter_statuses=filter_statuses,
        filter_ids=filter_ids,
    )
    return CostAggregationShort(
        budget=full.budget,
        summary=full.summary,
        tasks=[_to_short(task=task) for task in full.tasks],
        skipped_tasks=list(full.skipped_tasks),
    )


def aggregate_costs_full(
    *,
    filter_statuses: list[str] | None = None,
    filter_ids: list[str] | None = None,
) -> CostAggregationFull:
    return _aggregate_full(
        filter_statuses=filter_statuses,
        filter_ids=filter_ids,
    )


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def _format_short_json(*, aggregation: CostAggregationShort) -> str:
    return json.dumps(asdict(aggregation), indent=2, ensure_ascii=False)


def _format_full_json(*, aggregation: CostAggregationFull) -> str:
    return json.dumps(asdict(aggregation), indent=2, ensure_ascii=False)


def _format_budget_table(*, budget: BudgetInfo, summary: CostSummary) -> list[str]:
    lines: list[str] = [
        "| Field | Value |",
        "|-------|-------|",
        f"| Total budget | ${budget.total_budget:.2f} {budget.currency} |",
        f"| Total spent | ${summary.total_cost_usd:.2f} {budget.currency} |",
        f"| Budget left | ${summary.budget_left_usd:.2f} {budget.currency} |",
        (
            "| Budget left before stop threshold | "
            f"${summary.budget_left_before_stop_usd:.2f} {budget.currency} |"
        ),
        f"| Spent percent | {summary.spent_percent:.2f}% |",
        f"| Warn threshold | {budget.warn_at_percent}% (${budget.warn_threshold_usd:.2f}) |",
        f"| Stop threshold | {budget.stop_at_percent}% (${budget.stop_threshold_usd:.2f}) |",
        f"| Default per-task limit | ${budget.per_task_default_limit:.2f} {budget.currency} |",
    ]
    return lines


def _format_cost_map_section(
    *,
    heading: str,
    cost_map: dict[str, float],
) -> list[str]:
    if len(cost_map) == 0:
        return [f"## {heading}", "", "No entries found.", ""]

    lines: list[str] = [f"## {heading}", ""]
    lines.append("| Key | Cost (USD) |")
    lines.append("|-----|------------|")
    for key, value in cost_map.items():
        lines.append(f"| `{key}` | ${value:.2f} |")
    lines.append("")
    return lines


def _format_skipped_tasks(*, skipped_tasks: list[SkippedTaskCost]) -> list[str]:
    if len(skipped_tasks) == 0:
        return []

    lines: list[str] = ["## Skipped Tasks", ""]
    lines.append("| Task ID | Reason |")
    lines.append("|---------|--------|")
    for skipped in skipped_tasks:
        lines.append(f"| `{skipped.task_id}` | {skipped.reason} |")
    lines.append("")
    return lines


def _format_short_markdown(*, aggregation: CostAggregationShort) -> str:
    lines: list[str] = [
        "# Project Costs",
        "",
        (
            f"Spent ${aggregation.summary.total_cost_usd:.2f} of "
            f"${aggregation.budget.total_budget:.2f} {aggregation.budget.currency}. "
            f"${aggregation.summary.budget_left_usd:.2f} remains."
        ),
        "",
        "## Budget Summary",
        "",
        *_format_budget_table(
            budget=aggregation.budget,
            summary=aggregation.summary,
        ),
        "",
        "## Task Costs",
        "",
        "| Task ID | Name | Status | Cost (USD) | Limit (USD) | Over limit |",
        "|---------|------|--------|------------|-------------|------------|",
    ]

    for task in aggregation.tasks:
        over_limit: str = "yes" if task.exceeds_budget_limit else "no"
        lines.append(
            "| "
            f"`{task.task_id}` | {task.name} | {task.status} | ${task.total_cost_usd:.2f} | "
            f"${task.effective_budget_limit_usd:.2f} | {over_limit} |"
        )

    lines.append("")
    lines.extend(_format_skipped_tasks(skipped_tasks=aggregation.skipped_tasks))
    return "\n".join(lines)


def _format_full_markdown(*, aggregation: CostAggregationFull) -> str:
    lines: list[str] = [
        "# Project Costs",
        "",
        (
            f"Spent ${aggregation.summary.total_cost_usd:.2f} of "
            f"${aggregation.budget.total_budget:.2f} {aggregation.budget.currency}. "
            f"${aggregation.summary.budget_left_usd:.2f} remains overall and "
            f"${aggregation.summary.budget_left_before_stop_usd:.2f} remains before the "
            f"{aggregation.budget.stop_at_percent}% stop threshold."
        ),
        "",
        "## Budget Summary",
        "",
        *_format_budget_table(
            budget=aggregation.budget,
            summary=aggregation.summary,
        ),
        "",
    ]

    lines.extend(
        _format_cost_map_section(
            heading="Service Totals",
            cost_map=aggregation.service_totals,
        ),
    )
    lines.extend(
        _format_cost_map_section(
            heading="Breakdown Totals",
            cost_map=aggregation.breakdown_totals,
        ),
    )

    lines.append("## Task Costs")
    lines.append("")
    lines.append("| Task ID | Name | Status | Cost (USD) | Limit (USD) | Over limit |")
    lines.append("|---------|------|--------|------------|-------------|------------|")
    for task in aggregation.tasks:
        over_limit = "yes" if task.exceeds_budget_limit else "no"
        lines.append(
            "| "
            f"`{task.task_id}` | {task.name} | {task.status} | ${task.total_cost_usd:.2f} | "
            f"${task.effective_budget_limit_usd:.2f} | {over_limit} |"
        )
    lines.append("")

    for task in aggregation.tasks:
        lines.append(f"### {task.task_id}: {task.name}")
        lines.append("")
        lines.append(f"* **Status**: {task.status}")
        lines.append(f"* **Total cost**: ${task.total_cost_usd:.2f}")
        if task.task_budget_limit_usd is not None:
            lines.append(f"* **Task-specific budget limit**: ${task.task_budget_limit_usd:.2f}")
        lines.append(f"* **Effective budget limit**: ${task.effective_budget_limit_usd:.2f}")
        lines.append(f"* **Exceeds budget limit**: {'yes' if task.exceeds_budget_limit else 'no'}")
        if task.note is not None:
            lines.append(f"* **Note**: {task.note}")
        lines.append("")

        if len(task.service_breakdown) > 0:
            lines.append("| Service | Cost (USD) |")
            lines.append("|---------|------------|")
            for service, value in task.service_breakdown.items():
                lines.append(f"| `{service}` | ${value:.2f} |")
            lines.append("")

        if len(task.cost_breakdown) > 0:
            lines.append("| Breakdown key | Cost (USD) |")
            lines.append("|---------------|------------|")
            for key, value in task.cost_breakdown.items():
                lines.append(f"| `{key}` | ${value:.2f} |")
            lines.append("")

    lines.extend(_format_skipped_tasks(skipped_tasks=aggregation.skipped_tasks))
    return "\n".join(lines)


def _format_ids(*, aggregation: CostAggregationShort) -> str:
    return "\n".join(task.task_id for task in aggregation.tasks)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _add_filter_args(*, parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--status",
        nargs="+",
        default=None,
        help=f"Filter by task status ({', '.join(ALL_TASK_STATUSES)})",
    )
    parser.add_argument(
        "--ids",
        nargs="+",
        default=None,
        help="Filter by task ID (exact match)",
    )


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Aggregate project costs and remaining budget",
    )
    add_output_format_arg(parser=parser)
    add_detail_level_arg(parser=parser)
    _add_filter_args(parser=parser)
    args: argparse.Namespace = parser.parse_args()

    try:
        if args.detail == DETAIL_LEVEL_SHORT:
            aggregation_short: CostAggregationShort = aggregate_costs_short(
                filter_statuses=args.status,
                filter_ids=args.ids,
            )
            if args.format == OUTPUT_FORMAT_JSON:
                print(_format_short_json(aggregation=aggregation_short))
            elif args.format == OUTPUT_FORMAT_MARKDOWN:
                print(_format_short_markdown(aggregation=aggregation_short))
            elif args.format == OUTPUT_FORMAT_IDS:
                print(_format_ids(aggregation=aggregation_short))
            else:
                print(f"Unknown format: {args.format}", file=sys.stderr)
                sys.exit(1)
        elif args.detail == DETAIL_LEVEL_FULL:
            aggregation_full: CostAggregationFull = aggregate_costs_full(
                filter_statuses=args.status,
                filter_ids=args.ids,
            )
            if args.format == OUTPUT_FORMAT_JSON:
                print(_format_full_json(aggregation=aggregation_full))
            elif args.format == OUTPUT_FORMAT_MARKDOWN:
                print(_format_full_markdown(aggregation=aggregation_full))
            elif args.format == OUTPUT_FORMAT_IDS:
                print(
                    _format_ids(
                        aggregation=CostAggregationShort(
                            budget=aggregation_full.budget,
                            summary=aggregation_full.summary,
                            tasks=[_to_short(task=task) for task in aggregation_full.tasks],
                            skipped_tasks=aggregation_full.skipped_tasks,
                        ),
                    ),
                )
            else:
                print(f"Unknown format: {args.format}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Unknown detail level: {args.detail}", file=sys.stderr)
            sys.exit(1)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
