"""Aggregate all dataset assets in the project.

Discovers dataset folders under tasks/*/assets/dataset/ and
assets/dataset/, loads their details.json, and outputs structured data.
Supports filtering by category and dataset ID, and short/full detail
levels.

The fields `added_by_task` and `date_added` are not stored in
details.json — they are derived from the task folder path and
tasks/<task_id>/task.json respectively.

Applies shared correction overlays to dataset metadata, descriptions,
and file lists.

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
from arf.scripts.aggregators.common.task_dates import load_task_effective_date
from arf.scripts.common.artifacts import (
    DESCRIPTION_FILE_NAME,
    DOCUMENT_KIND_DESCRIPTION,
    TARGET_KIND_DATASET,
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
    dataset_base_dir,
    dataset_details_path,
)

# ---------------------------------------------------------------------------
# Pydantic models for details.json (I/O boundary)
# ---------------------------------------------------------------------------


DATASET_COUNT_KEY: str = "dataset_count"
DATASETS_KEY: str = "datasets"
UNKNOWN_LABEL: str = "unknown"
FILE_DESCRIPTION_FALLBACK: str = "File"
FILE_FORMAT_UNKNOWN: str = "unknown"


class AuthorModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    name: str
    country: str | None = None
    institution: str | None = None
    orcid: str | None = None


class InstitutionModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    name: str
    country: str


class DatasetFileModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    path: str
    description: str
    format: str


class DatasetDetailsModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    spec_version: str
    dataset_id: str
    name: str
    version: str | None
    short_description: str
    source_paper_id: str | None
    url: str | None
    download_url: str | None = None
    year: int
    date_published: str | None = None
    authors: list[AuthorModel]
    institutions: list[InstitutionModel]
    license: str | None
    access_kind: str
    size_description: str
    description_path: str | None = None
    files: list[DatasetFileModel]
    categories: list[str]


# ---------------------------------------------------------------------------
# Internal data types (dataclasses for downstream use)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AuthorInfo:
    name: str
    country: str | None
    institution: str | None


@dataclass(frozen=True, slots=True)
class InstitutionInfo:
    name: str
    country: str


@dataclass(frozen=True, slots=True)
class DatasetFileInfo:
    path: str
    description: str
    format: str


@dataclass(frozen=True, slots=True)
class DatasetInfoShort:
    dataset_id: str
    name: str
    version: str | None
    year: int
    authors: list[str]
    access_kind: str
    categories: list[str]
    size_description: str
    added_by_task: str | None
    date_added: str | None


@dataclass(frozen=True, slots=True)
class DatasetInfoFull:
    dataset_id: str
    name: str
    version: str | None
    short_description: str
    source_paper_id: str | None
    url: str | None
    download_url: str | None
    date_published: str | None
    year: int
    authors: list[AuthorInfo]
    institutions: list[InstitutionInfo]
    license: str | None
    access_kind: str
    size_description: str
    files: list[DatasetFileInfo]
    categories: list[str]
    added_by_task: str | None
    date_added: str | None
    description_path: str | None
    description_summary: str | None
    full_description: str | None


# ---------------------------------------------------------------------------
# Discovery and loading
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _DatasetLocation:
    dataset_id: str
    task_id: str | None


def _discover_datasets() -> list[_DatasetLocation]:
    seen: set[str] = set()
    locations: list[_DatasetLocation] = []

    if TASKS_DIR.exists():
        for task_dir in sorted(TASKS_DIR.iterdir()):
            if not task_dir.is_dir() or task_dir.name.startswith("."):
                continue
            base: Path = dataset_base_dir(task_id=task_dir.name)
            if not base.exists():
                continue
            for ds_dir in sorted(base.iterdir()):
                if ds_dir.is_dir() and not ds_dir.name.startswith(".") and ds_dir.name not in seen:
                    seen.add(ds_dir.name)
                    locations.append(
                        _DatasetLocation(
                            dataset_id=ds_dir.name,
                            task_id=task_dir.name,
                        ),
                    )

    top_level: Path = dataset_base_dir(task_id=None)
    if top_level.exists():
        for ds_dir in sorted(top_level.iterdir()):
            if ds_dir.is_dir() and not ds_dir.name.startswith(".") and ds_dir.name not in seen:
                seen.add(ds_dir.name)
                locations.append(
                    _DatasetLocation(
                        dataset_id=ds_dir.name,
                        task_id=None,
                    ),
                )

    return locations


def _load_effective_dataset_records() -> list[EffectiveTargetRecord]:
    correction_index = build_correction_index(
        correction_specs=discover_corrections(),
    )
    records: list[EffectiveTargetRecord] = []
    for location in _discover_datasets():
        if location.task_id is None:
            continue
        resolution = resolve_target(
            original_key=TargetKey(
                task_id=location.task_id,
                target_kind=TARGET_KIND_DATASET,
                target_id=location.dataset_id,
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


def _derive_date_added(*, task_id: str | None) -> str | None:
    return load_task_effective_date(task_id=task_id)


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


def _load_description_summary_from_effective_record(
    *,
    record: EffectiveTargetRecord,
) -> str | None:
    selection = select_canonical_document_path(
        target_kind=TARGET_KIND_DATASET,
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
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(content=content)
    if split_result is None:
        return None
    return split_result.body.strip()


def _load_full_description_from_effective_record(
    *,
    record: EffectiveTargetRecord,
) -> str | None:
    selection = select_canonical_document_path(
        target_kind=TARGET_KIND_DATASET,
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
    dataset_id: str,
    task_id: str | None,
) -> DatasetDetailsModel | None:
    file_path: Path = dataset_details_path(
        dataset_id=dataset_id,
        task_id=task_id,
    )
    if not file_path.exists():
        return None
    try:
        raw: str = file_path.read_text(encoding="utf-8")
        return DatasetDetailsModel.model_validate_json(raw)
    except (OSError, UnicodeDecodeError, ValidationError):
        return None


# ---------------------------------------------------------------------------
# Conversion from Pydantic model to internal dataclasses
# ---------------------------------------------------------------------------


def _to_short(
    *,
    details: DatasetDetailsModel,
    added_by_task: str | None,
    date_added: str | None,
) -> DatasetInfoShort:
    return DatasetInfoShort(
        dataset_id=details.dataset_id,
        name=details.name,
        version=details.version,
        year=details.year,
        authors=[a.name for a in details.authors],
        access_kind=details.access_kind,
        categories=details.categories,
        size_description=details.size_description,
        added_by_task=added_by_task,
        date_added=date_added,
    )


def _to_full(
    *,
    details: DatasetDetailsModel,
    added_by_task: str | None,
    date_added: str | None,
    file_infos: list[DatasetFileInfo],
    description_path: str | None,
    description_summary: str | None,
    full_description: str | None,
) -> DatasetInfoFull:
    return DatasetInfoFull(
        dataset_id=details.dataset_id,
        name=details.name,
        version=details.version,
        short_description=details.short_description,
        source_paper_id=details.source_paper_id,
        url=details.url,
        download_url=details.download_url,
        date_published=details.date_published,
        year=details.year,
        authors=[
            AuthorInfo(
                name=a.name,
                country=a.country,
                institution=a.institution,
            )
            for a in details.authors
        ],
        institutions=[
            InstitutionInfo(name=i.name, country=i.country) for i in details.institutions
        ],
        license=details.license,
        access_kind=details.access_kind,
        size_description=details.size_description,
        files=file_infos,
        categories=details.categories,
        added_by_task=added_by_task,
        date_added=date_added,
        description_path=description_path,
        description_summary=description_summary,
        full_description=full_description,
    )


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def aggregate_datasets_short(
    *,
    filter_categories: list[str] | None = None,
    filter_ids: list[str] | None = None,
) -> list[DatasetInfoShort]:
    datasets: list[DatasetInfoShort] = []
    for record in _load_effective_dataset_records():
        try:
            details: DatasetDetailsModel = DatasetDetailsModel.model_validate(record.payload)
        except ValidationError:
            continue
        if not matches_ids(
            asset_id=details.dataset_id,
            filter_ids=filter_ids,
        ):
            continue
        if not matches_categories(
            asset_categories=details.categories,
            filter_categories=filter_categories,
        ):
            continue
        added_by_task: str = record.effective_key.task_id
        date_added: str | None = _derive_date_added(task_id=record.effective_key.task_id)
        datasets.append(
            _to_short(
                details=details,
                added_by_task=added_by_task,
                date_added=date_added,
            ),
        )
    for loc in _discover_datasets():
        if loc.task_id is not None:
            continue
        if not matches_ids(
            asset_id=loc.dataset_id,
            filter_ids=filter_ids,
        ):
            continue
        top_level_details: DatasetDetailsModel | None = _load_details(
            dataset_id=loc.dataset_id,
            task_id=loc.task_id,
        )
        if top_level_details is None:
            continue
        if not matches_categories(
            asset_categories=top_level_details.categories,
            filter_categories=filter_categories,
        ):
            continue
        datasets.append(
            _to_short(
                details=top_level_details,
                added_by_task=None,
                date_added=_derive_date_added(task_id=loc.task_id),
            ),
        )
    return datasets


def aggregate_datasets_full(
    *,
    filter_categories: list[str] | None = None,
    filter_ids: list[str] | None = None,
    include_full_description: bool = False,
) -> list[DatasetInfoFull]:
    datasets: list[DatasetInfoFull] = []
    for record in _load_effective_dataset_records():
        try:
            details: DatasetDetailsModel = DatasetDetailsModel.model_validate(record.payload)
        except ValidationError:
            continue
        if not matches_ids(
            asset_id=details.dataset_id,
            filter_ids=filter_ids,
        ):
            continue
        if not matches_categories(
            asset_categories=details.categories,
            filter_categories=filter_categories,
        ):
            continue
        added_by_task: str = record.effective_key.task_id
        date_added: str | None = _derive_date_added(task_id=record.effective_key.task_id)
        description_summary: str | None = _load_description_summary_from_effective_record(
            record=record,
        )
        full_description: str | None = None
        if include_full_description:
            full_description = _load_full_description_from_effective_record(record=record)
        description_selection = select_canonical_document_path(
            target_kind=TARGET_KIND_DATASET,
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
        description_path: str | None = None
        if description_reference is not None:
            description_path = description_reference.repo_relative_path
        file_infos: list[DatasetFileInfo] = [
            DatasetFileInfo(
                path=reference.repo_relative_path,
                description=(
                    reference.description
                    if reference.description is not None
                    else FILE_DESCRIPTION_FALLBACK
                ),
                format=reference.format if reference.format is not None else FILE_FORMAT_UNKNOWN,
            )
            for reference in record.file_references
            if (
                description_selection is None
                or reference.logical_path != description_selection.logical_path
            )
        ]
        datasets.append(
            _to_full(
                details=details,
                added_by_task=added_by_task,
                date_added=date_added,
                file_infos=file_infos,
                description_path=description_path,
                description_summary=description_summary,
                full_description=full_description,
            ),
        )
    for loc in _discover_datasets():
        if loc.task_id is not None:
            continue
        if not matches_ids(
            asset_id=loc.dataset_id,
            filter_ids=filter_ids,
        ):
            continue
        top_level_details: DatasetDetailsModel | None = _load_details(
            dataset_id=loc.dataset_id,
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
            target_kind=TARGET_KIND_DATASET,
            payload=top_level_details.model_dump(),
            document_kind=DOCUMENT_KIND_DESCRIPTION,
        )
        top_level_description_file = (
            dataset_base_dir(task_id=loc.task_id)
            / loc.dataset_id
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
        datasets.append(
            _to_full(
                details=top_level_details,
                added_by_task=None,
                date_added=_derive_date_added(task_id=loc.task_id),
                file_infos=[
                    DatasetFileInfo(
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
    return datasets


# ---------------------------------------------------------------------------
# Output formatting — short
# ---------------------------------------------------------------------------


def _format_short_json(*, datasets: list[DatasetInfoShort]) -> str:
    records: list[dict[str, Any]] = [asdict(d) for d in datasets]
    output: dict[str, Any] = {
        DATASET_COUNT_KEY: len(records),
        DATASETS_KEY: records,
    }
    return json.dumps(obj=output, indent=2, ensure_ascii=False)


def _format_short_markdown(
    *,
    datasets: list[DatasetInfoShort],
) -> str:
    if len(datasets) == 0:
        return "No datasets found."

    lines: list[str] = [f"# Datasets ({len(datasets)})", ""]

    lines.append("| ID | Name | Version | Year | Access | Size |")
    lines.append("|----|------|---------|------|--------|------|")
    for d in datasets:
        version_str: str = d.version if d.version is not None else "—"
        lines.append(
            f"| `{d.dataset_id}` | {d.name} | {version_str}"
            f" | {d.year} | {d.access_kind} | {d.size_description} |",
        )

    lines.append("")
    for d in datasets:
        authors_str: str = ", ".join(d.authors)
        categories_str: str = ", ".join(f"`{c}`" for c in d.categories)
        lines.append(f"## {d.name}")
        lines.append("")
        lines.append(f"* **Dataset ID**: `{d.dataset_id}`")
        lines.append(f"* **Authors**: {authors_str}")
        lines.append(f"* **Year**: {d.year}")
        lines.append(f"* **Access**: {d.access_kind}")
        lines.append(f"* **Size**: {d.size_description}")
        lines.append(f"* **Categories**: {categories_str}")
        added_by_str: str = d.added_by_task if d.added_by_task is not None else UNKNOWN_LABEL
        date_added_str: str = d.date_added if d.date_added is not None else UNKNOWN_LABEL
        lines.append(f"* **Added by**: `{added_by_str}`")
        lines.append(f"* **Date added**: {date_added_str}")
        lines.append("")

    return "\n".join(lines)


def _format_ids(*, dataset_ids: list[str]) -> str:
    return "\n".join(dataset_ids)


# ---------------------------------------------------------------------------
# Output formatting — full
# ---------------------------------------------------------------------------


def _format_full_json(*, datasets: list[DatasetInfoFull]) -> str:
    records: list[dict[str, Any]] = [asdict(d) for d in datasets]
    output: dict[str, Any] = {
        DATASET_COUNT_KEY: len(records),
        DATASETS_KEY: records,
    }
    return json.dumps(obj=output, indent=2, ensure_ascii=False)


def format_full_markdown(*, datasets: list[DatasetInfoFull]) -> str:
    if len(datasets) == 0:
        return "No datasets found."

    lines: list[str] = [f"# Datasets ({len(datasets)})", ""]

    lines.append(
        "| Name | Version | Year | Access | License | Size |",
    )
    lines.append(
        "|------|---------|------|--------|---------|------|",
    )
    for d in datasets:
        version_str: str = d.version if d.version is not None else "—"
        license_str: str = d.license if d.license is not None else "—"
        lines.append(
            f"| {d.name} | {version_str} | {d.year}"
            f" | {d.access_kind} | {license_str}"
            f" | {d.size_description} |",
        )

    lines.append("")
    for d in datasets:
        authors_str: str = ", ".join(_format_author_full(author=a) for a in d.authors)
        institutions_str: str = ", ".join(
            f"{inst.name} ({inst.country})" for inst in d.institutions
        )
        categories_str: str = ", ".join(f"`{c}`" for c in d.categories)
        files_str: str = ", ".join(f"`{f.path}` ({f.format})" for f in d.files)
        url_str: str = d.url if d.url is not None else "—"
        license_str = d.license if d.license is not None else "—"
        source_paper_str: str = f"`{d.source_paper_id}`" if d.source_paper_id is not None else "—"

        lines.append(f"## {d.name}")
        lines.append("")
        lines.append(f"* **Dataset ID**: `{d.dataset_id}`")
        if d.version is not None:
            lines.append(f"* **Version**: {d.version}")
        lines.append(f"* **URL**: {url_str}")
        lines.append(f"* **Authors**: {authors_str}")
        lines.append(f"* **Institutions**: {institutions_str}")
        lines.append(f"* **Year**: {d.year}")
        if d.date_published is not None:
            lines.append(f"* **Published**: {d.date_published}")
        lines.append(f"* **License**: {license_str}")
        lines.append(f"* **Access**: {d.access_kind}")
        lines.append(f"* **Size**: {d.size_description}")
        lines.append(f"* **Source paper**: {source_paper_str}")
        lines.append(f"* **Files**: {files_str}")
        lines.append(f"* **Categories**: {categories_str}")
        added_by_str = d.added_by_task if d.added_by_task is not None else UNKNOWN_LABEL
        date_added_str = d.date_added if d.date_added is not None else UNKNOWN_LABEL
        lines.append(f"* **Added by**: `{added_by_str}`")
        lines.append(f"* **Date added**: {date_added_str}")
        lines.append("")
        lines.append(d.short_description)
        lines.append("")
        if d.full_description is not None:
            lines.append(d.full_description)
            lines.append("")
        elif d.description_summary is not None:
            lines.append("### Summary")
            lines.append("")
            lines.append(d.description_summary)
            lines.append("")

    return "\n".join(lines)


def _format_author_full(*, author: AuthorInfo) -> str:
    parts: list[str] = [author.name]
    if author.country is not None:
        parts.append(f"({author.country})")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Aggregate all dataset assets in the project",
    )
    add_output_format_arg(parser=parser)
    add_detail_level_arg(parser=parser)
    add_filter_args(parser=parser)
    parser.add_argument(
        "--include-full-description",
        action="store_true",
        default=False,
        help=("Include the full description.md content for each dataset (only with --detail full)"),
    )
    args: argparse.Namespace = parser.parse_args()

    output_format: str = args.format
    detail_level: str = args.detail
    filter_categories: list[str] | None = args.categories
    filter_ids: list[str] | None = args.ids
    include_full_description: bool = args.include_full_description

    if detail_level == DETAIL_LEVEL_SHORT:
        datasets_short: list[DatasetInfoShort] = aggregate_datasets_short(
            filter_categories=filter_categories,
            filter_ids=filter_ids,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_short_json(datasets=datasets_short))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(
                _format_short_markdown(datasets=datasets_short),
            )
        elif output_format == OUTPUT_FORMAT_IDS:
            print(
                _format_ids(
                    dataset_ids=[d.dataset_id for d in datasets_short],
                ),
            )
        else:
            print(
                f"Unknown format: {output_format}",
                file=sys.stderr,
            )
            sys.exit(1)
    elif detail_level == DETAIL_LEVEL_FULL:
        datasets_full: list[DatasetInfoFull] = aggregate_datasets_full(
            filter_categories=filter_categories,
            include_full_description=include_full_description,
            filter_ids=filter_ids,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_full_json(datasets=datasets_full))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(
                format_full_markdown(datasets=datasets_full),
            )
        elif output_format == OUTPUT_FORMAT_IDS:
            print(
                _format_ids(
                    dataset_ids=[d.dataset_id for d in datasets_full],
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
