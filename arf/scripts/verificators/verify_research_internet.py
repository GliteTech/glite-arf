"""Verificator for research_internet.md files.

Usage:
    uv run python -m arf.scripts.verificators.verify_research_internet <task_id>

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.citation_utils import (
    SourceIndexEntry,
    extract_inline_citations,
    parse_source_index,
)
from arf.scripts.verificators.common.constants import (
    FRONTMATTER_FIELD_STATUS,
    FRONTMATTER_FIELD_TASK_ID,
    STATUS_PARTIAL,
)
from arf.scripts.verificators.common.frontmatter import (
    FrontmatterResult,
    extract_frontmatter_and_body,
    parse_frontmatter,
)
from arf.scripts.verificators.common.markdown_sections import (
    MarkdownSection,
    count_words,
    extract_sections,
)
from arf.scripts.verificators.common.paths import research_internet_path
from arf.scripts.verificators.common.reporting import (
    exit_code_for_result,
    print_verification_result,
)
from arf.scripts.verificators.common.types import (
    Diagnostic,
    DiagnosticCode,
    Severity,
    VerificationResult,
)

# ---------------------------------------------------------------------------
# Research-internet-specific constants
# ---------------------------------------------------------------------------

FRONTMATTER_FIELD_SPEC_VERSION: str = "spec_version"
FRONTMATTER_FIELD_SOURCES_CITED: str = "sources_cited"
FRONTMATTER_FIELD_PAPERS_DISCOVERED: str = "papers_discovered"
FRONTMATTER_FIELD_SEARCHES_CONDUCTED: str = "searches_conducted"

RESEARCH_PAPERS_FILENAME: str = "research_papers.md"

SOURCE_FIELD_URL: str = "url"
SOURCE_FIELD_PEER_REVIEWED: str = "peer-reviewed"

SECTION_TASK_OBJECTIVE: str = "Task Objective"
SECTION_GAPS_ADDRESSED: str = "Gaps Addressed"
SECTION_SEARCH_STRATEGY: str = "Search Strategy"
SECTION_KEY_FINDINGS: str = "Key Findings"
SECTION_METHODOLOGY_INSIGHTS: str = "Methodology Insights"
SECTION_DISCOVERED_PAPERS: str = "Discovered Papers"
SECTION_RECOMMENDATIONS: str = "Recommendations for This Task"
SECTION_SOURCE_INDEX: str = "Source Index"

MANDATORY_SECTIONS: list[str] = [
    SECTION_TASK_OBJECTIVE,
    SECTION_GAPS_ADDRESSED,
    SECTION_SEARCH_STRATEGY,
    SECTION_KEY_FINDINGS,
    SECTION_METHODOLOGY_INSIGHTS,
    SECTION_DISCOVERED_PAPERS,
    SECTION_RECOMMENDATIONS,
    SECTION_SOURCE_INDEX,
]

MIN_WORDS_PER_SECTION: dict[str, int] = {
    SECTION_TASK_OBJECTIVE: 30,
    SECTION_GAPS_ADDRESSED: 50,
    SECTION_SEARCH_STRATEGY: 100,
    SECTION_KEY_FINDINGS: 200,
    SECTION_METHODOLOGY_INSIGHTS: 100,
    SECTION_DISCOVERED_PAPERS: 0,
    SECTION_RECOMMENDATIONS: 50,
    SECTION_SOURCE_INDEX: 0,
}

MIN_TOTAL_WORDS: int = 400
MIN_SEARCH_QUERIES: int = 3

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "RI"

RI_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
RI_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
RI_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
RI_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
RI_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
RI_E006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=6,
)
RI_E007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=7,
)
RI_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
RI_E009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=9,
)
RI_E010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=10,
)

RI_E011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=11,
)

RI_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
RI_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
RI_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
RI_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)
RI_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
RI_W006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=6,
)
RI_W007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=7,
)

# ---------------------------------------------------------------------------
# Numbered list pattern for counting search queries
# ---------------------------------------------------------------------------

_NUMBERED_ITEM_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*\d+\.\s+",
    re.MULTILINE,
)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_spec_version(
    *,
    frontmatter: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    if FRONTMATTER_FIELD_SPEC_VERSION not in frontmatter:
        return [
            Diagnostic(
                code=RI_E011,
                message="Frontmatter is missing the 'spec_version' field",
                file_path=file_path,
            ),
        ]
    return []


def _check_task_id_match(
    *,
    frontmatter: dict[str, Any],
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    fm_task_id: object = frontmatter.get(FRONTMATTER_FIELD_TASK_ID)
    if fm_task_id is None:
        return [
            Diagnostic(
                code=RI_E003,
                message="Frontmatter is missing the 'task_id' field",
                file_path=file_path,
            ),
        ]
    if str(fm_task_id) != task_id:
        return [
            Diagnostic(
                code=RI_E003,
                message=(
                    f"Frontmatter task_id '{fm_task_id}' does not match task folder '{task_id}'"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_mandatory_sections(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    found_headings: set[str] = {s.heading for s in sections}
    diagnostics: list[Diagnostic] = []
    for required in MANDATORY_SECTIONS:
        if required not in found_headings:
            diagnostics.append(
                Diagnostic(
                    code=RI_E004,
                    message=f"Missing mandatory section: '## {required}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_sources_cited(
    *,
    frontmatter: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    sources_cited: object = frontmatter.get(FRONTMATTER_FIELD_SOURCES_CITED)
    status: object = frontmatter.get(FRONTMATTER_FIELD_STATUS)
    if isinstance(sources_cited, int) and sources_cited < 1 and str(status) != STATUS_PARTIAL:
        return [
            Diagnostic(
                code=RI_E005,
                message="sources_cited is 0 but status is not 'partial'",
                file_path=file_path,
            ),
        ]
    return []


def _check_inline_citations(
    *,
    body: str,
    source_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    inline_keys: set[str] = extract_inline_citations(text=body)
    index_keys: set[str] = {entry.key for entry in source_entries}
    diagnostics: list[Diagnostic] = []
    for key in sorted(inline_keys - index_keys):
        diagnostics.append(
            Diagnostic(
                code=RI_E006,
                message=(f"Inline citation [{key}] has no matching Source Index entry"),
                file_path=file_path,
            ),
        )
    return diagnostics


def _check_source_count(
    *,
    frontmatter: dict[str, Any],
    source_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    sources_cited: object = frontmatter.get(FRONTMATTER_FIELD_SOURCES_CITED)
    if not isinstance(sources_cited, int):
        return [
            Diagnostic(
                code=RI_E007,
                message="Frontmatter is missing or has non-integer 'sources_cited'",
                file_path=file_path,
            ),
        ]
    actual_count: int = len(source_entries)
    if actual_count != sources_cited:
        return [
            Diagnostic(
                code=RI_E007,
                message=(
                    f"Source Index has {actual_count} entries "
                    f"but frontmatter says sources_cited={sources_cited}"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_source_urls(
    *,
    source_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for entry in source_entries:
        if SOURCE_FIELD_URL not in entry.fields:
            diagnostics.append(
                Diagnostic(
                    code=RI_E008,
                    message=f"Source Index entry [{entry.key}] is missing the URL field",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_total_word_count(
    *,
    body: str,
    file_path: Path,
) -> list[Diagnostic]:
    total: int = count_words(text=body)
    if total < MIN_TOTAL_WORDS:
        return [
            Diagnostic(
                code=RI_E009,
                message=(f"Total content has {total} words (minimum: {MIN_TOTAL_WORDS})"),
                file_path=file_path,
            ),
        ]
    return []


def _check_gaps_references_papers(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_GAPS_ADDRESSED:
            if RESEARCH_PAPERS_FILENAME in section.content:
                return []
            return [
                Diagnostic(
                    code=RI_E010,
                    message=(
                        "'## Gaps Addressed' section does not reference "
                        f"'{RESEARCH_PAPERS_FILENAME}'"
                    ),
                    file_path=file_path,
                ),
            ]
    return []


def _check_section_word_counts(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for section in sections:
        min_words: int | None = MIN_WORDS_PER_SECTION.get(section.heading)
        if min_words is None or min_words == 0:
            continue
        actual: int = count_words(text=section.content)
        if actual < min_words:
            diagnostics.append(
                Diagnostic(
                    code=RI_W001,
                    message=(
                        f"Section '{section.heading}' has {actual} words (minimum: {min_words})"
                    ),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_search_query_count(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_SEARCH_STRATEGY:
            query_count: int = len(
                _NUMBERED_ITEM_PATTERN.findall(section.content),
            )
            if query_count < MIN_SEARCH_QUERIES:
                return [
                    Diagnostic(
                        code=RI_W002,
                        message=(
                            f"Search Strategy lists {query_count} queries "
                            f"(minimum: {MIN_SEARCH_QUERIES})"
                        ),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


def _check_key_findings_subsections(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_KEY_FINDINGS:
            if re.search(r"^### ", section.content, re.MULTILINE) is None:
                return [
                    Diagnostic(
                        code=RI_W003,
                        message=("'## Key Findings' section contains no ### subsections"),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


def _check_source_peer_reviewed(
    *,
    source_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for entry in source_entries:
        if SOURCE_FIELD_PEER_REVIEWED not in entry.fields:
            diagnostics.append(
                Diagnostic(
                    code=RI_W004,
                    message=(
                        f"Source Index entry [{entry.key}] is missing the 'Peer-reviewed' field"
                    ),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_uncited_sources(
    *,
    body: str,
    source_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    inline_keys: set[str] = extract_inline_citations(text=body)
    diagnostics: list[Diagnostic] = []
    for entry in source_entries:
        if entry.key not in inline_keys:
            diagnostics.append(
                Diagnostic(
                    code=RI_W005,
                    message=(f"Source Index entry [{entry.key}] is never cited in body text"),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_papers_discovered_consistency(
    *,
    frontmatter: dict[str, Any],
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    papers_discovered: object = frontmatter.get(
        FRONTMATTER_FIELD_PAPERS_DISCOVERED,
    )
    if not isinstance(papers_discovered, int):
        return []

    entry_count: int = 0
    for section in sections:
        if section.heading == SECTION_DISCOVERED_PAPERS:
            entry_count = len(
                re.findall(r"^### ", section.content, re.MULTILINE),
            )
            break

    has_entries: bool = entry_count > 0
    has_count: bool = papers_discovered > 0
    if has_entries != has_count:
        return [
            Diagnostic(
                code=RI_W006,
                message=(
                    f"papers_discovered={papers_discovered} in frontmatter "
                    f"but Discovered Papers section has {entry_count} entries"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_searches_conducted_consistency(
    *,
    frontmatter: dict[str, Any],
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    searches_conducted: object = frontmatter.get(
        FRONTMATTER_FIELD_SEARCHES_CONDUCTED,
    )
    if not isinstance(searches_conducted, int):
        return []

    for section in sections:
        if section.heading == SECTION_SEARCH_STRATEGY:
            query_count: int = len(
                _NUMBERED_ITEM_PATTERN.findall(section.content),
            )
            if query_count != searches_conducted:
                return [
                    Diagnostic(
                        code=RI_W007,
                        message=(
                            f"searches_conducted={searches_conducted} "
                            f"in frontmatter but Search Strategy lists "
                            f"{query_count} queries"
                        ),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_research_internet(
    *,
    task_id: str,
) -> VerificationResult:
    file_path: Path = research_internet_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    # E001: File existence
    if not file_path.exists():
        diagnostics.append(
            Diagnostic(
                code=RI_E001,
                message=f"File does not exist: {file_path}",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    try:
        content: str = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        diagnostics.append(
            Diagnostic(
                code=RI_E002,
                message=f"File is not valid UTF-8: {exc}",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    # E002: Frontmatter parsing
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(
        content=content,
    )
    if split_result is None:
        diagnostics.append(
            Diagnostic(
                code=RI_E002,
                message="YAML frontmatter is missing or has invalid delimiters",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    raw_yaml: str = split_result.raw_yaml
    body: str = split_result.body
    frontmatter: dict[str, Any] | None = parse_frontmatter(raw_yaml=raw_yaml)
    if frontmatter is None:
        diagnostics.append(
            Diagnostic(
                code=RI_E002,
                message="YAML frontmatter is not parseable",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    # Extract sections and source index (used by many checks)
    sections: list[MarkdownSection] = extract_sections(
        body=body,
        level=2,
    )
    source_index_content: str = ""
    for section in sections:
        if section.heading == SECTION_SOURCE_INDEX:
            source_index_content = section.content
            break
    source_entries: list[SourceIndexEntry] = parse_source_index(
        section_content=source_index_content,
    )

    # E011: spec_version
    diagnostics.extend(
        _check_spec_version(
            frontmatter=frontmatter,
            file_path=file_path,
        ),
    )

    # E003: task_id match
    diagnostics.extend(
        _check_task_id_match(
            frontmatter=frontmatter,
            task_id=task_id,
            file_path=file_path,
        ),
    )

    # E004: Mandatory sections
    diagnostics.extend(
        _check_mandatory_sections(
            sections=sections,
            file_path=file_path,
        ),
    )

    # E005: sources_cited < 1 with non-partial status
    diagnostics.extend(
        _check_sources_cited(
            frontmatter=frontmatter,
            file_path=file_path,
        ),
    )

    # E006: Inline citations without Source Index match
    diagnostics.extend(
        _check_inline_citations(
            body=body,
            source_entries=source_entries,
            file_path=file_path,
        ),
    )

    # E007: Source Index count mismatch
    diagnostics.extend(
        _check_source_count(
            frontmatter=frontmatter,
            source_entries=source_entries,
            file_path=file_path,
        ),
    )

    # E008: Source Index entries missing URL
    diagnostics.extend(
        _check_source_urls(
            source_entries=source_entries,
            file_path=file_path,
        ),
    )

    # E009: Total word count
    diagnostics.extend(
        _check_total_word_count(
            body=body,
            file_path=file_path,
        ),
    )

    # E010: Gaps Addressed references research_papers.md
    diagnostics.extend(
        _check_gaps_references_papers(
            sections=sections,
            file_path=file_path,
        ),
    )

    # W001: Section word counts
    diagnostics.extend(
        _check_section_word_counts(
            sections=sections,
            file_path=file_path,
        ),
    )

    # W002: Search query count
    diagnostics.extend(
        _check_search_query_count(
            sections=sections,
            file_path=file_path,
        ),
    )

    # W003: Key Findings subsections
    diagnostics.extend(
        _check_key_findings_subsections(
            sections=sections,
            file_path=file_path,
        ),
    )

    # W004: Source entries missing Peer-reviewed
    diagnostics.extend(
        _check_source_peer_reviewed(
            source_entries=source_entries,
            file_path=file_path,
        ),
    )

    # W005: Uncited source entries
    diagnostics.extend(
        _check_uncited_sources(
            body=body,
            source_entries=source_entries,
            file_path=file_path,
        ),
    )

    # W006: papers_discovered consistency
    diagnostics.extend(
        _check_papers_discovered_consistency(
            frontmatter=frontmatter,
            sections=sections,
            file_path=file_path,
        ),
    )

    # W007: searches_conducted consistency
    diagnostics.extend(
        _check_searches_conducted_consistency(
            frontmatter=frontmatter,
            sections=sections,
            file_path=file_path,
        ),
    )

    return VerificationResult(
        file_path=file_path,
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify research_internet.md for a given task",
    )
    parser.add_argument(
        "task_id",
        help="Task ID (e.g. 0015-cohort-discrimination-analysis)",
    )
    args: argparse.Namespace = parser.parse_args()

    result: VerificationResult = verify_research_internet(
        task_id=args.task_id,
    )
    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
