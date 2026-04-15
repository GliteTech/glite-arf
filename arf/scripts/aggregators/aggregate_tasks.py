"""Aggregate all tasks in the project.

Discovers task.json files under tasks/, loads and validates them,
and outputs structured data. Supports filtering by status, task ID,
dependency, and source suggestion.

Aggregator version: 3
"""

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from arf.scripts.aggregators.common.cli import (
    DETAIL_LEVEL_FULL,
    DETAIL_LEVEL_SHORT,
    OUTPUT_FORMAT_IDS,
    OUTPUT_FORMAT_JSON,
    OUTPUT_FORMAT_MARKDOWN,
    add_detail_level_arg,
    add_output_format_arg,
)
from arf.scripts.aggregators.common.task_dates import derive_effective_task_date
from arf.scripts.common.task_description import (
    FIELD_LONG_DESCRIPTION,
    FIELD_LONG_DESCRIPTION_FILE,
    FIELD_SPEC_VERSION,
    load_task_long_description,
)
from arf.scripts.verificators.common.json_utils import load_json_file
from arf.scripts.verificators.common.paths import (
    TASKS_DIR,
    results_summary_path,
    step_tracker_path,
    task_json_path,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

type TaskID = str
type TaskStatus = str
type TaskType = str
type SourceSuggestionID = str
type EffectiveDate = str | None

TASK_STATUS_NOT_STARTED: TaskStatus = "not_started"
TASK_STATUS_IN_PROGRESS: TaskStatus = "in_progress"
TASK_STATUS_COMPLETED: TaskStatus = "completed"
TASK_STATUS_CANCELLED: TaskStatus = "cancelled"
TASK_STATUS_PERMANENTLY_FAILED: TaskStatus = "permanently_failed"
TASK_STATUS_INTERVENTION_BLOCKED: TaskStatus = "intervention_blocked"

ALL_TASK_STATUSES: list[TaskStatus] = [
    TASK_STATUS_NOT_STARTED,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_CANCELLED,
    TASK_STATUS_PERMANENTLY_FAILED,
    TASK_STATUS_INTERVENTION_BLOCKED,
]

STEP_STATUS_COMPLETED: str = "completed"
STEP_STATUS_IN_PROGRESS: str = "in_progress"

FIELD_STATUS: str = "status"

OUTPUT_KEY_TASK_COUNT: str = "task_count"
OUTPUT_KEY_TASKS: str = "tasks"

_TASK_BRANCH_REF_PREFIX: str = "branch refs/heads/task/"

# ---------------------------------------------------------------------------
# Pydantic models (I/O boundary)
# ---------------------------------------------------------------------------


class TaskFileModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    spec_version: int | None = None
    task_id: TaskID
    task_index: int
    name: str
    short_description: str
    long_description: str | None = None
    long_description_file: str | None = None
    status: TaskStatus
    dependencies: list[TaskID]
    start_time: str | None
    end_time: str | None
    task_types: list[TaskType] = Field(default_factory=list)
    expected_assets: dict[str, int]
    source_suggestion: SourceSuggestionID | None


class TaskModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    task_id: TaskID
    task_index: int
    name: str
    short_description: str
    long_description: str
    status: TaskStatus
    dependencies: list[TaskID]
    start_time: str | None
    end_time: str | None
    task_types: list[TaskType] = Field(default_factory=list)
    expected_assets: dict[str, int]
    source_suggestion: SourceSuggestionID | None


class StepTrackerStepModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    status: str
    name: str | None = None


class StepTrackerFileModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    steps: list[StepTrackerStepModel]


# ---------------------------------------------------------------------------
# Internal data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class StepProgressSummary:
    total_steps: int
    completed_steps: int
    current_step_name: str | None


@dataclass(frozen=True, slots=True)
class TaskInfoShort:
    task_id: TaskID
    task_index: int
    name: str
    short_description: str
    status: TaskStatus
    task_types: list[TaskType]
    dependencies: list[TaskID]
    source_suggestion: SourceSuggestionID | None
    effective_date: EffectiveDate


@dataclass(frozen=True, slots=True)
class TaskInfoFull:
    task_id: TaskID
    task_index: int
    name: str
    short_description: str
    long_description: str
    status: TaskStatus
    task_types: list[TaskType]
    dependencies: list[TaskID]
    start_time: str | None
    end_time: str | None
    expected_assets: dict[str, int]
    source_suggestion: SourceSuggestionID | None
    effective_date: EffectiveDate
    results_summary: str | None
    step_progress: StepProgressSummary | None


# ---------------------------------------------------------------------------
# Discovery and loading
# ---------------------------------------------------------------------------


def _get_active_worktree_task_ids() -> set[TaskID]:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(TASKS_DIR),
            check=False,
        )
    except FileNotFoundError:
        return set()
    if result.returncode != 0:
        return set()

    active_ids: set[TaskID] = set()
    for line in result.stdout.splitlines():
        if line.startswith(_TASK_BRANCH_REF_PREFIX):
            task_id: str = line[len(_TASK_BRANCH_REF_PREFIX) :]
            active_ids.add(task_id)

    return active_ids


def _discover_task_ids() -> list[TaskID]:
    if not TASKS_DIR.exists():
        return []
    task_ids: list[TaskID] = []
    for entry in sorted(TASKS_DIR.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if not task_json_path(task_id=entry.name).is_file():
            continue
        task_ids.append(entry.name)
    return task_ids


def _load_task(
    *,
    task_id: TaskID,
    active_worktree_task_ids: set[TaskID],
) -> TaskModel | None:
    file_path: Path = task_json_path(task_id=task_id)
    raw_data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if raw_data is None:
        return None

    long_description: str | None = load_task_long_description(
        task_id=task_id,
        data=raw_data,
    )
    if long_description is None:
        return None

    normalized_data: dict[str, Any] = dict(raw_data)
    normalized_data.pop(FIELD_SPEC_VERSION, None)
    normalized_data.pop(FIELD_LONG_DESCRIPTION_FILE, None)
    normalized_data[FIELD_LONG_DESCRIPTION] = long_description

    # Safety net: if main says not_started but a worktree exists for
    # this task, override to in_progress. This handles the case where
    # the "Start task" commit was lost from main (e.g. due to a reset).
    if (
        normalized_data.get(FIELD_STATUS) == TASK_STATUS_NOT_STARTED
        and task_id in active_worktree_task_ids
    ):
        normalized_data[FIELD_STATUS] = TASK_STATUS_IN_PROGRESS

    try:
        TaskFileModel.model_validate(raw_data)
        return TaskModel.model_validate(normalized_data)
    except ValidationError:
        return None


def _load_results_summary(*, task_id: TaskID) -> str | None:
    file_path: Path = results_summary_path(task_id=task_id)
    if not file_path.exists():
        return None
    try:
        return file_path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None


def _load_step_progress(*, task_id: TaskID) -> StepProgressSummary | None:
    file_path: Path = step_tracker_path(task_id=task_id)
    if not file_path.exists():
        return None
    try:
        raw: str = file_path.read_text(encoding="utf-8")
        step_tracker: StepTrackerFileModel = StepTrackerFileModel.model_validate_json(raw)
    except (OSError, UnicodeDecodeError, ValidationError):
        return None

    total: int = len(step_tracker.steps)
    completed: int = 0
    current_name: str | None = None
    for step in step_tracker.steps:
        if step.status == STEP_STATUS_COMPLETED:
            completed += 1
        elif step.status == STEP_STATUS_IN_PROGRESS and step.name is not None:
            current_name = step.name

    return StepProgressSummary(
        total_steps=total,
        completed_steps=completed,
        current_step_name=current_name,
    )


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def _matches_statuses(
    *,
    status: TaskStatus,
    filter_statuses: list[TaskStatus] | None,
) -> bool:
    if filter_statuses is None:
        return True
    return status in filter_statuses


def _matches_ids(
    *,
    task_id: TaskID,
    filter_ids: list[TaskID] | None,
) -> bool:
    if filter_ids is None:
        return True
    return task_id in filter_ids


def _matches_has_dependency(
    *,
    dependencies: list[TaskID],
    filter_has_dependency: TaskID | None,
) -> bool:
    if filter_has_dependency is None:
        return True
    return filter_has_dependency in dependencies


def _matches_source_suggestion(
    *,
    source_suggestion: SourceSuggestionID | None,
    filter_source_suggestion: SourceSuggestionID | None,
) -> bool:
    if filter_source_suggestion is None:
        return True
    return source_suggestion == filter_source_suggestion


def _matches_task_type(
    *,
    task_types: list[TaskType],
    filter_task_type: TaskType | None,
) -> bool:
    if filter_task_type is None:
        return True
    return filter_task_type in task_types


def _matches_filters(
    *,
    task: TaskModel,
    filter_statuses: list[TaskStatus] | None,
    filter_ids: list[TaskID] | None,
    filter_has_dependency: TaskID | None,
    filter_source_suggestion: SourceSuggestionID | None,
    filter_task_type: TaskType | None,
) -> bool:
    return (
        _matches_statuses(
            status=task.status,
            filter_statuses=filter_statuses,
        )
        and _matches_ids(
            task_id=task.task_id,
            filter_ids=filter_ids,
        )
        and _matches_has_dependency(
            dependencies=task.dependencies,
            filter_has_dependency=filter_has_dependency,
        )
        and _matches_source_suggestion(
            source_suggestion=task.source_suggestion,
            filter_source_suggestion=filter_source_suggestion,
        )
        and _matches_task_type(
            task_types=list(task.task_types),
            filter_task_type=filter_task_type,
        )
    )


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------


def _to_short(*, model: TaskModel) -> TaskInfoShort:
    return TaskInfoShort(
        task_id=model.task_id,
        task_index=model.task_index,
        name=model.name,
        short_description=model.short_description,
        status=model.status,
        task_types=list(model.task_types),
        dependencies=list(model.dependencies),
        source_suggestion=model.source_suggestion,
        effective_date=derive_effective_task_date(
            start_time=model.start_time,
            end_time=model.end_time,
            task_id=model.task_id,
        ),
    )


def _to_full(
    *,
    model: TaskModel,
    results_summary: str | None,
    step_progress: StepProgressSummary | None,
) -> TaskInfoFull:
    return TaskInfoFull(
        task_id=model.task_id,
        task_index=model.task_index,
        name=model.name,
        short_description=model.short_description,
        long_description=model.long_description,
        status=model.status,
        task_types=list(model.task_types),
        dependencies=list(model.dependencies),
        start_time=model.start_time,
        end_time=model.end_time,
        expected_assets=dict(model.expected_assets),
        source_suggestion=model.source_suggestion,
        effective_date=derive_effective_task_date(
            start_time=model.start_time,
            end_time=model.end_time,
            task_id=model.task_id,
        ),
        results_summary=results_summary,
        step_progress=step_progress,
    )


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def aggregate_tasks_short(
    *,
    filter_statuses: list[TaskStatus] | None = None,
    filter_ids: list[TaskID] | None = None,
    filter_has_dependency: TaskID | None = None,
    filter_source_suggestion: SourceSuggestionID | None = None,
    filter_task_type: TaskType | None = None,
) -> list[TaskInfoShort]:
    task_ids: list[TaskID] = _discover_task_ids()
    active_wt_ids: set[TaskID] = _get_active_worktree_task_ids()
    results: list[TaskInfoShort] = []
    for task_id in task_ids:
        task: TaskModel | None = _load_task(
            task_id=task_id,
            active_worktree_task_ids=active_wt_ids,
        )
        if task is None:
            continue
        if _matches_filters(
            task=task,
            filter_statuses=filter_statuses,
            filter_ids=filter_ids,
            filter_has_dependency=filter_has_dependency,
            filter_source_suggestion=filter_source_suggestion,
            filter_task_type=filter_task_type,
        ):
            results.append(_to_short(model=task))
    return results


def aggregate_tasks_full(
    *,
    filter_statuses: list[TaskStatus] | None = None,
    filter_ids: list[TaskID] | None = None,
    filter_has_dependency: TaskID | None = None,
    filter_source_suggestion: SourceSuggestionID | None = None,
    filter_task_type: TaskType | None = None,
) -> list[TaskInfoFull]:
    task_ids: list[TaskID] = _discover_task_ids()
    active_wt_ids: set[TaskID] = _get_active_worktree_task_ids()
    results: list[TaskInfoFull] = []
    for task_id in task_ids:
        task: TaskModel | None = _load_task(
            task_id=task_id,
            active_worktree_task_ids=active_wt_ids,
        )
        if task is None:
            continue
        if not _matches_filters(
            task=task,
            filter_statuses=filter_statuses,
            filter_ids=filter_ids,
            filter_has_dependency=filter_has_dependency,
            filter_source_suggestion=filter_source_suggestion,
            filter_task_type=filter_task_type,
        ):
            continue

        summary: str | None = None
        if task.status == TASK_STATUS_COMPLETED:
            summary = _load_results_summary(task_id=task_id)

        progress: StepProgressSummary | None = _load_step_progress(
            task_id=task_id,
        )

        results.append(
            _to_full(
                model=task,
                results_summary=summary,
                step_progress=progress,
            ),
        )
    return results


# ---------------------------------------------------------------------------
# Output formatting -- short
# ---------------------------------------------------------------------------


def _format_short_json(*, tasks: list[TaskInfoShort]) -> str:
    records: list[dict[str, Any]] = [asdict(t) for t in tasks]
    output: dict[str, Any] = {
        OUTPUT_KEY_TASK_COUNT: len(records),
        OUTPUT_KEY_TASKS: records,
    }
    return json.dumps(output, indent=2, ensure_ascii=False)


def _format_short_markdown(*, tasks: list[TaskInfoShort]) -> str:
    if len(tasks) == 0:
        return "No tasks found."

    lines: list[str] = [f"# Tasks ({len(tasks)})", ""]

    lines.append(
        "| Task ID | Name | Status | Effective Date | Dependencies | Source Suggestion |",
    )
    lines.append(
        "|---------|------|--------|----------------|--------------|-------------------|",
    )
    for t in tasks:
        deps_str: str = ", ".join(f"`{d}`" for d in t.dependencies)
        if len(deps_str) == 0:
            deps_str = "\u2014"
        effective_date_str: str = t.effective_date if t.effective_date is not None else "\u2014"
        suggestion_str: str = (
            f"`{t.source_suggestion}`" if t.source_suggestion is not None else "\u2014"
        )
        lines.append(
            (
                f"| `{t.task_id}` | {t.name} | {t.status} | {effective_date_str} | "
                f"{deps_str} | {suggestion_str} |"
            ),
        )

    lines.append("")
    for t in tasks:
        deps_str = ", ".join(f"`{d}`" for d in t.dependencies)
        if len(deps_str) == 0:
            deps_str = "\u2014"
        effective_date_str = t.effective_date if t.effective_date is not None else "\u2014"
        suggestion_str = f"`{t.source_suggestion}`" if t.source_suggestion is not None else "\u2014"
        lines.append(f"## {t.task_id}: {t.name}")
        lines.append("")
        lines.append(f"* **Status**: {t.status}")
        lines.append(f"* **Effective date**: {effective_date_str}")
        lines.append(f"* **Dependencies**: {deps_str}")
        lines.append(f"* **Source suggestion**: {suggestion_str}")
        lines.append("")
        lines.append(t.short_description)
        lines.append("")

    return "\n".join(lines)


def _format_ids(*, task_ids: list[TaskID]) -> str:
    return "\n".join(task_ids)


# ---------------------------------------------------------------------------
# Output formatting -- full
# ---------------------------------------------------------------------------


def _format_full_json(*, tasks: list[TaskInfoFull]) -> str:
    records: list[dict[str, Any]] = [asdict(t) for t in tasks]
    output: dict[str, Any] = {
        OUTPUT_KEY_TASK_COUNT: len(records),
        OUTPUT_KEY_TASKS: records,
    }
    return json.dumps(output, indent=2, ensure_ascii=False)


def format_full_markdown(*, tasks: list[TaskInfoFull]) -> str:
    if len(tasks) == 0:
        return "No tasks found."

    lines: list[str] = [f"# Tasks ({len(tasks)})", ""]

    lines.append(
        "| Task ID | Name | Status | Effective Date | Dependencies | Source Suggestion |",
    )
    lines.append(
        "|---------|------|--------|----------------|--------------|-------------------|",
    )
    for t in tasks:
        deps_str: str = ", ".join(f"`{d}`" for d in t.dependencies)
        if len(deps_str) == 0:
            deps_str = "\u2014"
        effective_date_str: str = t.effective_date if t.effective_date is not None else "\u2014"
        suggestion_str: str = (
            f"`{t.source_suggestion}`" if t.source_suggestion is not None else "\u2014"
        )
        lines.append(
            (
                f"| `{t.task_id}` | {t.name} | {t.status} | {effective_date_str} | "
                f"{deps_str} | {suggestion_str} |"
            ),
        )

    lines.append("")
    for t in tasks:
        deps_str = ", ".join(f"`{d}`" for d in t.dependencies)
        if len(deps_str) == 0:
            deps_str = "\u2014"
        effective_date_str = t.effective_date if t.effective_date is not None else "\u2014"
        suggestion_str = f"`{t.source_suggestion}`" if t.source_suggestion is not None else "\u2014"
        assets_str: str = ", ".join(f"{v} {k}" for k, v in t.expected_assets.items())
        if len(assets_str) == 0:
            assets_str = "\u2014"

        lines.append(f"## {t.task_id}: {t.name}")
        lines.append("")
        lines.append(f"* **Status**: {t.status}")
        lines.append(f"* **Effective date**: {effective_date_str}")
        lines.append(f"* **Dependencies**: {deps_str}")
        lines.append(f"* **Source suggestion**: {suggestion_str}")
        lines.append(f"* **Expected assets**: {assets_str}")
        if t.start_time is not None:
            lines.append(f"* **Start time**: {t.start_time}")
        if t.end_time is not None:
            lines.append(f"* **End time**: {t.end_time}")
        if t.step_progress is not None:
            progress: StepProgressSummary = t.step_progress
            progress_str: str = f"{progress.completed_steps}/{progress.total_steps}"
            if progress.current_step_name is not None:
                progress_str += f" (current: {progress.current_step_name})"
            lines.append(f"* **Step progress**: {progress_str}")
        lines.append("")
        lines.append(t.long_description)
        lines.append("")

        if t.results_summary is not None:
            lines.append("### Results Summary")
            lines.append("")
            lines.append(t.results_summary)
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _add_task_filter_args(*, parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--status",
        nargs="+",
        default=None,
        help=(
            "Filter by task status"
            " (not_started, in_progress, completed,"
            " cancelled, permanently_failed,"
            " intervention_blocked)"
        ),
    )
    parser.add_argument(
        "--ids",
        nargs="+",
        default=None,
        help="Filter by task ID (exact match)",
    )
    parser.add_argument(
        "--has-dependency",
        default=None,
        help="Show tasks that depend on this task ID",
    )
    parser.add_argument(
        "--source-suggestion",
        default=None,
        help="Show the task implementing this suggestion ID",
    )
    parser.add_argument(
        "--task-type",
        default=None,
        help="Filter by task type slug (e.g. build-model)",
    )


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Aggregate all tasks in the project",
    )
    add_output_format_arg(parser=parser)
    add_detail_level_arg(parser=parser)
    _add_task_filter_args(parser=parser)
    args: argparse.Namespace = parser.parse_args()

    output_format: str = args.format
    detail_level: str = args.detail
    filter_statuses: list[TaskStatus] | None = args.status
    filter_ids: list[TaskID] | None = args.ids
    filter_has_dependency: TaskID | None = args.has_dependency
    filter_source_suggestion: SourceSuggestionID | None = args.source_suggestion
    filter_task_type: TaskType | None = args.task_type

    if detail_level == DETAIL_LEVEL_SHORT:
        tasks_short: list[TaskInfoShort] = aggregate_tasks_short(
            filter_statuses=filter_statuses,
            filter_ids=filter_ids,
            filter_has_dependency=filter_has_dependency,
            filter_source_suggestion=filter_source_suggestion,
            filter_task_type=filter_task_type,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_short_json(tasks=tasks_short))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(_format_short_markdown(tasks=tasks_short))
        elif output_format == OUTPUT_FORMAT_IDS:
            print(_format_ids(task_ids=[t.task_id for t in tasks_short]))
        else:
            print(f"Unknown format: {output_format}", file=sys.stderr)
            sys.exit(1)
    elif detail_level == DETAIL_LEVEL_FULL:
        tasks_full: list[TaskInfoFull] = aggregate_tasks_full(
            filter_statuses=filter_statuses,
            filter_ids=filter_ids,
            filter_has_dependency=filter_has_dependency,
            filter_source_suggestion=filter_source_suggestion,
            filter_task_type=filter_task_type,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_full_json(tasks=tasks_full))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(format_full_markdown(tasks=tasks_full))
        elif output_format == OUTPUT_FORMAT_IDS:
            print(_format_ids(task_ids=[t.task_id for t in tasks_full]))
        else:
            print(f"Unknown format: {output_format}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unknown detail level: {detail_level}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
