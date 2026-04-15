"""Aggregate all model assets in the project.

Discovers model folders under tasks/*/assets/model/ and
assets/model/, loads their details.json, and outputs structured data.
Supports filtering by category and model ID, and short/full detail
levels.

Applies shared correction overlays to model metadata, descriptions, and
file lists.

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
    DESCRIPTION_FILE_NAME,
    DOCUMENT_KIND_DESCRIPTION,
    TARGET_KIND_MODEL,
    TargetKey,
    select_canonical_document_path,
    to_repo_relative_path,
)
from arf.scripts.common.corrections import (
    CorrectionSpec,
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
    model_base_dir,
    model_details_path,
)

type ModelID = str
type RepoRelativePath = str
type TaskID = str

MODEL_COUNT_KEY: str = "model_count"
MODELS_KEY: str = "models"
FILE_DESCRIPTION_FALLBACK: str = "File"
FILE_FORMAT_UNKNOWN: str = "unknown"
UTF8_ENCODING: str = "utf-8"
NO_MODELS_FOUND: str = "No models found."
EM_DASH: str = "\u2014"

# ---------------------------------------------------------------------------
# Pydantic models for details.json (I/O boundary)
# ---------------------------------------------------------------------------


class ModelFileModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    path: str
    description: str
    format: str


class ModelDetailsModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    spec_version: str
    model_id: ModelID
    name: str
    version: str
    short_description: str
    framework: str
    base_model: str | None
    base_model_source: str | None = None
    architecture: str
    training_task_id: TaskID
    training_dataset_ids: list[str]
    hyperparameters: dict[str, Any] | None = None
    training_metrics: dict[str, Any] | None = None
    description_path: RepoRelativePath | None = None
    files: list[ModelFileModel]
    categories: list[str]
    created_by_task: TaskID
    date_created: str


# ---------------------------------------------------------------------------
# Internal data types (dataclasses for downstream use)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ModelFileInfo:
    path: RepoRelativePath
    description: str
    format: str


@dataclass(frozen=True, slots=True)
class ModelInfoShort:
    model_id: ModelID
    name: str
    version: str
    framework: str
    base_model: str | None
    description_path: RepoRelativePath | None
    categories: list[str]
    created_by_task: TaskID
    date_created: str


@dataclass(frozen=True, slots=True)
class ModelInfoFull:
    model_id: ModelID
    name: str
    version: str
    short_description: str
    framework: str
    base_model: str | None
    base_model_source: str | None
    architecture: str
    training_task_id: str
    training_dataset_ids: list[str]
    hyperparameters: dict[str, Any] | None
    training_metrics: dict[str, Any] | None
    files: list[ModelFileInfo]
    categories: list[str]
    created_by_task: TaskID
    date_created: str
    description_path: RepoRelativePath | None
    description_summary: str | None
    full_description: str | None


# ---------------------------------------------------------------------------
# Discovery and loading
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _ModelLocation:
    model_id: ModelID
    task_id: TaskID | None


def _discover_models() -> list[_ModelLocation]:
    seen: set[ModelID] = set()
    locations: list[_ModelLocation] = []

    if TASKS_DIR.exists():
        for task_dir in sorted(TASKS_DIR.iterdir()):
            if not task_dir.is_dir() or task_dir.name.startswith("."):
                continue
            base: Path = model_base_dir(task_id=task_dir.name)
            if not base.exists():
                continue
            for m_dir in sorted(base.iterdir()):
                if m_dir.is_dir() and not m_dir.name.startswith(".") and m_dir.name not in seen:
                    seen.add(m_dir.name)
                    locations.append(
                        _ModelLocation(
                            model_id=m_dir.name,
                            task_id=task_dir.name,
                        ),
                    )

    top_level: Path = model_base_dir(task_id=None)
    if top_level.exists():
        for m_dir in sorted(top_level.iterdir()):
            if m_dir.is_dir() and not m_dir.name.startswith(".") and m_dir.name not in seen:
                seen.add(m_dir.name)
                locations.append(
                    _ModelLocation(
                        model_id=m_dir.name,
                        task_id=None,
                    ),
                )

    return locations


def _load_effective_model_records() -> list[EffectiveTargetRecord]:
    correction_index: dict[TargetKey, list[CorrectionSpec]] = build_correction_index(
        correction_specs=discover_corrections(),
    )
    records: list[EffectiveTargetRecord] = []
    for location in _discover_models():
        if location.task_id is None:
            continue
        resolution = resolve_target(
            original_key=TargetKey(
                task_id=location.task_id,
                target_kind=TARGET_KIND_MODEL,
                target_id=location.model_id,
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
        content: str = file_path.read_text(encoding=UTF8_ENCODING)
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


def _load_description_summary_from_repo_relative_path(
    *,
    repo_relative_path: RepoRelativePath,
) -> str | None:
    file_path: Path = REPO_ROOT / repo_relative_path
    if not file_path.exists():
        return None
    try:
        content: str = file_path.read_text(encoding=UTF8_ENCODING)
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
        target_kind=TARGET_KIND_MODEL,
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
        content: str = file_path.read_text(encoding=UTF8_ENCODING)
    except (OSError, UnicodeDecodeError):
        return None
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(
        content=content,
    )
    if split_result is None:
        return None
    return split_result.body.strip()


def _load_full_description_from_repo_relative_path(
    *,
    repo_relative_path: RepoRelativePath,
) -> str | None:
    file_path: Path = REPO_ROOT / repo_relative_path
    if not file_path.exists():
        return None
    try:
        content: str = file_path.read_text(encoding=UTF8_ENCODING)
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
        target_kind=TARGET_KIND_MODEL,
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
    model_id: str,
    task_id: str | None,
) -> ModelDetailsModel | None:
    file_path: Path = model_details_path(
        model_id=model_id,
        task_id=task_id,
    )
    if not file_path.exists():
        return None
    try:
        raw: str = file_path.read_text(encoding=UTF8_ENCODING)
        return ModelDetailsModel.model_validate_json(raw)
    except (OSError, UnicodeDecodeError, ValidationError):
        return None


# ---------------------------------------------------------------------------
# Conversion from Pydantic model to internal dataclasses
# ---------------------------------------------------------------------------


def _to_short(*, details: ModelDetailsModel) -> ModelInfoShort:
    return ModelInfoShort(
        model_id=details.model_id,
        name=details.name,
        version=details.version,
        framework=details.framework,
        base_model=details.base_model,
        description_path=details.description_path,
        categories=details.categories,
        created_by_task=details.created_by_task,
        date_created=details.date_created,
    )


def _to_full(
    *,
    details: ModelDetailsModel,
    file_infos: list[ModelFileInfo],
    description_path: str | None,
    description_summary: str | None,
    full_description: str | None,
) -> ModelInfoFull:
    return ModelInfoFull(
        model_id=details.model_id,
        name=details.name,
        version=details.version,
        short_description=details.short_description,
        framework=details.framework,
        base_model=details.base_model,
        base_model_source=details.base_model_source,
        architecture=details.architecture,
        training_task_id=details.training_task_id,
        training_dataset_ids=details.training_dataset_ids,
        hyperparameters=details.hyperparameters,
        training_metrics=details.training_metrics,
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


def aggregate_models_short(
    *,
    filter_categories: list[str] | None = None,
    filter_ids: list[str] | None = None,
) -> list[ModelInfoShort]:
    models: list[ModelInfoShort] = []
    for record in _load_effective_model_records():
        try:
            details: ModelDetailsModel = ModelDetailsModel.model_validate(
                record.payload,
            )
        except ValidationError:
            continue
        if not matches_ids(
            asset_id=details.model_id,
            filter_ids=filter_ids,
        ):
            continue
        if not matches_categories(
            asset_categories=details.categories,
            filter_categories=filter_categories,
        ):
            continue
        models.append(_to_short(details=details))
    for loc in _discover_models():
        if loc.task_id is not None:
            continue
        if not matches_ids(
            asset_id=loc.model_id,
            filter_ids=filter_ids,
        ):
            continue
        top_level_details: ModelDetailsModel | None = _load_details(
            model_id=loc.model_id,
            task_id=loc.task_id,
        )
        if top_level_details is None:
            continue
        if not matches_categories(
            asset_categories=top_level_details.categories,
            filter_categories=filter_categories,
        ):
            continue
        models.append(_to_short(details=top_level_details))
    return models


def aggregate_models_full(
    *,
    filter_categories: list[str] | None = None,
    filter_ids: list[str] | None = None,
    include_full_description: bool = False,
) -> list[ModelInfoFull]:
    models: list[ModelInfoFull] = []
    for record in _load_effective_model_records():
        try:
            details: ModelDetailsModel = ModelDetailsModel.model_validate(
                record.payload,
            )
        except ValidationError:
            continue
        if not matches_ids(
            asset_id=details.model_id,
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
            target_kind=TARGET_KIND_MODEL,
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
        file_infos: list[ModelFileInfo] = [
            ModelFileInfo(
                path=reference.repo_relative_path,
                description=(
                    reference.description
                    if reference.description is not None and reference.description != ""
                    else FILE_DESCRIPTION_FALLBACK
                ),
                format=(
                    reference.format
                    if reference.format is not None and reference.format != ""
                    else FILE_FORMAT_UNKNOWN
                ),
            )
            for reference in record.file_references
            if (
                description_selection is None
                or reference.logical_path != description_selection.logical_path
            )
        ]
        models.append(
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
    for loc in _discover_models():
        if loc.task_id is not None:
            continue
        if not matches_ids(
            asset_id=loc.model_id,
            filter_ids=filter_ids,
        ):
            continue
        top_level_details: ModelDetailsModel | None = _load_details(
            model_id=loc.model_id,
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
            target_kind=TARGET_KIND_MODEL,
            payload=top_level_details.model_dump(mode="json"),
            document_kind=DOCUMENT_KIND_DESCRIPTION,
        )
        top_level_description_file = (
            model_base_dir(task_id=loc.task_id)
            / loc.model_id
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
        top_level_description_path: RepoRelativePath | None = None
        if top_level_description_file.exists():
            top_level_description_path = to_repo_relative_path(
                file_path=top_level_description_file,
            )
        models.append(
            _to_full(
                details=top_level_details,
                file_infos=[
                    ModelFileInfo(
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
    return models


# ---------------------------------------------------------------------------
# Output formatting -- short
# ---------------------------------------------------------------------------


def _format_short_json(*, models: list[ModelInfoShort]) -> str:
    records: list[dict[str, Any]] = [asdict(m) for m in models]
    output: dict[str, Any] = {
        MODEL_COUNT_KEY: len(records),
        MODELS_KEY: records,
    }
    return dumps(obj=output, indent=2, ensure_ascii=False)


def _format_short_markdown(
    *,
    models: list[ModelInfoShort],
) -> str:
    if len(models) == 0:
        return NO_MODELS_FOUND

    lines: list[str] = [f"# Models ({len(models)})", ""]

    lines.append(
        "| ID | Name | Version | Framework | Base Model |",
    )
    lines.append(
        "|----|------|---------|-----------|------------|",
    )
    for m in models:
        base_str: str = m.base_model if m.base_model is not None else EM_DASH
        lines.append(
            f"| `{m.model_id}` | {m.name} | {m.version} | {m.framework} | {base_str} |",
        )

    lines.append("")
    for m in models:
        categories_str: str = ", ".join(f"`{c}`" for c in m.categories)
        base_str = m.base_model if m.base_model is not None else EM_DASH
        lines.append(f"## {m.name}")
        lines.append("")
        lines.append(f"* **Model ID**: `{m.model_id}`")
        lines.append(f"* **Version**: {m.version}")
        lines.append(f"* **Framework**: {m.framework}")
        lines.append(f"* **Base model**: {base_str}")
        lines.append(f"* **Categories**: {categories_str}")
        lines.append(f"* **Created by**: `{m.created_by_task}`")
        lines.append(f"* **Date created**: {m.date_created}")
        if m.description_path is not None:
            lines.append(f"* **Documentation**: `{m.description_path}`")
        lines.append("")

    return "\n".join(lines)


def _format_ids(*, model_ids: list[ModelID]) -> str:
    return "\n".join(model_ids)


# ---------------------------------------------------------------------------
# Output formatting -- full
# ---------------------------------------------------------------------------


def _format_full_json(*, models: list[ModelInfoFull]) -> str:
    records: list[dict[str, Any]] = [asdict(m) for m in models]
    output: dict[str, Any] = {
        MODEL_COUNT_KEY: len(records),
        MODELS_KEY: records,
    }
    return dumps(obj=output, indent=2, ensure_ascii=False)


def format_full_markdown(*, models: list[ModelInfoFull]) -> str:
    if len(models) == 0:
        return NO_MODELS_FOUND

    lines: list[str] = [f"# Models ({len(models)})", ""]

    lines.append(
        "| Name | Version | Framework | Base Model | Created |",
    )
    lines.append(
        "|------|---------|-----------|------------|---------|",
    )
    for m in models:
        base_str: str = m.base_model if m.base_model is not None else EM_DASH
        lines.append(
            f"| {m.name} | {m.version} | {m.framework} | {base_str} | {m.date_created} |",
        )

    lines.append("")
    for m in models:
        base_str = m.base_model if m.base_model is not None else EM_DASH
        base_source_str: str = m.base_model_source if m.base_model_source is not None else EM_DASH
        categories_str: str = ", ".join(f"`{c}`" for c in m.categories)
        files_str: str = ", ".join(f"`{f.path}` ({f.format})" for f in m.files)
        datasets_str: str = ", ".join(f"`{d}`" for d in m.training_dataset_ids)

        lines.append(f"## {m.name}")
        lines.append("")
        lines.append(f"* **Model ID**: `{m.model_id}`")
        lines.append(f"* **Version**: {m.version}")
        lines.append(f"* **Framework**: {m.framework}")
        lines.append(f"* **Base model**: {base_str}")
        lines.append(f"* **Base model source**: {base_source_str}")
        lines.append(f"* **Architecture**: {m.architecture}")
        lines.append(f"* **Training task**: `{m.training_task_id}`")
        lines.append(f"* **Training datasets**: {datasets_str}")
        lines.append(f"* **Files**: {files_str}")
        lines.append(f"* **Categories**: {categories_str}")
        lines.append(f"* **Created by**: `{m.created_by_task}`")
        lines.append(f"* **Date created**: {m.date_created}")
        lines.append("")
        lines.append(m.short_description)
        lines.append("")
        if m.full_description is not None and len(m.full_description.strip()) > 0:
            lines.append(m.full_description)
            lines.append("")
        elif m.description_summary is not None:
            lines.append("### Summary")
            lines.append("")
            lines.append(m.description_summary)
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: ArgumentParser = ArgumentParser(
        description="Aggregate all model assets in the project",
    )
    add_output_format_arg(parser=parser)
    add_detail_level_arg(parser=parser)
    add_filter_args(parser=parser)
    parser.add_argument(
        "--include-full-description",
        action="store_true",
        default=False,
        help=("Include the full description.md content for each model (only with --detail full)"),
    )
    args: Namespace = parser.parse_args()

    output_format: str = args.format
    detail_level: str = args.detail
    filter_categories: list[str] | None = args.categories
    filter_ids: list[str] | None = args.ids
    include_full_description: bool = args.include_full_description

    if detail_level == DETAIL_LEVEL_SHORT:
        models_short: list[ModelInfoShort] = aggregate_models_short(
            filter_categories=filter_categories,
            filter_ids=filter_ids,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_short_json(models=models_short))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(
                _format_short_markdown(models=models_short),
            )
        elif output_format == OUTPUT_FORMAT_IDS:
            print(
                _format_ids(
                    model_ids=[m.model_id for m in models_short],
                ),
            )
        else:
            print(
                f"Unknown format: {output_format}",
                file=stderr,
            )
            sys_exit(1)
    elif detail_level == DETAIL_LEVEL_FULL:
        models_full: list[ModelInfoFull] = aggregate_models_full(
            filter_categories=filter_categories,
            include_full_description=include_full_description,
            filter_ids=filter_ids,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_full_json(models=models_full))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(
                format_full_markdown(models=models_full),
            )
        elif output_format == OUTPUT_FORMAT_IDS:
            print(
                _format_ids(
                    model_ids=[m.model_id for m in models_full],
                ),
            )
        else:
            print(
                f"Unknown format: {output_format}",
                file=stderr,
            )
            sys_exit(1)
    else:
        print(
            f"Unknown detail level: {detail_level}",
            file=stderr,
        )
        sys_exit(1)


if __name__ == "__main__":
    main()
