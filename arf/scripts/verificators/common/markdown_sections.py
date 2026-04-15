import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MarkdownSection:
    heading: str
    level: int
    content: str
    start_line: int


def extract_sections(*, body: str, level: int) -> list[MarkdownSection]:
    """Extract all sections at the given heading level from markdown body."""
    prefix: str = "#" * level + " "
    heading_pattern: re.Pattern[str] = re.compile(
        rf"^{re.escape(prefix)}(.+)$",
        re.MULTILINE,
    )

    matches: list[re.Match[str]] = list(heading_pattern.finditer(body))
    sections: list[MarkdownSection] = []

    for i, match in enumerate(matches):
        heading: str = match.group(1).strip()
        start_pos: int = match.end()
        if i + 1 < len(matches):
            end_pos: int = matches[i + 1].start()
        else:
            end_pos = len(body)
        content: str = body[start_pos:end_pos].strip()
        start_line: int = body[: match.start()].count("\n") + 1
        sections.append(
            MarkdownSection(
                heading=heading,
                level=level,
                content=content,
                start_line=start_line,
            ),
        )

    return sections


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def count_words(*, text: str) -> int:
    """Count words in text, stripping markdown formatting artifacts."""
    cleaned: str = re.sub(r"[#*_`|~\-]", " ", text)
    cleaned = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cleaned)
    cleaned = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", cleaned)
    words: list[str] = cleaned.split()
    return len(words)
