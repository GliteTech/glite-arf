"""Suggestion overview formatting with by-category and by-date-added views."""

from pathlib import Path

from arf.scripts.aggregators.aggregate_suggestions import SuggestionInfoFull
from arf.scripts.overview.common import (
    BY_CATEGORY_VIEW,
    BY_DATE_ADDED_VIEW,
    EMPTY_MARKDOWN_VALUE,
    META_CATEGORIES_SEGMENT,
    README_FILE_NAME,
    TASKS_SEGMENT,
    DateGroup,
    category_links,
    group_items_by_date,
    normalize_markdown,
    overview_legacy_markdown_path,
    overview_section_readme,
    overview_section_view_dir,
    overview_section_view_readme,
    paper_asset_link,
    remove_dir_if_exists,
    remove_file_if_exists,
    task_link,
    write_file,
)

SECTION_NAME: str = "suggestions"
SUGGESTIONS_README: Path = overview_section_readme(section_name=SECTION_NAME)
SUGGESTIONS_BY_CATEGORY_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=BY_CATEGORY_VIEW,
)
SUGGESTIONS_BY_DATE_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=BY_DATE_ADDED_VIEW,
)
SUGGESTIONS_BY_DATE_README: Path = overview_section_view_readme(
    section_name=SECTION_NAME,
    view_name=BY_DATE_ADDED_VIEW,
)

KIND_EMOJI: dict[str, str] = {
    "experiment": "\U0001f9ea",
    "dataset": "\U0001f4c2",
    "library": "\U0001f4da",
    "technique": "\U0001f527",
    "evaluation": "\U0001f4ca",
}

PRIORITY_ORDER: list[str] = ["high", "medium", "low"]

_SECTION_REL: str = "../../"
_CATEGORY_REL: str = "../../../"
_DATE_REL: str = "../../../"


def _format_suggestion_detail(
    *,
    suggestion: SuggestionInfoFull,
    rel: str,
    covered_by: str | None,
) -> str:
    if suggestion.source_paper is not None:
        paper_str: str = paper_asset_link(
            paper_id=suggestion.source_paper,
            task_id=suggestion.source_task,
            rel=rel,
        )
    else:
        paper_str = EMPTY_MARKDOWN_VALUE

    if covered_by is not None:
        task_url: str = f"{rel}{TASKS_SEGMENT}/{covered_by}/"
        title_html: str = (
            f"<summary>\u2705 <s>{suggestion.title}</s>"
            f' \u2014 covered by <a href="{task_url}"><code>{covered_by}</code></a>'
            f" ({suggestion.id})</summary>"
        )
    else:
        emoji: str = KIND_EMOJI.get(suggestion.kind, "")
        title_html = (
            f"<summary>{emoji} <strong>{suggestion.title}</strong> ({suggestion.id})</summary>"
        )
    date_added_str: str = (
        suggestion.date_added if suggestion.date_added is not None else EMPTY_MARKDOWN_VALUE
    )

    lines: list[str] = [
        "<details>",
        title_html,
        "",
        "| Field | Value |",
        "|---|---|",
        f"| **ID** | `{suggestion.id}` |",
        f"| **Kind** | {suggestion.kind} |",
        f"| **Date added** | {date_added_str} |",
        f"| **Source task** | {task_link(task_id=suggestion.source_task, rel=rel)} |",
        f"| **Source paper** | {paper_str} |",
        f"| **Categories** | {category_links(categories=suggestion.categories, rel=rel)} |",
        "",
        suggestion.description,
        "",
        "</details>",
    ]
    return "\n".join(lines)


def _append_suggestion_sections(
    *,
    lines: list[str],
    suggestions: list[SuggestionInfoFull],
    task_map: dict[str, str],
    rel: str,
) -> None:
    open_suggestions: list[SuggestionInfoFull] = [s for s in suggestions if s.id not in task_map]
    closed_suggestions: list[SuggestionInfoFull] = [s for s in suggestions if s.id in task_map]

    if len(open_suggestions) > 0:
        for priority in PRIORITY_ORDER:
            group: list[SuggestionInfoFull] = [
                suggestion for suggestion in open_suggestions if suggestion.priority == priority
            ]
            if len(group) == 0:
                continue
            lines.append("")
            lines.append(f"## {priority.capitalize()} Priority")
            lines.append("")
            for suggestion in sorted(group, key=lambda item: (item.title.lower(), item.id)):
                lines.append(
                    _format_suggestion_detail(
                        suggestion=suggestion,
                        rel=rel,
                        covered_by=None,
                    ),
                )
                lines.append("")

    if len(closed_suggestions) > 0:
        lines.append("")
        lines.append("## Closed")
        lines.append("")
        for suggestion in sorted(
            closed_suggestions,
            key=lambda item: (item.title.lower(), item.id),
        ):
            lines.append(
                _format_suggestion_detail(
                    suggestion=suggestion,
                    rel=rel,
                    covered_by=task_map[suggestion.id],
                ),
            )
            lines.append("")


def _format_suggestions_page(
    *,
    title: str,
    subtitle: str,
    suggestions: list[SuggestionInfoFull],
    task_map: dict[str, str],
    rel: str,
    show_category_index: bool,
    show_date_index: bool,
    back_link: str | None,
) -> str:
    open_suggestions: list[SuggestionInfoFull] = [s for s in suggestions if s.id not in task_map]
    closed_suggestions: list[SuggestionInfoFull] = [s for s in suggestions if s.id in task_map]
    open_count: int = len(open_suggestions)
    closed_count: int = len(closed_suggestions)

    lines: list[str] = [f"# {title}", ""]

    parts: list[str] = []
    if open_count > 0:
        open_by_priority: list[str] = []
        for priority in PRIORITY_ORDER:
            count: int = len([s for s in open_suggestions if s.priority == priority])
            if count > 0:
                open_by_priority.append(f"{count} {priority}")
        parts.append(f"**{open_count} open** ({', '.join(open_by_priority)})")
    if closed_count > 0:
        parts.append(f"**{closed_count} closed**")
    lines.append(f"{subtitle} {', '.join(parts)}.")

    if back_link is not None:
        lines.append("")
        lines.append(f"[Back to all suggestions]({back_link})")

    browse_links: list[str] = []
    if show_category_index:
        all_categories: set[str] = set()
        for suggestion in suggestions:
            all_categories.update(suggestion.categories)
        if len(all_categories) > 0:
            category_links_md: list[str] = [
                f"[`{category}`]({BY_CATEGORY_VIEW}/{category}.md)"
                for category in sorted(all_categories)
            ]
            browse_links.append(f"By category: {', '.join(category_links_md)}")
    if show_date_index:
        browse_links.append(f"[By date added]({BY_DATE_ADDED_VIEW}/{README_FILE_NAME})")
    if len(browse_links) > 0:
        lines.append("")
        lines.append(f"**Browse by view**: {'; '.join(browse_links)}")

    lines.append("")
    lines.append("---")

    _append_suggestion_sections(
        lines=lines,
        suggestions=suggestions,
        task_map=task_map,
        rel=rel,
    )
    return "\n".join(lines)


def _format_suggestions_by_date_page(
    *,
    suggestions: list[SuggestionInfoFull],
    task_map: dict[str, str],
) -> str:
    if len(suggestions) == 0:
        return "# Suggestions by Date Added\n\nNo suggestions found."

    date_groups: list[DateGroup[SuggestionInfoFull]] = group_items_by_date(
        items=suggestions,
        get_date=lambda item: item.date_added,
        sort_key=lambda item: (item.title.lower(), item.id),
    )

    lines: list[str] = [
        "# Suggestions by Date Added",
        "",
        f"{len(suggestions)} suggestion(s) grouped by derived added date.",
        "",
        "[Back to all suggestions](../README.md)",
        "",
        "---",
    ]

    for date_group in date_groups:
        lines.append("")
        lines.append(f"## {date_group.date} ({len(date_group.items)})")
        _append_suggestion_sections(
            lines=lines,
            suggestions=date_group.items,
            task_map=task_map,
            rel=_DATE_REL,
        )

    return "\n".join(lines)


def materialize_suggestions(
    *,
    suggestions: list[SuggestionInfoFull],
    task_map: dict[str, str],
) -> None:
    remove_dir_if_exists(dir_path=SUGGESTIONS_BY_CATEGORY_DIR)
    remove_dir_if_exists(dir_path=SUGGESTIONS_BY_DATE_DIR)

    write_file(
        file_path=SUGGESTIONS_README,
        content=normalize_markdown(
            content=_format_suggestions_page(
                title="Research Suggestions Backlog",
                subtitle=f"{len(suggestions)} suggestions",
                suggestions=suggestions,
                task_map=task_map,
                rel=_SECTION_REL,
                show_category_index=True,
                show_date_index=True,
                back_link=None,
            ),
        ),
    )

    categories: dict[str, list[SuggestionInfoFull]] = {}
    for suggestion in suggestions:
        for category in suggestion.categories:
            if category not in categories:
                categories[category] = []
            categories[category].append(suggestion)

    for category, category_suggestions in sorted(categories.items()):
        write_file(
            file_path=SUGGESTIONS_BY_CATEGORY_DIR / f"{category}.md",
            content=normalize_markdown(
                content=_format_suggestions_page(
                    title=f"Suggestions: `{category}`",
                    subtitle=(
                        f"{len(category_suggestions)} suggestion(s) in category "
                        f"[`{category}`]({_CATEGORY_REL}{META_CATEGORIES_SEGMENT}/{category}/)"
                    ),
                    suggestions=category_suggestions,
                    task_map=task_map,
                    rel=_CATEGORY_REL,
                    show_category_index=False,
                    show_date_index=False,
                    back_link="../README.md",
                ),
            ),
        )

    write_file(
        file_path=SUGGESTIONS_BY_DATE_README,
        content=normalize_markdown(
            content=_format_suggestions_by_date_page(
                suggestions=suggestions,
                task_map=task_map,
            ),
        ),
    )

    remove_file_if_exists(
        file_path=overview_legacy_markdown_path(section_name=SECTION_NAME),
    )
    remove_file_if_exists(file_path=SUGGESTIONS_README.parent / "index.md")
