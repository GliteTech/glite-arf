"""Dataset overview formatting with by-date-added and by-category views."""

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
from meta.asset_types.dataset.aggregator import DatasetInfoFull

SECTION_NAME: str = "datasets"
DATASETS_README: Path = overview_section_readme(section_name=SECTION_NAME)
DATASETS_BY_DATE_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=BY_DATE_ADDED_VIEW,
)
DATASETS_BY_DATE_README: Path = overview_section_view_readme(
    section_name=SECTION_NAME,
    view_name=BY_DATE_ADDED_VIEW,
)
DATASETS_BY_CATEGORY_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=BY_CATEGORY_VIEW,
)

_SECTION_REL: str = "../../"
_DATE_REL: str = "../../../"
_CATEGORY_REL: str = "../../../"
DATASETS_BY_DATE_TITLE: str = "Datasets by Date Added"
NO_DATASETS_FOUND_TEXT: str = "No datasets found."


def _format_dataset_detail(*, dataset: DatasetInfoFull, rel: str) -> str:
    authors_str: str = ", ".join(author.name for author in dataset.authors)
    version_str: str = f" v{dataset.version}" if dataset.version is not None else ""
    license_str: str = dataset.license if dataset.license is not None else EMPTY_MARKDOWN_VALUE
    url_str: str = dataset.url if dataset.url is not None else EMPTY_MARKDOWN_VALUE
    date_added_str: str = (
        dataset.date_added if dataset.date_added is not None else EMPTY_MARKDOWN_VALUE
    )

    added_by_str: str = (
        task_link(task_id=dataset.added_by_task, rel=rel)
        if dataset.added_by_task is not None
        else EMPTY_MARKDOWN_VALUE
    )

    lines: list[str] = [
        "<details>",
        f"<summary>\U0001f4c2 <strong>{dataset.name}{version_str}</strong></summary>",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| **ID** | `{dataset.dataset_id}` |",
        f"| **Year** | {dataset.year} |",
        f"| **Authors** | {authors_str} |",
        f"| **URL** | {url_str} |",
        f"| **License** | {license_str} |",
        f"| **Access** | {dataset.access_kind} |",
        f"| **Size** | {dataset.size_description} |",
        f"| **Date added** | {date_added_str} |",
        f"| **Categories** | {category_links(categories=dataset.categories, rel=rel)} |",
        f"| **Added by** | {added_by_str} |",
    ]

    if dataset.description_path is not None:
        description_link: str = repo_file_link(
            label="description.md",
            repo_relative_path=dataset.description_path,
            rel=rel,
        )
        lines.append(f"| **Description** | {description_link} |")
    else:
        lines.append(f"| **Description** | {EMPTY_MARKDOWN_VALUE} |")

    if len(dataset.short_description) > 0:
        lines.append(f"| **Summary** | {dataset.short_description} |")
    else:
        lines.append(f"| **Summary** | {EMPTY_MARKDOWN_VALUE} |")

    lines.append("")
    lines.append("</details>")
    return "\n".join(lines)


def _format_datasets_page(
    *,
    title: str,
    datasets: list[DatasetInfoFull],
    rel: str,
    show_date_index: bool,
    show_category_index: bool,
    back_link: str | None,
) -> str:
    if len(datasets) == 0:
        return f"# {title}\n\n{NO_DATASETS_FOUND_TEXT}"

    lines: list[str] = [f"# {title}", "", f"{len(datasets)} dataset(s)."]

    if back_link is not None:
        lines.append("")
        lines.append(f"[Back to all datasets]({back_link})")

    browse_parts: list[str] = []
    if show_category_index:
        all_categories: set[str] = set()
        for d in datasets:
            all_categories.update(d.categories)
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

    for dataset in sorted(datasets, key=lambda item: (item.name.lower(), item.dataset_id)):
        lines.append(_format_dataset_detail(dataset=dataset, rel=rel))
        lines.append("")

    return "\n".join(lines)


def _format_datasets_by_date_page(*, datasets: list[DatasetInfoFull]) -> str:
    if len(datasets) == 0:
        return f"# {DATASETS_BY_DATE_TITLE}\n\n{NO_DATASETS_FOUND_TEXT}"

    date_groups: list[DateGroup[DatasetInfoFull]] = group_items_by_date(
        items=datasets,
        get_date=lambda item: item.date_added,
        sort_key=lambda item: (item.name.lower(), item.dataset_id),
    )

    lines: list[str] = [
        f"# {DATASETS_BY_DATE_TITLE}",
        "",
        f"{len(datasets)} dataset(s) grouped by project added date.",
        "",
        "[Back to all datasets](../README.md)",
        "",
        "---",
    ]

    for date_group in date_groups:
        lines.append("")
        lines.append(f"## {date_group.date} ({len(date_group.items)})")
        lines.append("")
        for dataset in date_group.items:
            lines.append(_format_dataset_detail(dataset=dataset, rel=_DATE_REL))
            lines.append("")

    return "\n".join(lines)


def materialize_datasets(*, datasets: list[DatasetInfoFull]) -> None:
    remove_dir_if_exists(dir_path=DATASETS_BY_DATE_DIR)
    remove_dir_if_exists(dir_path=DATASETS_BY_CATEGORY_DIR)

    write_file(
        file_path=DATASETS_README,
        content=normalize_markdown(
            content=_format_datasets_page(
                title=f"Datasets ({len(datasets)})",
                datasets=datasets,
                rel=_SECTION_REL,
                show_date_index=True,
                show_category_index=True,
                back_link=None,
            ),
        ),
    )
    write_file(
        file_path=DATASETS_BY_DATE_README,
        content=normalize_markdown(
            content=_format_datasets_by_date_page(datasets=datasets),
        ),
    )

    categories: dict[str, list[DatasetInfoFull]] = {}
    for d in datasets:
        for cat in d.categories:
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(d)

    for cat, cat_datasets in sorted(categories.items()):
        write_file(
            file_path=DATASETS_BY_CATEGORY_DIR / f"{cat}.md",
            content=normalize_markdown(
                content=_format_datasets_page(
                    title=f"Datasets: `{cat}`",
                    datasets=cat_datasets,
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
