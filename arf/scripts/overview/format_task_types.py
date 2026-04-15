"""Task types overview formatting."""

from pathlib import Path

from arf.scripts.aggregators.aggregate_task_types import TaskTypeInfo
from arf.scripts.overview.common import (
    normalize_markdown,
    overview_section_readme,
    remove_file_if_exists,
    write_file,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALL_OPTIONAL_STEPS_COUNT: int = 8
SECTION_NAME: str = "task-types"
TASK_TYPES_README: Path = overview_section_readme(section_name=SECTION_NAME)


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def _format_steps_column(*, optional_steps: list[str]) -> str:
    count: int = len(optional_steps)
    if count == ALL_OPTIONAL_STEPS_COUNT:
        return f"all {ALL_OPTIONAL_STEPS_COUNT}"
    return f"{count} optional"


def _format_task_type_detail(*, tt: TaskTypeInfo) -> str:
    steps_str: str = (
        ", ".join(f"`{s}`" for s in tt.optional_steps)
        if len(tt.optional_steps) > 0
        else "\u2014 none \u2014"
    )

    lines: list[str] = [
        "<details>",
        f"<summary><strong>{tt.name}</strong> (<code>{tt.task_type_id}</code>)</summary>",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| **ID** | `{tt.task_type_id}` |",
        f"| **Description** | {tt.short_description} |",
        f"| **Optional steps** | {steps_str} |",
        "",
        tt.detailed_description,
        "",
        "</details>",
    ]
    return "\n".join(lines)


def _format_task_types_overview(*, task_types: list[TaskTypeInfo]) -> str:
    if len(task_types) == 0:
        return "# Task Types\n\nNo task types found."

    lines: list[str] = [
        f"# Task Types ({len(task_types)})",
        "",
    ]

    # Summary table
    lines.append("| Type ID | Name | Steps | Description |")
    lines.append("|---------|------|-------|-------------|")
    for tt in task_types:
        steps_col: str = _format_steps_column(optional_steps=tt.optional_steps)
        lines.append(f"| `{tt.task_type_id}` | {tt.name} | {steps_col} | {tt.short_description} |")
    lines.append("")

    # Detail sections
    for tt in task_types:
        lines.append(_format_task_type_detail(tt=tt))
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Materialization
# ---------------------------------------------------------------------------


def materialize_task_types(*, task_types: list[TaskTypeInfo]) -> None:
    write_file(
        file_path=TASK_TYPES_README,
        content=normalize_markdown(
            content=_format_task_types_overview(task_types=task_types),
        ),
    )
    remove_file_if_exists(file_path=TASK_TYPES_README.parent.parent / "task-types.md")
