"""Paper overview formatting with by-category and by-date-added views."""

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
from meta.asset_types.paper.aggregator import AuthorInfo, PaperInfoFull

SECTION_NAME: str = "papers"
PAPERS_README: Path = overview_section_readme(section_name=SECTION_NAME)
PAPERS_BY_CATEGORY_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=BY_CATEGORY_VIEW,
)
PAPERS_BY_DATE_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=BY_DATE_ADDED_VIEW,
)
PAPERS_BY_DATE_README: Path = overview_section_view_readme(
    section_name=SECTION_NAME,
    view_name=BY_DATE_ADDED_VIEW,
)
PAPERS_LEGACY_MARKDOWN_PATH: Path = overview_legacy_markdown_path(
    section_name=SECTION_NAME,
)

VENUE_KIND_EMOJI: dict[str, str] = {
    "conference": "\U0001f3e4",
    "journal": "\U0001f4d6",
    "workshop": "\U0001f527",
    "preprint": "\U0001f4dd",
    "book": "\U0001f4da",
    "thesis": "\U0001f393",
    "technical_report": "\U0001f4cb",
    "other": "\U0001f4c4",
}

_SECTION_REL: str = "../../"
_CATEGORY_REL: str = "../../../"
_DATE_REL: str = "../../../"


def _short_authors(*, authors: list[AuthorInfo]) -> str:
    if len(authors) == 0:
        return "Unknown"
    first: str = authors[0].name.split()[-1]
    if len(authors) == 1:
        return first
    if len(authors) == 2:
        second: str = authors[1].name.split()[-1]
        return f"{first} & {second}"
    return f"{first} et al."


def _format_paper_detail(*, paper: PaperInfoFull, rel: str) -> str:
    emoji: str = VENUE_KIND_EMOJI.get(paper.venue_kind, "\U0001f4c4")
    authors_short: str = _short_authors(authors=paper.authors)
    authors_full: str = ", ".join(author.name for author in paper.authors)
    doi_str: str = f"`{paper.doi}`" if paper.doi is not None else EMPTY_MARKDOWN_VALUE
    url_str: str = paper.url if paper.url is not None else EMPTY_MARKDOWN_VALUE
    summary_str: str = (
        repo_file_link(
            label="summary.md",
            repo_relative_path=paper.summary_path.as_posix(),
            rel=rel,
        )
        if paper.summary_path is not None
        else EMPTY_MARKDOWN_VALUE
    )

    lines: list[str] = [
        "<details>",
        f"<summary>{emoji} {paper.title} \u2014 {authors_short}, {paper.year}</summary>",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| **ID** | `{paper.paper_id}` |",
        f"| **Authors** | {authors_full} |",
        f"| **Venue** | {paper.journal} ({paper.venue_kind}) |",
        f"| **DOI** | {doi_str} |",
        f"| **URL** | {url_str} |",
        f"| **Date added** | {paper.date_added} |",
        f"| **Categories** | {category_links(categories=paper.categories, rel=rel)} |",
        f"| **Added by** | {task_link(task_id=paper.added_by_task, rel=rel)} |",
        f"| **Full summary** | {summary_str} |",
        "",
    ]

    if paper.summary is not None and len(paper.summary.strip()) > 0:
        lines.append(paper.summary.strip())
        lines.append("")
    elif len(paper.abstract) > 0:
        lines.append(paper.abstract)
        lines.append("")

    lines.append("</details>")
    return "\n".join(lines)


def _format_papers_page(
    *,
    title: str,
    papers: list[PaperInfoFull],
    rel: str,
    show_category_index: bool,
    show_date_index: bool,
    back_link: str | None,
) -> str:
    if len(papers) == 0:
        return f"# {title}\n\nNo papers found."

    years: dict[int, list[PaperInfoFull]] = {}
    for paper in papers:
        if paper.year not in years:
            years[paper.year] = []
        years[paper.year].append(paper)

    lines: list[str] = [f"# {title}", "", f"{len(papers)} papers across {len(years)} year(s)."]

    if back_link is not None:
        lines.append("")
        lines.append(f"[Back to all papers]({back_link})")

    browse_links: list[str] = []
    if show_category_index:
        all_categories: set[str] = set()
        for paper in papers:
            all_categories.update(paper.categories)
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

    for year in sorted(years.keys(), reverse=True):
        year_papers: list[PaperInfoFull] = sorted(
            years[year],
            key=lambda item: (item.title.lower(), item.paper_id),
        )
        lines.append("")
        lines.append(f"## {year} ({len(year_papers)})")
        lines.append("")
        for paper in year_papers:
            lines.append(_format_paper_detail(paper=paper, rel=rel))
            lines.append("")

    return "\n".join(lines)


def _format_papers_by_date_page(*, papers: list[PaperInfoFull]) -> str:
    if len(papers) == 0:
        return "# Papers by Date Added\n\nNo papers found."

    date_groups: list[DateGroup[PaperInfoFull]] = group_items_by_date(
        items=papers,
        get_date=lambda item: item.date_added,
        sort_key=lambda item: (item.title.lower(), item.paper_id),
    )

    lines: list[str] = [
        "# Papers by Date Added",
        "",
        f"{len(papers)} paper(s) grouped by project added date.",
        "",
        "[Back to all papers](../README.md)",
        "",
        "---",
    ]

    for date_group in date_groups:
        lines.append("")
        lines.append(f"## {date_group.date} ({len(date_group.items)})")
        lines.append("")
        for paper in date_group.items:
            lines.append(_format_paper_detail(paper=paper, rel=_DATE_REL))
            lines.append("")

    return "\n".join(lines)


def materialize_papers(*, papers: list[PaperInfoFull]) -> None:
    remove_dir_if_exists(dir_path=PAPERS_BY_CATEGORY_DIR)
    remove_dir_if_exists(dir_path=PAPERS_BY_DATE_DIR)

    write_file(
        file_path=PAPERS_README,
        content=normalize_markdown(
            content=_format_papers_page(
                title=f"Papers ({len(papers)})",
                papers=papers,
                rel=_SECTION_REL,
                show_category_index=True,
                show_date_index=True,
                back_link=None,
            ),
        ),
    )

    categories: dict[str, list[PaperInfoFull]] = {}
    for paper in papers:
        for category in paper.categories:
            if category not in categories:
                categories[category] = []
            categories[category].append(paper)

    for category, category_papers in sorted(categories.items()):
        write_file(
            file_path=PAPERS_BY_CATEGORY_DIR / f"{category}.md",
            content=normalize_markdown(
                content=_format_papers_page(
                    title=f"Papers: `{category}` ({len(category_papers)})",
                    papers=category_papers,
                    rel=_CATEGORY_REL,
                    show_category_index=False,
                    show_date_index=False,
                    back_link="../README.md",
                ),
            ),
        )

    write_file(
        file_path=PAPERS_BY_DATE_README,
        content=normalize_markdown(
            content=_format_papers_by_date_page(papers=papers),
        ),
    )

    remove_file_if_exists(file_path=PAPERS_LEGACY_MARKDOWN_PATH)
