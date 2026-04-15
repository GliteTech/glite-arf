"""Aggregate all suggestions across tasks in the project.

Discovers suggestions.json files under tasks/*/results/, loads and
validates them, and outputs structured data. Supports filtering by
kind, priority, source task, categories, and suggestion ID.

Applies shared correction overlays to compute the effective suggestion
state, including metadata updates, deletion, and replacement.

Aggregator version: 4
"""

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from arf.scripts.aggregators.common.cli import (
    DETAIL_LEVEL_FULL,
    DETAIL_LEVEL_SHORT,
    OUTPUT_FORMAT_IDS,
    OUTPUT_FORMAT_JSON,
    OUTPUT_FORMAT_MARKDOWN,
    add_detail_level_arg,
    add_output_format_arg,
)
from arf.scripts.aggregators.common.task_dates import load_task_effective_date
from arf.scripts.common.artifacts import (
    TARGET_KIND_SUGGESTION,
    TargetKey,
)
from arf.scripts.common.corrections import (
    build_correction_index,
    dedupe_effective_records,
    discover_corrections,
    load_effective_target_record,
    resolve_target,
)
from arf.scripts.verificators.common.paths import (
    TASKS_DIR,
    suggestions_path,
    task_json_path,
)

# ---------------------------------------------------------------------------
# Pydantic models (I/O boundary)
# ---------------------------------------------------------------------------


SUGGESTION_STATUS_ACTIVE: str = "active"
SUGGESTION_STATUS_REJECTED: str = "rejected"

KEY_SUGGESTION_COUNT: str = "suggestion_count"
KEY_SUGGESTIONS: str = "suggestions"


class SuggestionModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    id: str
    title: str
    description: str
    kind: str
    priority: str
    source_task: str
    source_paper: str | None
    categories: list[str]
    status: str = SUGGESTION_STATUS_ACTIVE


class SuggestionsFileModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    spec_version: str
    suggestions: list[SuggestionModel]


class TaskSourceSuggestionModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    source_suggestion: str | None = None


# ---------------------------------------------------------------------------
# Internal data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SuggestionInfoShort:
    id: str
    title: str
    kind: str
    priority: str
    source_task: str
    source_paper: str | None
    categories: list[str]
    status: str
    date_added: str | None


@dataclass(frozen=True, slots=True)
class SuggestionInfoFull:
    id: str
    title: str
    description: str
    kind: str
    priority: str
    source_task: str
    source_paper: str | None
    categories: list[str]
    status: str
    date_added: str | None


# ---------------------------------------------------------------------------
# Discovery and loading
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _SuggestionFileLocation:
    task_id: str
    file_path: Path


def _discover_suggestion_files() -> list[_SuggestionFileLocation]:
    if not TASKS_DIR.exists():
        return []
    locations: list[_SuggestionFileLocation] = []
    for task_dir in sorted(TASKS_DIR.iterdir()):
        if not task_dir.is_dir() or task_dir.name.startswith("."):
            continue
        file_path: Path = suggestions_path(task_id=task_dir.name)
        if file_path.exists():
            locations.append(
                _SuggestionFileLocation(
                    task_id=task_dir.name,
                    file_path=file_path,
                ),
            )
    return locations


def _load_suggestions(*, file_path: Path) -> list[SuggestionModel]:
    try:
        raw: str = file_path.read_text(encoding="utf-8")
        file_data: SuggestionsFileModel = SuggestionsFileModel.model_validate_json(raw)
        return list(file_data.suggestions)
    except (OSError, UnicodeDecodeError, ValidationError):
        return []


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def _matches_kind(
    *,
    kind: str,
    filter_kinds: list[str] | None,
) -> bool:
    if filter_kinds is None:
        return True
    return kind in filter_kinds


def _matches_priority(
    *,
    priority: str,
    filter_priorities: list[str] | None,
) -> bool:
    if filter_priorities is None:
        return True
    return priority in filter_priorities


def _matches_source_task(
    *,
    source_task: str,
    filter_source_tasks: list[str] | None,
) -> bool:
    if filter_source_tasks is None:
        return True
    return source_task in filter_source_tasks


def _matches_ids(
    *,
    suggestion_id: str,
    filter_ids: list[str] | None,
) -> bool:
    if filter_ids is None:
        return True
    return suggestion_id in filter_ids


def _matches_categories(
    *,
    suggestion_categories: list[str],
    filter_categories: list[str] | None,
) -> bool:
    if filter_categories is None:
        return True
    return len(set(suggestion_categories) & set(filter_categories)) > 0


def _matches_filters(
    *,
    suggestion: SuggestionModel,
    filter_kinds: list[str] | None,
    filter_priorities: list[str] | None,
    filter_source_tasks: list[str] | None,
    filter_ids: list[str] | None,
    filter_categories: list[str] | None,
) -> bool:
    return (
        _matches_kind(kind=suggestion.kind, filter_kinds=filter_kinds)
        and _matches_priority(
            priority=suggestion.priority,
            filter_priorities=filter_priorities,
        )
        and _matches_source_task(
            source_task=suggestion.source_task,
            filter_source_tasks=filter_source_tasks,
        )
        and _matches_ids(
            suggestion_id=suggestion.id,
            filter_ids=filter_ids,
        )
        and _matches_categories(
            suggestion_categories=suggestion.categories,
            filter_categories=filter_categories,
        )
    )


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------


def _to_short(*, model: SuggestionModel, date_added: str | None) -> SuggestionInfoShort:
    return SuggestionInfoShort(
        id=model.id,
        title=model.title,
        kind=model.kind,
        priority=model.priority,
        source_task=model.source_task,
        source_paper=model.source_paper,
        categories=list(model.categories),
        status=model.status,
        date_added=date_added,
    )


def _to_full(*, model: SuggestionModel, date_added: str | None) -> SuggestionInfoFull:
    return SuggestionInfoFull(
        id=model.id,
        title=model.title,
        description=model.description,
        kind=model.kind,
        priority=model.priority,
        source_task=model.source_task,
        source_paper=model.source_paper,
        categories=list(model.categories),
        status=model.status,
        date_added=date_added,
    )


def _build_task_date_cache(*, suggestions: list[SuggestionModel]) -> dict[str, str | None]:
    source_tasks: set[str] = {suggestion.source_task for suggestion in suggestions}
    return {
        source_task: load_task_effective_date(task_id=source_task)
        for source_task in sorted(source_tasks)
    }


# ---------------------------------------------------------------------------
# Covered-suggestion collection
# ---------------------------------------------------------------------------

FIELD_SOURCE_SUGGESTION: str = "source_suggestion"


def collect_suggestion_task_map() -> dict[str, str]:
    if not TASKS_DIR.exists():
        return {}
    result: dict[str, str] = {}
    for task_dir in sorted(TASKS_DIR.iterdir()):
        if not task_dir.is_dir() or task_dir.name.startswith("."):
            continue
        file_path: Path = task_json_path(task_id=task_dir.name)
        if not file_path.exists():
            continue
        try:
            task_model: TaskSourceSuggestionModel = TaskSourceSuggestionModel.model_validate_json(
                file_path.read_text(encoding="utf-8"),
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValidationError):
            continue
        source_suggestion: str | None = task_model.source_suggestion
        if source_suggestion is not None and len(source_suggestion) > 0:
            result[source_suggestion] = task_dir.name
    return result


def collect_covered_suggestion_ids() -> set[str]:
    return set(collect_suggestion_task_map().keys())


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _SuggestionLocation:
    key: TargetKey


@dataclass(frozen=True, slots=True)
class _CoverageFilteredSuggestions:
    short: list[SuggestionInfoShort] | None
    full: list[SuggestionInfoFull] | None


def _discover_suggestion_keys() -> list[_SuggestionLocation]:
    locations: list[_SuggestionFileLocation] = _discover_suggestion_files()
    discovered: list[_SuggestionLocation] = []
    for location in locations:
        suggestions: list[SuggestionModel] = _load_suggestions(
            file_path=location.file_path,
        )
        for suggestion in suggestions:
            discovered.append(
                _SuggestionLocation(
                    key=TargetKey(
                        task_id=location.task_id,
                        target_kind=TARGET_KIND_SUGGESTION,
                        target_id=suggestion.id,
                    ),
                ),
            )
    return discovered


def _load_all_suggestions_with_corrections() -> list[SuggestionModel]:
    correction_index = build_correction_index(
        correction_specs=discover_corrections(),
    )
    effective_records: list[Any] = []
    for location in _discover_suggestion_keys():
        resolution = resolve_target(
            original_key=location.key,
            correction_index=correction_index,
        )
        if resolution.deleted:
            continue
        effective_record = load_effective_target_record(
            resolution=resolution,
            correction_index=correction_index,
        )
        if effective_record is not None:
            effective_records.append(effective_record)

    suggestions: list[SuggestionModel] = []
    for record in dedupe_effective_records(records=effective_records):
        try:
            suggestions.append(
                SuggestionModel.model_validate(record.payload),
            )
        except ValidationError:
            continue
    return suggestions


def aggregate_suggestions_short(
    *,
    filter_kinds: list[str] | None = None,
    filter_priorities: list[str] | None = None,
    filter_source_tasks: list[str] | None = None,
    filter_ids: list[str] | None = None,
    filter_categories: list[str] | None = None,
) -> list[SuggestionInfoShort]:
    suggestions: list[SuggestionModel] = _load_all_suggestions_with_corrections()
    task_date_cache: dict[str, str | None] = _build_task_date_cache(suggestions=suggestions)
    results: list[SuggestionInfoShort] = []
    for s in suggestions:
        if _matches_filters(
            suggestion=s,
            filter_kinds=filter_kinds,
            filter_priorities=filter_priorities,
            filter_source_tasks=filter_source_tasks,
            filter_ids=filter_ids,
            filter_categories=filter_categories,
        ):
            results.append(
                _to_short(
                    model=s,
                    date_added=task_date_cache[s.source_task],
                ),
            )
    return results


def aggregate_suggestions_full(
    *,
    filter_kinds: list[str] | None = None,
    filter_priorities: list[str] | None = None,
    filter_source_tasks: list[str] | None = None,
    filter_ids: list[str] | None = None,
    filter_categories: list[str] | None = None,
) -> list[SuggestionInfoFull]:
    suggestions: list[SuggestionModel] = _load_all_suggestions_with_corrections()
    task_date_cache: dict[str, str | None] = _build_task_date_cache(suggestions=suggestions)
    results: list[SuggestionInfoFull] = []
    for s in suggestions:
        if _matches_filters(
            suggestion=s,
            filter_kinds=filter_kinds,
            filter_priorities=filter_priorities,
            filter_source_tasks=filter_source_tasks,
            filter_ids=filter_ids,
            filter_categories=filter_categories,
        ):
            results.append(
                _to_full(
                    model=s,
                    date_added=task_date_cache[s.source_task],
                ),
            )
    return results


# ---------------------------------------------------------------------------
# Output formatting — short
# ---------------------------------------------------------------------------


def _format_short_json(*, suggestions: list[SuggestionInfoShort]) -> str:
    records: list[dict[str, Any]] = [asdict(s) for s in suggestions]
    output: dict[str, Any] = {
        KEY_SUGGESTION_COUNT: len(records),
        KEY_SUGGESTIONS: records,
    }
    return json.dumps(output, indent=2, ensure_ascii=False)


def _format_short_markdown(
    *,
    suggestions: list[SuggestionInfoShort],
) -> str:
    if len(suggestions) == 0:
        return "No suggestions found."

    lines: list[str] = [f"# Suggestions ({len(suggestions)})", ""]

    lines.append("| ID | Title | Kind | Priority | Status | Source Task | Date Added |")
    lines.append("|-----|-------|------|----------|--------|-------------|------------|")
    for s in suggestions:
        lines.append(
            (
                f"| {s.id} | {s.title} | {s.kind} | {s.priority} | {s.status} | "
                f"`{s.source_task}` | {s.date_added} |"
            ),
        )

    lines.append("")
    for s in suggestions:
        paper_str: str = f"`{s.source_paper}`" if s.source_paper is not None else "—"
        categories_str: str = ", ".join(f"`{c}`" for c in s.categories)
        if len(categories_str) == 0:
            categories_str = "—"
        lines.append(f"## {s.id}: {s.title}")
        lines.append("")
        lines.append(f"* **Kind**: {s.kind}")
        lines.append(f"* **Priority**: {s.priority}")
        lines.append(f"* **Status**: {s.status}")
        lines.append(f"* **Source task**: `{s.source_task}`")
        lines.append(f"* **Date added**: {s.date_added}")
        lines.append(f"* **Source paper**: {paper_str}")
        lines.append(f"* **Categories**: {categories_str}")
        lines.append("")

    return "\n".join(lines)


def _format_ids(*, suggestion_ids: list[str]) -> str:
    return "\n".join(suggestion_ids)


# ---------------------------------------------------------------------------
# Output formatting — full
# ---------------------------------------------------------------------------


def _format_full_json(*, suggestions: list[SuggestionInfoFull]) -> str:
    records: list[dict[str, Any]] = [asdict(s) for s in suggestions]
    output: dict[str, Any] = {
        KEY_SUGGESTION_COUNT: len(records),
        KEY_SUGGESTIONS: records,
    }
    return json.dumps(output, indent=2, ensure_ascii=False)


def format_full_markdown(*, suggestions: list[SuggestionInfoFull]) -> str:
    if len(suggestions) == 0:
        return "No suggestions found."

    lines: list[str] = [f"# Suggestions ({len(suggestions)})", ""]

    lines.append("| ID | Title | Kind | Priority | Status | Source Task | Date Added |")
    lines.append("|-----|-------|------|----------|--------|-------------|------------|")
    for s in suggestions:
        lines.append(
            (
                f"| {s.id} | {s.title} | {s.kind} | {s.priority} | {s.status} | "
                f"`{s.source_task}` | {s.date_added} |"
            ),
        )

    lines.append("")
    for s in suggestions:
        paper_str: str = f"`{s.source_paper}`" if s.source_paper is not None else "—"
        categories_str: str = ", ".join(f"`{c}`" for c in s.categories)
        if len(categories_str) == 0:
            categories_str = "—"
        lines.append(f"## {s.id}: {s.title}")
        lines.append("")
        lines.append(f"* **Kind**: {s.kind}")
        lines.append(f"* **Priority**: {s.priority}")
        lines.append(f"* **Status**: {s.status}")
        lines.append(f"* **Source task**: `{s.source_task}`")
        lines.append(f"* **Date added**: {s.date_added}")
        lines.append(f"* **Source paper**: {paper_str}")
        lines.append(f"* **Categories**: {categories_str}")
        lines.append("")
        lines.append(s.description)
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _add_suggestion_filter_args(*, parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--kind",
        nargs="+",
        default=None,
        help="Filter by suggestion kind (experiment, technique, evaluation, dataset, library)",
    )
    parser.add_argument(
        "--priority",
        nargs="+",
        default=None,
        help="Filter by priority (high, medium, low)",
    )
    parser.add_argument(
        "--source-task",
        nargs="+",
        default=None,
        help="Filter by source task ID",
    )
    parser.add_argument(
        "--ids",
        nargs="+",
        default=None,
        help="Filter by suggestion ID",
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        default=None,
        help="Filter by category slug (any match)",
    )
    parser.add_argument(
        "--uncovered",
        action="store_true",
        default=False,
        help="Show only actionable suggestions (not covered by a task and not rejected)",
    )
    parser.add_argument(
        "--include-rejected",
        action="store_true",
        default=False,
        help="Include rejected suggestions in output (excluded by default)",
    )


def _filter_by_coverage_and_status(
    *,
    suggestions_short: list[SuggestionInfoShort] | None = None,
    suggestions_full: list[SuggestionInfoFull] | None = None,
    uncovered_only: bool,
    include_rejected: bool,
    covered_ids: set[str] | None,
) -> _CoverageFilteredSuggestions:
    if suggestions_short is not None:
        result_short: list[SuggestionInfoShort] = list(suggestions_short)
        if not include_rejected:
            result_short = [s for s in result_short if s.status != SUGGESTION_STATUS_REJECTED]
        if uncovered_only and covered_ids is not None:
            result_short = [s for s in result_short if s.id not in covered_ids]
        return _CoverageFilteredSuggestions(short=result_short, full=None)
    if suggestions_full is not None:
        result_full: list[SuggestionInfoFull] = list(suggestions_full)
        if not include_rejected:
            result_full = [s for s in result_full if s.status != SUGGESTION_STATUS_REJECTED]
        if uncovered_only and covered_ids is not None:
            result_full = [s for s in result_full if s.id not in covered_ids]
        return _CoverageFilteredSuggestions(short=None, full=result_full)
    return _CoverageFilteredSuggestions(short=None, full=None)


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Aggregate all suggestions across tasks",
    )
    add_output_format_arg(parser=parser)
    add_detail_level_arg(parser=parser)
    _add_suggestion_filter_args(parser=parser)
    args: argparse.Namespace = parser.parse_args()

    output_format: str = args.format
    detail_level: str = args.detail
    filter_kinds: list[str] | None = args.kind
    filter_priorities: list[str] | None = args.priority
    filter_source_tasks: list[str] | None = args.source_task
    filter_ids: list[str] | None = args.ids
    filter_categories: list[str] | None = args.categories
    uncovered_only: bool = args.uncovered
    include_rejected: bool = args.include_rejected

    covered_ids: set[str] | None = None
    if uncovered_only:
        covered_ids = collect_covered_suggestion_ids()

    if detail_level == DETAIL_LEVEL_SHORT:
        suggestions_short: list[SuggestionInfoShort] = aggregate_suggestions_short(
            filter_kinds=filter_kinds,
            filter_priorities=filter_priorities,
            filter_source_tasks=filter_source_tasks,
            filter_ids=filter_ids,
            filter_categories=filter_categories,
        )
        filtered_result = _filter_by_coverage_and_status(
            suggestions_short=suggestions_short,
            uncovered_only=uncovered_only,
            include_rejected=include_rejected,
            covered_ids=covered_ids,
        )
        filtered_short: list[SuggestionInfoShort] | None = filtered_result.short
        assert filtered_short is not None, "filtered_short is not None"
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_short_json(suggestions=filtered_short))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(_format_short_markdown(suggestions=filtered_short))
        elif output_format == OUTPUT_FORMAT_IDS:
            print(
                _format_ids(
                    suggestion_ids=[s.id for s in filtered_short],
                ),
            )
        else:
            print(f"Unknown format: {output_format}", file=sys.stderr)
            sys.exit(1)
    elif detail_level == DETAIL_LEVEL_FULL:
        suggestions_full: list[SuggestionInfoFull] = aggregate_suggestions_full(
            filter_kinds=filter_kinds,
            filter_priorities=filter_priorities,
            filter_source_tasks=filter_source_tasks,
            filter_ids=filter_ids,
            filter_categories=filter_categories,
        )
        filtered_result = _filter_by_coverage_and_status(
            suggestions_full=suggestions_full,
            uncovered_only=uncovered_only,
            include_rejected=include_rejected,
            covered_ids=covered_ids,
        )
        filtered_full: list[SuggestionInfoFull] | None = filtered_result.full
        assert filtered_full is not None, "filtered_full is not None"
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_full_json(suggestions=filtered_full))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(format_full_markdown(suggestions=filtered_full))
        elif output_format == OUTPUT_FORMAT_IDS:
            print(
                _format_ids(
                    suggestion_ids=[s.id for s in filtered_full],
                ),
            )
        else:
            print(f"Unknown format: {output_format}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unknown detail level: {detail_level}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
