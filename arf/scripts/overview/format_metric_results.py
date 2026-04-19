"""Metric results overview: overview/metrics-results/.

Generates an index page listing all metrics and separate per-metric
subpages with full results tables.
"""

from pathlib import Path

from arf.scripts.aggregators.aggregate_metric_results import (
    MetricResultEntry,
    MetricResultsFull,
)
from arf.scripts.overview.common import (
    EMPTY_MARKDOWN_VALUE,
    normalize_markdown,
    overview_legacy_markdown_path,
    overview_section_dir,
    overview_section_readme,
    remove_dir_if_exists,
    remove_file_if_exists,
    task_name_link,
    write_file,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SECTION_NAME: str = "metrics-results"
METRICS_RESULTS_DIR: Path = overview_section_dir(
    section_name=SECTION_NAME,
)
METRICS_RESULTS_README: Path = overview_section_readme(
    section_name=SECTION_NAME,
)
METRICS_RESULTS_TITLE: str = "Metrics Results"

_SECTION_REL: str = "../../"
_SUBPAGE_REL: str = "../../../"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sort_key_for_value(
    *,
    value: object,
    higher_is_better: bool,
) -> tuple[int, float]:
    # Ascending sort, so "better first" means the better value must
    # produce the smaller sort key. Higher-is-better metrics negate
    # the value (larger -> more negative); lower-is-better metrics
    # use the value as-is (smaller -> smaller). The leading tuple
    # element groups numeric (0) before non-numeric/None (1/2) so
    # nulls and strings always land at the bottom regardless of
    # direction.
    sign: float = -1.0 if higher_is_better else 1.0
    if isinstance(value, bool):
        return (1, sign * float(value))
    if isinstance(value, int | float):
        return (0, sign * float(value))
    if value is None:
        return (2, 0.0)
    return (1, 0.0)


def _format_value(*, value: object) -> str:
    if value is None:
        return EMPTY_MARKDOWN_VALUE
    return f"**{value}**"


def _metric_subpage_filename(*, metric_key: str) -> str:
    return f"{metric_key}.md"


# ---------------------------------------------------------------------------
# Per-metric subpage
# ---------------------------------------------------------------------------


def _format_metric_subpage(
    *,
    metric: MetricResultsFull,
    rel: str,
    task_name_map: dict[str, str],
) -> str:
    emoji_prefix: str = f"{metric.emoji} " if metric.emoji is not None else ""
    lines: list[str] = [
        f"# {emoji_prefix}{metric.metric_name}",
        "",
        f"**Key**: `{metric.metric_key}`"
        f" | **Unit**: {metric.unit}"
        f" | **Results**: {metric.result_count}",
        "",
        "[Back to all metrics](README.md)",
        "",
    ]

    if metric.result_count == 0:
        lines.append("No results.")
        return "\n".join(lines)

    sorted_entries: list[MetricResultEntry] = sorted(
        metric.entries,
        key=lambda e: _sort_key_for_value(
            value=e.value,
            higher_is_better=metric.higher_is_better,
        ),
    )

    lines.append("| # | Task | Variant | Value |")
    lines.append("|---|------|---------|-------|")
    for rank, entry in enumerate(sorted_entries, start=1):
        variant_str: str = (
            entry.variant_label if entry.variant_label is not None else EMPTY_MARKDOWN_VALUE
        )
        value_str: str = _format_value(value=entry.value)
        name: str = task_name_map.get(entry.task_id, entry.task_id)
        task_ref: str = task_name_link(
            task_id=entry.task_id,
            name=name,
            rel=rel,
        )
        lines.append(
            f"| {rank} | {task_ref} | {variant_str} | {value_str} |",
        )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Index page
# ---------------------------------------------------------------------------


def _format_metric_results_index(
    *,
    metric_results: list[MetricResultsFull],
) -> str:
    if len(metric_results) == 0:
        return f"# {METRICS_RESULTS_TITLE}\n\nNo metric results found."

    total_entries: int = sum(r.result_count for r in metric_results)
    lines: list[str] = [
        f"# {METRICS_RESULTS_TITLE} ({len(metric_results)} metrics, {total_entries} results)",
        "",
    ]

    key_metrics: list[MetricResultsFull] = [r for r in metric_results if r.is_key]
    other_metrics: list[MetricResultsFull] = [r for r in metric_results if not r.is_key]

    if len(key_metrics) > 0:
        lines.append("## Key Metrics")
        lines.append("")
        for r in key_metrics:
            emoji_prefix: str = f"{r.emoji} " if r.emoji is not None else ""
            filename: str = _metric_subpage_filename(
                metric_key=r.metric_key,
            )
            lines.append(
                f"* [{emoji_prefix}{r.metric_name}]({filename}) ({r.result_count} results)",
            )
        lines.append("")

    if len(other_metrics) > 0:
        lines.append("## All Metrics")
        lines.append("")
        lines.append("| Metric | Results |")
        lines.append("|--------|---------|")
        for r in other_metrics:
            filename = _metric_subpage_filename(
                metric_key=r.metric_key,
            )
            lines.append(
                f"| [{r.metric_name}]({filename}) | {r.result_count} |",
            )
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def materialize_metric_results(
    *,
    metric_results: list[MetricResultsFull],
    task_name_map: dict[str, str],
) -> None:
    remove_dir_if_exists(dir_path=METRICS_RESULTS_DIR)

    write_file(
        file_path=METRICS_RESULTS_README,
        content=normalize_markdown(
            content=_format_metric_results_index(
                metric_results=metric_results,
            ),
        ),
    )

    for metric in metric_results:
        subpage_path: Path = METRICS_RESULTS_DIR / _metric_subpage_filename(
            metric_key=metric.metric_key,
        )
        write_file(
            file_path=subpage_path,
            content=normalize_markdown(
                content=_format_metric_subpage(
                    metric=metric,
                    rel=_SUBPAGE_REL,
                    task_name_map=task_name_map,
                ),
            ),
        )

    remove_file_if_exists(
        file_path=overview_legacy_markdown_path(
            section_name=SECTION_NAME,
        ),
    )
