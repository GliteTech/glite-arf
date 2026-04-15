"""Collect normalized archive sections for overview LLM context presets."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import overload

from arf.scripts.aggregators.aggregate_metrics import MetricInfoFull
from arf.scripts.aggregators.aggregate_suggestions import (
    SUGGESTION_STATUS_ACTIVE,
    SuggestionInfoFull,
)
from arf.scripts.aggregators.aggregate_tasks import (
    TASK_STATUS_COMPLETED,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_INTERVENTION_BLOCKED,
    TASK_STATUS_NOT_STARTED,
    TaskInfoFull,
)
from arf.scripts.overview import paths as overview_paths
from arf.scripts.overview.llm_context.models import (
    ArchiveSection,
    PresetDefinition,
    ProjectSnapshot,
)
from arf.scripts.verificators.common import paths as repo_paths
from meta.asset_types.answer.aggregator import AnswerInfoFull
from meta.asset_types.dataset.aggregator import DatasetInfoFull
from meta.asset_types.library.aggregator import LibraryInfoFull
from meta.asset_types.paper.aggregator import PaperInfoFull

RESEARCH_DIR_NAME: str = "research"
RESEARCH_FILE_NAMES: list[str] = [
    "research_papers.md",
    "research_internet.md",
    "research_code.md",
]
PLANNED_TASK_STATUSES: set[str] = {
    TASK_STATUS_NOT_STARTED,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_INTERVENTION_BLOCKED,
}
PRIORITY_ORDER: dict[str, int] = {
    "high": 0,
    "medium": 1,
    "low": 2,
}
MULTISPACE_RE: re.Pattern[str] = re.compile(r"\s+")
MARKDOWN_HEADING_RE: re.Pattern[str] = re.compile(r"^#+\s*", re.MULTILINE)
HEADING_RE: re.Pattern[str] = re.compile(r"^(#{1,6})\s", re.MULTILINE)
LEADING_HEADING_RE: re.Pattern[str] = re.compile(r"^#{1,6}\s+[^\n]*\n*")
HEADING_SHIFT: int = 2
DEFAULT_EXCERPT_CHARS: int = 700
SHORT_EXCERPT_CHARS: int = 420
PAPER_EXCERPT_CHARS: int = 560
SOURCE_KIND_FILE: str = "file"
SOURCE_KIND_AGGREGATOR: str = "aggregator"
SECTION_ID_PROJECT_DESCRIPTION: str = "project-description"
SECTION_ID_COMPLETED_TASK_SUMMARIES: str = "completed-task-summaries"
SECTION_ID_PLANNED_TASKS: str = "planned-tasks"
SECTION_ID_QUESTIONS_AND_ANSWERS: str = "questions-and-answers"
SECTION_ID_OPEN_SUGGESTIONS: str = "open-suggestions"
SECTION_ID_PAPER_SUMMARIES: str = "paper-summaries"
SECTION_ID_DATASETS: str = "datasets"
SECTION_ID_LIBRARIES: str = "libraries"
SECTION_ID_METRICS: str = "metrics"


@dataclass(frozen=True, slots=True)
class RepoDocument:
    title: str
    repo_relative_path: Path
    source_kind: str
    source_name: str
    source_ids: list[str]


def build_sections(
    *,
    snapshot: ProjectSnapshot,
    preset: PresetDefinition,
) -> list[ArchiveSection]:
    sections: list[ArchiveSection] = []
    sections.append(
        ArchiveSection(
            section_id=SECTION_ID_PROJECT_DESCRIPTION,
            title="Project Description",
            source_kind=SOURCE_KIND_FILE,
            source_name="project/description.md",
            source_ids=[],
            repo_paths=[overview_paths.PROJECT_DESCRIPTION_REPO_PATH.as_posix()],
            content=snapshot.project_description.strip(),
        ),
    )
    sections.append(_collect_completed_task_summaries(tasks=snapshot.tasks))
    sections.append(
        _collect_planned_tasks(
            tasks=snapshot.tasks,
            include_long_descriptions=preset.options.include_planned_task_long_descriptions,
        ),
    )
    sections.append(
        _collect_answers(
            answers=snapshot.answers,
            include_full_answers=preset.options.include_full_answers,
        ),
    )

    if preset.options.include_suggestions:
        sections.append(
            _collect_suggestions(
                suggestions=snapshot.suggestions,
                suggestion_limit=preset.options.suggestion_limit,
            ),
        )

    if preset.options.include_papers:
        sections.append(
            _collect_papers(
                papers=snapshot.papers,
                paper_limit=preset.options.paper_limit,
            ),
        )

    if preset.options.include_datasets:
        sections.append(_collect_datasets(datasets=snapshot.datasets))

    if preset.options.include_libraries:
        sections.append(_collect_libraries(libraries=snapshot.libraries))

    if preset.options.include_metrics:
        sections.append(_collect_metrics(metrics=snapshot.metrics))

    if preset.options.include_completed_task_details:
        sections.extend(_collect_completed_task_details(tasks=snapshot.tasks))

    if preset.options.include_research_documents:
        sections.extend(_collect_research_documents(tasks=snapshot.tasks))

    return [section for section in sections if len(section.content.strip()) > 0]


def _completed_tasks(*, tasks: list[TaskInfoFull]) -> list[TaskInfoFull]:
    return sorted(
        [task for task in tasks if task.status == TASK_STATUS_COMPLETED],
        key=lambda task: task.task_index,
    )


def _planned_tasks(*, tasks: list[TaskInfoFull]) -> list[TaskInfoFull]:
    return sorted(
        [task for task in tasks if task.status in PLANNED_TASK_STATUSES],
        key=lambda task: task.task_index,
    )


def _load_repo_text(*, repo_relative_path: Path) -> str | None:
    file_path: Path = repo_paths.REPO_ROOT / repo_relative_path
    if not file_path.exists():
        return None
    try:
        return file_path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None


def _compact_excerpt(*, text: str | None, max_chars: int) -> str:
    if text is None:
        return "No summary available."
    without_headings: str = MARKDOWN_HEADING_RE.sub("", text)
    normalized: str = MULTISPACE_RE.sub(" ", without_headings).strip()
    if len(normalized) == 0:
        return "No summary available."
    if len(normalized) <= max_chars:
        return normalized

    clipped: str = normalized[: max_chars + 1]
    last_space: int = clipped.rfind(" ")
    if last_space > 0:
        clipped = clipped[:last_space]
    return clipped.rstrip(" ,;:.") + "..."


@overload
def _coalesce_nonempty_text(*values: str | None) -> str | None: ...


@overload
def _coalesce_nonempty_text(*values: str | None, default: str) -> str: ...


def _coalesce_nonempty_text(*values: str | None, default: str | None = None) -> str | None:
    for value in values:
        if value is None:
            continue
        if len(value) == 0:
            continue
        return value
    return default


def _task_effective_date(*, task: TaskInfoFull) -> str:
    if task.end_time is not None:
        return task.end_time[:10]
    if task.start_time is not None:
        return task.start_time[:10]
    if task.effective_date is not None:
        return task.effective_date
    return "unknown"


def _strip_leading_heading(*, text: str) -> str:
    """Remove the first markdown heading if it appears at the start of the text."""
    stripped: str = text.lstrip()
    if len(stripped) == 0 or stripped[0] != "#":
        return text
    return LEADING_HEADING_RE.sub("", stripped, count=1).lstrip("\n")


def _shift_headings(*, text: str) -> str:
    """Shift all markdown headings down by HEADING_SHIFT levels (clamped at H6)."""

    def _add_levels(match: re.Match[str]) -> str:
        hashes: str = match.group(1)
        new_level: int = min(len(hashes) + HEADING_SHIFT, 6)
        return "#" * new_level + " "

    return HEADING_RE.sub(_add_levels, text)


def _prepare_content(*, text: str) -> str:
    """Strip leading heading and shift remaining headings for embedding."""
    return _shift_headings(text=_strip_leading_heading(text=text))


def _collect_completed_task_summaries(*, tasks: list[TaskInfoFull]) -> ArchiveSection:
    completed: list[TaskInfoFull] = _completed_tasks(tasks=tasks)
    lines: list[str] = [
        f"Completed tasks: {len(completed)}",
        "",
    ]

    for task in completed:
        lines.extend(
            [
                f"## {task.name}",
                f"ID: {task.task_id}",
                f"Completed: {_task_effective_date(task=task)}",
                f"Short description: {task.short_description}",
                (
                    "Result summary: "
                    + _compact_excerpt(
                        text=task.results_summary,
                        max_chars=DEFAULT_EXCERPT_CHARS,
                    )
                ),
                "",
            ]
        )

    return ArchiveSection(
        section_id=SECTION_ID_COMPLETED_TASK_SUMMARIES,
        title="Completed Tasks and Results",
        source_kind=SOURCE_KIND_AGGREGATOR,
        source_name="aggregate_tasks_full",
        source_ids=[task.task_id for task in completed],
        repo_paths=[],
        content="\n".join(lines).strip(),
    )


def _collect_planned_tasks(
    *,
    tasks: list[TaskInfoFull],
    include_long_descriptions: bool,
) -> ArchiveSection:
    planned: list[TaskInfoFull] = _planned_tasks(tasks=tasks)
    lines: list[str] = [
        f"Planned or active tasks: {len(planned)}",
        "",
    ]

    for task in planned:
        lines.extend(
            [
                f"## {task.name}",
                f"ID: {task.task_id}",
                f"Status: {task.status}",
                f"Effective date: {_task_effective_date(task=task)}",
                f"Short description: {task.short_description}",
            ]
        )
        if len(task.dependencies) > 0:
            lines.append("Dependencies: " + ", ".join(task.dependencies))
        if include_long_descriptions:
            lines.append("")
            lines.append(_prepare_content(text=task.long_description.strip()))
        lines.append("")

    return ArchiveSection(
        section_id=SECTION_ID_PLANNED_TASKS,
        title="Planned Tasks",
        source_kind=SOURCE_KIND_AGGREGATOR,
        source_name="aggregate_tasks_full",
        source_ids=[task.task_id for task in planned],
        repo_paths=[],
        content="\n".join(lines).strip(),
    )


def _collect_answers(
    *,
    answers: list[AnswerInfoFull],
    include_full_answers: bool,
) -> ArchiveSection:
    ordered_answers: list[AnswerInfoFull] = sorted(
        answers,
        key=lambda answer: (answer.date_created, answer.answer_id),
    )
    lines: list[str] = [
        f"Answers: {len(ordered_answers)}",
        "",
    ]

    for answer in ordered_answers:
        lines.extend(
            [
                f"## {answer.question}",
                f"ID: {answer.answer_id}",
                f"Created by: {answer.created_by_task} on {answer.date_created}",
                f"Confidence: {answer.confidence}",
            ]
        )
        if len(answer.categories) > 0:
            lines.append("Categories: " + ", ".join(answer.categories))
        answer_text: str | None = answer.short_answer
        if include_full_answers and answer.full_answer is not None:
            answer_text = answer.full_answer
        if answer_text is None:
            answer_text = "No answer available."
        lines.append("")
        if not include_full_answers:
            lines.append(
                _compact_excerpt(
                    text=answer_text,
                    max_chars=DEFAULT_EXCERPT_CHARS,
                )
            )
        else:
            lines.append(_prepare_content(text=answer_text.strip()))
        lines.append("")

    return ArchiveSection(
        section_id=SECTION_ID_QUESTIONS_AND_ANSWERS,
        title="Questions and Answers",
        source_kind=SOURCE_KIND_AGGREGATOR,
        source_name="aggregate_answers_full",
        source_ids=[answer.answer_id for answer in ordered_answers],
        repo_paths=[],
        content="\n".join(lines).strip(),
    )


def _collect_suggestions(
    *,
    suggestions: list[SuggestionInfoFull],
    suggestion_limit: int | None,
) -> ArchiveSection:
    active_suggestions: list[SuggestionInfoFull] = sorted(
        [suggestion for suggestion in suggestions if suggestion.status == SUGGESTION_STATUS_ACTIVE],
        key=lambda suggestion: (
            PRIORITY_ORDER.get(suggestion.priority, 99),
            _coalesce_nonempty_text(suggestion.date_added, default=""),
            suggestion.id,
        ),
    )
    if suggestion_limit is not None:
        active_suggestions = active_suggestions[:suggestion_limit]

    lines: list[str] = [
        f"Open suggestions: {len(active_suggestions)}",
        "",
    ]
    for suggestion in active_suggestions:
        lines.extend(
            [
                f"## {suggestion.title}",
                f"ID: {suggestion.id}",
                f"Priority: {suggestion.priority}",
                f"Kind: {suggestion.kind}",
                f"Source task: {suggestion.source_task}",
                _compact_excerpt(
                    text=suggestion.description,
                    max_chars=DEFAULT_EXCERPT_CHARS,
                ),
                "",
            ]
        )

    return ArchiveSection(
        section_id=SECTION_ID_OPEN_SUGGESTIONS,
        title="Open Suggestions",
        source_kind=SOURCE_KIND_AGGREGATOR,
        source_name="aggregate_suggestions_full",
        source_ids=[suggestion.id for suggestion in active_suggestions],
        repo_paths=[],
        content="\n".join(lines).strip(),
    )


def _collect_papers(*, papers: list[PaperInfoFull], paper_limit: int | None) -> ArchiveSection:
    ordered_papers: list[PaperInfoFull] = sorted(
        papers,
        key=lambda paper: (
            _coalesce_nonempty_text(paper.date_added, default=""),
            paper.year,
            paper.paper_id,
        ),
        reverse=True,
    )
    if paper_limit is not None:
        ordered_papers = ordered_papers[:paper_limit]

    lines: list[str] = [
        f"Papers: {len(ordered_papers)}",
        "",
    ]
    for paper in ordered_papers:
        author_names: str = ", ".join(author.name for author in paper.authors[:4])
        lines.extend(
            [
                f"## {paper.title}",
                f"ID: {paper.paper_id}",
                f"Year: {paper.year}",
                f"Authors: {author_names}",
                f"Added by task: {paper.added_by_task}",
                _compact_excerpt(
                    text=_coalesce_nonempty_text(
                        paper.summary,
                        paper.full_summary,
                        paper.abstract,
                    ),
                    max_chars=PAPER_EXCERPT_CHARS,
                ),
                "",
            ]
        )

    return ArchiveSection(
        section_id=SECTION_ID_PAPER_SUMMARIES,
        title="Paper Summaries",
        source_kind=SOURCE_KIND_AGGREGATOR,
        source_name="aggregate_papers_full",
        source_ids=[paper.paper_id for paper in ordered_papers],
        repo_paths=[],
        content="\n".join(lines).strip(),
    )


def _collect_datasets(*, datasets: list[DatasetInfoFull]) -> ArchiveSection:
    ordered_datasets: list[DatasetInfoFull] = sorted(
        datasets,
        key=lambda dataset: (
            _coalesce_nonempty_text(dataset.date_added, default=""),
            dataset.dataset_id,
        ),
    )
    lines: list[str] = [
        f"Datasets: {len(ordered_datasets)}",
        "",
    ]
    for dataset in ordered_datasets:
        lines.extend(
            [
                f"## {dataset.name}",
                f"ID: {dataset.dataset_id}",
                f"Year: {dataset.year}",
                f"Access: {dataset.access_kind}",
                "Added by task: "
                + _coalesce_nonempty_text(dataset.added_by_task, default="unknown"),
                f"Size: {dataset.size_description}",
                _compact_excerpt(
                    text=_coalesce_nonempty_text(
                        dataset.description_summary,
                        dataset.short_description,
                    ),
                    max_chars=SHORT_EXCERPT_CHARS,
                ),
                "",
            ]
        )

    return ArchiveSection(
        section_id=SECTION_ID_DATASETS,
        title="Datasets",
        source_kind=SOURCE_KIND_AGGREGATOR,
        source_name="aggregate_datasets_full",
        source_ids=[dataset.dataset_id for dataset in ordered_datasets],
        repo_paths=[],
        content="\n".join(lines).strip(),
    )


def _collect_libraries(*, libraries: list[LibraryInfoFull]) -> ArchiveSection:
    ordered_libraries: list[LibraryInfoFull] = sorted(
        libraries,
        key=lambda library: (library.date_created, library.library_id),
    )
    lines: list[str] = [
        f"Libraries: {len(ordered_libraries)}",
        "",
    ]
    for library in ordered_libraries:
        lines.extend(
            [
                f"## {library.name}",
                f"ID: {library.library_id}",
                f"Version: {library.version}",
                f"Created by task: {library.created_by_task}",
            ]
        )
        if len(library.module_paths) > 0:
            lines.append("Module paths: " + ", ".join(library.module_paths))
        lines.append(
            _compact_excerpt(
                text=_coalesce_nonempty_text(
                    library.description_summary,
                    library.short_description,
                ),
                max_chars=SHORT_EXCERPT_CHARS,
            )
        )
        lines.append("")

    return ArchiveSection(
        section_id=SECTION_ID_LIBRARIES,
        title="Libraries",
        source_kind=SOURCE_KIND_AGGREGATOR,
        source_name="aggregate_libraries_full",
        source_ids=[library.library_id for library in ordered_libraries],
        repo_paths=[],
        content="\n".join(lines).strip(),
    )


def _collect_metrics(*, metrics: list[MetricInfoFull]) -> ArchiveSection:
    ordered_metrics: list[MetricInfoFull] = sorted(
        metrics,
        key=lambda metric: metric.metric_key,
    )
    lines: list[str] = [
        f"Metrics: {len(ordered_metrics)}",
        "",
    ]
    for metric in ordered_metrics:
        lines.extend(
            [
                f"## {metric.name}",
                f"Key: {metric.metric_key}",
                f"Unit: {metric.unit}",
                f"Value type: {metric.value_type}",
                _compact_excerpt(
                    text=metric.description,
                    max_chars=SHORT_EXCERPT_CHARS,
                ),
                "",
            ]
        )

    return ArchiveSection(
        section_id=SECTION_ID_METRICS,
        title="Metrics",
        source_kind=SOURCE_KIND_AGGREGATOR,
        source_name="aggregate_metrics_full",
        source_ids=[metric.metric_key for metric in ordered_metrics],
        repo_paths=[],
        content="\n".join(lines).strip(),
    )


def _results_detailed_document(*, task: TaskInfoFull) -> RepoDocument:
    return RepoDocument(
        title=f"{task.task_id} — {task.name} — results_detailed.md",
        repo_relative_path=overview_paths.results_detailed_repo_path(task_id=task.task_id),
        source_kind=SOURCE_KIND_FILE,
        source_name="results_detailed.md",
        source_ids=[task.task_id],
    )


def _collect_completed_task_details(*, tasks: list[TaskInfoFull]) -> list[ArchiveSection]:
    sections: list[ArchiveSection] = []
    for task in _completed_tasks(tasks=tasks):
        document: RepoDocument = _results_detailed_document(task=task)
        content: str | None = _load_repo_text(repo_relative_path=document.repo_relative_path)
        if content is None:
            continue
        sections.append(
            ArchiveSection(
                section_id=f"{task.task_id}-results-detailed",
                title=document.title,
                source_kind=document.source_kind,
                source_name=document.source_name,
                source_ids=document.source_ids,
                repo_paths=[document.repo_relative_path.as_posix()],
                content=_prepare_content(text=content),
            ),
        )
    return sections


def _collect_research_documents(*, tasks: list[TaskInfoFull]) -> list[ArchiveSection]:
    sections: list[ArchiveSection] = []
    for task in _completed_tasks(tasks=tasks):
        for file_name in RESEARCH_FILE_NAMES:
            repo_relative_path = overview_paths.task_research_repo_path(
                task_id=task.task_id,
                file_name=file_name,
            )
            content: str | None = _load_repo_text(repo_relative_path=repo_relative_path)
            if content is None:
                continue
            sections.append(
                ArchiveSection(
                    section_id=f"{task.task_id}-{file_name.removesuffix('.md')}",
                    title=f"{task.task_id} — {task.name} — {file_name}",
                    source_kind=SOURCE_KIND_FILE,
                    source_name=file_name,
                    source_ids=[task.task_id],
                    repo_paths=[repo_relative_path.as_posix()],
                    content=_prepare_content(text=content),
                ),
            )
    return sections
