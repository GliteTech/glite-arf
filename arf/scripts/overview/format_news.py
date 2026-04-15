"""News overview formatting.

Creates overview/news/ with an index page and per-day pages that embed
the raw news/*.md content with prev/next navigation.
"""

import json
import re
from dataclasses import dataclass
from datetime import date as date_type
from pathlib import Path

from arf.scripts.overview.common import (
    normalize_markdown,
    rewrite_embedded_paths,
    write_file,
)
from arf.scripts.overview.paths import (
    OVERVIEW_DIR,
    README_FILE_NAME,
)
from arf.scripts.verificators.common.paths import NEWS_DIR

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SECTION_NAME: str = "news"
NEWS_OVERVIEW_DIR: Path = OVERVIEW_DIR / SECTION_NAME
NEWS_INDEX_README: Path = NEWS_OVERVIEW_DIR / README_FILE_NAME

DATE_PATTERN: re.Pattern[str] = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_MONTH_ABBR: list[str] = [
    "",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def format_date_human(iso_date: str) -> str:
    """Convert ``YYYY-MM-DD`` to ``Apr 7, 2026`` style."""
    d: date_type = date_type.fromisoformat(iso_date)
    return f"{_MONTH_ABBR[d.month]} {d.day}, {d.year}"


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class NewsDayInfo:
    date: str
    md_path: Path
    json_path: Path
    total_cost_usd: float | None
    tasks_completed_count: int
    tasks_created_count: int


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def discover_news_dates() -> list[str]:
    if not NEWS_DIR.exists():
        return []
    dates: list[str] = []
    for md_file in sorted(NEWS_DIR.glob("*.md")):
        stem: str = md_file.stem
        if DATE_PATTERN.match(stem) is not None:
            dates.append(stem)
    return dates


def _load_news_day(*, date: str) -> NewsDayInfo:
    md_path: Path = NEWS_DIR / f"{date}.md"
    json_path: Path = NEWS_DIR / f"{date}.json"
    total_cost: float | None = None
    completed: int = 0
    created: int = 0
    if json_path.exists():
        try:
            data: object = json.loads(json_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cost_val: object = data.get("total_cost_usd")
                if isinstance(cost_val, int | float):
                    total_cost = float(cost_val)
                completed_val: object = data.get("tasks_completed")
                if isinstance(completed_val, list):
                    completed = len(completed_val)
                created_val: object = data.get("tasks_created")
                if isinstance(created_val, list):
                    created = len(created_val)
        except (json.JSONDecodeError, OSError):
            pass
    return NewsDayInfo(
        date=date,
        md_path=md_path,
        json_path=json_path,
        total_cost_usd=total_cost,
        tasks_completed_count=completed,
        tasks_created_count=created,
    )


def load_all_news() -> list[NewsDayInfo]:
    dates: list[str] = discover_news_dates()
    return [_load_news_day(date=d) for d in dates]


# ---------------------------------------------------------------------------
# Path rewriting
# ---------------------------------------------------------------------------

NEWS_SOURCE_DIR: str = "news"
NEWS_TARGET_REL: str = "../../"


def _rewrite_relative_paths(*, content: str) -> str:
    return rewrite_embedded_paths(
        content=content,
        source_dir=NEWS_SOURCE_DIR,
        target_rel=NEWS_TARGET_REL,
    )


# ---------------------------------------------------------------------------
# Per-day page
# ---------------------------------------------------------------------------


def _format_day_page(
    *,
    day: NewsDayInfo,
    prev_date: str | None,
    next_date: str | None,
) -> str:
    lines: list[str] = []

    # Navigation bar
    nav_parts: list[str] = []
    if prev_date is not None:
        nav_parts.append(f"[← {format_date_human(prev_date)}]({prev_date}.md)")
    nav_parts.append("[Index](README.md)")
    if next_date is not None:
        nav_parts.append(f"[{format_date_human(next_date)} →]({next_date}.md)")
    lines.append(" | ".join(nav_parts))
    lines.append("")
    lines.append("---")
    lines.append("")

    # Embed the raw markdown content with rewritten relative paths.
    # News files live in news/ and use ../tasks/, ../overview/ etc.
    # Overview pages live in overview/news/ — one level deeper — so
    # rewrite ../ to ../../ for all relative links and images.
    if day.md_path.exists():
        try:
            raw_content: str = day.md_path.read_text(encoding="utf-8").rstrip()
            raw_content = _rewrite_relative_paths(content=raw_content)
            lines.append(raw_content)
        except (OSError, UnicodeDecodeError):
            lines.append(f"*Error reading {day.md_path}*")
    else:
        lines.append(f"*No news file found for {day.date}*")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Bottom navigation (repeat)
    lines.append(" | ".join(nav_parts))
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Index page
# ---------------------------------------------------------------------------


def _format_index_page(*, days: list[NewsDayInfo]) -> str:
    lines: list[str] = [
        "# Daily News",
        "",
        f"{len(days)} daily summaries.",
        "",
        "[Back to dashboard](../README.md)",
        "",
        "---",
        "",
    ]

    if len(days) == 0:
        lines.append("No news files found yet.")
        lines.append("")
        return "\n".join(lines)

    lines.append("| Date | Tasks completed | Tasks created | Cost |")
    lines.append("| --- | --- | --- | --- |")

    # Newest first
    for day in reversed(days):
        cost_str: str = f"${day.total_cost_usd:,.0f}" if day.total_cost_usd is not None else "—"
        lines.append(
            f"| [{format_date_human(day.date)}]({day.date}.md)"
            f" | {day.tasks_completed_count}"
            f" | {day.tasks_created_count}"
            f" | {cost_str} |"
        )

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def materialize_news() -> list[NewsDayInfo]:
    days: list[NewsDayInfo] = load_all_news()

    # Ensure output directory exists
    NEWS_OVERVIEW_DIR.mkdir(parents=True, exist_ok=True)

    # Write index page
    write_file(
        file_path=NEWS_INDEX_README,
        content=normalize_markdown(
            content=_format_index_page(days=days),
        ),
    )

    # Write per-day pages
    for i, day in enumerate(days):
        prev_date: str | None = days[i - 1].date if i > 0 else None
        next_date: str | None = days[i + 1].date if i < len(days) - 1 else None
        page_path: Path = NEWS_OVERVIEW_DIR / f"{day.date}.md"
        write_file(
            file_path=page_path,
            content=_format_day_page(
                day=day,
                prev_date=prev_date,
                next_date=next_date,
            ),
        )

    return days
