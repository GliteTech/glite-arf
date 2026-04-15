"""Machine provisioning overview formatting."""

from pathlib import Path

from arf.scripts.aggregators.aggregate_machines import (
    MachineAggregation,
    MachineSummary,
    TaskMachineInfo,
)
from arf.scripts.overview.common import (
    normalize_markdown,
    overview_section_readme,
    task_link,
    write_file,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REL: str = "../../"
SECTION_NAME: str = "machines"
MACHINES_README: Path = overview_section_readme(section_name=SECTION_NAME)


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def _format_summary_table(*, summary: MachineSummary) -> list[str]:
    prov_time: str = (
        f"{summary.avg_provisioning_seconds:.0f}s"
        if summary.avg_provisioning_seconds is not None
        else "N/A"
    )
    lines: list[str] = [
        "## Summary",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Total machines | {summary.total_machines} |",
        f"| Total failed attempts | {summary.total_failed_attempts} |",
        f"| Failure rate | {summary.failure_rate:.1%} |",
        f"| Avg provisioning time | {prov_time} |",
        f"| Total cost | ${summary.total_cost_usd:.2f} |",
        f"| Total wasted cost | ${summary.total_wasted_cost_usd:.2f} |",
        "",
    ]
    return lines


def _format_gpu_tier_costs(*, gpu_tier_costs: dict[str, float]) -> list[str]:
    if len(gpu_tier_costs) == 0:
        return []

    sorted_tiers: list[tuple[str, float]] = sorted(
        gpu_tier_costs.items(),
        key=lambda x: x[1],
        reverse=True,
    )
    lines: list[str] = [
        "## Cost by GPU Tier",
        "",
        "| GPU | Total Cost (USD) |",
        "|-----|-----------------|",
    ]
    for gpu, cost in sorted_tiers:
        lines.append(f"| {gpu} | ${cost:.2f} |")
    lines.append("")
    return lines


def _format_failure_reasons(*, failure_reasons: dict[str, int]) -> list[str]:
    if len(failure_reasons) == 0:
        return []

    sorted_reasons: list[tuple[str, int]] = sorted(
        failure_reasons.items(),
        key=lambda x: x[1],
        reverse=True,
    )
    lines: list[str] = [
        "## Failure Reasons",
        "",
        "| Reason | Count |",
        "|--------|-------|",
    ]
    for reason, count in sorted_reasons:
        lines.append(f"| {reason} | {count} |")
    lines.append("")
    return lines


def _format_task_table(*, tasks: list[TaskMachineInfo]) -> list[str]:
    if len(tasks) == 0:
        return ["No tasks used remote machines.", ""]

    lines: list[str] = [
        "## Tasks",
        "",
        "| Task | Machines | Cost (USD) | Failed | GPUs |",
        "|------|----------|------------|--------|------|",
    ]
    for task in tasks:
        gpu_str: str = ", ".join(task.gpu_models)
        lines.append(
            f"| {task_link(task_id=task.task_id, rel=_REL)}"
            f" | {task.machine_count}"
            f" | ${task.total_cost_usd:.2f}"
            f" | {task.total_failed}"
            f" | {gpu_str} |"
        )
    lines.append("")
    return lines


def _format_overview(*, aggregation: MachineAggregation) -> str:
    summary: MachineSummary = aggregation.summary
    lines: list[str] = [
        f"# Machine Provisioning ({summary.total_machines} machines)",
        "",
        f"**{summary.total_machines}** machines provisioned across"
        f" **{len(aggregation.tasks)}** tasks."
        f" Total cost: **${summary.total_cost_usd:.2f}**.",
        "",
    ]

    if summary.total_failed_attempts > 0:
        lines.append(
            f"**{summary.total_failed_attempts}** failed provisioning"
            f" attempts wasted **${summary.total_wasted_cost_usd:.2f}**"
            f" ({summary.failure_rate:.1%} failure rate)."
        )
        lines.append("")

    lines.extend(_format_summary_table(summary=summary))
    lines.extend(
        _format_gpu_tier_costs(gpu_tier_costs=summary.gpu_tier_costs),
    )
    lines.extend(
        _format_failure_reasons(
            failure_reasons=summary.failure_reasons,
        ),
    )
    lines.extend(_format_task_table(tasks=aggregation.tasks))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Materialization
# ---------------------------------------------------------------------------


def materialize_machines(*, aggregation: MachineAggregation) -> None:
    write_file(
        file_path=MACHINES_README,
        content=normalize_markdown(
            content=_format_overview(aggregation=aggregation),
        ),
    )
