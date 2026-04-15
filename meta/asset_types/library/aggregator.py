"""Aggregate all library assets in the project.

Discovers library folders under tasks/*/assets/library/, loads their
details.json, and outputs structured data. Supports filtering by
category and library ID, and short/full detail levels.

Applies shared correction overlays to library metadata, descriptions,
and code-path references.

Aggregator version: 3
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
    TARGET_KIND_LIBRARY,
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
    library_base_dir,
    library_details_path,
)

LIBRARY_COUNT_KEY: str = "library_count"
LIBRARIES_KEY: str = "libraries"

# ---------------------------------------------------------------------------
# Pydantic models for details.json (I/O boundary)
# ---------------------------------------------------------------------------


class EntryPointModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    name: str
    kind: str
    module: str
    description: str


class LibraryDetailsModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    spec_version: str
    library_id: str
    name: str
    version: str
    short_description: str
    module_paths: list[str]
    entry_points: list[EntryPointModel]
    dependencies: list[str]
    test_paths: list[str] | None = None
    description_path: str | None = None
    categories: list[str]
    created_by_task: str
    date_created: str


# ---------------------------------------------------------------------------
# Internal data types (dataclasses for downstream use)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class EntryPointInfo:
    name: str
    kind: str
    module: str
    description: str


@dataclass(frozen=True, slots=True)
class LibraryInfoShort:
    library_id: str
    name: str
    version: str
    categories: list[str]
    short_description: str
    created_by_task: str
    date_created: str


@dataclass(frozen=True, slots=True)
class LibraryInfoFull:
    library_id: str
    name: str
    version: str
    short_description: str
    module_paths: list[str]
    entry_points: list[EntryPointInfo]
    dependencies: list[str]
    test_paths: list[str] | None
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
class _LibraryLocation:
    library_id: str
    task_id: str | None


def _discover_libraries() -> list[_LibraryLocation]:
    seen: set[str] = set()
    locations: list[_LibraryLocation] = []

    if TASKS_DIR.exists():
        for task_dir in sorted(TASKS_DIR.iterdir()):
            if not task_dir.is_dir() or task_dir.name.startswith("."):
                continue
            base: Path = library_base_dir(task_id=task_dir.name)
            if not base.exists():
                continue
            for lib_dir in sorted(base.iterdir()):
                if (
                    lib_dir.is_dir()
                    and not lib_dir.name.startswith(".")
                    and lib_dir.name not in seen
                ):
                    seen.add(lib_dir.name)
                    locations.append(
                        _LibraryLocation(
                            library_id=lib_dir.name,
                            task_id=task_dir.name,
                        ),
                    )

    top_level: Path = library_base_dir(task_id=None)
    if top_level.exists():
        for lib_dir in sorted(top_level.iterdir()):
            if lib_dir.is_dir() and not lib_dir.name.startswith(".") and lib_dir.name not in seen:
                seen.add(lib_dir.name)
                locations.append(
                    _LibraryLocation(
                        library_id=lib_dir.name,
                        task_id=None,
                    ),
                )

    return locations


def _load_effective_library_records() -> list[EffectiveTargetRecord]:
    correction_index = build_correction_index(
        correction_specs=discover_corrections(),
    )
    records: list[EffectiveTargetRecord] = []
    for location in _discover_libraries():
        if location.task_id is None:
            continue
        resolution = resolve_target(
            original_key=TargetKey(
                task_id=location.task_id,
                target_kind=TARGET_KIND_LIBRARY,
                target_id=location.library_id,
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
        target_kind=TARGET_KIND_LIBRARY,
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
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(
        content=content,
    )
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
        target_kind=TARGET_KIND_LIBRARY,
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
    library_id: str,
    task_id: str | None,
) -> LibraryDetailsModel | None:
    file_path: Path = library_details_path(
        library_id=library_id,
        task_id=task_id,
    )
    if not file_path.exists():
        return None
    try:
        raw: str = file_path.read_text(encoding="utf-8")
        return LibraryDetailsModel.model_validate_json(raw)
    except (OSError, UnicodeDecodeError, ValidationError):
        return None


# ---------------------------------------------------------------------------
# Conversion from Pydantic model to internal dataclasses
# ---------------------------------------------------------------------------


def _to_short(
    *,
    details: LibraryDetailsModel,
) -> LibraryInfoShort:
    return LibraryInfoShort(
        library_id=details.library_id,
        name=details.name,
        version=details.version,
        categories=details.categories,
        short_description=details.short_description,
        created_by_task=details.created_by_task,
        date_created=details.date_created,
    )


def _to_full(
    *,
    details: LibraryDetailsModel,
    module_paths: list[str],
    test_paths: list[str] | None,
    description_path: str | None,
    description_summary: str | None,
    full_description: str | None,
) -> LibraryInfoFull:
    return LibraryInfoFull(
        library_id=details.library_id,
        name=details.name,
        version=details.version,
        short_description=details.short_description,
        module_paths=module_paths,
        entry_points=[
            EntryPointInfo(
                name=ep.name,
                kind=ep.kind,
                module=ep.module,
                description=ep.description,
            )
            for ep in details.entry_points
        ],
        dependencies=details.dependencies,
        test_paths=test_paths,
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


def _resolve_library_paths(
    *,
    record: EffectiveTargetRecord,
    logical_paths: list[str] | None,
) -> list[str] | None:
    if logical_paths is None:
        return None
    resolved_paths: list[str] = []
    for logical_path in logical_paths:
        resolved_reference = find_resolved_file(
            record=record,
            logical_path=logical_path,
        )
        if resolved_reference is None:
            continue
        resolved_paths.append(resolved_reference.repo_relative_path)
    return resolved_paths


def aggregate_libraries_short(
    *,
    filter_categories: list[str] | None = None,
    filter_ids: list[str] | None = None,
) -> list[LibraryInfoShort]:
    libraries: list[LibraryInfoShort] = []
    for record in _load_effective_library_records():
        try:
            details: LibraryDetailsModel = LibraryDetailsModel.model_validate(
                record.payload,
            )
        except ValidationError:
            continue
        if not matches_ids(
            asset_id=details.library_id,
            filter_ids=filter_ids,
        ):
            continue
        if not matches_categories(
            asset_categories=details.categories,
            filter_categories=filter_categories,
        ):
            continue
        libraries.append(_to_short(details=details))
    for loc in _discover_libraries():
        if loc.task_id is not None:
            continue
        if not matches_ids(
            asset_id=loc.library_id,
            filter_ids=filter_ids,
        ):
            continue
        top_level_details: LibraryDetailsModel | None = _load_details(
            library_id=loc.library_id,
            task_id=loc.task_id,
        )
        if top_level_details is None:
            continue
        if not matches_categories(
            asset_categories=top_level_details.categories,
            filter_categories=filter_categories,
        ):
            continue
        libraries.append(_to_short(details=top_level_details))
    return libraries


def aggregate_libraries_full(
    *,
    filter_categories: list[str] | None = None,
    filter_ids: list[str] | None = None,
    include_full_description: bool = False,
) -> list[LibraryInfoFull]:
    libraries: list[LibraryInfoFull] = []
    for record in _load_effective_library_records():
        try:
            details: LibraryDetailsModel = LibraryDetailsModel.model_validate(
                record.payload,
            )
        except ValidationError:
            continue
        if not matches_ids(
            asset_id=details.library_id,
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
            target_kind=TARGET_KIND_LIBRARY,
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
        resolved_module_paths: list[str] | None = _resolve_library_paths(
            record=record,
            logical_paths=details.module_paths,
        )
        libraries.append(
            _to_full(
                details=details,
                module_paths=(resolved_module_paths if resolved_module_paths is not None else []),
                test_paths=_resolve_library_paths(
                    record=record,
                    logical_paths=details.test_paths,
                ),
                description_path=(
                    description_reference.repo_relative_path
                    if description_reference is not None
                    else None
                ),
                description_summary=description_summary,
                full_description=full_description,
            ),
        )
    for loc in _discover_libraries():
        if loc.task_id is not None:
            continue
        if not matches_ids(
            asset_id=loc.library_id,
            filter_ids=filter_ids,
        ):
            continue
        top_level_details: LibraryDetailsModel | None = _load_details(
            library_id=loc.library_id,
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
            target_kind=TARGET_KIND_LIBRARY,
            payload=top_level_details.model_dump(),
            document_kind=DOCUMENT_KIND_DESCRIPTION,
        )
        top_level_description_file = (
            library_base_dir(task_id=loc.task_id)
            / loc.library_id
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
        libraries.append(
            _to_full(
                details=top_level_details,
                module_paths=top_level_details.module_paths,
                test_paths=top_level_details.test_paths,
                description_path=top_level_description_path,
                description_summary=top_level_description_summary,
                full_description=top_level_full_description,
            ),
        )
    return libraries


# ---------------------------------------------------------------------------
# Output formatting — short
# ---------------------------------------------------------------------------


def _format_short_json(*, libraries: list[LibraryInfoShort]) -> str:
    records: list[dict[str, Any]] = [asdict(lib) for lib in libraries]
    output: dict[str, Any] = {
        LIBRARY_COUNT_KEY: len(records),
        LIBRARIES_KEY: records,
    }
    return json.dumps(obj=output, indent=2, ensure_ascii=False)


def _format_short_markdown(
    *,
    libraries: list[LibraryInfoShort],
) -> str:
    if len(libraries) == 0:
        return "No libraries found."

    lines: list[str] = [f"# Libraries ({len(libraries)})", ""]

    lines.append("| ID | Name | Version | Categories | Task |")
    lines.append("|----|------|---------|------------|------|")
    for lib in libraries:
        categories_str: str = ", ".join(f"`{c}`" for c in lib.categories)
        lines.append(
            f"| `{lib.library_id}` | {lib.name} | {lib.version}"
            f" | {categories_str} | `{lib.created_by_task}` |",
        )

    lines.append("")
    for lib in libraries:
        categories_str = ", ".join(f"`{c}`" for c in lib.categories)
        lines.append(f"## {lib.name}")
        lines.append("")
        lines.append(f"* **Library ID**: `{lib.library_id}`")
        lines.append(f"* **Version**: {lib.version}")
        lines.append(f"* **Categories**: {categories_str}")
        lines.append(f"* **Created by**: `{lib.created_by_task}`")
        lines.append(f"* **Date created**: {lib.date_created}")
        lines.append("")
        lines.append(lib.short_description)
        lines.append("")

    return "\n".join(lines)


def _format_ids(*, library_ids: list[str]) -> str:
    return "\n".join(library_ids)


# ---------------------------------------------------------------------------
# Output formatting — full
# ---------------------------------------------------------------------------


def _format_full_json(*, libraries: list[LibraryInfoFull]) -> str:
    records: list[dict[str, Any]] = [asdict(lib) for lib in libraries]
    output: dict[str, Any] = {
        LIBRARY_COUNT_KEY: len(records),
        LIBRARIES_KEY: records,
    }
    return json.dumps(obj=output, indent=2, ensure_ascii=False)


def format_full_markdown(*, libraries: list[LibraryInfoFull]) -> str:
    if len(libraries) == 0:
        return "No libraries found."

    lines: list[str] = [f"# Libraries ({len(libraries)})", ""]

    lines.append("| Name | Version | Dependencies | Task |")
    lines.append("|------|---------|-------------|------|")
    for lib in libraries:
        deps_str: str = ", ".join(lib.dependencies) if len(lib.dependencies) > 0 else "\u2014"
        lines.append(
            f"| {lib.name} | {lib.version} | {deps_str} | `{lib.created_by_task}` |",
        )

    lines.append("")
    for lib in libraries:
        categories_str: str = ", ".join(f"`{c}`" for c in lib.categories)
        modules_str: str = ", ".join(f"`{m}`" for m in lib.module_paths)
        deps_str = ", ".join(lib.dependencies) if len(lib.dependencies) > 0 else "\u2014"

        lines.append(f"## {lib.name}")
        lines.append("")
        lines.append(f"* **Library ID**: `{lib.library_id}`")
        lines.append(f"* **Version**: {lib.version}")
        lines.append(f"* **Modules**: {modules_str}")
        lines.append(f"* **Dependencies**: {deps_str}")
        lines.append(f"* **Categories**: {categories_str}")
        lines.append(f"* **Created by**: `{lib.created_by_task}`")
        lines.append(f"* **Date created**: {lib.date_created}")
        if lib.description_path is not None:
            lines.append(f"* **Documentation**: `{lib.description_path}`")
        lines.append("")

        if len(lib.entry_points) > 0:
            lines.append("### Entry Points")
            lines.append("")
            for ep in lib.entry_points:
                lines.append(f"* `{ep.name}` ({ep.kind}) — {ep.description}")
            lines.append("")

        lines.append(lib.short_description)
        lines.append("")

        if lib.full_description is not None:
            lines.append(lib.full_description)
            lines.append("")
        elif lib.description_summary is not None:
            lines.append("### Summary")
            lines.append("")
            lines.append(lib.description_summary)
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Aggregate all library assets in the project",
    )
    add_output_format_arg(parser=parser)
    add_detail_level_arg(parser=parser)
    add_filter_args(parser=parser)
    parser.add_argument(
        "--include-full-description",
        action="store_true",
        default=False,
        help=("Include the full description.md content for each library (only with --detail full)"),
    )
    args: argparse.Namespace = parser.parse_args()

    output_format: str = args.format
    detail_level: str = args.detail
    filter_categories: list[str] | None = args.categories
    filter_ids: list[str] | None = args.ids
    include_full_description: bool = args.include_full_description

    if detail_level == DETAIL_LEVEL_SHORT:
        libraries_short: list[LibraryInfoShort] = aggregate_libraries_short(
            filter_categories=filter_categories,
            filter_ids=filter_ids,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_short_json(libraries=libraries_short))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(
                _format_short_markdown(libraries=libraries_short),
            )
        elif output_format == OUTPUT_FORMAT_IDS:
            print(
                _format_ids(
                    library_ids=[lib.library_id for lib in libraries_short],
                ),
            )
        else:
            print(
                f"Unknown format: {output_format}",
                file=sys.stderr,
            )
            sys.exit(1)
    elif detail_level == DETAIL_LEVEL_FULL:
        libraries_full: list[LibraryInfoFull] = aggregate_libraries_full(
            filter_categories=filter_categories,
            include_full_description=include_full_description,
            filter_ids=filter_ids,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_full_json(libraries=libraries_full))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(
                format_full_markdown(libraries=libraries_full),
            )
        elif output_format == OUTPUT_FORMAT_IDS:
            print(
                _format_ids(
                    library_ids=[lib.library_id for lib in libraries_full],
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
