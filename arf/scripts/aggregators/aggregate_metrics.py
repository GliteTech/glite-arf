"""Aggregate all registered metrics in the project.

Reads every metric folder under meta/metrics/ and outputs
structured data about each registered metric definition.

Aggregator version: 2
"""

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Any

from arf.scripts.aggregators.common.cli import (
    DETAIL_LEVEL_FULL,
    DETAIL_LEVEL_SHORT,
    OUTPUT_FORMAT_IDS,
    OUTPUT_FORMAT_JSON,
    OUTPUT_FORMAT_MARKDOWN,
    add_detail_level_arg,
    add_output_format_arg,
)
from arf.scripts.aggregators.common.filtering import matches_ids
from arf.scripts.verificators.common.json_utils import load_json_file
from arf.scripts.verificators.common.paths import (
    METRICS_DIR,
    metric_definition_path,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VERSION_FIELD: str = "spec_version"
NAME_FIELD: str = "name"
DESCRIPTION_FIELD: str = "description"
UNIT_FIELD: str = "unit"
VALUE_TYPE_FIELD: str = "value_type"
HIGHER_IS_BETTER_FIELD: str = "higher_is_better"
DATASETS_FIELD: str = "datasets"
IS_KEY_FIELD: str = "is_key"
EMOJI_FIELD: str = "emoji"

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class MetricInfoShort:
    metric_key: str
    name: str
    unit: str
    value_type: str
    higher_is_better: bool
    is_key: bool
    emoji: str | None


@dataclass(frozen=True, slots=True)
class MetricInfoFull:
    metric_key: str
    name: str
    description: str
    unit: str
    value_type: str
    version: int
    higher_is_better: bool
    datasets: list[str]
    is_key: bool
    emoji: str | None


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def _discover_metric_keys() -> list[str]:
    if not METRICS_DIR.exists():
        return []
    return sorted(
        d.name for d in METRICS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
    )


def _load_metric(*, metric_key: str) -> MetricInfoFull | None:
    data: dict[str, Any] | None = load_json_file(
        file_path=metric_definition_path(metric_key=metric_key),
    )
    if data is None:
        return None

    version: object = data.get(VERSION_FIELD)
    name: object = data.get(NAME_FIELD)
    description: object = data.get(DESCRIPTION_FIELD)
    unit: object = data.get(UNIT_FIELD)
    value_type: object = data.get(VALUE_TYPE_FIELD)
    datasets: object = data.get(DATASETS_FIELD)

    if not isinstance(version, int) or isinstance(version, bool):
        return None
    if not isinstance(name, str):
        return None
    if not isinstance(description, str):
        return None
    if not isinstance(unit, str):
        return None
    if not isinstance(value_type, str):
        return None

    higher_is_better_raw: object = data.get(HIGHER_IS_BETTER_FIELD)
    if not isinstance(higher_is_better_raw, bool):
        return None
    higher_is_better: bool = higher_is_better_raw

    datasets_list: list[str] = []
    if datasets is not None:
        if not isinstance(datasets, list):
            return None
        for item in datasets:
            if not isinstance(item, str):
                return None
            datasets_list.append(item)

    is_key_raw: object = data.get(IS_KEY_FIELD)
    is_key: bool = is_key_raw is True

    emoji_raw: object = data.get(EMOJI_FIELD)
    emoji: str | None = emoji_raw if isinstance(emoji_raw, str) else None

    return MetricInfoFull(
        metric_key=metric_key,
        name=name,
        description=description,
        unit=unit,
        value_type=value_type,
        version=version,
        higher_is_better=higher_is_better,
        datasets=datasets_list,
        is_key=is_key,
        emoji=emoji,
    )


def _matches_unit(
    *,
    unit: str,
    filter_unit: list[str] | None,
) -> bool:
    if filter_unit is None:
        return True
    return unit in set(filter_unit)


def _to_short(*, metric: MetricInfoFull) -> MetricInfoShort:
    return MetricInfoShort(
        metric_key=metric.metric_key,
        name=metric.name,
        unit=metric.unit,
        value_type=metric.value_type,
        higher_is_better=metric.higher_is_better,
        is_key=metric.is_key,
        emoji=metric.emoji,
    )


def _load_and_filter(
    *,
    filter_unit: list[str] | None = None,
    filter_ids: list[str] | None = None,
) -> list[MetricInfoFull]:
    keys: list[str] = _discover_metric_keys()
    metrics: list[MetricInfoFull] = []
    for key in keys:
        if not matches_ids(asset_id=key, filter_ids=filter_ids):
            continue
        info: MetricInfoFull | None = _load_metric(metric_key=key)
        if info is None:
            continue
        if not _matches_unit(unit=info.unit, filter_unit=filter_unit):
            continue
        metrics.append(info)
    return metrics


def aggregate_metrics_short(
    *,
    filter_unit: list[str] | None = None,
    filter_ids: list[str] | None = None,
) -> list[MetricInfoShort]:
    full: list[MetricInfoFull] = _load_and_filter(
        filter_unit=filter_unit,
        filter_ids=filter_ids,
    )
    return [_to_short(metric=m) for m in full]


def aggregate_metrics_full(
    *,
    filter_unit: list[str] | None = None,
    filter_ids: list[str] | None = None,
) -> list[MetricInfoFull]:
    return _load_and_filter(
        filter_unit=filter_unit,
        filter_ids=filter_ids,
    )


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def _format_short_json(*, metrics: list[MetricInfoShort]) -> str:
    records: list[dict[str, Any]] = [asdict(m) for m in metrics]
    output: dict[str, Any] = {
        "metric_count": len(records),
        "metrics": records,
    }
    return json.dumps(output, indent=2, ensure_ascii=False)


def _format_full_json(*, metrics: list[MetricInfoFull]) -> str:
    records: list[dict[str, Any]] = [asdict(m) for m in metrics]
    output: dict[str, Any] = {
        "metric_count": len(records),
        "metrics": records,
    }
    return json.dumps(output, indent=2, ensure_ascii=False)


def _format_short_markdown(*, metrics: list[MetricInfoShort]) -> str:
    if len(metrics) == 0:
        return "No metrics found."

    lines: list[str] = [f"# Metrics ({len(metrics)})", ""]

    lines.append("| Metric Key | Name | Unit | Value Type |")
    lines.append("|------------|------|------|------------|")
    for m in metrics:
        lines.append(f"| `{m.metric_key}` | {m.name} | {m.unit} | {m.value_type} |")
    lines.append("")

    return "\n".join(lines)


def _format_full_markdown(*, metrics: list[MetricInfoFull]) -> str:
    if len(metrics) == 0:
        return "No metrics found."

    lines: list[str] = [f"# Metrics ({len(metrics)})", ""]

    # Summary table
    lines.append("| Metric Key | Name | Unit | Value Type |")
    lines.append("|------------|------|------|------------|")
    for m in metrics:
        key_link: str = f"[`{m.metric_key}`](#{m.metric_key})"
        lines.append(f"| {key_link} | {m.name} | {m.unit} | {m.value_type} |")
    lines.append("")

    # Detailed sections
    for m in metrics:
        lines.append(f"## {m.name} {{#{m.metric_key}}}")
        lines.append("")
        lines.append(f"**Key**: `{m.metric_key}`")
        lines.append(f"**Unit**: {m.unit}")
        lines.append(f"**Value type**: {m.value_type}")
        lines.append(f"**Version**: {m.version}")
        lines.append("")
        lines.append(m.description)
        lines.append("")
        if len(m.datasets) > 0:
            datasets_str: str = ", ".join(f"`{d}`" for d in m.datasets)
            lines.append(f"**Datasets**: {datasets_str}")
            lines.append("")

    return "\n".join(lines)


def _format_ids(*, metrics: list[MetricInfoShort]) -> str:
    return "\n".join(m.metric_key for m in metrics)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Aggregate all registered metrics in the project",
    )
    add_output_format_arg(parser=parser)
    add_detail_level_arg(parser=parser)
    parser.add_argument(
        "--unit",
        nargs="+",
        default=None,
        help="Filter by unit (e.g., f1 accuracy)",
    )
    parser.add_argument(
        "--ids",
        nargs="+",
        default=None,
        help="Filter by metric keys (exact match)",
    )

    args: argparse.Namespace = parser.parse_args()
    output_format: str = args.format
    detail_level: str = args.detail
    filter_unit: list[str] | None = args.unit
    filter_ids: list[str] | None = args.ids

    if detail_level == DETAIL_LEVEL_SHORT:
        short_metrics: list[MetricInfoShort] = aggregate_metrics_short(
            filter_unit=filter_unit,
            filter_ids=filter_ids,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_short_json(metrics=short_metrics))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(_format_short_markdown(metrics=short_metrics))
        elif output_format == OUTPUT_FORMAT_IDS:
            print(_format_ids(metrics=short_metrics))
        else:
            print(f"Unknown format: {output_format}", file=sys.stderr)
            sys.exit(1)
    elif detail_level == DETAIL_LEVEL_FULL:
        full_metrics: list[MetricInfoFull] = aggregate_metrics_full(
            filter_unit=filter_unit,
            filter_ids=filter_ids,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_full_json(metrics=full_metrics))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(_format_full_markdown(metrics=full_metrics))
        elif output_format == OUTPUT_FORMAT_IDS:
            short_from_full: list[MetricInfoShort] = [_to_short(metric=m) for m in full_metrics]
            print(_format_ids(metrics=short_from_full))
        else:
            print(f"Unknown format: {output_format}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unknown detail level: {detail_level}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
