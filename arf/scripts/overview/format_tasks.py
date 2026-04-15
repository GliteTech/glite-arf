"""Task overview formatting with by-status and by-date-added views."""

import json
import re
import textwrap
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from arf.scripts.aggregators.aggregate_metrics import (
    MetricInfoShort,
    aggregate_metrics_short,
)
from arf.scripts.aggregators.aggregate_tasks import (
    TASK_STATUS_CANCELLED,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_INTERVENTION_BLOCKED,
    TASK_STATUS_NOT_STARTED,
    TASK_STATUS_PERMANENTLY_FAILED,
    StepProgressSummary,
    TaskInfoFull,
)
from arf.scripts.overview.common import (
    BY_DATE_ADDED_VIEW,
    BY_STATUS_VIEW,
    EMPTY_MARKDOWN_VALUE,
    OVERVIEW_TASK_PAGES_PATH,
    README_FILE_NAME,
    RESULTS_DETAILED_FILE_NAME,
    RESULTS_SEGMENT,
    TASKS_SEGMENT,
    DateGroup,
    group_items_by_date,
    normalize_markdown,
    overview_legacy_markdown_path,
    overview_section_readme,
    overview_section_view_dir,
    overview_section_view_readme,
    remove_dir_if_exists,
    remove_file_if_exists,
    results_detailed_path,
    rewrite_embedded_paths,
    task_link,
    write_file,
)
from arf.scripts.overview.paths import overview_repo_task_path

SECTION_NAME: str = TASKS_SEGMENT
TASKS_README: Path = overview_section_readme(section_name=SECTION_NAME)
TASKS_BY_STATUS_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=BY_STATUS_VIEW,
)
TASKS_BY_DATE_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=BY_DATE_ADDED_VIEW,
)
TASKS_BY_DATE_README: Path = overview_section_view_readme(
    section_name=SECTION_NAME,
    view_name=BY_DATE_ADDED_VIEW,
)

STATUS_EMOJI: dict[str, str] = {
    TASK_STATUS_COMPLETED: "\u2705",
    TASK_STATUS_IN_PROGRESS: "\u23f3",
    TASK_STATUS_NOT_STARTED: "\u23f9",
    TASK_STATUS_CANCELLED: "\u274c",
    TASK_STATUS_PERMANENTLY_FAILED: "\U0001f4a5",
    TASK_STATUS_INTERVENTION_BLOCKED: "\u26a0\ufe0f",
}

STATUS_DISPLAY_ORDER: list[str] = [
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_NOT_STARTED,
    TASK_STATUS_INTERVENTION_BLOCKED,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_CANCELLED,
    TASK_STATUS_PERMANENTLY_FAILED,
]

_SECTION_REL: str = "../../"
_STATUS_REL: str = "../../../"
_DATE_REL: str = "../../../"
_LIST_RE: re.Pattern[str] = re.compile(r"^([*-] |\d+\. )(.*)$")
_RESULTS_WRAP_WIDTH: int = 94


@dataclass(frozen=True, slots=True)
class TaskKeyMetric:
    metric_name: str
    emoji: str | None
    value: object


@dataclass(frozen=True, slots=True)
class _KeyMetricInfo:
    emoji: str


def _build_key_metrics_lookup() -> dict[str, _KeyMetricInfo]:
    metrics: list[MetricInfoShort] = aggregate_metrics_short()
    result: dict[str, _KeyMetricInfo] = {}
    for m in metrics:
        if m.is_key and m.emoji is not None:
            result[m.metric_key] = _KeyMetricInfo(emoji=m.emoji)
    return result


def _mermaid_node_id(*, task_id: str) -> str:
    return task_id.replace("-", "_")


COMPLETED_STATUSES: set[str] = {
    TASK_STATUS_COMPLETED,
    TASK_STATUS_CANCELLED,
    TASK_STATUS_PERMANENTLY_FAILED,
}


def _format_dependency_graph(*, tasks: list[TaskInfoFull]) -> str:
    task_map: dict[str, TaskInfoFull] = {task.task_id: task for task in tasks}
    active_ids: set[str] = {task.task_id for task in tasks if task.status not in COMPLETED_STATUSES}

    graph_ids: set[str] = set(active_ids)
    for task_id in active_ids:
        task: TaskInfoFull | None = task_map.get(task_id)
        if task is None:
            continue
        for dependency in task.dependencies:
            graph_ids.add(dependency)

    if len(graph_ids) == 0:
        return "## Dependency Graph\n\nAll tasks completed."

    lines: list[str] = ["## Dependency Graph", "", "```mermaid", "graph LR"]

    for task in tasks:
        if task.task_id not in graph_ids:
            continue
        node: str = _mermaid_node_id(task_id=task.task_id)
        emoji: str = STATUS_EMOJI.get(task.status, "")
        label: str = f"{emoji} {task.task_id}"
        lines.append(f'    {node}["{label}"]')

    lines.append("")
    for task in tasks:
        if task.task_id not in graph_ids:
            continue
        task_node: str = _mermaid_node_id(task_id=task.task_id)
        for dependency in task.dependencies:
            if dependency not in graph_ids:
                continue
            dependency_node: str = _mermaid_node_id(task_id=dependency)
            lines.append(f"    {dependency_node} --> {task_node}")

    lines.append("```")
    return "\n".join(lines)


def _format_task_detail(
    *,
    task: TaskInfoFull,
    rel: str,
    key_metrics_by_task: dict[str, list[TaskKeyMetric]] | None = None,
) -> str:
    emoji: str = STATUS_EMOJI.get(task.status, "")
    task_number: str = f"{task.task_index:04d}"
    title_html: str = f"<summary>{emoji} {task_number} — <strong>{task.name}</strong></summary>"

    if len(task.dependencies) == 0:
        dependencies_str: str = EMPTY_MARKDOWN_VALUE
    else:
        dependencies_str = ", ".join(
            task_link(task_id=dependency, rel=rel) for dependency in task.dependencies
        )

    source_suggestion_str: str = (
        f"`{task.source_suggestion}`"
        if task.source_suggestion is not None
        else EMPTY_MARKDOWN_VALUE
    )
    effective_date_str: str = (
        task.effective_date if task.effective_date is not None else EMPTY_MARKDOWN_VALUE
    )
    expected_assets_str: str = ", ".join(
        f"{count} {kind}" for kind, count in task.expected_assets.items()
    )
    if len(expected_assets_str) == 0:
        expected_assets_str = EMPTY_MARKDOWN_VALUE

    detail_lines: list[str] = [
        "<details>",
        title_html,
        "",
        "| Field | Value |",
        "|---|---|",
        f"| **ID** | `{task.task_id}` |",
        f"| **Status** | {task.status} |",
        f"| **Effective date** | {effective_date_str} |",
        f"| **Dependencies** | {dependencies_str} |",
        f"| **Expected assets** | {expected_assets_str} |",
        f"| **Source suggestion** | {source_suggestion_str} |",
    ]

    if len(task.task_types) > 0:
        task_types_str: str = ", ".join(
            f"[`{task_type}`]({rel}meta/task_types/{task_type}/)" for task_type in task.task_types
        )
        detail_lines.append(f"| **Task types** | {task_types_str} |")

    if task.start_time is not None:
        detail_lines.append(f"| **Start time** | {task.start_time} |")
    if task.end_time is not None:
        detail_lines.append(f"| **End time** | {task.end_time} |")

    if task.step_progress is not None:
        progress: StepProgressSummary = task.step_progress
        progress_str: str = f"{progress.completed_steps}/{progress.total_steps}"
        if progress.current_step_name is not None:
            progress_str += f" (current: {progress.current_step_name})"
        detail_lines.append(f"| **Step progress** | {progress_str} |")

    if key_metrics_by_task is not None:
        task_key_metrics: list[TaskKeyMetric] = key_metrics_by_task.get(
            task.task_id,
            [],
        )
        if len(task_key_metrics) > 0:
            parts: list[str] = []
            for km in task_key_metrics:
                prefix: str = f"{km.emoji} " if km.emoji is not None else ""
                parts.append(f"{prefix}{km.metric_name}: **{km.value}**")
            detail_lines.append(
                f"| **Key metrics** | {', '.join(parts)} |",
            )

    detail_lines.append(
        f"| **Task page** | [{task.name}]({rel}{OVERVIEW_TASK_PAGES_PATH}/{task.task_id}.md) |",
    )
    detail_lines.append(
        f"| **Task folder** | [`{task.task_id}/`]({rel}{TASKS_SEGMENT}/{task.task_id}/) |",
    )

    report_path: Path = results_detailed_path(task_id=task.task_id)
    if report_path.exists():
        report_link: str = (
            f"{rel}{TASKS_SEGMENT}/{task.task_id}/{RESULTS_SEGMENT}/{RESULTS_DETAILED_FILE_NAME}"
        )
        detail_lines.append(
            f"| **Detailed report** | [{RESULTS_DETAILED_FILE_NAME}]({report_link}) |",
        )

    detail_lines.append("")
    detail_lines.append(task.long_description)

    if task.results_summary is not None:
        detail_lines.append("")
        detail_lines.append("**Results summary:**")
        detail_lines.append("")
        _append_results_summary(
            detail_lines=detail_lines,
            summary=task.results_summary,
        )

    detail_lines.append("")
    detail_lines.append("</details>")
    return "\n".join(detail_lines)


def _format_status_summary(*, tasks: list[TaskInfoFull]) -> str:
    counts: dict[str, int] = {}
    for task in tasks:
        counts[task.status] = counts.get(task.status, 0) + 1

    parts: list[str] = []
    for status in STATUS_DISPLAY_ORDER:
        count: int = counts.get(status, 0)
        if count > 0:
            emoji: str = STATUS_EMOJI.get(status, "")
            parts.append(f"{emoji} **{count} {status}**")

    return f"{len(tasks)} tasks. {', '.join(parts)}."


def _append_results_summary(
    *,
    detail_lines: list[str],
    summary: str,
) -> None:
    for raw_line in summary.splitlines()[:20]:
        stripped: str = raw_line.strip()
        if len(stripped) == 0:
            detail_lines.append(">")
            continue

        if stripped.startswith("#"):
            heading_text: str = stripped.lstrip("#").strip()
            wrapped_heading: str = textwrap.fill(
                text=f"**{heading_text}**",
                width=_RESULTS_WRAP_WIDTH,
                initial_indent="> ",
                subsequent_indent="> ",
                break_long_words=False,
                break_on_hyphens=False,
            )
            detail_lines.extend(wrapped_heading.splitlines())
            continue

        if stripped.startswith(("|", "<", "#", "```")):
            detail_lines.append(f"> {stripped}")
            continue

        list_match: re.Match[str] | None = _LIST_RE.match(stripped)
        if list_match is not None:
            marker, text = list_match.groups()
            wrapped: str = textwrap.fill(
                text=text,
                width=_RESULTS_WRAP_WIDTH,
                initial_indent=f"> {marker}",
                subsequent_indent=f"> {' ' * len(marker)}",
                break_long_words=False,
                break_on_hyphens=False,
            )
            detail_lines.extend(wrapped.splitlines())
            continue

        wrapped = textwrap.fill(
            text=stripped,
            width=_RESULTS_WRAP_WIDTH,
            initial_indent="> ",
            subsequent_indent="> ",
            break_long_words=False,
            break_on_hyphens=False,
        )
        detail_lines.extend(wrapped.splitlines())


def _append_task_status_sections(
    *,
    lines: list[str],
    tasks: list[TaskInfoFull],
    rel: str,
    key_metrics_by_task: dict[str, list[TaskKeyMetric]] | None = None,
) -> None:
    _REVERSE_STATUSES: set[str] = {TASK_STATUS_NOT_STARTED, TASK_STATUS_COMPLETED}
    for status in STATUS_DISPLAY_ORDER:
        group: list[TaskInfoFull] = [task for task in tasks if task.status == status]
        if len(group) == 0:
            continue
        emoji: str = STATUS_EMOJI.get(status, "")
        lines.append("")
        lines.append(f"## {emoji} {status.replace('_', ' ').title()}")
        lines.append("")
        should_reverse: bool = status in _REVERSE_STATUSES
        for task in sorted(
            group,
            key=lambda item: (item.task_index, item.task_id),
            reverse=should_reverse,
        ):
            lines.append(
                _format_task_detail(
                    task=task,
                    rel=rel,
                    key_metrics_by_task=key_metrics_by_task,
                ),
            )
            lines.append("")


def _format_tasks_page(
    *,
    title: str,
    tasks: list[TaskInfoFull],
    rel: str,
    show_status_index: bool,
    show_date_index: bool,
    show_dependency_graph: bool,
    back_link: str | None,
    key_metrics_by_task: dict[str, list[TaskKeyMetric]] | None = None,
) -> str:
    lines: list[str] = [f"# {title}", "", _format_status_summary(tasks=tasks)]

    if back_link is not None:
        lines.append("")
        lines.append(f"[Back to all tasks]({back_link})")

    browse_links: list[str] = []
    if show_status_index:
        counts: dict[str, int] = {}
        for task in tasks:
            counts[task.status] = counts.get(task.status, 0) + 1
        status_links: list[str] = []
        for status in STATUS_DISPLAY_ORDER:
            if counts.get(status, 0) > 0:
                emoji: str = STATUS_EMOJI.get(status, "")
                status_links.append(f"[{emoji} `{status}`]({BY_STATUS_VIEW}/{status}.md)")
        if len(status_links) > 0:
            browse_links.append(f"By status: {', '.join(status_links)}")
    if show_date_index:
        browse_links.append(f"[By date added]({BY_DATE_ADDED_VIEW}/{README_FILE_NAME})")
    if len(browse_links) > 0:
        lines.append("")
        lines.append(f"**Browse by view**: {'; '.join(browse_links)}")

    if show_dependency_graph and len(tasks) > 0:
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(_format_dependency_graph(tasks=tasks))

    lines.append("")
    lines.append("---")
    _append_task_status_sections(
        lines=lines,
        tasks=tasks,
        rel=rel,
        key_metrics_by_task=key_metrics_by_task,
    )
    return "\n".join(lines)


def _format_tasks_by_date_page(*, tasks: list[TaskInfoFull]) -> str:
    if len(tasks) == 0:
        return "# Tasks by Date Added\n\nNo tasks found."

    date_groups: list[DateGroup[TaskInfoFull]] = group_items_by_date(
        items=tasks,
        get_date=lambda item: item.effective_date,
        sort_key=lambda item: (-item.task_index, item.task_id),
    )

    lines: list[str] = [
        "# Tasks by Date Added",
        "",
        f"{len(tasks)} tasks grouped by effective task date.",
        "",
        "[Back to all tasks](../README.md)",
        "",
        "---",
    ]

    for date_group in date_groups:
        lines.append("")
        lines.append(f"## {date_group.date} ({len(date_group.items)})")
        _append_task_status_sections(
            lines=lines,
            tasks=date_group.items,
            rel=_DATE_REL,
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Per-task detail pages: overview/tasks/task_pages/<task_id>.md
# ---------------------------------------------------------------------------

TASK_PAGES_VIEW: str = "task_pages"
TASK_PAGES_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=TASK_PAGES_VIEW,
)

_TASK_PAGE_REL: str = "../../../"


def _load_json_safe(*, path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _collect_task_categories(*, task_dir: Path) -> list[str]:
    assets_dir: Path = task_dir / "assets"
    if not assets_dir.is_dir():
        return []
    categories: set[str] = set()
    for kind_dir in assets_dir.iterdir():
        if not kind_dir.is_dir() or kind_dir.name.startswith("."):
            continue
        for asset_entry in kind_dir.iterdir():
            if not asset_entry.is_dir() or asset_entry.name.startswith("."):
                continue
            details: Any = _load_json_safe(
                path=asset_entry / "details.json",
            )
            if isinstance(details, dict):
                cats: object = details.get("categories")
                if isinstance(cats, list):
                    for cat in cats:
                        if isinstance(cat, str):
                            categories.add(cat)
    return sorted(categories)


def _format_duration(*, start: str, end: str) -> str:
    try:
        t_start: datetime = datetime.fromisoformat(
            start.replace("Z", "+00:00"),
        )
        t_end: datetime = datetime.fromisoformat(
            end.replace("Z", "+00:00"),
        )
        delta = t_end - t_start
        total_seconds: int = int(delta.total_seconds())
        if total_seconds < 60:
            return f"{total_seconds}s"
        minutes: int = total_seconds // 60
        hours: int = minutes // 60
        remaining_minutes: int = minutes % 60
        if hours == 0:
            return f"{minutes}m"
        return f"{hours}h {remaining_minutes}m"
    except (ValueError, TypeError):
        return EMPTY_MARKDOWN_VALUE


def _format_task_page(
    *,
    task: TaskInfoFull,
    rel: str,
    key_metrics: list[TaskKeyMetric],
    key_metrics_lookup: dict[str, _KeyMetricInfo],
) -> str:
    emoji: str = STATUS_EMOJI.get(task.status, "")
    task_dir: Path = overview_repo_task_path(task_id=task.task_id)
    task_folder_path: str = f"{TASKS_SEGMENT}/{task.task_id}"
    results_path: str = f"{task_folder_path}/{RESULTS_SEGMENT}"
    metrics_results_rel: str = "../../metrics-results"

    lines: list[str] = [
        f"# {emoji} {task.name}",
        "",
        "[Back to all tasks](../README.md)",
        "",
    ]

    # Key metrics banner
    if len(key_metrics) > 0:
        parts: list[str] = []
        for km in key_metrics:
            prefix: str = f"{km.emoji} " if km.emoji is not None else ""
            parts.append(f"{prefix}{km.metric_name}: **{km.value}**")
        lines.append(f"> {' | '.join(parts)}")
        lines.append("")

    # ---- Overview table ----
    lines.append("## Overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    lines.append(f"| **ID** | `{task.task_id}` |")
    lines.append(f"| **Status** | {emoji} {task.status} |")

    if task.start_time is not None:
        lines.append(f"| **Started** | {task.start_time} |")
    if task.end_time is not None:
        lines.append(f"| **Completed** | {task.end_time} |")
    if task.start_time is not None and task.end_time is not None:
        duration: str = _format_duration(
            start=task.start_time,
            end=task.end_time,
        )
        lines.append(f"| **Duration** | {duration} |")

    if len(task.dependencies) > 0:
        dep_str: str = ", ".join(task_link(task_id=dep, rel=rel) for dep in task.dependencies)
        lines.append(f"| **Dependencies** | {dep_str} |")

    if task.source_suggestion is not None:
        lines.append(
            f"| **Source suggestion** | `{task.source_suggestion}` |",
        )

    if len(task.task_types) > 0:
        tt_str: str = ", ".join(f"`{tt}`" for tt in task.task_types)
        lines.append(f"| **Task types** | {tt_str} |")

    # Categories from assets
    task_categories: list[str] = _collect_task_categories(
        task_dir=task_dir,
    )
    if len(task_categories) > 0:
        cat_links: str = ", ".join(
            f"[`{cat}`](../../by-category/{cat}.md)" for cat in task_categories
        )
        lines.append(f"| **Categories** | {cat_links} |")

    if len(task.expected_assets) > 0:
        ea_str: str = ", ".join(f"{count} {kind}" for kind, count in task.expected_assets.items())
        lines.append(f"| **Expected assets** | {ea_str} |")

    if task.step_progress is not None:
        progress: StepProgressSummary = task.step_progress
        progress_str: str = f"{progress.completed_steps}/{progress.total_steps}"
        if progress.current_step_name is not None:
            progress_str += f" (current: {progress.current_step_name})"
        lines.append(f"| **Step progress** | {progress_str} |")

    # Cost
    costs_data: Any = _load_json_safe(
        path=task_dir / RESULTS_SEGMENT / "costs.json",
    )
    if isinstance(costs_data, dict):
        total_cost: object = costs_data.get("total_cost_usd")
        if isinstance(total_cost, int | float) and total_cost > 0:
            lines.append(f"| **Cost** | **${total_cost:.2f}** |")

    # File links
    lines.append(
        f"| **Task folder** | [`{task.task_id}/`]({rel}{task_folder_path}/) |",
    )
    report_full_path: Path = results_detailed_path(
        task_id=task.task_id,
    )
    if report_full_path.exists():
        lines.append(
            f"| **Detailed results** |"
            f" [`results_detailed.md`]"
            f"({rel}{results_path}/results_detailed.md) |",
        )

    lines.append("")

    # ---- Task description (collapsed, right after overview) ----
    lines.append("<details>")
    lines.append(
        "<summary><strong>Task Description</strong></summary>",
    )
    lines.append("")
    lines.append(
        f"*Source: [`task_description.md`]({rel}{task_folder_path}/task_description.md)*",
    )
    lines.append("")
    lines.append(task.long_description)
    lines.append("")
    lines.append("</details>")
    lines.append("")

    # ---- Costs breakdown ----
    if isinstance(costs_data, dict):
        total_cost_val: object = costs_data.get("total_cost_usd")
        breakdown: object = costs_data.get("breakdown")
        if (
            isinstance(total_cost_val, int | float)
            and total_cost_val > 0
            and isinstance(breakdown, dict)
            and len(breakdown) > 0
        ):
            lines.append("## Costs")
            lines.append("")
            lines.append(f"**Total**: **${total_cost_val:.2f}**")
            lines.append("")
            lines.append("| Category | Amount |")
            lines.append("|----------|--------|")
            for cat_key, cat_val in breakdown.items():
                if isinstance(cat_val, int | float):
                    lines.append(f"| {cat_key} | ${cat_val:.2f} |")
                elif isinstance(cat_val, dict):
                    inner_cost: object = cat_val.get("cost_usd")
                    if isinstance(inner_cost, int | float):
                        lines.append(
                            f"| {cat_key} | ${inner_cost:.2f} |",
                        )
            lines.append("")

    # ---- Remote machines ----
    machines_data: Any = _load_json_safe(
        path=task_dir / RESULTS_SEGMENT / "remote_machines_used.json",
    )
    if isinstance(machines_data, list) and len(machines_data) > 0:
        lines.append("## Remote Machines")
        lines.append("")
        lines.append(
            "| Provider | GPU | Count | RAM | Duration | Cost |",
        )
        lines.append("|----------|-----|-------|-----|----------|------|")
        for machine in machines_data:
            if not isinstance(machine, dict):
                continue
            provider: str = str(
                machine.get("provider", EMPTY_MARKDOWN_VALUE),
            )
            gpu: str = str(machine.get("gpu", EMPTY_MARKDOWN_VALUE))
            gpu_count: object = machine.get("gpu_count", 1)
            ram_gb: object = machine.get("ram_gb", EMPTY_MARKDOWN_VALUE)
            dur_h: object = machine.get("duration_hours")
            dur_str: str = (
                f"{dur_h:.1f}h" if isinstance(dur_h, int | float) else EMPTY_MARKDOWN_VALUE
            )
            m_cost: object = machine.get("cost_usd")
            cost_str: str = (
                f"${m_cost:.2f}" if isinstance(m_cost, int | float) else EMPTY_MARKDOWN_VALUE
            )
            lines.append(
                f"| {provider} | {gpu} | {gpu_count} | {ram_gb} GB | {dur_str} | {cost_str} |",
            )
        lines.append("")

    # ---- Metrics ----
    metrics_data: Any = _load_json_safe(
        path=task_dir / RESULTS_SEGMENT / "metrics.json",
    )
    if isinstance(metrics_data, dict) and len(metrics_data) > 0:
        if "variants" in metrics_data:
            _append_variant_metrics(
                lines=lines,
                metrics_data=metrics_data,
                metrics_results_rel=metrics_results_rel,
                key_metrics_lookup=key_metrics_lookup,
            )
        else:
            _append_flat_metrics(
                lines=lines,
                metrics_data=metrics_data,
                metrics_results_rel=metrics_results_rel,
                key_metrics_lookup=key_metrics_lookup,
            )

    # ---- Assets produced ----
    _append_assets_produced(
        lines=lines,
        task_dir=task_dir,
        task_folder_path=task_folder_path,
        rel=rel,
    )

    # ---- Suggestions generated ----
    suggestions_data: Any = _load_json_safe(
        path=task_dir / RESULTS_SEGMENT / "suggestions.json",
    )
    if isinstance(suggestions_data, dict):
        sugg_list: object = suggestions_data.get("suggestions")
        if isinstance(sugg_list, list) and len(sugg_list) > 0:
            lines.append("## Suggestions Generated")
            lines.append("")
            for sugg in sugg_list:
                if not isinstance(sugg, dict):
                    continue
                title: str = str(sugg.get("title", "Untitled"))
                sugg_id: str = str(sugg.get("id", ""))
                description: str = str(
                    sugg.get("description", ""),
                )
                kind: str = str(sugg.get("kind", ""))
                priority: str = str(sugg.get("priority", ""))
                lines.append("<details>")
                lines.append(
                    f"<summary><strong>{title}</strong> ({sugg_id})</summary>",
                )
                lines.append("")
                if len(kind) > 0 or len(priority) > 0:
                    lines.append(
                        f"**Kind**: {kind} | **Priority**: {priority}",
                    )
                    lines.append("")
                if len(description) > 0:
                    lines.append(description)
                    lines.append("")
                lines.append("</details>")
                lines.append("")

    # ---- Research files ----
    research_dir: Path = task_dir / "research"
    if research_dir.is_dir():
        research_files: list[str] = sorted(
            f.name for f in research_dir.iterdir() if f.is_file() and f.suffix == ".md"
        )
        if len(research_files) > 0:
            lines.append("## Research")
            lines.append("")
            for rf in research_files:
                lines.append(
                    f"* [`{rf}`]({rel}{task_folder_path}/research/{rf})",
                )
            lines.append("")

    # ---- Results summary (collapsed) ----
    if task.results_summary is not None:
        lines.append("<details>")
        lines.append(
            "<summary><strong>Results Summary</strong></summary>",
        )
        lines.append("")
        lines.append(
            f"*Source: [`results_summary.md`]({rel}{results_path}/results_summary.md)*",
        )
        lines.append("")
        lines.append(task.results_summary)
        lines.append("")
        lines.append("</details>")
        lines.append("")

    # ---- Detailed results (collapsed) ----
    if report_full_path.exists():
        try:
            detailed_content: str = report_full_path.read_text(
                encoding="utf-8",
            )
            if len(detailed_content.strip()) > 0:
                detailed_content = rewrite_embedded_paths(
                    content=detailed_content,
                    source_dir=results_path,
                    target_rel=rel,
                )
                lines.append("<details>")
                lines.append(
                    "<summary><strong>Detailed Results</strong></summary>",
                )
                lines.append("")
                lines.append(
                    f"*Source: [`results_detailed.md`]({rel}{results_path}/results_detailed.md)*",
                )
                lines.append("")
                lines.append(detailed_content)
                lines.append("")
                lines.append("</details>")
                lines.append("")
        except OSError:
            pass

    # ---- Literature comparison (collapsed) ----
    compare_lit_path: Path = task_dir / RESULTS_SEGMENT / "compare_literature.md"
    if compare_lit_path.exists():
        try:
            compare_content: str = compare_lit_path.read_text(
                encoding="utf-8",
            )
            if len(compare_content.strip()) > 0:
                compare_content = rewrite_embedded_paths(
                    content=compare_content,
                    source_dir=results_path,
                    target_rel=rel,
                )
                lines.append("<details>")
                lines.append(
                    "<summary><strong>Literature Comparison</strong></summary>",
                )
                lines.append("")
                lines.append(
                    f"*Source: [`compare_literature.md`]"
                    f"({rel}{results_path}"
                    f"/compare_literature.md)*",
                )
                lines.append("")
                lines.append(compare_content)
                lines.append("")
                lines.append("</details>")
                lines.append("")
        except OSError:
            pass

    return "\n".join(lines)


def _sanitize_for_table(*, text: str) -> str:
    return " ".join(text.replace("\n", " ").replace("|", "/").split())


def _get_asset_display_name(
    *,
    asset_dir: Path,
    asset_name: str,
    kind: str,
) -> str:
    details: Any = _load_json_safe(
        path=asset_dir / asset_name / "details.json",
    )
    if not isinstance(details, dict):
        return asset_name
    raw: str | None = None
    if kind == "paper":
        title: object = details.get("title")
        if isinstance(title, str) and len(title) > 0:
            raw = title
    elif kind == "answer":
        question: object = details.get("question")
        if isinstance(question, str) and len(question) > 0:
            raw = question
        else:
            short_title: object = details.get("short_title")
            if isinstance(short_title, str) and len(short_title) > 0:
                raw = short_title
    else:
        name: object = details.get("name")
        if isinstance(name, str) and len(name) > 0:
            raw = name
    if raw is not None:
        return _sanitize_for_table(text=raw)
    return asset_name


def _get_asset_md_path(
    *,
    asset_dir: Path,
    asset_name: str,
    kind: str,
) -> str | None:
    details: Any = _load_json_safe(
        path=asset_dir / asset_name / "details.json",
    )
    if not isinstance(details, dict):
        return None
    if kind == "paper":
        md_file: object = details.get("summary_path")
    elif kind == "answer":
        md_file = details.get("full_answer_path")
    else:
        md_file = details.get("description_path")
    if isinstance(md_file, str) and len(md_file) > 0:
        full_path: Path = asset_dir / asset_name / md_file
        if full_path.exists():
            return md_file
    # Fallback: check common names
    for fallback in (
        "summary.md",
        "description.md",
        "full_answer.md",
    ):
        if (asset_dir / asset_name / fallback).exists():
            return fallback
    return None


def _append_assets_produced(
    *,
    lines: list[str],
    task_dir: Path,
    task_folder_path: str,
    rel: str,
) -> None:
    assets_dir: Path = task_dir / "assets"
    if not assets_dir.is_dir():
        return
    asset_rows: list[str] = []
    for kind_dir in sorted(assets_dir.iterdir()):
        if not kind_dir.is_dir() or kind_dir.name.startswith("."):
            continue
        kind: str = kind_dir.name
        asset_names: list[str] = sorted(
            e.name for e in kind_dir.iterdir() if e.is_dir() and not e.name.startswith(".")
        )
        for asset_name in asset_names:
            display_name: str = _get_asset_display_name(
                asset_dir=kind_dir,
                asset_name=asset_name,
                kind=kind,
            )
            asset_folder_link: str = (
                f"[{display_name}]({rel}{task_folder_path}/assets/{kind}/{asset_name}/)"
            )
            md_file: str | None = _get_asset_md_path(
                asset_dir=kind_dir,
                asset_name=asset_name,
                kind=kind,
            )
            md_link: str
            if md_file is not None:
                md_link = (
                    f"[`{md_file}`]({rel}{task_folder_path}/assets/{kind}/{asset_name}/{md_file})"
                )
            else:
                md_link = EMPTY_MARKDOWN_VALUE
            asset_rows.append(
                f"| {kind} | {asset_folder_link} | {md_link} |",
            )
    if len(asset_rows) > 0:
        lines.append("## Assets Produced")
        lines.append("")
        lines.append("| Type | Asset | Details |")
        lines.append("|------|-------|---------|")
        lines.extend(asset_rows)
        lines.append("")


def _metric_link(
    *,
    key: str,
    metrics_results_rel: str,
    emoji: str | None = None,
) -> str:
    prefix: str = f"{emoji} " if emoji is not None else ""
    return f"{prefix}[`{key}`]({metrics_results_rel}/{key}.md)"


def _sorted_metric_keys(
    *,
    raw_keys: list[str],
    key_metrics_lookup: dict[str, _KeyMetricInfo],
) -> list[str]:
    key_first: list[str] = [k for k in raw_keys if k in key_metrics_lookup]
    rest: list[str] = [k for k in raw_keys if k not in key_metrics_lookup]
    return key_first + rest


def _append_metric_rows(
    *,
    lines: list[str],
    metrics: dict[str, Any],
    metrics_results_rel: str,
    key_metrics_lookup: dict[str, _KeyMetricInfo],
    skip_keys: set[str] | None = None,
) -> bool:
    effective_skip: set[str] = skip_keys if skip_keys is not None else set()
    eligible_keys: list[str] = [
        k for k, v in metrics.items() if v is not None and k not in effective_skip
    ]
    sorted_keys: list[str] = _sorted_metric_keys(
        raw_keys=eligible_keys,
        key_metrics_lookup=key_metrics_lookup,
    )
    if len(sorted_keys) == 0:
        return False
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    for key in sorted_keys:
        info: _KeyMetricInfo | None = key_metrics_lookup.get(key)
        emoji: str | None = info.emoji if info is not None else None
        m_link: str = _metric_link(
            key=key,
            metrics_results_rel=metrics_results_rel,
            emoji=emoji,
        )
        lines.append(f"| {m_link} | **{metrics[key]}** |")
    return True


def _append_flat_metrics(
    *,
    lines: list[str],
    metrics_data: dict[str, Any],
    metrics_results_rel: str,
    key_metrics_lookup: dict[str, _KeyMetricInfo],
) -> None:
    lines.append("## Metrics")
    lines.append("")
    has_metrics: bool = _append_metric_rows(
        lines=lines,
        metrics=metrics_data,
        metrics_results_rel=metrics_results_rel,
        key_metrics_lookup=key_metrics_lookup,
        skip_keys={"spec_version"},
    )
    if has_metrics:
        lines.append("")
    else:
        # Remove the heading we just added
        lines.pop()
        lines.pop()


def _append_variant_metrics(
    *,
    lines: list[str],
    metrics_data: dict[str, Any],
    metrics_results_rel: str,
    key_metrics_lookup: dict[str, _KeyMetricInfo],
) -> None:
    variants: object = metrics_data.get("variants")
    if not isinstance(variants, list) or len(variants) == 0:
        return
    lines.append("## Metrics")
    lines.append("")
    for variant in variants:
        if not isinstance(variant, dict):
            continue
        label: str = str(
            variant.get("label", variant.get("variant_id", "?")),
        )
        metrics: object = variant.get("metrics")
        if not isinstance(metrics, dict):
            continue
        lines.append(f"### {label}")
        lines.append("")
        has_values: bool = _append_metric_rows(
            lines=lines,
            metrics=metrics,
            metrics_results_rel=metrics_results_rel,
            key_metrics_lookup=key_metrics_lookup,
        )
        if has_values:
            lines.append("")
        else:
            # Remove the heading we just added
            lines.pop()
            lines.pop()


def _materialize_task_pages(
    *,
    tasks: list[TaskInfoFull],
    key_metrics_by_task: dict[str, list[TaskKeyMetric]] | None = None,
) -> None:
    remove_dir_if_exists(dir_path=TASK_PAGES_DIR)
    key_metrics_lookup: dict[str, _KeyMetricInfo] = _build_key_metrics_lookup()
    for task in tasks:
        key_metrics: list[TaskKeyMetric] = (
            key_metrics_by_task.get(task.task_id, []) if key_metrics_by_task is not None else []
        )
        page_path: Path = TASK_PAGES_DIR / f"{task.task_id}.md"
        write_file(
            file_path=page_path,
            content=normalize_markdown(
                content=_format_task_page(
                    task=task,
                    rel=_TASK_PAGE_REL,
                    key_metrics=key_metrics,
                    key_metrics_lookup=key_metrics_lookup,
                ),
            ),
        )


def materialize_tasks(
    *,
    tasks: list[TaskInfoFull],
    key_metrics_by_task: dict[str, list[TaskKeyMetric]] | None = None,
) -> None:
    remove_dir_if_exists(dir_path=TASKS_BY_STATUS_DIR)
    remove_dir_if_exists(dir_path=TASKS_BY_DATE_DIR)

    # Remove legacy per-task pages from overview/tasks/ (now in task_pages/)
    for old_page in TASK_PAGES_DIR.parent.glob("t[0-9]*.md"):
        old_page.unlink()

    write_file(
        file_path=TASKS_README,
        content=normalize_markdown(
            content=_format_tasks_page(
                title="Project Tasks",
                tasks=tasks,
                rel=_SECTION_REL,
                show_status_index=True,
                show_date_index=True,
                show_dependency_graph=True,
                back_link=None,
                key_metrics_by_task=key_metrics_by_task,
            ),
        ),
    )

    by_status: dict[str, list[TaskInfoFull]] = {}
    for task in tasks:
        if task.status not in by_status:
            by_status[task.status] = []
        by_status[task.status].append(task)

    for status, status_tasks in sorted(by_status.items()):
        emoji: str = STATUS_EMOJI.get(status, "")
        write_file(
            file_path=TASKS_BY_STATUS_DIR / f"{status}.md",
            content=normalize_markdown(
                content=_format_tasks_page(
                    title=(f"{emoji} Tasks: {status.replace('_', ' ').title()}"),
                    tasks=status_tasks,
                    rel=_STATUS_REL,
                    show_status_index=False,
                    show_date_index=False,
                    show_dependency_graph=False,
                    back_link="../README.md",
                    key_metrics_by_task=key_metrics_by_task,
                ),
            ),
        )

    write_file(
        file_path=TASKS_BY_DATE_README,
        content=normalize_markdown(
            content=_format_tasks_by_date_page(tasks=tasks),
        ),
    )

    _materialize_task_pages(
        tasks=tasks,
        key_metrics_by_task=key_metrics_by_task,
    )

    remove_file_if_exists(
        file_path=overview_legacy_markdown_path(section_name=SECTION_NAME),
    )
