"""Per-category overview pages: overview/by-category/<slug>.md.

Each page shows papers, tasks, answers, and suggestions filtered to
a single category.
"""

from pathlib import Path

from arf.scripts.aggregators.aggregate_categories import CategoryInfo
from arf.scripts.aggregators.aggregate_suggestions import SuggestionInfoFull
from arf.scripts.aggregators.aggregate_tasks import TaskInfoFull
from arf.scripts.overview.common import (
    EMPTY_MARKDOWN_VALUE,
    normalize_markdown,
    remove_dir_if_exists,
    task_name_link,
    write_file,
)
from arf.scripts.overview.format_dashboard import (
    format_answer_detail,
    format_paper_card,
    format_suggestion_detail,
)
from arf.scripts.overview.paths import BY_CATEGORY_DIR
from meta.asset_types.answer.aggregator import AnswerInfoFull
from meta.asset_types.dataset.aggregator import DatasetInfoFull
from meta.asset_types.library.aggregator import LibraryInfoFull
from meta.asset_types.model.aggregator import ModelInfoFull
from meta.asset_types.paper.aggregator import PaperInfoFull
from meta.asset_types.predictions.aggregator import PredictionsInfoFull

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REL: str = "../../"


# ---------------------------------------------------------------------------
# Input data
# ---------------------------------------------------------------------------


def _tasks_for_category(
    *,
    tasks: list[TaskInfoFull],
    papers: list[PaperInfoFull],
    category_id: str,
) -> list[TaskInfoFull]:
    task_ids_from_papers: set[str] = {
        p.added_by_task for p in papers if category_id in p.categories
    }
    direct_task_ids: set[str] = set()
    for task in tasks:
        if category_id in task.task_types:
            direct_task_ids.add(task.task_id)
    return [t for t in tasks if t.task_id in task_ids_from_papers or t.task_id in direct_task_ids]


# ---------------------------------------------------------------------------
# Section formatters
# ---------------------------------------------------------------------------


def _format_papers_section(
    *,
    papers: list[PaperInfoFull],
    category_id: str,
) -> list[str]:
    filtered: list[PaperInfoFull] = [p for p in papers if category_id in p.categories]
    filtered.sort(key=lambda p: (-p.year, p.citation_key))
    total: int = len(filtered)

    lines: list[str] = [f"## Papers ({total})", ""]
    if total == 0:
        lines.append("No papers in this category.")
        lines.append("")
        return lines

    for p in filtered:
        lines.extend(format_paper_card(paper=p, rel=_REL))
    return lines


def _format_tasks_section(
    *,
    tasks: list[TaskInfoFull],
    papers: list[PaperInfoFull],
    category_id: str,
) -> list[str]:
    filtered: list[TaskInfoFull] = _tasks_for_category(
        tasks=tasks,
        papers=papers,
        category_id=category_id,
    )
    filtered.sort(key=lambda t: t.task_index)
    total: int = len(filtered)

    lines: list[str] = [f"## Tasks ({total})", ""]
    if total == 0:
        lines.append("No tasks related to this category.")
        lines.append("")
        return lines

    lines.append("| # | Task | Status | Completed |")
    lines.append("|---|------|--------|-----------|")
    for t in filtered:
        date_str: str = EMPTY_MARKDOWN_VALUE
        if t.end_time is not None:
            date_str = t.end_time[:16].replace("T", " ")
        lines.append(
            f"| {t.task_index:04d}"
            f" | {task_name_link(task_id=t.task_id, name=t.name, rel=_REL)}"
            f" | {t.status} | {date_str} |"
        )
    lines.append("")
    return lines


def _format_answers_section(
    *,
    answers: list[AnswerInfoFull],
    category_id: str,
) -> list[str]:
    filtered: list[AnswerInfoFull] = [a for a in answers if category_id in a.categories]
    filtered.sort(key=lambda a: a.date_created, reverse=True)
    total: int = len(filtered)

    lines: list[str] = [f"## Answers ({total})", ""]
    if total == 0:
        lines.append("No answers in this category.")
        lines.append("")
        return lines

    for a in filtered:
        lines.extend(format_answer_detail(answer=a, rel=_REL))
    return lines


def _format_suggestions_section(
    *,
    suggestions: list[SuggestionInfoFull],
    task_map: dict[str, str],
    category_id: str,
) -> list[str]:
    filtered: list[SuggestionInfoFull] = [s for s in suggestions if category_id in s.categories]
    open_suggestions: list[SuggestionInfoFull] = [s for s in filtered if s.id not in task_map]
    open_suggestions.sort(
        key=lambda s: s.date_added if s.date_added is not None else "0000-00-00",
        reverse=True,
    )
    total_open: int = len(open_suggestions)
    total_closed: int = len(filtered) - total_open

    lines: list[str] = [
        f"## Suggestions ({total_open} open, {total_closed} closed)",
        "",
    ]
    if total_open == 0:
        lines.append("No open suggestions in this category.")
        lines.append("")
        return lines

    for s in open_suggestions:
        lines.extend(format_suggestion_detail(suggestion=s, rel=_REL))
    return lines


# ---------------------------------------------------------------------------
# Single category page
# ---------------------------------------------------------------------------


def _format_detail_links(
    *,
    category_id: str,
    papers: list[PaperInfoFull],
    answers: list[AnswerInfoFull],
    suggestions: list[SuggestionInfoFull],
    datasets: list[DatasetInfoFull],
    libraries: list[LibraryInfoFull],
    models: list[ModelInfoFull],
    predictions: list[PredictionsInfoFull],
) -> list[str]:
    slug: str = category_id
    link_parts: list[str] = []

    paper_count: int = len([p for p in papers if category_id in p.categories])
    if paper_count > 0:
        link_parts.append(f"[Papers ({paper_count})](../papers/by-category/{slug}.md)")

    answer_count: int = len([a for a in answers if category_id in a.categories])
    if answer_count > 0:
        link_parts.append(f"[Answers ({answer_count})](../answers/by-category/{slug}.md)")

    suggestion_count: int = len([s for s in suggestions if category_id in s.categories])
    if suggestion_count > 0:
        link_parts.append(
            f"[Suggestions ({suggestion_count})](../suggestions/by-category/{slug}.md)"
        )

    dataset_count: int = len([d for d in datasets if category_id in d.categories])
    if dataset_count > 0:
        link_parts.append(f"[Datasets ({dataset_count})](../datasets/by-category/{slug}.md)")

    library_count: int = len([lib for lib in libraries if category_id in lib.categories])
    if library_count > 0:
        link_parts.append(f"[Libraries ({library_count})](../libraries/by-category/{slug}.md)")

    model_count: int = len([m for m in models if category_id in m.categories])
    if model_count > 0:
        link_parts.append(f"[Models ({model_count})](../models/by-category/{slug}.md)")

    prediction_count: int = len([p for p in predictions if category_id in p.categories])
    if prediction_count > 0:
        link_parts.append(
            f"[Predictions ({prediction_count})](../predictions/by-category/{slug}.md)"
        )

    if len(link_parts) == 0:
        return []
    return [
        f"**Detail pages**: {' | '.join(link_parts)}",
        "",
    ]


def _format_category_page(
    *,
    category: CategoryInfo,
    tasks: list[TaskInfoFull],
    papers: list[PaperInfoFull],
    answers: list[AnswerInfoFull],
    suggestions: list[SuggestionInfoFull],
    task_map: dict[str, str],
    datasets: list[DatasetInfoFull],
    libraries: list[LibraryInfoFull],
    models: list[ModelInfoFull],
    predictions: list[PredictionsInfoFull],
) -> str:
    lines: list[str] = [
        f"# Category: {category.name}",
        "",
        category.short_description,
        "",
        "[Back to Dashboard](../README.md)",
        "",
    ]

    lines.extend(
        _format_detail_links(
            category_id=category.category_id,
            papers=papers,
            answers=answers,
            suggestions=suggestions,
            datasets=datasets,
            libraries=libraries,
            models=models,
            predictions=predictions,
        ),
    )

    lines.append("---")
    lines.append("")

    lines.extend(
        _format_papers_section(
            papers=papers,
            category_id=category.category_id,
        ),
    )
    lines.extend(
        _format_tasks_section(
            tasks=tasks,
            papers=papers,
            category_id=category.category_id,
        ),
    )
    lines.extend(
        _format_answers_section(
            answers=answers,
            category_id=category.category_id,
        ),
    )
    lines.extend(
        _format_suggestions_section(
            suggestions=suggestions,
            task_map=task_map,
            category_id=category.category_id,
        ),
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def materialize_categories(
    *,
    categories: list[CategoryInfo],
    tasks: list[TaskInfoFull],
    papers: list[PaperInfoFull],
    answers: list[AnswerInfoFull],
    suggestions: list[SuggestionInfoFull],
    suggestion_task_map: dict[str, str],
    datasets: list[DatasetInfoFull],
    libraries: list[LibraryInfoFull],
    models: list[ModelInfoFull],
    predictions: list[PredictionsInfoFull],
) -> None:
    remove_dir_if_exists(dir_path=BY_CATEGORY_DIR)

    for category in categories:
        file_path: Path = BY_CATEGORY_DIR / f"{category.category_id}.md"
        content: str = _format_category_page(
            category=category,
            tasks=tasks,
            papers=papers,
            answers=answers,
            suggestions=suggestions,
            task_map=suggestion_task_map,
            datasets=datasets,
            libraries=libraries,
            models=models,
            predictions=predictions,
        )
        write_file(
            file_path=file_path,
            content=normalize_markdown(content=content),
        )
