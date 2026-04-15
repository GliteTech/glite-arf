"""Aggregate all answer assets in the project.

Discovers answer folders under tasks/*/assets/answer/ and assets/answer/,
loads their details.json files, and outputs structured data. Supports
filtering by category and answer ID, and short/full detail levels.

Applies shared correction overlays to answer metadata and answer
documents.

Aggregator version: 2
"""

from argparse import ArgumentParser, Namespace
from dataclasses import asdict, dataclass
from json import dumps
from pathlib import Path
from sys import exit as sys_exit
from sys import stderr
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from arf.scripts.aggregators.common.cli import (
    DETAIL_LEVEL_FULL,
    DETAIL_LEVEL_SHORT,
    OUTPUT_FORMAT_IDS,
    OUTPUT_FORMAT_JSON,
    OUTPUT_FORMAT_MARKDOWN,
    add_detail_level_arg,
    add_filter_args,
    add_output_format_arg,
)
from arf.scripts.aggregators.common.filtering import (
    matches_categories,
    matches_ids,
)
from arf.scripts.common.artifacts import (
    DOCUMENT_KIND_FULL_ANSWER,
    DOCUMENT_KIND_SHORT_ANSWER,
    FULL_ANSWER_FILE_NAME,
    SHORT_ANSWER_FILE_NAME,
    TARGET_KIND_ANSWER,
    TargetKey,
    select_canonical_document_path,
    to_repo_relative_path,
)
from arf.scripts.common.corrections import (
    EffectiveTargetRecord,
    build_correction_index,
    dedupe_effective_records,
    discover_corrections,
    find_resolved_file,
    load_effective_target_record,
    resolve_target,
)
from arf.scripts.verificators.common.frontmatter import (
    FrontmatterResult,
    extract_frontmatter_and_body,
)
from arf.scripts.verificators.common.markdown_sections import (
    MarkdownSection,
    extract_sections,
)
from arf.scripts.verificators.common.paths import (
    REPO_ROOT,
    TASKS_DIR,
    answer_base_dir,
    answer_details_path,
)

type AnswerID = str
type AnswerCategory = str
type AnswerMethod = str
type ConfidenceLabel = str
type PaperID = str
type TaskID = str

ANSWER_COUNT_KEY: str = "answer_count"
ANSWERS_KEY: str = "answers"


class AnswerDetailsModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    spec_version: str
    answer_id: AnswerID
    question: str
    short_title: str
    categories: list[AnswerCategory]
    answer_methods: list[AnswerMethod]
    source_paper_ids: list[PaperID]
    source_urls: list[str]
    source_task_ids: list[TaskID]
    confidence: ConfidenceLabel
    short_answer_path: Path | None = None
    full_answer_path: Path | None = None
    created_by_task: TaskID
    date_created: str


@dataclass(frozen=True, slots=True)
class AnswerInfoShort:
    answer_id: AnswerID
    question: str
    short_title: str
    categories: list[AnswerCategory]
    answer_methods: list[AnswerMethod]
    confidence: ConfidenceLabel
    created_by_task: TaskID
    date_created: str
    short_answer: str | None


@dataclass(frozen=True, slots=True)
class AnswerInfoFull:
    answer_id: AnswerID
    question: str
    short_title: str
    categories: list[AnswerCategory]
    answer_methods: list[AnswerMethod]
    source_paper_ids: list[PaperID]
    source_urls: list[str]
    source_task_ids: list[TaskID]
    confidence: ConfidenceLabel
    created_by_task: TaskID
    date_created: str
    short_answer_path: Path | None
    full_answer_path: Path | None
    short_answer: str | None
    full_answer: str | None


@dataclass(frozen=True, slots=True)
class _AnswerLocation:
    answer_id: AnswerID
    task_id: TaskID | None


def _discover_answers() -> list[_AnswerLocation]:
    seen: set[str] = set()
    locations: list[_AnswerLocation] = []

    if TASKS_DIR.exists():
        for task_dir in sorted(TASKS_DIR.iterdir()):
            if not task_dir.is_dir() or task_dir.name.startswith("."):
                continue
            base_dir: Path = answer_base_dir(task_id=task_dir.name)
            if not base_dir.exists():
                continue
            for answer_dir in sorted(base_dir.iterdir()):
                if (
                    answer_dir.is_dir()
                    and not answer_dir.name.startswith(".")
                    and answer_dir.name not in seen
                ):
                    seen.add(answer_dir.name)
                    locations.append(
                        _AnswerLocation(
                            answer_id=answer_dir.name,
                            task_id=task_dir.name,
                        ),
                    )

    top_level: Path = answer_base_dir(task_id=None)
    if top_level.exists():
        for answer_dir in sorted(top_level.iterdir()):
            if (
                answer_dir.is_dir()
                and not answer_dir.name.startswith(".")
                and answer_dir.name not in seen
            ):
                seen.add(answer_dir.name)
                locations.append(
                    _AnswerLocation(
                        answer_id=answer_dir.name,
                        task_id=None,
                    ),
                )

    return locations


def _load_effective_answer_records() -> list[EffectiveTargetRecord]:
    correction_index = build_correction_index(
        correction_specs=discover_corrections(),
    )
    records: list[EffectiveTargetRecord] = []
    for location in _discover_answers():
        if location.task_id is None:
            continue
        resolution = resolve_target(
            original_key=TargetKey(
                task_id=location.task_id,
                target_kind=TARGET_KIND_ANSWER,
                target_id=location.answer_id,
            ),
            correction_index=correction_index,
        )
        if resolution.deleted:
            continue
        record = load_effective_target_record(
            resolution=resolution,
            correction_index=correction_index,
        )
        if record is not None:
            records.append(record)
    return dedupe_effective_records(records=records)


def _load_details(
    *,
    answer_id: str,
    task_id: str | None,
) -> AnswerDetailsModel | None:
    file_path: Path = answer_details_path(
        answer_id=answer_id,
        task_id=task_id,
    )
    if not file_path.exists():
        return None
    try:
        raw: str = file_path.read_text(encoding="utf-8")
        return AnswerDetailsModel.model_validate_json(raw)
    except (OSError, UnicodeDecodeError, ValidationError):
        return None


_SHORT_ANSWER_SECTION_HEADING: str = "Answer"


def _load_short_answer(
    *,
    file_path: Path,
) -> str | None:
    if not file_path.exists():
        return None
    try:
        content: str = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(content=content)
    if split_result is None:
        return None
    sections: list[MarkdownSection] = extract_sections(
        body=split_result.body,
        level=2,
    )
    for section in sections:
        if section.heading == _SHORT_ANSWER_SECTION_HEADING:
            return section.content.strip()
    return split_result.body.strip()


def _load_short_answer_from_repo_relative_path(*, repo_relative_path: Path) -> str | None:
    file_path: Path = REPO_ROOT / repo_relative_path
    if not file_path.exists():
        return None
    try:
        content: str = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(content=content)
    if split_result is None:
        return None
    sections: list[MarkdownSection] = extract_sections(
        body=split_result.body,
        level=2,
    )
    for section in sections:
        if section.heading == _SHORT_ANSWER_SECTION_HEADING:
            return section.content.strip()
    return split_result.body.strip()


def _load_short_answer_from_effective_record(
    *,
    record: EffectiveTargetRecord,
) -> str | None:
    selection = select_canonical_document_path(
        target_kind=TARGET_KIND_ANSWER,
        payload=record.payload,
        document_kind=DOCUMENT_KIND_SHORT_ANSWER,
    )
    if selection is None or selection.logical_path is None:
        return None
    resolved_file = find_resolved_file(record=record, logical_path=selection.logical_path)
    if resolved_file is None:
        return None
    return _load_short_answer_from_repo_relative_path(
        repo_relative_path=Path(resolved_file.repo_relative_path),
    )


def _load_full_answer(
    *,
    file_path: Path,
) -> str | None:
    if not file_path.exists():
        return None
    try:
        content: str = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(content=content)
    if split_result is None:
        return None
    return split_result.body.strip()


def _load_full_answer_from_repo_relative_path(*, repo_relative_path: Path) -> str | None:
    file_path: Path = REPO_ROOT / repo_relative_path
    if not file_path.exists():
        return None
    try:
        content: str = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(content=content)
    if split_result is None:
        return None
    return split_result.body.strip()


def _load_full_answer_from_effective_record(
    *,
    record: EffectiveTargetRecord,
) -> str | None:
    selection = select_canonical_document_path(
        target_kind=TARGET_KIND_ANSWER,
        payload=record.payload,
        document_kind=DOCUMENT_KIND_FULL_ANSWER,
    )
    if selection is None or selection.logical_path is None:
        return None
    resolved_file = find_resolved_file(record=record, logical_path=selection.logical_path)
    if resolved_file is None:
        return None
    return _load_full_answer_from_repo_relative_path(
        repo_relative_path=Path(resolved_file.repo_relative_path),
    )


def _to_short(
    *,
    details: AnswerDetailsModel,
    short_answer: str | None,
) -> AnswerInfoShort:
    return AnswerInfoShort(
        answer_id=details.answer_id,
        question=details.question,
        short_title=details.short_title,
        categories=details.categories,
        answer_methods=details.answer_methods,
        confidence=details.confidence,
        created_by_task=details.created_by_task,
        date_created=details.date_created,
        short_answer=short_answer,
    )


def _to_full(
    *,
    details: AnswerDetailsModel,
    short_answer_path: Path | None,
    full_answer_path: Path | None,
    short_answer: str | None,
    full_answer: str | None,
) -> AnswerInfoFull:
    return AnswerInfoFull(
        answer_id=details.answer_id,
        question=details.question,
        short_title=details.short_title,
        categories=details.categories,
        answer_methods=details.answer_methods,
        source_paper_ids=details.source_paper_ids,
        source_urls=details.source_urls,
        source_task_ids=details.source_task_ids,
        confidence=details.confidence,
        created_by_task=details.created_by_task,
        date_created=details.date_created,
        short_answer_path=short_answer_path,
        full_answer_path=full_answer_path,
        short_answer=short_answer,
        full_answer=full_answer,
    )


def aggregate_answers_short(
    *,
    filter_categories: list[AnswerCategory] | None = None,
    filter_ids: list[AnswerID] | None = None,
) -> list[AnswerInfoShort]:
    answers: list[AnswerInfoShort] = []
    for record in _load_effective_answer_records():
        try:
            details: AnswerDetailsModel = AnswerDetailsModel.model_validate(record.payload)
        except ValidationError:
            continue
        if not matches_ids(asset_id=details.answer_id, filter_ids=filter_ids):
            continue
        if not matches_categories(
            asset_categories=details.categories,
            filter_categories=filter_categories,
        ):
            continue
        short_answer = _load_short_answer_from_effective_record(record=record)
        answers.append(_to_short(details=details, short_answer=short_answer))
    for location in _discover_answers():
        if location.task_id is not None:
            continue
        if not matches_ids(asset_id=location.answer_id, filter_ids=filter_ids):
            continue
        top_level_details: AnswerDetailsModel | None = _load_details(
            answer_id=location.answer_id,
            task_id=location.task_id,
        )
        if top_level_details is None:
            continue
        if not matches_categories(
            asset_categories=top_level_details.categories,
            filter_categories=filter_categories,
        ):
            continue
        top_level_short_answer: str | None = _load_short_answer(
            file_path=answer_base_dir(task_id=location.task_id)
            / location.answer_id
            / (
                short_selection.logical_path
                if (
                    short_selection := select_canonical_document_path(
                        target_kind=TARGET_KIND_ANSWER,
                        payload=top_level_details.model_dump(),
                        document_kind=DOCUMENT_KIND_SHORT_ANSWER,
                    )
                )
                is not None
                and short_selection.logical_path is not None
                else SHORT_ANSWER_FILE_NAME
            ),
        )
        answers.append(
            _to_short(
                details=top_level_details,
                short_answer=top_level_short_answer,
            ),
        )
    return answers


def aggregate_answers_full(
    *,
    filter_categories: list[AnswerCategory] | None = None,
    filter_ids: list[AnswerID] | None = None,
    include_short_answer: bool = True,
    include_full_answer: bool = False,
) -> list[AnswerInfoFull]:
    answers: list[AnswerInfoFull] = []
    for record in _load_effective_answer_records():
        try:
            details: AnswerDetailsModel = AnswerDetailsModel.model_validate(record.payload)
        except ValidationError:
            continue
        if not matches_ids(asset_id=details.answer_id, filter_ids=filter_ids):
            continue
        if not matches_categories(
            asset_categories=details.categories,
            filter_categories=filter_categories,
        ):
            continue
        short_answer: str | None = None
        if include_short_answer:
            short_answer = _load_short_answer_from_effective_record(record=record)
        full_answer: str | None = None
        if include_full_answer:
            full_answer = _load_full_answer_from_effective_record(record=record)
        short_selection = select_canonical_document_path(
            target_kind=TARGET_KIND_ANSWER,
            payload=record.payload,
            document_kind=DOCUMENT_KIND_SHORT_ANSWER,
        )
        full_selection = select_canonical_document_path(
            target_kind=TARGET_KIND_ANSWER,
            payload=record.payload,
            document_kind=DOCUMENT_KIND_FULL_ANSWER,
        )
        short_reference = (
            find_resolved_file(
                record=record,
                logical_path=short_selection.logical_path,
            )
            if short_selection is not None and short_selection.logical_path is not None
            else None
        )
        full_reference = (
            find_resolved_file(
                record=record,
                logical_path=full_selection.logical_path,
            )
            if full_selection is not None and full_selection.logical_path is not None
            else None
        )
        answers.append(
            _to_full(
                details=details,
                short_answer_path=(
                    Path(short_reference.repo_relative_path)
                    if short_reference is not None
                    else None
                ),
                full_answer_path=(
                    Path(full_reference.repo_relative_path) if full_reference is not None else None
                ),
                short_answer=short_answer,
                full_answer=full_answer,
            ),
        )
    for location in _discover_answers():
        if location.task_id is not None:
            continue
        if not matches_ids(asset_id=location.answer_id, filter_ids=filter_ids):
            continue
        top_level_details: AnswerDetailsModel | None = _load_details(
            answer_id=location.answer_id,
            task_id=location.task_id,
        )
        if top_level_details is None:
            continue
        if not matches_categories(
            asset_categories=top_level_details.categories,
            filter_categories=filter_categories,
        ):
            continue
        short_selection = select_canonical_document_path(
            target_kind=TARGET_KIND_ANSWER,
            payload=top_level_details.model_dump(mode="json"),
            document_kind=DOCUMENT_KIND_SHORT_ANSWER,
        )
        full_selection = select_canonical_document_path(
            target_kind=TARGET_KIND_ANSWER,
            payload=top_level_details.model_dump(mode="json"),
            document_kind=DOCUMENT_KIND_FULL_ANSWER,
        )
        top_level_short_answer_file = (
            answer_base_dir(task_id=location.task_id)
            / location.answer_id
            / (
                short_selection.logical_path
                if short_selection is not None and short_selection.logical_path is not None
                else SHORT_ANSWER_FILE_NAME
            )
        )
        top_level_short_answer: str | None = _load_short_answer(
            file_path=top_level_short_answer_file,
        )
        if not include_short_answer:
            top_level_short_answer = None
        top_level_full_answer: str | None = None
        top_level_full_answer_file = (
            answer_base_dir(task_id=location.task_id)
            / location.answer_id
            / (
                full_selection.logical_path
                if full_selection is not None and full_selection.logical_path is not None
                else FULL_ANSWER_FILE_NAME
            )
        )
        if include_full_answer:
            top_level_full_answer = _load_full_answer(
                file_path=top_level_full_answer_file,
            )
        top_level_short_answer_path: Path | None = None
        if top_level_short_answer_file.exists():
            top_level_short_answer_path = Path(
                to_repo_relative_path(
                    file_path=top_level_short_answer_file,
                ),
            )
        top_level_full_answer_path: Path | None = None
        if top_level_full_answer_file.exists():
            top_level_full_answer_path = Path(
                to_repo_relative_path(
                    file_path=top_level_full_answer_file,
                ),
            )
        answers.append(
            _to_full(
                details=top_level_details,
                short_answer_path=top_level_short_answer_path,
                full_answer_path=top_level_full_answer_path,
                short_answer=top_level_short_answer,
                full_answer=top_level_full_answer,
            ),
        )
    return answers


def _answer_full_to_dict(*, answer: AnswerInfoFull) -> dict[str, Any]:
    record: dict[str, Any] = asdict(answer)
    record["short_answer_path"] = (
        answer.short_answer_path.as_posix() if answer.short_answer_path is not None else None
    )
    record["full_answer_path"] = (
        answer.full_answer_path.as_posix() if answer.full_answer_path is not None else None
    )
    return record


def _format_short_json(*, answers: list[AnswerInfoShort]) -> str:
    records: list[dict[str, Any]] = [asdict(answer) for answer in answers]
    output: dict[str, Any] = {
        ANSWER_COUNT_KEY: len(records),
        ANSWERS_KEY: records,
    }
    return dumps(obj=output, indent=2, ensure_ascii=False)


def _format_short_markdown(*, answers: list[AnswerInfoShort]) -> str:
    if len(answers) == 0:
        return "No answers found."

    lines: list[str] = [f"# Answers ({len(answers)})", ""]
    lines.append("| ID | Title | Confidence | Methods | Task |")
    lines.append("|----|-------|------------|---------|------|")
    for answer in answers:
        methods_str: str = ", ".join(f"`{method}`" for method in answer.answer_methods)
        lines.append(
            f"| `{answer.answer_id}` | {answer.short_title} | {answer.confidence} "
            f"| {methods_str} | `{answer.created_by_task}` |"
        )

    lines.append("")
    for answer in answers:
        categories_str: str = ", ".join(f"`{category}`" for category in answer.categories)
        methods_str = ", ".join(f"`{method}`" for method in answer.answer_methods)
        lines.append(f"## {answer.short_title}")
        lines.append("")
        lines.append(f"* **Answer ID**: `{answer.answer_id}`")
        lines.append(f"* **Question**: {answer.question}")
        lines.append(f"* **Confidence**: {answer.confidence}")
        lines.append(f"* **Methods**: {methods_str}")
        lines.append(f"* **Categories**: {categories_str}")
        lines.append(f"* **Created by**: `{answer.created_by_task}`")
        lines.append(f"* **Date created**: {answer.date_created}")
        lines.append("")
        if answer.short_answer is not None:
            lines.append(answer.short_answer)
            lines.append("")

    return "\n".join(lines)


def _format_full_json(*, answers: list[AnswerInfoFull]) -> str:
    records: list[dict[str, Any]] = [_answer_full_to_dict(answer=answer) for answer in answers]
    output: dict[str, Any] = {
        ANSWER_COUNT_KEY: len(records),
        ANSWERS_KEY: records,
    }
    return dumps(obj=output, indent=2, ensure_ascii=False)


def _format_ids(*, answer_ids: list[AnswerID]) -> str:
    return "\n".join(answer_ids)


def format_full_markdown(*, answers: list[AnswerInfoFull]) -> str:
    if len(answers) == 0:
        return "No answers found."

    lines: list[str] = [f"# Answers ({len(answers)})", ""]
    lines.append("| Title | Confidence | Methods | Task |")
    lines.append("|-------|------------|---------|------|")
    for answer in answers:
        methods_str: str = ", ".join(answer.answer_methods)
        lines.append(
            f"| {answer.short_title} | {answer.confidence} | {methods_str} "
            f"| `{answer.created_by_task}` |"
        )

    lines.append("")
    for answer in answers:
        categories_str: str = ", ".join(f"`{category}`" for category in answer.categories)
        methods_str = ", ".join(f"`{method}`" for method in answer.answer_methods)
        paper_ids_str: str = (
            ", ".join(f"`{paper_id}`" for paper_id in answer.source_paper_ids)
            if len(answer.source_paper_ids) > 0
            else "—"
        )
        source_tasks_str: str = (
            ", ".join(f"`{task_id}`" for task_id in answer.source_task_ids)
            if len(answer.source_task_ids) > 0
            else "—"
        )
        source_urls_str: str = ", ".join(answer.source_urls) if len(answer.source_urls) > 0 else "—"
        lines.append(f"## {answer.short_title}")
        lines.append("")
        lines.append(f"* **Answer ID**: `{answer.answer_id}`")
        lines.append(f"* **Question**: {answer.question}")
        lines.append(f"* **Confidence**: {answer.confidence}")
        lines.append(f"* **Methods**: {methods_str}")
        lines.append(f"* **Paper sources**: {paper_ids_str}")
        lines.append(f"* **Task sources**: {source_tasks_str}")
        lines.append(f"* **URL sources**: {source_urls_str}")
        lines.append(f"* **Categories**: {categories_str}")
        lines.append(f"* **Created by**: `{answer.created_by_task}`")
        lines.append(f"* **Date created**: {answer.date_created}")
        if answer.short_answer_path is not None:
            lines.append(f"* **Short answer file**: `{answer.short_answer_path.as_posix()}`")
        if answer.full_answer_path is not None:
            lines.append(f"* **Full answer file**: `{answer.full_answer_path.as_posix()}`")
        lines.append("")
        if answer.short_answer is not None:
            lines.append("### Short Answer")
            lines.append("")
            lines.append(answer.short_answer)
            lines.append("")
        if answer.full_answer is not None:
            lines.append(answer.full_answer)
            lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser: ArgumentParser = ArgumentParser(
        description="Aggregate all answer assets in the project",
    )
    add_output_format_arg(parser=parser)
    add_detail_level_arg(parser=parser)
    add_filter_args(parser=parser)
    parser.add_argument(
        "--include-full-answer",
        action="store_true",
        default=False,
        help="Include the full full_answer.md body for each answer (only with --detail full)",
    )
    args: Namespace = parser.parse_args()

    output_format: str = args.format
    detail_level: str = args.detail
    filter_categories: list[str] | None = args.categories
    filter_ids: list[str] | None = args.ids
    include_full_answer: bool = args.include_full_answer

    if detail_level == DETAIL_LEVEL_SHORT:
        answers_short: list[AnswerInfoShort] = aggregate_answers_short(
            filter_categories=filter_categories,
            filter_ids=filter_ids,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_short_json(answers=answers_short))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(_format_short_markdown(answers=answers_short))
        elif output_format == OUTPUT_FORMAT_IDS:
            print(_format_ids(answer_ids=[answer.answer_id for answer in answers_short]))
        else:
            print(f"Unknown format: {output_format}", file=stderr)
            sys_exit(1)
    elif detail_level == DETAIL_LEVEL_FULL:
        answers_full: list[AnswerInfoFull] = aggregate_answers_full(
            filter_categories=filter_categories,
            filter_ids=filter_ids,
            include_full_answer=include_full_answer,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_full_json(answers=answers_full))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(format_full_markdown(answers=answers_full))
        elif output_format == OUTPUT_FORMAT_IDS:
            print(_format_ids(answer_ids=[answer.answer_id for answer in answers_full]))
        else:
            print(f"Unknown format: {output_format}", file=stderr)
            sys_exit(1)
    else:
        print(f"Unknown detail level: {detail_level}", file=stderr)
        sys_exit(1)


if __name__ == "__main__":
    main()
