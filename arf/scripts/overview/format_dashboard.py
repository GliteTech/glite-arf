"""Dashboard overview page: overview/README.md.

Generates a single-page project dashboard with navigation, budget summary,
task status, suggestions, answers, and cost leaders.
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from arf.scripts.aggregators.aggregate_categories import CategoryInfo
from arf.scripts.aggregators.aggregate_costs import (
    BudgetInfo,
    CostAggregationFull,
    CostSummary,
    TaskCostInfoFull,
)
from arf.scripts.aggregators.aggregate_machines import (
    MachineAggregation,
    MachineSummary,
)
from arf.scripts.aggregators.aggregate_metric_results import (
    MetricResultEntry,
    MetricResultsFull,
)
from arf.scripts.aggregators.aggregate_metrics import MetricInfoFull
from arf.scripts.aggregators.aggregate_suggestions import SuggestionInfoFull
from arf.scripts.aggregators.aggregate_task_types import TaskTypeInfo
from arf.scripts.aggregators.aggregate_tasks import (
    TASK_STATUS_COMPLETED,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_INTERVENTION_BLOCKED,
    TASK_STATUS_NOT_STARTED,
    TaskInfoFull,
)
from arf.scripts.overview.common import (
    EMPTY_MARKDOWN_VALUE,
    KIND_EMOJI,
    RESULTS_SEGMENT,
    SUGGESTION_PRIORITY_HIGH,
    TASKS_SEGMENT,
    answer_asset_link,
    asset_name_link,
    category_links,
    normalize_markdown,
    repo_file_link,
    task_index_link,
    task_link,
    task_name_link,
    write_file,
)
from arf.scripts.overview.format_news import NewsDayInfo, format_date_human
from arf.scripts.overview.llm_context.models import LLMContextArchiveSummary
from arf.scripts.overview.paths import DASHBOARD_README
from meta.asset_types.answer.aggregator import AnswerInfoFull
from meta.asset_types.dataset.aggregator import DatasetInfoFull
from meta.asset_types.library.aggregator import LibraryInfoFull
from meta.asset_types.model.aggregator import ModelInfoFull
from meta.asset_types.paper.aggregator import (
    AuthorInfo,
    PaperInfoFull,
)
from meta.asset_types.predictions.aggregator import PredictionsInfoFull

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REL: str = "../"
_MAX_NEWS: int = 5
_MAX_IN_PROGRESS: int = 10
_MAX_READY: int = 10
_MAX_COMPLETED: int = 10
_MAX_SUGGESTIONS: int = 10
_MAX_HIGH_PRIORITY: int = 10
_MAX_ANSWERS: int = 10
_MAX_COST_LEADERS: int = 10
_MAX_KEY_METRIC_ENTRIES: int = 10
_UNKNOWN_DATE_SORT_KEY: str = "0000-00-00"


# ---------------------------------------------------------------------------
# Input data
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DashboardData:
    tasks: list[TaskInfoFull]
    costs: CostAggregationFull
    machines: MachineAggregation
    suggestions: list[SuggestionInfoFull]
    suggestion_task_map: dict[str, str]
    answers: list[AnswerInfoFull]
    papers: list[PaperInfoFull]
    datasets: list[DatasetInfoFull]
    models: list[ModelInfoFull]
    predictions: list[PredictionsInfoFull]
    libraries: list[LibraryInfoFull]
    metrics: list[MetricInfoFull]
    metric_results: list[MetricResultsFull]
    task_types: list[TaskTypeInfo]
    categories: list[CategoryInfo]
    llm_context_archives: list[LLMContextArchiveSummary]
    news_days: list[NewsDayInfo]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _more_link(*, count: int, label: str, url: str) -> str:
    if count <= 0:
        return ""
    noun: str = label if count != 1 else label.rstrip("s")
    return f"\n*{count} more {noun} \u2192 [{label}]({url})*\n"


def _date_sort_key_desc(*, value: str | None) -> str:
    if value is None:
        return _UNKNOWN_DATE_SORT_KEY
    return value


def _extract_task_index(*, task_id: str) -> int:
    return int(task_id[1:5])


def _effective_date_for_sort(*, task: TaskInfoFull) -> str:
    if task.end_time is not None:
        return task.end_time
    if task.start_time is not None:
        return task.start_time
    if task.effective_date is not None:
        return task.effective_date
    return _UNKNOWN_DATE_SORT_KEY


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------


def _badge(*, label: str, count: int, color: str, url: str) -> str:
    encoded_label: str = label.replace(" ", "%20").replace("-", "--")
    img: str = f"https://img.shields.io/badge/{encoded_label}-{count}-{color}"
    return f'<a href="{url}"><img src="{img}" alt="{label}"></a>'


def _format_nav(*, data: DashboardData) -> list[str]:
    total_suggestions: int = len(data.suggestions)

    asset_badges: list[str] = [
        _badge(label="Papers", count=len(data.papers), color="4169E1", url="papers/"),
        _badge(label="Datasets", count=len(data.datasets), color="2E8B57", url="datasets/"),
        _badge(label="Models", count=len(data.models), color="FF8C00", url="models/"),
        _badge(
            label="Predictions",
            count=len(data.predictions),
            color="9370DB",
            url="predictions/",
        ),
        _badge(
            label="Libraries",
            count=len(data.libraries),
            color="20B2AA",
            url="libraries/",
        ),
        _badge(label="Answers", count=len(data.answers), color="CD853F", url="answers/"),
    ]

    project_badges: list[str] = [
        _badge(label="News", count=len(data.news_days), color="FF6347", url="news/"),
        _badge(label="Tasks", count=len(data.tasks), color="4682B4", url="tasks/"),
        _badge(
            label="Suggestions",
            count=total_suggestions,
            color="DAA520",
            url="suggestions/",
        ),
        _badge(
            label="LLM Contexts",
            count=len(data.llm_context_archives),
            color="8B4513",
            url="llm-context/",
        ),
        _badge(label="Metrics", count=len(data.metrics), color="708090", url="metrics/"),
        _badge(
            label="Results",
            count=len(data.metric_results),
            color="DC143C",
            url="metrics-results/",
        ),
        _badge(
            label="Task%20Types",
            count=len(data.task_types),
            color="708090",
            url="task-types/",
        ),
    ]

    category_parts: list[str] = [
        f"[{cat.category_id}](by-category/{cat.category_id}.md)" for cat in data.categories
    ]

    lines: list[str] = [
        '<p align="center">',
        "  " + "\n  ".join(asset_badges),
        "</p>",
        "",
        '<p align="center">',
        "  " + "\n  ".join(project_badges),
        "</p>",
        "",
        "\U0001f3f7\ufe0f **Categories**: " + " | ".join(category_parts),
    ]
    llm_context_highlights: str | None = _format_llm_context_highlights(
        archives=data.llm_context_archives,
    )
    if llm_context_highlights is not None:
        lines.append("")
        lines.append(llm_context_highlights)
    return lines


# ---------------------------------------------------------------------------
# Budget
# ---------------------------------------------------------------------------


def _format_budget(*, costs: CostAggregationFull) -> list[str]:
    summary: CostSummary = costs.summary
    budget: BudgetInfo = costs.budget
    bar_width: int = 20
    filled: int = round(summary.spent_percent / 100.0 * bar_width)
    empty: int = bar_width - filled
    bar: str = "\u2588" * filled + "\u2591" * empty
    return [
        f"* **Budget**: **${summary.total_cost_usd:.0f}** spent of ${budget.total_budget:.0f}",
        f"* **Remaining**: **${summary.budget_left_usd:.0f}**",
        f"* **Usage**: `{bar}` {summary.spent_percent:.1f}%",
    ]


def _format_machines_summary(*, machines: MachineAggregation) -> list[str]:
    summary: MachineSummary = machines.summary
    if summary.total_machines == 0:
        return []
    lines: list[str] = [
        f"* **GPU Machines**: **{summary.total_machines}** provisioned"
        f" across {len(machines.tasks)} tasks"
        f" · **${summary.total_cost_usd:.0f}** GPU spend"
        f" ([details](machines/))",
    ]
    if summary.total_failed_attempts > 0:
        lines.append(
            f"* **Provisioning**: {summary.total_failed_attempts}"
            f" failed attempts"
            f" · ${summary.total_wasted_cost_usd:.2f} wasted"
            f" · {summary.failure_rate:.0%} failure rate",
        )
    return lines


# ---------------------------------------------------------------------------
# LLM context archives
# ---------------------------------------------------------------------------


def _format_token_count_short(*, estimated_tokens: int) -> str:
    if estimated_tokens >= 1_000_000:
        return f"{round(estimated_tokens / 1_000_000)}M"
    if estimated_tokens >= 1_000:
        rounded_thousands: int = round(estimated_tokens / 1_000)
        if rounded_thousands >= 1_000:
            return "1M"
        return f"{rounded_thousands}K"
    return str(estimated_tokens)


def _format_llm_context_highlights(
    *,
    archives: list[LLMContextArchiveSummary],
) -> str | None:
    featured_archives: list[LLMContextArchiveSummary] = sorted(
        [archive for archive in archives if archive.featured_rank is not None],
        key=lambda archive: (
            archive.featured_rank if archive.featured_rank is not None else 999,
            archive.preset_id,
        ),
    )[:5]
    if len(featured_archives) == 0:
        return None

    featured_parts: list[str] = [
        f"[{archive.short_name if archive.short_name is not None else archive.preset_id}]"
        f"(llm-context/{archive.file_name})"
        f" ({_format_token_count_short(estimated_tokens=archive.estimated_tokens)})"
        for archive in featured_archives
    ]
    return "**[LLM Contexts](llm-context/README.md)**: " + " | ".join(featured_parts)


# ---------------------------------------------------------------------------
# Key metrics leaderboard
# ---------------------------------------------------------------------------


def _sort_key_for_value(
    *,
    value: object,
    higher_is_better: bool,
) -> tuple[int, float]:
    # Mirrors `format_metric_results._sort_key_for_value` — kept
    # duplicated deliberately so the dashboard has no cross-module
    # dependency on the metric-results formatter.
    sign: float = -1.0 if higher_is_better else 1.0
    if isinstance(value, bool):
        return (1, sign * float(value))
    if isinstance(value, int | float):
        return (0, sign * float(value))
    if value is None:
        return (2, 0.0)
    return (1, 0.0)


def _format_key_metrics_leaderboard(
    *,
    metric_results: list[MetricResultsFull],
    tasks: list[TaskInfoFull],
) -> list[str]:
    key_metrics: list[MetricResultsFull] = [
        r for r in metric_results if r.is_key and r.result_count > 0
    ]
    if len(key_metrics) == 0:
        return []

    task_name_map: dict[str, str] = {t.task_id: t.name for t in tasks}

    lines: list[str] = [
        "## [Key Metrics Leaderboard](metrics-results/)",
        "",
    ]

    for metric in key_metrics:
        emoji_prefix: str = f"{metric.emoji} " if metric.emoji is not None else ""
        lines.append(f"### {emoji_prefix}{metric.metric_name}")
        lines.append("")

        sorted_entries: list[MetricResultEntry] = sorted(
            [e for e in metric.entries if e.value is not None],
            key=lambda e: _sort_key_for_value(
                value=e.value,
                higher_is_better=metric.higher_is_better,
            ),
        )
        shown: list[MetricResultEntry] = sorted_entries[:_MAX_KEY_METRIC_ENTRIES]

        lines.append("| # | Task | Variant | Value |")
        lines.append("|---|------|---------|-------|")
        for rank, entry in enumerate(shown, start=1):
            variant_str: str = entry.variant_label if entry.variant_label is not None else ""
            value_str: str = f"**{entry.value}**"
            name: str = task_name_map.get(
                entry.task_id,
                entry.task_id,
            )
            task_ref: str = task_name_link(
                task_id=entry.task_id,
                name=name,
                rel=_REL,
            )
            lines.append(
                f"| {rank} | {task_ref} | {variant_str} | {value_str} |",
            )
        lines.append("")

        remaining: int = metric.result_count - len(shown)
        if remaining > 0:
            lines.append(
                f"*{remaining} more results \u2192 [all results](metrics-results/)*",
            )
            lines.append("")

    return lines


# ---------------------------------------------------------------------------
# News
# ---------------------------------------------------------------------------


def _format_latest_news(*, data: DashboardData) -> list[str]:
    total: int = len(data.news_days)
    lines: list[str] = [f"## [Daily News ({total})](news/)", ""]
    if total == 0:
        lines.append("No daily news yet.")
        lines.append("")
        return lines
    recent: list[NewsDayInfo] = sorted(
        data.news_days,
        key=lambda d: d.date,
        reverse=True,
    )[:_MAX_NEWS]
    for day in recent:
        cost_str: str = f"~${day.total_cost_usd:,.0f}" if day.total_cost_usd is not None else ""
        parts: list[str] = []
        if day.tasks_completed_count > 0:
            parts.append(f"{day.tasks_completed_count} completed")
        if day.tasks_created_count > 0:
            parts.append(f"{day.tasks_created_count} created")
        if len(cost_str) > 0:
            parts.append(cost_str)
        summary: str = " · ".join(parts) if len(parts) > 0 else ""
        lines.append(
            f"* [{format_date_human(day.date)}](news/{day.date}.md)"
            + (f" — {summary}" if len(summary) > 0 else ""),
        )
    if total > _MAX_NEWS:
        lines.append(f"* *... and {total - _MAX_NEWS} more → [all news](news/)*")
    lines.append("")
    return lines


# ---------------------------------------------------------------------------
# Tasks: in progress
# ---------------------------------------------------------------------------


def _format_in_progress_tasks(*, tasks: list[TaskInfoFull]) -> list[str]:
    in_progress: list[TaskInfoFull] = [t for t in tasks if t.status == TASK_STATUS_IN_PROGRESS]
    in_progress.sort(
        key=lambda t: _effective_date_for_sort(task=t),
        reverse=True,
    )
    total: int = len(in_progress)

    heading: str = f"## [In Progress ({total})](tasks/by-status/in_progress.md)"
    lines: list[str] = [heading, ""]
    if total == 0:
        lines.append("No tasks in progress.")
        lines.append("")
        return lines

    shown: list[TaskInfoFull] = in_progress[:_MAX_IN_PROGRESS]
    lines.append("| # | Task | Started |")
    lines.append("|---|------|---------|")
    for t in shown:
        date_str: str = EMPTY_MARKDOWN_VALUE
        if t.start_time is not None:
            date_str = t.start_time[:16].replace("T", " ")
        lines.append(
            f"| {t.task_index:04d}"
            f" | {task_name_link(task_id=t.task_id, name=t.name, rel=_REL)}"
            f" | {date_str} |"
        )
    lines.append("")

    remaining: int = total - len(shown)
    if remaining > 0:
        lines.append(
            _more_link(
                count=remaining,
                label="in-progress tasks",
                url="tasks/by-status/in_progress.md",
            ),
        )
    return lines


# ---------------------------------------------------------------------------
# Tasks: ready to start
# ---------------------------------------------------------------------------


def _is_ready(*, task: TaskInfoFull, completed_ids: set[str]) -> bool:
    if task.status != TASK_STATUS_NOT_STARTED:
        return False
    return all(dep in completed_ids for dep in task.dependencies)


def _is_blocked(*, task: TaskInfoFull, completed_ids: set[str]) -> bool:
    if task.status != TASK_STATUS_NOT_STARTED:
        return False
    return any(dep not in completed_ids for dep in task.dependencies)


def _format_ready_tasks(
    *,
    tasks: list[TaskInfoFull],
    completed_ids: set[str],
) -> list[str]:
    ready: list[TaskInfoFull] = [t for t in tasks if _is_ready(task=t, completed_ids=completed_ids)]
    ready.sort(key=lambda t: _effective_date_for_sort(task=t))
    total: int = len(ready)

    lines: list[str] = [f"## [Ready to Start ({total})](tasks/by-status/not_started.md)", ""]
    if total == 0:
        lines.append("No tasks ready to start.")
        lines.append("")
        return lines

    shown: list[TaskInfoFull] = ready[:_MAX_READY]
    lines.append("| # | Task | Description | Date Added |")
    lines.append("|---|------|-------------|------------|")
    for t in shown:
        date_str: str = t.effective_date if t.effective_date is not None else EMPTY_MARKDOWN_VALUE
        desc_link: str = repo_file_link(
            label="description",
            repo_relative_path=f"{TASKS_SEGMENT}/{t.task_id}/task_description.md",
            rel=_REL,
        )
        lines.append(
            f"| {t.task_index:04d}"
            f" | {task_name_link(task_id=t.task_id, name=t.name, rel=_REL)}"
            f" | {desc_link} | {date_str} |"
        )
    lines.append("")

    remaining: int = total - len(shown)
    if remaining > 0:
        lines.append(
            _more_link(
                count=remaining,
                label="ready tasks",
                url="tasks/by-status/not_started.md",
            ),
        )
    return lines


# ---------------------------------------------------------------------------
# Tasks: blocked
# ---------------------------------------------------------------------------


def _format_blocked_tasks(
    *,
    tasks: list[TaskInfoFull],
    completed_ids: set[str],
) -> list[str]:
    blocked: list[TaskInfoFull] = [
        t for t in tasks if _is_blocked(task=t, completed_ids=completed_ids)
    ]
    blocked.sort(key=lambda t: t.task_index)
    total: int = len(blocked)

    lines: list[str] = [f"## [Blocked Tasks ({total})](tasks/)", ""]
    if total == 0:
        lines.append("No blocked tasks.")
        lines.append("")
        return lines

    lines.append("| # | Task | Blocked By |")
    lines.append("|---|------|------------|")
    for t in blocked:
        missing_deps: list[str] = [dep for dep in t.dependencies if dep not in completed_ids]
        dep_links: str = ", ".join(task_link(task_id=dep, rel=_REL) for dep in missing_deps)
        lines.append(
            f"| {t.task_index:04d}"
            f" | {task_name_link(task_id=t.task_id, name=t.name, rel=_REL)}"
            f" | {dep_links} |"
        )
    lines.append("")
    return lines


# ---------------------------------------------------------------------------
# Tasks: intervention blocked
# ---------------------------------------------------------------------------


def _format_intervention_blocked(*, tasks: list[TaskInfoFull]) -> list[str]:
    intervention: list[TaskInfoFull] = [
        t for t in tasks if t.status == TASK_STATUS_INTERVENTION_BLOCKED
    ]
    if len(intervention) == 0:
        return []

    intervention.sort(key=lambda t: t.task_index)
    total: int = len(intervention)

    lines: list[str] = [f"## Intervention Blocked ({total})", ""]
    lines.append("| # | Task |")
    lines.append("|---|------|")
    for t in intervention:
        lines.append(
            f"| {t.task_index:04d} | {task_name_link(task_id=t.task_id, name=t.name, rel=_REL)} |"
        )
    lines.append("")
    return lines


# ---------------------------------------------------------------------------
# Tasks: recently completed
# ---------------------------------------------------------------------------


def _format_recently_completed(*, tasks: list[TaskInfoFull]) -> list[str]:
    completed: list[TaskInfoFull] = [t for t in tasks if t.status == TASK_STATUS_COMPLETED]
    completed.sort(
        key=lambda t: _effective_date_for_sort(task=t),
        reverse=True,
    )
    total: int = len(completed)

    heading: str = f"## [Recently Completed ({total} total)](tasks/by-status/completed.md)"
    lines: list[str] = [heading, ""]
    if total == 0:
        lines.append("No completed tasks.")
        lines.append("")
        return lines

    shown: list[TaskInfoFull] = completed[:_MAX_COMPLETED]
    lines.append("| # | Task | Results | Completed |")
    lines.append("|---|------|---------|-----------|")
    for t in shown:
        date_str: str = EMPTY_MARKDOWN_VALUE
        if t.end_time is not None:
            date_str = t.end_time[:16].replace("T", " ")
        elif t.effective_date is not None:
            date_str = t.effective_date
        results_link: str = repo_file_link(
            label="results",
            repo_relative_path=(
                f"{TASKS_SEGMENT}/{t.task_id}/{RESULTS_SEGMENT}/results_detailed.md"
            ),
            rel=_REL,
        )
        lines.append(
            f"| {t.task_index:04d}"
            f" | {task_name_link(task_id=t.task_id, name=t.name, rel=_REL)}"
            f" | {results_link} | {date_str} |"
        )
    lines.append("")

    remaining: int = total - len(shown)
    if remaining > 0:
        lines.append(
            _more_link(
                count=remaining,
                label="completed tasks",
                url="tasks/by-status/completed.md",
            ),
        )
    return lines


# ---------------------------------------------------------------------------
# Suggestions: recent
# ---------------------------------------------------------------------------


def format_suggestion_detail(
    *,
    suggestion: SuggestionInfoFull,
    rel: str,
) -> list[str]:
    emoji: str = KIND_EMOJI.get(suggestion.kind, "")
    date_str: str = (
        suggestion.date_added if suggestion.date_added is not None else EMPTY_MARKDOWN_VALUE
    )
    source_link: str = f"[{suggestion.source_task}]({rel}{TASKS_SEGMENT}/{suggestion.source_task}/)"
    return [
        "<details>",
        f"<summary>{emoji} <strong>{suggestion.title}</strong> ({suggestion.id})</summary>",
        "",
        f"**Kind**: {suggestion.kind} | **Priority**: {suggestion.priority}"
        f" | **Date**: {date_str} | **Source**: {source_link}",
        "",
        suggestion.description,
        "",
        "</details>",
        "",
    ]


def _format_recent_suggestions(
    *,
    suggestions: list[SuggestionInfoFull],
    task_map: dict[str, str],
) -> list[str]:
    open_suggestions: list[SuggestionInfoFull] = [s for s in suggestions if s.id not in task_map]
    open_suggestions.sort(
        key=lambda s: _date_sort_key_desc(value=s.date_added),
        reverse=True,
    )
    total: int = len(open_suggestions)

    lines: list[str] = [f"## [Recent Suggestions ({total} open)](suggestions/)", ""]
    if total == 0:
        lines.append("No open suggestions.")
        lines.append("")
        return lines

    shown: list[SuggestionInfoFull] = open_suggestions[:_MAX_SUGGESTIONS]
    for s in shown:
        lines.extend(format_suggestion_detail(suggestion=s, rel=_REL))

    remaining: int = total - len(shown)
    if remaining > 0:
        lines.append(
            _more_link(
                count=remaining,
                label="open suggestions",
                url="suggestions/",
            ),
        )
    return lines


# ---------------------------------------------------------------------------
# Suggestions: high priority
# ---------------------------------------------------------------------------


def _format_high_priority_suggestions(
    *,
    suggestions: list[SuggestionInfoFull],
    task_map: dict[str, str],
) -> list[str]:
    high: list[SuggestionInfoFull] = [
        s for s in suggestions if s.priority == SUGGESTION_PRIORITY_HIGH and s.id not in task_map
    ]
    high.sort(
        key=lambda s: _date_sort_key_desc(value=s.date_added),
        reverse=True,
    )
    total: int = len(high)

    lines: list[str] = [f"## [High Priority Suggestions ({total})](suggestions/)", ""]
    if total == 0:
        lines.append("No high-priority open suggestions.")
        lines.append("")
        return lines

    shown: list[SuggestionInfoFull] = high[:_MAX_HIGH_PRIORITY]
    for s in shown:
        lines.extend(format_suggestion_detail(suggestion=s, rel=_REL))

    remaining: int = total - len(shown)
    if remaining > 0:
        lines.append(
            _more_link(
                count=remaining,
                label="high-priority suggestions",
                url="suggestions/",
            ),
        )
    return lines


# ---------------------------------------------------------------------------
# Answers: recent
# ---------------------------------------------------------------------------


def format_answer_detail(*, answer: AnswerInfoFull, rel: str) -> list[str]:
    full_link: str = answer_asset_link(
        answer_id=answer.answer_id,
        task_id=answer.created_by_task,
        rel=rel,
    )
    short_text: str | None = None
    if answer.short_answer is not None and len(answer.short_answer) > 0:
        short_text = answer.short_answer
    lines: list[str] = [
        "<details>",
        f"<summary><strong>{answer.question}</strong></summary>",
        "",
        f"**Confidence**: {answer.confidence}"
        f" | **Date**: {answer.date_created}"
        f" | **Full answer**: {full_link}",
        "",
    ]
    if short_text is not None:
        lines.append(short_text)
        lines.append("")
    lines.append("</details>")
    lines.append("")
    return lines


def _format_recent_answers(*, answers: list[AnswerInfoFull]) -> list[str]:
    sorted_answers: list[AnswerInfoFull] = sorted(
        answers,
        key=lambda a: _date_sort_key_desc(value=a.date_created),
        reverse=True,
    )
    total: int = len(sorted_answers)

    lines: list[str] = [f"## [Recent Answers ({total} total)](answers/)", ""]
    if total == 0:
        lines.append("No answers yet.")
        lines.append("")
        return lines

    shown: list[AnswerInfoFull] = sorted_answers[:_MAX_ANSWERS]
    for a in shown:
        lines.extend(format_answer_detail(answer=a, rel=_REL))

    remaining: int = total - len(shown)
    if remaining > 0:
        lines.append(
            _more_link(
                count=remaining,
                label="answers",
                url="answers/",
            ),
        )
    return lines


# ---------------------------------------------------------------------------
# Latest assets
# ---------------------------------------------------------------------------

_MAX_LATEST_PAPERS: int = 10
_MAX_LATEST_ASSETS: int = 10


VENUE_KIND_EMOJI: dict[str, str] = {
    "conference": "\U0001f3e4",
    "journal": "\U0001f4d6",
    "workshop": "\U0001f527",
    "preprint": "\U0001f4dd",
    "book": "\U0001f4da",
    "thesis": "\U0001f393",
    "technical_report": "\U0001f4cb",
    "other": "\U0001f4c4",
}


def _short_authors(*, authors: list[AuthorInfo]) -> str:
    if len(authors) == 0:
        return "Unknown"
    first: str = authors[0].name.split()[-1]
    if len(authors) == 1:
        return first
    if len(authors) == 2:
        second: str = authors[1].name.split()[-1]
        return f"{first} & {second}"
    return f"{first} et al."


def format_paper_card(*, paper: PaperInfoFull, rel: str) -> list[str]:
    emoji: str = VENUE_KIND_EMOJI.get(paper.venue_kind, "\U0001f4c4")
    authors_short: str = _short_authors(authors=paper.authors)
    authors_full: str = ", ".join(a.name for a in paper.authors)
    doi_str: str = f"`{paper.doi}`" if paper.doi is not None else EMPTY_MARKDOWN_VALUE
    url_str: str = paper.url if paper.url is not None else EMPTY_MARKDOWN_VALUE
    summary_str: str = EMPTY_MARKDOWN_VALUE
    if paper.summary_path is not None:
        summary_str = repo_file_link(
            label="summary.md",
            repo_relative_path=paper.summary_path.as_posix(),
            rel=rel,
        )

    lines: list[str] = [
        "<details>",
        (
            f"<summary>{emoji} <strong>{paper.title}</strong>"
            f" \u2014 {authors_short}, {paper.year}</summary>"
        ),
        "",
        "| Field | Value |",
        "|---|---|",
        f"| **ID** | `{paper.paper_id}` |",
        f"| **Authors** | {authors_full} |",
        f"| **Venue** | {paper.journal} ({paper.venue_kind}) |",
        f"| **DOI** | {doi_str} |",
        f"| **URL** | {url_str} |",
        f"| **Date added** | {paper.date_added} |",
        f"| **Categories** | {category_links(categories=paper.categories, rel=rel)} |",
        f"| **Added by** | {task_link(task_id=paper.added_by_task, rel=rel)} |",
        f"| **Full summary** | {summary_str} |",
        "",
    ]

    if paper.summary is not None and len(paper.summary.strip()) > 0:
        lines.append(paper.summary.strip())
        lines.append("")
    elif len(paper.abstract) > 0:
        lines.append(paper.abstract)
        lines.append("")

    lines.append("</details>")
    lines.append("")
    return lines


def _format_latest_papers(*, data: DashboardData) -> list[str]:
    sorted_papers: list[PaperInfoFull] = sorted(
        data.papers,
        key=lambda p: (p.date_added, p.citation_key),
        reverse=True,
    )
    total: int = len(sorted_papers)

    lines: list[str] = [
        f"## [Latest Papers ({total} total)](papers/)",
        "",
    ]
    if total == 0:
        lines.append("No papers yet.")
        lines.append("")
        return lines

    shown: list[PaperInfoFull] = sorted_papers[:_MAX_LATEST_PAPERS]
    for p in shown:
        lines.extend(format_paper_card(paper=p, rel=_REL))

    remaining: int = total - len(shown)
    if remaining > 0:
        lines.append(
            _more_link(count=remaining, label="papers", url="papers/"),
        )
    return lines


def _format_latest_datasets(*, data: DashboardData) -> list[str]:
    sorted_datasets: list[DatasetInfoFull] = sorted(
        data.datasets,
        key=lambda d: (
            d.date_added if d.date_added is not None else _UNKNOWN_DATE_SORT_KEY,
            d.name,
        ),
        reverse=True,
    )
    total: int = len(sorted_datasets)

    lines: list[str] = [
        f"## [Latest Datasets ({total} total)](datasets/)",
        "",
    ]
    if total == 0:
        lines.append("No datasets yet.")
        lines.append("")
        return lines

    shown: list[DatasetInfoFull] = sorted_datasets[:_MAX_LATEST_ASSETS]
    lines.append("| Name | Size | Source | Added |")
    lines.append("|------|------|--------|-------|")
    for d in shown:
        date_str: str = d.date_added if d.date_added is not None else EMPTY_MARKDOWN_VALUE
        name_display: str = asset_name_link(
            name=d.name,
            description_path=d.description_path,
            rel=_REL,
        )
        source: str = (
            task_index_link(
                task_id=d.added_by_task,
                task_index=_extract_task_index(task_id=d.added_by_task),
                rel=_REL,
            )
            if d.added_by_task is not None
            else EMPTY_MARKDOWN_VALUE
        )
        lines.append(f"| {name_display} | {d.size_description} | {source} | {date_str} |")
    lines.append("")

    remaining: int = total - len(shown)
    if remaining > 0:
        lines.append(
            _more_link(count=remaining, label="datasets", url="datasets/"),
        )
    return lines


def _format_latest_models(*, data: DashboardData) -> list[str]:
    sorted_models: list[ModelInfoFull] = sorted(
        data.models,
        key=lambda m: (m.date_created, m.name),
        reverse=True,
    )
    total: int = len(sorted_models)

    lines: list[str] = [
        f"## [Latest Models ({total} total)](models/)",
        "",
    ]
    if total == 0:
        lines.append("No models yet.")
        lines.append("")
        return lines

    shown: list[ModelInfoFull] = sorted_models[:_MAX_LATEST_ASSETS]
    lines.append("| Name | Source | Created |")
    lines.append("|------|--------|---------|")
    for m in shown:
        name_display: str = asset_name_link(
            name=m.name,
            description_path=m.description_path,
            rel=_REL,
        )
        source: str = task_index_link(
            task_id=m.created_by_task,
            task_index=_extract_task_index(task_id=m.created_by_task),
            rel=_REL,
        )
        lines.append(f"| {name_display} | {source} | {m.date_created} |")
    lines.append("")

    remaining: int = total - len(shown)
    if remaining > 0:
        lines.append(
            _more_link(count=remaining, label="models", url="models/"),
        )
    return lines


def _format_latest_predictions(*, data: DashboardData) -> list[str]:
    sorted_preds: list[PredictionsInfoFull] = sorted(
        data.predictions,
        key=lambda p: (p.date_created, p.name),
        reverse=True,
    )
    total: int = len(sorted_preds)

    lines: list[str] = [
        f"## [Latest Predictions ({total} total)](predictions/)",
        "",
    ]
    if total == 0:
        lines.append("No predictions yet.")
        lines.append("")
        return lines

    shown: list[PredictionsInfoFull] = sorted_preds[:_MAX_LATEST_ASSETS]
    lines.append("| Name | Source | Created |")
    lines.append("|------|--------|---------|")
    for p in shown:
        name_display: str = asset_name_link(
            name=p.name,
            description_path=p.description_path,
            rel=_REL,
        )
        source: str = task_index_link(
            task_id=p.created_by_task,
            task_index=_extract_task_index(task_id=p.created_by_task),
            rel=_REL,
        )
        lines.append(f"| {name_display} | {source} | {p.date_created} |")
    lines.append("")

    remaining: int = total - len(shown)
    if remaining > 0:
        lines.append(
            _more_link(count=remaining, label="predictions", url="predictions/"),
        )
    return lines


def _format_latest_libraries(*, data: DashboardData) -> list[str]:
    sorted_libs: list[LibraryInfoFull] = sorted(
        data.libraries,
        key=lambda lib: (lib.date_created, lib.name),
        reverse=True,
    )
    total: int = len(sorted_libs)

    lines: list[str] = [
        f"## [Latest Libraries ({total} total)](libraries/)",
        "",
    ]
    if total == 0:
        lines.append("No libraries yet.")
        lines.append("")
        return lines

    shown: list[LibraryInfoFull] = sorted_libs[:_MAX_LATEST_ASSETS]
    lines.append("| Name | Source | Created |")
    lines.append("|------|--------|---------|")
    for lib in shown:
        name_display: str = asset_name_link(
            name=lib.name,
            description_path=lib.description_path,
            rel=_REL,
        )
        source: str = task_index_link(
            task_id=lib.created_by_task,
            task_index=_extract_task_index(task_id=lib.created_by_task),
            rel=_REL,
        )
        lines.append(f"| {name_display} | {source} | {lib.date_created} |")
    lines.append("")

    remaining: int = total - len(shown)
    if remaining > 0:
        lines.append(
            _more_link(count=remaining, label="libraries", url="libraries/"),
        )
    return lines


# ---------------------------------------------------------------------------
# Cost leaders
# ---------------------------------------------------------------------------


def _format_cost_leaders(
    *,
    costs: CostAggregationFull,
    tasks: list[TaskInfoFull],
) -> list[str]:
    task_map: dict[str, TaskInfoFull] = {t.task_id: t for t in tasks}
    nonzero: list[TaskCostInfoFull] = [t for t in costs.tasks if t.total_cost_usd > 0]
    nonzero.sort(key=lambda t: t.total_cost_usd, reverse=True)
    total: int = len(nonzero)

    lines: list[str] = [f"## [Cost Leaders ({total} tasks with spend)](costs/)", ""]
    if total == 0:
        lines.append("No tasks with non-zero spend.")
        lines.append("")
        return lines

    shown: list[TaskCostInfoFull] = nonzero[:_MAX_COST_LEADERS]
    lines.append("| Task | Cost | Date |")
    lines.append("|------|------|------|")
    for t in shown:
        task_info: TaskInfoFull | None = task_map.get(t.task_id)
        date_str: str = EMPTY_MARKDOWN_VALUE
        if task_info is not None:
            if task_info.end_time is not None:
                date_str = task_info.end_time[:16].replace("T", " ")
            elif task_info.effective_date is not None:
                date_str = task_info.effective_date
        cost_link: str = repo_file_link(
            label=f"${t.total_cost_usd:.2f}",
            repo_relative_path=f"{TASKS_SEGMENT}/{t.task_id}/{RESULTS_SEGMENT}/costs.json",
            rel=_REL,
        )
        lines.append(
            f"| {task_name_link(task_id=t.task_id, name=t.name, rel=_REL)}"
            f" | {cost_link} | {date_str} |"
        )
    lines.append("")

    remaining: int = total - len(shown)
    if remaining > 0:
        lines.append(
            _more_link(
                count=remaining,
                label="tasks with spend",
                url="costs/",
            ),
        )
    return lines


# ---------------------------------------------------------------------------
# Main assembly
# ---------------------------------------------------------------------------


def _format_dashboard(*, data: DashboardData) -> str:
    completed_ids: set[str] = {t.task_id for t in data.tasks if t.status == TASK_STATUS_COMPLETED}

    now_utc: str = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC")

    lines: list[str] = ["# Project Dashboard", ""]
    lines.extend(_format_nav(data=data))
    lines.append("")
    lines.append(f"*Last updated: {now_utc}*")
    lines.append("")
    lines.extend(_format_budget(costs=data.costs))
    lines.extend(_format_machines_summary(machines=data.machines))
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.extend(_format_latest_news(data=data))
    lines.append("---")
    lines.append("")

    lines.extend(_format_in_progress_tasks(tasks=data.tasks))
    lines.append("---")
    lines.append("")

    lines.extend(
        _format_ready_tasks(tasks=data.tasks, completed_ids=completed_ids),
    )
    lines.append("---")
    lines.append("")
    lines.extend(
        _format_blocked_tasks(tasks=data.tasks, completed_ids=completed_ids),
    )
    intervention_lines: list[str] = _format_intervention_blocked(
        tasks=data.tasks,
    )
    if len(intervention_lines) > 0:
        lines.append("---")
        lines.append("")
        lines.extend(intervention_lines)
    lines.append("---")
    lines.append("")
    lines.extend(_format_recently_completed(tasks=data.tasks))
    lines.append("---")
    lines.append("")

    key_metrics_lines: list[str] = _format_key_metrics_leaderboard(
        metric_results=data.metric_results,
        tasks=data.tasks,
    )
    if len(key_metrics_lines) > 0:
        lines.extend(key_metrics_lines)
        lines.append("---")
        lines.append("")
    lines.extend(
        _format_recent_suggestions(
            suggestions=data.suggestions,
            task_map=data.suggestion_task_map,
        ),
    )
    lines.append("---")
    lines.append("")
    lines.extend(
        _format_high_priority_suggestions(
            suggestions=data.suggestions,
            task_map=data.suggestion_task_map,
        ),
    )
    lines.append("---")
    lines.append("")
    lines.extend(_format_recent_answers(answers=data.answers))
    lines.append("---")
    lines.append("")
    lines.extend(_format_latest_papers(data=data))
    lines.append("---")
    lines.append("")
    lines.extend(_format_latest_datasets(data=data))
    lines.append("---")
    lines.append("")
    lines.extend(_format_latest_models(data=data))
    lines.append("---")
    lines.append("")
    lines.extend(_format_latest_predictions(data=data))
    lines.append("---")
    lines.append("")
    lines.extend(_format_latest_libraries(data=data))
    lines.append("---")
    lines.append("")
    lines.extend(_format_cost_leaders(costs=data.costs, tasks=data.tasks))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def materialize_dashboard(*, data: DashboardData) -> None:
    write_file(
        file_path=DASHBOARD_README,
        content=normalize_markdown(content=_format_dashboard(data=data)),
    )
