"""Aggregate all task types in the project.

Reads every task type folder under meta/task_types/ and outputs
structured data about each task type.

Aggregator version: 2
"""

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from arf.scripts.aggregators.common.cli import (
    OUTPUT_FORMAT_IDS,
    OUTPUT_FORMAT_JSON,
    OUTPUT_FORMAT_MARKDOWN,
)
from arf.scripts.verificators.common.json_utils import load_json_file
from arf.scripts.verificators.common.paths import (
    TASK_TYPES_DIR,
    task_type_description_path,
    task_type_instruction_path,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VERSION_FIELD: str = "spec_version"
NAME_FIELD: str = "name"
SHORT_DESCRIPTION_FIELD: str = "short_description"
DETAILED_DESCRIPTION_FIELD: str = "detailed_description"
OPTIONAL_STEPS_FIELD: str = "optional_steps"
HAS_EXTERNAL_COSTS_FIELD: str = "has_external_costs"

OUTPUT_KEY_TASK_TYPES: str = "task_types"
OUTPUT_FIELD_TASK_TYPE_ID: str = "task_type_id"
OUTPUT_FIELD_SLUG: str = "slug"


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TaskTypeInfo:
    task_type_id: str
    name: str
    short_description: str
    detailed_description: str
    version: int
    optional_steps: list[str]
    has_external_costs: bool
    instruction: str


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def _discover_task_type_slugs() -> list[str]:
    if not TASK_TYPES_DIR.exists():
        return []
    return sorted(
        d.name for d in TASK_TYPES_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
    )


def _load_instruction(*, task_type_slug: str) -> str:
    file_path: Path = task_type_instruction_path(
        task_type_slug=task_type_slug,
    )
    if not file_path.exists():
        return ""
    return file_path.read_text(encoding="utf-8")


def _load_task_type(*, task_type_slug: str) -> TaskTypeInfo | None:
    file_path: Path = task_type_description_path(
        task_type_slug=task_type_slug,
    )
    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return None

    name: object = data.get(NAME_FIELD)
    short_desc: object = data.get(SHORT_DESCRIPTION_FIELD)
    detailed_desc: object = data.get(DETAILED_DESCRIPTION_FIELD)
    version: object = data.get(VERSION_FIELD)
    optional_steps: object = data.get(OPTIONAL_STEPS_FIELD)
    has_external_costs: object = data.get(HAS_EXTERNAL_COSTS_FIELD)

    if not isinstance(name, str):
        return None
    if not isinstance(short_desc, str):
        return None
    if not isinstance(detailed_desc, str):
        return None
    if not isinstance(version, int) or isinstance(version, bool):
        return None
    if not isinstance(optional_steps, list):
        return None
    if not all(isinstance(s, str) for s in optional_steps):
        return None
    if not isinstance(has_external_costs, bool):
        return None

    instruction: str = _load_instruction(task_type_slug=task_type_slug)

    return TaskTypeInfo(
        task_type_id=task_type_slug,
        name=name,
        short_description=short_desc,
        detailed_description=detailed_desc,
        version=version,
        optional_steps=optional_steps,
        has_external_costs=has_external_costs,
        instruction=instruction,
    )


def aggregate_task_types() -> list[TaskTypeInfo]:
    task_type_ids: list[str] = _discover_task_type_slugs()
    task_types: list[TaskTypeInfo] = []
    for task_type_id in task_type_ids:
        info: TaskTypeInfo | None = _load_task_type(
            task_type_slug=task_type_id,
        )
        if info is not None:
            task_types.append(info)
    return task_types


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def _task_type_to_dict(*, task_type: TaskTypeInfo) -> dict[str, Any]:
    record: dict[str, Any] = asdict(task_type)
    record[OUTPUT_FIELD_SLUG] = record[OUTPUT_FIELD_TASK_TYPE_ID]
    return record


def _format_json(*, task_types: list[TaskTypeInfo]) -> str:
    records: list[dict[str, Any]] = [_task_type_to_dict(task_type=t) for t in task_types]
    output: dict[str, Any] = {OUTPUT_KEY_TASK_TYPES: records}
    return json.dumps(output, indent=2, ensure_ascii=False)


def _format_markdown(*, task_types: list[TaskTypeInfo]) -> str:
    if len(task_types) == 0:
        return "No task types found."

    lines: list[str] = [f"# Task Types ({len(task_types)})", ""]

    # Table of contents
    lines.append("| Task Type ID | Name | Description |")
    lines.append("|--------------|------|-------------|")
    for t in task_types:
        task_type_id_link: str = f"[`{t.task_type_id}`](#{t.task_type_id})"
        lines.append(f"| {task_type_id_link} | {t.name} | {t.short_description} |")
    lines.append("")

    # Detailed sections
    for t in task_types:
        lines.append(f"## {t.name} {{#{t.task_type_id}}}")
        lines.append("")
        lines.append(f"**Task Type ID**: `{t.task_type_id}`")
        lines.append("")
        lines.append(t.detailed_description)
        lines.append("")

    return "\n".join(lines)


def _format_task_type_ids(*, task_types: list[TaskTypeInfo]) -> str:
    return "\n".join(t.task_type_id for t in task_types)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Aggregate all task types in the project",
    )
    parser.add_argument(
        "--format",
        choices=[
            OUTPUT_FORMAT_JSON,
            OUTPUT_FORMAT_MARKDOWN,
            OUTPUT_FORMAT_IDS,
        ],
        default=OUTPUT_FORMAT_JSON,
        help="Output format (default: json)",
    )
    args: argparse.Namespace = parser.parse_args()

    task_types: list[TaskTypeInfo] = aggregate_task_types()

    output_format: str = args.format
    if output_format == OUTPUT_FORMAT_JSON:
        print(_format_json(task_types=task_types))
    elif output_format == OUTPUT_FORMAT_MARKDOWN:
        print(_format_markdown(task_types=task_types))
    elif output_format == OUTPUT_FORMAT_IDS:
        print(_format_task_type_ids(task_types=task_types))
    else:
        print(f"Unknown format: {output_format}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
