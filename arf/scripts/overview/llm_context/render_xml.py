"""XML rendering for overview LLM context archives."""

from html import escape as xml_escape

from arf.scripts.overview.llm_context.models import (
    ArchiveSection,
    PresetDefinition,
    TypeArchiveDefinition,
)


def render_archive_xml(
    *,
    preset: PresetDefinition,
    sections: list[ArchiveSection],
    generated_at_utc: str,
    char_count: int,
    byte_count: int,
    estimated_tokens: int,
    compatibility_labels: list[str],
) -> str:
    compatibility_text: str = (
        ", ".join(compatibility_labels)
        if len(compatibility_labels) > 0
        else "Needs a context window larger than 1M-class."
    )

    lines: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            "<llm_context_archive "
            f'preset_id="{xml_escape(preset.preset_id)}" '
            f'generated_at_utc="{xml_escape(generated_at_utc)}">'
        ),
        "  <archive_summary>",
        f"    <title>{xml_escape(preset.title)}</title>",
        f"    <description>{xml_escape(preset.description)}</description>",
        f"    <use_case>{xml_escape(preset.use_case)}</use_case>",
        f"    <section_count>{len(sections)}</section_count>",
        f"    <char_count>{char_count}</char_count>",
        f"    <byte_count>{byte_count}</byte_count>",
        f"    <estimated_tokens>{estimated_tokens}</estimated_tokens>",
        f"    <compatibility>{xml_escape(compatibility_text)}</compatibility>",
        "  </archive_summary>",
        "  <included_content>",
    ]

    for item in preset.included_content:
        lines.append(f"    <item>{xml_escape(item)}</item>")

    lines.extend(
        [
            "  </included_content>",
            "  <sections>",
        ]
    )

    for section in sections:
        lines.extend(_render_section(section=section))

    lines.extend(
        [
            "  </sections>",
            "</llm_context_archive>",
        ]
    )
    return "\n".join(lines)


def render_type_archive_xml(
    *,
    definition: TypeArchiveDefinition,
    sections: list[ArchiveSection],
    generated_at_utc: str,
    char_count: int,
    byte_count: int,
    estimated_tokens: int,
    compatibility_labels: list[str],
) -> str:
    compatibility_text: str = (
        ", ".join(compatibility_labels)
        if len(compatibility_labels) > 0
        else "Needs a context window larger than 1M-class."
    )

    lines: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            "<llm_context_archive "
            f'type_id="{xml_escape(definition.type_id)}" '
            f'generated_at_utc="{xml_escape(generated_at_utc)}">'
        ),
        "  <archive_summary>",
        f"    <title>{xml_escape(definition.title)}</title>",
        f"    <description>{xml_escape(definition.description)}</description>",
        f"    <section_count>{len(sections)}</section_count>",
        f"    <char_count>{char_count}</char_count>",
        f"    <byte_count>{byte_count}</byte_count>",
        f"    <estimated_tokens>{estimated_tokens}</estimated_tokens>",
        f"    <compatibility>{xml_escape(compatibility_text)}</compatibility>",
        "  </archive_summary>",
        "  <included_content>",
    ]

    for item in definition.included_content:
        lines.append(f"    <item>{xml_escape(item)}</item>")

    lines.extend(
        [
            "  </included_content>",
            "  <sections>",
        ]
    )

    for section in sections:
        lines.extend(_render_section(section=section))

    lines.extend(
        [
            "  </sections>",
            "</llm_context_archive>",
        ]
    )
    return "\n".join(lines)


def _render_section(*, section: ArchiveSection) -> list[str]:
    lines: list[str] = [
        (
            "    <section "
            f'id="{xml_escape(section.section_id)}" '
            f'source_kind="{xml_escape(section.source_kind)}">'
        ),
        f"      <title>{xml_escape(section.title)}</title>",
        f"      <source_name>{xml_escape(section.source_name)}</source_name>",
    ]

    if len(section.source_ids) > 0:
        lines.append("      <source_ids>")
        for source_id in section.source_ids:
            lines.append(f"        <id>{xml_escape(source_id)}</id>")
        lines.append("      </source_ids>")

    if len(section.repo_paths) > 0:
        lines.append("      <repo_paths>")
        for repo_path in section.repo_paths:
            lines.append(f"        <path>{xml_escape(repo_path)}</path>")
        lines.append("      </repo_paths>")

    lines.extend(
        [
            "      <content>",
            xml_escape(section.content),
            "      </content>",
            "    </section>",
        ]
    )
    return lines
