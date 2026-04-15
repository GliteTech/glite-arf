"""Aggregate all categories in the project.

Reads every category folder under meta/categories/ and outputs
structured data about each category.

Aggregator version: 1.0
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
    CATEGORIES_DIR,
    category_description_path,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VERSION_FIELD: str = "spec_version"
NAME_FIELD: str = "name"
SHORT_DESCRIPTION_FIELD: str = "short_description"
DETAILED_DESCRIPTION_FIELD: str = "detailed_description"


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CategoryInfo:
    category_id: str
    name: str
    short_description: str
    detailed_description: str
    version: int


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def _discover_category_slugs() -> list[str]:
    if not CATEGORIES_DIR.exists():
        return []
    return sorted(
        d.name for d in CATEGORIES_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
    )


def _load_category(*, category_slug: str) -> CategoryInfo | None:
    file_path: Path = category_description_path(
        category_slug=category_slug,
    )
    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return None

    name: object = data.get(NAME_FIELD)
    short_desc: object = data.get(SHORT_DESCRIPTION_FIELD)
    detailed_desc: object = data.get(DETAILED_DESCRIPTION_FIELD)
    version: object = data.get(VERSION_FIELD)

    if not isinstance(name, str):
        return None
    if not isinstance(short_desc, str):
        return None
    if not isinstance(detailed_desc, str):
        return None
    if not isinstance(version, int) or isinstance(version, bool):
        return None

    return CategoryInfo(
        category_id=category_slug,
        name=name,
        short_description=short_desc,
        detailed_description=detailed_desc,
        version=version,
    )


def aggregate_categories() -> list[CategoryInfo]:
    category_ids: list[str] = _discover_category_slugs()
    categories: list[CategoryInfo] = []
    for category_id in category_ids:
        info: CategoryInfo | None = _load_category(category_slug=category_id)
        if info is not None:
            categories.append(info)
    return categories


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def _format_json(*, categories: list[CategoryInfo]) -> str:
    records: list[dict[str, Any]] = [asdict(c) for c in categories]
    output: dict[str, Any] = {"categories": records}
    return json.dumps(obj=output, indent=2, ensure_ascii=False)


def _format_markdown(*, categories: list[CategoryInfo]) -> str:
    if len(categories) == 0:
        return "No categories found."

    lines: list[str] = [f"# Categories ({len(categories)})", ""]

    # Table of contents
    lines.append("| Category ID | Name | Description |")
    lines.append("|-------------|------|-------------|")
    for c in categories:
        category_id_link: str = f"[`{c.category_id}`](#{c.category_id})"
        lines.append(f"| {category_id_link} | {c.name} | {c.short_description} |")
    lines.append("")

    # Detailed sections
    for c in categories:
        lines.append(f"## {c.name} {{#{c.category_id}}}")
        lines.append("")
        lines.append(f"**Category ID**: `{c.category_id}`")
        lines.append("")
        lines.append(c.detailed_description)
        lines.append("")

    return "\n".join(lines)


def _format_category_ids(*, categories: list[CategoryInfo]) -> str:
    return "\n".join(c.category_id for c in categories)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Aggregate all categories in the project",
    )
    parser.add_argument(
        "--format",
        choices=[OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_MARKDOWN, OUTPUT_FORMAT_IDS],
        default=OUTPUT_FORMAT_JSON,
        help="Output format (default: json)",
    )
    args: argparse.Namespace = parser.parse_args()

    categories: list[CategoryInfo] = aggregate_categories()

    output_format: str = args.format
    if output_format == OUTPUT_FORMAT_JSON:
        print(_format_json(categories=categories))
    elif output_format == OUTPUT_FORMAT_MARKDOWN:
        print(_format_markdown(categories=categories))
    elif output_format == OUTPUT_FORMAT_IDS:
        print(_format_category_ids(categories=categories))
    else:
        print(f"Unknown format: {output_format}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
