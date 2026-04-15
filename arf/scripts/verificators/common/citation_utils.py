import re
from dataclasses import dataclass

_CITATION_PATTERN: re.Pattern[str] = re.compile(
    r"(?<!!)\[([A-Za-z][A-Za-z0-9_-]*)\](?!\()",
)

_SOURCE_HEADING_PATTERN: re.Pattern[str] = re.compile(
    r"^###\s+\[([A-Za-z][A-Za-z0-9_-]*)\]\s*$",
    re.MULTILINE,
)

_FIELD_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*\*\s+\*\*([^*]+)\*\*\s*:\s*(.+)$",
    re.MULTILINE,
)


@dataclass(frozen=True, slots=True)
class SourceIndexEntry:
    key: str
    fields: dict[str, str]


def extract_inline_citations(*, text: str) -> set[str]:
    """Excludes markdown links [text](url) and images ![alt](url)."""
    return set(_CITATION_PATTERN.findall(text))


def parse_source_index(
    *,
    section_content: str,
) -> list[SourceIndexEntry]:
    """Expects ### [Key] headings followed by * **Field**: value bullet lines."""
    heading_matches: list[re.Match[str]] = list(
        _SOURCE_HEADING_PATTERN.finditer(section_content),
    )
    entries: list[SourceIndexEntry] = []

    for i, match in enumerate(heading_matches):
        key: str = match.group(1)
        start_pos: int = match.end()
        if i + 1 < len(heading_matches):
            end_pos: int = heading_matches[i + 1].start()
        else:
            end_pos = len(section_content)
        entry_text: str = section_content[start_pos:end_pos]
        fields: dict[str, str] = {}
        for field_match in _FIELD_PATTERN.finditer(entry_text):
            field_name: str = field_match.group(1).strip().lower()
            field_value: str = field_match.group(2).strip()
            fields[field_name] = field_value
        entries.append(SourceIndexEntry(key=key, fields=fields))

    return entries
