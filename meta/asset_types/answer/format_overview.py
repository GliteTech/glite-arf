"""Answer overview formatting with by-category and by-date-added views."""

from re import Pattern
from re import compile as compile_regex

from arf.scripts.overview.common import (
    BY_CATEGORY_VIEW,
    BY_DATE_ADDED_VIEW,
    EMPTY_MARKDOWN_VALUE,
    README_FILE_NAME,
    DateGroup,
    answer_asset_link,
    category_links,
    group_items_by_date,
    normalize_markdown,
    overview_legacy_markdown_path,
    remove_dir_if_exists,
    remove_file_if_exists,
    repo_file_link,
    task_link,
    write_file,
)
from arf.scripts.overview.paths import (
    ANSWERS_BY_CATEGORY_DIR,
    ANSWERS_BY_DATE_DIR,
    ANSWERS_BY_DATE_README,
    ANSWERS_README,
    CATEGORY_PAGE_REL,
    DATE_PAGE_REL,
    SUBPAGE_REL,
    markdown_rel_prefix,
)
from meta.asset_types.answer.aggregator import AnswerCategory, AnswerInfoFull, TaskID

SECTION_NAME: str = "answers"
_SECTION_REL: str = markdown_rel_prefix(relative_path=SUBPAGE_REL)
_CATEGORY_REL: str = markdown_rel_prefix(relative_path=CATEGORY_PAGE_REL)
_DATE_REL: str = markdown_rel_prefix(relative_path=DATE_PAGE_REL)

_CITATION_PATTERN: Pattern[str] = compile_regex(r"\[[^\[\]]+\]")


def _strip_citations(*, text: str) -> str:
    return _CITATION_PATTERN.sub("", text).strip()


def _format_url_links(*, urls: list[str]) -> str:
    if len(urls) == 0:
        return EMPTY_MARKDOWN_VALUE
    return ", ".join(f"[url {index + 1}]({url})" for index, url in enumerate(urls))


def _format_task_links(*, task_ids: list[TaskID], rel: str) -> str:
    if len(task_ids) == 0:
        return EMPTY_MARKDOWN_VALUE
    return ", ".join(task_link(task_id=task_id, rel=rel) for task_id in task_ids)


def _format_answer_detail(*, answer: AnswerInfoFull, rel: str) -> str:
    methods_str: str = ", ".join(f"`{method}`" for method in answer.answer_methods)
    answer_link_str: str = answer_asset_link(
        answer_id=answer.answer_id,
        task_id=answer.created_by_task,
        rel=rel,
    )
    paper_sources_str: str = (
        ", ".join(f"`{paper_id}`" for paper_id in answer.source_paper_ids)
        if len(answer.source_paper_ids) > 0
        else EMPTY_MARKDOWN_VALUE
    )
    full_answer_str: str = (
        repo_file_link(
            label="full_answer.md",
            repo_relative_path=answer.full_answer_path.as_posix(),
            rel=rel,
        )
        if answer.full_answer_path is not None
        else EMPTY_MARKDOWN_VALUE
    )

    lines: list[str] = [
        "<details>",
        f"<summary><strong>{answer.question}</strong></summary>",
        "",
        f"**Confidence**: {answer.confidence}",
        "",
    ]

    if answer.short_answer is not None and len(answer.short_answer.strip()) > 0:
        lines.append(_strip_citations(text=answer.short_answer.strip()))
        lines.append("")

    lines.extend(
        [
            "| Field | Value |",
            "|---|---|",
            f"| **Full answer** | {full_answer_str} |",
            f"| **ID** | {answer_link_str} |",
            f"| **Question** | {answer.question} |",
            f"| **Methods** | {methods_str} |",
            f"| **Confidence** | {answer.confidence} |",
            f"| **Date created** | {answer.date_created} |",
            f"| **Categories** | {category_links(categories=answer.categories, rel=rel)} |",
            f"| **Paper sources** | {paper_sources_str} |",
            (
                "| **Task sources** | "
                f"{_format_task_links(task_ids=answer.source_task_ids, rel=rel)} |"
            ),
            f"| **URL sources** | {_format_url_links(urls=answer.source_urls)} |",
            f"| **Created by** | {task_link(task_id=answer.created_by_task, rel=rel)} |",
            "",
        ]
    )

    lines.append("</details>")
    return "\n".join(lines)


def _format_answers_page(
    *,
    title: str,
    answers: list[AnswerInfoFull],
    rel: str,
    show_category_index: bool,
    show_date_index: bool,
    back_link: str | None,
) -> str:
    if len(answers) == 0:
        return f"# {title}\n\nNo answers found."

    lines: list[str] = [f"# {title}", "", f"{len(answers)} answer(s)."]

    if back_link is not None:
        lines.append("")
        lines.append(f"[Back to all answers]({back_link})")

    browse_links: list[str] = []
    if show_category_index:
        all_categories: set[AnswerCategory] = set()
        for answer in answers:
            all_categories.update(answer.categories)
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
    lines.append("")

    for answer in sorted(answers, key=lambda item: (item.question.lower(), item.answer_id)):
        lines.append(_format_answer_detail(answer=answer, rel=rel))
        lines.append("")

    return "\n".join(lines)


def _format_answers_by_date_page(*, answers: list[AnswerInfoFull]) -> str:
    if len(answers) == 0:
        return "# Answers by Date Added\n\nNo answers found."

    date_groups: list[DateGroup[AnswerInfoFull]] = group_items_by_date(
        items=answers,
        get_date=lambda item: item.date_created,
        sort_key=lambda item: (item.question.lower(), item.answer_id),
    )

    lines: list[str] = [
        "# Answers by Date Added",
        "",
        f"{len(answers)} answer(s) grouped by creation date.",
        "",
        "[Back to all answers](../README.md)",
        "",
        "---",
    ]

    for date_group in date_groups:
        lines.append("")
        lines.append(f"## {date_group.date} ({len(date_group.items)})")
        lines.append("")
        for answer in date_group.items:
            lines.append(_format_answer_detail(answer=answer, rel=_DATE_REL))
            lines.append("")

    return "\n".join(lines)


def materialize_answers(*, answers: list[AnswerInfoFull]) -> None:
    remove_dir_if_exists(dir_path=ANSWERS_BY_CATEGORY_DIR)
    remove_dir_if_exists(dir_path=ANSWERS_BY_DATE_DIR)

    write_file(
        file_path=ANSWERS_README,
        content=normalize_markdown(
            content=_format_answers_page(
                title=f"Answers ({len(answers)})",
                answers=answers,
                rel=_SECTION_REL,
                show_category_index=True,
                show_date_index=True,
                back_link=None,
            ),
        ),
    )

    categories: dict[AnswerCategory, list[AnswerInfoFull]] = {}
    for answer in answers:
        for category in answer.categories:
            if category not in categories:
                categories[category] = []
            categories[category].append(answer)

    for category, category_answers in sorted(categories.items()):
        write_file(
            file_path=ANSWERS_BY_CATEGORY_DIR / f"{category}.md",
            content=normalize_markdown(
                content=_format_answers_page(
                    title=f"Answers: `{category}` ({len(category_answers)})",
                    answers=category_answers,
                    rel=_CATEGORY_REL,
                    show_category_index=False,
                    show_date_index=False,
                    back_link="../README.md",
                ),
            ),
        )

    write_file(
        file_path=ANSWERS_BY_DATE_README,
        content=normalize_markdown(
            content=_format_answers_by_date_page(answers=answers),
        ),
    )
    remove_file_if_exists(
        file_path=overview_legacy_markdown_path(section_name=SECTION_NAME),
    )
