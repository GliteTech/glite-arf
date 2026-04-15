"""Metrics overview formatting."""

from pathlib import Path

from arf.scripts.aggregators.aggregate_metrics import (
    MetricInfoFull,
)
from arf.scripts.overview.common import (
    EMPTY_MARKDOWN_VALUE,
    normalize_markdown,
    overview_legacy_markdown_path,
    overview_section_readme,
    remove_file_if_exists,
    write_file,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

UNIT_EMOJI: dict[str, str] = {
    "f1": "\U0001f3af",
    "accuracy": "\u2705",
    "precision": "\U0001f4cd",
    "recall": "\U0001f50d",
    "ratio": "\U0001f4ca",
    "count": "#\ufe0f\u20e3",
    "usd": "\U0001f4b2",
    "seconds": "\u23f1\ufe0f",
    "bytes": "\U0001f4be",
    "instances_per_second": "\u26a1",
    "none": "\u2796",
}
DEFAULT_UNIT_EMOJI: str = "\U0001f4cf"
METRICS_TITLE: str = "Metrics"
NO_METRICS_FOUND_TEXT: str = "No metrics found."

SECTION_NAME: str = "metrics"
METRICS_README: Path = overview_section_readme(section_name=SECTION_NAME)


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def _format_metric_detail(*, m: MetricInfoFull) -> str:
    emoji: str = UNIT_EMOJI.get(m.unit, DEFAULT_UNIT_EMOJI)
    datasets_str: str = (
        ", ".join(f"`{d}`" for d in m.datasets) if len(m.datasets) > 0 else EMPTY_MARKDOWN_VALUE
    )

    lines: list[str] = [
        "<details>",
        f"<summary>{emoji} <strong>{m.name}</strong> (<code>{m.metric_key}</code>)</summary>",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| **Key** | `{m.metric_key}` |",
        f"| **Unit** | {m.unit} |",
        f"| **Value type** | {m.value_type} |",
        f"| **Datasets** | {datasets_str} |",
        "",
        m.description,
        "",
        "</details>",
    ]
    return "\n".join(lines)


def _format_metrics_by_unit(
    *,
    metrics: list[MetricInfoFull],
    unit: str,
) -> list[str]:
    filtered: list[MetricInfoFull] = [m for m in metrics if m.unit == unit]
    if len(filtered) == 0:
        return []
    emoji: str = UNIT_EMOJI.get(unit, DEFAULT_UNIT_EMOJI)
    lines: list[str] = [f"## {emoji} {unit} ({len(filtered)})", ""]
    for m in filtered:
        lines.append(_format_metric_detail(m=m))
        lines.append("")
    return lines


def _format_metrics_overview(*, metrics: list[MetricInfoFull]) -> str:
    if len(metrics) == 0:
        return f"# {METRICS_TITLE}\n\n{NO_METRICS_FOUND_TEXT}"

    lines: list[str] = [
        f"# {METRICS_TITLE} ({len(metrics)})",
        "",
    ]

    # Collect unique units in order of appearance
    seen_units: set[str] = set()
    unit_order: list[str] = []
    for m in metrics:
        if m.unit not in seen_units:
            seen_units.add(m.unit)
            unit_order.append(m.unit)

    for unit in unit_order:
        lines.extend(
            _format_metrics_by_unit(metrics=metrics, unit=unit),
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Materialization
# ---------------------------------------------------------------------------


def materialize_metrics(*, metrics: list[MetricInfoFull]) -> None:
    write_file(
        file_path=METRICS_README,
        content=normalize_markdown(
            content=_format_metrics_overview(metrics=metrics),
        ),
    )
    remove_file_if_exists(
        file_path=overview_legacy_markdown_path(section_name=SECTION_NAME),
    )
