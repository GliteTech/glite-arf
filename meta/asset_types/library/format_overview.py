"""Library overview formatting with by-date-added and by-category views."""

from pathlib import Path

from arf.scripts.overview.common import (
    BY_CATEGORY_VIEW,
    BY_DATE_ADDED_VIEW,
    EMPTY_MARKDOWN_VALUE,
    README_FILE_NAME,
    DateGroup,
    category_links,
    group_items_by_date,
    normalize_markdown,
    overview_legacy_markdown_path,
    overview_section_readme,
    overview_section_view_dir,
    overview_section_view_readme,
    remove_dir_if_exists,
    remove_file_if_exists,
    repo_file_link,
    task_link,
    write_file,
)
from meta.asset_types.library.aggregator import LibraryInfoFull

SECTION_NAME: str = "libraries"
LIBRARIES_README: Path = overview_section_readme(section_name=SECTION_NAME)
LIBRARIES_BY_DATE_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=BY_DATE_ADDED_VIEW,
)
LIBRARIES_BY_DATE_README: Path = overview_section_view_readme(
    section_name=SECTION_NAME,
    view_name=BY_DATE_ADDED_VIEW,
)
LIBRARIES_BY_CATEGORY_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=BY_CATEGORY_VIEW,
)

_SECTION_REL: str = "../../"
_DATE_REL: str = "../../../"
_CATEGORY_REL: str = "../../../"


def _format_library_detail(*, library: LibraryInfoFull, rel: str) -> str:
    modules_str: str = ", ".join(f"`{module_path}`" for module_path in library.module_paths)
    dependencies_str: str = (
        ", ".join(library.dependencies) if len(library.dependencies) > 0 else EMPTY_MARKDOWN_VALUE
    )

    lines: list[str] = [
        "<details>",
        f"<summary>\U0001f4e6 <strong>{library.name}</strong>"
        f" (<code>{library.library_id}</code>)</summary>",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| **ID** | `{library.library_id}` |",
        f"| **Version** | {library.version} |",
        f"| **Modules** | {modules_str} |",
        f"| **Dependencies** | {dependencies_str} |",
        f"| **Date created** | {library.date_created} |",
        f"| **Categories** | {category_links(categories=library.categories, rel=rel)} |",
        f"| **Created by** | {task_link(task_id=library.created_by_task, rel=rel)} |",
        (
            "| **Documentation** | "
            f"{_format_description_link(description_path=library.description_path, rel=rel)} |"
        ),
        "",
    ]

    if len(library.entry_points) > 0:
        lines.append("**Entry points:**")
        lines.append("")
        for entry_point in library.entry_points:
            lines.append(
                f"* `{entry_point.name}` ({entry_point.kind}) \u2014 {entry_point.description}",
            )
        lines.append("")

    if len(library.short_description) > 0:
        lines.append(library.short_description)
        lines.append("")
    elif library.full_description is not None and len(library.full_description.strip()) > 0:
        lines.append(library.full_description.strip())
        lines.append("")

    lines.append("</details>")
    return "\n".join(lines)


def _format_description_link(*, description_path: str | None, rel: str) -> str:
    if description_path is None:
        return EMPTY_MARKDOWN_VALUE
    return repo_file_link(
        label="description.md",
        repo_relative_path=description_path,
        rel=rel,
    )


def _format_libraries_page(
    *,
    title: str,
    libraries: list[LibraryInfoFull],
    rel: str,
    show_date_index: bool,
    show_category_index: bool,
    back_link: str | None,
) -> str:
    if len(libraries) == 0:
        return f"# {title}\n\nNo libraries found."

    lines: list[str] = [f"# {title}", "", f"{len(libraries)} librar(y/ies)."]

    if back_link is not None:
        lines.append("")
        lines.append(f"[Back to all libraries]({back_link})")

    browse_parts: list[str] = []
    if show_category_index:
        all_categories: set[str] = set()
        for lib in libraries:
            all_categories.update(lib.categories)
        if len(all_categories) > 0:
            category_links_md: list[str] = [
                f"[`{c}`]({BY_CATEGORY_VIEW}/{c}.md)" for c in sorted(all_categories)
            ]
            browse_parts.append(f"By category: {', '.join(category_links_md)}")
    if show_date_index:
        browse_parts.append(f"[By date added]({BY_DATE_ADDED_VIEW}/{README_FILE_NAME})")
    if len(browse_parts) > 0:
        lines.append("")
        lines.append(f"**Browse by view**: {'; '.join(browse_parts)}")

    lines.append("")
    lines.append("---")
    lines.append("")

    for library in sorted(libraries, key=lambda item: (item.name.lower(), item.library_id)):
        lines.append(_format_library_detail(library=library, rel=rel))
        lines.append("")

    return "\n".join(lines)


def _format_libraries_by_date_page(*, libraries: list[LibraryInfoFull]) -> str:
    if len(libraries) == 0:
        return "# Libraries by Date Added\n\nNo libraries found."

    date_groups: list[DateGroup[LibraryInfoFull]] = group_items_by_date(
        items=libraries,
        get_date=lambda item: item.date_created,
        sort_key=lambda item: (item.name.lower(), item.library_id),
    )

    lines: list[str] = [
        "# Libraries by Date Added",
        "",
        f"{len(libraries)} librar(y/ies) grouped by creation date.",
        "",
        "[Back to all libraries](../README.md)",
        "",
        "---",
    ]

    for date_group in date_groups:
        lines.append("")
        lines.append(f"## {date_group.date} ({len(date_group.items)})")
        lines.append("")
        for library in date_group.items:
            lines.append(_format_library_detail(library=library, rel=_DATE_REL))
            lines.append("")

    return "\n".join(lines)


def materialize_libraries(*, libraries: list[LibraryInfoFull]) -> None:
    remove_dir_if_exists(dir_path=LIBRARIES_BY_DATE_DIR)
    remove_dir_if_exists(dir_path=LIBRARIES_BY_CATEGORY_DIR)

    write_file(
        file_path=LIBRARIES_README,
        content=normalize_markdown(
            content=_format_libraries_page(
                title=f"Libraries ({len(libraries)})",
                libraries=libraries,
                rel=_SECTION_REL,
                show_date_index=True,
                show_category_index=True,
                back_link=None,
            ),
        ),
    )
    write_file(
        file_path=LIBRARIES_BY_DATE_README,
        content=normalize_markdown(
            content=_format_libraries_by_date_page(libraries=libraries),
        ),
    )

    categories: dict[str, list[LibraryInfoFull]] = {}
    for lib in libraries:
        for cat in lib.categories:
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(lib)

    for cat, cat_libraries in sorted(categories.items()):
        write_file(
            file_path=LIBRARIES_BY_CATEGORY_DIR / f"{cat}.md",
            content=normalize_markdown(
                content=_format_libraries_page(
                    title=f"Libraries: `{cat}`",
                    libraries=cat_libraries,
                    rel=_CATEGORY_REL,
                    show_date_index=False,
                    show_category_index=False,
                    back_link="../README.md",
                ),
            ),
        )

    remove_file_if_exists(
        file_path=overview_legacy_markdown_path(section_name=SECTION_NAME),
    )
