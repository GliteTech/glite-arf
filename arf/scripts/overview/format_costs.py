"""Costs overview formatting."""

from pathlib import Path

from arf.scripts.aggregators.aggregate_costs import (
    CostAggregationFull,
    TaskCostInfoFull,
)
from arf.scripts.overview.common import (
    normalize_markdown,
    overview_section_readme,
    remove_file_if_exists,
    task_link,
    write_file,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REL: str = "../../"
SECTION_NAME: str = "costs"
COSTS_README: Path = overview_section_readme(section_name=SECTION_NAME)
COSTS_LEGACY_MARKDOWN_PATH: Path = COSTS_README.parent.parent / "costs.md"


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def _format_budget_summary(*, aggregation: CostAggregationFull) -> list[str]:
    budget = aggregation.budget
    summary = aggregation.summary
    lines: list[str] = [
        "## Budget Summary",
        "",
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
        f"| Tasks with cost records | {summary.cost_record_count} |",
        f"| Tasks with non-zero spend | {summary.nonzero_cost_task_count} |",
        f"| Skipped tasks | {summary.skipped_task_count} |",
        "",
    ]
    return lines


def _format_cost_map(
    *,
    heading: str,
    cost_map: dict[str, float],
) -> list[str]:
    lines: list[str] = [f"## {heading}", ""]
    if len(cost_map) == 0:
        lines.append("No entries found.")
        lines.append("")
        return lines

    lines.append("| Key | Cost (USD) |")
    lines.append("|-----|------------|")
    for key, value in cost_map.items():
        lines.append(f"| `{key}` | ${value:.2f} |")
    lines.append("")
    return lines


def _format_task_table(*, tasks: list[TaskCostInfoFull]) -> list[str]:
    lines: list[str] = [
        "## Task Spend",
        "",
    ]
    if len(tasks) == 0:
        lines.append("No task cost records found.")
        lines.append("")
        return lines

    lines.append("| Task | Status | Total (USD) | Limit (USD) | Over limit |")
    lines.append("|------|--------|-------------|-------------|------------|")
    for task in tasks:
        over_limit: str = "yes" if task.exceeds_budget_limit else "no"
        lines.append(
            "| "
            f"{task_link(task_id=task.task_id, rel=_REL)} | {task.status} | "
            f"${task.total_cost_usd:.2f} | ${task.effective_budget_limit_usd:.2f} | "
            f"{over_limit} |"
        )
    lines.append("")
    return lines


def _format_skipped_tasks(*, aggregation: CostAggregationFull) -> list[str]:
    if len(aggregation.skipped_tasks) == 0:
        return []

    lines: list[str] = ["## Skipped Tasks", ""]
    lines.append("| Task ID | Reason |")
    lines.append("|---------|--------|")
    for skipped in aggregation.skipped_tasks:
        lines.append(f"| `{skipped.task_id}` | {skipped.reason} |")
    lines.append("")
    return lines


def _format_overview(*, aggregation: CostAggregationFull) -> str:
    lines: list[str] = [
        "# Project Costs",
        "",
        f"Spent ${aggregation.summary.total_cost_usd:.2f} of "
        f"${aggregation.budget.total_budget:.2f} {aggregation.budget.currency}. "
        f"${aggregation.summary.budget_left_usd:.2f} remains overall and "
        f"${aggregation.summary.budget_left_before_stop_usd:.2f} remains before the "
        f"{aggregation.budget.stop_at_percent}%",
        "stop threshold.",
        "",
    ]

    lines.extend(_format_budget_summary(aggregation=aggregation))
    lines.extend(_format_cost_map(heading="Service Totals", cost_map=aggregation.service_totals))
    lines.extend(
        _format_cost_map(heading="Breakdown Totals", cost_map=aggregation.breakdown_totals)
    )

    nonzero_tasks: list[TaskCostInfoFull] = [
        task for task in aggregation.tasks if task.total_cost_usd > 0
    ]
    zero_cost_count: int = len(aggregation.tasks) - len(nonzero_tasks)
    if zero_cost_count > 0:
        lines.append(
            f"{zero_cost_count} task cost record(s) are zero-cost and omitted from the "
            "main spend table."
        )
        lines.append("")

    lines.extend(_format_task_table(tasks=nonzero_tasks))
    lines.extend(_format_skipped_tasks(aggregation=aggregation))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Materialization
# ---------------------------------------------------------------------------


def materialize_costs(*, aggregation: CostAggregationFull) -> None:
    write_file(
        file_path=COSTS_README,
        content=normalize_markdown(
            content=_format_overview(aggregation=aggregation),
        ),
    )
    remove_file_if_exists(file_path=COSTS_LEGACY_MARKDOWN_PATH)
