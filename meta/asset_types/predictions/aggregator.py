"""Aggregate all predictions assets in the project.

Discovers predictions folders under tasks/*/assets/predictions/ and
assets/predictions/, loads their details.json, and outputs structured
data. Supports filtering by category and predictions ID, and short/full
detail levels.

Applies shared correction overlays to predictions metadata,
descriptions, and file lists.

Aggregator version: 2
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
    add_filter_args,
    add_output_format_arg,
)
from arf.scripts.aggregators.common.filtering import (
    matches_categories,
    matches_ids,
)
from arf.scripts.common.artifacts import (
    DESCRIPTION_FILE_NAME,
    DOCUMENT_KIND_DESCRIPTION,
    TARGET_KIND_PREDICTIONS,
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
    predictions_base_dir,
    predictions_details_path,
)

PREDICTIONS_COUNT_KEY: str = "predictions_count"
PREDICTIONS_KEY: str = "predictions"
FILE_DESCRIPTION_FALLBACK: str = "File"
FILE_FORMAT_UNKNOWN: str = "unknown"

# ---------------------------------------------------------------------------
# Pydantic models for details.json (I/O boundary)
# ---------------------------------------------------------------------------


class PredictionFileModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    path: str
    description: str
    format: str


class PredictionsDetailsModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    spec_version: str
    predictions_id: str
    name: str
    short_description: str
    model_id: str | None
    model_description: str
    dataset_ids: list[str]
    prediction_format: str
    prediction_schema: str
    instance_count: int | None = None
    metrics_at_creation: dict[str, Any] | None = None
    description_path: str | None = None
    files: list[PredictionFileModel]
    categories: list[str]
    created_by_task: str
    date_created: str


def _coalesce_optional_string(*, value: str | None, fallback: str) -> str:
    normalized_value: str | None = value
    if normalized_value == "":
        normalized_value = None
    if normalized_value is None:
        return fallback
    return normalized_value


# ---------------------------------------------------------------------------
# Internal data types (dataclasses for downstream use)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PredictionFileInfo:
    path: str
    description: str
    format: str


@dataclass(frozen=True, slots=True)
class PredictionsInfoShort:
    predictions_id: str
    name: str
    model_id: str | None
    model_description: str
    dataset_ids: list[str]
    prediction_format: str
    instance_count: int | None
    description_path: str | None
    categories: list[str]
    created_by_task: str
    date_created: str


@dataclass(frozen=True, slots=True)
class PredictionsInfoFull:
    predictions_id: str
    name: str
    short_description: str
    model_id: str | None
    model_description: str
    dataset_ids: list[str]
    prediction_format: str
    prediction_schema: str
    instance_count: int | None
    metrics_at_creation: dict[str, Any] | None
    files: list[PredictionFileInfo]
    categories: list[str]
    created_by_task: str
    date_created: str
    description_path: str | None
    description_summary: str | None
    full_description: str | None


# ---------------------------------------------------------------------------
# Discovery and loading
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _PredictionsLocation:
    predictions_id: str
    task_id: str | None


def _discover_predictions() -> list[_PredictionsLocation]:
    seen: set[str] = set()
    locations: list[_PredictionsLocation] = []

    if TASKS_DIR.exists():
        for task_dir in sorted(TASKS_DIR.iterdir()):
            if not task_dir.is_dir() or task_dir.name.startswith("."):
                continue
            base: Path = predictions_base_dir(
                task_id=task_dir.name,
            )
            if not base.exists():
                continue
            for pr_dir in sorted(base.iterdir()):
                if pr_dir.is_dir() and not pr_dir.name.startswith(".") and pr_dir.name not in seen:
                    seen.add(pr_dir.name)
                    locations.append(
                        _PredictionsLocation(
                            predictions_id=pr_dir.name,
                            task_id=task_dir.name,
                        ),
                    )

    top_level: Path = predictions_base_dir(task_id=None)
    if top_level.exists():
        for pr_dir in sorted(top_level.iterdir()):
            if pr_dir.is_dir() and not pr_dir.name.startswith(".") and pr_dir.name not in seen:
                seen.add(pr_dir.name)
                locations.append(
                    _PredictionsLocation(
                        predictions_id=pr_dir.name,
                        task_id=None,
                    ),
                )

    return locations


def _load_effective_predictions_records() -> list[EffectiveTargetRecord]:
    correction_index = build_correction_index(
        correction_specs=discover_corrections(),
    )
    records: list[EffectiveTargetRecord] = []
    for location in _discover_predictions():
        if location.task_id is None:
            continue
        resolution = resolve_target(
            original_key=TargetKey(
                task_id=location.task_id,
                target_kind=TARGET_KIND_PREDICTIONS,
                target_id=location.predictions_id,
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


_SUMMARY_SECTION_HEADING: str = "Summary"


def _load_description_summary(
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
        if section.heading == _SUMMARY_SECTION_HEADING:
            return section.content.strip()
    return None


def _load_description_summary_from_repo_relative_path(*, repo_relative_path: str) -> str | None:
    file_path: Path = REPO_ROOT / repo_relative_path
    if not file_path.exists():
        return None
    try:
        content: str = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(
        content=content,
    )
    if split_result is None:
        return None
    sections: list[MarkdownSection] = extract_sections(
        body=split_result.body,
        level=2,
    )
    for section in sections:
        if section.heading == _SUMMARY_SECTION_HEADING:
            return section.content.strip()
    return None


def _load_description_summary_from_effective_record(
    *,
    record: EffectiveTargetRecord,
) -> str | None:
    selection = select_canonical_document_path(
        target_kind=TARGET_KIND_PREDICTIONS,
        payload=record.payload,
        document_kind=DOCUMENT_KIND_DESCRIPTION,
    )
    if selection is None or selection.logical_path is None:
        return None
    resolved_file = find_resolved_file(record=record, logical_path=selection.logical_path)
    if resolved_file is None:
        return None
    return _load_description_summary_from_repo_relative_path(
        repo_relative_path=resolved_file.repo_relative_path,
    )


def _load_full_description(
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


def _load_full_description_from_repo_relative_path(*, repo_relative_path: str) -> str | None:
    file_path: Path = REPO_ROOT / repo_relative_path
    if not file_path.exists():
        return None
    try:
        content: str = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(
        content=content,
    )
    if split_result is None:
        return None
    return split_result.body.strip()


def _load_full_description_from_effective_record(
    *,
    record: EffectiveTargetRecord,
) -> str | None:
    selection = select_canonical_document_path(
        target_kind=TARGET_KIND_PREDICTIONS,
        payload=record.payload,
        document_kind=DOCUMENT_KIND_DESCRIPTION,
    )
    if selection is None or selection.logical_path is None:
        return None
    resolved_file = find_resolved_file(record=record, logical_path=selection.logical_path)
    if resolved_file is None:
        return None
    return _load_full_description_from_repo_relative_path(
        repo_relative_path=resolved_file.repo_relative_path,
    )


def _load_details(
    *,
    predictions_id: str,
    task_id: str | None,
) -> PredictionsDetailsModel | None:
    file_path: Path = predictions_details_path(
        predictions_id=predictions_id,
        task_id=task_id,
    )
    if not file_path.exists():
        return None
    try:
        raw: str = file_path.read_text(encoding="utf-8")
        return PredictionsDetailsModel.model_validate_json(raw)
    except (OSError, UnicodeDecodeError, ValidationError):
        return None


# ---------------------------------------------------------------------------
# Conversion from Pydantic model to internal dataclasses
# ---------------------------------------------------------------------------


def _to_short(
    *,
    details: PredictionsDetailsModel,
) -> PredictionsInfoShort:
    return PredictionsInfoShort(
        predictions_id=details.predictions_id,
        name=details.name,
        model_id=details.model_id,
        model_description=details.model_description,
        dataset_ids=details.dataset_ids,
        prediction_format=details.prediction_format,
        instance_count=details.instance_count,
        description_path=details.description_path,
        categories=details.categories,
        created_by_task=details.created_by_task,
        date_created=details.date_created,
    )


def _to_full(
    *,
    details: PredictionsDetailsModel,
    file_infos: list[PredictionFileInfo],
    description_path: str | None,
    description_summary: str | None,
    full_description: str | None,
) -> PredictionsInfoFull:
    return PredictionsInfoFull(
        predictions_id=details.predictions_id,
        name=details.name,
        short_description=details.short_description,
        model_id=details.model_id,
        model_description=details.model_description,
        dataset_ids=details.dataset_ids,
        prediction_format=details.prediction_format,
        prediction_schema=details.prediction_schema,
        instance_count=details.instance_count,
        metrics_at_creation=details.metrics_at_creation,
        files=file_infos,
        categories=details.categories,
        created_by_task=details.created_by_task,
        date_created=details.date_created,
        description_path=description_path,
        description_summary=description_summary,
        full_description=full_description,
    )


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def aggregate_predictions_short(
    *,
    filter_categories: list[str] | None = None,
    filter_ids: list[str] | None = None,
) -> list[PredictionsInfoShort]:
    predictions: list[PredictionsInfoShort] = []
    for record in _load_effective_predictions_records():
        try:
            details: PredictionsDetailsModel = PredictionsDetailsModel.model_validate(
                record.payload,
            )
        except ValidationError:
            continue
        if not matches_ids(
            asset_id=details.predictions_id,
            filter_ids=filter_ids,
        ):
            continue
        if not matches_categories(
            asset_categories=details.categories,
            filter_categories=filter_categories,
        ):
            continue
        predictions.append(_to_short(details=details))
    for loc in _discover_predictions():
        if loc.task_id is not None:
            continue
        if not matches_ids(
            asset_id=loc.predictions_id,
            filter_ids=filter_ids,
        ):
            continue
        top_level_details: PredictionsDetailsModel | None = _load_details(
            predictions_id=loc.predictions_id,
            task_id=loc.task_id,
        )
        if top_level_details is None:
            continue
        if not matches_categories(
            asset_categories=top_level_details.categories,
            filter_categories=filter_categories,
        ):
            continue
        predictions.append(_to_short(details=top_level_details))
    return predictions


def aggregate_predictions_full(
    *,
    filter_categories: list[str] | None = None,
    filter_ids: list[str] | None = None,
    include_full_description: bool = False,
) -> list[PredictionsInfoFull]:
    predictions: list[PredictionsInfoFull] = []
    for record in _load_effective_predictions_records():
        try:
            details: PredictionsDetailsModel = PredictionsDetailsModel.model_validate(
                record.payload,
            )
        except ValidationError:
            continue
        if not matches_ids(
            asset_id=details.predictions_id,
            filter_ids=filter_ids,
        ):
            continue
        if not matches_categories(
            asset_categories=details.categories,
            filter_categories=filter_categories,
        ):
            continue
        description_summary: str | None = _load_description_summary_from_effective_record(
            record=record,
        )
        full_description: str | None = None
        if include_full_description:
            full_description = _load_full_description_from_effective_record(
                record=record,
            )
        description_selection = select_canonical_document_path(
            target_kind=TARGET_KIND_PREDICTIONS,
            payload=record.payload,
            document_kind=DOCUMENT_KIND_DESCRIPTION,
        )
        description_reference = (
            find_resolved_file(
                record=record,
                logical_path=description_selection.logical_path,
            )
            if description_selection is not None and description_selection.logical_path is not None
            else None
        )
        file_infos: list[PredictionFileInfo] = [
            PredictionFileInfo(
                path=reference.repo_relative_path,
                description=_coalesce_optional_string(
                    value=reference.description,
                    fallback=FILE_DESCRIPTION_FALLBACK,
                ),
                format=_coalesce_optional_string(
                    value=reference.format,
                    fallback=FILE_FORMAT_UNKNOWN,
                ),
            )
            for reference in record.file_references
            if (
                description_selection is None
                or reference.logical_path != description_selection.logical_path
            )
        ]
        predictions.append(
            _to_full(
                details=details,
                file_infos=file_infos,
                description_path=(
                    description_reference.repo_relative_path
                    if description_reference is not None
                    else None
                ),
                description_summary=description_summary,
                full_description=full_description,
            ),
        )
    for loc in _discover_predictions():
        if loc.task_id is not None:
            continue
        if not matches_ids(
            asset_id=loc.predictions_id,
            filter_ids=filter_ids,
        ):
            continue
        top_level_details: PredictionsDetailsModel | None = _load_details(
            predictions_id=loc.predictions_id,
            task_id=loc.task_id,
        )
        if top_level_details is None:
            continue
        if not matches_categories(
            asset_categories=top_level_details.categories,
            filter_categories=filter_categories,
        ):
            continue
        selection = select_canonical_document_path(
            target_kind=TARGET_KIND_PREDICTIONS,
            payload=top_level_details.model_dump(),
            document_kind=DOCUMENT_KIND_DESCRIPTION,
        )
        top_level_description_file = (
            predictions_base_dir(task_id=loc.task_id)
            / loc.predictions_id
            / (
                selection.logical_path
                if selection is not None and selection.logical_path is not None
                else DESCRIPTION_FILE_NAME
            )
        )
        top_level_description_summary = _load_description_summary(
            file_path=top_level_description_file,
        )
        top_level_full_description: str | None = None
        if include_full_description:
            top_level_full_description = _load_full_description(
                file_path=top_level_description_file,
            )
        top_level_description_path: str | None = None
        if top_level_description_file.exists():
            top_level_description_path = to_repo_relative_path(file_path=top_level_description_file)
        predictions.append(
            _to_full(
                details=top_level_details,
                file_infos=[
                    PredictionFileInfo(
                        path=item.path,
                        description=item.description,
                        format=item.format,
                    )
                    for item in top_level_details.files
                ],
                description_path=top_level_description_path,
                description_summary=top_level_description_summary,
                full_description=top_level_full_description,
            ),
        )
    return predictions


# ---------------------------------------------------------------------------
# Output formatting — short
# ---------------------------------------------------------------------------


def _format_short_json(
    *,
    predictions: list[PredictionsInfoShort],
) -> str:
    records: list[dict[str, Any]] = [asdict(d) for d in predictions]
    output: dict[str, Any] = {
        PREDICTIONS_COUNT_KEY: len(records),
        PREDICTIONS_KEY: records,
    }
    return json.dumps(obj=output, indent=2, ensure_ascii=False)


def _format_short_markdown(
    *,
    predictions: list[PredictionsInfoShort],
) -> str:
    if len(predictions) == 0:
        return "No predictions found."

    lines: list[str] = [
        f"# Predictions ({len(predictions)})",
        "",
    ]

    lines.append(
        "| ID | Name | Model | Format | Instances |",
    )
    lines.append(
        "|----|------|-------|--------|-----------|",
    )
    for p in predictions:
        model_str: str = p.model_id if p.model_id is not None else "\u2014"
        instance_str: str = str(p.instance_count) if p.instance_count is not None else "\u2014"
        lines.append(
            f"| `{p.predictions_id}` | {p.name} | {model_str}"
            f" | {p.prediction_format} | {instance_str} |",
        )

    lines.append("")
    for p in predictions:
        datasets_str: str = ", ".join(f"`{d}`" for d in p.dataset_ids)
        categories_str: str = ", ".join(f"`{c}`" for c in p.categories)
        instance_str = str(p.instance_count) if p.instance_count is not None else "\u2014"
        lines.append(f"## {p.name}")
        lines.append("")
        lines.append(f"* **Predictions ID**: `{p.predictions_id}`")
        lines.append(f"* **Model**: {p.model_description}")
        lines.append(f"* **Datasets**: {datasets_str}")
        lines.append(f"* **Format**: {p.prediction_format}")
        lines.append(f"* **Instances**: {instance_str}")
        lines.append(f"* **Categories**: {categories_str}")
        lines.append(f"* **Created by**: `{p.created_by_task}`")
        lines.append(f"* **Date created**: {p.date_created}")
        if p.description_path is not None:
            lines.append(f"* **Documentation**: `{p.description_path}`")
        lines.append("")

    return "\n".join(lines)


def _format_ids(*, predictions_ids: list[str]) -> str:
    return "\n".join(predictions_ids)


# ---------------------------------------------------------------------------
# Output formatting — full
# ---------------------------------------------------------------------------


def _format_full_json(
    *,
    predictions: list[PredictionsInfoFull],
) -> str:
    records: list[dict[str, Any]] = [asdict(d) for d in predictions]
    output: dict[str, Any] = {
        PREDICTIONS_COUNT_KEY: len(records),
        PREDICTIONS_KEY: records,
    }
    return json.dumps(obj=output, indent=2, ensure_ascii=False)


def format_full_markdown(
    *,
    predictions: list[PredictionsInfoFull],
) -> str:
    if len(predictions) == 0:
        return "No predictions found."

    lines: list[str] = [
        f"# Predictions ({len(predictions)})",
        "",
    ]

    lines.append(
        "| Name | Model | Format | Instances | Created |",
    )
    lines.append(
        "|------|-------|--------|-----------|---------|",
    )
    for p in predictions:
        model_str: str = p.model_id if p.model_id is not None else "\u2014"
        instance_str: str = str(p.instance_count) if p.instance_count is not None else "\u2014"
        lines.append(
            f"| {p.name} | {model_str}"
            f" | {p.prediction_format} | {instance_str}"
            f" | {p.date_created} |",
        )

    lines.append("")
    for p in predictions:
        datasets_str: str = ", ".join(f"`{d}`" for d in p.dataset_ids)
        categories_str: str = ", ".join(f"`{c}`" for c in p.categories)
        files_str: str = ", ".join(f"`{f.path}` ({f.format})" for f in p.files)
        model_id_str: str = f"`{p.model_id}`" if p.model_id is not None else "\u2014"
        instance_str = str(p.instance_count) if p.instance_count is not None else "\u2014"

        lines.append(f"## {p.name}")
        lines.append("")
        lines.append(f"* **Predictions ID**: `{p.predictions_id}`")
        lines.append(f"* **Model ID**: {model_id_str}")
        lines.append(f"* **Model**: {p.model_description}")
        lines.append(f"* **Datasets**: {datasets_str}")
        lines.append(f"* **Format**: {p.prediction_format}")
        lines.append(f"* **Instances**: {instance_str}")
        lines.append(f"* **Files**: {files_str}")
        lines.append(f"* **Categories**: {categories_str}")
        lines.append(f"* **Created by**: `{p.created_by_task}`")
        lines.append(f"* **Date created**: {p.date_created}")
        lines.append("")
        lines.append(p.short_description)
        lines.append("")

        if p.metrics_at_creation is not None:
            lines.append("### Metrics at Creation")
            lines.append("")
            for metric_name, metric_value in p.metrics_at_creation.items():
                lines.append(f"* **{metric_name}**: {metric_value}")
            lines.append("")

        if p.full_description is not None:
            lines.append(p.full_description)
            lines.append("")
        elif p.description_summary is not None:
            lines.append("### Summary")
            lines.append("")
            lines.append(p.description_summary)
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Aggregate all predictions assets in the project",
    )
    add_output_format_arg(parser=parser)
    add_detail_level_arg(parser=parser)
    add_filter_args(parser=parser)
    parser.add_argument(
        "--include-full-description",
        action="store_true",
        default=False,
        help=(
            "Include the full description.md content for each "
            "predictions asset (only with --detail full)"
        ),
    )
    args: argparse.Namespace = parser.parse_args()

    output_format: str = args.format
    detail_level: str = args.detail
    filter_categories: list[str] | None = args.categories
    filter_ids: list[str] | None = args.ids
    include_full_description: bool = args.include_full_description

    if detail_level == DETAIL_LEVEL_SHORT:
        predictions_short: list[PredictionsInfoShort] = aggregate_predictions_short(
            filter_categories=filter_categories,
            filter_ids=filter_ids,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(
                _format_short_json(predictions=predictions_short),
            )
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(
                _format_short_markdown(
                    predictions=predictions_short,
                ),
            )
        elif output_format == OUTPUT_FORMAT_IDS:
            print(
                _format_ids(
                    predictions_ids=[p.predictions_id for p in predictions_short],
                ),
            )
        else:
            print(
                f"Unknown format: {output_format}",
                file=sys.stderr,
            )
            sys.exit(1)
    elif detail_level == DETAIL_LEVEL_FULL:
        predictions_full: list[PredictionsInfoFull] = aggregate_predictions_full(
            filter_categories=filter_categories,
            include_full_description=include_full_description,
            filter_ids=filter_ids,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(
                _format_full_json(predictions=predictions_full),
            )
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(
                format_full_markdown(
                    predictions=predictions_full,
                ),
            )
        elif output_format == OUTPUT_FORMAT_IDS:
            print(
                _format_ids(
                    predictions_ids=[p.predictions_id for p in predictions_full],
                ),
            )
        else:
            print(
                f"Unknown format: {output_format}",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        print(
            f"Unknown detail level: {detail_level}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
