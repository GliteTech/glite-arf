"""Aggregate all paper assets in the project.

Discovers paper folders under tasks/*/assets/paper/ and assets/paper/,
loads their details.json, and outputs structured data. Supports filtering
by category and paper ID, and short/full detail levels.

Applies shared correction overlays to paper metadata, summaries, and
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

from pydantic import BaseModel, ConfigDict, Field, ValidationError

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
    DOCUMENT_KIND_SUMMARY,
    SUMMARY_FILE_NAME,
    TARGET_KIND_PAPER,
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
    paper_base_dir,
    paper_details_path,
)

type CitationKey = str
type PaperID = str
type RepoRelativePath = str
type TaskID = str

PAPER_COUNT_KEY: str = "paper_count"
PAPERS_KEY: str = "papers"
UTF8_ENCODING: str = "utf-8"
NO_PAPERS_FOUND: str = "No papers found."
EM_DASH: str = "\u2014"

# ---------------------------------------------------------------------------
# Pydantic models for details.json (I/O boundary)
# ---------------------------------------------------------------------------


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


class PaperDetailsModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore", populate_by_name=True)

    spec_version: str
    paper_id: PaperID
    doi: str | None
    title: str
    url: str | None
    pdf_url: str | None = None
    date_published: str | None = None
    year: int
    authors: list[AuthorModel]
    institutions: list[InstitutionModel]
    journal: str
    venue_kind: str = Field(alias="venue_type")
    categories: list[str]
    abstract: str
    citation_key: CitationKey
    summary_path: Path | None = None
    files: list[Path]
    download_status: str
    download_failure_reason: str | None
    added_by_task: TaskID
    date_added: str


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
class PaperInfoShort:
    paper_id: PaperID
    title: str
    year: int
    authors: list[str]
    citation_key: CitationKey
    categories: list[str]
    journal: str
    download_status: str
    added_by_task: TaskID


@dataclass(frozen=True, slots=True)
class PaperInfoFull:
    paper_id: PaperID
    title: str
    doi: str | None
    url: str | None
    pdf_url: str | None
    date_published: str | None
    year: int
    authors: list[AuthorInfo]
    institutions: list[InstitutionInfo]
    journal: str
    venue_kind: str
    categories: list[str]
    abstract: str
    citation_key: CitationKey
    files: list[Path]
    download_status: str
    download_failure_reason: str | None
    added_by_task: TaskID
    date_added: str
    summary_path: Path | None
    summary: str | None
    full_summary: str | None


# ---------------------------------------------------------------------------
# Discovery and loading
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _PaperLocation:
    paper_id: PaperID
    task_id: TaskID | None


def _discover_papers() -> list[_PaperLocation]:
    seen: set[PaperID] = set()
    locations: list[_PaperLocation] = []

    # Scan tasks/*/assets/paper/
    if TASKS_DIR.exists():
        for task_dir in sorted(TASKS_DIR.iterdir()):
            if not task_dir.is_dir() or task_dir.name.startswith("."):
                continue
            base: Path = paper_base_dir(task_id=task_dir.name)
            if not base.exists():
                continue
            for paper_dir in sorted(base.iterdir()):
                if (
                    paper_dir.is_dir()
                    and not paper_dir.name.startswith(".")
                    and paper_dir.name not in seen
                ):
                    seen.add(paper_dir.name)
                    locations.append(
                        _PaperLocation(
                            paper_id=paper_dir.name,
                            task_id=task_dir.name,
                        ),
                    )

    # Scan top-level assets/paper/
    top_level: Path = paper_base_dir(task_id=None)
    if top_level.exists():
        for paper_dir in sorted(top_level.iterdir()):
            if (
                paper_dir.is_dir()
                and not paper_dir.name.startswith(".")
                and paper_dir.name not in seen
            ):
                seen.add(paper_dir.name)
                locations.append(
                    _PaperLocation(paper_id=paper_dir.name, task_id=None),
                )

    return locations


def _load_effective_paper_records() -> list[EffectiveTargetRecord]:
    correction_index: dict[TargetKey, list[CorrectionSpec]] = build_correction_index(
        correction_specs=discover_corrections(),
    )
    records: list[EffectiveTargetRecord] = []
    for location in _discover_papers():
        if location.task_id is None:
            continue
        resolution = resolve_target(
            original_key=TargetKey(
                task_id=location.task_id,
                target_kind=TARGET_KIND_PAPER,
                target_id=location.paper_id,
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


def _load_summary_section(*, file_path: Path) -> str | None:
    if not file_path.exists():
        return None
    try:
        content: str = file_path.read_text(encoding=UTF8_ENCODING)
    except (OSError, UnicodeDecodeError):
        return None
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(content=content)
    if split_result is None:
        return None
    sections: list[MarkdownSection] = extract_sections(body=split_result.body, level=2)
    for section in sections:
        if section.heading == _SUMMARY_SECTION_HEADING:
            return section.content.strip()
    return None


def _load_summary_section_from_repo_relative_path(
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
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(content=content)
    if split_result is None:
        return None
    sections: list[MarkdownSection] = extract_sections(body=split_result.body, level=2)
    for section in sections:
        if section.heading == _SUMMARY_SECTION_HEADING:
            return section.content.strip()
    return None


def _load_summary_section_from_effective_record(
    *,
    record: EffectiveTargetRecord,
) -> str | None:
    selection = select_canonical_document_path(
        target_kind=TARGET_KIND_PAPER,
        payload=record.payload,
        document_kind=DOCUMENT_KIND_SUMMARY,
    )
    if selection is None or selection.logical_path is None:
        return None
    resolved_file = find_resolved_file(record=record, logical_path=selection.logical_path)
    if resolved_file is None:
        return None
    return _load_summary_section_from_repo_relative_path(
        repo_relative_path=resolved_file.repo_relative_path,
    )


def _load_full_summary(*, file_path: Path) -> str | None:
    if not file_path.exists():
        return None
    try:
        content: str = file_path.read_text(encoding=UTF8_ENCODING)
    except (OSError, UnicodeDecodeError):
        return None
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(content=content)
    if split_result is None:
        return None
    return split_result.body.strip()


def _load_full_summary_from_repo_relative_path(
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
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(content=content)
    if split_result is None:
        return None
    return split_result.body.strip()


def _load_full_summary_from_effective_record(
    *,
    record: EffectiveTargetRecord,
) -> str | None:
    selection = select_canonical_document_path(
        target_kind=TARGET_KIND_PAPER,
        payload=record.payload,
        document_kind=DOCUMENT_KIND_SUMMARY,
    )
    if selection is None or selection.logical_path is None:
        return None
    resolved_file = find_resolved_file(record=record, logical_path=selection.logical_path)
    if resolved_file is None:
        return None
    return _load_full_summary_from_repo_relative_path(
        repo_relative_path=resolved_file.repo_relative_path,
    )


def _load_details(*, paper_id: PaperID, task_id: TaskID | None) -> PaperDetailsModel | None:
    file_path: Path = paper_details_path(paper_id=paper_id, task_id=task_id)
    if not file_path.exists():
        return None
    try:
        raw: str = file_path.read_text(encoding=UTF8_ENCODING)
        return PaperDetailsModel.model_validate_json(raw)
    except (OSError, UnicodeDecodeError, ValidationError):
        return None


# ---------------------------------------------------------------------------
# Conversion from Pydantic model to internal dataclasses
# ---------------------------------------------------------------------------


def _to_short(*, details: PaperDetailsModel) -> PaperInfoShort:
    return PaperInfoShort(
        paper_id=details.paper_id,
        title=details.title,
        year=details.year,
        authors=[a.name for a in details.authors],
        citation_key=details.citation_key,
        categories=details.categories,
        journal=details.journal,
        download_status=details.download_status,
        added_by_task=details.added_by_task,
    )


def _to_full(
    *,
    details: PaperDetailsModel,
    file_paths: list[Path],
    summary_path: Path | None,
    summary: str | None,
    full_summary: str | None,
) -> PaperInfoFull:
    return PaperInfoFull(
        paper_id=details.paper_id,
        title=details.title,
        doi=details.doi,
        url=details.url,
        pdf_url=details.pdf_url,
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
        journal=details.journal,
        venue_kind=details.venue_kind,
        categories=details.categories,
        abstract=details.abstract,
        citation_key=details.citation_key,
        files=file_paths,
        download_status=details.download_status,
        download_failure_reason=details.download_failure_reason,
        added_by_task=details.added_by_task,
        date_added=details.date_added,
        summary_path=summary_path,
        summary=summary,
        full_summary=full_summary,
    )


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def aggregate_papers_short(
    *,
    filter_categories: list[str] | None = None,
    filter_ids: list[str] | None = None,
) -> list[PaperInfoShort]:
    papers: list[PaperInfoShort] = []
    for record in _load_effective_paper_records():
        try:
            details: PaperDetailsModel = PaperDetailsModel.model_validate(record.payload)
        except ValidationError:
            continue
        if not matches_ids(asset_id=details.paper_id, filter_ids=filter_ids):
            continue
        if not matches_categories(
            asset_categories=details.categories,
            filter_categories=filter_categories,
        ):
            continue
        papers.append(_to_short(details=details))

    for loc in _discover_papers():
        if loc.task_id is not None:
            continue
        if not matches_ids(asset_id=loc.paper_id, filter_ids=filter_ids):
            continue
        top_level_details: PaperDetailsModel | None = _load_details(
            paper_id=loc.paper_id,
            task_id=loc.task_id,
        )
        if top_level_details is None:
            continue
        if not matches_categories(
            asset_categories=top_level_details.categories,
            filter_categories=filter_categories,
        ):
            continue
        papers.append(_to_short(details=top_level_details))
    return papers


def aggregate_papers_full(
    *,
    filter_categories: list[str] | None = None,
    filter_ids: list[str] | None = None,
    include_full_summary: bool = False,
) -> list[PaperInfoFull]:
    papers: list[PaperInfoFull] = []
    for record in _load_effective_paper_records():
        try:
            details: PaperDetailsModel = PaperDetailsModel.model_validate(record.payload)
        except ValidationError:
            continue
        if not matches_ids(asset_id=details.paper_id, filter_ids=filter_ids):
            continue
        if not matches_categories(
            asset_categories=details.categories,
            filter_categories=filter_categories,
        ):
            continue
        summary: str | None = _load_summary_section_from_effective_record(record=record)
        full_summary: str | None = None
        if include_full_summary:
            full_summary = _load_full_summary_from_effective_record(record=record)
        summary_selection = select_canonical_document_path(
            target_kind=TARGET_KIND_PAPER,
            payload=record.payload,
            document_kind=DOCUMENT_KIND_SUMMARY,
        )
        summary_reference = (
            find_resolved_file(
                record=record,
                logical_path=summary_selection.logical_path,
            )
            if summary_selection is not None and summary_selection.logical_path is not None
            else None
        )
        file_paths: list[Path] = [
            Path(reference.repo_relative_path)
            for reference in record.file_references
            if summary_selection is None or reference.logical_path != summary_selection.logical_path
        ]
        papers.append(
            _to_full(
                details=details,
                file_paths=file_paths,
                summary_path=(
                    Path(summary_reference.repo_relative_path)
                    if summary_reference is not None
                    else None
                ),
                summary=summary,
                full_summary=full_summary,
            ),
        )

    for loc in _discover_papers():
        if loc.task_id is not None:
            continue
        if not matches_ids(asset_id=loc.paper_id, filter_ids=filter_ids):
            continue
        top_level_details: PaperDetailsModel | None = _load_details(
            paper_id=loc.paper_id,
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
            target_kind=TARGET_KIND_PAPER,
            payload=top_level_details.model_dump(mode="json"),
            document_kind=DOCUMENT_KIND_SUMMARY,
        )
        top_level_summary_file = (
            paper_base_dir(task_id=loc.task_id)
            / loc.paper_id
            / (
                selection.logical_path
                if selection is not None and selection.logical_path is not None
                else SUMMARY_FILE_NAME
            )
        )
        top_level_summary = _load_summary_section(
            file_path=top_level_summary_file,
        )
        top_level_full_summary: str | None = None
        if include_full_summary:
            top_level_full_summary = _load_full_summary(
                file_path=top_level_summary_file,
            )
        top_level_summary_path: Path | None = None
        if top_level_summary_file.exists():
            top_level_summary_path = Path(
                to_repo_relative_path(file_path=top_level_summary_file),
            )
        papers.append(
            _to_full(
                details=top_level_details,
                file_paths=top_level_details.files,
                summary_path=top_level_summary_path,
                summary=top_level_summary,
                full_summary=top_level_full_summary,
            ),
        )
    return papers


# ---------------------------------------------------------------------------
# Output formatting — short
# ---------------------------------------------------------------------------


def _format_short_json(*, papers: list[PaperInfoShort]) -> str:
    records: list[dict[str, Any]] = [asdict(p) for p in papers]
    output: dict[str, Any] = {
        PAPER_COUNT_KEY: len(records),
        PAPERS_KEY: records,
    }
    return dumps(obj=output, indent=2, ensure_ascii=False)


def _format_short_markdown(*, papers: list[PaperInfoShort]) -> str:
    if len(papers) == 0:
        return NO_PAPERS_FOUND

    lines: list[str] = [f"# Papers ({len(papers)})", ""]

    lines.append("| ID | Citation | Title | Year | Venue | Status |")
    lines.append("|----|----------|-------|------|-------|--------|")
    for p in papers:
        lines.append(
            f"| `{p.paper_id}` | {p.citation_key} | {p.title}"
            f" | {p.year} | {p.journal} | {p.download_status} |",
        )

    lines.append("")
    for p in papers:
        authors_str: str = ", ".join(p.authors)
        categories_str: str = ", ".join(f"`{c}`" for c in p.categories)
        lines.append(f"## {p.citation_key}: {p.title}")
        lines.append("")
        lines.append(f"* **Paper ID**: `{p.paper_id}`")
        lines.append(f"* **Authors**: {authors_str}")
        lines.append(f"* **Year**: {p.year}")
        lines.append(f"* **Venue**: {p.journal}")
        lines.append(f"* **Categories**: {categories_str}")
        lines.append(f"* **Download**: {p.download_status}")
        lines.append(f"* **Added by**: `{p.added_by_task}`")
        lines.append("")

    return "\n".join(lines)


def _format_ids(*, paper_ids: list[PaperID]) -> str:
    return "\n".join(paper_ids)


# ---------------------------------------------------------------------------
# Output formatting — full
# ---------------------------------------------------------------------------


def _format_full_json(*, papers: list[PaperInfoFull]) -> str:
    records: list[dict[str, Any]] = [_paper_full_to_dict(paper=paper) for paper in papers]
    output: dict[str, Any] = {
        PAPER_COUNT_KEY: len(records),
        PAPERS_KEY: records,
    }
    return dumps(obj=output, indent=2, ensure_ascii=False)


def _paper_full_to_dict(*, paper: PaperInfoFull) -> dict[str, Any]:
    record: dict[str, Any] = asdict(paper)
    record["files"] = [file_path.as_posix() for file_path in paper.files]
    record["summary_path"] = (
        paper.summary_path.as_posix() if paper.summary_path is not None else None
    )
    return record


def format_full_markdown(*, papers: list[PaperInfoFull]) -> str:
    if len(papers) == 0:
        return NO_PAPERS_FOUND

    lines: list[str] = [f"# Papers ({len(papers)})", ""]

    lines.append("| Citation | Title | Year | Venue | DOI | Status |")
    lines.append(
        "|----------|-------|------|-------|-----|--------|",
    )
    for p in papers:
        doi_str: str = f"`{p.doi}`" if p.doi is not None else EM_DASH
        lines.append(
            f"| {p.citation_key} | {p.title} | {p.year}"
            f" | {p.journal} | {doi_str} | {p.download_status} |",
        )

    lines.append("")
    for p in papers:
        authors_str: str = ", ".join(_format_author_full(author=a) for a in p.authors)
        institutions_str: str = ", ".join(
            f"{inst.name} ({inst.country})" for inst in p.institutions
        )
        categories_str: str = ", ".join(f"`{c}`" for c in p.categories)
        files_str: str = ", ".join(f"`{file_path.as_posix()}`" for file_path in p.files)
        doi_str = f"`{p.doi}`" if p.doi is not None else EM_DASH
        url_str: str = p.url if p.url is not None else EM_DASH

        lines.append(f"## {p.citation_key}: {p.title}")
        lines.append("")
        lines.append(f"* **Paper ID**: `{p.paper_id}`")
        lines.append(f"* **DOI**: {doi_str}")
        lines.append(f"* **URL**: {url_str}")
        lines.append(f"* **Authors**: {authors_str}")
        lines.append(f"* **Institutions**: {institutions_str}")
        lines.append(f"* **Year**: {p.year}")
        if p.date_published is not None:
            lines.append(f"* **Published**: {p.date_published}")
        lines.append(f"* **Venue**: {p.journal} ({p.venue_kind})")
        lines.append(f"* **Categories**: {categories_str}")
        lines.append(f"* **Files**: {files_str}")
        lines.append(f"* **Download**: {p.download_status}")
        if p.download_failure_reason is not None:
            lines.append(
                f"* **Failure reason**: {p.download_failure_reason}",
            )
        lines.append(f"* **Added by**: `{p.added_by_task}`")
        lines.append(f"* **Date added**: {p.date_added}")
        if p.summary_path is not None:
            lines.append(f"* **Summary file**: `{p.summary_path.as_posix()}`")
        lines.append("")
        if p.full_summary is not None:
            lines.append(p.full_summary)
            lines.append("")
        elif p.summary is not None:
            lines.append("### Summary")
            lines.append("")
            lines.append(p.summary)
            lines.append("")
        else:
            lines.append("### Abstract")
            lines.append("")
            lines.append(p.abstract)
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
    parser: ArgumentParser = ArgumentParser(
        description="Aggregate all paper assets in the project",
    )
    add_output_format_arg(parser=parser)
    add_detail_level_arg(parser=parser)
    add_filter_args(parser=parser)
    parser.add_argument(
        "--include-full-summary",
        action="store_true",
        default=False,
        help="Include the full summary.md content for each paper (only with --detail full)",
    )
    args: Namespace = parser.parse_args()

    output_format: str = args.format
    detail_level: str = args.detail
    filter_categories: list[str] | None = args.categories
    filter_ids: list[str] | None = args.ids
    include_full_summary: bool = args.include_full_summary

    if detail_level == DETAIL_LEVEL_SHORT:
        papers_short: list[PaperInfoShort] = aggregate_papers_short(
            filter_categories=filter_categories,
            filter_ids=filter_ids,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_short_json(papers=papers_short))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(_format_short_markdown(papers=papers_short))
        elif output_format == OUTPUT_FORMAT_IDS:
            print(
                _format_ids(
                    paper_ids=[p.paper_id for p in papers_short],
                ),
            )
        else:
            print(f"Unknown format: {output_format}", file=stderr)
            sys_exit(1)
    elif detail_level == DETAIL_LEVEL_FULL:
        papers_full: list[PaperInfoFull] = aggregate_papers_full(
            filter_categories=filter_categories,
            include_full_summary=include_full_summary,
            filter_ids=filter_ids,
        )
        if output_format == OUTPUT_FORMAT_JSON:
            print(_format_full_json(papers=papers_full))
        elif output_format == OUTPUT_FORMAT_MARKDOWN:
            print(format_full_markdown(papers=papers_full))
        elif output_format == OUTPUT_FORMAT_IDS:
            print(
                _format_ids(
                    paper_ids=[p.paper_id for p in papers_full],
                ),
            )
        else:
            print(f"Unknown format: {output_format}", file=stderr)
            sys_exit(1)
    else:
        print(f"Unknown detail level: {detail_level}", file=stderr)
        sys_exit(1)


if __name__ == "__main__":
    main()
