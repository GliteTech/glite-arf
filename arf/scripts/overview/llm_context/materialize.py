"""Materialize committed LLM context archives under overview/llm-context/."""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from arf.scripts.aggregators.aggregate_categories import CategoryInfo
from arf.scripts.aggregators.aggregate_costs import CostAggregationFull
from arf.scripts.aggregators.aggregate_metrics import MetricInfoFull
from arf.scripts.aggregators.aggregate_suggestions import SuggestionInfoFull
from arf.scripts.aggregators.aggregate_task_types import TaskTypeInfo
from arf.scripts.aggregators.aggregate_tasks import TaskInfoFull
from arf.scripts.overview import paths as overview_paths
from arf.scripts.overview.common import (
    normalize_markdown,
    remove_dir_if_exists,
    write_file,
)
from arf.scripts.overview.llm_context.collect import (
    build_sections,
)
from arf.scripts.overview.llm_context.models import (
    ArchiveSection,
    LLMContextArchiveSummary,
    PresetDefinition,
    ProjectSnapshot,
    RenderedArchive,
    RenderedTypeArchive,
    TypeArchiveDefinition,
    TypeArchiveSummary,
)
from arf.scripts.overview.llm_context.presets import build_presets
from arf.scripts.overview.llm_context.render_xml import (
    render_archive_xml,
    render_type_archive_xml,
)
from arf.scripts.overview.llm_context.token_estimation import (
    CONTEXT_WINDOWS,
    compatible_windows,
    estimate_tokens,
)
from arf.scripts.overview.llm_context.type_archives import (
    build_type_archive_definitions,
    collect_sections_for_type,
)
from arf.scripts.verificators.common import paths as repo_paths
from meta.asset_types.answer.aggregator import AnswerInfoFull
from meta.asset_types.dataset.aggregator import DatasetInfoFull
from meta.asset_types.library.aggregator import LibraryInfoFull
from meta.asset_types.model.aggregator import ModelInfoFull
from meta.asset_types.paper.aggregator import PaperInfoFull
from meta.asset_types.predictions.aggregator import PredictionsInfoFull

SECTION_NAME: str = "llm-context"
README_FILE_NAME: str = "README.md"
MAX_RENDER_PASSES: int = 10


@dataclass(frozen=True, slots=True)
class MaterializationResult:
    preset_summaries: list[LLMContextArchiveSummary]
    type_summaries: list[TypeArchiveSummary]


def materialize_llm_context(
    *,
    tasks: list[TaskInfoFull],
    answers: list[AnswerInfoFull],
    papers: list[PaperInfoFull],
    datasets: list[DatasetInfoFull],
    libraries: list[LibraryInfoFull],
    metrics: list[MetricInfoFull],
    suggestions: list[SuggestionInfoFull],
    models: list[ModelInfoFull] | None = None,
    predictions: list[PredictionsInfoFull] | None = None,
    categories: list[CategoryInfo] | None = None,
    task_types: list[TaskTypeInfo] | None = None,
    costs: CostAggregationFull | None = None,
) -> MaterializationResult:
    llm_context_dir: Path = overview_paths.overview_section_dir(
        section_name=SECTION_NAME,
    )

    remove_dir_if_exists(dir_path=llm_context_dir)

    snapshot: ProjectSnapshot = ProjectSnapshot(
        project_description=_load_project_description(),
        tasks=tasks,
        answers=answers,
        papers=papers,
        datasets=datasets,
        libraries=libraries,
        metrics=metrics,
        suggestions=suggestions,
        models=models if models is not None else [],
        predictions=predictions if predictions is not None else [],
        categories=categories if categories is not None else [],
        task_types=task_types if task_types is not None else [],
        costs=costs,
    )
    generated_at_utc: str = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    rendered_archives: list[RenderedArchive] = []
    for preset in build_presets():
        rendered_archive: RenderedArchive = _render_preset_archive(
            snapshot=snapshot,
            preset=preset,
            generated_at_utc=generated_at_utc,
        )
        rendered_archives.append(rendered_archive)
        write_file(
            file_path=llm_context_dir / preset.file_name,
            content=rendered_archive.content,
        )

    rendered_type_archives: list[RenderedTypeArchive] = []
    for definition in build_type_archive_definitions():
        sections: list[ArchiveSection] = collect_sections_for_type(
            type_id=definition.type_id,
            snapshot=snapshot,
        )
        if len(sections) == 0:
            continue
        rendered_type: RenderedTypeArchive = _render_type_archive(
            definition=definition,
            sections=sections,
            generated_at_utc=generated_at_utc,
        )
        rendered_type_archives.append(rendered_type)
        write_file(
            file_path=llm_context_dir / definition.file_name,
            content=rendered_type.content,
        )

    llm_context_readme: Path = overview_paths.overview_section_readme(
        section_name=SECTION_NAME,
    )
    write_file(
        file_path=llm_context_readme,
        content=normalize_markdown(
            content=_format_index(
                preset_summaries=[a.summary for a in rendered_archives],
                type_summaries=[a.summary for a in rendered_type_archives],
            ),
        ),
    )
    return MaterializationResult(
        preset_summaries=[a.summary for a in rendered_archives],
        type_summaries=[a.summary for a in rendered_type_archives],
    )


def _load_project_description() -> str:
    file_path: Path = repo_paths.REPO_ROOT / overview_paths.PROJECT_DESCRIPTION_REPO_PATH
    return file_path.read_text(encoding="utf-8").strip()


def _render_preset_archive(
    *,
    snapshot: ProjectSnapshot,
    preset: PresetDefinition,
    generated_at_utc: str,
) -> RenderedArchive:
    sections = build_sections(
        snapshot=snapshot,
        preset=preset,
    )

    provisional_char_count: int = 0
    provisional_byte_count: int = 0
    provisional_estimated_tokens: int = 0
    provisional_compatibility: list[str] = []
    content: str = ""

    for _ in range(MAX_RENDER_PASSES):
        content = render_archive_xml(
            preset=preset,
            sections=sections,
            generated_at_utc=generated_at_utc,
            char_count=provisional_char_count,
            byte_count=provisional_byte_count,
            estimated_tokens=provisional_estimated_tokens,
            compatibility_labels=provisional_compatibility,
        )
        file_content: str = content + "\n"
        char_count = len(file_content)
        byte_count = len(file_content.encode("utf-8"))
        estimated_tokens = estimate_tokens(text=file_content)
        compatibility: list[str] = compatible_windows(
            estimated_tokens=estimated_tokens,
        )
        if (
            char_count == provisional_char_count
            and byte_count == provisional_byte_count
            and estimated_tokens == provisional_estimated_tokens
            and compatibility == provisional_compatibility
        ):
            break
        provisional_char_count = char_count
        provisional_byte_count = byte_count
        provisional_estimated_tokens = estimated_tokens
        provisional_compatibility = compatibility

    content = render_archive_xml(
        preset=preset,
        sections=sections,
        generated_at_utc=generated_at_utc,
        char_count=provisional_char_count,
        byte_count=provisional_byte_count,
        estimated_tokens=provisional_estimated_tokens,
        compatibility_labels=provisional_compatibility,
    )
    final_file_content: str = content + "\n"
    final_char_count = len(final_file_content)
    final_byte_count = len(final_file_content.encode("utf-8"))
    final_estimated_tokens = estimate_tokens(text=final_file_content)
    final_compatibility: list[str] = compatible_windows(
        estimated_tokens=final_estimated_tokens,
    )

    summary: LLMContextArchiveSummary = LLMContextArchiveSummary(
        preset_id=preset.preset_id,
        title=preset.title,
        file_name=preset.file_name,
        description=preset.description,
        use_case=preset.use_case,
        included_content=preset.included_content,
        section_count=len(sections),
        char_count=final_char_count,
        byte_count=final_byte_count,
        estimated_tokens=final_estimated_tokens,
        compatibility_labels=final_compatibility,
        short_name=preset.short_name,
        featured_rank=preset.featured_rank,
        content_details=preset.content_details,
    )
    return RenderedArchive(
        preset=preset,
        sections=sections,
        content=content,
        summary=summary,
    )


def _render_type_archive(
    *,
    definition: TypeArchiveDefinition,
    sections: list[ArchiveSection],
    generated_at_utc: str,
) -> RenderedTypeArchive:
    provisional_char_count: int = 0
    provisional_byte_count: int = 0
    provisional_estimated_tokens: int = 0
    provisional_compatibility: list[str] = []
    content: str = ""

    for _ in range(MAX_RENDER_PASSES):
        content = render_type_archive_xml(
            definition=definition,
            sections=sections,
            generated_at_utc=generated_at_utc,
            char_count=provisional_char_count,
            byte_count=provisional_byte_count,
            estimated_tokens=provisional_estimated_tokens,
            compatibility_labels=provisional_compatibility,
        )
        file_content: str = content + "\n"
        char_count = len(file_content)
        byte_count = len(file_content.encode("utf-8"))
        estimated_tokens = estimate_tokens(text=file_content)
        compatibility: list[str] = compatible_windows(
            estimated_tokens=estimated_tokens,
        )
        if (
            char_count == provisional_char_count
            and byte_count == provisional_byte_count
            and estimated_tokens == provisional_estimated_tokens
            and compatibility == provisional_compatibility
        ):
            break
        provisional_char_count = char_count
        provisional_byte_count = byte_count
        provisional_estimated_tokens = estimated_tokens
        provisional_compatibility = compatibility

    content = render_type_archive_xml(
        definition=definition,
        sections=sections,
        generated_at_utc=generated_at_utc,
        char_count=provisional_char_count,
        byte_count=provisional_byte_count,
        estimated_tokens=provisional_estimated_tokens,
        compatibility_labels=provisional_compatibility,
    )
    final_file_content: str = content + "\n"
    final_char_count = len(final_file_content)
    final_byte_count = len(final_file_content.encode("utf-8"))
    final_estimated_tokens = estimate_tokens(text=final_file_content)
    final_compatibility: list[str] = compatible_windows(
        estimated_tokens=final_estimated_tokens,
    )

    summary: TypeArchiveSummary = TypeArchiveSummary(
        type_id=definition.type_id,
        title=definition.title,
        file_name=definition.file_name,
        description=definition.description,
        included_content=definition.included_content,
        section_count=len(sections),
        char_count=final_char_count,
        byte_count=final_byte_count,
        estimated_tokens=final_estimated_tokens,
        compatibility_labels=final_compatibility,
    )
    return RenderedTypeArchive(
        definition=definition,
        sections=sections,
        content=content,
        summary=summary,
    )


def _format_size(*, byte_count: int) -> str:
    if byte_count < 1024:
        return f"{byte_count} B"
    kib: float = byte_count / 1024
    return f"{kib:.1f} KiB"


def _format_compatibility(*, compatibility_labels: list[str]) -> str:
    if len(compatibility_labels) == 0:
        return ">1M-class only"
    return ", ".join(compatibility_labels)


def _format_token_count_short(*, estimated_tokens: int) -> str:
    if estimated_tokens >= 1_000_000:
        return f"{round(estimated_tokens / 1_000_000)}M"
    if estimated_tokens >= 1_000:
        rounded_thousands: int = round(estimated_tokens / 1_000)
        if rounded_thousands >= 1_000:
            return "1M"
        return f"{rounded_thousands}K"
    return str(estimated_tokens)


def _format_index(
    *,
    preset_summaries: list[LLMContextArchiveSummary],
    type_summaries: list[TypeArchiveSummary],
) -> str:
    lines: list[str] = [
        "# LLM Context Archives",
        "",
        "Generated XML archives for pasting into ChatGPT, Gemini, Claude, and similar tools.",
        "",
        "## Preset Archives",
        "",
        "Curated presets that mix content from multiple aggregator types for specific use cases.",
        "",
        "| Preset | Tokens | Best For |",
        "|---|---:|---|",
    ]

    for summary in preset_summaries:
        lines.append(
            f"| [`{summary.preset_id}`]({summary.file_name}) | "
            f"{_format_token_count_short(estimated_tokens=summary.estimated_tokens)} | "
            f"{summary.use_case} |"
        )

    if len(type_summaries) > 0:
        lines.extend(
            [
                "",
                "## Per-Type Archives",
                "",
                "One file per aggregator type with complete untruncated data.",
                "",
                "| Type | Tokens | Description |",
                "|---|---:|---|",
            ]
        )
        for type_summary in type_summaries:
            lines.append(
                f"| [`{type_summary.type_id}`]({type_summary.file_name}) | "
                f"{_format_token_count_short(estimated_tokens=type_summary.estimated_tokens)}"
                f" | {type_summary.description} |"
            )

    lines.extend(
        [
            "",
            "## Context Windows",
            "",
        ]
    )

    for window in CONTEXT_WINDOWS:
        lines.append(f"* `{window.label}` — up to {window.max_tokens:,} estimated tokens")

    lines.extend(
        [
            "",
            "Token counts are approximate and use the shared rule `1 token ~= 4 chars`.",
        ]
    )

    for summary in preset_summaries:
        short_label: str = (
            summary.short_name if summary.short_name is not None else summary.preset_id
        )
        lines.append(
            "\n".join(
                [
                    "",
                    f"## {summary.title}",
                    "",
                    summary.description,
                    "",
                    f"* Preset id: `{summary.preset_id}`",
                    f"* Short label: `{short_label}`"
                    f" ({_format_token_count_short(estimated_tokens=summary.estimated_tokens)})",
                    f"* Best for: {summary.use_case}",
                    f"* File: [`{summary.file_name}`]({summary.file_name})",
                    f"* Size: {_format_size(byte_count=summary.byte_count)}"
                    f" ({summary.byte_count:,} bytes; {summary.char_count:,} chars)",
                    f"* Estimated tokens: {summary.estimated_tokens:,}",
                    "* Fits: "
                    + _format_compatibility(
                        compatibility_labels=summary.compatibility_labels,
                    ),
                    "",
                    "### Included Types",
                    "",
                    "| Included Type | Coverage |",
                    "|---|---|",
                ]
            )
        )
        for content_detail in summary.content_details:
            lines.append(f"| {content_detail.content_type} | {content_detail.coverage} |")

    if len(type_summaries) > 0:
        lines.extend(
            [
                "",
                "## Per-Type Archive Details",
            ]
        )
        for type_summary in type_summaries:
            lines.extend(
                [
                    "",
                    f"### {type_summary.title}",
                    "",
                    type_summary.description,
                    "",
                    f"* Type id: `{type_summary.type_id}`",
                    f"* File: [`{type_summary.file_name}`]({type_summary.file_name})",
                    f"* Size: {_format_size(byte_count=type_summary.byte_count)}"
                    f" ({type_summary.byte_count:,} bytes;"
                    f" {type_summary.char_count:,} chars)",
                    f"* Estimated tokens: {type_summary.estimated_tokens:,}",
                    "* Fits: "
                    + _format_compatibility(
                        compatibility_labels=type_summary.compatibility_labels,
                    ),
                ]
            )

    return "\n".join(lines)
